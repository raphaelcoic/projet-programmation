import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / "code"))

import unittest
from network import Network

NET_DIR = ROOT / "examples"


class TimedTestCase(unittest.TestCase):
    def setUp(self):
        self._start = time.perf_counter()

    def tearDown(self):
        elapsed = time.perf_counter() - self._start
        print(f"\n  [{self._testMethodName}]  {elapsed:.4f}s")


class TestNetworkCreation(TimedTestCase):

    def test_small_start_end(self):
        net = Network.from_file(NET_DIR / "small.txt")
        self.assertEqual(net.start, "lozere")
        self.assertEqual(net.end, "saclay")

    def test_small_roads(self):
        net = Network.from_file(NET_DIR / "small.txt")
        self.assertEqual(net._roads, {
            "lozere":  [("ensae", 10, 2), ("guichet", 20, 0)],
            "ensae":   [("saclay", 45, 0)],
            "guichet": [("ensae", 15, 1)],
            "saclay":  [],
        })

    def test_small_node_count(self):
        net = Network.from_file(NET_DIR / "small.txt")
        self.assertEqual(len(net._roads), 4)

    def test_medium_nofatigue_start_end(self):
        net = Network.from_file(NET_DIR / "medium-nofatigue.txt")
        self.assertEqual(net.start, "v0")
        self.assertEqual(net.end, "v99")

    def test_medium_nofatigue_node_count(self):
        net = Network.from_file(NET_DIR / "medium-nofatigue.txt")
        self.assertGreater(len(net._roads), 0)

    def test_medium_nofatigue_all_fatigues_zero(self):
        net = Network.from_file(NET_DIR / "medium-nofatigue.txt")
        for neighbors in net._roads.values():
            for _, _, fatigue in neighbors:
                self.assertEqual(fatigue, 0)

    def test_medium_smallfatigue_start_end(self):
        net = Network.from_file(NET_DIR / "medium-smallfatigue.txt")
        self.assertEqual(net.start, "v0")
        self.assertEqual(net.end, "v99")

    def test_medium_smallfatigue_node_count(self):
        net = Network.from_file(NET_DIR / "medium-smallfatigue.txt")
        self.assertGreater(len(net._roads), 0)

    def test_medium_largefatigue_start_end(self):
        net = Network.from_file(NET_DIR / "medium-largefatigue.txt")
        self.assertEqual(net.start, "v0")
        self.assertEqual(net.end, "v99")

    def test_medium_largefatigue_node_count(self):
        net = Network.from_file(NET_DIR / "medium-largefatigue.txt")
        self.assertGreater(len(net._roads), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
