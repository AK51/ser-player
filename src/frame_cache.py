"""Frame cache with LRU eviction for improved performance."""

from collections import OrderedDict
from typing import Optional, Callable, List
import numpy as np


class FrameCache:
    """LRU cache for processed frames."""
    
    def __init__(self, max_size: int = 10):
        """Initialize cache with maximum size.
        
        Args:
            max_size: Maximum number of frames to cache
        """
        self.max_size = max_size
        self._cache: OrderedDict[int, np.ndarray] = OrderedDict()
    
    def get(self, frame_index: int) -> Optional[np.ndarray]:
        """Retrieve frame from cache if present.
        
        Args:
            frame_index: Frame index to retrieve
            
        Returns:
            Cached frame or None if not in cache
        """
        if frame_index in self._cache:
            # Move to end (most recently used)
            self._cache.move_to_end(frame_index)
            return self._cache[frame_index]
        return None
    
    def put(self, frame_index: int, frame_data: np.ndarray):
        """Add frame to cache, evicting oldest if necessary.
        
        Args:
            frame_index: Frame index
            frame_data: Processed frame data
        """
        # If already in cache, update and move to end
        if frame_index in self._cache:
            self._cache.move_to_end(frame_index)
            self._cache[frame_index] = frame_data
        else:
            # Add new frame
            self._cache[frame_index] = frame_data
            
            # Evict oldest if over limit
            if len(self._cache) > self.max_size:
                self._cache.popitem(last=False)
    
    def clear(self):
        """Clear all cached frames."""
        self._cache.clear()
    
    def prefetch(self, frame_indices: List[int], fetch_func: Callable[[int], np.ndarray]):
        """Prefetch frames for smooth playback.
        
        Args:
            frame_indices: List of frame indices to prefetch
            fetch_func: Function to fetch frame if not cached
        """
        for frame_index in frame_indices:
            if frame_index not in self._cache:
                try:
                    frame_data = fetch_func(frame_index)
                    self.put(frame_index, frame_data)
                except Exception:
                    # Silently ignore prefetch errors
                    pass
    
    def __len__(self) -> int:
        """Get number of cached frames."""
        return len(self._cache)
    
    def __contains__(self, frame_index: int) -> bool:
        """Check if frame is in cache."""
        return frame_index in self._cache
