"""Image processor for converting SER frame data to displayable format."""

import numpy as np
from typing import Optional

# Try to import OpenCV for advanced debayering
try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False


class ImageProcessor:
    """Converts raw SER frame data to display format."""
    
    # Color ID mappings
    COLOR_MONO = 0
    COLOR_BAYER_RGGB = 1
    COLOR_BAYER_GRBG = 2
    COLOR_BAYER_GBRG = 3
    COLOR_BAYER_BGGR = 4
    COLOR_BAYER_CYYM = 8
    COLOR_BAYER_YCMY = 9
    COLOR_BAYER_YMCY = 16
    COLOR_BAYER_MYYC = 17
    COLOR_RGB = 100
    COLOR_BGR = 101
    
    # CYYM pattern preference (can be changed by user)
    CYYM_PATTERN = "CYYM"  # Default pattern
    
    # Camera-specific CYYM pattern mappings
    # Based on known camera models and their sensor arrangements
    CAMERA_CYYM_PATTERNS = {
        'ZWO ASI183MC': 'YCMY',  # ZWO ASI183MC uses YCMY arrangement
        'ZWO ASI183MM': 'YCMY',
        'ZWO ASI294MC': 'YCMY',
        'ZWO ASI533MC': 'YCMY',
        'ZWO ASI678MC': 'YCMY',
        # Add more camera models as discovered
    }
    
    @staticmethod
    def detect_cyym_pattern(instrument: str) -> str:
        """Detect CYYM pattern based on camera/instrument name.
        
        Args:
            instrument: Instrument/camera name from SER header
            
        Returns:
            Detected pattern name (CYYM, YCMY, YMCY, MYYC) or default "CYYM"
        """
        if not instrument:
            return "CYYM"
        
        # Check for exact match first
        if instrument in ImageProcessor.CAMERA_CYYM_PATTERNS:
            return ImageProcessor.CAMERA_CYYM_PATTERNS[instrument]
        
        # Check for partial match (case-insensitive)
        instrument_upper = instrument.upper()
        for camera_name, pattern in ImageProcessor.CAMERA_CYYM_PATTERNS.items():
            if camera_name.upper() in instrument_upper:
                return pattern
        
        # Default to CYYM if no match found
        return "CYYM"
    
    # Bayer pattern mappings for OpenCV
    BAYER_PATTERNS = {
        COLOR_BAYER_RGGB: cv2.COLOR_BAYER_BG2RGB if HAS_OPENCV else None,
        COLOR_BAYER_GRBG: cv2.COLOR_BAYER_GB2RGB if HAS_OPENCV else None,
        COLOR_BAYER_GBRG: cv2.COLOR_BAYER_GR2RGB if HAS_OPENCV else None,
        COLOR_BAYER_BGGR: cv2.COLOR_BAYER_RG2RGB if HAS_OPENCV else None,
    }
    
    @staticmethod
    def normalize_16bit(data: np.ndarray) -> np.ndarray:
        """Normalize 16-bit data to 8-bit range.
        
        Args:
            data: 16-bit image data
            
        Returns:
            8-bit normalized data
        """
        # Linear scaling from [0, 65535] to [0, 255]
        return (data / 256).astype(np.uint8)
    
    @staticmethod
    def bgr_to_rgb(data: np.ndarray) -> np.ndarray:
        """Convert BGR to RGB channel order.
        
        Args:
            data: BGR image data
            
        Returns:
            RGB image data
        """
        return data[:, :, ::-1].copy()
    
    @staticmethod
    def mono_to_rgb(data: np.ndarray) -> np.ndarray:
        """Convert mono to RGB by replicating channels.
        
        Args:
            data: Mono image data (height, width)
            
        Returns:
            RGB image data (height, width, 3)
        """
        return np.stack([data, data, data], axis=2)
    
    @staticmethod
    def debayer_simple(data: np.ndarray, pattern: str) -> np.ndarray:
        """Apply simple bilinear debayering to Bayer CFA data.
        
        Args:
            data: Raw Bayer pattern data
            pattern: Bayer pattern name (RGGB, GRBG, GBRG, BGGR)
            
        Returns:
            RGB image data
        """
        height, width = data.shape
        rgb = np.zeros((height, width, 3), dtype=data.dtype)
        
        # Simple nearest-neighbor debayering (fast but lower quality)
        # This is a fallback when OpenCV is not available
        
        if pattern == 'RGGB':
            # R at (0,0), G at (0,1) and (1,0), B at (1,1)
            rgb[0::2, 0::2, 0] = data[0::2, 0::2]  # R
            rgb[0::2, 1::2, 1] = data[0::2, 1::2]  # G
            rgb[1::2, 0::2, 1] = data[1::2, 0::2]  # G
            rgb[1::2, 1::2, 2] = data[1::2, 1::2]  # B
            
            # Interpolate missing values (simple averaging)
            rgb[0::2, 1::2, 0] = (rgb[0::2, 0::2, 0] + np.roll(rgb[0::2, 0::2, 0], -1, axis=1)) // 2
            rgb[1::2, :, 0] = (rgb[0::2, :, 0] + np.roll(rgb[0::2, :, 0], -1, axis=0)) // 2
            rgb[1::2, 0::2, 2] = (rgb[1::2, 1::2, 2] + np.roll(rgb[1::2, 1::2, 2], 1, axis=1)) // 2
            rgb[0::2, :, 2] = (rgb[1::2, :, 2] + np.roll(rgb[1::2, :, 2], 1, axis=0)) // 2
            
        elif pattern == 'GRBG':
            rgb[0::2, 1::2, 0] = data[0::2, 1::2]  # R
            rgb[0::2, 0::2, 1] = data[0::2, 0::2]  # G
            rgb[1::2, 1::2, 1] = data[1::2, 1::2]  # G
            rgb[1::2, 0::2, 2] = data[1::2, 0::2]  # B
            
        elif pattern == 'GBRG':
            rgb[0::2, 0::2, 1] = data[0::2, 0::2]  # G
            rgb[0::2, 1::2, 2] = data[0::2, 1::2]  # B
            rgb[1::2, 0::2, 0] = data[1::2, 0::2]  # R
            rgb[1::2, 1::2, 1] = data[1::2, 1::2]  # G
            
        elif pattern == 'BGGR':
            rgb[0::2, 0::2, 2] = data[0::2, 0::2]  # B
            rgb[0::2, 1::2, 1] = data[0::2, 1::2]  # G
            rgb[1::2, 0::2, 1] = data[1::2, 0::2]  # G
            rgb[1::2, 1::2, 0] = data[1::2, 1::2]  # R
        
        return rgb
    
    @staticmethod
    def debayer_cyym(data: np.ndarray, pattern: str = "CYYM") -> np.ndarray:
        """Apply debayering to CYYM Bayer pattern.
        
        CYYM patterns (also called CYGM):
        - CYYM: Cy Y / Y Mg
        - YCMY: Y Cy / Mg Y
        - YMCY: Y Mg / Cy Y
        - MYYC: Mg Y / Y Cy
        
        Where:
        - Cy (Cyan) = G + B
        - Y (Yellow) = R + G  
        - Mg (Magenta) = R + B
        
        Args:
            data: Raw CYYM Bayer pattern data
            pattern: Pattern arrangement (CYYM, YCMY, YMCY, MYYC)
            
        Returns:
            RGB image data
        """
        height, width = data.shape
        rgb = np.zeros((height, width, 3), dtype=np.float32)
        
        # Extract the 2x2 pattern based on arrangement
        if pattern == "CYYM":
            # Cy Y / Y Mg
            cy = data[0::2, 0::2].astype(np.float32)
            y1 = data[0::2, 1::2].astype(np.float32)
            y2 = data[1::2, 0::2].astype(np.float32)
            mg = data[1::2, 1::2].astype(np.float32)
        elif pattern == "YCMY":
            # Y Cy / Mg Y
            y1 = data[0::2, 0::2].astype(np.float32)
            cy = data[0::2, 1::2].astype(np.float32)
            mg = data[1::2, 0::2].astype(np.float32)
            y2 = data[1::2, 1::2].astype(np.float32)
        elif pattern == "YMCY":
            # Y Mg / Cy Y
            y1 = data[0::2, 0::2].astype(np.float32)
            mg = data[0::2, 1::2].astype(np.float32)
            cy = data[1::2, 0::2].astype(np.float32)
            y2 = data[1::2, 1::2].astype(np.float32)
        elif pattern == "MYYC":
            # Mg Y / Y Cy
            mg = data[0::2, 0::2].astype(np.float32)
            y1 = data[0::2, 1::2].astype(np.float32)
            y2 = data[1::2, 0::2].astype(np.float32)
            cy = data[1::2, 1::2].astype(np.float32)
        else:
            # Default to CYYM
            cy = data[0::2, 0::2].astype(np.float32)
            y1 = data[0::2, 1::2].astype(np.float32)
            y2 = data[1::2, 0::2].astype(np.float32)
            mg = data[1::2, 1::2].astype(np.float32)
        
        # Average the two yellow values
        y_avg = (y1 + y2) / 2
        
        # Solve for RGB from CYYM:
        # Cy = G + B
        # Y = R + G
        # Mg = R + B
        # 
        # From these equations:
        # R = (Y + Mg - Cy) / 2
        # G = (Y + Cy - Mg) / 2
        # B = (Cy + Mg - Y) / 2
        
        r = (y_avg + mg - cy) / 2
        g = (y_avg + cy - mg) / 2
        b = (cy + mg - y_avg) / 2
        
        # Clip to valid range
        r = np.clip(r, 0, 255)
        g = np.clip(g, 0, 255)
        b = np.clip(b, 0, 255)
        
        # Upsample to full resolution using bilinear interpolation
        from scipy.ndimage import zoom
        r_full = zoom(r, 2, order=1)[:height, :width]
        g_full = zoom(g, 2, order=1)[:height, :width]
        b_full = zoom(b, 2, order=1)[:height, :width]
        
        rgb[:, :, 0] = r_full
        rgb[:, :, 1] = g_full
        rgb[:, :, 2] = b_full
        
        return rgb.astype(np.uint8)
    
    @staticmethod
    def debayer(data: np.ndarray, color_id: int) -> np.ndarray:
        """Apply debayering to Bayer CFA data.
        
        Args:
            data: Raw Bayer pattern data
            color_id: SER ColorID value
            
        Returns:
            RGB image data
        """
        # Handle CYYM pattern specially with user-selected pattern
        if color_id == ImageProcessor.COLOR_BAYER_CYYM:
            return ImageProcessor.debayer_cyym(data, ImageProcessor.CYYM_PATTERN)
        
        # Use OpenCV if available for better quality
        if HAS_OPENCV and color_id in ImageProcessor.BAYER_PATTERNS:
            pattern = ImageProcessor.BAYER_PATTERNS[color_id]
            if pattern is not None:
                return cv2.cvtColor(data, pattern)
        
        # Fallback to simple debayering
        pattern_names = {
            ImageProcessor.COLOR_BAYER_RGGB: 'RGGB',
            ImageProcessor.COLOR_BAYER_GRBG: 'GRBG',
            ImageProcessor.COLOR_BAYER_GBRG: 'GBRG',
            ImageProcessor.COLOR_BAYER_BGGR: 'BGGR',
        }
        
        if color_id in pattern_names:
            return ImageProcessor.debayer_simple(data, pattern_names[color_id])
        
        # For advanced patterns without implementation, treat as mono
        return ImageProcessor.mono_to_rgb(data)
    
    @staticmethod
    def process_frame(raw_data: np.ndarray, color_id: int, pixel_depth: int) -> np.ndarray:
        """Convert raw frame to 8-bit RGB for display.
        
        Args:
            raw_data: Raw pixel data from parser
            color_id: SER ColorID value
            pixel_depth: Bits per pixel (8 or 16)
            
        Returns:
            NumPy array with shape (height, width, 3) and dtype uint8
        """
        # Normalize 16-bit to 8-bit if necessary
        if pixel_depth == 16:
            data = ImageProcessor.normalize_16bit(raw_data)
        else:
            data = raw_data
        
        # Handle different color formats
        if color_id == ImageProcessor.COLOR_MONO:
            # Mono: convert to RGB
            return ImageProcessor.mono_to_rgb(data)
        
        elif color_id in [ImageProcessor.COLOR_BAYER_RGGB, 
                         ImageProcessor.COLOR_BAYER_GRBG,
                         ImageProcessor.COLOR_BAYER_GBRG, 
                         ImageProcessor.COLOR_BAYER_BGGR,
                         ImageProcessor.COLOR_BAYER_CYYM,
                         ImageProcessor.COLOR_BAYER_YCMY,
                         ImageProcessor.COLOR_BAYER_YMCY,
                         ImageProcessor.COLOR_BAYER_MYYC]:
            # Bayer: debayer to RGB
            return ImageProcessor.debayer(data, color_id)
        
        elif color_id == ImageProcessor.COLOR_RGB:
            # RGB: passthrough
            return data
        
        elif color_id == ImageProcessor.COLOR_BGR:
            # BGR: convert to RGB
            return ImageProcessor.bgr_to_rgb(data)
        
        else:
            # Unknown format: treat as mono
            if len(data.shape) == 2:
                return ImageProcessor.mono_to_rgb(data)
            return data
