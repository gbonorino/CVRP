"""Data loader for trash collection problem files."""

import logging
from typing import List, Dict, Tuple
from .trash_node import TrashNode
from ..base_classes.tw_node import TwBucket, NodeType

logger = logging.getLogger(__name__)


class DataLoader:
    """Loads data from text files for trash collection problem."""
    
    @staticmethod
    def load_containers(filename: str) -> List[TrashNode]:
        """Load containers from file.
        
        Format: id x y opens closes service demand street_id
        
        Args:
            filename: Path to containers file
            
        Returns:
            List of TrashNode objects
        """
        containers = []
        with open(filename, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                try:
                    node = TrashNode.from_string(line)
                    containers.append(node)
                except (ValueError, IndexError) as e:
                    logger.warning(f"Error loading container at line {line_num}: {e}")
        
        return containers
    
    @staticmethod
    def load_other_locs(filename: str) -> List[TrashNode]:
        """Load other locations (depots, dumps, endings) from file.
        
        Format: id x y opens closes
        
        Args:
            filename: Path to otherlocs file
            
        Returns:
            List of TrashNode objects
        """
        other_locs = []
        with open(filename, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                try:
                    parts = line.split()
                    if len(parts) < 3:
                        continue
                    
                    node_id = int(parts[0])
                    x = float(parts[1])
                    y = float(parts[2])
                    opens = float(parts[3]) if len(parts) > 3 else 0.0
                    closes = float(parts[4]) if len(parts) > 4 else float('inf')
                    
                    node = TrashNode(
                        x=x, y=y, nid=node_id, node_id=node_id,
                        opens=opens, closes=closes,
                        node_type=NodeType.UNKNOWN
                    )
                    other_locs.append(node)
                except (ValueError, IndexError) as e:
                    logger.warning(f"Error loading other location at line {line_num}: {e}")
        
        return other_locs
    
    @staticmethod
    def load_vehicles(filename: str) -> List[Dict]:
        """Load vehicles from file.
        
        Format: vid start_id dump_id end_id capacity max_trips shift_start shift_end
        
        Args:
            filename: Path to vehicles file
            
        Returns:
            List of vehicle dictionaries
        """
        vehicles = []
        with open(filename, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                try:
                    parts = line.split()
                    if len(parts) < 5:
                        continue
                    
                    vehicle = {
                        'vid': int(parts[0]),
                        'start_id': int(parts[1]),
                        'dump_id': int(parts[2]),
                        'end_id': int(parts[3]),
                        'capacity': float(parts[4]),
                        'max_trips': int(parts[5]) if len(parts) > 5 else 1,
                        'shift_start': float(parts[6]) if len(parts) > 6 else 0.0,
                        'shift_end': float(parts[7]) if len(parts) > 7 else float('inf')
                    }
                    vehicles.append(vehicle)
                except (ValueError, IndexError) as e:
                    logger.warning(f"Error loading vehicle at line {line_num}: {e}")
        
        return vehicles
    
    @staticmethod
    def load_distance_matrix(filename: str) -> Dict[Tuple[int, int], float]:
        """Load distance/time matrix from file.
        
        Format: from_id to_id cost
        
        Args:
            filename: Path to distance matrix file
            
        Returns:
            Dictionary mapping (from_id, to_id) to cost
        """
        matrix = {}
        with open(filename, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                try:
                    parts = line.split()
                    if len(parts) < 3:
                        continue
                    
                    from_id = int(parts[0])
                    to_id = int(parts[1])
                    cost = float(parts[2])
                    
                    matrix[(from_id, to_id)] = cost
                except (ValueError, IndexError) as e:
                    logger.warning(f"Error loading distance matrix at line {line_num}: {e}")
        
        return matrix

