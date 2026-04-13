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
        self._estimated_distances = {}


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
        if isinstance(node, tuple):
            v, f = node
        else:
            v = node
            f = 1

        if v not in self._edges:
            return []
        return [
            ((dest, 1), weight) if not isinstance(dest, tuple) else (dest, weight)
            for dest, weight in self._edges[v]
        ]


    def shortest_path(self, start, end, multiple_missions = False, initial_distance = 0):
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
        # Extract all source nodes (handling both tuple and non-tuple formats)
        all_sources = set()
        for node in self._edges.keys():
            if isinstance(node, tuple):
                all_sources.add(node[0])
            else:
                all_sources.add(node)

        # Extract all destination nodes (handling both tuple and non-tuple formats)
        all_destinations = set()
        for neighbors in self._edges.values():
            for dest, _ in neighbors:
                if isinstance(dest, tuple):
                    all_destinations.add(dest[0])
                else:
                    all_destinations.add(dest)

        # Check if start and end nodes are valid
        start_node = start[0] if isinstance(start, tuple) else start
        end_node = end[0] if isinstance(end, tuple) else end

        if start_node not in all_sources or end_node not in all_destinations:
            return math.inf, [], []


        # Initialize distances, and visited status for all nodes.

        if isinstance(start, tuple):
            self.distances = {start : initial_distance}
        else:
            self.distances = {(start, 1) : initial_distance}   # Distance to the starting node

        visited = {}  # Tracks whether a node has been visited.


        while True:
            # Find the unvisited node with the smallest estimated total cost (A*: g + h).
            current = min((node for node in self.distances.keys() if not visited.get(node, False)),
                          key=lambda x: self.distances[x] + self.heuristic(x, end), default=None)
            # If no node can be reached or the smallest distance is infinity, terminate (no path exists).
            if current is None or self.distances[current] == math.inf:
                break
                return math.inf, [], []

            visited[current] = True  # Mark the current node as visited.

            # If the current node is the destination, terminate.
            if current[0] == end:
                if multiple_missions:
                    continue
                else:
                    break


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
        if not multiple_missions:
            path = self._path(end1)
        else:
            path = []
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

        if isinstance(node, tuple):
            v, fatigue = node
        else:
            v, fatigue = node, 1

        distance = self.distances[(v, fatigue)]
        for (s, f), d in self.distances.items():
            if s == v and ((d < distance and f <= fatigue) or (d <= distance and f < fatigue)):
                return True
        return False

    def _compute_estimated_distances(self, end):
        if end in self._estimated_distances:
            return

        reversed_edges = {}
        for src, neighbors in self._edges.items():
            for dest, weight in neighbors:
                dest_v = dest[0] if isinstance(dest, tuple) else dest
                reversed_edges.setdefault(dest_v, []).append((src, weight))

        dist = {end: 0}
        visited = {}

        while True:
            current = min(
                (n for n in dist if not visited.get(n, False)),
                key=lambda n: dist[n],
                default=None
            )
            if current is None:
                break
            visited[current] = True
            for neighbor, weight in reversed_edges.get(current, []):
                new_dist = dist[current] + weight
                if new_dist < dist.get(neighbor, math.inf):
                    dist[neighbor] = new_dist

        self._estimated_distances[end] = dist

    def heuristic(self, node, end):

        v, f = node if isinstance(node, tuple) else (node, 1)
        if v == end:
            return 0
        self._compute_estimated_distances(end)
        return self._estimated_distances[end].get(v, math.inf) * f


    def _ends_pruning(self, ends, distances):

        unique_ends = set(ends)

        ends_pruned = []
        for end in unique_ends:
            dominated = False
            v, fatigue = end
            distance = distances[end]
            for (s, f), d in distances.items():
                if (d < distance and f <= fatigue) or (d <= distance and f < fatigue):
                    dominated = True

            if not dominated:
                ends_pruned.append(end)

        return ends_pruned


    def _get_ends_distances(self, ends):
        return {end : self.distances.get(end, math.inf) for end in ends}

    def shortest_path_multiple_missions(self, missions:list[tuple]):

        start = missions[0][0]

        targets = []
        for (u,v) in missions:
            if u !=start:
                targets.append(u)
            targets.append(v)

        n = len(targets)
        ends = self.shortest_path(start, targets[0], multiple_missions = True)[2]
        ends_distances = self._get_ends_distances(ends)
        ends = self._ends_pruning(ends, ends_distances)


        for i in range(n-1):
            end_i = targets[i+1]
            ends_i = []
            ends_distances_i = {}

            for j in range(len(ends)):
                start_i_j = ends[j]
                initial_distance = ends_distances[start_i_j]
                ends_i_j = self.shortest_path(start_i_j, end_i, multiple_missions = True, initial_distance=initial_distance)[2]
                ends_distances_i_j = self._get_ends_distances(ends_i_j)
                ends_i.extend(ends_i_j)
                ends_distances_i.update(ends_distances_i_j)

            ends = self._ends_pruning(ends_i, ends_distances_i)
            ends_distances.update(ends_distances_i)

        end = min(ends, key=lambda x: ends_distances[x])
        return ends_distances[end], self._path(end)


    def best_missions_order(self, missions: list[tuple]):
        """
        Teste TOUTES les permutations d'ordre des missions et retourne la meilleure.
        Complexité: O(n! * n) - OK jusqu'à n=10.
        """

        from itertools import permutations

        n = len(missions)
        if n == 0:
            return [], 0

        best_order = None
        best_dist = math.inf

        # Test every possible order of missions
        for perm in permutations(missions):  # perm = ((s1,e1), (s2,e2), ...)
            total_dist = 0


            for i in range(n - 1):
                trans_dist = self.shortest_path(perm[i][1], perm[i + 1][0])[0]  # end_i → start_{i+1}
                total_dist += trans_dist
                if total_dist >= best_dist:
                    break

            if total_dist < best_dist:
                best_dist = total_dist
                best_order = perm

        return list(best_order)



    def render_graph_with_path(self, start, end, output_file="graph"):
        """
        Graphviz parfait : layout pro, chemin highlighté, HD.
        """
        distance, path, _ = self.shortest_path(start, end)

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



class GraphExtended(Graph):

    def __init__(self, edges, extended_edges):
        super().__init__(edges)
        self._extended_edges = extended_edges

        def neighbours(node):
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

            if node not in self._extended_edges:
                return []
            return [
                ((dest, 1), weight) if not isinstance(dest, tuple) else (dest, weight)
                for dest, weight in self._extended_edges[node]
            ]

        self.neighbours = neighbours



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


