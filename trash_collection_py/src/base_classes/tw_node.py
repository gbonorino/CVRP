"""Time Window Node classes - TwNode, TwPath, TwBucket."""

from typing import List, Optional, TypeVar, Generic, Deque
from enum import IntEnum
from .node import Node

KNode = TypeVar('KNode', bound=Node)


class NodeType(IntEnum):
    """Node type enumeration."""
    INVALID = -2
    UNKNOWN = -1
    START = 0
    PICKUP = 1
    DUMP = 2
    END = 3
    DELIVERY = 4
    LOAD = 5
    PHANTOM_NODE = 100


class TwNode(Node):
    """
    Extends Node class to create a Node with time window attributes.
    
    A Time Window node is a Node with additional attributes and methods to
    support Time Windows and to model a more complex Node needed in many
    vehicle routing problems.
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
        """Initialize a TwNode.
        
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
        super().__init__(x, y, nid, node_id, hint)
        self._type: NodeType = node_type
        self._demand: float = demand
        self._opens: float = opens
        self._closes: float = closes
        self._service_time: float = service_time
        self._street_id: int = street_id
    
    @classmethod
    def from_string(cls, line: str) -> 'TwNode':
        """Create a TwNode by parsing a string.
        
        Format: "id x y opens closes service demand street_id"
        """
        parts = line.strip().split()
        if len(parts) < 7:
            raise ValueError(f"Invalid TwNode string: {line}")
        
        node_id = int(parts[0])
        x = float(parts[1])
        y = float(parts[2])
        opens = float(parts[3])
        closes = float(parts[4])
        service = float(parts[5])
        demand = float(parts[6])
        street_id = int(parts[7]) if len(parts) > 7 else -1
        
        return cls(
            x=x, y=y, nid=node_id, node_id=node_id,
            demand=demand, opens=opens, closes=closes,
            service_time=service, street_id=street_id
        )
    
    # Accessors
    @property
    def opens(self) -> float:
        """Get opening time."""
        return self._opens
    
    @property
    def closes(self) -> float:
        """Get closing time."""
        return self._closes
    
    @property
    def demand(self) -> float:
        """Get demand."""
        return self._demand
    
    @property
    def service_time(self) -> float:
        """Get service time."""
        return self._service_time
    
    @property
    def type(self) -> NodeType:
        """Get node type."""
        return self._type
    
    @property
    def street_id(self) -> int:
        """Get street id."""
        return self._street_id
    
    @property
    def window_length(self) -> float:
        """Get length of time window."""
        return self._closes - self._opens
    
    # Type checks
    def is_depot(self) -> bool:
        """Check if node is a depot/starting site."""
        return self._type == NodeType.START
    
    def is_starting(self) -> bool:
        """Check if node is a starting site."""
        return self._type == NodeType.START
    
    def is_dump(self) -> bool:
        """Check if node is a dump site."""
        return self._type == NodeType.DUMP
    
    def is_pickup(self) -> bool:
        """Check if node is a pickup site."""
        return self._type == NodeType.PICKUP
    
    def is_ending(self) -> bool:
        """Check if node is an ending site."""
        return self._type == NodeType.END
    
    def is_delivery(self) -> bool:
        """Check if node is a delivery site."""
        return self._type == NodeType.DELIVERY
    
    def is_load(self) -> bool:
        """Check if node is a loading site."""
        return self._type == NodeType.LOAD
    
    def is_phantom_node(self) -> bool:
        """Check if node is a phantom node."""
        return self._type == NodeType.PHANTOM_NODE
    
    # Demand checks
    def has_demand(self) -> bool:
        """Check if node has positive demand."""
        return self._demand > 0
    
    def has_supply(self) -> bool:
        """Check if node has negative demand (supply)."""
        return self._demand < 0
    
    def has_no_goods(self) -> bool:
        """Check if node has zero demand."""
        return self._demand == 0
    
    # Time window checks
    def early_arrival(self, arrival_time: float) -> bool:
        """Check if arrival time is before opening time."""
        return arrival_time < self._opens
    
    def late_arrival(self, arrival_time: float) -> bool:
        """Check if arrival time is after closing time."""
        return arrival_time > self._closes
    
    def on_time(self, arrival_time: float) -> bool:
        """Check if arrival time is within time window."""
        return not self.early_arrival(arrival_time) and not self.late_arrival(arrival_time)
    
    # Street checks
    def same_street(self, other: 'TwNode') -> bool:
        """Check if nodes are on the same street."""
        return self._street_id == other._street_id
    
    def same_street_id(self, street_id: int) -> bool:
        """Check if node is on specified street."""
        return self._street_id == street_id
    
    # Mutators
    def set_demand(self, demand: float) -> None:
        """Set demand."""
        self._demand = demand
    
    def set_type(self, node_type: NodeType) -> None:
        """Set node type."""
        self._type = node_type
    
    def set_opens(self, opens: float) -> None:
        """Set opening time."""
        self._opens = opens
    
    def set_closes(self, closes: float) -> None:
        """Set closing time."""
        self._closes = closes
    
    def set_service_time(self, service_time: float) -> None:
        """Set service time."""
        self._service_time = service_time
    
    def set_street_id(self, street_id: int) -> None:
        """Set street id."""
        self._street_id = street_id
    
    def set(
        self,
        nid: int,
        node_id: int,
        x: float,
        y: float,
        demand: float,
        opens: float,
        closes: float,
        service_time: float,
        street_id: int = -1
    ) -> None:
        """Set all attributes."""
        super().set(nid, x, y)
        self._id = node_id
        self._demand = demand
        self._opens = opens
        self._closes = closes
        self._service_time = service_time
        self._street_id = street_id
    
    def __repr__(self) -> str:
        """String representation."""
        return (f"TwNode(nid={self._nid}, id={self._id}, x={self._x}, y={self._y}, "
                f"demand={self._demand}, opens={self._opens}, closes={self._closes}, "
                f"service={self._service_time}, type={self._type.name})")


