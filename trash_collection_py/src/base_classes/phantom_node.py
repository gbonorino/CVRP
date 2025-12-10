"""PhantomNode class - implements information of Phantom Nodes from OSRM."""

from typing import Optional
from dataclasses import dataclass


@dataclass
class Point:
    """Simple point class with x, y coordinates."""
    x: float = 0.0
    y: float = 0.0
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Point({self.x}, {self.y})"


class PhantomNode:
    """
    This class implements information of Phantom Nodes.
    
    OSRM phantom nodes are virtual nodes - the nearest point in an edge
    from an input point.
    """
    
    def __init__(
        self,
        phantom_node_id: int = 0,
        x: float = 0.0,
        y: float = 0.0,
        fw_node_id: int = 0,
        rv_node_id: int = 0,
        fw_weight: int = 0,
        rv_weight: int = 0,
        name_id: int = 0
    ):
        """Initialize a PhantomNode.
        
        Args:
            phantom_node_id: Internal phantom node number
            x: Longitude
            y: Latitude
            fw_node_id: OSRM forward node id
            rv_node_id: OSRM reverse node id
            fw_weight: OSRM forward weight
            rv_weight: OSRM reverse weight
            name_id: OSRM name id
        """
        self._phantom_node_id: int = phantom_node_id
        self._point: Point = Point(x, y)
        self._forw_node_id: int = fw_node_id
        self._reve_node_id: int = rv_node_id
        self._forw_weight: int = fw_weight
        self._reve_weight: int = rv_weight
        self._name_id: int = name_id
        self._before_p_node: Point = Point(0.0, 0.0)
        self._after_p_node: Point = Point(0.0, 0.0)
    
    @property
    def id(self) -> int:
        """Get phantom node id."""
        return self._phantom_node_id
    
    def set_id(self, phantom_node_id: int) -> None:
        """Set phantom node id."""
        self._phantom_node_id = phantom_node_id
    
    @property
    def point(self) -> Point:
        """Get point coordinates."""
        return self._point
    
    def set_point(self, point: Point) -> None:
        """Set point coordinates."""
        self._point = Point(point.x, point.y)
    
    @property
    def forw_node_id(self) -> int:
        """Get forward node id."""
        return self._forw_node_id
    
    def set_forw_node_id(self, fw_node_id: int) -> None:
        """Set forward node id."""
        self._forw_node_id = fw_node_id
    
    @property
    def reve_node_id(self) -> int:
        """Get reverse node id."""
        return self._reve_node_id
    
    def set_reve_node_id(self, rv_node_id: int) -> None:
        """Set reverse node id."""
        self._reve_node_id = rv_node_id
    
    @property
    def forw_weight(self) -> int:
        """Get forward weight."""
        return self._forw_weight
    
    def set_forw_weight(self, fw_weight: int) -> None:
        """Set forward weight."""
        self._forw_weight = fw_weight
    
    @property
    def reve_weight(self) -> int:
        """Get reverse weight."""
        return self._reve_weight
    
    def set_reve_weight(self, rv_weight: int) -> None:
        """Set reverse weight."""
        self._reve_weight = rv_weight
    
    @property
    def name_id(self) -> int:
        """Get name id."""
        return self._name_id
    
    def set_name_id(self, name_id: int) -> None:
        """Set name id."""
        self._name_id = name_id
    
    @property
    def before_p_node(self) -> Point:
        """Get point before phantom node."""
        return self._before_p_node
    
    def set_before_p_node(self, point: Point) -> None:
        """Set point before phantom node."""
        self._before_p_node = Point(point.x, point.y)
    
    @property
    def after_p_node(self) -> Point:
        """Get point after phantom node."""
        return self._after_p_node
    
    def set_after_p_node(self, point: Point) -> None:
        """Set point after phantom node."""
        self._after_p_node = Point(point.x, point.y)
    
    def in_same_street(self, other: 'PhantomNode') -> bool:
        """Check if phantom nodes are on the same street."""
        return self._name_id == other._name_id
    
    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if not isinstance(other, PhantomNode):
            return False
        return self._phantom_node_id == other._phantom_node_id
    
    def __repr__(self) -> str:
        """String representation."""
        return (f"PhantomNode(id={self._phantom_node_id}, "
                f"point={self._point}, "
                f"forw_node_id={self._forw_node_id}, "
                f"reve_node_id={self._reve_node_id}, "
                f"forw_weight={self._forw_weight}, "
                f"reve_weight={self._reve_weight}, "
                f"name_id={self._name_id}, "
                f"before={self._before_p_node}, "
                f"after={self._after_p_node})")

