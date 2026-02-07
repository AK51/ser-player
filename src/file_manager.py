"""High-level interface for video file operations (SER and AVI)."""

import os
from typing import Optional, Union
from PIL import Image
import numpy as np

from .ser_parser import SERParser, SERHeader, SERError
from .avi_parser import AVIParser, AVIHeader
from .image_processor import ImageProcessor
from .frame_cache import FrameCache


class VideoFile:
    """Unified interface for SER and AVI video files."""
    
    def __init__(self, file_path: str, cache_size: int = 10):
        """Open and parse video file (SER or AVI).
        
        Args:
            file_path: Path to video file
            cache_size: Maximum number of frames to cache
            
        Raises:
            Exception: If file cannot be opened or parsed
        """
        self.file_path = file_path
        self.cache = FrameCache(max_size=cache_size)
        
        # Determine file type and create appropriate parser
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.ser':
            self.parser = SERParser(file_path)
            self.header = self.parser.parse_header()
            self.file_type = 'SER'
        elif ext in ['.avi', '.mp4']:
            self.parser = AVIParser(file_path)
            self.header = AVIHeader(self.parser)
            self.file_type = 'AVI' if ext == '.avi' else 'MP4'
        else:
            raise Exception(f"Unsupported file format: {ext}")
    
    def get_header(self) -> Union[SERHeader, AVIHeader]:
        """Get parsed header information.
        
        Returns:
            Header object (SERHeader or AVIHeader)
        """
        return self.header
    
    def get_display_frame(self, frame_index: int) -> Image.Image:
        """Get frame ready for display.
        
        Args:
            frame_index: Zero-based frame index
            
        Returns:
            PIL Image object in RGB mode
            
        Raises:
            Exception: If frame cannot be retrieved
        """
        # Check cache first
        cached_frame = self.cache.get(frame_index)
        if cached_frame is not None:
            return Image.fromarray(cached_frame, mode='RGB')
        
        # Parse raw frame
        raw_frame = self.parser.get_frame(frame_index)
        
        # Process frame (only for SER files with Bayer patterns)
        if self.file_type == 'SER':
            processed_frame = ImageProcessor.process_frame(
                raw_frame,
                self.header.color_id,
                self.header.pixel_depth
            )
        else:
            # AVI frames are already in RGB format
            processed_frame = raw_frame
        
        # Cache processed frame
        self.cache.put(frame_index, processed_frame)
        
        return Image.fromarray(processed_frame, mode='RGB')
    
    def get_frame_info(self, frame_index: int) -> dict:
        """Get information about specific frame.
        
        Args:
            frame_index: Zero-based frame index
            
        Returns:
            Dictionary with frame_index, timestamp (if available)
        """
        info = {
            'frame_index': frame_index,
            'timestamp': None
        }
        
        if self.parser.has_timestamps():
            try:
                info['timestamp'] = self.parser.get_timestamp(frame_index)
            except Exception:
                pass
        
        return info
    
    def prefetch_frames(self, frame_indices: list):
        """Prefetch frames for smooth playback.
        
        Args:
            frame_indices: List of frame indices to prefetch
        """
        def fetch_func(idx):
            raw_frame = self.parser.get_frame(idx)
            if self.file_type == 'SER':
                return ImageProcessor.process_frame(
                    raw_frame,
                    self.header.color_id,
                    self.header.pixel_depth
                )
            else:
                return raw_frame
        
        self.cache.prefetch(frame_indices, fetch_func)
    
    def get_file_size(self) -> int:
        """Get file size in bytes.
        
        Returns:
            File size in bytes
        """
        return os.path.getsize(self.file_path)
    
    def close(self):
        """Close file and release resources."""
        self.parser.close()
        self.cache.clear()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Keep SERFile as alias for backward compatibility
SERFile = VideoFile
