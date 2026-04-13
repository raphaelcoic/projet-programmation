import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / "code"))

import unittest
from network import Network
from graph import Graph, GraphExtended, GraphImplicit

NET_DIR = ROOT / "examples"


class TimedTestCase(unittest.TestCase):
    def setUp(self):
        self._start = time.perf_counter()

    def tearDown(self):
        elapsed = time.perf_counter() - self._start
        print(f"\n  [{self._testMethodName}]  {elapsed:.4f}s")


class TestSimpleGraphCreation(TimedTestCase):

    def test_small_is_graph(self):
        net = Network.from_file(NET_DIR / "small.txt")
        g = net.build_simple_graph()
        self.assertIsInstance(g, Graph)
        self.assertNotIsInstance(g, GraphExtended)
        self.assertNotIsInstance(g, GraphImplicit)

    def test_small_edges_match_roads(self):
        net = Network.from_file(NET_DIR / "small.txt")
        g = net.build_simple_graph()
        # Fatigue should be stripped; only (dest, length) pairs remain
        self.assertEqual(g._edges["lozere"], [("ensae", 10), ("guichet", 20)])
        self.assertEqual(g._edges["ensae"], [("saclay", 45)])

    def test_medium_is_graph(self):
        net = Network.from_file(NET_DIR / "medium-nofatigue.txt")
        g = net.build_simple_graph()
        self.assertIsInstance(g, Graph)

    def test_medium_edge_count(self):
        net = Network.from_file(NET_DIR / "medium-nofatigue.txt")
        g = net.build_simple_graph()
        self.assertGreater(len(g._edges), 0)


class TestExtendedGraphCreation(TimedTestCase):

    def test_small_is_extended(self):
        net = Network.from_file(NET_DIR / "small.txt")
        g = net.build_extended_graph(max_fatigue=10)
        self.assertIsInstance(g, GraphExtended)

    def test_small_extended_edges_non_empty(self):
        net = Network.from_file(NET_DIR / "small.txt")
        g = net.build_extended_graph(max_fatigue=10)
        self.assertGreater(len(g._extended_edges), 0)

    def test_small_extended_keys_are_tuples(self):
        net = Network.from_file(NET_DIR / "small.txt")
        g = net.build_extended_graph(max_fatigue=10)
        for key in g._extended_edges:
            self.assertIsInstance(key, tuple)
            self.assertEqual(len(key), 2)

    def test_medium_is_extended(self):
        net = Network.from_file(NET_DIR / "medium-smallfatigue.txt")
        g = net.build_extended_graph(max_fatigue=50)
        self.assertIsInstance(g, GraphExtended)

    def test_medium_extended_edges_non_empty(self):
        net = Network.from_file(NET_DIR / "medium-smallfatigue.txt")
        g = net.build_extended_graph(max_fatigue=50)
        self.assertGreater(len(g._extended_edges), 0)


class TestImplicitGraphCreation(TimedTestCase):

    def test_small_is_implicit(self):
        net = Network.from_file(NET_DIR / "small.txt")
        g = net.build_implicit_graph()
        self.assertIsInstance(g, GraphImplicit)

    def test_small_neighbours_callable(self):
        net = Network.from_file(NET_DIR / "small.txt")
        g = net.build_implicit_graph()
        self.assertTrue(callable(g.neighbours))

    def test_small_neighbours_output(self):
        net = Network.from_file(NET_DIR / "small.txt")
        g = net.build_implicit_graph()
        # Starting at lozere with fatigue=1: ensae has fatigue_increment=2
        result = g.neighbours(("lozere", 1))
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        for dest, weight in result:
            self.assertIsInstance(dest, tuple)
            self.assertIsInstance(weight, (int, float))

    def test_medium_is_implicit(self):
        net = Network.from_file(NET_DIR / "medium-nofatigue.txt")
        g = net.build_implicit_graph()
        self.assertIsInstance(g, GraphImplicit)


if __name__ == "__main__":
    unittest.main(verbosity=2)
