"""Vehicle and Trip classes."""

from typing import List, Optional
from ..base_classes.tw_node import TwPath, NodeType
from ..problem.trash_node import TrashNode


class Trip:
    """Represents a single trip for a vehicle."""
    
    def __init__(
        self,
        depot: TrashNode,
        dump_site: TrashNode,
        max_capacity: float
    ):
        """Initialize a trip.
        
        Args:
            depot: Starting depot
            dump_site: Dump site for this trip
            max_capacity: Maximum capacity
        """
        self.depot = depot
        self.dump_site = dump_site
        self.max_capacity = max_capacity
        self.path: TwPath[TrashNode] = TwPath()
        self.path.push_back(depot)
    
    def size(self) -> int:
        """Get path size."""
        return len(self.path.path)
    
    def evaluate(self) -> None:
        """Evaluate the trip."""
        if self.path.path:
            self.path.evaluate(0, self.max_capacity)
    
    def feasable(self) -> bool:
        """Check if trip is feasible."""
        if not self.path.path:
            return False
        return self.path.path[-1].feasable(self.max_capacity)
    
    def get_cost(self) -> float:
        """Get cost of trip."""
        if not self.path.path:
            return 0.0
        last = self.path.path[-1]
        return last.departure_time
    
    def count_pickups(self) -> int:
        """Count number of pickups in trip."""
        return sum(1 for node in self.path.path if node.is_pickup())


class Vehicle:
    """Represents a vehicle with multiple trips."""
    
    def __init__(
        self,
        vid: int,
        depot: TrashNode,
        dump_site: TrashNode,
        ending_site: TrashNode,
        max_capacity: float,
        max_trips: int = 1,
        shift_start: float = 0.0,
        shift_end: float = float('inf')
    ):
        """Initialize a vehicle.
        
        Args:
            vid: Vehicle id
            depot: Starting depot
            dump_site: Dump site
            ending_site: Ending site
            max_capacity: Maximum capacity
            max_trips: Maximum number of trips
            shift_start: Shift start time
            shift_end: Shift end time
        """
        self.vid = vid
        self.depot = depot
        self.dump_site = dump_site
        self.ending_site = ending_site
        self.max_capacity = max_capacity
        self.max_trips = max_trips
        self.shift_start = shift_start
        self.shift_end = shift_end
        self.trips: List[Trip] = []
        self.cost: float = 0.0
    
    def size(self) -> int:
        """Get total number of nodes in all trips."""
        return sum(trip.size() for trip in self.trips)
    
    def evaluate(self) -> None:
        """Evaluate all trips."""
        for trip in self.trips:
            trip.evaluate()
        self._compute_cost()
    
    def feasable(self) -> bool:
        """Check if vehicle is feasible."""
        return all(trip.feasable() for trip in self.trips)
    
    def _compute_cost(self) -> None:
        """Compute total cost."""
        self.cost = sum(trip.get_cost() for trip in self.trips)
    
    def get_cost(self) -> float:
        """Get total cost."""
        return self.cost
    
    def get_cost_osrm(self) -> float:
        """Get cost using OSRM (placeholder)."""
        return self.get_cost()
    
    def count_pickups(self) -> int:
        """Count total pickups."""
        return sum(trip.count_pickups() for trip in self.trips)
    
    def add_trip(self, trip: Trip) -> None:
        """Add a trip to vehicle."""
        self.trips.append(trip)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Vehicle(vid={self.vid}, trips={len(self.trips)}, cost={self.cost})"

