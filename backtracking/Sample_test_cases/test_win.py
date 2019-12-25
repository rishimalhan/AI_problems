import copy
import random
from queue import PriorityQueue
import sys

path = "Sample_test_cases/"
inputs = open(path+"input3.txt","r")
input_data = []
i = 0
for line in inputs:
    input_data.append(str(line))
    i += 1


class IpProp:  # Class which will contain all parameters used later.
    pots = []
    conf = {}
    def __init__(self):
        self.grp_cnt = None
        self.pot_cnt = None
        self.node_cnt = None
        self.depth_idx = None
        self.pot_seq = None
        return

#*********************************READING INPUTS BEGINS*******************************************#
global goal_node
goal_node = None
Node_map = {}
props = IpProp()
props.grp_cnt = int(input_data[0])
props.pot_cnt = int(input_data[1])
props.node_cnt = 0
props.filled_teams = 0

# Assigning the pots to pot array
for i in range(2,2+props.pot_cnt):
    props.pots.append(input_data[i].rstrip().split(","))
# Assigning the confederations
for i in range(2+props.pot_cnt,2+props.pot_cnt+6):
    props.conf[str(input_data[i].split(":")[0])] = input_data[i].split(":")[1].rstrip().split(",")

#*********************************READING INPUTS ENDS*******************************************#
# Prioritize pots according to diversity
def diversity(props,team_info):
    div_sum = []
    for i in range(props.pot_cnt):
        div_sum.append(0)
    queue = PriorityQueue(maxsize=0)
    for i in range(props.pot_cnt):
        for confederation in ["AFC", "CAF", "OFC", "CONCACAF", "CONMEBOL", "UEFA"]:
            for pot_ctr in range(len(props.pots[i])):
                if confederation in team_info[props.pots[i][pot_ctr]][0]:
                    div_sum[i] += 1
                    break
        queue.put([div_sum[i],i])
    updated_pots = []
    pot_seq = []
    for i in range(props.pot_cnt):
        curr_idx = int(queue.get()[1])
        pot_seq.append(curr_idx)
        updated_pots.append(props.pots[curr_idx])
    return updated_pots,pot_seq

# Collecting all teams with their corresponding confederation and pot in dictionary
teams = {}
team_info = {}  #Stores information of a team as Confederation and Pot Number
counter = 0
for confederation in ["AFC","CAF","OFC","CONCACAF","CONMEBOL","UEFA"]:
    if "None" not in props.conf[confederation]:
        for j in range(len(props.conf[confederation])):
            list1 = []
            list2 = []
            curr_team = props.conf[confederation][j]
            list1.append(curr_team)
            list1.append(confederation)
            list2.append(confederation)
            for k in range(props.pot_cnt):
                if curr_team in props.pots[k]:
                    list1.append(k)
                    list2.append(k)
                    teams[str(counter)] = list1
                    team_info[curr_team] = list2
                    counter += 1
props.no_teams = len(team_info)
# Updating Pots according to constraints as heuristics
props.pots,props.pot_seq = diversity(props,team_info)

# Randomize Teams
team_idx = []
counter = 0
for i in range(len(teams)):
    team_idx.append(i)
updated_teams = {}
while len(team_idx) != 0:
    curr_choice = random.choice(team_idx)
    updated_teams[str(counter)] = teams[str(curr_choice)]
    team_idx.remove(curr_choice)
    counter += 1
teams = updated_teams

##########################################EVALUATING RUBBISH CASES##################################
# Checking for Max number of teams in a pot greater than number of groups.
max_teams = 0
for i in range(props.pot_cnt):
    max_teams = max(max_teams,len(props.pots[i]))
if max_teams>props.grp_cnt:
    print("Solution Doesnot Exist. Pigeon Hole Failure")
    sys.exit()
# Checking for teams in UEFA greater than twice the number of groups.
for confederation in ["AFC","CAF","OFC","CONCACAF","CONMEBOL","UEFA"]:
    if "UEFA" in props.conf[confederation]:
        if len(props.conf[confederation])>props.grp_cnt*2:
            print("Solution Doesnot Exist. UEFA Failure")
            sys.exit()

