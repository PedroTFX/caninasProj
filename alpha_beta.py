# alpha beta pruning tree search
# this is a tree search algorithm that uses alpha beta pruning to reduce the number of nodes that need to be evaluated in a minimax search tree
# it should print the alpha beta values for each node in the tree letting know when there was a pruning

# The tree is represented as a dictionary where the key is the node name and the value is a list of children nodes


def alpha_beta_search(node, depth, alpha, beta, maximizing_player, prunning=False):
    if depth == 0 or not node:
        return 0

    if maximizing_player:
        value = float('-inf')
        for child in node:
            value = max(value, alpha_beta_search(node[child], depth - 1, alpha, beta, False, prunning))
            alpha = max(alpha, value)
            print(f"Node: {child}, Alpha: {alpha}, Beta: {beta}")
            if alpha >= beta and prunning:
                print(f"Pruned at node {child}")
                break
        return value
    else:
        value = float('inf')
        for child in node:
            value = min(value, alpha_beta_search(node[child], depth - 1, alpha, beta, True, prunning))
            beta = min(beta, value)
            print(f"Node: {child}, Alpha: {alpha}, Beta: {beta}")
            if alpha >= beta and prunning:
                print(f"Pruned at node {child}")
                break
        return value
    
    
# def minmax that prints the values of each node
def minmax(node, depth, maximizing_player):
    if depth == 0 or not node:
        # print(f"Value: {node}")
        return node

    if maximizing_player:
        value = float('-inf')
        for child in node: 
            # value_of_child = minmax(node[child], depth - 1, False)
            # value = max(value, value_of_child)
            # print(f"Node: {child}-{value_of_child}, Min: {value}")

            value1 = minmax(node[child], depth - 1, False)
            value = max(value, value1)
            print(f"Node: {child} - {value1}, Min: {value}")
        return value
    else:
        value = float('inf')
        for child in node:
            # value_of_child = minmax(node[child], depth - 1, False)
            # value = min(value, value_of_child)
            # print(f"Node: {child}-{value_of_child}, Max: {value}")
            value1 = minmax(node[child], depth - 1, True)
            value = min(value, value1)
            print(f"Node: {child} - {value1}, Max: {value}")
        return value
    
# Example tree
tree = {
    'A': {'B': {'D': 0, 'E': 1}, 'C': {'F': 5, 'G': 2}}
}



F = { 'N':8, 'O':5}
E = { 'L':2, 'M':3}
G = { 'P':7, 'Q':6}

H= { 'R':0, 'S':1}
I= { 'T':5, 'U':2}

J = { 'V':8, 'W':4}
K = { 'X':10, 'Y':2}

D = { 'J':J, 'K':K}
C = { 'H':H, 'I':I}
B = { 'E':E, 'F':F, 'G':G}

A = {'A': {'B': B, 'C':C, 'D':D}} 

tree = A


# alpha_beta_search(tree, 3, float('-inf'), float('inf'), False, False)
minmax(tree, 4, True)

