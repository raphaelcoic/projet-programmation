from graph import Graph, GraphExtended, GraphImplicit, MultipleMissionsGraph
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / "code"))
NET_DIR = ROOT / "examples"


class Network:
    """
    Road network with weighted, fatigue-inducing edges.

    Each edge (u, v) carries a *length* and a *fatigue* cost. Traversing the
    edge at current fatigue level f incurs a distance cost of length * f and
    raises the fatigue to f + fatigue.

    Attributes
    ----------
    _roads : dict
        Adjacency list: _roads[u] = [(v, length, fatigue), ...]
    start : str
        Default source node (loaded from file).
    end : str
        Default destination node (loaded from file).
    """

    def __init__(self, roads={}, start=None, end=None):
        """
        Parameters
        ----------
        roads : dict
            Adjacency list: roads[u] = [(v, length, fatigue), ...]
        start : str, optional
            Default source node.
        end : str, optional
            Default destination node.
        """
        self._roads = roads
        self.start = start
        self.end = end

    def __str__(self):
        """Return a human-readable description of the network."""
        header = f"Network with {len(self._roads)} nodes:\n"
        return header + self._roads.__str__()

    @classmethod
    def from_file(cls, filename: str):
        """
        Load a Network from a text file.

        File format (one edge per line after the header)::

            <nb_edges> <start> <end>
            <u> <v> <length> <fatigue>
            ...

        Parameters
        ----------
        filename : str or Path
            Path to the network file.

        Returns
        -------
        Network
        """
        roads = {}

        with open(filename, "r") as f:
            nb, start, end = f.readline().strip().split()
            for _ in range(int(nb)):
                i, j, l, fatigue = f.readline().strip().split()
                l, fatigue = int(l), int(fatigue)
                roads.setdefault(i, []).append((j, l, fatigue))
                roads.setdefault(j, [])

        return cls(roads=roads, start=start, end=end)

    def build_simple_graph(self):
        """
        Build a Graph that ignores fatigue (uses only edge lengths).

        Useful as a baseline or when fatigue is not relevant.

        Returns
        -------
        Graph
        """
        edges = {
            node: [(dest, length) for dest, length, _ in neighbors]
            for node, neighbors in self._roads.items()
        }
        return Graph(edges)

    def build_extended_graph(self, max_fatigue=1000):
        """
        Build a fatigue-expanded graph where each node is a (location, fatigue) pair.

        Every combination of location and fatigue level up to *max_fatigue* is
        pre-computed. Edge cost is length * fatigue_level and new fatigue is
        fatigue_level + edge_fatigue.

        Parameters
        ----------
        max_fatigue : int
            Maximum fatigue level to expand (default: 1000).

        Returns
        -------
        GraphExtended
        """
        plain_edges = {
            node: [(dest, length) for dest, length, _ in neighbors]
            for node, neighbors in self._roads.items()
        }

        extended_roads = {}
        for fatigue_level in range(1, max_fatigue):
            for node, neighbors in self._roads.items():
                extended_roads[(node, fatigue_level)] = [
                    ((dest, fatigue_level + fatigue), length * fatigue_level)
                    for dest, length, fatigue in neighbors
                    if fatigue_level + fatigue <= max_fatigue
                ]

        return GraphExtended(plain_edges, extended_roads)

    def build_implicit_graph(self):
        """
        Build a GraphImplicit where fatigue-expanded neighbours are computed on the fly.

        This avoids pre-expanding the full state space and is more memory-efficient
        than build_extended_graph for large networks or high fatigue values.

        Returns
        -------
        GraphImplicit
        """
        plain_edges = {
            node: [(dest, length) for dest, length, _ in neighbors]
            for node, neighbors in self._roads.items()
        }

        def compute_neighbours(node):
            v, current_fatigue = node
            return [
                ((dest, current_fatigue + fatigue), length * current_fatigue)
                for dest, length, fatigue in self._roads[v]
            ]

        return GraphImplicit(plain_edges, compute_neighbours)

    def build_multi_missions_graph(self):
        """
        Build a MultipleMissionsGraph for multi-mission routing with fatigue.

        Identical to build_implicit_graph but returns a MultipleMissionsGraph
        instance, which exposes shortest_path_multiple_missions and
        best_shortest_path_multiple_missions.

        Returns
        -------
        MultipleMissionsGraph
        """
        plain_edges = {
            node: [(dest, length) for dest, length, _ in neighbors]
            for node, neighbors in self._roads.items()
        }

        def compute_neighbours(node):
            v, current_fatigue = node
            return [
                ((dest, current_fatigue + fatigue), length * current_fatigue)
                for dest, length, fatigue in self._roads[v]
            ]

        return MultipleMissionsGraph(plain_edges, compute_neighbours)
