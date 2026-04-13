import sys
import time
import math
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


EXPECTED = load_expected_distances()


class TimedTestCase(unittest.TestCase):
    def setUp(self):
        self._start = time.perf_counter()

    def tearDown(self):
        elapsed = time.perf_counter() - self._start
        print(f"\n  [{self._testMethodName}]  {elapsed:.4f}s")


class TestImplicitGraphSmall(TimedTestCase):

    @classmethod
    def setUpClass(cls):
        net = Network.from_file(NET_DIR / "small.txt")
        cls.graph = net.build_implicit_graph()
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


class TestImplicitGraphMediumNoFatigue(TimedTestCase):

    @classmethod
    def setUpClass(cls):
        net = Network.from_file(NET_DIR / "medium-nofatigue.txt")
        cls.graph = net.build_implicit_graph()
        cls.start = net.start
        cls.end = net.end

    def test_distance(self):
        dist, _, _ = self.graph.shortest_path(self.start, self.end)
        self.assertEqual(dist, EXPECTED["medium-nofatigue.txt"])

    def test_path_endpoints(self):
        _, path, _ = self.graph.shortest_path(self.start, self.end)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[-1], self.end)

    def test_distance_is_finite(self):
        dist, _, _ = self.graph.shortest_path(self.start, self.end)
        self.assertLess(dist, math.inf)


class TestImplicitGraphMediumSmallFatigue(TimedTestCase):

    @classmethod
    def setUpClass(cls):
        net = Network.from_file(NET_DIR / "medium-smallfatigue.txt")
        cls.graph = net.build_implicit_graph()
        cls.start = net.start
        cls.end = net.end

    def test_distance(self):
        dist, _, _ = self.graph.shortest_path(self.start, self.end)
        self.assertEqual(dist, EXPECTED["medium-smallfatigue.txt"])

    def test_path_endpoints(self):
        _, path, _ = self.graph.shortest_path(self.start, self.end)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[-1], self.end)

    def test_distance_is_finite(self):
        dist, _, _ = self.graph.shortest_path(self.start, self.end)
        self.assertLess(dist, math.inf)


class TestImplicitGraphMediumLargeFatigue(TimedTestCase):

    @classmethod
    def setUpClass(cls):
        net = Network.from_file(NET_DIR / "medium-largefatigue.txt")
        cls.graph = net.build_implicit_graph()
        cls.start = net.start
        cls.end = net.end

    def test_distance(self):
        dist, _, _ = self.graph.shortest_path(self.start, self.end)
        self.assertEqual(dist, EXPECTED["medium-largefatigue.txt"])

    def test_path_endpoints(self):
        _, path, _ = self.graph.shortest_path(self.start, self.end)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[-1], self.end)

    def test_distance_is_finite(self):
        dist, _, _ = self.graph.shortest_path(self.start, self.end)
        self.assertLess(dist, math.inf)


class TestImplicitGraphLargeNoFatigue(TimedTestCase):

    @classmethod
    def setUpClass(cls):
        net = Network.from_file(NET_DIR / "large-nofatigue.txt")
        cls.graph = net.build_implicit_graph()
        cls.start = net.start
        cls.end = net.end

    def test_distance(self):
        dist, _, _ = self.graph.shortest_path(self.start, self.end)
        self.assertEqual(dist, EXPECTED["large-nofatigue.txt"])

    def test_path_endpoints(self):
        _, path, _ = self.graph.shortest_path(self.start, self.end)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[-1], self.end)

    def test_distance_is_finite(self):
        dist, _, _ = self.graph.shortest_path(self.start, self.end)
        self.assertLess(dist, math.inf)


class TestImplicitGraphLargeSmallFatigue(TimedTestCase):

    @classmethod
    def setUpClass(cls):
        net = Network.from_file(NET_DIR / "large-smallfatigue.txt")
        cls.graph = net.build_implicit_graph()
        cls.start = net.start
        cls.end = net.end

    def test_distance(self):
        dist, _, _ = self.graph.shortest_path(self.start, self.end)
        self.assertEqual(dist, EXPECTED["large-smallfatigue.txt"])

    def test_path_endpoints(self):
        _, path, _ = self.graph.shortest_path(self.start, self.end)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[-1], self.end)

    def test_distance_is_finite(self):
        dist, _, _ = self.graph.shortest_path(self.start, self.end)
        self.assertLess(dist, math.inf)


class TestImplicitGraphLargeLargeFatigue(TimedTestCase):

    @classmethod
    def setUpClass(cls):
        net = Network.from_file(NET_DIR / "large-largefatigue.txt")
        cls.graph = net.build_implicit_graph()
        cls.start = net.start
        cls.end = net.end

    def test_distance(self):
        dist, _, _ = self.graph.shortest_path(self.start, self.end)
        self.assertEqual(dist, EXPECTED["large-largefatigue.txt"])

    def test_path_endpoints(self):
        _, path, _ = self.graph.shortest_path(self.start, self.end)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[-1], self.end)

    def test_distance_is_finite(self):
        dist, _, _ = self.graph.shortest_path(self.start, self.end)
        self.assertLess(dist, math.inf)


if __name__ == "__main__":
    unittest.main(verbosity=2)
