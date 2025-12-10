"""Fleet optimization for trash collection VRP."""

from typing import List
from ..solution.solution import Solution
from ..solution.vehicle import Vehicle


class FleetOpt:
    """Fleet optimizer."""
    
    def __init__(self):
        """Initialize fleet optimizer."""
        self.fleet: List[Vehicle] = []
        self.ids: List[int] = []
        self.trips: List = []  # List of trips
    
    def optimize(self, iterations: int) -> None:
        """Optimize fleet.
        
        Args:
            iterations: Number of iterations
        """
        self.extract_trips()
        
        # Placeholder for fleet optimization
        # Would include:
        # - intraTripOptimizationNoOsrm()
        # - exchangesWorse()
        # - exchangesWithOnPath()
        # - exchangesWithNotOnPath()
        # - reconstruct_fleet()
        pass
    
    def get_opt_fleet(self) -> List[Vehicle]:
        """Get optimized fleet."""
        return self.fleet
    
    def insert(self, fleet: List[Vehicle]) -> None:
        """Insert fleet to optimize.
        
        Args:
            fleet: List of vehicles
        """
        self.fleet = fleet
    
    def extract_trips(self) -> None:
        """Extract trips from fleet."""
        self.trips = []
        self.ids = []
        for i, vehicle in enumerate(self.fleet):
            for trip in vehicle.trips:
                self.ids.append(i)
                self.trips.append(trip)
    
    def reconstruct_fleet(self) -> None:
        """Reconstruct fleet from optimized trips."""
        # Clear existing trips in fleet
        for truck in self.fleet:
            truck.trips.clear()
        
        # Reassign trips to vehicles
        for i, trip in enumerate(self.trips):
            if i < len(self.ids) and self.ids[i] < len(self.fleet):
                self.fleet[self.ids[i]].add_trip(trip)


class Optimizer(Solution):
    """Optimizer that extends Solution."""
    
    def __init__(self, solution: Solution, iterations: int):
        """Initialize optimizer.
        
        Args:
            solution: Initial solution
            iterations: Number of iterations
        """
        super().__init__(solution)
        self.fleet = list(solution.fleet) if solution.fleet else []
        self.optimize_fleet(iterations)
    
    def optimize_fleet(self, iterations: int) -> None:
        """Optimize fleet.
        
        Args:
            iterations: Number of iterations
        """
        fleet_opt = FleetOpt()
        fleet_opt.insert(self.fleet)
        fleet_opt.optimize(iterations)
        self.fleet = fleet_opt.get_opt_fleet()
        self.evaluate()