class Node(object):
    def __init__(self):
        self.parent = None
        self.id = None
        self.depth = None
        self.is_closed = None
        self.state = None
        self.conf_mat = None
        self.filled_teams = None
        return
props.depth_idx = {}    # DONOT Randomize
counter = 1
for i in range(props.grp_cnt):
    for j in range(props.pot_cnt):
        props.depth_idx[str(counter)] = [i,j]
        counter += 1

def create_node(in_parent,in_value,Node_map,props):
    new_node = Node()
    new_node.is_closed = copy.deepcopy(False)
    new_node.parent = copy.deepcopy(in_parent)
    new_node.id = copy.deepcopy(props.node_cnt)
    curr_depth = Node_map[str(in_parent)].depth+1
    curr_fill_teams = Node_map[str(in_parent)].filled_teams+1
    new_node.depth = copy.deepcopy(curr_depth)
    # Initializing the state in the node
    new_node.state = copy.deepcopy(Node_map[str(in_parent)].state)
    new_node.conf_mat = copy.deepcopy(Node_map[str(in_parent)].conf_mat)
    row = props.depth_idx[str(curr_depth)][0]
    col = props.depth_idx[str(curr_depth)][1]
    if not in_value:
        new_node.state[row][col] = []
        new_node.filled_teams = copy.deepcopy(Node_map[str(in_parent)].filled_teams)
    else:
        new_node.state[row][col] = [in_value]
        new_node.conf_mat[row][col] = in_value[1]
        new_node.filled_teams = curr_fill_teams
    return new_node


def consistency_check(in_state,parent,in_var,depth,props):
    # This should take the node, update the domains of the node and if consistency
    # is lost, then returns inconsistent which will not store the Node in possible actions
    # in get children function
    # print_state(in_state,props)

    row = props.depth_idx[str(depth)][0]
    col = props.depth_idx[str(depth)][1]
    # Removing this country from current col domains
    for i in range(props.grp_cnt):
        if (i == row):
            continue
        curr_domain = copy.deepcopy(in_state[i][col])
        if in_var in curr_domain:
            curr_domain.remove(in_var)
            in_state[i][col] = curr_domain

    curr_conf = in_var[1]
    if curr_conf=="UEFA":
        no_uefa = Node_map[str(parent)].conf_mat[row].count("UEFA")
        if (no_uefa>1):
            return "inconsistent"
        elif (no_uefa==1):
            for i in range(col+1,props.pot_cnt):
                curr_domain = copy.deepcopy(in_state[row][i])
                ctr = 0
                while ctr < len(curr_domain):
                    elmnt_rmvd = False
                    if curr_conf in curr_domain[ctr]:
                        elmnt_rmvd = True
                        curr_domain.remove(curr_domain[ctr])
                    if not elmnt_rmvd:
                        ctr += 1
                in_state[row][i] = curr_domain
    else:
        if curr_conf in Node_map[str(parent)].conf_mat[row]:
            return "inconsistent"
        else:
            for i in range(col+1,props.pot_cnt):
                curr_domain = copy.deepcopy(in_state[row][i])
                ctr = 0
                while ctr < len(curr_domain):
                    elmnt_rmvd = False
                    if curr_conf in curr_domain[ctr]:
                        elmnt_rmvd = True
                        curr_domain.remove(curr_domain[ctr])
                    if not elmnt_rmvd:
                        ctr += 1
                in_state[row][i] = curr_domain
    # print_state(in_state,props)
    return in_state


def print_state(in_state,props):
    print("**********************************************")
    for i in range(props.grp_cnt):
        row = []
        for j in range(props.pot_cnt):
            domain = []
            for k in range(len(in_state[i][j])):
                domain.append(in_state[i][j][k][0])
            row.append(domain)
        print(row)
    print("**********************************************")


