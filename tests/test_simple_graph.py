import sys
import time
import math
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / "code"))

import unittest
from network import Network

NET_DIR = ROOT / "examples"

# small.txt : lozere->ensae(10)->saclay(45) = 55  (fatigue ignorée)
# medium-nofatigue.txt : fatigue=0 partout => identique à implicit = 1771
EXPECTED = {
    "small.txt": 55,
    "medium-nofatigue.txt": 1771,
}


class TimedTestCase(unittest.TestCase):
    def setUp(self):
        self._start = time.perf_counter()

    def tearDown(self):
        elapsed = time.perf_counter() - self._start
        print(f"\n  [{self._testMethodName}]  {elapsed:.4f}s")


class TestSimpleGraphSmall(TimedTestCase):

    @classmethod
    def setUpClass(cls):
        net = Network.from_file(NET_DIR / "small.txt")
        cls.graph = net.build_simple_graph()
        cls.start = net.start
        cls.end = net.end

    def test_distance(self):
        dist, _, _ = self.graph.shortest_path(self.start, self.end)
        self.assertEqual(dist, EXPECTED["small.txt"])

    def test_path_endpoints(self):
        _, path, _ = self.graph.shortest_path(self.start, self.end)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[-1], self.end)

    def test_path_length(self):
        _, path, _ = self.graph.shortest_path(self.start, self.end)
        self.assertGreater(len(path), 1)

    def test_no_path_returns_inf(self):
        dist, path, _ = self.graph.shortest_path(self.end, self.start)
        self.assertEqual(dist, math.inf)
        self.assertEqual(path, [])


class TestSimpleGraphMediumNoFatigue(TimedTestCase):

    @classmethod
    def setUpClass(cls):
        net = Network.from_file(NET_DIR / "medium-nofatigue.txt")
        cls.graph = net.build_simple_graph()
        cls.start = net.start
        cls.end = net.end

    def test_distance(self):
        dist, _, _ = self.graph.shortest_path(self.start, self.end)
        self.assertEqual(dist, EXPECTED["medium-nofatigue.txt"])

    def test_path_endpoints(self):
        _, path, _ = self.graph.shortest_path(self.start, self.end)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[-1], self.end)


class TestSimpleGraphMediumSmallFatigue(TimedTestCase):
    """Fatigue is ignored by simple graph — only checks the path is valid."""

    @classmethod
    def setUpClass(cls):
        net = Network.from_file(NET_DIR / "medium-smallfatigue.txt")
        cls.graph = net.build_simple_graph()
        cls.start = net.start
        cls.end = net.end

    def test_distance_is_finite(self):
        dist, _, _ = self.graph.shortest_path(self.start, self.end)
        self.assertLess(dist, math.inf)

    def test_path_endpoints(self):
        _, path, _ = self.graph.shortest_path(self.start, self.end)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[-1], self.end)


class TestSimpleGraphMediumLargeFatigue(TimedTestCase):
    """Fatigue is ignored by simple graph — only checks the path is valid."""

    @classmethod
    def setUpClass(cls):
        net = Network.from_file(NET_DIR / "medium-largefatigue.txt")
        cls.graph = net.build_simple_graph()
        cls.start = net.start
        cls.end = net.end

    def test_distance_is_finite(self):
        dist, _, _ = self.graph.shortest_path(self.start, self.end)
        self.assertLess(dist, math.inf)

    def test_path_endpoints(self):
        _, path, _ = self.graph.shortest_path(self.start, self.end)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[-1], self.end)


if __name__ == "__main__":
    unittest.main(verbosity=2)
