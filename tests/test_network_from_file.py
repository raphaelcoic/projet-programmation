# This will work if ran from the root folder (the folder in which there is the subfolder code/)
import sys 
sys.path.append("code/")

import unittest 
from network import Network

class Test_NetworkLoading(unittest.TestCase):
    def test_network_small(self):
        network = Network.from_file("examples/small.txt")
        self.assertEqual(network.start, "lozere")
        self.assertEqual(network.end, "saclay")
        self.assertEqual(network._roads, {'lozere': [('ensae', 10, 2), ('guichet', 20, 0)], 
                                          'ensae': [('saclay', 45, 0)], 
                                          'guichet': [('ensae', 15, 1)],
                                          'saclay': []})

if __name__ == '__main__':
    unittest.main()