def get_children(in_node_id,Node_map,props):
    Node_map[str(in_node_id)].is_closed = True
    # print("Evaluating Children for: ",in_node_id)
    children = []
    curr_depth = Node_map[str(in_node_id)].depth+1
    row = props.depth_idx[str(curr_depth)][0]
    col = props.depth_idx[str(curr_depth)][1]
    domain = copy.deepcopy(Node_map[str(in_node_id)].state[row][col])
    if not domain:
        remaining_spots = (props.grp_cnt*props.pot_cnt)-curr_depth
        filled_Spots = Node_map[str(in_node_id)].filled_teams
        if ((props.no_teams-filled_Spots)<=remaining_spots):
            # print("******************************Can accommodate empty")
            op_node = create_node(in_node_id, [], Node_map, props)
            Node_map[str(props.node_cnt)] = op_node
            children.append(props.node_cnt)
            # if (props.node_cnt%1000==0):
                # print(props.node_cnt,Node_map[str(props.node_cnt)].depth)
            props.node_cnt += 1
            return children
        else:
            return children

    # Possible Value options
    for i in range(len(domain)):
        child = domain[i]
        op_node = create_node(in_node_id,child,Node_map,props)
        updated_state = consistency_check(op_node.state,in_node_id,child,curr_depth,props)
        if updated_state!="inconsistent":
            op_node.state = updated_state
            Node_map[str(props.node_cnt)] = op_node
            children.append(props.node_cnt)
            # if (props.node_cnt%100==0):
                # print(props.node_cnt,Node_map[str(props.node_cnt)].depth)
            props.node_cnt += 1
    if not children:
        return children
    return children

# Full depth expansion for test
def backtracking(in_node_id,Node_map,props):
    global goal_node
    # if (Node_map[str(in_node_id)].depth==(props.no_teams)):
    if (Node_map[str(in_node_id)].filled_teams==(props.no_teams)):
        # is_goal = goal_check(in_node_id,Node_map,props)
        is_goal = True
        if is_goal:
            print("Goal Found. Reached Maximum Depth")
            goal_node = in_node_id
        return is_goal
    else:
        children = get_children(in_node_id,Node_map,props)
        # print(children)
        if not children:
            return False
        for i in children:
            print("Currently Evaluating: ",(i,Node_map[str(i)].depth))
            print_state(Node_map[str(i)].state,props)
            print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            if Node_map[str(i)].is_closed:
                print("OOPPSS CLOSED")
            if Node_map[str(i)].is_closed==False:
                is_goal = backtracking(i,Node_map,props)
                print("Should i proceed further???",is_goal)
                if is_goal:
                    return is_goal
        return False

#*******************************MAIN****************************#
# Initializing the Root node
root_idx = 0
new_node = Node()
new_node.parent = copy.deepcopy(None)
new_node.id = copy.deepcopy(0)
new_node.depth = copy.deepcopy(0)
new_node.filled_teams = copy.deepcopy(0)
new_node.is_closed = copy.deepcopy(False)
# Initializing state domains for the root node
list = []
for ctr in range(len(teams)):
    list.append(teams[str(ctr)])
rows = []
for i in range(props.grp_cnt):
    cols = []
    for j in range(props.pot_cnt):
        cols.append(list)
    rows.append(cols)
# Applying the Unary constraint of having one value from each pot about the column
for i in range(props.pot_cnt):
    for j in range(props.grp_cnt):
        curr_domain = []
        curr_domain = copy.deepcopy(rows[j][i])
        ctr = 0
        while ctr<len(curr_domain):
            elmnt_rmvd = False
            if (curr_domain[ctr][2]!=props.pot_seq[i]):
                elmnt_rmvd = True
                curr_domain.remove(curr_domain[ctr])
            if not elmnt_rmvd:
               ctr += 1
        rows[j][i] = curr_domain
new_node.state = rows

# Initializing the confederation matrix
new_node.conf_mat = copy.deepcopy([])
rows = []
for i in range(props.grp_cnt):
    col = []
    for j in range(props.pot_cnt):
        col.append("")
    rows.append(col)
print(rows[0][0])
new_node.conf_mat = copy.deepcopy(rows)
Node_map[str(root_idx)] = new_node
props.node_cnt += 1

print("Search Begins")
reply = backtracking(0,Node_map,props)
print ("GOAL REACHED AT NODE",goal_node)
state = Node_map[str(goal_node)].state
goal = []
for a in range(props.grp_cnt):
    row = []
    for b in range(props.pot_cnt):
        if not state[a][b]:
            row.append("Empty")
            continue
        row.append(state[a][b][0][0])
    goal.append(row)
for k in range(len(goal)):
    print(goal[k])
