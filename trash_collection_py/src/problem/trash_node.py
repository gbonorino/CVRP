"""TrashNode class - extends TwNode to evaluate vehicle at node level."""

from typing import Optional
from ..base_classes.tw_node import TwNode, NodeType


class TrashNode(TwNode):
    """
    Extends TwNode to evaluate the vehicle at node level.
    
    This class extends TwNode by adding attributes to store information
    about the node in a path and provides tools to evaluate the node
    and to set and get these attribute values.
    """
    
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        nid: int = 0,
        node_id: int = 0,
        demand: float = 0.0,
        opens: float = 0.0,
        closes: float = float('inf'),
        service_time: float = 0.0,
        street_id: int = -1,
        node_type: NodeType = NodeType.UNKNOWN,
        hint: str = ""
    ):
        """Initialize a TrashNode.
        
        Args:
            x: x or longitude coordinate
            y: y or latitude coordinate
            nid: internal node number
            node_id: user supplied node number
            demand: demand for this node
            opens: earliest possible arrival time
            closes: latest possible arrival time
            service_time: time required to service this node
            street_id: street identifier
            node_type: type of node
            hint: OSRM hint string
        """
        super().__init__(
            x, y, nid, node_id, demand, opens, closes,
            service_time, street_id, node_type, hint
        )
        # Node evaluation members
        self._travel_time: float = 0.0
        self._arrival_time: float = 0.0
        self._wait_time: float = 0.0
        self._departure_time: float = 0.0
        self._delta_time: float = 0.0
        
        # Accumulated evaluation members
        self._cargo: float = 0.0
        self._twv_tot: int = 0
        self._cv_tot: int = 0
        self._tot_wait_time: float = 0.0
        self._tot_travel_time: float = 0.0
        self._tot_service_time: float = 0.0
        self._dump_visits: int = 0
    
    @classmethod
    def from_string(cls, line: str) -> 'TrashNode':
        """Create a TrashNode by parsing a string.
        
        Format: "id x y opens closes service demand street_id"
        """
        parts = line.strip().split()
        if len(parts) < 7:
            raise ValueError(f"Invalid TrashNode string: {line}")
        
        node_id = int(parts[0])
        x = float(parts[1])
        y = float(parts[2])
        opens = float(parts[3])
        closes = float(parts[4])
        service = float(parts[5])
        demand = float(parts[6])
        street_id = int(parts[7]) if len(parts) > 7 else -1
        
        node = cls(
            x=x, y=y, nid=node_id, node_id=node_id,
            demand=demand, opens=opens, closes=closes,
            service_time=service, street_id=street_id
        )
        node.set_type(NodeType.PICKUP)
        return node
    
    # Node evaluation accessors
    @property
    def travel_time(self) -> float:
        """Get travel time from previous node."""
        return self._travel_time
    
    @property
    def arrival_time(self) -> float:
        """Get arrival time at this node."""
        return self._arrival_time
    
    @property
    def wait_time(self) -> float:
        """Get wait time at this node."""
        return self._wait_time
    
    @property
    def departure_time(self) -> float:
        """Get departure time from this node."""
        return self._departure_time
    
    @property
    def delta_time(self) -> float:
        """Get delta time (departure - previous departure)."""
        return self._delta_time
    
    # Accumulated evaluation accessors
    @property
    def twv_tot(self) -> int:
        """Get total time window violations."""
        return self._twv_tot
    
    @property
    def cv_tot(self) -> int:
        """Get total capacity violations."""
        return self._cv_tot
    
    @property
    def cargo(self) -> float:
        """Get cargo after node is served."""
        return self._cargo
    
    @property
    def duration(self) -> float:
        """Get travel duration up to this node."""
        return self._departure_time
    
    @property
    def tot_travel_time(self) -> float:
        """Get total travel time."""
        return self._tot_travel_time
    
    @property
    def tot_wait_time(self) -> float:
        """Get total wait time."""
        return self._tot_wait_time
    
    @property
    def tot_service_time(self) -> float:
        """Get total service time."""
        return self._tot_service_time
    
    @property
    def dump_visits(self) -> int:
        """Get total dump visits."""
        return self._dump_visits
    
    # State checks
    def feasable(self, cargo_limit: Optional[float] = None) -> bool:
        """Check if node is feasible.
        
        Args:
            cargo_limit: Optional cargo limit to check
            
        Returns:
            True if feasible
        """
        if cargo_limit is None:
            return self._twv_tot == 0 and self._cv_tot == 0
        return (self._twv_tot == 0 and self._cv_tot == 0 and
                not self.has_twv() and not self.has_cv(cargo_limit))
    
    def has_twv(self) -> bool:
        """Check if node has time window violation."""
        return self.late_arrival(self._arrival_time)
    
    def has_cv(self, cargo_limit: float) -> bool:
        """Check if node has capacity violation.
        
        Args:
            cargo_limit: Maximum cargo limit
            
        Returns:
            True if violation exists
        """
        return self._cargo > cargo_limit or self._cargo < 0
    
    def delta_generates_twv(self, delta_time: float) -> bool:
        """Check if delta time generates time window violation.
        
        Args:
            delta_time: Time delta to check
            
        Returns:
            True if violation would occur
        """
        return self._arrival_time + delta_time > self.closes
    
    # Evaluation methods
    def evaluate(self, cargo_limit: float, pred: Optional['TrashNode'] = None) -> None:
        """Evaluate node in path.
        
        Args:
            cargo_limit: Maximum cargo capacity
            pred: Optional predecessor node
        """
        if pred is None:
            # First node (starting site)
            self._evaluate_start(cargo_limit)
        else:
            # Node with predecessor
            self._evaluate_with_pred(pred, cargo_limit)
    
    def _evaluate_start(self, cargo_limit: float) -> None:
        """Evaluate starting node."""
        if not self.is_starting():
            raise ValueError("First node must be a starting site")
        
        self._cargo = self.demand
        self._travel_time = 0.0
        self._arrival_time = self.opens
        self._tot_travel_time = 0.0
        self._tot_wait_time = 0.0
        self._tot_service_time = self.service_time
        self._departure_time = self._arrival_time + self.service_time
        self._twv_tot = 0
        self._cv_tot = 1 if self._cargo > cargo_limit else 0
        self._delta_time = 0.0
        self._dump_visits = 0
    
    def _evaluate_with_pred(self, pred: 'TrashNode', cargo_limit: float) -> None:
        """Evaluate node with predecessor.
        
        Args:
            pred: Predecessor node
            cargo_limit: Maximum cargo capacity
        """
        # This would need access to TWC for travel time
        # For now, use placeholder
        from ..problem.problem import get_travel_time
        
        self._travel_time = get_travel_time(pred.nid, self.nid)
        self._tot_travel_time = pred._tot_travel_time + self._travel_time
        self._arrival_time = pred._departure_time + self._travel_time
        self._wait_time = self.opens - self._arrival_time if self.early_arrival(self._arrival_time) else 0.0
        self._tot_wait_time = pred._tot_wait_time + self._wait_time
        self._tot_service_time = pred._tot_service_time + self.service_time
        self._departure_time = self._arrival_time + self._wait_time + self.service_time
        
        # Handle dump sites
        if self.is_dump() and pred._cargo >= 0:
            self.set_demand(-pred._cargo)
        
        self._dump_visits = pred._dump_visits + 1 if self.is_dump() else pred._dump_visits
        self._cargo = pred._cargo + self.demand
        
        self._twv_tot = pred._twv_tot + 1 if self.has_twv() else pred._twv_tot
        self._cv_tot = pred._cv_tot + 1 if self.has_cv(cargo_limit) else pred._cv_tot
        self._delta_time = self._departure_time - pred._departure_time
    
    def __repr__(self) -> str:
        """String representation."""
        return (f"TrashNode(nid={self._nid}, id={self._id}, x={self._x}, y={self._y}, "
                f"demand={self._demand}, opens={self._opens}, closes={self._closes}, "
                f"cargo={self._cargo}, twv={self._twv_tot}, cv={self._cv_tot})")

