"""
This is the graph module. It contains the classes Graph and GraphImplicit.
"""
import math
import graphviz

from networkx.algorithms.shortest_paths.generic import \
    shortest_path  # Importing NetworkX's shortest path algorithm, though it's not used here.
from pip._internal.commands import index


class Graph:
    """
    A minimal class for directed weighted graph represented as an adjacency list.

    Attributes: 
    -----$------
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
        self.distances = {}
        self.predecessors = {}  # Tracks the previous node in the shortest path.


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


    def shortest_path(self, start, end, initial_distance = 0):
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

        # Initialize distances, and visited status for all nodes.
        self.distances[(start, 1)] = initial_distance  # Distance to the starting node is 0.
        visited = {}  # Tracks whether a node has been visited.

        while True:
            # Find the unvisited node with the smallest estimated total cost (A*: g + h).
            current = min((node for node in self.distances.keys() if not visited.get(node, False)),
                          key=lambda x: self.distances[x] + self.heuristic(x, end), default=None)

            # If no node can be reached or the smallest distance is infinity, terminate (no path exists).
            if current is None or self.distances[current] == math.inf:
                return math.inf, []

            # If the current node is the destination, terminate.
            if current[0] == end:
                break

            visited[current] = True  # Mark the current node as visited.

            if not self._is_pareto_dominated(current):
                # Update distances and predecessors for each neighbor of the current node.
                for dest, length in self.neighbours(current):
                    if not visited.get(dest, False):  # Only consider unvisited nodes.
                        distance = self.distances[current] + length
                        # Check if this path offers a shorter distance.
                        if distance < self.distances.get(dest, math.inf):
                            self.distances[dest] = distance
                            self.predecessors[dest] = current


        # Reconstruct the shortest path from end to start using the predecessors dictionary.
        ends = [(v, f) for v, f in self.distances.keys() if v == end]
        end1 = min((node for node in ends), key=lambda x: self.distances[x])
        path = self._path(end1)

        return self.distances[end1], path, ends


    def _path(self, v):
        path = []
        current = v
        while current is not None:
            if type(current) is tuple:
                path.append(current[0])
            else:
                path.append(current)
            current = self.predecessors.get(current, None)
        path.reverse()
        return path

    def _is_pareto_dominated(self, node):
        v, fatigue = node
        distance = self.distances[(v, fatigue)]
        for (s, f), d in self.distances.items():
            if s == v and ((d > distance and f >= fatigue) or (d >= distance and f > fatigue)):
                return True
        return False

    def heuristic(self, node, end):
        """
        Minoration du coût restant de node jusqu'à end.

        Dijkstra sur self._edges (graphe simplifié, longueurs seulement) en
        partant de la fatigue du nœud courant et en l'incrémentant de 1 à
        chaque arête.  Comme la vraie fatigue croît d'au moins 1 par arête,
        cela fournit une minoration admissible (heuristique de type A*).
        """
        if node == end:
            return 0

        if isinstance(node, tuple):
            v, f = node
        else:
            v, f = node, 1

        if v not in self._edges:
            return 0

        heur_dist = {(v, f): 0}
        heur_visited = set()

        while True:
            current = min(
                (s for s in heur_dist if s not in heur_visited),
                key=lambda s: heur_dist[s],
                default=None
            )

            if current is None or heur_dist[current] == math.inf:
                return math.inf

            if current == end:
                return heur_dist[current]

            heur_visited.add(current)

            curr_v, curr_f = current if isinstance(current, tuple) else (current, f)

            for dest, length in self._edges.get(curr_v, []):
                cost = length * curr_f
                new_state = end if dest == end else (dest, curr_f + 1)
                new_dist = heur_dist[current] + cost
                if new_dist < heur_dist.get(new_state, math.inf):
                    heur_dist[new_state] = new_dist


    def _ends_pruning(self, ends):
        return [end for end in ends if not self._is_pareto_dominated(end)]

    def shortest_path_multiple_missions(self, start, end, checkpoints):

        checkpoints.append(end)
        n = len(checkpoints)
        ends = shortest_path(start, checkpoints[0])[2]
        ends = self._ends_pruning(ends)

        for i in range(n-1):
            ends_i = []
            for j in range(len(ends)):
                end_j = ends[j]
                ends_i += shortest_path(end_j, checkpoints[i], initial_distance=self.distances[end_j])[2]
            ends = self._ends_pruning(ends_i)

        end = min(ends, key=lambda x: self.distances[x])
        return self.distances[end], self._path(end)


    def best_missions_order(self, start, missions : list[tuple]):
        
        n = len(missions)
        ordered_missions = []
        current = start
        for i in range(n):
            mission_i = min(missions, key=lambda x: self.shortest_path(current, x[0])[0])
            missions.pop(missions.index(mission_i))
            ordered_missions.append(mission_i)
            current = mission_i[1]
        
        return ordered_missions



    def render_graph_with_path(self, start, end, output_file="graph"):
        """
        Graphviz parfait : layout pro, chemin highlighté, HD.
        """
        distance, path = self.shortest_path(start, end)

        if not path:
            print("❌ Pas de chemin trouvé")
            return

        dot = graphviz.Digraph()
        dot.attr(engine='dot', rankdir='TB', size='18,14', dpi='300')  # HD vertical
        dot.attr('node', fontname='Arial', fontsize='11')
        dot.attr('edge', fontname='Arial', fontsize='9')

        # Tous les nœuds (graphe + chemin)
        all_nodes = set(self._edges.keys())
        for neighbors in self._edges.values():
            for dest, _ in neighbors:
                all_nodes.add(dest)
        all_nodes.update(path)  # Sécurité

        # Nœuds avec couleurs
        for node in all_nodes:
            node_id = str(node)
            if node == start:
                dot.node(node_id, fillcolor='lightgreen', style='filled,bold',
                         shape='doublecircle', fontsize='13')
            elif node == end:
                dot.node(node_id, fillcolor='orange', style='filled,bold',
                         shape='doublecircle', fontsize='13')
            elif node in path:
                dot.node(node_id, fillcolor='#E6F3FF', style='filled', shape='ellipse')
            else:
                dot.node(node_id, shape='circle', style='filled', fillcolor='lightgray')

        # Arêtes du chemin (SANS IndexError)
        path_edges = set(zip(path[:-1], path[1:]))  # Couples consécutifs

        for src, neighbors in self._edges.items():
            src_id = str(src)
            for dest, weight in neighbors:
                dest_id = str(dest)
                if (src, dest) in path_edges:
                    dot.edge(src_id, dest_id, label=f'{weight}', color='red',
                             penwidth='5', arrowsize='2.0')
                else:
                    dot.edge(src_id, dest_id, label=f'{weight}', color='#666',
                             penwidth='1.8')

        # Titre pro
        dot.attr(label=f'Plus court chemin {start} → {end}\n'
                       f'{len(path) - 1} arêtes | Distance: {distance}')
        dot.attr(labelfontname='Arial', labelfontsize='16', labelloc='t')
        dot.attr(engine='fdp')
        dot.render(output_file, format='svg', cleanup=True)
        print(f"🎨 {output_file}.png généré (layout pro !)")


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
        super().__init__(edges)
        self.neighbours = fonction_neighbours


