"""Playback controller for automatic frame advancement."""

from typing import Callable, Optional


class PlaybackController:
    """Manages playback state and timing."""
    
    def __init__(self, navigation_controller, prefetch_callback: Optional[Callable] = None):
        """Initialize playback controller.
        
        Args:
            navigation_controller: NavigationController instance
            prefetch_callback: Optional callback for prefetching frames
        """
        self.nav_controller = navigation_controller
        self.prefetch_callback = prefetch_callback
        self.is_playing = False
        self.fps = 30
        self.timer = None
        self.timer_callback = None
    
    def set_timer_callback(self, callback: Callable):
        """Set the timer callback function (provided by GUI).
        
        Args:
            callback: Function that schedules next frame update
        """
        self.timer_callback = callback
    
    def play(self, fps: int = 30):
        """Start playback at specified frame rate.
        
        Args:
            fps: Frames per second
        """
        self.fps = fps
        self.is_playing = True
        self._advance_frame()
    
    def pause(self):
        """Pause playback."""
        self.is_playing = False
    
    def stop(self):
        """Stop playback and return to first frame."""
        self.is_playing = False
        self.nav_controller.first_frame()
    
    def set_frame_rate(self, fps: int):
        """Change playback frame rate.
        
        Args:
            fps: New frames per second
        """
        self.fps = fps
    
    def _advance_frame(self):
        """Advance to next frame during playback."""
        if not self.is_playing:
            return
        
        current = self.nav_controller.get_current_frame()
        total = self.nav_controller.total_frames
        
        # Prefetch upcoming frames
        if self.prefetch_callback:
            prefetch_indices = [
                i for i in range(current + 1, min(current + 6, total))
            ]
            if prefetch_indices:
                self.prefetch_callback(prefetch_indices)
        
        # Advance frame
        if current < total - 1:
            self.nav_controller.next_frame()
            
            # Schedule next frame
            if self.timer_callback and self.is_playing:
                interval_ms = int(1000 / self.fps)
                self.timer_callback(interval_ms, self._advance_frame)
        else:
            # Reached end, stop playback
            self.is_playing = False
    
    def toggle_play_pause(self):
        """Toggle between play and pause."""
        if self.is_playing:
            self.pause()
        else:
            self.play(self.fps)
