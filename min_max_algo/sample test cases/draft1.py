# HomeWork 1. Authored by Rishi Malhan
import copy
from Queue import PriorityQueue

inputs = open("input.txt","r")
input_data = []
i = 0
for line in inputs:
    input_data.append(str(line))
    i += 1

grid = []

for i in range(len(input_data[3:(len(input_data)-1)])):
    curr_row = input_data[i+3].split(",")
    grid.append(curr_row)


global Nodes
global node_count
global row_alphabets
global max_player
global min_player
global max_depth
global row_values
global algorithm
algorithm = input_data[1].rstrip()
row_values = []
row_utility = input_data[11].split(",")
for i in range(len(row_utility)):
    row_values.append(int(row_utility[i]))
max_depth = int(input_data[2].rstrip())
Nodes  = {}
node_count = -1
row_alphabets = ['H','G','F','E','D','C','B','A']
max_player = input_data[0].rstrip()

if (max_player=="Star"):
    min_player = "Circle"
else:
    min_player = "Star"


# Function get_actions. Input is the current state of board and player
# and it gives out the possible actions to be taken in the form of a grid.

class node(object):
    def __init__(self):
        self.id = None
        self.utility = None
        self.state = []
        self.pass_status = False
        self.parent = None
        self.depth = None
        self.plyr_lost = False
        self.eog = False
        self.init_pos = None
        self.final_pos = None
        self.is_explored = None
        return

def get_actions(curr_state,player,parent):
    global node_count
    global Nodes
    global depth
    action_nodes = []

# Assign the Initial positions of Star and Circle players to lists.
# Note that these values are already sorted
    star_pos = []   # Current Positions of star player
    circ_pos = []  # Current Positions of circle player
    for i in range(len(curr_state[0])):
        for j in range(len(curr_state[0])):
            if (curr_state[i][j].rstrip()!=str(0)):
                if(curr_state[i][j][0]=='S'):
                    star_pos.append([i,j])

                if (curr_state[i][j][0] == 'C'):
                    circ_pos.append([i, j])

