# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-07

### Added
- Initial release of SER File Viewer
- Support for SER file format parsing and display
- Multiple color format support (MONO, RGB, BGR, Bayer patterns)
- 8-bit and 16-bit pixel depth support
- Frame navigation with intuitive controls
- Playback functionality with configurable frame rates
- Frame stacking capabilities (Average, Median, Sum)
- CYYM auto-detection from camera model
- Metadata display panel
- Timestamp support for frames
- High-tech dark-themed GUI with PyQt5
- LRU frame caching for performance
- Keyboard shortcuts for navigation
- Export stacked images to PNG
- Comprehensive test suite (unit, property-based, integration)
- User manual and documentation

### Features
- **Frame Navigation**: Navigate through frames with toolbar, slider, and keyboard
- **Playback**: Play sequences at adjustable speeds
- **Stacking**: Combine frames using Average, Median, or Sum methods
- **Color Support**: Full support for all SER color formats including advanced Bayer patterns
- **Performance**: Efficient memory management with frame caching
- **GUI**: Modern dark-themed interface with cyan/green accents

### Technical
- Python 3.8+ support
- PyQt5 GUI framework
- NumPy for array operations
- Pillow for image processing
- OpenCV for advanced Bayer debayering (optional)
- Property-based testing with Hypothesis
- 90%+ test coverage

## [Unreleased]

### Planned
- AVI file format support
- MP4 file format support
- FITS file format support
- Batch processing capabilities
- Advanced image enhancement options
- Frame alignment algorithms
- Lucky imaging integration
- Export to additional formats

---

For more details, see the [README](README.md) and [USER_MANUAL](USER_MANUAL.md).
