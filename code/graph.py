"""
Graph module.

Contains the following classes:
  - Graph:                 Directed weighted graph with A* shortest path.
  - GraphExtended:         Subclass using pre-built fatigue-expanded edges.
  - GraphImplicit:         Subclass using a dynamic neighbour function.
  - MultipleMissionsGraph: Subclass of GraphImplicit with multi-mission routing.
"""

import math
import graphviz


class Graph:
    """
    Directed weighted graph represented as an adjacency list.

    Nodes can be plain values or (location, fatigue) tuples. The shortest-path
    algorithm is A* with a Pareto-dominance pruning on (distance, fatigue) pairs.

    Attributes
    ----------
    _edges : dict
        Adjacency list: _edges[node] = [(neighbour, weight), ...]
    distances : dict
        Distances computed by the last call to shortest_path.
    predecessors : dict
        Predecessor map built during the last shortest_path call.
    _estimated_distances : dict
        Cache of backward-Dijkstra distances used by the heuristic.
    """

    def __init__(self, edges):
        """
        Parameters
        ----------
        edges : dict
            Adjacency list where each key is a node and each value is a list
            of (neighbour, weight) tuples.
        """
        self._edges = edges
        self.distances = {}
        self.predecessors = {}
        self._estimated_distances = {}

    # ------------------------------------------------------------------
    # Neighbours
    # ------------------------------------------------------------------

    def neighbours(self, node):
        """
        Return the neighbours of *node* with their edge weights.

        If *node* is a (location, fatigue) tuple the location part is used
        to look up the adjacency list. Plain-node destinations are wrapped as
        (destination, 1) so that all returned neighbours are tuples.

        Parameters
        ----------
        node : value or (value, int)
            The node whose neighbours are requested.

        Returns
        -------
        list of ((neighbour, fatigue), weight)
            Empty list when the node has no outgoing edges.
        """
        v = node[0] if isinstance(node, tuple) else node

        if v not in self._edges:
            return []
        return [
            ((dest, 1), weight) if not isinstance(dest, tuple) else (dest, weight)
            for dest, weight in self._edges[v]
        ]

    # ------------------------------------------------------------------
    # Shortest path (A*)
    # ------------------------------------------------------------------

    def shortest_path(self, start, end, multiple_missions=False, initial_distance=0):
        """
        Find the shortest path from *start* to *end* using A*.

        The algorithm uses a backward-Dijkstra heuristic weighted by the current
        fatigue level and prunes states that are Pareto-dominated on the
        (distance, fatigue) plane.

        Parameters
        ----------
        start : node
            Starting node. May be a plain value or a (location, fatigue) tuple.
        end : node
            Target location (plain value or tuple; only the location part is matched).
        multiple_missions : bool
            When True, the search continues past *end* so that all (end, fatigue)
            states are discovered. Used by shortest_path_multiple_missions.
        initial_distance : int or float
            Initial accumulated distance, used when chaining mission segments.

        Returns
        -------
        (distance, path, ends)
            distance : minimum cost to reach *end*. math.inf if unreachable.
            path     : list of node locations from start to end (empty when
                       multiple_missions=True or when unreachable).
            ends     : list of (end_location, fatigue) states reached.
        """
        # Validate that start and end exist in the graph
        all_sources = set()
        for node in self._edges.keys():
            all_sources.add(node[0] if isinstance(node, tuple) else node)

        all_destinations = set()
        for neighbors in self._edges.values():
            for dest, _ in neighbors:
                all_destinations.add(dest[0] if isinstance(dest, tuple) else dest)

        start_node = start[0] if isinstance(start, tuple) else start
        end_node = end[0] if isinstance(end, tuple) else end

        if start_node not in all_sources or end_node not in all_destinations:
            return math.inf, [], {}

        # Initialise with start node; wrap plain nodes as (node, fatigue=1)
        if isinstance(start, tuple):
            self.distances = {start: initial_distance}
        else:
            self.distances = {(start, 1): initial_distance}

        visited = {}

        while True:
            # Pick the unvisited node with the lowest f = g + h
            current = min(
                (node for node in self.distances if not visited.get(node, False)),
                key=lambda x: self.distances[x] + self.heuristic(x, end),
                default=None,
            )

            if current is None or self.distances[current] == math.inf:
                break

            visited[current] = True

            if current[0] == end:
                if not multiple_missions:
                    break
                # In multiple_missions mode keep expanding to find all end states

            if not self._is_pareto_dominated(current):
                for dest, length in self.neighbours(current):
                    if not visited.get(dest, False):
                        new_dist = self.distances[current] + length
                        if new_dist < self.distances.get(dest, math.inf):
                            self.distances[dest] = new_dist
                            self.predecessors[dest] = current

        # Collect all reached states whose location equals end
        ends = {(v, f): self.distances[(v, f)] for v, f in self.distances if v == end}
        if not ends:
            return math.inf, [], {}

        best_end = min(ends, key=lambda x: ends[x])

        if not multiple_missions:
            path = self._path(best_end)
        else:
            path = []

        return ends[best_end], path, ends

    # ------------------------------------------------------------------
    # Path reconstruction
    # ------------------------------------------------------------------

    def _path(self, v):
        """
        Reconstruct the path that ends at node *v* using the predecessors map.

        Parameters
        ----------
        v : (location, fatigue)
            The destination node.

        Returns
        -------
        list
            Ordered list of locations from source to *v*.
        """
        path = []
        current = v
        while current is not None:
            path.append(current[0] if isinstance(current, tuple) else current)
            current = self.predecessors.get(current)
        path.reverse()
        return path

    # ------------------------------------------------------------------
    # Pareto dominance
    # ------------------------------------------------------------------

    def _is_pareto_dominated(self, node):
        """
        Return True if *node* is dominated by another known state on the same
        location.

        A state (v, f, d) is dominated if another state (v, f', d') exists with
        d' <= d and f' <= f (strictly less for at least one criterion).

        Parameters
        ----------
        node : (location, fatigue)

        Returns
        -------
        bool
        """
        v, fatigue = node if isinstance(node, tuple) else (node, 1)
        distance = self.distances[(v, fatigue)]

        for (s, f), d in self.distances.items():
            if s == v and ((d < distance and f <= fatigue) or (d <= distance and f < fatigue)):
                return True
        return False

    # ------------------------------------------------------------------
    # Heuristic (backward Dijkstra)
    # ------------------------------------------------------------------

    def _compute_estimated_distances(self, end):
        """
        Run backward Dijkstra from *end* on the simple (non-fatigue) graph and
        cache the result.

        The result is stored in self._estimated_distances[end] and reused on
        subsequent calls with the same endpoint.

        Parameters
        ----------
        end : location
        """
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
                default=None,
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
        """
        A* heuristic: backward-Dijkstra distance to *end* scaled by fatigue.

        Multiplying the distance lower-bound by the current fatigue gives an
        admissible heuristic because fatigue is non-decreasing.

        Parameters
        ----------
        node : (location, fatigue)
        end : location

        Returns
        -------
        float
        """
        v, f = node if isinstance(node, tuple) else (node, 1)
        if v == end:
            return 0
        self._compute_estimated_distances(end)
        return self._estimated_distances[end].get(v, math.inf) * f

    # ------------------------------------------------------------------
    # Visualisation
    # ------------------------------------------------------------------

    def render_graph_with_path(self, start, end, output_file="graph"):
        """
        Render the graph with the shortest path highlighted using Graphviz.

        The start node is green, the end node is orange, intermediate path nodes
        are light blue, and all other nodes are grey.

        Parameters
        ----------
        start : node
            Starting location.
        end : node
            Target location.
        output_file : str
            Base filename for the generated SVG (no extension needed).
        """
        distance, path, _ = self.shortest_path(start, end)

        if not path:
            print("No path found.")
            return

        dot = graphviz.Digraph()
        dot.attr(engine="dot", rankdir="TB", size="18,14", dpi="300")
        dot.attr("node", fontname="Arial", fontsize="11")
        dot.attr("edge", fontname="Arial", fontsize="9")

        all_nodes = set(self._edges.keys())
        for neighbors in self._edges.values():
            for dest, _ in neighbors:
                all_nodes.add(dest)
        all_nodes.update(path)

        for node in all_nodes:
            node_id = str(node)
            if node == start:
                dot.node(node_id, fillcolor="lightgreen", style="filled,bold",
                         shape="doublecircle", fontsize="13")
            elif node == end:
                dot.node(node_id, fillcolor="orange", style="filled,bold",
                         shape="doublecircle", fontsize="13")
            elif node in path:
                dot.node(node_id, fillcolor="#E6F3FF", style="filled", shape="ellipse")
            else:
                dot.node(node_id, shape="circle", style="filled", fillcolor="lightgray")

        path_edges = set(zip(path[:-1], path[1:]))

        for src, neighbors in self._edges.items():
            for dest, weight in neighbors:
                if (src, dest) in path_edges:
                    dot.edge(str(src), str(dest), label=str(weight),
                             color="red", penwidth="5", arrowsize="2.0")
                else:
                    dot.edge(str(src), str(dest), label=str(weight),
                             color="#666", penwidth="1.8")

        dot.attr(
            label=f"Shortest path {start} -> {end}\n"
                  f"{len(path) - 1} edges | Distance: {distance}"
        )
        dot.attr(labelfontname="Arial", labelfontsize="16", labelloc="t")
        dot.attr(engine="fdp")
        dot.render(output_file, format="svg", cleanup=True)
        print(f"Graph saved to {output_file}.svg")


