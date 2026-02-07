"""Frame stacking module for combining multiple frames with alignment."""

import numpy as np
from typing import Optional, Callable
import logging
from .frame_aligner import FrameAligner
from .lucky_imaging import LuckyImaging


class FrameStacker:
    """Stacks multiple frames to create a single high-quality image."""
    
    def __init__(self):
        """Initialize frame stacker."""
        self.logger = logging.getLogger(__name__)
        self.aligner = FrameAligner()
    
    def _auto_stretch(self, data: np.ndarray, dtype) -> np.ndarray:
        """Apply automatic histogram stretching for better contrast.
        
        Args:
            data: Input data (float64)
            dtype: Target data type
            
        Returns:
            Stretched data in target dtype
        """
        # Calculate percentiles for stretching (ignore extreme outliers)
        low_percentile = np.percentile(data, 0.1)
        high_percentile = np.percentile(data, 99.9)
        
        # Avoid division by zero
        if high_percentile - low_percentile < 1e-10:
            return data.astype(dtype)
        
        # Stretch to full range
        stretched = (data - low_percentile) / (high_percentile - low_percentile)
        stretched = np.clip(stretched, 0, 1)
        
        # Scale to target range
        max_val = np.iinfo(dtype).max if np.issubdtype(dtype, np.integer) else 1.0
        stretched = stretched * max_val
        
        return stretched.astype(dtype)
    
    def stack_frames(self, ser_file, method: str = 'average', 
                    progress_callback: Optional[Callable[[int, int], None]] = None,
                    auto_stretch: bool = True,
                    align_frames: bool = True,
                    quality_threshold: float = 0.0) -> np.ndarray:
        """Stack all frames from video file with optional alignment.
        
        Args:
            ser_file: VideoFile instance (SER or AVI)
            method: Stacking method ('average', 'median', 'sum')
            progress_callback: Optional callback(current, total) for progress
            auto_stretch: Apply automatic histogram stretching (default: True)
            align_frames: Align frames before stacking (default: True for AVI)
            quality_threshold: Minimum quality score (0.0 = use all frames)
            
        Returns:
            Stacked image as numpy array (height, width, 3)
        """
        header = ser_file.get_header()
        frame_count = header.frame_count
        
        # Auto-enable lucky imaging for AVI/MP4 files
        if hasattr(ser_file, 'file_type') and ser_file.file_type in ['AVI', 'MP4']:
            # Use lucky imaging (select best 10% of frames, align, and stack)
            self.logger.info(f"{ser_file.file_type} file detected - using lucky imaging")
            return LuckyImaging.align_and_stack_lucky(
                ser_file,
                percentage=10.0,  # Keep best 10% of frames
                method=method,
                progress_callback=progress_callback
            )
        
        self.logger.info(f"Stacking {frame_count} frames using {method} method (align={align_frames})")
        
        # Get first frame as reference
        first_frame = ser_file.parser.get_frame(0)
        
        # For alignment, we need to process frames first
        if align_frames:
            self.logger.info("Aligning frames for sharp stacking...")
            aligned_frames = []
            quality_scores = []
            
            # Use first frame as reference
            reference = first_frame.copy()
            aligned_frames.append(reference)
            quality_scores.append(self.aligner.calculate_quality_score(reference))
            
            if progress_callback:
                progress_callback(1, frame_count)
            
            # Align all other frames
            for i in range(1, frame_count):
                frame = ser_file.parser.get_frame(i)
                
                # Try ECC alignment first (handles rotation + translation)
                aligned = self.aligner.align_frame_ecc(reference, frame)
                
                # If ECC fails, try ORB feature-based alignment
                if aligned is None:
                    aligned = self.aligner.align_frame_orb(reference, frame)
                
                if aligned is not None:
                    # Calculate quality score
                    quality = self.aligner.calculate_quality_score(aligned)
                    
                    # Only use frame if quality is above threshold
                    if quality >= quality_threshold:
                        aligned_frames.append(aligned)
                        quality_scores.append(quality)
                    else:
                        self.logger.debug(f"Frame {i} rejected (quality {quality:.2f} < {quality_threshold:.2f})")
                else:
                    self.logger.debug(f"Frame {i} alignment failed")
                
                if progress_callback:
                    progress_callback(i + 1, frame_count)
            
            used_frames = len(aligned_frames)
            self.logger.info(f"Successfully aligned {used_frames}/{frame_count} frames")
            
            # Stack aligned frames
            if method == 'median':
                frames_array = np.array([f.astype(np.float32) for f in aligned_frames])
                stacked_float = np.median(frames_array, axis=0)
                stacked = self._auto_stretch(stacked_float, first_frame.dtype) if auto_stretch else stacked_float.astype(first_frame.dtype)
                
            elif method == 'sum':
                accumulator = np.zeros_like(first_frame, dtype=np.float64)
                for frame in aligned_frames:
                    accumulator += frame.astype(np.float64)
                stacked = self._auto_stretch(accumulator, first_frame.dtype)
                
            else:  # average
                accumulator = np.zeros_like(first_frame, dtype=np.float64)
                for frame in aligned_frames:
                    accumulator += frame.astype(np.float64)
                averaged = accumulator / used_frames
                stacked = self._auto_stretch(averaged, first_frame.dtype) if auto_stretch else averaged.astype(first_frame.dtype)
            
            return stacked
        
        # Original stacking without alignment (for SER files)
        if method == 'median':
            # For median, we need to store all frames
            # Check if we have enough memory
            # Use float32 instead of float64 to save memory (half the size)
            frame_size_mb = (first_frame.nbytes * 4) / (1024 * 1024)  # float32 is 4 bytes per pixel
            total_size_mb = frame_size_mb * frame_count
            
            # Warn if file is very large (>8GB)
            if total_size_mb > 8192:
                self.logger.warning(
                    f"Median stacking requires approximately {total_size_mb:.1f} MB of memory. "
                    f"Consider using 'average' method for large files."
                )
            
            self.logger.info(f"Loading {frame_count} frames for median (total: {total_size_mb:.1f} MB)")
            
            frames = []
            for i in range(frame_count):
                frame = ser_file.parser.get_frame(i)
                # Use float32 instead of float64 to save memory
                frames.append(frame.astype(np.float32))
                
                if progress_callback:
                    progress_callback(i + 1, frame_count)
            
            # Stack and compute median
            stacked_float = np.median(frames, axis=0)
            
            # Apply auto-stretch if enabled, otherwise just convert
            if auto_stretch:
                stacked = self._auto_stretch(stacked_float, first_frame.dtype)
            else:
                stacked = stacked_float.astype(first_frame.dtype)
            
        elif method == 'sum':
            # Sum all frames
            accumulator = np.zeros_like(first_frame, dtype=np.float64)
            
            for i in range(frame_count):
                frame = ser_file.parser.get_frame(i)
                accumulator += frame.astype(np.float64)
                
                if progress_callback:
                    progress_callback(i + 1, frame_count)
            
            # For sum, always apply auto-stretch to prevent overflow
            # This is the key fix for the "all white" issue
            stacked = self._auto_stretch(accumulator, first_frame.dtype)
            
        else:  # average (default)
            # Average all frames
            accumulator = np.zeros_like(first_frame, dtype=np.float64)
            
            for i in range(frame_count):
                frame = ser_file.parser.get_frame(i)
                accumulator += frame.astype(np.float64)
                
                if progress_callback:
                    progress_callback(i + 1, frame_count)
            
            # Average
            averaged = accumulator / frame_count
            
            # Apply auto-stretch if enabled, otherwise just convert
            if auto_stretch:
                stacked = self._auto_stretch(averaged, first_frame.dtype)
            else:
                stacked = averaged.astype(first_frame.dtype)
        
        return stacked
