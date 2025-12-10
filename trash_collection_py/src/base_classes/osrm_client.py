"""OSRM Client - provides connection to OSRM routing service."""

import os
import logging
from typing import List, Optional, Deque
from .node import Node

logger = logging.getLogger(__name__)


class OsrmClient:
    """
    This class provides a connection to OSRM.
    
    This class interfaces with OSRM via HTTP API and wraps the interface
    into a simple class to abstract the features we need access to.
    """
    
    _instance: Optional['OsrmClient'] = None
    _connection_available: bool = True
    
    def __init__(self):
        """Initialize OSRM client (private, use Instance())."""
        self._status: int = 0
        self._err_msg: str = ""
        self._use: bool = False
        self._coordinates: List[tuple] = []  # List of (lon, lat) tuples
        self._hints: List[str] = []
        self._osrm_base_url: str = os.getenv(
            'OSRM_BASE_URL',
            'http://localhost:5000'
        )
    
    @classmethod
    def instance(cls) -> 'OsrmClient':
        """Get singleton instance of OsrmClient."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def use_osrm(self, decision: bool) -> None:
        """Set whether to use OSRM."""
        self._use = decision
    
    def get_use(self) -> bool:
        """Get whether OSRM is being used."""
        return self._use
    
    def clear(self) -> None:
        """Reset the OsrmClient to a clean state."""
        self._coordinates.clear()
        self._hints.clear()
        self._status = 0
        self._err_msg = ""
    
    def add_via_point(self, node: Node) -> None:
        """Add a location in WGS84 to the OSRM request.
        
        Args:
            node: Node to add as via point
        """
        self._coordinates.append((node.x, node.y))
        if node.has_hint():
            self._hints.append(node.hint)
        else:
            self._hints.append("")
    
    def add_via_points(self, path: List[Node]) -> None:
        """Add a path of nodes as locations to the OSRM request.
        
        Args:
            path: List of nodes to add
        """
        for node in path:
            self.add_via_point(node)
    
    def get_osrm_time(self, node1: Node, node2: Node) -> Optional[float]:
        """Get OSRM travel time between two nodes.
        
        Args:
            node1: First node
            node2: Second node
            
        Returns:
            Travel time in minutes, or None if error
        """
        if not self._connection_available or not self._use:
            return None
        
        self.clear()
        self.add_via_point(node1)
        self.add_via_point(node2)
        
        if self._get_osrm_viaroute():
            return self._extract_time()
        return None
    
    def get_osrm_times(self) -> Optional[List[float]]:
        """Get OSRM travel times for each leg of the path.
        
        Returns:
            List of travel times for each leg, or None if error
        """
        if not self._connection_available or not self._use:
            return None
        
        # This would need to parse the OSRM response
        # For now, return None as placeholder
        return None
    
    def get_osrm_geometry(self) -> Optional[List[Node]]:
        """Extract geometry from OSRM response.
        
        Returns:
            List of nodes representing the path geometry, or None if error
        """
        if not self._connection_available or not self._use:
            return None
        
        # This would need to parse the OSRM response
        # For now, return None as placeholder
        return None
    
    def get_osrm_hints(self) -> Optional[List[str]]:
        """Extract hints from OSRM response.
        
        Returns:
            List of hint strings, or None if error
        """
        if not self._connection_available or not self._use:
            return None
        
        # This would need to parse the OSRM response
        # For now, return None as placeholder
        return None
    
    def get_osrm_street_names(self) -> Optional[List[str]]:
        """Extract street names from OSRM response.
        
        Returns:
            List of street names, or None if error
        """
        if not self._connection_available or not self._use:
            return None
        
        # This would need to parse the OSRM response
        # For now, return None as placeholder
        return None
    
    def get_osrm_nearest(
        self,
        node: Node
    ) -> Optional[tuple]:
        """Get nearest point on road network.
        
        Args:
            node: Input node
            
        Returns:
            Tuple of (nearest_node, distance, street_name) or None if error
        """
        if not self._connection_available or not self._use:
            return None
        
        # This would need to call OSRM nearest API
        # For now, return None as placeholder
        return None
    
    def test_osrm_client(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        x3: float,
        y3: float
    ) -> bool:
        """Test OSRM client connection.
        
        Args:
            x1, y1: First point coordinates
            x2, y2: Second point coordinates
            x3, y3: Third point coordinates
            
        Returns:
            True if test successful
        """
        old_use = self._use
        self._use = True
        
        if not self._connection_available:
            self._use = old_use
            return False
        
        if self._status == -1:
            self._use = old_use
            return False
        
        # Test with first two points
        node1 = Node(x=x1, y=y1)
        node2 = Node(x=x2, y=y2)
        
        time = self.get_osrm_time(node1, node2)
        if time is None:
            self._use = old_use
            return False
        
        logger.info(f"Test time: {time}")
        
        # Test with all three points
        self.clear()
        self.add_via_point(Node(x=x1, y=y1))
        self.add_via_point(Node(x=x2, y=y2))
        self.add_via_point(Node(x=x3, y=y3))
        self.add_via_point(Node(x=x1, y=y1))
        
        if not self._get_osrm_viaroute():
            self._use = old_use
            return False
        
        self._use = old_use
        return True
    
    def get_status(self) -> int:
        """Get current status."""
        return self._status
    
    def get_connection(self) -> bool:
        """Get connection availability."""
        return self._connection_available
    
    def get_error_msg(self) -> str:
        """Get error message."""
        return self._err_msg
    
    def _get_osrm_viaroute(self) -> bool:
        """Connect to OSRM engine and issue request.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._connection_available or not self._use:
            return False
        
        if len(self._coordinates) < 2:
            self._status = -1
            self._err_msg = "Need at least 2 coordinates"
            return False
        
        # TODO: Implement actual OSRM HTTP request
        # For now, this is a placeholder that would use requests library
        # to call OSRM API
        
        try:
            # Placeholder for actual OSRM API call
            # import requests
            # url = f"{self._osrm_base_url}/route/v1/driving/"
            # coords = ";".join([f"{lon},{lat}" for lon, lat in self._coordinates])
            # response = requests.get(f"{url}{coords}")
            # Parse response...
            
            self._status = 1
            return True
        except Exception as e:
            self._err_msg = f"OsrmClient error: {str(e)}"
            logger.error(self._err_msg)
            self._status = -1
            return False
    
    def _extract_time(self) -> Optional[float]:
        """Extract travel time from OSRM response.
        
        Returns:
            Travel time in minutes, or None if error
        """
        # TODO: Parse actual OSRM JSON response
        # For now, return None as placeholder
        return None


# Global instance accessor
def osrmi() -> OsrmClient:
    """Get OSRM client instance."""
    return OsrmClient.instance()

