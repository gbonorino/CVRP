"""Solution class for trash collection VRP."""

from typing import List, Optional
from ..problem.problem import ProbTrash
from .vehicle import Vehicle
from ..base_classes.tw_node import NodeType


class Solution(ProbTrash):
    """
    Solution class extends ProbTrash to represent a solution.
    
    A solution consists of a fleet of vehicles with assigned routes.
    """
    
    def __init__(self, problem: Optional[ProbTrash] = None):
        """Initialize solution from problem.
        
        Args:
            problem: Problem instance, or None for empty solution
        """
        # Copy problem data
        if problem:
            super().__init__(problem.datafile)
            # Copy problem attributes
            self.datanodes = problem.datanodes
            self.otherlocs = problem.otherlocs
            self.dumps = problem.dumps
            self.depots = problem.depots
            self.pickups = problem.pickups
            self.endings = problem.endings
            self.trucks = problem.trucks
        else:
            super().__init__(None)
        
        self.fleet: List[Vehicle] = []
        self.total_distance: float = 0.0
        self.total_cost: float = 0.0
        self.w1: float = 1.0  # Weight for duration
        self.w2: float = 100.0  # Weight for TWV
        self.w3: float = 100.0  # Weight for CV
    
    def evaluate(self) -> None:
        """Evaluate all vehicles in fleet."""
        for vehicle in self.fleet:
            vehicle.evaluate()
        self._compute_costs()
    
    def _compute_costs(self) -> None:
        """Compute total costs."""
        self.total_cost = sum(vehicle.get_cost() for vehicle in self.fleet)
        # Distance would be computed from actual routes
        self.total_distance = self.total_cost  # Placeholder
    
    def get_cost(self) -> float:
        """Get total cost."""
        return self.total_cost
    
    def get_cost_osrm(self) -> float:
        """Get cost using OSRM."""
        self.total_cost = sum(vehicle.get_cost_osrm() for vehicle in self.fleet)
        return self.total_cost
    
    def get_distance(self) -> float:
        """Get total distance."""
        return self.total_distance
    
    def get_fleet_size(self) -> int:
        """Get number of vehicles in fleet."""
        return len(self.fleet)
    
    def feasable(self) -> bool:
        """Check if solution is feasible."""
        return all(vehicle.feasable() for vehicle in self.fleet)
    
    def count_pickups(self) -> int:
        """Count total pickups in solution."""
        return sum(vehicle.count_pickups() for vehicle in self.fleet)
    
    def compute_costs(self) -> int:
        """Compute costs and remove empty vehicles.
        
        Returns:
            Position of removed vehicle or -1
        """
        removed_pos = -1
        for i, vehicle in enumerate(self.fleet):
            if vehicle.size() == 1:  # Only depot
                removed_pos = i
                self.fleet.pop(i)
                break
        
        self._compute_costs()
        return removed_pos
    
    def set_weights(self, w1: float, w2: float, w3: float) -> None:
        """Set cost weights.
        
        Args:
            w1: Weight for duration
            w2: Weight for TWV
            w3: Weight for CV
        """
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3
    
    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if not isinstance(other, Solution):
            return False
        return (self.get_fleet_size() == other.get_fleet_size() and
                abs(self.total_cost - other.total_cost) < 0.001)
    
    def __lt__(self, other: 'Solution') -> bool:
        """Less than comparison."""
        if self.get_fleet_size() != other.get_fleet_size():
            return self.get_fleet_size() < other.get_fleet_size()
        return self.total_cost < other.total_cost
    
    def dump_solution_for_pg(self) -> None:
        """Dump solution in PostgreSQL format."""
        seq = 1
        for vehicle in self.fleet:
            for trip in vehicle.trips:
                for node in trip.path.path:
                    cost = node.departure_time if hasattr(node, 'departure_time') else 0.0
                    print(f"{seq}\t{vehicle.vid}\t{node.id}\t{cost}")
                    seq += 1
    
    def save_to_file(self, filename: str) -> None:
        """Save solution to file in .sol.txt format.
        
        Format matches the C++ solution file format:
        Each line: type id
        - -1 0 at start
        - For each vehicle: 0 vid, then nodes with type id
        - -1 vid at end of vehicle (or just -1)
        - -2 -2 at end
        
        Args:
            filename: Output filename
        """
        with open(filename, 'w') as f:
            f.write("-1 0\n")  # Start marker
            
            for vehicle in self.fleet:
                if vehicle.size() <= 1:  # Skip empty vehicles
                    continue
                
                f.write(f"0 {vehicle.vid}\n")  # Vehicle ID (type 0 = START, id = vid)
                
                # Write all trips for this vehicle
                for trip in vehicle.trips:
                    # Skip the depot node at the start of the path
                    for node in trip.path.path[1:]:  # Skip first node (depot)
                        node_type = node.type  # type is a property, not a method
                        if node_type == NodeType.PICKUP:
                            f.write(f"1 {node.id}\n")
                        elif node_type == NodeType.DUMP:
                            f.write(f"2 {node.id}\n")
                        elif node_type == NodeType.END or node_type == NodeType.START:
                            f.write(f"3 {node.id}\n")
                
                # Write dump and ending sites (always at end of vehicle)
                f.write(f"2 {vehicle.dump_site.id}\n")
                f.write(f"3 {vehicle.ending_site.id}\n")
                f.write(f"-1 {vehicle.vid}\n")  # End of vehicle marker
            
            f.write("-2 -2\n")  # End marker
    
    def solution_as_text(self) -> str:
        """Get solution as comma-separated text string.
        
        Returns:
            Comma-separated string of node nids
        """
        sol_vector = self.solution_as_vector()
        return ",".join(str(nid) for nid in sol_vector)
    
    def solution_as_text_id(self) -> str:
        """Get solution as comma-separated text string using user IDs.
        
        Returns:
            Comma-separated string of node ids
        """
        sol_vector = self.solution_as_vector_id()
        return ",".join(str(node_id) for node_id in sol_vector)
    
    def solution_as_vector(self) -> List[int]:
        """Get solution as vector of node nids (internal IDs).
        
        Returns:
            List of node nids representing the solution
        """
        sol = [-2]  # Start marker
        
        for vehicle in self.fleet:
            if vehicle.size() <= 1:  # Skip empty vehicles
                continue
            
            sol.append(vehicle.vid)
            sol.append(-2)  # Vehicle separator
            
            # Add all nodes from all trips
            for trip in vehicle.trips:
                # Skip depot at start, add all other nodes
                for node in trip.path.path[1:]:
                    sol.append(node.nid)
            
            # Add dump and depot nids
            sol.append(vehicle.dump_site.nid)
            sol.append(vehicle.depot.nid)
            sol.append(-2)  # End of vehicle
        
        return sol
    
    def solution_as_vector_id(self) -> List[int]:
        """Get solution as vector of node ids (user IDs).
        
        Returns:
            List of node ids representing the solution
        """
        sol = [-1]  # Start marker
        
        for vehicle in self.fleet:
            if vehicle.size() <= 1:  # Skip empty vehicles
                continue
            
            sol.append(vehicle.vid)
            sol.append(-1)  # Vehicle separator
            
            # Add all nodes from all trips
            for trip in vehicle.trips:
                # Skip depot at start, add all other nodes
                for node in trip.path.path[1:]:
                    sol.append(node.id)
            
            # Add dump and depot ids
            sol.append(vehicle.dump_site.id)
            sol.append(vehicle.depot.id)
            sol.append(-1)  # End of vehicle
        
        return sol
    
    def __repr__(self) -> str:
        """String representation."""
        return (f"Solution(fleet_size={len(self.fleet)}, "
                f"cost={self.total_cost}, pickups={self.count_pickups()})")

