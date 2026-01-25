# This will work if ran from the root folder (the folder in which there is the subfolder code/)
import sys 
sys.path.append("code/")

import pytest
from network import Network

def test_network_small():
    # Setup
    network = Network.from_file("examples/small.txt")
    
    # Assertions
    assert network.start == "lozere"
    assert network.end == "saclay"
    assert network._roads == {
        'lozere': [('ensae', 10, 2), ('guichet', 20, 0)], 
        'ensae': [('saclay', 45, 0)], 
        'guichet': [('ensae', 15, 1)],
        'saclay': []
    }