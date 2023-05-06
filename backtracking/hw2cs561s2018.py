import copy
import random
from Queue import PriorityQueue
import time

exit_flag = False
inputs = open("input.txt", "r")
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
        self.clock_strt = None
        self.clock_stamp = None
        self.clock_tot = None
        self.brk_pt = None
        return


# *********************************READING INPUTS BEGINS*******************************************#
global goal_node
goal_node = None
props = IpProp()
props.grp_cnt = int(input_data[0])
props.pot_cnt = int(input_data[1])
props.filled_teams = 0

# Assigning the pots to pot array
for i in range(2, 2 + props.pot_cnt):
    props.pots.append(input_data[i].rstrip().split(","))
# Assigning the confederations
for i in range(2 + props.pot_cnt, 2 + props.pot_cnt + 6):
    props.conf[str(input_data[i].split(":")[0])] = (
        input_data[i].split(":")[1].rstrip().split(",")
    )


# *********************************READING INPUTS ENDS*******************************************#
# Prioritize pots according to diversity
def diversity(props, team_info):
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
        queue.put([div_sum[i], i])
    updated_pots = []
    pot_seq = []
    for i in range(props.pot_cnt):
        curr_idx = int(queue.get()[1])
        pot_seq.append(curr_idx)
        updated_pots.append(props.pots[curr_idx])
    return updated_pots, pot_seq


# Collecting all teams with their corresponding confederation and pot in dictionary
teams = {}
team_info = {}  # Stores information of a team as Confederation and Pot Number
counter = 0
for confederation in ["AFC", "CAF", "OFC", "CONCACAF", "CONMEBOL", "UEFA"]:
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
props.pots, props.pot_seq = diversity(props, team_info)
list_of_teams = copy.deepcopy(teams)


def randomize_teams(teams):
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
    return updated_teams


##########################################EVALUATING RUBBISH CASES##################################
# Checking for Max number of teams in a pot greater than number of groups.
max_teams = 0
for i in range(props.pot_cnt):
    max_teams = max(max_teams, len(props.pots[i]))
if max_teams > props.grp_cnt:
    exit_flag = True
# Checking for teams in UEFA greater than twice the number of groups.
for confederation in ["AFC", "CAF", "OFC", "CONCACAF", "CONMEBOL", "UEFA"]:
    if "UEFA" in props.conf[confederation]:
        if len(props.conf[confederation]) > props.grp_cnt * 2:
            exit_flag = True


class Node(object):
    def __init__(self):
        self.parent = None
        self.id = None
        self.depth = None
        self.state = None
        self.conf_mat = None
        self.filled_teams = None
        return


props.depth_idx = {}  # DONOT Randomize
counter = 1
for i in range(props.pot_cnt):
    for j in range(props.grp_cnt):
        props.depth_idx[str(counter)] = [j, i]
        counter += 1


def create_node(in_parent, in_value, Node_map, props):
    new_node = Node()
    new_node.parent = copy.deepcopy(in_parent)
    new_node.id = copy.deepcopy(props.node_cnt)
    curr_depth = Node_map[str(in_parent)].depth + 1
    curr_fill_teams = Node_map[str(in_parent)].filled_teams + 1
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


def consistency_check(in_state, parent, in_var, depth, props):
    # This should take the node, update the domains of the node and if consistency
    # is lost, then returns inconsistent which will not store the Node in possible actions
    # in get children function

    row = props.depth_idx[str(depth)][0]
    col = props.depth_idx[str(depth)][1]
    # Removing this country from current col domains
    for i in range(props.grp_cnt):
        if i == row:
            continue
        curr_domain = copy.deepcopy(in_state[i][col])
        if in_var in curr_domain:
            curr_domain.remove(in_var)
            in_state[i][col] = curr_domain

    curr_conf = in_var[1]
    if curr_conf == "UEFA":
        no_uefa = Node_map[str(parent)].conf_mat[row].count("UEFA")
        if no_uefa > 1:
            return "inconsistent"
        elif no_uefa == 1:
            for i in range(col + 1, props.pot_cnt):
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
            for i in range(col + 1, props.pot_cnt):
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
    return in_state


