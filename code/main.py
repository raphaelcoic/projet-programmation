from jupyter_server.services.contents import checkpoints

from network import Network
from graph import Graph

# Load the network
network_file = "../examples/small.txt"
network = Network.from_file(network_file)

# Test shortest_path
G = network.build_simple_graph()
print(G.shortest_path("lozere", "saclay"))


#Test graphe étendu
network_file_2 = "../examples/medium-smallfatigue.txt"
network_2 = Network.from_file(network_file_2)
G_extended = network_2.build_extended_graph(max_fatigue = 1000)
print(G_extended.shortest_path(network_2.start, network_2.end))


#Test graphe implicite
G_implicit = network_2.build_implicit_graph()
distance, path, _ = G_implicit.shortest_path(network_2.start, network_2.end)
print(distance)
print(path)
#G_implicit.render_graph_with_path(network_2.start, network_2.end)

#Test graphe implicite multi missions
G_implicit_multi_missions = network_2.build_implicit_graph()
missions = [('v0', 'v15'),('v87', 'v36'), ('v51', 'v99'), ('v10', 'v75')]
ordered_missions = G_implicit_multi_missions.best_missions_order(missions)
print(ordered_missions)
distance, path = G_implicit_multi_missions.shortest_path_multiple_missions(ordered_missions)
print(distance)
print(path)


