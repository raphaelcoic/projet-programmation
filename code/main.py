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
G_extended = network_2.build_extended_graph(max_fatigue = 100)
#print(G_extended.shortest_path(network_2.start, network_2.end))


#Test graphe implicite
G_implicit = network_2.build_implicit_graph()
print(G_implicit.shortest_path(network_2.start, network_2.end))