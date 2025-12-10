"""Node class - defines a point in 2D space with an id."""

import math
from typing import Optional


class Node:
    """
    A Node is a point that defines a location in 2D space.
    
    It maintains a user id and an internal nid along with its x, y location.
    This is the base object that things like depots, customer locations, etc.
    are built upon.
    """
    
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        nid: int = 0,
        node_id: int = 0,
        hint: str = ""
    ):
        """Initialize a Node.
        
        Args:
            x: x or longitude of the node's location
            y: y or latitude of the node's location
            nid: internal node number
            node_id: user supplied node number
            hint: OSRM hint string
        """
        self._nid: int = nid
        self._id: int = node_id
        self._x: float = x
        self._y: float = y
        self._hint: str = hint
        self._valid: bool = node_id > 0
    
    @classmethod
    def from_string(cls, line: str) -> 'Node':
        """Create a Node by parsing a string.
        
        Args:
            line: String with format "id x y" or "id x y hint"
            
        Returns:
            A new Node instance
        """
        parts = line.strip().split()
        if len(parts) < 3:
            raise ValueError(f"Invalid node string: {line}")
        
        node_id = int(parts[0])
        x = float(parts[1])
        y = float(parts[2])
        hint = parts[3] if len(parts) > 3 else ""
        
        valid = node_id >= 0
        nid = node_id if valid else 0
        
        return cls(x=x, y=y, nid=nid, node_id=nid, hint=hint)
    
    # Accessors
    @property
    def nid(self) -> int:
        """Get internal node number."""
        return self._nid
    
    @property
    def id(self) -> int:
        """Get user supplied node number."""
        return self._id
    
    @property
    def x(self) -> float:
        """Get x or longitude coordinate."""
        return self._x
    
    @property
    def y(self) -> float:
        """Get y or latitude coordinate."""
        return self._y
    
    @property
    def hint(self) -> str:
        """Get OSRM hint string."""
        return self._hint
    
    # State checks
    def is_lat_lon(self) -> bool:
        """Check if coordinates are in lat/lon format."""
        return -180 < self._x < 180 and -90 < self._y < 90
    
    def is_valid(self) -> bool:
        """Check if node is valid."""
        return self._valid
    
    def is_same_pos(self, other: 'Node', tolerance: float = 0.0) -> bool:
        """Check if this node is at the same position as another.
        
        Args:
            other: Another Node to compare
            tolerance: Distance tolerance (0.0 for exact match)
            
        Returns:
            True if nodes are at the same position
        """
        if tolerance == 0.0:
            return self.distance(other) == 0.0
        return self.distance(other) < tolerance
    
    def has_hint(self) -> bool:
        """Check if node has an OSRM hint."""
        return bool(self._hint)
    
    # Mutators
    def clear(self) -> None:
        """Clear all node attributes."""
        self._nid = 0
        self._id = 0
        self._x = 0.0
        self._y = 0.0
        self._hint = ""
        self._valid = False
    
    def set(self, nid: int, x: float, y: float) -> None:
        """Set node attributes.
        
        Args:
            nid: Node id (used for both nid and id)
            x: x coordinate
            y: y coordinate
        """
        self._id = self._nid = nid
        self._x = x
        self._y = y
        self._valid = True
    
    def set_nid(self, nid: int) -> None:
        """Set internal node number."""
        self._nid = nid
    
    def set_id(self, node_id: int) -> None:
        """Set user node id."""
        self._id = node_id
        self._valid = node_id > 0
    
    def set_x(self, x: float) -> None:
        """Set x coordinate."""
        self._x = x
    
    def set_y(self, y: float) -> None:
        """Set y coordinate."""
        self._y = y
    
    def set_hint(self, hint: str) -> None:
        """Set OSRM hint string."""
        self._hint = hint
    
    # Operators
    def __lt__(self, other: 'Node') -> bool:
        """Less than comparison by nid."""
        return self._nid < other._nid
    
    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if not isinstance(other, Node):
            return False
        return (self._nid == other._nid and
                self._x == other._x and
                self._y == other._y)
    
    def __ne__(self, other: object) -> bool:
        """Inequality comparison."""
        return not self.__eq__(other)
    
    def __gt__(self, other: 'Node') -> bool:
        """Greater than comparison by nid."""
        return self._nid > other._nid
    
    # Vector operations
    def __add__(self, other: 'Node') -> 'Node':
        """Vector addition."""
        return Node(x=self._x + other._x, y=self._y + other._y)
    
    def __sub__(self, other: 'Node') -> 'Node':
        """Vector subtraction."""
        return Node(x=self._x - other._x, y=self._y - other._y)
    
    def __mul__(self, factor: float) -> 'Node':
        """Scalar multiplication."""
        return Node(x=self._x * factor, y=self._y * factor)
    
    def dot_product(self, other: 'Node') -> float:
        """Compute vector dot product."""
        return self._x * other._x + self._y * other._y
    
    def length(self) -> float:
        """Compute Euclidean length of vector."""
        return math.sqrt(self._x * self._x + self._y * self._y)
    
    def gradient(self, other: 'Node') -> float:
        """Compute gradient or slope of vector.
        
        Returns:
            Gradient value, or infinity if deltaX is zero
        """
        delta_y = other._y - self._y
        delta_x = other._x - self._x
        
        if delta_x == 0:
            return float('inf') if delta_y >= 0 else float('-inf')
        return delta_y / delta_x
    
    def unit(self) -> 'Node':
        """Compute unit vector."""
        length = self.length()
        if length == 0.0:
            return Node(x=0.0, y=0.0)
        scale = 1.0 / length
        return self * scale
    
    # Distance calculations
    def distance(self, other: 'Node') -> float:
        """Compute distance to another node.
        
        Uses Haversine for lat/lon coordinates, Euclidean otherwise.
        """
        if self.is_lat_lon() and other.is_lat_lon():
            return self.haversine_distance(other)
        return self.distance_to(other)
    
    def haversine_distance(self, other: 'Node') -> float:
        """Compute Haversine spherical distance between two nodes.
        
        Assumes x,y are loaded with longitude,latitude values.
        """
        pi = math.pi
        deg2rad = pi / 180.0
        radius = 6367000  # Earth radius 6367 Km in meters
        
        dlon = (other._x - self._x) * deg2rad
        dlat = (other._y - self._y) * deg2rad
        
        a = (math.sin(dlat / 2.0) ** 2 +
             math.cos(self._y * deg2rad) * math.cos(other._y * deg2rad) *
             math.sin(dlon / 2.0) ** 2)
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        
        return radius * c
    
    def distance_to(self, other: 'Node') -> float:
        """Compute Euclidean distance to another node."""
        return math.sqrt(self.distance_to_squared(other))
    
    def distance_to_squared(self, other: 'Node') -> float:
        """Compute Euclidean distance squared to another node."""
        dx = other._x - self._x
        dy = other._y - self._y
        return dx * dx + dy * dy
    
    def distance_to_segment(
        self,
        v: 'Node',
        w: 'Node',
        q: Optional['Node'] = None
    ) -> float:
        """Compute shortest distance from this node to a line segment.
        
        Args:
            v: Start of segment
            w: End of segment
            q: Optional output parameter for closest point on segment
            
        Returns:
            Distance to segment
        """
        dist_sq = v.distance_to_squared(w)
        
        if dist_sq == 0.0:  # v == w case
            if q is not None:
                q.set(v._x, v._y)
            return self.distance_to(v)
        
        # Find projection of point onto line
        t = ((self - v).dot_product(w - v)) / dist_sq
        
        if t < 0.0:  # Beyond v end
            if q is not None:
                q.set(v._x, v._y)
            return self.distance_to(v)
        
        if t > 1.0:  # Beyond w end
            if q is not None:
                q.set(w._x, w._y)
            return self.distance_to(w)
        
        # Projection falls on segment
        projection = v + ((w - v) * t)
        if q is not None:
            q.set(projection._x, projection._y)
        
        return self.distance_to(projection)
    
    def position_along_segment(self, v: 'Node', w: 'Node', tol: float) -> float:
        """Compute position along line segment.
        
        Args:
            v: Start of segment
            w: End of segment
            tol: Distance tolerance
            
        Returns:
            Position 0.0 to 1.0 along segment, or -1.0 if not within tolerance
        """
        tolerance_sqr = tol * tol
        distance_sqr = v.distance_to_squared(w)
        
        if distance_sqr == 0.0:
            return 0.0 if self.distance_to_squared(v) < tolerance_sqr else -1.0
        
        t = ((self - v).dot_product(w - v)) / distance_sqr
        
        if t < 0.0 or t > 1.0:
            return -1.0
        
        projection = v + ((w - v) * t)
        if self.distance_to_squared(projection) > tolerance_sqr:
            return -1.0
        
        return t
    
    def is_right_to_segment(self, line_begin: 'Node', line_end: 'Node') -> bool:
        """Check if node is to the right of a line segment."""
        return ((line_end._x - line_begin._x) * (self._y - line_begin._y) -
                (line_end._y - line_begin._y) * (self._x - line_begin._x)) < 0
    
    def dump(self) -> str:
        """Return string representation for debugging."""
        return f"Node(nid={self._nid}, id={self._id}, x={self._x}, y={self._y}, hint={self._hint})"
    
    def __repr__(self) -> str:
        """String representation."""
        return self.dump()

