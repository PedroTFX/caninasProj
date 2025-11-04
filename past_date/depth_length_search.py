from collections import deque

def bfs_with_frontier_and_expansion(graph, start, goal):
    """
    Perform BFS, printing the frontier and expanded nodes at each step.

    :param graph: dict representing the graph as an adjacency list with step costs (node -> [(neighbor, cost)]).
    :param start: starting node.
    :param goal: goal node.
    """
    frontier = deque([start])  # Queue for BFS
    explored = set()  # Set of explored nodes to prevent loops

    print("\nStarting Breadth-First Search\n")

    while frontier:
        # Print the current state of the frontier
        print(f"Frontier: {list(frontier)}")

        # Pop the first node from the frontier
        current_node = frontier.popleft()
        print(f"Expanding: {current_node}")

        # Add the node to the explored set
        explored.add(current_node)
        print(f"Explored so far: {list(reversed(list(explored)))}\n")

        # If the goal is found, stop the search
        if current_node == goal:
            print(f"Goal {goal} reached!\n")
            return

        # Add neighbors to the frontier if they haven't been explored or are not already in the frontier
        for neighbor, cost in sorted(graph.get(current_node, []), key=lambda x: x[0]):
            if neighbor not in explored and neighbor not in frontier:
                frontier.append(neighbor)

    print("Goal not found.")

# Example graph represented as an adjacency list
# Each node points to a list of (neighbor, cost) pairs
graph = {
    'M': [('A', 5), ('B', 3), ('D', 4), ('E', 21)],
    'B': [('A', 1), ('C', 12), ('M', 3)],
    'A': [('B', 1), ('M', 5), ('R', 30)],
    'D': [('M', 4), ('R', 8)],
    'E': [('M', 21), ('R', 2)],
    'C': [('B', 12), ('R', 6)],
    'R': [('A', 30), ('C', 6), ('D', 8), ('E', 2)]
}

# Ensure all connections in the graph are sorted alphabetically by neighbor
graph = {node: sorted(neighbors, key=lambda x: x[0]) for node, neighbors in graph.items()}

# Perform BFS from M to R
bfs_with_frontier_and_expansion(graph, 'M', 'R')
