from neo4j.v1 import GraphDatabase, basic_auth

uri = "bolt://localhost:7687"
username = "neo4j"
password = "wildcraft"

driver = GraphDatabase.driver(uri, auth=basic_auth(username, password))

def move1(x, y):
    #Only one person moves on boat
    return x - 1, y + 1

def move2(x, y):
    #Two person of same type moves on boat
    return x - 2, y + 2

def move11(x, y, p, q):
    #One person of both types moves on boat
    return x - 1, y + 1, p - 1, q + 1

def checkState(states, goal_state):
    for curr_state in states:
        if(curr_state["left_gaurds"] == goal_state["left_gaurds"] and curr_state["right_gaurds"] == goal_state["right_gaurds"] and curr_state["left_prisn"] == goal_state["left_prisn"] and curr_state["right_prisn"] == goal_state["right_prisn"]):
            return curr_state["timestamp"]
        else:
            return 0

def createState(left_gaurds=3, right_gaurds=0, left_prisn=3, right_prisn=0, time=0):
    params = {"left_gaurds": left_gaurds, "right_gaurds": right_gaurds, "left_prisn": left_prisn, "right_prisn": right_prisn, "timestamp": time}
    return params

def createRelationship(state_0, states, reverse=False):
    with driver.session() as session:
        with session.begin_transaction() as tx:
            if(state_0["timestamp"] == 0):
                tx.run("CREATE (n:state {left_gaurds: {lg0}, right_gaurds: {rg0}, left_prisn: {lp0}, right_prisn: {rp0}, timestamp: {t}})", {"lg0": state_0["left_gaurds"], "rg0": state_0["right_gaurds"], "lp0": state_0["left_prisn"], "rp0": state_0["right_prisn"], "t": state_0["timestamp"]})
            for state_1 in states:
                if(reverse == False):
                    relation = "FORWARD"
                else:
                    relation = "BACKWARD"
                query1 = "MATCH (n:state) WHERE n.timestamp = " + str(state_0["timestamp"])
                query2 = "CREATE (m:state {left_gaurds: {lg1}, right_gaurds: {rg1}, left_prisn: {lp1}, right_prisn: {rp1}, timestamp: {t}}),"
                query3 = "(n)-[:" + relation + "]->(m)"
                query = query1 + "\n" + query2 + "\n" + query3
                tx.run(query, {"lg1": state_1["left_gaurds"], "rg1": state_1["right_gaurds"], "lp1": state_1["left_prisn"], "rp1": state_1["right_prisn"], "t": state_1["timestamp"]})

def dumbGenerator(initial_state, reverse=False):
    params = initial_state
    ini_lg = params["left_gaurds"]
    ini_rg = params["right_gaurds"]
    ini_lp = params["left_prisn"]
    ini_rp = params["right_prisn"]
    ini_time = params["timestamp"]

    generated_states = []
    if(reverse == False):
        if(ini_lg > 0):
            final_lg, final_rg = move1(ini_lg, ini_rg)
            generated_states.append(createState(final_lg, final_rg, ini_lp, ini_rp, ini_time + 1))
        if(ini_lp > 0):
            final_lp, final_rp = move1(ini_lp, ini_rp)
            generated_states.append(createState(ini_lg, ini_rg, final_lp, final_rp, ini_time + 1))
        if(ini_lg > 1):
            final_lg, final_rg = move2(ini_lg, ini_rg)
            generated_states.append(createState(final_lg, final_rg, ini_lp, ini_rp, ini_time + 1))
        if(ini_lp > 1):
            final_lp, final_rp = move2(ini_lp, ini_rp)
            generated_states.append(createState(ini_lg, ini_rg, final_lp, final_rp, ini_time + 1))
        if(ini_lg > 0 and ini_lp > 0):
            final_lg, final_rg, final_lp, final_rp = move11(ini_lg, ini_rg, ini_lp, ini_rp)
            generated_states.append(createState(final_lg, final_rg, final_lp, final_rp, ini_time + 1))
    else:
        if(ini_rg > 0):
            final_rg, final_lg = move1(ini_rg, ini_lg)
            generated_states.append(createState(final_lg, final_rg, ini_lp, ini_rp, ini_time + 1))
        if(ini_rp > 0):
            final_rp, final_lp = move1(ini_rp, ini_lp)
            generated_states.append(createState(ini_lg, ini_rg, final_lp, final_rp, ini_time + 1))
        if(ini_rg > 1):
            final_rg, final_lg = move2(ini_rg, ini_lg)
            generated_states.append(createState(final_lg, final_rg, ini_lp, ini_rp, ini_time + 1))
        if(ini_rp > 1):
            final_rp, final_lp = move2(ini_rp, ini_lp)
            generated_states.append(createState(ini_lg, ini_rg, final_lp, final_rp, ini_time + 1))
        if(ini_rg > 0 and ini_rp > 0):
            final_rg, final_lg, final_rp, final_lp = move11(ini_rg, ini_lg, ini_rp, ini_lp)
            generated_states.append(createState(final_lg, final_rg, final_lp, final_rp, ini_time + 1))

    return generated_states

def dumbTester(generated_states, occured_states):
    final_states = []
    for state in generated_states:
        # CHECK = 0
        # for occured_state in occured_states:
        #     if(occured_state["left_gaurds"] == state["left_gaurds"] and occured_state["right_gaurds"] == state["right_gaurds"] and occured_state["left_prisn"] == state["left_prisn"] and occured_state["right_prisn"] == state["right_prisn"]):
        #         CHECK = 1
        #         break

        # if(CHECK == 0):
            flag = 0
            params = state
            lg = params["left_gaurds"]
            rg = params["right_gaurds"]
            lp = params["left_prisn"]
            rp = params["right_prisn"]

            if(lg != 0 and lp != 0):
                if(lg < lp):
                    flag = 1
            if(rg != 0 and rp != 0):
                if(rg < rp):
                    flag = 1
            if(flag == 0):
                final_states.append(state)
                # occured_states.append(state)

    return final_states, occured_states

#MAIN
reverse = False
GAME = True
ini_lg = 3
ini_rg = 0
ini_lp = 3
ini_rp = 0

initial_state = createState(ini_lg, ini_rg, ini_lp, ini_rp)
goal_state = createState(ini_rg, ini_lg, ini_rp, ini_lp)

game_states = []
occured_states = []
game_states.append(initial_state)
occured_states.append(initial_state)
print ("hello")
while(GAME):
    for ini_state in game_states:
        if(ini_state["timestamp"] % 2 == 0):
            reverse = False
        else:
            reverse = True

        generated_states = dumbGenerator(ini_state, reverse)
        final_states, occured_states = dumbTester(generated_states, occured_states)
        createRelationship(ini_state, final_states, reverse)
        STOP = checkState(final_states, goal_state)
        print(STOP)
        if(STOP != 0 ):
            GAME = False
            print("STOPPED!!!\n")
            break

        game_states += final_states
        game_states = game_states[1:]
