import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / "code"))

NET_DIR = ROOT / "examples"

from network import Network
from graph import Graph

def test_build_simple_graph_is_correct_and_robust():
    """
    Checks everything that might typically cause issues for build_simple_graph:
    - return type (Graph)
    - same vertices as the network (including those without outputs)
    - correct conversion of edges: (dest, length, fatigue) -> (dest, length)
    - fatigue is properly ignored (not present / not used)
    - numerical weights
    - neighbours() returns [] for an unknown node
    - the constructed graph does not depend on subsequent modifications of network._roads
    """
    network = Network.from_file(NET_DIR / "small.txt")
    g = network.build_simple_graph()

    # 1) Type and presence of expected internal storage
    assert isinstance(g, Graph)
    assert hasattr(g, "_edges")
    assert isinstance(g._edges, dict)

    # 2) The nodes of the simple graph match exactly the keys of network._roads
    assert set(g._edges.keys()) == set(network._roads.keys())

    # 3) Each neighbor list is correctly converted to (dest, length) and ignores fatigue
    for node, roads in network._roads.items():
        expected = [(dest, length) for (dest, length, fatigue) in roads]
        got = g.neighbours(node)

        assert got == expected

        # Check shape and types
        for edge in got:
            assert isinstance(edge, tuple)
            assert len(edge) == 2  # no fatigue in the simple graph

            dest, weight = edge
            assert isinstance(dest, str)
            assert isinstance(weight, (int, float))

    # 4) Robust behavior: unknown node => []
    assert g.neighbours("__UNKNOWN_NODE__") == []

    # 5) The simple graph should not "move" if network._roads is modified afterward
    # (build_simple_graph must construct a new structure)
    before = list(g.neighbours(network.start))
    network._roads[network.start].append(("__X__", 123, 999))  # huge fatigue but supposed to be ignored
    after = list(g.neighbours(network.start))

    assert after == before  # the constructed graph remains identical

    # 6) Test shortest_path method to ensure it calculates correct shortest paths
    distance, path = g.shortest_path("lozere", "saclay")
    assert distance == 55  # Expected distance based on the roads in example
    assert path == ["lozere", "ensae", "saclay"]  # Expected path
