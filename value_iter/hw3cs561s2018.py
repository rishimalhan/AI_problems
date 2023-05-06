import copy
import numpy as np

inputs = open("input.txt", "r")
input_data = []
i = 0
for line in inputs:
    input_data.append(str(line))
    i += 1


# INITIALIZING MAP, PROPERTIES, POLICY, ACTIONS
class InProp:
    act_set = []
    neighbors = []
    act_idx = []
    term_nodes = []
    node_status = []

    def __init__(self):
        self.n_rows = None
        self.n_cols = None
        self.n_walls = None
        self.n_term = None
        self.p_walk = None
        self.p_run = None
        self.r_walk = None
        self.r_run = None
        self.d_fac = None
        self.acts = None

    def create_map(self, rows, cols):
        self.map = np.zeros((rows, cols), dtype=int)
        return self.map


props = InProp()
props.acts = [
    "Walk Up",
    "Walk Down",
    "Walk Left",
    "Walk Right",
    "Run Up",
    "Run Down",
    "Run Left",
    "Run Right",
    "None",
    "Exit",
]

props.neighbors = np.array(
    [[1, 0], [2, 0], [-1, 0], [-2, 0], [0, -1], [0, -2], [0, 1], [0, 2]], dtype=int
)


props.n_rows = int(input_data[0].rstrip().split(",")[0])
props.n_cols = int(input_data[0].rstrip().split(",")[1])
props.map = props.create_map(props.n_rows, props.n_cols)
props.node_status = np.zeros((props.n_rows, props.n_cols), dtype=int)
iter = 0
act0 = np.empty((props.n_rows, props.n_cols), dtype=int)
# Instantiate the utility map.
pol0 = np.zeros((props.n_rows, props.n_cols), dtype=float)
props.n_walls = int(input_data[1].rstrip())
for i in range(2, 2 + props.n_walls):
    curr_loc = [
        int(input_data[i].rstrip().split(",")[0]) - 1,
        int(input_data[i].rstrip().split(",")[1]) - 1,
    ]
    pol0[curr_loc[0]][curr_loc[1]] = -1
    act0[curr_loc[0]][curr_loc[1]] = 8
    props.map[curr_loc[0]][curr_loc[1]] = -1

props.n_term = int(input_data[2 + props.n_walls].rstrip())
rewards = []
for i in range(2 + props.n_walls + 1, 2 + props.n_walls + 1 + props.n_term):
    curr_loc = [
        int(input_data[i].rstrip().split(",")[0]) - 1,
        int(input_data[i].rstrip().split(",")[1]) - 1,
    ]
    reward = float(input_data[i].rstrip().split(",")[2])
    pol0[curr_loc[0]][curr_loc[1]] = reward
    rewards.append(reward)
    act0[curr_loc[0]][curr_loc[1]] = 9
    props.map[curr_loc[0]][curr_loc[1]] = 1
    props.term_nodes.append([curr_loc[0], curr_loc[1]])

# Sort terminal nodes accoridng to decreasing order of reward
props.term_nodes = [
    props.term_nodes
    for rewards, props.term_nodes in sorted(zip(rewards, props.term_nodes))
]
props.p_walk = float(
    input_data[2 + props.n_walls + 1 + props.n_term].rstrip().split(",")[0]
)
props.p_run = float(
    input_data[2 + props.n_walls + 1 + props.n_term].rstrip().split(",")[1]
)
props.r_walk = float(
    input_data[2 + props.n_walls + 1 + props.n_term + 1].rstrip().split(",")[0]
)
props.r_run = float(
    input_data[2 + props.n_walls + 1 + props.n_term + 1].rstrip().split(",")[1]
)
props.d_fac = float(input_data[2 + props.n_walls + 1 + props.n_term + 2].rstrip())
##############################INITIALIZATION COMPLETE############################


def get_utilities(state, curr_policy, props, action_data):
    acts = action_data[state[0]][state[1]]
    utilities = []
    ######## WALK
    p = 0.5 * (1.0 - props.p_walk)
    a = p * curr_policy[acts[2][0]][acts[2][1]]
    b = p * curr_policy[acts[3][0]][acts[3][1]]
    c = p * curr_policy[acts[0][0]][acts[0][1]]
    d = p * curr_policy[acts[1][0]][acts[1][1]]
    sum = 0.0
    # Walk Up
    sum += props.p_walk * curr_policy[acts[0][0]][acts[0][1]]
    sum += a
    sum += b
    utilities.append(props.r_walk + (props.d_fac * sum))

    sum = 0.0
    # Walk Down
    sum += props.p_walk * curr_policy[acts[1][0]][acts[1][1]]
    sum += a
    sum += b
    utilities.append(props.r_walk + (props.d_fac * sum))

    sum = 0.0
    # Walk Left
    sum += props.p_walk * curr_policy[acts[2][0]][acts[2][1]]
    sum += c
    sum += d
    utilities.append(props.r_walk + (props.d_fac * sum))

    sum = 0.0
    # Walk Right
    sum += props.p_walk * curr_policy[acts[3][0]][acts[3][1]]
    sum += c
    sum += d
    utilities.append(props.r_walk + (props.d_fac * sum))

    ######## RUN
    p = 0.5 * (1.0 - props.p_run)
    a = p * curr_policy[acts[6][0]][acts[6][1]]
    b = p * curr_policy[acts[7][0]][acts[7][1]]
    c = p * curr_policy[acts[4][0]][acts[4][1]]
    d = p * curr_policy[acts[5][0]][acts[5][1]]
    sum = 0.0
    # Run Up
    sum += props.p_run * curr_policy[acts[4][0]][acts[4][1]]
    sum += a
    sum += b
    utilities.append(props.r_run + (props.d_fac * sum))

    sum = 0.0
    # Run Down
    sum += props.p_run * curr_policy[acts[5][0]][acts[5][1]]
    sum += a
    sum += b
    utilities.append(props.r_run + (props.d_fac * sum))

    sum = 0.0
    # Run Left
    sum += props.p_run * curr_policy[acts[6][0]][acts[6][1]]
    sum += c
    sum += d
    utilities.append(props.r_run + (props.d_fac * sum))

    sum = 0.0
    # Run Right
    sum += props.p_run * curr_policy[acts[7][0]][acts[7][1]]
    sum += c
    sum += d
    utilities.append(props.r_run + (props.d_fac * sum))

    return utilities


