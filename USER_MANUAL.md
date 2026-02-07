# SER File Viewer - User Manual

## Version 1.0
## Created by Andy Kong

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [User Interface](#user-interface)
5. [Features](#features)
6. [Keyboard Shortcuts](#keyboard-shortcuts)
7. [Frame Stacking](#frame-stacking)
8. [Troubleshooting](#troubleshooting)
9. [Technical Specifications](#technical-specifications)

---

## Introduction

SER File Viewer is a professional application for viewing and processing astronomical SER (Super Enhanced Recording) image sequences. It features a modern high-tech interface with advanced capabilities including frame navigation, playback, and frame stacking.

### What is SER Format?

SER is a video format commonly used in astronomy for capturing planetary and lunar images. It stores sequences of uncompressed frames with metadata, making it ideal for lucky imaging and image stacking techniques.

### Key Features

- View SER files with all color formats (Mono, RGB, BGR, Bayer)
- Navigate through frames with intuitive controls
- Play sequences with adjustable speed
- Stack multiple frames to create high-quality images
- Display comprehensive metadata
- High-tech dark-themed interface

---

## Installation

### System Requirements

- **Operating System**: Windows, Linux, or macOS
- **Python**: Version 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 100MB for application + space for SER files

### Installation Steps

1. **Install Python** (if not already installed)
   - Download from [python.org](https://www.python.org)
   - Ensure Python 3.8 or higher is installed

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Installation**
   ```bash
   python main.py
   ```

### Dependencies

The application requires the following Python packages:
- **PyQt5**: GUI framework
- **NumPy**: Array operations
- **Pillow**: Image processing
- **OpenCV** (optional): Advanced Bayer debayering

---

## Getting Started

### Launching the Application

1. Open a terminal or command prompt
2. Navigate to the application directory
3. Run: `python main.py`
4. The application window will open maximized

### Opening Your First SER File

**Method 1: Auto-Open (Default)**
- The application automatically opens the first .ser file from `E:\test\Kiro_ser\ser`
- To change this path, edit `main.py`

**Method 2: Manual Open**
1. Click **File → Open** (or press `Ctrl+O`)
2. Browse to your SER file location
3. Select a .ser file
4. Click **Open**

### First Look

Once a file is loaded, you'll see:
- **Center**: The current frame displayed
- **Right Panel**: Metadata information
- **Top Toolbar**: Navigation and playback controls
- **Bottom Status Bar**: Frame number and timestamp

---

## User Interface

### Main Window Layout

```
┌─────────────────────────────────────────────────────────┐
│ File  About                                             │
├─────────────────────────────────────────────────────────┤
│ ⏮ First │ ⏪ Prev │ ▶ Play │ Next ⏩ │ Last ⏭ │ [Slider]│
├──────────────────────────────┬──────────────────────────┤
│                              │  Metadata Panel          │
│                              │  ─────────────────       │
│      Frame Display           │  File: example.ser       │
│      (Image Canvas)          │  Dimensions: 1920×1080   │
│                              │  Frames: 1000            │
│                              │  Color: RGB              │
│                              │  Depth: 16-bit           │
│                              │  Observer: ...           │
│                              │  Instrument: ...         │
│                              │  Telescope: ...          │
│                              │  Timestamps: Yes         │
│                              │  File Size: 125.5 MB     │
├──────────────────────────────┴──────────────────────────┤
│ Frame 1 / 1000 | 2024-01-29 12:34:56.789 UTC           │
└─────────────────────────────────────────────────────────┘
```

### Color Scheme

The application uses a high-tech dark theme:
- **Background**: Deep black (#0a0a0a, #1a1a1a)
- **Primary Accent**: Cyan (#00ffff)
- **Secondary Accent**: Green (#00ff00)
- **Text**: Cyan and green on dark backgrounds
- **Borders**: Glowing cyan borders with hover effects

### Controls

#### Navigation Buttons
- **⏮ First**: Jump to first frame
- **⏪ Prev**: Go to previous frame
- **▶ Play / ⏸ Pause**: Start/stop playback
- **Next ⏩**: Go to next frame
- **Last ⏭**: Jump to last frame

#### Frame Slider
- Drag to quickly navigate to any frame
- Shows current position
- Updates in real-time during playback

#### Metadata Panel
Displays comprehensive file information:
- File name and path
- Image dimensions (width × height)
- Total frame count
- Color format (with human-readable name)
- Pixel depth (8-bit or 16-bit)
- Observer name (if available)
- Instrument name (if available)
- Telescope name (if available)
- Timestamp availability
- File size in MB

---

## Features

### 1. Frame Navigation

Navigate through your SER sequence frame by frame.

**Using Buttons:**
- Click **Next** or **Prev** buttons
- Click **First** or **Last** for endpoints

**Using Slider:**
- Drag the slider to any position
- Click on the slider track to jump

**Using Keyboard:**
- Press `Right Arrow` for next frame
- Press `Left Arrow` for previous frame
- Press `Home` for first frame
- Press `End` for last frame

### 2. Playback

Play your SER sequence as a video.

**Starting Playback:**
- Click the **▶ Play** button
- Press `Space` bar

**Stopping Playback:**
- Click the **⏸ Pause** button
- Press `Space` bar again

**During Playback:**
- Frames advance automatically
- Frame counter updates in real-time
- Slider position updates
- Frames are buffered for smooth playback

### 3. Frame Stacking

Combine multiple frames into a single high-quality image.

**Why Stack Frames?**
- **Reduce Noise**: Averaging reduces random noise
- **Remove Artifacts**: Median removes outliers and hot pixels
- **Increase Brightness**: Sum increases signal for faint objects

**How to Stack:**

1. **Open a SER file**
2. **Start Stacking**:
   - Click **File → Stack Frames to PNG**
   - Or press `Ctrl+S`
3. **Choose Method**:
   - **Average**: Best for general noise reduction
   - **Median**: Best for removing artifacts
   - **Sum**: Best for faint objects
4. **Select Save Location**:
   - Choose where to save the PNG file
   - Enter a filename
   - Click **Save**
5. **Wait for Completion**:
   - Progress bar shows status
   - Can cancel at any time
   - Success message when done

**Stacking Methods Explained:**

**Average Method:**
- Calculates mean pixel value across all frames
- Reduces random noise by √N (N = frame count)
- Best for: General purpose, most situations
- Output: Balanced image with reduced noise

**Median Method:**
- Takes median pixel value across all frames
- Removes outliers (hot pixels, cosmic rays, satellites)
- Best for: Removing artifacts and outliers
- Output: Clean image without artifacts

**Sum Method:**
- Adds all pixel values together
- Increases overall brightness
- Best for: Faint objects, deep sky imaging
- Output: Brighter image (may need adjustment)

### 4. Metadata Display

View comprehensive information about your SER file.

**File Information:**
- Filename and full path
- File size in megabytes
- Image dimensions (width × height)
- Total number of frames

**Format Information:**
- Color format (MONO, RGB, BGR, Bayer patterns)
- Pixel depth (8-bit or 16-bit)
- Timestamp availability

**Observation Information:**
- Observer name
- Instrument/camera name
- Telescope name

**Frame Information:**
- Current frame number
- Timestamp (if available)
- UTC time display

### 5. Image Processing

Automatic processing for optimal display.

**Color Format Handling:**
- **Mono**: Converted to RGB for display
- **RGB**: Displayed directly
- **BGR**: Converted to RGB
- **Bayer**: Debayered to RGB (uses OpenCV if available)

**Bit Depth Handling:**
- **8-bit**: Displayed directly
- **16-bit**: Normalized to 8-bit for display
- Linear scaling preserves relative brightness

**Performance Optimization:**
- Frame caching (LRU cache)
- Lazy loading (frames loaded on demand)
- Prefetching during playback
- Efficient memory management

---

## Keyboard Shortcuts

### File Operations
- `Ctrl+O`: Open file
- `Ctrl+S`: Stack frames to PNG
- `Ctrl+Q`: Quit application

### Navigation
- `Right Arrow`: Next frame
- `Left Arrow`: Previous frame
- `Home`: First frame
- `End`: Last frame

### Playback
- `Space`: Play/Pause toggle

### Tips
- Hold arrow keys for rapid navigation
- Use Home/End for quick jumps
- Space bar is fastest for play/pause

---

## Frame Stacking

### Detailed Guide

#### When to Use Each Method

**Average Stacking:**
- **Use for**: General planetary imaging, lunar imaging
- **Advantages**: Reduces noise, balanced output
- **Best with**: 50-500 frames
- **Example**: Jupiter, Saturn, Moon

**Median Stacking:**
- **Use for**: Removing satellites, airplanes, hot pixels
- **Advantages**: Robust to outliers, clean output
- **Best with**: 100+ frames (more frames = better outlier rejection)
- **Example**: Planetary imaging with artifacts

**Sum Stacking:**
- **Use for**: Faint objects, deep sky imaging
- **Advantages**: Increases brightness, preserves detail
- **Best with**: Many frames (100+)
- **Example**: Faint nebulae, galaxies
- **Note**: Output may be very bright, adjust in post-processing

#### Stacking Workflow

1. **Capture**: Record SER sequence with your camera
2. **Load**: Open SER file in viewer
3. **Review**: Check frames for quality
4. **Stack**: Choose method and stack
5. **Save**: Export as PNG
6. **Process**: Further processing in image editor (optional)

#### Tips for Best Results

- **More frames = better results** (up to a point)
- **Use median for planetary** (removes atmospheric turbulence artifacts)
- **Use average for general purpose** (good balance)
- **Use sum for faint objects** (increases signal)
- **Check progress bar** (can take time for many frames)
- **Save to SSD** (faster than HDD)

#### Technical Details

**Processing Time:**
- Depends on: Frame count, image size, method
- Average: Fast (single pass)
- Median: Slower (requires sorting)
- Sum: Fast (single pass)
- Example: 1000 frames @ 1920×1080 ≈ 10-30 seconds

**Memory Usage:**
- Average: Low (single accumulator)
- Median: High (stores all frames)
- Sum: Low (single accumulator)

**Output Quality:**
- Format: PNG (lossless)
- Color: RGB (8-bit per channel)
- Size: Same as input frame dimensions

---

## Troubleshooting

### Common Issues

#### Application Won't Start

**Problem**: Error when running `python main.py`

**Solutions:**
1. Check Python version: `python --version` (need 3.8+)
2. Install dependencies: `pip install -r requirements.txt`
3. Check for error messages in terminal
4. Verify PyQt5 is installed: `pip show PyQt5`

#### File Won't Open

**Problem**: Error when opening SER file

**Solutions:**
1. Verify file is valid SER format
2. Check file isn't corrupted
3. Ensure file isn't locked by another program
4. Check file permissions
5. Try a different SER file

#### Frames Display Incorrectly

**Problem**: Colors wrong or image distorted

**Solutions:**
1. Check color format in metadata panel
2. For Bayer files, install OpenCV: `pip install opencv-python`
3. Verify file isn't corrupted
4. Check pixel depth matches file format

#### Playback is Choppy

**Problem**: Frames skip or stutter during playback

**Solutions:**
1. Increase cache size (edit `file_manager.py`)
2. Close other applications
3. Use SSD instead of HDD
4. Reduce frame rate (if option available)

#### Stacking Takes Too Long

**Problem**: Stacking progress is very slow

**Solutions:**
1. Use Average or Sum instead of Median
2. Reduce number of frames (if possible)
3. Close other applications
4. Check disk space
5. Save to faster drive (SSD)

#### Out of Memory Error

**Problem**: Application crashes with memory error

**Solutions:**
1. Close other applications
2. Use Average or Sum instead of Median
3. Reduce cache size
4. Process fewer frames at once
5. Upgrade RAM (if possible)

### Error Messages

#### "Invalid SER file format"
- File is not a valid SER file
- File may be corrupted
- Try opening in another SER viewer to verify

#### "Unsupported color format"
- Color ID not recognized
- File may use non-standard format
- Check file with hex editor

#### "Frame index out of bounds"
- Trying to access non-existent frame
- File may be truncated
- Check frame count in metadata

#### "Cannot write to file"
- No write permission
- Disk full
- File path invalid
- Choose different save location

### Getting Help

If you encounter issues not covered here:

1. Check the log file: `ser_viewer.log`
2. Note the exact error message
3. Check Python version and dependencies
4. Try with a different SER file
5. Verify file integrity

---

## Technical Specifications

### Supported Formats

**SER Format Version:** 3

**Color Formats:**
- MONO (ColorID 0): Monochrome
- BAYER_RGGB (ColorID 1): Bayer RGGB pattern
- BAYER_GRBG (ColorID 2): Bayer GRBG pattern
- BAYER_GBRG (ColorID 3): Bayer GBRG pattern
- BAYER_BGGR (ColorID 4): Bayer BGGR pattern
- BAYER_CYYM (ColorID 8): Bayer CYYM pattern
- BAYER_YCMY (ColorID 9): Bayer YCMY pattern
- BAYER_YMCY (ColorID 16): Bayer YMCY pattern
- BAYER_MYYC (ColorID 17): Bayer MYYC pattern
- RGB (ColorID 100): RGB color
- BGR (ColorID 101): BGR color

**Pixel Depths:**
- 8-bit (1 byte per pixel per plane)
- 16-bit (2 bytes per pixel per plane)

**Timestamps:**
- Optional 64-bit Windows FILETIME format
- Converted to UTC datetime for display

### Performance Characteristics

**Frame Loading:**
- Lazy loading (on-demand)
- LRU cache (default 10 frames)
- Prefetching during playback

**Memory Usage:**
- Base: ~50MB
- Per cached frame: ~6MB (1920×1080 RGB)
- Stacking (Average/Sum): +1 frame
- Stacking (Median): +N frames (all frames)

**Processing Speed:**
- Frame display: <10ms
- Navigation: Instant (if cached)
- Stacking: 10-30 seconds (1000 frames)

### File Size Limits

**Theoretical:**
- Maximum frames: 2^32 (4.3 billion)
- Maximum dimensions: 2^32 × 2^32 pixels
- Maximum file size: Limited by filesystem

**Practical:**
- Tested up to: 10,000 frames
- Tested dimensions: 4096×4096 pixels
- Tested file size: 10GB
- Limited by: Available RAM and disk space

### System Requirements

**Minimum:**
- CPU: Dual-core 2GHz
- RAM: 4GB
- Disk: 100MB + SER files
- Display: 1024×768

**Recommended:**
- CPU: Quad-core 3GHz+
- RAM: 8GB+
- Disk: SSD with 10GB+ free
- Display: 1920×1080+

---

## Appendix

### Keyboard Shortcut Reference

| Action | Shortcut |
|--------|----------|
| Open File | Ctrl+O |
| Stack Frames | Ctrl+S |
| Quit | Ctrl+Q |
| Next Frame | Right Arrow |
| Previous Frame | Left Arrow |
| First Frame | Home |
| Last Frame | End |
| Play/Pause | Space |

### Color Format Reference

| ColorID | Name | Description |
|---------|------|-------------|
| 0 | MONO | Monochrome/Grayscale |
| 1 | BAYER_RGGB | Bayer pattern RGGB |
| 2 | BAYER_GRBG | Bayer pattern GRBG |
| 3 | BAYER_GBRG | Bayer pattern GBRG |
| 4 | BAYER_BGGR | Bayer pattern BGGR |
| 8 | BAYER_CYYM | Bayer pattern CYYM |
| 9 | BAYER_YCMY | Bayer pattern YCMY |
| 16 | BAYER_YMCY | Bayer pattern YMCY |
| 17 | BAYER_MYYC | Bayer pattern MYYC |
| 100 | RGB | RGB color |
| 101 | BGR | BGR color |

### File Structure Reference

**SER File Structure:**
```
[Header: 178 bytes]
[Frame 0 data]
[Frame 1 data]
...
[Frame N-1 data]
[Timestamps: 8 bytes × N] (optional)
```

**Header Fields:**
- FileID: "LUCAM-RECORDER" (14 bytes)
- LuID: Camera ID (4 bytes)
- ColorID: Color format (4 bytes)
- LittleEndian: Byte order (4 bytes)
- ImageWidth: Width in pixels (4 bytes)
- ImageHeight: Height in pixels (4 bytes)
- PixelDepthPerPlane: Bits per pixel (4 bytes)
- FrameCount: Number of frames (4 bytes)
- Observer: Observer name (40 bytes)
- Instrument: Instrument name (40 bytes)
- Telescope: Telescope name (40 bytes)
- DateTime: Capture time (8 bytes)
- DateTime_UTC: UTC time (8 bytes)

---

## About

**SER File Viewer**
Version 1.0

Created by Andy Kong

A professional application for viewing and processing astronomical SER image sequences.

Built with:
- Python 3.10
- PyQt5 (GUI framework)
- NumPy (array operations)
- Pillow (image processing)
- OpenCV (optional, Bayer debayering)

© 2026 Andy Kong. All rights reserved.

---

**End of User Manual**
