# SER File Viewer (AVI also) and stacking
<img width="1278" height="601" alt="ser_main" src="https://github.com/user-attachments/assets/d6d7090f-8a32-4f36-a24c-b4c118415ad9" />

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)

A high-tech Python-based viewer for astronomical SER (Simple Event Recorder) image sequences with a modern dark-themed GUI.

![SER File Viewer](https://img.shields.io/badge/Status-Production-brightgreen.svg)

## Features

- **Parse SER Files**: Read and parse SER file headers and frame data
- **Multiple Color Formats**: Support for MONO, RGB, BGR, and Bayer CFA patterns
- **CYYM Auto-Detection**: Automatically detects correct color pattern from camera model
- **8-bit and 16-bit Support**: Handle both 8-bit and 16-bit pixel depths
- **Frame Navigation**: Navigate through frames with intuitive controls
- **Playback**: Play sequences at configurable frame rates
- **Frame Stacking**: Combine multiple frames into high-quality images
  - **Average**: Reduces noise by averaging all frames
  - **Median**: Removes outliers and artifacts  
  - **Sum**: Increases brightness for faint objects
  - Export stacked images to PNG format
- **Metadata Display**: View comprehensive file and observation metadata
- **Timestamp Support**: Display frame timestamps when available
- **High-Tech GUI**: Modern dark-themed interface with PyQt5
- **Efficient Memory Management**: LRU frame caching for smooth performance

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ser-file-viewer.git
cd ser-file-viewer
```

2. Install dependencies:

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

**Or manually:**
```bash
pip install -r requirements.txt
```

3. Run the application:

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

**Or manually:**
```bash
python main.py
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Dependencies

- **numpy**: Array operations for image data
- **Pillow**: Image processing
- **PyQt5**: Modern GUI framework
- **opencv-python** (optional): Advanced Bayer debayering
- **pytest**: Testing framework
- **hypothesis**: Property-based testing

## Usage

### Launch the Application

```bash
python main.py
```

### Open a SER File

1. Click **File → Open** or press `Ctrl+O`
2. Select a `.ser` file
3. The first frame will be displayed automatically

### Navigation Controls

- **First Frame**: Jump to the first frame
- **Previous Frame**: Go to previous frame (or press `Left Arrow`)
- **Play/Pause**: Start/stop automatic playback (or press `Space`)
- **Next Frame**: Go to next frame (or press `Right Arrow`)
- **Last Frame**: Jump to the last frame
- **Slider**: Drag to jump to any frame

### Keyboard Shortcuts

- `Ctrl+O`: Open file
- `Ctrl+S`: Stack frames to PNG
- `Space`: Play/Pause
- `Left Arrow`: Previous frame
- `Right Arrow`: Next frame
- `Home`: First frame
- `End`: Last frame
- `Ctrl+Q`: Quit application

### Frame Stacking

Stack all frames into a single high-quality image:

1. Open a SER file
2. Click **File → Stack Frames to PNG** or press `Ctrl+S`
3. Select stacking method:
   - **Average**: Best for general noise reduction
   - **Median**: Best for removing artifacts and outliers
   - **Sum**: Best for increasing brightness of faint objects
4. Choose save location for PNG output
5. Wait for stacking to complete (progress bar shows status)

The stacked image will be saved as a PNG file with full RGB color.

### Command Line

You can also open a file directly from the command line:

```bash
python main.py path/to/your/file.ser
```

## SER Format Support

### Supported Color Formats

- **MONO** (ColorID 0): Monochrome
- **BAYER_RGGB** (ColorID 1): Bayer pattern RGGB
- **BAYER_GRBG** (ColorID 2): Bayer pattern GRBG
- **BAYER_GBRG** (ColorID 3): Bayer pattern GBRG
- **BAYER_BGGR** (ColorID 4): Bayer pattern BGGR
- **BAYER_CYYM** (ColorID 8): Bayer pattern CYYM
- **BAYER_YCMY** (ColorID 9): Bayer pattern YCMY
- **BAYER_YMCY** (ColorID 16): Bayer pattern YMCY
- **BAYER_MYYC** (ColorID 17): Bayer pattern MYYC
- **RGB** (ColorID 100): RGB color
- **BGR** (ColorID 101): BGR color

### Supported Pixel Depths

- 8-bit per pixel
- 16-bit per pixel (automatically normalized to 8-bit for display)

### Endianness

The viewer correctly handles the endianness quirk in SER implementations where the LittleEndian field is inverted from the specification (0=little-endian, 1=big-endian).

### Timestamps

Optional timestamp trailers are automatically detected and displayed when available.

## Architecture

The application follows a Model-View-Controller (MVC) architecture:

- **Model Layer**: SER Parser, Image Processor, Frame Cache
- **Controller Layer**: Navigation Controller, Playback Controller, File Manager
- **View Layer**: PyQt5 GUI with high-tech dark theme

## Known Limitations

- Advanced Bayer patterns (CYYM, YCMY, YMCY, MYYC) require OpenCV for proper debayering; otherwise displayed as monochrome
- Very large files (>2GB) may have performance limitations depending on available RAM
- Playback frame rate may vary based on system performance and file size

## Troubleshooting

### PyQt5 Not Found

If you get an error about PyQt5 not being installed:

```bash
pip install PyQt5
```

### OpenCV Not Found

OpenCV is optional but recommended for better Bayer debayering:

```bash
pip install opencv-python
```

### File Won't Open

- Ensure the file has a `.ser` extension
- Verify the file is a valid SER file (starts with "LUCAM-RECORDER")
- Check the log file `ser_viewer.log` for detailed error messages

## Development

### Project Structure

```
ser-file-viewer/
├── src/
│   ├── __init__.py
│   ├── ser_parser.py          # SER file parser
│   ├── image_processor.py     # Image processing
│   ├── frame_cache.py         # Frame caching
│   ├── file_manager.py        # High-level file interface
│   ├── navigation_controller.py
│   ├── playback_controller.py
│   └── gui/
│       ├── __init__.py
│       └── main_window.py     # Main GUI window
├── tests/                     # Test suite
├── main.py                    # Application entry point
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

### Running Tests

```bash
pytest tests/
```

### Running with Coverage

```bash
pytest --cov=src tests/
```

## References

- [SER Format Specification](https://free-astro.org/index.php?title=SER)
- [Siril SER Documentation](https://siril.readthedocs.io/en/latest/file-formats/SER.html)
- [SER Player (C implementation)](https://github.com/cgarry/ser-player)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Author

Created by Andy Kong for the astronomical imaging community.

## Acknowledgments

- [SER Format Specification](https://free-astro.org/index.php?title=SER)
- [Siril](https://siril.readthedocs.io/) for SER format documentation
- The astronomical imaging community for feedback and testing