# ---------------------------------------------------------------------------
# GraphExtended
# ---------------------------------------------------------------------------

class GraphExtended(Graph):
    """
    Subclass of Graph that uses a pre-built fatigue-expanded edge set.

    Each node in the extended graph is a (location, fatigue_level) tuple.
    Edges encode the cost as length * fatigue_level and the new fatigue as
    fatigue_level + edge_fatigue.

    Attributes
    ----------
    _extended_edges : dict
        Fatigue-expanded adjacency list:
        _extended_edges[(location, fatigue)] = [((dest, new_fatigue), cost), ...]
    """

    def __init__(self, edges, extended_edges):
        """
        Parameters
        ----------
        edges : dict
            Plain adjacency list (used by the heuristic backward Dijkstra).
        extended_edges : dict
            Fatigue-expanded adjacency list.
        """
        super().__init__(edges)
        self._extended_edges = extended_edges

        def neighbours(node):
            """Return neighbours from the fatigue-expanded edge set."""
            if node not in self._extended_edges:
                return []
            return [
                ((dest, 1), weight) if not isinstance(dest, tuple) else (dest, weight)
                for dest, weight in self._extended_edges[node]
            ]

        self.neighbours = neighbours


# ---------------------------------------------------------------------------
# GraphImplicit
# ---------------------------------------------------------------------------

