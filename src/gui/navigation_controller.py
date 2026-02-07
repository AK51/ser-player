"""Navigation controller for frame navigation."""

from typing import Callable


class NavigationController:
    """Manages frame navigation."""
    
    def __init__(self, total_frames: int, frame_callback: Callable[[int], None]):
        """Initialize with total frame count and callback.
        
        Args:
            total_frames: Total number of frames
            frame_callback: Callback function to call when frame changes
        """
        self.total_frames = total_frames
        self.frame_callback = frame_callback
        self.current_frame = 0
    
    def next_frame(self):
        """Advance to next frame."""
        if self.current_frame < self.total_frames - 1:
            self.current_frame += 1
            self.frame_callback(self.current_frame)
    
    def previous_frame(self):
        """Go to previous frame."""
        if self.current_frame > 0:
            self.current_frame -= 1
            self.frame_callback(self.current_frame)
    
    def first_frame(self):
        """Jump to first frame."""
        self.current_frame = 0
        self.frame_callback(self.current_frame)
    
    def last_frame(self):
        """Jump to last frame."""
        self.current_frame = self.total_frames - 1
        self.frame_callback(self.current_frame)
    
    def goto_frame(self, frame_index: int):
        """Jump to specific frame.
        
        Args:
            frame_index: Frame index to jump to
        """
        if 0 <= frame_index < self.total_frames:
            self.current_frame = frame_index
            self.frame_callback(self.current_frame)
    
    def get_current_frame(self) -> int:
        """Get current frame index.
        
        Returns:
            Current frame index
        """
        return self.current_frame
