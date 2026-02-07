"""Playback controller for automatic frame advancement."""

from typing import Callable


class PlaybackController:
    """Manages playback state and timing."""
    
    def __init__(self, frame_callback: Callable[[int], None]):
        """Initialize with callback for frame updates.
        
        Args:
            frame_callback: Callback to advance frame
        """
        self.frame_callback = frame_callback
        self.is_playing = False
        self.fps = 30
        self._timer_id = None
        self._after_func = None
    
    def play(self, fps: int = 30):
        """Start playback at specified frame rate.
        
        Args:
            fps: Frames per second
        """
        self.fps = fps
        self.is_playing = True
    
    def pause(self):
        """Pause playback."""
        self.is_playing = False
        if self._timer_id and self._after_func:
            self._after_func.after_cancel(self._timer_id)
            self._timer_id = None
    
    def stop(self):
        """Stop playback and return to first frame."""
        self.pause()
        # Caller should handle returning to first frame
    
    def set_frame_rate(self, fps: int):
        """Change playback frame rate.
        
        Args:
            fps: New frames per second
        """
        self.fps = fps
    
    def set_after_func(self, after_func):
        """Set the tkinter after function for scheduling.
        
        Args:
            after_func: Tkinter widget with after() method
        """
        self._after_func = after_func
    
    def schedule_next_frame(self):
        """Schedule next frame advancement."""
        if self.is_playing and self._after_func:
            delay = int(1000 / self.fps)
            self._timer_id = self._after_func.after(delay, self.frame_callback)
