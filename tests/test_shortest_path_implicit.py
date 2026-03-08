import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / "code"))

import unittest
from network import Network

NET_DIR = ROOT / "examples"
EXPECTED_FILE = ROOT / "tests" / "data" / "expected_distances.txt"


def load_expected_distances():
    expected = {}
    with EXPECTED_FILE.open("r") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            filename, distance = line.split()
            expected[filename] = int(distance)
    return expected


class Test_ShortestPathImplicit(unittest.TestCase):
    def test_shortest_path_implicit_small(self):
        expected = load_expected_distances()
        network = Network.from_file(NET_DIR / "large-smallfatigue.txt") ### Ici on teste avec un fichier à la fois pour que cela prenne moins de temps
        graph = network.build_implicit_graph()
        actual, _ = graph.shortest_path(network.start, network.end)
        self.assertEqual(actual, expected["large-smallfatigue.txt"])


if __name__ == "__main__":
    unittest.main()
