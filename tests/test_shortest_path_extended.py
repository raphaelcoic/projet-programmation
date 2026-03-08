import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / "code"))

import unittest
from network import Network

NET_DIR = ROOT / "examples"


class Test_ShortestPath_Extended(unittest.TestCase):
    def assert_shortest_path_distance(self, filename, expected_distance):
        network = Network.from_file(NET_DIR / filename)
        graph = network.build_extended_graph()
        actual, _ = graph.shortest_path(network.start, network.end)
        self.assertEqual(actual, expected_distance)

    def test_shortest_path_expected_distances(self):
        expected_file = ROOT / "tests" / "data" / "expected_distances.txt"
        with expected_file.open("r") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                filename, distance = line.split()

                if filename != "medium-smallfatigue.txt":  ### Ici on teste avec un fichier à la fois pour que cela prenne moins de temps
                    continue  ### On peut enlever ces deux lignes pour tester tout le fichiers en même temps
                print(f"Testing graph: {filename}")  # Print the graph name being tested
                self.assert_shortest_path_distance(filename, int(distance))

if __name__ == "__main__":
    unittest.main()


