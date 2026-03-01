from graph import *  # Importing Graph and GraphImplicit classes
import sys
from pathlib import Path

# Define the root directory and set up the path for importing other modules
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / "code"))

# Directory for example network data files
NET_DIR = ROOT / "examples"


class Network:
    """
    Class representing a transportation network with roads characterized by length and fatigue.

    A Network is essentially a graph with additional attributes such as start and end nodes and 
    allows conversion into different representations (simple/extended/implicit graphs). 
    """

    def __init__(self, roads={}, start=None, end=None):
        """
        Initializes the network using a dictionary of roads and optional start/end nodes.

        Parameters:
        -----------
        roads: dict
            Adjacency list representing the road network. Each key is a node, and each value is a list of
            tuples (destination, length, fatigue). 
            Example:
            roads = {
                'v0': [('v1', 21, 2), ('v2', 12, 4)],
                'v1': [('v0', 74, 2), ('v2', 32, 1)],
                ...
            }
        start: str, optional
            The starting node of the network (default: None).
        end: str, optional
            The ending node of the network (default: None).
        """
        self._roads = roads  # Internal representation of roads
        self.start = start  # Start node of the network
        self.end = end  # End node of the network

    def __str__(self):
        """
        Provides a string representation of the network, including the number of nodes
        and details of the adjacency list.

        Returns:
        --------
        str
            Human-readable representation of the network.
        """
        output = f"A network with {len(self._roads)} nodes and the following adjacency list:\n"
        return output + self._roads.__str__()

    @classmethod
    def from_file(cls, filename: str):
        """
        Constructs a Network object by reading a file. The file must specify the adjacency list
        with edges formatted as: start end length fatigue.

        Parameters:
        -----------
        filename: str
            Path to the file containing the network data.

        Returns:
        --------
        Network
            Instance of the Network class created from the file input.
        """
        roads = {}  # Initialize the adjacency list

        with open(filename, "r") as testcase:
            # Read the first line containing the number of roads, start and end node
            nb, start, end = testcase.readline().strip().split()

            # Parse each remaining line to populate the adjacency list
            for _ in range(int(nb)):
                i, j, l, f = testcase.readline().strip().split()
                l, f = int(l), int(f)

                # Add road data to the adjacency list
                roads.setdefault(i, []).append((j, l, f))
                roads.setdefault(j, [])  # Ensure all nodes are initialized

        return cls(roads=roads, start=start, end=end)

    def build_simple_graph(self):
        """
        Generates a simple graph representation of the network, ignoring fatigue levels.
        Useful for shortest path analysis in terms of road length only.

        Returns:
        --------
        Graph
            An instance of the Graph class with the converted adjacency list.
        """
        edges = {}  # Initialize the adjacency list for the simple graph

        for node, neighbors in self._roads.items():
            # For each node, add its neighbors with length but ignore fatigue
            edges[node] = [(dest, length) for dest, length, fatigue in neighbors]

        return Graph(edges)

    def build_extended_graph(self, max_fatigue=1000):
        """
        Generates an extended graph that incorporates fatigue levels. Nodes are expanded
        to include distinct fatigue levels in their representation.

        Parameters:
        -----------
        max_fatigue: int
            Maximum allowable fatigue level. Nodes with fatigue levels beyond this value are excluded.

        Returns:
        --------
        Graph
            An extended graph, where nodes include fatigue levels (e.g., ('v1', fatigue)).
        """
        # Initialize the extended adjacency list
        extended_roads = {
            self.start: [((dest, 1), length) for dest, length, fatigue in self._roads[self.start]],
            self.end: []
        }

        # Expand nodes for different fatigue levels
        for fatigue_level in range(1, max_fatigue):
            for node, neighbors in self._roads.items():
                if node != self.end:  # Process all nodes except the end node
                    # Add expanded nodes to the extended adjacency list
                    extended_roads[(node, fatigue_level)] = [
                        ((dest, fatigue_level + fatigue), length * fatigue_level)
                        if dest != self.end  # For intermediate nodes
                        else (dest, length * fatigue_level)  # For edges to the end node
                        for dest, length, fatigue in neighbors
                        if fatigue_level + fatigue <= max_fatigue  # Respect max fatigue limit
                    ]

        print('Extended graph created.')  # Log for debugging
        return Graph(extended_roads)

    def build_implicit_graph(self):
        """
        Builds an implicit graph representation of the network. This representation uses a dynamic
        function (`fonction_neighbours`) to compute neighbors on demand instead of storing them explicitly.

        Returns:
        --------
        GraphImplicit
            An instance of the GraphImplicit class with a provided neighbor function.
        """
        # Prepare the core adjacency list for nodes without fatigue
        edges = {}
        for node, neighbors in self._roads.items():
            edges[node] = [(dest, length) for dest, length, fatigue in neighbors]

        # Define the dynamic function for computing neighbors based on fatigue
        def fonction_neighbours(node):
            if node == self.start:
                # Special case for the start node: consider all outgoing edges with fatigue
                neighbours = []
                for dest, length, fatigue in self._roads[node]:
                    if dest != self.end:
                        neighbours.append(((dest, fatigue), length))
                    else:
                        neighbours.append((dest, length))
            else:
                # Default case: expand neighbor based on the current fatigue level
                v, current_fatigue = node  # Decompose the node into base node and fatigue level
                neighbours = []
                for dest, length, fatigue in self._roads[v]:
                    if dest != self.end:
                        neighbours.append(((dest, current_fatigue + fatigue), length * current_fatigue))
                    else:
                        neighbours.append((dest, length * current_fatigue))

            return neighbours

        return GraphImplicit(edges, fonction_neighbours)
