"""Initial solution solver for trash collection VRP."""

from typing import List
from ..problem.problem import ProbTrash
from ..solution.solution import Solution
from ..solution.vehicle import Vehicle, Trip
from ..problem.trash_node import TrashNode
from .basic_operations import BasicOperations


class TruckManyVisitsDump(BasicOperations):
    """Generates initial solutions using multiple strategies."""
    
    def __init__(self, infile: str):
        """Initialize solver.
        
        Args:
            infile: Input file base name
        """
        problem = ProbTrash(infile)
        super().__init__(problem)
        self.unused_trucks = self._create_vehicles()
        self.unassigned = list(self.problem.pickups.path)
        self.fleet = []
    
    def _create_vehicles(self) -> List[Vehicle]:
        """Create vehicles from problem data."""
        from ..problem.trash_node import TrashNode
        from ..base_classes.tw_node import NodeType
        
        vehicles = []
        for truck_data in self.problem.trucks:
            # Find nodes by id
            depot = self._find_node_by_id(truck_data['start_id'])
            dump = self._find_node_by_id(truck_data['dump_id'])
            ending = self._find_node_by_id(truck_data['end_id'])
            
            if depot and dump and ending:
                # Si el depot es el mismo que el ending, crear una copia para el depot
                # para que pueda tener tipo START sin afectar el ending
                if depot.id == ending.id:
                    # Crear una copia del nodo para usar como depot
                    depot_copy = TrashNode(
                        x=depot.x,
                        y=depot.y,
                        nid=depot.nid,
                        node_id=depot.id,
                        demand=depot.demand,
                        opens=depot.opens,
                        closes=depot.closes,
                        service_time=depot.service_time,
                        street_id=depot.street_id,
                        node_type=NodeType.START,
                        hint=getattr(depot, 'hint', '')
                    )
                    depot = depot_copy
                else:
                    # Asegurar que el depot tenga tipo START
                    if not depot.is_starting():
                        depot.set_type(NodeType.START)
                
                vehicle = Vehicle(
                    vid=truck_data['vid'],
                    depot=depot,
                    dump_site=dump,
                    ending_site=ending,
                    max_capacity=truck_data['capacity'],
                    max_trips=truck_data.get('max_trips', 1),
                    shift_start=truck_data.get('shift_start', 0.0),
                    shift_end=truck_data.get('shift_end', float('inf'))
                )
                vehicles.append(vehicle)
        
        return vehicles
    
    def _find_node_by_id(self, node_id: int) -> TrashNode:
        """Find node by user id."""
        for node in self.problem.otherlocs.path:
            if node.id == node_id:
                return node
        return None
    
    def process(self, case: int) -> None:
        """Process initial solution with given strategy.
        
        Args:
            case: Strategy number (1-7)
        """
        self.fleet = []
        self.unassigned = list(self.problem.pickups.path)
        self.unused_trucks = self._create_vehicles()
        
        if case == 1:
            self._strategy1()
        elif case == 2:
            self._strategy2()
        elif case == 3:
            self._strategy3()
        elif case == 4:
            self._strategy4()
        elif case == 5:
            self._strategy5()
        elif case == 6:
            self._strategy6()
        elif case == 7:
            self._strategy7()
        else:
            self._strategy1()  # Default
    
    def _strategy1(self) -> None:
        """Strategy 1: Nearest neighbor."""
        while self.unassigned and self.unused_trucks:
            vehicle = self.unused_trucks.pop(0)
            trip = Trip(vehicle.depot, vehicle.dump_site, vehicle.max_capacity)
            
            while self.unassigned:
                best_node = None
                best_pos = -1
                best_cost = float('inf')
                
                for node in self.unassigned:
                    for pos in range(1, len(trip.path.path) + 1):
                        if self.safe_insert_node(trip, node, pos):
                            cost = trip.get_cost()
                            if cost < best_cost:
                                best_cost = cost
                                best_node = node
                                best_pos = pos
                            self.safe_delete_node(trip, pos)
                
                if best_node:
                    self.safe_insert_node(trip, best_node, best_pos)
                    self.unassigned.remove(best_node)
                else:
                    break
            
            vehicle.add_trip(trip)
            self.fleet.append(vehicle)
    
    def _strategy2(self) -> None:
        """Strategy 2: Similar to strategy 1 with different ordering."""
        self._strategy1()  # Placeholder
    
    def _strategy3(self) -> None:
        """Strategy 3: Another variant."""
        self._strategy1()  # Placeholder
    
    def _strategy4(self) -> None:
        """Strategy 4: Another variant."""
        self._strategy1()  # Placeholder
    
    def _strategy5(self) -> None:
        """Strategy 5: Another variant."""
        self._strategy1()  # Placeholder
    
    def _strategy6(self) -> None:
        """Strategy 6: Another variant."""
        self._strategy1()  # Placeholder
    
    def _strategy7(self) -> None:
        """Strategy 7: Another variant."""
        self._strategy1()  # Placeholder
    
    def get_cost_osrm(self) -> float:
        """Get cost using OSRM."""
        total = 0.0
        for vehicle in self.fleet:
            total += vehicle.get_cost_osrm()
        return total
    
    def to_solution(self) -> Solution:
        """Convert to Solution object."""
        solution = Solution(self.problem)
        solution.fleet = self.fleet
        solution.evaluate()
        return solution

