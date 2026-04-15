"""
Unit tests for multi-mission routing (MultipleMissionsGraph).

All tests use the medium-smallfatigue.txt network (100 nodes, v0..v99).
Known single-mission reference: shortest_path(v0, v99) = 29934.
"""

import sys
import math
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / "code"))

import unittest
from network import Network

NET_DIR = ROOT / "examples"
NETWORK_FILE = NET_DIR / "medium-smallfatigue.txt"

EXPECTED_V0_V99 = 29934  # ground truth from expected_distances.txt


@unittest.skipUnless(NETWORK_FILE.exists(), f"{NETWORK_FILE} not found")
class TestShortestPathMultipleMissions(unittest.TestCase):
    """Tests for shortest_path_multiple_missions on medium-smallfatigue."""

    @classmethod
    def setUpClass(cls):
        net = Network.from_file(NETWORK_FILE)
        cls.graph = net.build_multi_missions_graph()
        cls.start = net.start   # 'v0'
        cls.end = net.end       # 'v99'

    def test_single_mission_matches_reference(self):
        """
        A single mission (v0, v99) through shortest_path_multiple_missions
        must give the same distance as the reference shortest_path result.
        """
        dist, _ = self.graph.shortest_path_multiple_missions(
            [(self.start, self.end)]
        )
        self.assertEqual(dist, EXPECTED_V0_V99)

    def test_single_mission_is_finite(self):
        dist, _ = self.graph.shortest_path_multiple_missions(
            [(self.start, self.end)]
        )
        self.assertLess(dist, math.inf)

    def test_two_missions_is_finite(self):
        """Two chained missions must produce a finite total distance."""
        missions = [(self.start, "v25"), ("v50", self.end)]
        dist, _ = self.graph.shortest_path_multiple_missions(missions)
        self.assertLess(dist, math.inf)

    def test_two_missions_more_expensive_than_one(self):
        """
        Completing two missions (v0->v25 then v50->v99) must cost at least as
        much as going directly from v0 to v99, because the two-mission path
        includes all the waypoints of the direct path plus detours, under
        increasing fatigue.
        """
        direct_dist, _ = self.graph.shortest_path_multiple_missions(
            [(self.start, self.end)]
        )
        two_mission_dist, _ = self.graph.shortest_path_multiple_missions(
            [(self.start, "v25"), ("v50", self.end)]
        )
        self.assertGreaterEqual(two_mission_dist, direct_dist)

    def test_unreachable_mission_returns_inf(self):
        """A mission referencing a non-existent node must return math.inf."""
        dist, _ = self.graph.shortest_path_multiple_missions(
            [(self.start, "v_unknown")]
        )
        self.assertEqual(dist, math.inf)


@unittest.skipUnless(NETWORK_FILE.exists(), f"{NETWORK_FILE} not found")
class TestBestShortestPathMultipleMissions(unittest.TestCase):
    """Tests for best_shortest_path_multiple_missions on medium-smallfatigue."""

    @classmethod
    def setUpClass(cls):
        net = Network.from_file(NETWORK_FILE)
        cls.graph = net.build_multi_missions_graph()
        cls.start = net.start
        cls.end = net.end

    def test_empty_missions(self):
        dist, path = self.graph.best_shortest_path_multiple_missions([])
        self.assertEqual(dist, math.inf)
        self.assertEqual(path, [])

    def test_single_mission_matches_reference(self):
        """Single mission must match the known reference distance."""
        dist, _ = self.graph.best_shortest_path_multiple_missions(
            [(self.start, self.end)]
        )
        self.assertEqual(dist, EXPECTED_V0_V99)

    def test_optimal_leq_any_fixed_order(self):
        """
        The optimal ordering found by best_shortest_path_multiple_missions must
        cost no more than any specific fixed ordering of the same missions.
        """
        missions = [(self.start, "v25"), ("v50", self.end)]

        best_dist, _ = self.graph.best_shortest_path_multiple_missions(missions)

        for fixed_order in [
            [(self.start, "v25"), ("v50", self.end)],
            [("v50", self.end), (self.start, "v25")],
        ]:
            fixed_dist, _ = self.graph.shortest_path_multiple_missions(fixed_order)
            self.assertLessEqual(best_dist, fixed_dist)

    def test_optimal_is_finite(self):
        missions = [(self.start, "v25"), ("v50", self.end)]
        dist, _ = self.graph.best_shortest_path_multiple_missions(missions)
        self.assertLess(dist, math.inf)

    def test_optimal_with_three_missions_is_finite(self):
        missions = [(self.start, "v10"), ("v30", "v60"), ("v70", self.end)]
        dist, _ = self.graph.best_shortest_path_multiple_missions(missions)
        self.assertLess(dist, math.inf)

    def test_path_contains_all_mission_waypoints_three_missions(self):
        """
        Same check with three missions: every mission start and end must
        appear in the returned path.
        """
        missions = [("v0", "v15"), ("v51", "v99"), ("v10", "v75")]
        _, path = self.graph.best_shortest_path_multiple_missions(missions)

        all_waypoints = {node for mission in missions for node in mission}
        for waypoint in all_waypoints:
            self.assertIn(waypoint, path, msg=f"Waypoint {waypoint} missing from path")


    def test_optimal_with_three_missions_leq_fixed_order(self):
        """Optimal over 3 missions (6 permutations) must beat any single ordering."""

        missions = [("v0", "v15"), ("v51", "v99"), ("v10", "v75")]
        best_dist, best_path = self.graph.best_shortest_path_multiple_missions(missions)
        expected_distance, expected_path = 119376, ['v0', 'v7', 'v9', 'v17', 'v12', 'v21', 'v23', 'v15', 'v19', 'v10',
                                                    'v7', 'v9', 'v18', 'v27', 'v36', 'v32', 'v33', 'v40', 'v47', 'v48',
                                                    'v56', 'v58', 'v63', 'v68', 'v73', 'v78', 'v87', 'v85', 'v75', 'v72',
                                                    'v67', 'v62', 'v55', 'v51', 'v58', 'v63', 'v73', 'v81', 'v88', 'v91',
                                                    'v95', 'v99']
        self.assertEqual(expected_distance, best_dist)
        self.assertEqual(expected_path, best_path)




if __name__ == "__main__":
    unittest.main(verbosity=2)
