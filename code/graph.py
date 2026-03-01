"""
This is the graph module. It contains the classes Graph and GraphImplicit.
"""
import math

from networkx.algorithms.shortest_paths.generic import \
    shortest_path  # Importing NetworkX's shortest path algorithm, though it's not used here.


class Graph:
    """
    A minimal class for directed weighted graph represented as an adjacency list. 

    Attributes: 
    -----------
    edges: dict
        A dictionary that contains the list of neighbors of each node along with their corresponding weights.
        Example: edges = {v0: [(v1, 21), (v2, 12)], 
                          v1: [(v0, 74), (v2, 32)], 
                          ...}

    Methods: 
    --------
    neighbours(self, node): 
        Returns the list of all neighbors of a particular node.
    shortest_path(self, start, end): 
        Computes the shortest path between two nodes using Dijkstra's algorithm.
    """

    def __init__(self, edges):
        """
        Initializes the Graph with an adjacency list stored in 'edges'.
        
        Parameters:
        -----------
        edges: dict
            Dictionary where keys represent nodes and values are lists of tuples, 
            each containing a neighboring node and the weight of the edge to it.
        """
        self._edges = edges

    def neighbours(self, node):
        """
        Returns the list of neighbors for a given node.

        Parameters:
        -----------
        node: 
            The node whose neighbors need to be fetched.

        Returns:
        --------
        list
            A list of tuples, where each tuple consists of a neighbor and the weight to that neighbor.
            If the node does not exist in the graph, an empty list is returned.
        """
        if node not in self._edges:
            return []
        return self._edges[node]

    def shortest_path(self, start, end):
        """
        Finds the shortest path between start and end nodes using Dijkstra's algorithm.
        
        Dijkstra's algorithm is implemented using a greedy approach:
        1. Initialize distances of all nodes from the start node as infinite (`math.inf`), except the start node itself (distance 0).
        2. Compute the shortest distances iteratively by visiting the unvisited node with the smallest distance.
        3. Update distances to its neighbors if a shorter path is found via the current node.

        Parameters:
        -----------
        start: node
            The starting node of the path.
        end: node
            The target/destination node.

        Returns:
        --------
        tuple:
            A pair (distance, path) where:
            - distance: The minimum distance from start to end. If no path exists, returns `math.inf`.
            - path: A list of nodes forming the shortest path. If no path exists, returns an empty list.
        """
        # Check if start and end nodes are valid in the graph.
        if (start not in self._edges
                or end not in {dest for neighbors in self._edges.values()
                               for dest, _ in neighbors}):
            return math.inf, []

        # Initialize distances, predecessors, and visited status for all nodes.
        distances = {start: 0}  # Distance to the starting node is 0.
        predecessors = {}  # Tracks the previous node in the shortest path.
        visited = {}  # Tracks whether a node has been visited.

        while True:
            # Find the unvisited node with the smallest distance.
            current = min((node for node in distances.keys() if not visited.get(node, False)),
                          key=lambda x: distances[x], default=None)

            # If no node can be reached or the smallest distance is infinity, terminate (no path exists).
            if current is None or distances[current] == math.inf:
                return math.inf, []

            # If the current node is the destination, terminate.
            if current == end:
                break

            visited[current] = True  # Mark the current node as visited.

            # Update distances and predecessors for each neighbor of the current node.
            for dest, length in self.neighbours(current):
                if not visited.get(dest, False):  # Only consider unvisited nodes.
                    distance = distances[current] + length
                    # Check if this path offers a shorter distance.
                    if distance < distances.get(dest, math.inf):
                        distances[dest] = distance
                        predecessors[dest] = current

        # Reconstruct the shortest path from end to start using the predecessors dictionary.
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = predecessors.get(current, None)
        path.reverse()  # Reverse the path to get it from start to end.

        return distances[end], path


class GraphImplicit(Graph):
    """
    A subclass of Graph that supports graphs with implicitly defined neighbors.

    In addition to storing an adjacency list explicitly, this class allows the definition of
    a custom function `fonction_neighbours` that dynamically computes the neighbors of a node.

    Attributes:
    -----------
    edges: dict
        A standard adjacency list for the graph.
    fonction_neighbours: function
        A user-provided function that calculates the neighbors of a node dynamically.

    Methods:
    --------
    neighbours(self, node):
        Overrides the `neighbours` method to use the custom `fonction_neighbours` function.
    """

    def __init__(self, edges, fonction_neighbours):
        """
        Initializes the implicit graph with both an adjacency list and a neighbor function.

        Parameters:
        -----------
        edges: dict
            Standard adjacency list for explicitly defined parts of the graph.
        fonction_neighbours: function
            A function that dynamically computes the neighbors of a node. This allows for
            representing large or infinite graphs without explicitly enumerating all edges.
        """
        # Call the parent Graph constructor to initialize the adjacency list.
        super().__init__(edges)
        # Override the `neighbours` method with the provided custom function.
        self.neighbours = fonction_neighbours
