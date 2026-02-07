"""Frame alignment for image stacking with rotation support."""

import numpy as np
import cv2
from typing import Tuple, Optional


class FrameAligner:
    """Aligns frames for sharp stacking with rotation support."""
    
    @staticmethod
    def align_frame_ecc(reference: np.ndarray, frame: np.ndarray,
                       max_iterations: int = 5000,
                       termination_eps: float = 1e-6) -> Optional[np.ndarray]:
        """Align frame using ECC (Enhanced Correlation Coefficient) - handles rotation.
        
        This method can handle translation, rotation, and scaling.
        Perfect for non-equatorial mount tracking.
        
        Args:
            reference: Reference image
            frame: Frame to align
            max_iterations: Maximum iterations for ECC
            termination_eps: Termination threshold
            
        Returns:
            Aligned frame or None if alignment fails
        """
        try:
            # Convert to grayscale if needed
            if len(reference.shape) == 3:
                ref_gray = cv2.cvtColor(reference, cv2.COLOR_RGB2GRAY)
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            else:
                ref_gray = reference
                frame_gray = frame
            
            # Convert to float32
            ref_gray = np.float32(ref_gray)
            frame_gray = np.float32(frame_gray)
            
            # Define motion model - EUCLIDEAN handles rotation + translation
            warp_mode = cv2.MOTION_EUCLIDEAN
            
            # Initialize warp matrix (identity)
            warp_matrix = np.eye(2, 3, dtype=np.float32)
            
            # Define termination criteria
            criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
                       max_iterations, termination_eps)
            
            # Run ECC algorithm
            try:
                (cc, warp_matrix) = cv2.findTransformECC(
                    ref_gray, frame_gray, warp_matrix, warp_mode, criteria,
                    inputMask=None, gaussFiltSize=5
                )
            except cv2.error:
                # ECC failed, return None
                return None
            
            # Apply transformation to original frame
            h, w = reference.shape[:2]
            aligned = cv2.warpAffine(frame, warp_matrix, (w, h),
                                    flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP,
                                    borderMode=cv2.BORDER_CONSTANT,
                                    borderValue=0)
            
            return aligned
            
        except Exception as e:
            return None
    
    @staticmethod
    def align_frame_orb(reference: np.ndarray, frame: np.ndarray,
                       max_shift: int = 200) -> Optional[np.ndarray]:
        """Align frame using ORB features - handles rotation and scaling.
        
        Args:
            reference: Reference image
            frame: Frame to align
            max_shift: Maximum allowed shift in pixels
            
        Returns:
            Aligned frame or None if alignment fails
        """
        try:
            # Convert to grayscale if needed
            if len(reference.shape) == 3:
                ref_gray = cv2.cvtColor(reference, cv2.COLOR_RGB2GRAY)
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            else:
                ref_gray = reference
                frame_gray = frame
            
            # Detect ORB features
            orb = cv2.ORB_create(nfeatures=10000, scaleFactor=1.2, nlevels=8)
            kp1, des1 = orb.detectAndCompute(ref_gray, None)
            kp2, des2 = orb.detectAndCompute(frame_gray, None)
            
            if des1 is None or des2 is None or len(kp1) < 10 or len(kp2) < 10:
                return None
            
            # Match features using BFMatcher
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
            matches = bf.knnMatch(des1, des2, k=2)
            
            # Apply ratio test (Lowe's ratio test)
            good_matches = []
            for match_pair in matches:
                if len(match_pair) == 2:
                    m, n = match_pair
                    if m.distance < 0.75 * n.distance:
                        good_matches.append(m)
            
            if len(good_matches) < 10:
                return None
            
            # Extract matched keypoints
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            
            # Find affine transformation (handles rotation + translation + scaling)
            M, inliers = cv2.estimateAffinePartial2D(dst_pts, src_pts, method=cv2.RANSAC,
                                                     ransacReprojThreshold=5.0, maxIters=5000,
                                                     confidence=0.99)
            
            if M is None:
                return None
            
            # Check if transformation is reasonable
            # Extract translation
            shift_x = M[0, 2]
            shift_y = M[1, 2]
            
            if abs(shift_x) > max_shift or abs(shift_y) > max_shift:
                return None
            
            # Apply transformation
            h, w = reference.shape[:2]
            aligned = cv2.warpAffine(frame, M, (w, h),
                                    flags=cv2.INTER_LINEAR,
                                    borderMode=cv2.BORDER_CONSTANT,
                                    borderValue=0)
            
            return aligned
            
        except Exception as e:
            return None
    
    @staticmethod
    def align_frame_astropy(reference: np.ndarray, frame: np.ndarray) -> Optional[np.ndarray]:
        """Align frame to reference using astropy image registration.
        
        Note: This only handles translation, not rotation.
        Use align_frame_ecc or align_frame_orb for rotation.
        
        Args:
            reference: Reference image
            frame: Frame to align
            
        Returns:
            Aligned frame or None if alignment fails
        """
        try:
            from scipy.ndimage import shift as scipy_shift
            
            # Convert to grayscale if needed
            if len(reference.shape) == 3:
                ref_gray = cv2.cvtColor(reference, cv2.COLOR_RGB2GRAY)
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            else:
                ref_gray = reference
                frame_gray = frame
            
            # Use cross-correlation to find shift
            from skimage.registration import phase_cross_correlation
            
            # Calculate shift using phase cross-correlation
            shift_result = phase_cross_correlation(ref_gray, frame_gray, upsample_factor=10)
            shift_y, shift_x = shift_result[0]
            
            # Apply shift to each channel
            if len(frame.shape) == 3:
                aligned = np.zeros_like(frame)
                for i in range(frame.shape[2]):
                    aligned[:, :, i] = scipy_shift(frame[:, :, i], (shift_y, shift_x), order=3)
            else:
                aligned = scipy_shift(frame, (shift_y, shift_x), order=3)
            
            return aligned
            
        except Exception as e:
            return None
    
    @staticmethod
    def align_frame_simple(reference: np.ndarray, frame: np.ndarray,
                          max_shift: int = 100) -> Optional[np.ndarray]:
        """Align frame using simple phase correlation (translation only).
        
        Args:
            reference: Reference image
            frame: Frame to align
            max_shift: Maximum allowed shift in pixels
            
        Returns:
            Aligned frame or None if alignment fails
        """
        try:
            # Convert to grayscale if needed
            if len(reference.shape) == 3:
                ref_gray = cv2.cvtColor(reference, cv2.COLOR_RGB2GRAY)
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            else:
                ref_gray = reference
                frame_gray = frame
            
            # Use phase correlation to find shift
            shift, response = cv2.phaseCorrelate(
                np.float32(ref_gray), 
                np.float32(frame_gray)
            )
            
            # Check if shift is reasonable
            if abs(shift[0]) > max_shift or abs(shift[1]) > max_shift:
                return None
            
            # Create translation matrix
            M = np.float32([[1, 0, shift[0]], [0, 1, shift[1]]])
            
            # Apply translation
            h, w = reference.shape[:2]
            aligned = cv2.warpAffine(frame, M, (w, h))
            
            return aligned
            
        except Exception:
            return None
    
    @staticmethod
    def calculate_quality_score(image: np.ndarray) -> float:
        """Calculate image quality score (sharpness).
        
        Args:
            image: Input image
            
        Returns:
            Quality score (higher is better)
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Use Laplacian variance as sharpness metric
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        score = laplacian.var()
        
        return score
