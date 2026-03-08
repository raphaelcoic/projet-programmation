"""
This is the graph module. It contains the classes Graph and GraphImplicit
"""
import math


class Graph:
    """
    A minimal class for directed weighted graph represented as adjacency list. 
    
    Attributes: 
    -----------
    edges: dict
        A dictionary that contains the list of neighbors of each node with its weight.
        Ex: edges = {v0: [(v1, 21), (v2, 12)], 
                     v1: [(v0, 74), (v2, 32)], 
                     ...}

    Methods: 
    --------
    neighbours(self, node): 
        Returns the list of all neighbors of a node
    """

    def __init__(self, edges):
        self._edges = edges

    def neighbours(self, node):
        if node not in self._edges:
            return []
        return self._edges[node]
### Ici edges est un dictionnaire, et la fonction neighbours renvoie la liste des voisins du node, qui est
### une clé du dictionnaire edges

    def shortest_path(self, start, end): ### ici start et end sont des noeuds
        """
        Finds the shortest path between start and end nodes using Dijkstra's algorithm.

        Parameters:
        -----------
        start: node
            Starting node
        end: node
            Target node

        Returns:
        --------
        tuple (distance, path)
            distance: shortest distance from start to end
            path: list of nodes forming the shortest path
        """
        if (start not in self._edges
                or end not in {dest for neighbors in self._edges.values()
                                 for dest, _ in neighbors}):
            return math.inf, []

        # Initialize distances and predecessors
        nodes = set(self._edges.keys())
        distances = {node: math.inf for node in nodes}
        distances[start] = 0
        predecessors = {node: None for node in nodes}
        visited = set()

        while True:
            current = min(
                (node for node in distances if node not in visited),
                key=lambda x: distances[x],
                default=None,
            )

            if current is None or distances[current] == math.inf:
                return math.inf, []

            if current == end:
                break

            visited.add(current)

            # Update distances to neighbors
            for dest, length in self.neighbours(current):
                if dest in visited:
                    continue
                distance = distances[current] + length
                if distance < distances.get(dest, math.inf):
                    distances[dest] = distance
                    predecessors[dest] = current

        # Reconstruct path
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = predecessors.get(current, None)
        path.reverse()

        return distances[end], path

class GraphImplicit(Graph):
    def __init__(self, edges, fonction_neighbours):
        super().__init__(edges)
        self.neighbours = fonction_neighbours


