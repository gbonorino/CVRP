"""Utility classes - Logger, Stats, Timer."""

import logging
import os
import time
from typing import Dict, Optional
from collections import defaultdict


class Logger:
    """Simple logger wrapper."""
    
    @staticmethod
    def setup_logging(log_dir: str = "./logs/", log_to_stderr: bool = False):
        """Setup logging configuration.
        
        Args:
            log_dir: Directory for log files
            log_to_stderr: Whether to log to stderr
        """
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"{log_dir}/vrp_trash_collection.log"),
                logging.StreamHandler() if log_to_stderr else logging.NullHandler()
            ]
        )


class Stats:
    """Statistics collection class."""
    
    _instance: Optional['Stats'] = None
    
    def __init__(self):
        """Initialize stats (private, use instance())."""
        self._counts: Dict[str, int] = defaultdict(int)
    
    @classmethod
    def instance(cls) -> 'Stats':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def inc(self, key: str) -> None:
        """Increment counter for key."""
        self._counts[key] += 1
    
    def get(self, key: str) -> int:
        """Get count for key."""
        return self._counts.get(key, 0)
    
    def reset(self) -> None:
        """Reset all statistics."""
        self._counts.clear()
    
    def dump(self, prefix: str = "") -> str:
        """Dump statistics to string.
        
        Args:
            prefix: Optional prefix for output
            
        Returns:
            Formatted statistics string
        """
        lines = [f"{prefix}Statistics:"]
        for key, count in sorted(self._counts.items()):
            lines.append(f"  {key}: {count}")
        return "\n".join(lines)


class Timer:
    """Simple timer class."""
    
    def __init__(self):
        """Initialize timer."""
        self._start_time: Optional[float] = None
        self._elapsed: float = 0.0
    
    def start(self) -> None:
        """Start timer."""
        self._start_time = time.time()
    
    def stop(self) -> float:
        """Stop timer and return elapsed time.
        
        Returns:
            Elapsed time in seconds
        """
        if self._start_time is not None:
            self._elapsed = time.time() - self._start_time
            self._start_time = None
        return self._elapsed
    
    def elapsed(self) -> float:
        """Get elapsed time without stopping.
        
        Returns:
            Elapsed time in seconds
        """
        if self._start_time is not None:
            return time.time() - self._start_time
        return self._elapsed
    
    def reset(self) -> None:
        """Reset timer."""
        self._start_time = None
        self._elapsed = 0.0


# Global instances
def get_stats() -> Stats:
    """Get stats instance."""
    return Stats.instance()