class TwBucket(Generic[KNode]):
    """
    A template class that provides deque-like container with additional functionality.
    
    TwBucket provides a set-like container. It is used by TwPath for storage.
    It also provides several un-evaluated path operations.
    """
    
    def __init__(self, path: Optional[List[KNode]] = None):
        """Initialize TwBucket.
        
        Args:
            path: Optional initial list of nodes
        """
        self.path: List[KNode] = path if path is not None else []
    
    # Deque-like operations
    def size(self) -> int:
        """Get size of bucket."""
        return len(self.path)
    
    def empty(self) -> bool:
        """Check if bucket is empty."""
        return len(self.path) == 0
    
    def clear(self) -> None:
        """Clear all nodes."""
        self.path.clear()
    
    def push_back(self, node: KNode) -> bool:
        """Add node to end of path."""
        self.path.append(node)
        return True
    
    def push_front(self, node: KNode) -> bool:
        """Add node to beginning of path."""
        self.path.insert(0, node)
        return True
    
    def pop_back(self) -> None:
        """Remove last node."""
        if self.path:
            self.path.pop()
    
    def pop_front(self) -> None:
        """Remove first node."""
        if self.path:
            self.path.pop(0)
    
    def insert(self, node: KNode, at_pos: int) -> bool:
        """Insert node at position.
        
        Args:
            node: Node to insert
            at_pos: Position to insert at
            
        Returns:
            True if successful
        """
        if at_pos < 0 or at_pos > len(self.path):
            return False
        self.path.insert(at_pos, node)
        return True
    
    def erase(self, at_pos: int) -> bool:
        """Erase node at position.
        
        Args:
            at_pos: Position to erase
            
        Returns:
            True if successful
        """
        if at_pos < 0 or at_pos >= len(self.path):
            return False
        del self.path[at_pos]
        return True
    
    def swap(self, i: int, j: int) -> None:
        """Swap nodes at positions i and j."""
        if 0 <= i < len(self.path) and 0 <= j < len(self.path):
            self.path[i], self.path[j] = self.path[j], self.path[i]
    
    def __getitem__(self, pos: int) -> KNode:
        """Get node at position."""
        return self.path[pos]
    
    def __setitem__(self, pos: int, node: KNode) -> None:
        """Set node at position."""
        self.path[pos] = node
    
    def __len__(self) -> int:
        """Get size."""
        return len(self.path)
    
    # Node finding operations
    def has_nid(self, nid: int) -> bool:
        """Check if bucket contains node with given nid."""
        return any(node.nid == nid for node in self.path)
    
    def has_id(self, node_id: int) -> bool:
        """Check if bucket contains node with given id."""
        return any(node.id == node_id for node in self.path)
    
    def pos(self, nid: int) -> int:
        """Get position of node with given nid, or -1 if not found."""
        for i, node in enumerate(self.path):
            if node.nid == nid:
                return i
        return -1
    
    def pos_from_id(self, node_id: int) -> int:
        """Get position of node with given id, or -1 if not found."""
        for i, node in enumerate(self.path):
            if node.id == node_id:
                return i
        return -1
    
    def front(self) -> KNode:
        """Get first node."""
        if not self.path:
            raise IndexError("Bucket is empty")
        return self.path[0]
    
    def back(self) -> KNode:
        """Get last node."""
        if not self.path:
            raise IndexError("Bucket is empty")
        return self.path[-1]
    
    def last(self) -> KNode:
        """Get last node (alias for back)."""
        return self.back()