# Taking action depending on which player is playing
    if (player=="Star"):
        curr_player = star_pos
        row_incr = -1
        sec_last = 1
        third_last = 2
        lst_row = 0
        myself = 'S'
        opp = 'C'

    elif (player=="Circle"):
        curr_player = circ_pos
        row_incr = 1
        sec_last = 6
        third_last = 5
        lst_row = 7
        myself = 'C'
        opp = 'S'

    if not curr_player:
        Nodes[str(parent)].plyr_lost = True   # Player doesnot exist. End of Game
        Nodes[str(parent)].eog = True
        return action_nodes

    for i in range(len(curr_player)):
        curr_col = curr_player[i][1]
        curr_row = curr_player[i][0]
        # Last Row check
        if(curr_player[i][0]==lst_row):
            continue
        # Check if second last row is reached
        if (curr_player[i][0] == sec_last):
            a = 1
            for count in range(0, 2):
                # Corner cases where a move will be out of the board
                if ( (curr_col - a < 0) or (curr_col - a > 7) ):
                    a *= -1
                    continue
                if (curr_state[curr_row+row_incr][curr_col-a][0].rstrip()==myself):
                    no_plyr = int(curr_state[curr_row + row_incr][curr_col - a][1].rstrip()) + 1
                    node_id = create_node(curr_state, curr_player[i], [curr_row + row_incr, curr_col - a],parent)
                    action_nodes.append(node_id)
                    Nodes[str(node_id)].state[curr_row + row_incr][curr_col - a] = (myself + str(no_plyr))
                if (curr_state[curr_row+row_incr][curr_col-a].rstrip() == str(0)):
                    node_id = create_node(curr_state, curr_player[i], [curr_row + row_incr, curr_col - a],parent)
                    action_nodes.append(node_id)
                a *= -1
            continue
        # Check if third last row is reached
        if (curr_player[i][0] == third_last):
            a = 1
            for count in range(0, 2):
                # Corner cases where a move will be out of the board
                if ( ((curr_col - a) >= 0) and ((curr_col - a) <= 7) ):
                    if (curr_state[curr_row + row_incr][curr_col - a].rstrip() == str(0)):
                        action_nodes.append(create_node(curr_state, curr_player[i], [curr_row + row_incr, curr_col - a], parent))
                    if (curr_state[curr_row + row_incr][curr_col - a][0].rstrip() == opp):
                        if ( (curr_col - a * 2 < 0) or (curr_col - a * 2 > 7) ):
                            a *= -1
                            continue
                        if (curr_state[curr_row + row_incr*2][curr_col - a*2].rstrip()=='0'):
                            node_id = create_node(curr_state, curr_player[i], [curr_row + row_incr*2, curr_col - a*2],parent)
                            action_nodes.append(node_id)
                            Nodes[str(node_id)].state[curr_row + row_incr][curr_col - a] = '0'
                        if (curr_state[curr_row + row_incr*2][curr_col - a*2][0].rstrip() == myself):
                            no_plyr = int(curr_state[curr_row + row_incr*2][curr_col - a*2][1].rstrip()) + 1
                            node_id = create_node(curr_state, curr_player[i], [curr_row + row_incr*2, curr_col - a*2],parent)
                            action_nodes.append(node_id)
                            Nodes[str(node_id)].state[curr_row + row_incr*2][curr_col - a*2] = (myself + str(no_plyr))
                            Nodes[str(node_id)].state[curr_row + row_incr][curr_col - a] = '0'
                a *= -1
            continue
        # For every other case:
        # Tie Breaker
        a = 1
        for count in range(0, 2):
            if (curr_col - a >=0 and curr_col - a <8):
                if (curr_state[curr_row + row_incr][curr_col - a].rstrip() == '0'):
                    action_nodes.append(create_node(curr_state, curr_player[i], [curr_row + row_incr, curr_col - a],parent))
                if (curr_state[curr_row + row_incr][curr_col - a][0].rstrip() == opp):
                    if (curr_col - a*2 >= 0 and curr_col - a*2 < 8):
                        if (curr_state[curr_row + row_incr*2][curr_col - a*2].rstrip() == '0'):
                            node_id = create_node(curr_state, curr_player[i], [curr_row + row_incr*2, curr_col - a*2],parent)
                            action_nodes.append(node_id)
                            Nodes[str(node_id)].state[curr_row + row_incr][curr_col - a] = '0'
            a *= -1
    if action_nodes:
        action_nodes = tie_breaker(action_nodes)
    return action_nodes

def tie_breaker(action_nodes):
    priority_no = []
    updated_nodes = []
    for i in action_nodes:
        row = Nodes[str(i)].final_pos[0]
        col = Nodes[str(i)].final_pos[1]
        priority_no.append(8*row + col)
    queue = PriorityQueue(maxsize=0)
    for i in range(len(action_nodes)):
        queue.put([priority_no[i], str(action_nodes[i])])
    for i in range(len(action_nodes)):
        updated_nodes.append(int(queue.get()[1]))
    return updated_nodes


def create_node(curr_state,init_sq,final_sq,parent):
    global node_count
    global Nodes
    node_count += 1
    new_node = node()
    new_node.id = copy.deepcopy(node_count)
    new_node.map_key = str(copy.deepcopy(node_count))
    new_node.state = copy.deepcopy(curr_state)
    new_node.parent = copy.deepcopy(parent)
    new_node.init_pos = copy.deepcopy(init_sq)
    new_node.final_pos = copy.deepcopy(final_sq)
    new_node.is_explored = False
    if node_count != 0:
        new_node.depth = Nodes[str(parent)].depth + 1
    else:
        new_node.depth = 0
    if (init_sq and final_sq):
        temp = new_node.state[init_sq[0]][init_sq[1]]
        new_node.state[init_sq[0]][init_sq[1]] = '0'
        new_node.state[final_sq[0]][final_sq[1]] = temp
    for i in range(len(new_node.state)):
        for j in range(len(new_node.state)):
            new_node.state[i][j] = new_node.state[i][j].rstrip()
    Nodes[str(node_count)] = new_node
    return new_node.id



