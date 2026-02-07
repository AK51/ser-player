"""Lucky imaging - select and stack only the sharpest frames."""

import numpy as np
import cv2
from typing import List, Tuple, Optional
import logging


class LuckyImaging:
    """Lucky imaging implementation for astronomical videos."""
    
    def __init__(self):
        """Initialize lucky imaging."""
        self.logger = logging.getLogger(__name__)
    
    @staticmethod
    def calculate_sharpness(frame: np.ndarray) -> float:
        """Calculate frame sharpness score.
        
        Args:
            frame: Input frame
            
        Returns:
            Sharpness score (higher is better)
        """
        # Convert to grayscale if needed
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        else:
            gray = frame
        
        # Laplacian variance (sharpness metric)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        score = laplacian.var()
        
        return score
    
    @staticmethod
    def select_best_frames(video_file, percentage: float = 10.0,
                          progress_callback=None) -> List[Tuple[int, float, np.ndarray]]:
        """Select the sharpest frames from video.
        
        Args:
            video_file: VideoFile instance
            percentage: Percentage of frames to keep (default: 10%)
            progress_callback: Progress callback function
            
        Returns:
            List of (frame_index, quality_score, frame_data)
        """
        logger = logging.getLogger(__name__)
        frame_count = video_file.header.frame_count
        
        # Calculate how many frames to keep
        keep_count = max(1, int(frame_count * percentage / 100.0))
        logger.info(f"Analyzing {frame_count} frames, will keep best {keep_count} ({percentage}%)")
        
        # Analyze all frames
        frame_scores = []
        for i in range(frame_count):
            frame = video_file.parser.get_frame(i)
            score = LuckyImaging.calculate_sharpness(frame)
            frame_scores.append((i, score))
            
            if progress_callback:
                progress_callback(i + 1, frame_count)
        
        # Sort by quality score (descending)
        frame_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Keep only the best frames
        best_frames = frame_scores[:keep_count]
        
        # Sort by frame index for sequential processing
        best_frames.sort(key=lambda x: x[0])
        
        logger.info(f"Selected {len(best_frames)} best frames")
        logger.info(f"Quality range: {best_frames[-1][1]:.2f} to {best_frames[0][1]:.2f}")
        
        # Load the actual frame data
        result = []
        for idx, score in best_frames:
            frame = video_file.parser.get_frame(idx)
            result.append((idx, score, frame))
        
        return result
    
    @staticmethod
    def align_and_stack_lucky(video_file, percentage: float = 10.0,
                             method: str = 'average',
                             progress_callback=None) -> np.ndarray:
        """Lucky imaging: select best frames, align, and stack.
        
        Args:
            video_file: VideoFile instance
            percentage: Percentage of frames to keep
            method: Stacking method ('average', 'median', 'sum')
            progress_callback: Progress callback
            
        Returns:
            Stacked image
        """
        logger = logging.getLogger(__name__)
        
        # Step 1: Select best frames
        logger.info("Step 1: Selecting sharpest frames...")
        best_frames = LuckyImaging.select_best_frames(
            video_file, percentage, progress_callback
        )
        
        if len(best_frames) == 0:
            raise Exception("No frames selected")
        
        # Step 2: Use first (sharpest) frame as reference
        reference_idx, reference_score, reference_frame = best_frames[0]
        logger.info(f"Using frame {reference_idx} as reference (quality: {reference_score:.2f})")
        
        # Step 3: Align all frames to reference
        logger.info("Step 2: Aligning frames...")
        aligned_frames = [reference_frame]
        
        for i, (idx, score, frame) in enumerate(best_frames[1:], 1):
            # Align using feature-based method
            aligned = LuckyImaging.align_frame_features(reference_frame, frame)
            
            if aligned is not None:
                aligned_frames.append(aligned)
                logger.debug(f"Aligned frame {idx} ({i}/{len(best_frames)-1})")
            else:
                logger.debug(f"Failed to align frame {idx}, skipping")
            
            if progress_callback:
                progress_callback(i, len(best_frames))
        
        logger.info(f"Successfully aligned {len(aligned_frames)}/{len(best_frames)} frames")
        
        # Step 4: Stack aligned frames
        logger.info("Step 3: Stacking aligned frames...")
        if method == 'median':
            stacked = np.median(aligned_frames, axis=0).astype(np.uint8)
        elif method == 'sum':
            stacked = np.sum(aligned_frames, axis=0)
            stacked = np.clip(stacked * 255.0 / stacked.max(), 0, 255).astype(np.uint8)
        else:  # average
            stacked = np.mean(aligned_frames, axis=0).astype(np.uint8)
        
        return stacked
    
    @staticmethod
    def align_frame_features(reference: np.ndarray, frame: np.ndarray) -> Optional[np.ndarray]:
        """Align frame using ORB features.
        
        Args:
            reference: Reference frame
            frame: Frame to align
            
        Returns:
            Aligned frame or None if failed
        """
        try:
            # Convert to grayscale
            if len(reference.shape) == 3:
                ref_gray = cv2.cvtColor(reference, cv2.COLOR_RGB2GRAY)
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            else:
                ref_gray = reference
                frame_gray = frame
            
            # Detect ORB features
            orb = cv2.ORB_create(nfeatures=5000, scaleFactor=1.2, nlevels=8)
            kp1, des1 = orb.detectAndCompute(ref_gray, None)
            kp2, des2 = orb.detectAndCompute(frame_gray, None)
            
            if des1 is None or des2 is None or len(kp1) < 10 or len(kp2) < 10:
                return None
            
            # Match features
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
            matches = bf.knnMatch(des1, des2, k=2)
            
            # Apply ratio test
            good_matches = []
            for match_pair in matches:
                if len(match_pair) == 2:
                    m, n = match_pair
                    if m.distance < 0.7 * n.distance:
                        good_matches.append(m)
            
            if len(good_matches) < 10:
                return None
            
            # Extract matched points
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            
            # Find transformation (affine - handles rotation + translation)
            M, inliers = cv2.estimateAffinePartial2D(
                dst_pts, src_pts, method=cv2.RANSAC,
                ransacReprojThreshold=3.0, maxIters=2000, confidence=0.99
            )
            
            if M is None:
                return None
            
            # Apply transformation
            h, w = reference.shape[:2]
            aligned = cv2.warpAffine(frame, M, (w, h),
                                    flags=cv2.INTER_LINEAR,
                                    borderMode=cv2.BORDER_CONSTANT,
                                    borderValue=0)
            
            return aligned
            
        except Exception:
            return None