class TwPath(Generic[KNode], TwBucket[KNode]):
    """
    TwPath class members are auto-evaluating.
    
    A path is an ordered sequence of nodes from starting site to ending site.
    The problem will define which type of nodes belongs to the twpath and
    which shall be outside twpath.
    """
    
    def evaluate(self, from_pos: int, max_capacity: float) -> None:
        """Evaluate path from given position.
        
        Args:
            from_pos: Starting position for evaluation
            max_capacity: Maximum capacity of vehicle
        """
        if from_pos >= len(self.path):
            from_pos = len(self.path) - 1
        
        for i in range(from_pos, len(self.path)):
            if i == 0:
                # First node - evaluate without predecessor
                if hasattr(self.path[i], 'evaluate'):
                    self.path[i].evaluate(max_capacity)
            else:
                # Evaluate with predecessor
                if hasattr(self.path[i], 'evaluate'):
                    self.path[i].evaluate(max_capacity, self.path[i - 1])
    
    def eval_last(self, max_capacity: float) -> None:
        """Evaluate last node of path."""
        if self.path:
            self.evaluate(len(self.path) - 1, max_capacity)
    
    def e_insert(self, node: KNode, at_pos: int, max_capacity: float) -> bool:
        """Evaluated insert: Insert node and evaluate.
        
        Args:
            node: Node to insert
            at_pos: Position to insert at
            max_capacity: Maximum capacity
            
        Returns:
            True if successful
        """
        if not self.insert(node, at_pos):
            return False
        self.evaluate(at_pos, max_capacity)
        return True
    
    def e_push_back(self, node: KNode, max_capacity: float) -> bool:
        """Evaluated push_back: Add node and evaluate."""
        if not self.push_back(node):
            return False
        self.eval_last(max_capacity)
        return True
    
    def e_remove(self, pos: int, max_capacity: float) -> bool:
        """Evaluated remove: Remove node and evaluate."""
        if not self.erase(pos):
            return False
        self.evaluate(pos, max_capacity)
        return True
    
    def e_swap(self, i: int, j: int, max_capacity: float) -> bool:
        """Evaluated swap: Swap nodes and evaluate."""
        if i == j:
            return False
        self.swap(i, j)
        start_pos = min(i, j)
        self.evaluate(start_pos, max_capacity)
        return True

