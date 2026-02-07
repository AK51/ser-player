"""AVI file parser for astronomical video files."""

import numpy as np
import cv2
from typing import Optional, Tuple
from datetime import datetime


class AVIParser:
    """Parser for AVI video files."""
    
    def __init__(self, file_path: str):
        """Initialize AVI parser.
        
        Args:
            file_path: Path to AVI file
        """
        self.file_path = file_path
        self.cap = cv2.VideoCapture(file_path)
        
        if not self.cap.isOpened():
            raise Exception(f"Failed to open AVI file: {file_path}")
        
        # Get video properties
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        # Determine color format
        # Read first frame to check
        ret, frame = self.cap.read()
        if ret:
            if len(frame.shape) == 3:
                self.is_color = True
                self.channels = frame.shape[2]
            else:
                self.is_color = False
                self.channels = 1
            # Reset to beginning
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        else:
            raise Exception("Failed to read first frame from AVI file")
    
    def get_frame(self, frame_index: int) -> np.ndarray:
        """Get frame at specified index.
        
        Args:
            frame_index: Frame index (0-based)
            
        Returns:
            Frame data as numpy array
        """
        if frame_index < 0 or frame_index >= self.frame_count:
            raise ValueError(f"Frame index {frame_index} out of range [0, {self.frame_count})")
        
        # Seek to frame
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        
        # Read frame
        ret, frame = self.cap.read()
        if not ret:
            raise Exception(f"Failed to read frame {frame_index}")
        
        # OpenCV reads as BGR, convert to RGB for consistency
        if self.is_color and frame.shape[2] == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        return frame
    
    def get_timestamp(self, frame_index: int) -> Optional[datetime]:
        """Get timestamp for frame (if available).
        
        Args:
            frame_index: Frame index
            
        Returns:
            Timestamp or None if not available
        """
        # AVI files typically don't have per-frame timestamps
        # Calculate based on FPS
        if self.fps > 0:
            seconds = frame_index / self.fps
            # Use file modification time as base
            import os
            file_time = os.path.getmtime(self.file_path)
            base_time = datetime.fromtimestamp(file_time)
            # Subtract total duration to get start time
            total_duration = self.frame_count / self.fps
            start_time = datetime.fromtimestamp(file_time - total_duration)
            # Add frame offset
            from datetime import timedelta
            return start_time + timedelta(seconds=seconds)
        return None
    
    def has_timestamps(self) -> bool:
        """Check if file has timestamps.
        
        Returns:
            True if timestamps available
        """
        return self.fps > 0
    
    def close(self):
        """Close AVI file."""
        if self.cap:
            self.cap.release()
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()


class AVIHeader:
    """AVI file header information."""
    
    def __init__(self, parser: AVIParser):
        """Initialize from AVI parser.
        
        Args:
            parser: AVIParser instance
        """
        self.image_width = parser.width
        self.image_height = parser.height
        self.frame_count = parser.frame_count
        self.fps = parser.fps
        
        # Determine color ID based on format
        if parser.is_color:
            self.color_id = 100  # RGB
            self.pixel_depth = 8  # 8-bit per channel
        else:
            self.color_id = 0  # MONO
            self.pixel_depth = 8
        
        # AVI metadata (if available)
        self.observer = ""
        self.instrument = "AVI Video"
        self.telescope = ""
        
        # Try to extract metadata from filename
        import os
        filename = os.path.basename(parser.file_path)
        # Example: 2025-01-10-220715-Lunar-RAW.avi
        parts = filename.replace('.avi', '').split('-')
        if len(parts) >= 5:
            self.telescope = '-'.join(parts[4:])  # "Lunar RAW"
