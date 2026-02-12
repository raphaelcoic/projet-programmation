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

    def shortest_path(self, start, end):
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
        if start not in self._edges or end not in self._edges:
            return math.inf, []

        # Initialize distances and predecessors
        distances = {node: math.inf for node in self._edges}
        distances[start] = 0
        predecessors = {node: None for node in self._edges}
        visited = []

        while len(visited) < len(self._edges):
            current = min((node for node in self.edges if node not in visited), key=lambda x: distances[x],
                          default=None)

            if current == end:
                break

            visited.append(current)

            # Update distances to neighbors
            for neighbor, weight in self.neighbours(current):
                if neighbor not in visited:
                    distance = distances[current] + weight
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        predecessors[neighbor] = current

        # Reconstruct path
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = predecessors[current]
        path.reverse()

        return distances[end], path
