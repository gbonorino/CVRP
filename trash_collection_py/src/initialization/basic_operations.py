"""Basic operations for initial solution generation."""

from typing import List
from ..problem.problem import ProbTrash
from ..solution.vehicle import Vehicle, Trip
from ..problem.trash_node import TrashNode


class BasicOperations:
    """Basic operations for manipulating vehicle routes."""
    
    def __init__(self, problem: ProbTrash):
        """Initialize with problem.
        
        Args:
            problem: Problem instance
        """
        self.problem = problem
        self.unused_trucks: List[Vehicle] = []
        self.used_trucks: List[Vehicle] = []
        self.unassigned: List[TrashNode] = []
        self.assigned: List[TrashNode] = []
        self.fleet: List[Vehicle] = []
    
    def safe_insert_node(
        self,
        trip: Trip,
        node: TrashNode,
        pos: int
    ) -> bool:
        """Safely insert node into trip.
        
        Args:
            trip: Trip to insert into
            node: Node to insert
            pos: Position to insert at
            
        Returns:
            True if successful
        """
        if pos < 0 or pos > len(trip.path.path):
            return False
        
        trip.path.path.insert(pos, node)
        trip.evaluate()
        
        if not trip.feasable():
            trip.path.path.pop(pos)
            trip.evaluate()
            return False
        
        return True
    
    def safe_delete_node(self, trip: Trip, pos: int) -> bool:
        """Safely delete node from trip.
        
        Args:
            trip: Trip to delete from
            pos: Position to delete
            
        Returns:
            True if successful
        """
        if pos < 0 or pos >= len(trip.path.path):
            return False
        
        trip.path.path.pop(pos)
        trip.evaluate()
        return True