def get_children(in_node_id, Node_map, props):
    children = []
    curr_depth = Node_map[str(in_node_id)].depth + 1
    row = props.depth_idx[str(curr_depth)][0]
    col = props.depth_idx[str(curr_depth)][1]
    domain = copy.deepcopy(Node_map[str(in_node_id)].state[row][col])
    if not domain:
        remaining_spots = (props.grp_cnt * props.pot_cnt) - curr_depth
        filled_Spots = Node_map[str(in_node_id)].filled_teams
        if (props.no_teams - filled_Spots) <= remaining_spots:
            op_node = create_node(in_node_id, [], Node_map, props)
            Node_map[str(props.node_cnt)] = op_node
            children.append(props.node_cnt)
            props.node_cnt += 1
            return children
        else:
            return children

    # Possible Value options
    for i in range(len(domain)):
        child = domain[i]
        op_node = create_node(in_node_id, child, Node_map, props)
        updated_state = consistency_check(
            op_node.state, in_node_id, child, curr_depth, props
        )
        if updated_state != "inconsistent":
            op_node.state = updated_state
            Node_map[str(props.node_cnt)] = op_node
            children.append(props.node_cnt)
            props.node_cnt += 1
    if not children:
        return children
    updated_children = []
    # Randomize the children generated
    while len(children) != 0:
        curr_choice = random.choice(children)
        updated_children.append(curr_choice)
        children.remove(curr_choice)
    children = updated_children
    return children


def goal_checker(state, team_info, props):
    teams_in_goal = 0
    for i in range(props.grp_cnt):
        for j in range(props.pot_cnt):
            if not state[i][j]:
                continue
            curr_val = state[i][j][0][0]
            if curr_val:
                teams_in_goal += 1
                curr_conf = team_info[curr_val][0]
                curr_pot = team_info[curr_val][1]
                if curr_pot != props.pot_seq[j]:
                    return False
                for confederation in [
                    "AFC",
                    "CAF",
                    "OFC",
                    "CONCACAF",
                    "CONMEBOL",
                    "UEFA",
                ]:
                    if confederation != "UEFA":
                        conf_counter = curr_val.count(confederation)
                        if conf_counter > 1:
                            return False
                    else:
                        conf_counter = curr_val.count(confederation)
                        if conf_counter > 2:
                            return False
    if teams_in_goal != props.no_teams:
        return False
    return True


# Full depth expansion for test
def backtracking(in_node_id, Node_map, props, team_info):
    props.clock_stamp = time.time()
    global goal_node
    if (props.clock_stamp - props.clock_strt) > props.brk_pt:
        props.clock_tot += props.clock_stamp - props.clock_strt
        is_goal = "exit"
        return is_goal
    if Node_map[str(in_node_id)].filled_teams == (props.no_teams):
        is_goal = goal_checker(Node_map[str(in_node_id)].state, team_info, props)
        if is_goal:
            goal_node = in_node_id
        return is_goal
    else:
        children = get_children(in_node_id, Node_map, props)
        if not children:
            return False
        for i in children:
            is_goal = backtracking(i, Node_map, props, team_info)
            if is_goal == "exit":
                break
            if is_goal:
                return is_goal
        if is_goal == "exit":
            return "exit"
        return False


def initialize_root(Node_map, teams, props):
    props.node_cnt = 0
    # Initializing the Root node
    root_idx = 0
    new_node = Node()
    new_node.parent = copy.deepcopy(None)
    new_node.id = copy.deepcopy(0)
    new_node.depth = copy.deepcopy(0)
    new_node.filled_teams = copy.deepcopy(0)
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
            while ctr < len(curr_domain):
                elmnt_rmvd = False
                if curr_domain[ctr][2] != props.pot_seq[i]:
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
    new_node.conf_mat = copy.deepcopy(rows)
    Node_map[str(root_idx)] = new_node
    props.node_cnt += 1


def write_to_file(state, props):
    op_file = open("output.txt", "w+")
    if state == "No":
        op_file.write("No")
    else:
        op_file.write("Yes" + "\n")
        for a in range(props.grp_cnt):
            row = []
            for b in range(props.pot_cnt):
                if not state[a][b]:
                    continue
                row.append(state[a][b][0][0])
            if not row:
                op_file.write("None")
            else:
                for ctr in range(len(row)):
                    op_file.write(row[ctr])
                    if ctr < len(row) - 1:
                        op_file.write(",")
            if a < (props.grp_cnt - 1):
                op_file.write("\n")
    op_file.close()


# *****************************************************************************MAIN***************************************************************************#
if not exit_flag:
    props.brk_pt = 15
    props.clock_tot = 0
    reply = "exit"
    trial = 1
    while (props.clock_tot < 165) and (reply == "exit"):
        props.clock_strt = time.time()
        Node_map = {}
        teams = randomize_teams(list_of_teams)
        initialize_root(Node_map, teams, props)
        reply = backtracking(0, Node_map, props, team_info)
        trial += 1
    if reply == True:
        state = Node_map[str(goal_node)].state
        write_to_file(state, props)

    else:
        write_to_file("No", props)
else:
    write_to_file("No", props)
