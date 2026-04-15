from network import Network

# ---------------------------------------------------------------------------
# Simple graph — ignores fatigue
# ---------------------------------------------------------------------------
print("=== Simple graph (small.txt) ===")
net_small = Network.from_file("../examples/small.txt")
G_simple = net_small.build_simple_graph()
dist, path, _ = G_simple.shortest_path(net_small.start, net_small.end)
print(f"Distance : {dist}")
print(f"Path     : {path}")

# ---------------------------------------------------------------------------
# Extended graph — pre-expanded fatigue states
# ---------------------------------------------------------------------------
print("\n=== Extended graph (medium-smallfatigue.txt) ===")
net_medium = Network.from_file("../examples/medium-smallfatigue.txt")
G_extended = net_medium.build_extended_graph(max_fatigue=1000)
dist, path, _ = G_extended.shortest_path(net_medium.start, net_medium.end)
print(f"Distance : {dist}")
print(f"Path     : {path}")

# ---------------------------------------------------------------------------
# Implicit graph — fatigue computed on the fly
# ---------------------------------------------------------------------------
print("\n=== Implicit graph (medium-largefatigue.txt) ===")
net_large = Network.from_file("../examples/medium-largefatigue.txt")
G_implicit = net_large.build_implicit_graph()
dist, path, _ = G_implicit.shortest_path(net_large.start, net_large.end)
print(f"Distance : {dist}")
print(f"Path     : {path}")

# ---------------------------------------------------------------------------
# Multi-mission graph — exact ordering with fatigue propagation
# ---------------------------------------------------------------------------
print("\n=== Multi-mission graph (medium-smallfatigue.txt) ===")
G_multi = net_medium.build_multi_missions_graph()
missions = [("v0", "v15"), ("v51", "v99"), ("v10", "v75")]

best_dist, best_path = G_multi.best_shortest_path_multiple_missions(missions)
print(f"Best distance : {best_dist}")
print(f"Best path     : {best_path}")
