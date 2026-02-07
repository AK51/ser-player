"""SER file parser for reading and extracting frames from SER files."""

import struct
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
import numpy as np


class SERError(Exception):
    """Base exception for SER file errors."""
    pass


class SERFormatError(SERError):
    """Invalid SER file format."""
    pass


class SERIOError(SERError):
    """I/O error reading SER file."""
    pass


class SERIndexError(SERError):
    """Frame or timestamp index out of bounds."""
    pass


@dataclass
class SERHeader:
    """Represents parsed SER file header."""
    file_id: str
    lu_id: int
    color_id: int
    little_endian: int  # 0=little, 1=big (inverted from spec)
    image_width: int
    image_height: int
    pixel_depth: int
    frame_count: int
    observer: str
    instrument: str
    telescope: str
    datetime_utc: int


class SERParser:
    """Parses SER files and extracts frames."""
    
    HEADER_SIZE = 178
    FILE_ID = b"LUCAM-RECORDER"
    VALID_COLOR_IDS = {0, 1, 2, 3, 4, 8, 9, 16, 17, 100, 101}
    VALID_PIXEL_DEPTHS = {8, 16}
    
    def __init__(self, file_path: str):
        """Initialize parser with file path.
        
        Args:
            file_path: Path to SER file
            
        Raises:
            SERIOError: If file cannot be opened
        """
        self.file_path = file_path
        self.header: Optional[SERHeader] = None
        self._file_handle = None
        self._frame_size = 0
        self._has_timestamps = False
        
        try:
            if not os.path.exists(file_path):
                raise SERIOError(f"File not found: {file_path}")
            if not os.path.isfile(file_path):
                raise SERIOError(f"Not a file: {file_path}")
            
            self._file_handle = open(file_path, 'rb')
        except IOError as e:
            raise SERIOError(f"Cannot open file: {e}")
    
    def parse_header(self) -> SERHeader:
        """Read and parse 178-byte header.
        
        Returns:
            SERHeader object with parsed metadata
            
        Raises:
            SERFormatError: If file is not valid SER format
            SERIOError: If file cannot be read
        """
        try:
            self._file_handle.seek(0)
            header_bytes = self._file_handle.read(self.HEADER_SIZE)
            
            if len(header_bytes) < self.HEADER_SIZE:
                raise SERFormatError(
                    f"File too small for header: {len(header_bytes)} bytes, expected {self.HEADER_SIZE}"
                )
            
            # Parse FileID (14 bytes)
            file_id = header_bytes[0:14].rstrip(b'\x00')
            if file_id != self.FILE_ID:
                raise SERFormatError(
                    f"Invalid FileID: {file_id}, expected {self.FILE_ID}"
                )
            
            # Parse LittleEndian field first to determine byte order
            little_endian = struct.unpack('<I', header_bytes[22:26])[0]
            endian_char = '<' if little_endian == 0 else '>'
            
            # Parse integer fields with correct endianness
            lu_id = struct.unpack(f'{endian_char}I', header_bytes[14:18])[0]
            color_id = struct.unpack(f'{endian_char}I', header_bytes[18:22])[0]
            image_width = struct.unpack(f'{endian_char}I', header_bytes[26:30])[0]
            image_height = struct.unpack(f'{endian_char}I', header_bytes[30:34])[0]
            pixel_depth = struct.unpack(f'{endian_char}I', header_bytes[34:38])[0]
            frame_count = struct.unpack(f'{endian_char}I', header_bytes[38:42])[0]
            datetime_utc = struct.unpack(f'{endian_char}Q', header_bytes[162:170])[0]
            
            # Validate ColorID
            if color_id not in self.VALID_COLOR_IDS:
                raise SERFormatError(
                    f"Unsupported ColorID: {color_id}, valid values: {self.VALID_COLOR_IDS}"
                )
            
            # Validate PixelDepth
            if pixel_depth not in self.VALID_PIXEL_DEPTHS:
                raise SERFormatError(
                    f"Unsupported pixel depth: {pixel_depth}, valid values: {self.VALID_PIXEL_DEPTHS}"
                )
            
            # Validate FrameCount
            if frame_count == 0:
                raise SERFormatError("Invalid FrameCount: 0")
            
            # Parse string fields (null-terminated)
            observer = header_bytes[42:82].rstrip(b'\x00').decode('utf-8', errors='ignore')
            instrument = header_bytes[82:122].rstrip(b'\x00').decode('utf-8', errors='ignore')
            telescope = header_bytes[122:162].rstrip(b'\x00').decode('utf-8', errors='ignore')
            
            self.header = SERHeader(
                file_id=file_id.decode('utf-8'),
                lu_id=lu_id,
                color_id=color_id,
                little_endian=little_endian,
                image_width=image_width,
                image_height=image_height,
                pixel_depth=pixel_depth,
                frame_count=frame_count,
                observer=observer,
                instrument=instrument,
                telescope=telescope,
                datetime_utc=datetime_utc
            )
            
            # Calculate frame size
            self._frame_size = self.calculate_frame_size()
            
            # Check for timestamp trailer
            file_size = os.path.getsize(self.file_path)
            expected_size_with_timestamps = (
                self.HEADER_SIZE + 
                frame_count * self._frame_size + 
                frame_count * 8
            )
            self._has_timestamps = (file_size == expected_size_with_timestamps)
            
            return self.header
            
        except struct.error as e:
            raise SERFormatError(f"Error parsing header: {e}")
        except IOError as e:
            raise SERIOError(f"Error reading header: {e}")
    
    def calculate_frame_size(self) -> int:
        """Calculate size of one frame in bytes.
        
        Returns:
            Frame size in bytes
        """
        if not self.header:
            raise SERError("Header not parsed yet")
        
        # Determine number of planes based on ColorID
        planes = 3 if self.header.color_id in [100, 101] else 1
        bytes_per_pixel = self.header.pixel_depth // 8
        
        return (self.header.image_width * self.header.image_height * 
                bytes_per_pixel * planes)
    
    def get_frame(self, frame_index: int) -> np.ndarray:
        """Extract raw frame data at given index.
        
        Args:
            frame_index: Zero-based frame index
            
        Returns:
            NumPy array with shape (height, width) for mono
            or (height, width, 3) for RGB/BGR
            
        Raises:
            SERIndexError: If frame_index >= frame_count
            SERIOError: If frame data cannot be read
        """
        if not self.header:
            raise SERError("Header not parsed yet")
        
        if frame_index < 0 or frame_index >= self.header.frame_count:
            raise SERIndexError(
                f"Frame index {frame_index} out of bounds [0, {self.header.frame_count})"
            )
        
        try:
            # Calculate byte offset
            offset = self.HEADER_SIZE + frame_index * self._frame_size
            self._file_handle.seek(offset)
            
            # Read frame data
            frame_bytes = self._file_handle.read(self._frame_size)
            if len(frame_bytes) < self._frame_size:
                raise SERIOError(
                    f"Incomplete frame data: {len(frame_bytes)} bytes, expected {self._frame_size}"
                )
            
            # Determine dtype based on pixel depth and endianness
            endian_char = '<' if self.header.little_endian == 0 else '>'
            if self.header.pixel_depth == 8:
                dtype = np.uint8
            else:  # 16-bit
                dtype = np.dtype(f'{endian_char}u2')
            
            # Convert to numpy array
            frame_data = np.frombuffer(frame_bytes, dtype=dtype)
            
            # Reshape based on color format
            if self.header.color_id in [100, 101]:  # RGB/BGR
                frame_data = frame_data.reshape(
                    (self.header.image_height, self.header.image_width, 3)
                )
            else:  # Mono/Bayer
                frame_data = frame_data.reshape(
                    (self.header.image_height, self.header.image_width)
                )
            
            return frame_data
            
        except IOError as e:
            raise SERIOError(f"Error reading frame {frame_index}: {e}")
    
    def has_timestamps(self) -> bool:
        """Check if file contains timestamp trailer.
        
        Returns:
            True if timestamps are available
        """
        return self._has_timestamps
    
    def get_timestamp(self, frame_index: int) -> Optional[datetime]:
        """Get timestamp for frame if trailer exists.
        
        Args:
            frame_index: Zero-based frame index
            
        Returns:
            datetime object or None if no timestamps
            
        Raises:
            SERIndexError: If frame_index >= frame_count
        """
        if not self.header:
            raise SERError("Header not parsed yet")
        
        if not self._has_timestamps:
            return None
        
        if frame_index < 0 or frame_index >= self.header.frame_count:
            raise SERIndexError(
                f"Frame index {frame_index} out of bounds [0, {self.header.frame_count})"
            )
        
        try:
            # Calculate timestamp offset
            timestamp_offset = (
                self.HEADER_SIZE + 
                self.header.frame_count * self._frame_size + 
                frame_index * 8
            )
            
            self._file_handle.seek(timestamp_offset)
            timestamp_bytes = self._file_handle.read(8)
            
            # Parse timestamp with correct endianness
            endian_char = '<' if self.header.little_endian == 0 else '>'
            raw_timestamp = struct.unpack(f'{endian_char}Q', timestamp_bytes)[0]
            
            # Convert Windows FILETIME to Python datetime
            # FILETIME: 100-nanosecond intervals since Jan 1, 1601
            EPOCH_DIFF = 116444736000000000  # 100-ns intervals from 1601 to 1970
            unix_timestamp = (raw_timestamp - EPOCH_DIFF) / 10000000.0
            
            return datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
            
        except (IOError, struct.error) as e:
            raise SERIOError(f"Error reading timestamp {frame_index}: {e}")
    
    def close(self):
        """Close file handle."""
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