class GraphImplicit(Graph):
    """
    Subclass of Graph where neighbours are computed on the fly.

    Instead of a static adjacency list, a callable *fonction_neighbours* is
    provided. It receives a (location, fatigue) node and returns the list of
    ((neighbour_location, new_fatigue), cost) pairs.

    Attributes
    ----------
    neighbours : callable
        Dynamic neighbour function supplied at construction time.
    """

    def __init__(self, edges, fonction_neighbours):
        """
        Parameters
        ----------
        edges : dict
            Plain adjacency list kept for the backward-Dijkstra heuristic.
        fonction_neighbours : callable
            Function (node) -> list of ((dest, fatigue), cost).
        """
        super().__init__(edges)
        self.neighbours = fonction_neighbours


# ---------------------------------------------------------------------------
# MultipleMissionsGraph
# ---------------------------------------------------------------------------

class MultipleMissionsGraph(GraphImplicit):
    """
    Extension of GraphImplicit with multi-mission routing support.

    A *mission* is a (start, end) tuple. This class provides:

    - shortest_path_multiple_missions: optimal path through an ordered list
      of missions with correct fatigue propagation between missions.
    - best_missions_order_brute: approximate mission ordering (ignores fatigue
      for the transition distances).
    - best_shortest_path_multiple_missions: exact mission ordering evaluated
      via full path simulation with fatigue propagation.
    """

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ends_pruning(self, ends: dict):
        """
        Remove end-states that are Pareto-dominated by another end-state.

        A state (v, f, d) is dominated if there exists (v, f', d') with
        d' <= d and f' <= f (at least one strict).

        Parameters
        ----------
        ends : dict mapping (location, fatigue) -> distance

        Returns
        -------
        dict
            Non-dominated subset of *ends*.
        """
        pruned = {}
        for end, distance in ends.items():
            v, fatigue = end
            dominated = any(
                (d < distance and f <= fatigue) or (d <= distance and f < fatigue)
                for (s, f), d in ends.items()
                if s == v
            )
            if not dominated:
                pruned[end] = distance
        return pruned

    # ------------------------------------------------------------------
    # Multi-mission shortest path
    # ------------------------------------------------------------------

    def shortest_path_multiple_missions(self, missions: list[tuple]):
        """
        Compute the shortest path through an ordered sequence of missions.

        Each mission is a (start, end) tuple. The algorithm chains A* calls
        and carries over the fatigue state between consecutive missions, so
        the result is exact with respect to fatigue accumulation.

        The targets visited in order are:
          mission[0].start, mission[0].end, mission[1].start (if != previous
          end), mission[1].end, ...

        Pareto pruning on (distance, fatigue) is applied after each segment to
        limit the frontier size.

        Parameters
        ----------
        missions : list of (start, end)
            Ordered list of missions to complete.

        Returns
        -------
        (distance, path)
            distance : total cost of the optimal path. math.inf if infeasible.
            path     : list of locations visited.
        """

        self.predecessors = {}

        start = missions[0][0]

        targets = []
        for (u, v) in missions:
            if u != start:
                targets.append(u)
            targets.append(v)

        n = len(targets)
        ends = self._ends_pruning(self.shortest_path(start, targets[0], multiple_missions=True)[2])

        for i in range(n - 1):
            end_i = targets[i + 1]
            ends_i = {}

            for start_i_j, initial_distance in ends.items():
                ends_i_j = self.shortest_path(start_i_j, end_i, multiple_missions=True, initial_distance=initial_distance)[2]
                for state, dist in ends_i_j.items():
                    if dist < ends_i.get(state, math.inf):
                        ends_i[state] = dist

            ends = self._ends_pruning(ends_i)

        if not ends:
            return math.inf, []
        best_end = min(ends, key=lambda x: ends[x])
        return ends[best_end], self._path(best_end)

    # ------------------------------------------------------------------
    # Mission ordering — approximate (ignores fatigue on transitions)
    # ------------------------------------------------------------------

    def best_missions_order_brute(self, missions: list[tuple]):
        """
        Find the mission order minimising total transition distance.

        Pre-computes all n*(n-1) directed transition distances (end_i -> start_j)
        using shortest_path with default fatigue, then exhaustively searches all
        n! permutations with branch-and-bound pruning.

        Note: transition distances are computed independently of accumulated
        fatigue, so this is an approximation when fatigue is significant.

        Parameters
        ----------
        missions : list of (start, end)

        Returns
        -------
        list of (start, end)
            Missions in the order that minimises the sum of transition distances.
        """
        from itertools import permutations

        n = len(missions)
        if n == 0:
            return []
        if n == 1:
            return list(missions)

        # Pre-compute all directed transition costs end_i -> start_j
        trans = {}
        for i in range(n):
            for j in range(n):
                if i != j:
                    trans[(i, j)] = self.shortest_path(missions[i][1], missions[j][0])[0]

        best_order = None
        best_dist = math.inf

        for perm in permutations(range(n)):
            total = 0
            for k in range(n - 1):
                total += trans[(perm[k], perm[k + 1])]
                if total >= best_dist:
                    break
            if total < best_dist:
                best_dist = total
                best_order = perm

        return [missions[i] for i in best_order]

    # ------------------------------------------------------------------
    # Mission ordering — exact (full fatigue propagation)
    # ------------------------------------------------------------------

    def best_shortest_path_multiple_missions(self, missions: list[tuple]):
        """
        Find the mission order and path that minimise total cost with fatigue.

        Evaluates every permutation of missions by simulating the full path
        through shortest_path_multiple_missions, which correctly propagates
        fatigue across mission boundaries.

        Complexity: O(n! * cost_of_full_path) — exact but exponential in n.
        Practical for up to ~8 missions.

        Parameters
        ----------
        missions : list of (start, end)

        Returns
        -------
        (distance, path)
            distance : minimum total cost across all orderings.
            path     : corresponding list of locations.
        """
        from itertools import permutations

        n = len(missions)
        if n == 0:
            return math.inf, []
        if n == 1:
            return self.shortest_path_multiple_missions(list(missions))

        best_dist = math.inf
        best_path = []

        for perm in permutations(missions):
            print(f"Testing permutation {perm}...")
            dist, path = self.shortest_path_multiple_missions(list(perm))
            print(f"Mission order: {perm} -> {dist} = {path}")
            if dist < best_dist:
                best_dist = dist
                best_path = path

        return best_dist, best_path