def run_validity(curr_row, curr_col, nxt_row, nxt_col, props):
    if curr_row == nxt_row:
        if nxt_col > curr_col and props.map[nxt_row][nxt_col - 1] == -1:
            return False
        if nxt_col < curr_col and props.map[nxt_row][nxt_col + 1] == -1:
            return False
    else:
        if nxt_row > curr_row and props.map[nxt_row - 1][nxt_col] == -1:
            return False
        if nxt_row < curr_row and props.map[nxt_row + 1][nxt_col] == -1:
            return False
    return True


def boundary_viol(nxt_row, nxt_col, props):
    if nxt_row < 0 or nxt_col < 0:
        return True
    elif nxt_row > (props.n_rows - 1) or nxt_col > (props.n_cols - 1):
        return True
    elif props.map[nxt_row][nxt_col] == -1:
        return True
    else:
        return False


def get_neighbors(curr_row, curr_col, action_data):
    neighbors = []
    acts = action_data[curr_row][curr_col]
    for i in range(0, 8):
        poss_nghbr = acts[i]
        if props.node_status[poss_nghbr[0]][poss_nghbr[1]] == 1:
            continue
        else:
            neighbors.append(poss_nghbr)
            props.node_status[poss_nghbr[0]][poss_nghbr[1]] = 1
    return neighbors


#################### Precomputing where my actions lead me ####################################
action_data = []
for i in range(props.n_rows):
    row = []
    for j in range(props.n_cols):
        actions = []
        # WALK
        for k in [0, 2, 4, 6]:
            nxt_row = i + props.neighbors[k][0]
            nxt_col = j + props.neighbors[k][1]
            if not boundary_viol(nxt_row, nxt_col, props):
                actions.append([nxt_row, nxt_col])
            else:
                actions.append([i, j])
        # RUN
        for k in [1, 3, 5, 7]:
            nxt_row = i + props.neighbors[k][0]
            nxt_col = j + props.neighbors[k][1]
            if not boundary_viol(nxt_row, nxt_col, props) and run_validity(
                i, j, nxt_row, nxt_col, props
            ):
                actions.append([nxt_row, nxt_col])
            else:
                actions.append([i, j])
        row.append(actions)
    action_data.append(row)
###################################### MAIN #############################################
################################## RIPPLE MOVEMENT ALGORITHM ############################

# Take coord from open list. Evaluate Utility. IF wall or terminal, it continues.
# Once evaluated, close the node in the map.
# Get neighbors for this cell. Put them in temporary list and continue to next
flag = True
count = 0
max_count = 3
curr_pol = copy.deepcopy(pol0)
nxt_act = copy.deepcopy(act0)
nxt_pol = copy.deepcopy(pol0)

while flag:
    open_list = copy.copy(props.term_nodes)
    while open_list:
        curr_cell = open_list[0]
        del open_list[0]
        i = curr_cell[0]
        j = curr_cell[1]
        if props.map[i][j] != -1 and props.map[i][j] != 1:
            utilities = get_utilities([i, j], nxt_pol, props, action_data)
            index = utilities.index(max(utilities))
            nxt_act[i][j] = index
            nxt_pol[i][j] = utilities[index]
        neighbors = get_neighbors(i, j, action_data)
        if neighbors:
            open_list.extend(neighbors)

    iter += 1
    if np.array_equal(curr_pol, nxt_pol):
        if count > 0:
            prev_mark = mark_iter
        mark_iter = iter
        count += 1
        if count > 1:
            if (mark_iter - prev_mark) > 1:
                count = 0
    if count == max_count:
        flag = False
    curr_pol = copy.deepcopy(nxt_pol)
    props.node_status = np.zeros((props.n_rows, props.n_cols), dtype=float)


def write_to_file(nxt_act):
    op_file = open("output.txt", "w+")
    for i in range(props.n_rows):
        for j in range(props.n_cols):
            curr_line = props.acts[nxt_act[nxt_act.shape[0] - i - 1][j]]
            op_file.write(curr_line)
            if j < nxt_act.shape[1] - 1:
                op_file.write(",")
        if i < nxt_act.shape[0] - 1:
            op_file.write("\n")
    op_file.close()


write_to_file(nxt_act)
