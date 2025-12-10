"""Basic tests for trash collection VRP."""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.base_classes.node import Node
from src.base_classes.tw_node import TwNode, NodeType
from src.problem.trash_node import TrashNode


class TestNode(unittest.TestCase):
    """Test Node class."""
    
    def test_node_creation(self):
        """Test node creation."""
        node = Node(x=1.0, y=2.0, nid=1, node_id=1)
        self.assertEqual(node.x, 1.0)
        self.assertEqual(node.y, 2.0)
        self.assertEqual(node.nid, 1)
        self.assertEqual(node.id, 1)
    
    def test_node_distance(self):
        """Test distance calculation."""
        node1 = Node(x=0.0, y=0.0)
        node2 = Node(x=3.0, y=4.0)
        distance = node1.distance(node2)
        self.assertAlmostEqual(distance, 5.0, places=1)


class TestTwNode(unittest.TestCase):
    """Test TwNode class."""
    
    def test_twnode_creation(self):
        """Test TwNode creation."""
        node = TwNode(
            x=1.0, y=2.0, nid=1, node_id=1,
            demand=5.0, opens=0.0, closes=100.0,
            service_time=10.0
        )
        self.assertEqual(node.demand, 5.0)
        self.assertEqual(node.opens, 0.0)
        self.assertEqual(node.closes, 100.0)
    
    def test_time_window_checks(self):
        """Test time window checks."""
        node = TwNode(opens=10.0, closes=20.0)
        self.assertTrue(node.early_arrival(5.0))
        self.assertTrue(node.late_arrival(25.0))
        self.assertTrue(node.on_time(15.0))


class TestTrashNode(unittest.TestCase):
    """Test TrashNode class."""
    
    def test_trashnode_from_string(self):
        """Test TrashNode creation from string."""
        line = "1 -56.196  -34.868  1320 1800 216 1.5 -1"
        node = TrashNode.from_string(line)
        self.assertEqual(node.id, 1)
        self.assertAlmostEqual(node.x, -56.196, places=3)
        self.assertAlmostEqual(node.y, -34.868, places=3)
        self.assertEqual(node.demand, 1.5)


if __name__ == '__main__':
    unittest.main()