def is_terminal(node_id,player):
    global Nodes
    global max_depth
    global node_count

    depth = Nodes[str(node_id)].depth
    if (depth == max_depth):
        return True
    node_state = Nodes[str(node_id)].state
    actions = get_actions(node_state,player,node_id)
    if(player=="Star"):
        opp = "Circle"
    else:
        opp = "Star"
    if not actions:
        if Nodes[str(node_id)].plyr_lost==True:    # If no players exist
            if (node_id==0):
                Nodes[str(node_id)].eog=True
            return True
        # If both players pass the game
        if Nodes[str(Nodes[str(node_id)].parent)].pass_status==True and Nodes[str(node_id)].pass_status==True:
            Nodes[str(Nodes[str(Nodes[str(node_id)].parent)].parent)].eog = True
            return True
        else:
            if (node_id==0):
                Nodes[str(node_id)].eog = True
            new_id = create_node(Nodes[str(node_id)].state, [], [],node_id)
            Nodes[str(new_id)].pass_status = True
            actions.append(new_id)
            return actions
    else:
        return actions


def get_utility(node_id):
    global Nodes
    global row_values
    global max_player

    node_state = Nodes[str(node_id)].state
    sum_plyr = 0
    sum_opp = 0
    wght_circ = row_values
    wght_star = []
    for i in range(len(wght_circ)):
        wght_star.append(wght_circ[len(wght_circ) - 1 - i])
    if(max_player=="Star"):
        wght_plyr = wght_star
        myself = 'S'
        opp = 'C'
    else:
        wght_plyr = wght_circ
        myself = 'C'
        opp = 'S'
    wght_opp = []
    for i in range(len(wght_plyr)):
        wght_opp.append(wght_plyr[len(wght_plyr) - 1 - i])

    for i in range(len(node_state)):
        for j in range(len(node_state)):
            if(node_state[i][j][0]==myself):
                alpha_player = int(node_state[i][j][1].rstrip())
                sum_plyr = sum_plyr + alpha_player*wght_plyr[i]
            if (node_state[i][j][0] == opp):
                alpha_opp = int(node_state[i][j][1].rstrip())
                sum_opp = sum_opp + alpha_opp*wght_opp[i]
    utility = (sum_plyr - sum_opp)
    Nodes[str(node_id)].utility = utility
    return utility





# Minimax Algorithm
def minimax(input_state):
    global Nodes
    global max_player
    # Creating the First Node as Initial Node
    node_id = create_node(input_state, [], [],0)
    utility = max_value(node_id)
    # Check to see which node has this utility
    frst_children = []
    if (Nodes[str(0)].eog==True):
        nxt_action = "pass"
        farsighted = Nodes[str(1)].utility
        write_to_file(nxt_action, get_utility(1), farsighted, len(Nodes))
    else:
        for i in range(len(Nodes)):
            if (Nodes[str(i)].depth==1):
                frst_children.append(i)
        for i in range(len(frst_children)):
            if (Nodes[str(frst_children[i])].utility == utility):
                nxt_action = frst_children[i]
                farsighted = Nodes[str(nxt_action)].utility
                write_to_file(nxt_action, get_utility(nxt_action), farsighted, len(Nodes))
                break
    # Remember to put a checker for a Pass game.

def max_value(input_node_id):
    global max_player
    global min_player
    global Nodes

    actions = is_terminal(input_node_id, max_player)
    if(actions==True):
        utility = get_utility(input_node_id)
        return utility
    utility = -float("inf")
    for action_node in actions:
        nxt_utility = min_value(action_node)
        if ( nxt_utility > utility ):
            utility = nxt_utility
    Nodes[str(input_node_id)].utility  = utility
    return utility



