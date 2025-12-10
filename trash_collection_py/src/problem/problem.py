"""Problem class for trash collection VRP."""

import logging
import math
from typing import List, Dict, Tuple, Optional
from ..base_classes.tw_node import TwBucket, TwNode, NodeType
from ..base_classes.phantom_node import PhantomNode
from .trash_node import TrashNode
from .data_loader import DataLoader

logger = logging.getLogger(__name__)

# Global travel time matrix (simplified TWC)
_travel_time_matrix: Dict[Tuple[int, int], float] = {}


def get_travel_time(from_nid: int, to_nid: int) -> float:
    """Get travel time between two nodes.
    
    Args:
        from_nid: Source node id
        to_nid: Destination node id
        
    Returns:
        Travel time in minutes
    """
    key = (from_nid, to_nid)
    if key in _travel_time_matrix:
        return _travel_time_matrix[key]
    
    # Fallback: estimate from coordinates if available
    # This is a placeholder - would need node coordinates
    return 15.0  # Default 15 minutes


def set_travel_time(from_nid: int, to_nid: int, time: float) -> None:
    """Set travel time between two nodes.
    
    Args:
        from_nid: Source node id
        to_nid: Destination node id
        time: Travel time in minutes
    """
    _travel_time_matrix[(from_nid, to_nid)] = time


class ProbTrash:
    """
    Problem class for trash collection VRP.
    
    Manages all problem data: containers, depots, dumps, vehicles, etc.
    """
    
    def __init__(self, infile: Optional[str] = None):
        """Initialize problem from file base name.
        
        Args:
            infile: Base filename (without extension), or None for empty problem
        """
        self.datafile: str = infile or ""
        self.datanodes: TwBucket[TrashNode] = TwBucket()
        self.otherlocs: TwBucket[TrashNode] = TwBucket()
        self.dumps: TwBucket[TrashNode] = TwBucket()
        self.depots: TwBucket[TrashNode] = TwBucket()
        self.pickups: TwBucket[TrashNode] = TwBucket()
        self.endings: TwBucket[TrashNode] = TwBucket()
        self.invalid: TwBucket[TrashNode] = TwBucket()
        self.phantom_nodes: Dict[int, PhantomNode] = {}
        self.trucks: List[Dict] = []
        self.invalid_trucks: List[Dict] = []
        self.C: TrashNode = TrashNode()  # Average node
        
        if infile:
            self.load_problem(infile)
    
    def load_problem(self, infile: str) -> None:
        """Load problem from files.
        
        Args:
            infile: Base filename
        """
        logger.info(f"Loading problem: {infile}")
        
        # Load pickups (containers)
        pickups_list = DataLoader.load_containers(f"{infile}.containers.txt")
        for node in pickups_list:
            node.set_type(NodeType.PICKUP)
            self.pickups.push_back(node)
        
        # Load other locations
        other_locs_list = DataLoader.load_other_locs(f"{infile}.otherlocs.txt")
        for node in other_locs_list:
            self.otherlocs.push_back(node)
        
        # Check for intersection (invalid nodes)
        intersection = self._find_intersection(self.otherlocs, self.pickups)
        if intersection:
            logger.warning("Found nodes in both otherlocs and pickups - removing from pickups")
            for node in intersection:
                self.invalid.push_back(node)
                # Remove from pickups
                pos = self.pickups.pos(node.nid)
                if pos >= 0:
                    self.pickups.erase(pos)
        
        # Combine all nodes
        nodes = TwBucket[TrashNode]()
        for node in self.pickups.path:
            nodes.push_back(node)
        for node in self.otherlocs.path:
            nodes.push_back(node)
        
        # Assign nids
        for i, node in enumerate(nodes.path):
            node.set_nid(i)
            # Update in original buckets
            if self.pickups.has_nid(node.id):
                pos = self.pickups.pos_from_id(node.id)
                if pos >= 0:
                    self.pickups[pos].set_nid(i)
            elif self.otherlocs.has_nid(node.id):
                pos = self.otherlocs.pos_from_id(node.id)
                if pos >= 0:
                    self.otherlocs[pos].set_nid(i)
        
        self.datanodes = nodes
        
        # Calculate average node C
        self._calculate_average_node()
        
        # Load distance matrix
        matrix = DataLoader.load_distance_matrix(f"{infile}.dmatrix-time.txt")
        for (from_id, to_id), cost in matrix.items():
            # Find nids for these ids
            from_nid = self._get_nid_from_id(from_id)
            to_nid = self._get_nid_from_id(to_id)
            if from_nid >= 0 and to_nid >= 0:
                set_travel_time(from_nid, to_nid, cost)
        
        # Load vehicles
        vehicles_list = DataLoader.load_vehicles(f"{infile}.vehicles.txt")
        for vehicle in vehicles_list:
            if self._validate_vehicle(vehicle):
                self.trucks.append(vehicle)
                # Add to depots, dumps, endings
                self._add_vehicle_locations(vehicle)
            else:
                self.invalid_trucks.append(vehicle)
        
        logger.info(f"Loaded {len(self.pickups)} pickups, {len(self.otherlocs)} other locations, "
                   f"{len(self.trucks)} vehicles")
    
    def _find_intersection(
        self,
        bucket1: TwBucket[TrashNode],
        bucket2: TwBucket[TrashNode]
    ) -> List[TrashNode]:
        """Find intersection of two buckets by id."""
        intersection = []
        ids1 = {node.id for node in bucket1.path}
        for node in bucket2.path:
            if node.id in ids1:
                intersection.append(node)
        return intersection
    
    def _calculate_average_node(self) -> None:
        """Calculate average node C from pickups."""
        if not self.pickups.path:
            return
        
        total_x = sum(node.x for node in self.pickups.path)
        total_y = sum(node.y for node in self.pickups.path)
        total_demand = sum(node.demand for node in self.pickups.path)
        total_opens = sum(node.opens for node in self.pickups.path)
        total_closes = sum(node.closes for node in self.pickups.path)
        total_service = sum(node.service_time for node in self.pickups.path)
        
        n = len(self.pickups.path)
        self.C = TrashNode(
            x=total_x / n,
            y=total_y / n,
            nid=-1,
            node_id=-1,
            demand=total_demand / n,
            opens=total_opens / n,
            closes=total_closes / n,
            service_time=total_service / n
        )
    
    def _get_nid_from_id(self, node_id: int) -> int:
        """Get nid from user id."""
        for node in self.datanodes.path:
            if node.id == node_id:
                return node.nid
        return -1
    
    def _validate_vehicle(self, vehicle: Dict) -> bool:
        """Validate vehicle data.
        
        Args:
            vehicle: Vehicle dictionary
            
        Returns:
            True if valid
        """
        # Check that all location ids exist in otherlocs
        for loc_id in [vehicle['start_id'], vehicle['dump_id'], vehicle['end_id']]:
            if not any(node.id == loc_id for node in self.otherlocs.path):
                return False
        return True
    
    def _add_vehicle_locations(self, vehicle: Dict) -> None:
        """Add vehicle locations to appropriate buckets.
        
        Args:
            vehicle: Vehicle dictionary
        """
        # Find nodes by id
        start_node = self._find_node_by_id(vehicle['start_id'])
        dump_node = self._find_node_by_id(vehicle['dump_id'])
        end_node = self._find_node_by_id(vehicle['end_id'])
        
        if start_node:
            start_node.set_type(NodeType.START)
            if not self.depots.has_nid(start_node.nid):
                self.depots.push_back(start_node)
        
        if dump_node:
            dump_node.set_type(NodeType.DUMP)
            if not self.dumps.has_nid(dump_node.nid):
                self.dumps.push_back(dump_node)
        
        if end_node:
            end_node.set_type(NodeType.END)
            if not self.endings.has_nid(end_node.nid):
                self.endings.push_back(end_node)
    
    def _find_node_by_id(self, node_id: int) -> Optional[TrashNode]:
        """Find node by user id."""
        for node in self.otherlocs.path:
            if node.id == node_id:
                return node
        return None
    
    def get_node_count(self) -> int:
        """Get total node count."""
        return len(self.datanodes.path)
    
    def distance(self, n1: int, n2: int) -> float:
        """Get distance between two nodes by nid.
        
        Args:
            n1: First node nid
            n2: Second node nid
            
        Returns:
            Distance
        """
        node1 = self._get_node_by_nid(n1)
        node2 = self._get_node_by_nid(n2)
        if node1 and node2:
            return node1.distance(node2)
        return float('inf')
    
    def _get_node_by_nid(self, nid: int) -> Optional[TrashNode]:
        """Get node by nid."""
        for node in self.datanodes.path:
            if node.nid == nid:
                return node
        return None
    
    def node_demand(self, nid: int) -> float:
        """Get demand for node."""
        node = self._get_node_by_nid(nid)
        return node.demand if node else 0.0
    
    def node_service_time(self, nid: int) -> float:
        """Get service time for node."""
        node = self._get_node_by_nid(nid)
        return node.service_time if node else 0.0
    
    def early_arrival(self, nid: int, arrival_time: float) -> bool:
        """Check if arrival is early."""
        node = self._get_node_by_nid(nid)
        return node.early_arrival(arrival_time) if node else False
    
    def late_arrival(self, nid: int, arrival_time: float) -> bool:
        """Check if arrival is late."""
        node = self._get_node_by_nid(nid)
        return node.late_arrival(arrival_time) if node else False
    
    def check_integrity(self) -> bool:
        """Check problem integrity.
        
        Returns:
            True if problem is valid
        """
        if not self.pickups.path:
            logger.error("No pickups loaded")
            return False
        if not self.otherlocs.path:
            logger.error("No other locations loaded")
            return False
        if not self.trucks:
            logger.error("No vehicles loaded")
            return False
        return True
    
    def pickup_has_phantom_node(self, node_id: int) -> Tuple[bool, Optional[PhantomNode]]:
        """Check if pickup has phantom node.
        
        Args:
            node_id: Pickup node id
            
        Returns:
            Tuple of (has_phantom, phantom_node)
        """
        if node_id in self.phantom_nodes:
            return True, self.phantom_nodes[node_id]
        return False, None