def min_value(input_node_id):
    global max_player
    global min_player
    global Nodes

    actions = is_terminal(input_node_id, min_player)
    if (actions == True):
        utility = get_utility(input_node_id)
        return utility
    utility = float("inf")
    for action_node in actions:
        nxt_utility = max_value(action_node)
        if (nxt_utility < utility):
            utility = nxt_utility
    Nodes[str(input_node_id)].utility = utility
    return utility



# Alpha-Beta Pruning Algorithm
def ab_pruning(input_state):
    global Nodes
    global max_player
    # Creating the First Node as Initial Node
    node_id = create_node(input_state, [], [],0)
    Nodes[str(0)].is_explored = True
    utility = ab_max(node_id,-float("inf"),float("inf"))
    explored_nodes = 0
    for i in range(len(Nodes)):
        if (Nodes[str(i)].is_explored==True):
            explored_nodes += 1
    # Check to see which node has this utility
    frst_children = []
    if (Nodes[str(0)].eog==True):
        nxt_action = "pass"
        farsighted = Nodes[str(1)].utility
        write_to_file(nxt_action,get_utility(1),farsighted,explored_nodes)
    else:
        for i in range(len(Nodes)):
            if (Nodes[str(i)].depth==1):
                frst_children.append(i)

        for i in range(len(frst_children)):
            if (Nodes[str(frst_children[i])].utility == utility):
                nxt_action = frst_children[i]
                farsighted = Nodes[str(nxt_action)].utility
                write_to_file(nxt_action, get_utility(nxt_action), farsighted, explored_nodes)
                break
    # Remember to put a checker for a Pass game.

def ab_max(input_node_id,alpha,beta):
    global max_player
    global min_player
    global Nodes

    actions = is_terminal(input_node_id, max_player)
    if(actions==True):
        utility = get_utility(input_node_id)
        Nodes[str(input_node_id)].is_explored = True
        return utility
    utility = -float("inf")
    for action_node in actions:
        Nodes[str(action_node)].is_explored = True
        nxt_utility = ab_min(action_node,alpha,beta)
        if ( nxt_utility > utility ):
            utility = nxt_utility
        if (utility >= beta):
            return utility
        alpha = max(utility,alpha)
    Nodes[str(input_node_id)].utility  = utility
    return utility



def ab_min(input_node_id,alpha,beta):
    global max_player
    global min_player
    global Nodes

    actions = is_terminal(input_node_id, min_player)
    if (actions == True):
        utility = get_utility(input_node_id)
        Nodes[str(input_node_id)].is_explored = True
        return utility
    utility = float("inf")
    for action_node in actions:
        Nodes[str(action_node)].is_explored = True
        nxt_utility = ab_max(action_node,alpha,beta)
        if (nxt_utility < utility):
            utility = nxt_utility
        if ( utility<=alpha ):
            return utility
        beta = min(utility,beta)
    Nodes[str(input_node_id)].utility = utility
    return utility

def write_to_file(node, myopic, farsighted_utility, no_nodes):
    global row_alphabets
    global Nodes
    op_file = open("output.txt","w+")
    if (node=="pass"):
        move = node
    else:
        init_sq = str(row_alphabets[Nodes[str(node)].init_pos[0]]) + str(Nodes[str(node)].init_pos[1]+1)
        final_sq = str(row_alphabets[Nodes[str(node)].final_pos[0]]) + str(Nodes[str(node)].final_pos[1]+1)
        move = init_sq + "-" + final_sq
    op_file.write(move+"\n")
    op_file.write(str(myopic)+"\n")
    op_file.write(str(farsighted_utility)+"\n")
    op_file.write(str(no_nodes))
    op_file.close()


if (algorithm=="MINIMAX"):
    minimax(grid)
if (algorithm=="ALPHABETA"):
    ab_pruning(grid)