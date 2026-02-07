"""Main application window with high-tech dark theme."""

import os
import logging
from typing import Optional

try:
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QSlider, QPushButton, QFileDialog, QMessageBox,
        QToolBar, QStatusBar, QDockWidget, QAction, QSizePolicy,
        QProgressDialog, QInputDialog, QDialog
    )
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal
    from PyQt5.QtGui import QPixmap, QImage, QIcon, QKeySequence
except ImportError:
    print("PyQt5 not installed. Please install: pip install PyQt5")
    raise

from PIL import Image
from ..file_manager import SERFile, SERError
from ..navigation_controller import NavigationController
from ..playback_controller import PlaybackController
from ..stacker import FrameStacker
from ..image_processor import ImageProcessor
from ..image_enhancer import ImageEnhancer
from .enhancement_dialog import EnhancementDialog


class ImageCanvas(QLabel):
    """Widget for displaying frames."""
    
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 2px solid #00ffff;
                border-radius: 5px;
            }
        """)
        self.setMinimumSize(640, 480)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setText("No file loaded")
        self.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 2px solid #00ffff;
                border-radius: 5px;
                color: #00ffff;
                font-size: 28px;
            }
        """)
    
    def set_image(self, pil_image):
        """Display PIL Image.
        
        Args:
            pil_image: PIL Image object
        """
        # Convert PIL Image to QPixmap
        img_data = pil_image.tobytes("raw", "RGB")
        qimage = QImage(img_data, pil_image.width, pil_image.height, 
                       pil_image.width * 3, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        
        # Scale to fit while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(
            self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.setPixmap(scaled_pixmap)
    
    def clear(self):
        """Clear canvas."""
        self.clear()
        self.setText("No file loaded")


class MetadataPanel(QWidget):
    """Metadata display panel with high-tech styling."""
    
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.layout)
        
        self.labels = {}
        self._create_labels()
        
        self.setStyleSheet("""
            QWidget {
                background-color: #0d0d0d;
                color: #00ff00;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 18px;
            }
            QLabel {
                padding: 5px;
                border-bottom: 1px solid #003300;
            }
        """)
    
    def _create_labels(self):
        """Create metadata labels."""
        fields = [
            ('file', 'File:'),
            ('dimensions', 'Dimensions:'),
            ('frames', 'Frames:'),
            ('color', 'Color Format:'),
            ('depth', 'Pixel Depth:'),
            ('observer', 'Observer:'),
            ('instrument', 'Instrument:'),
            ('telescope', 'Telescope:'),
            ('timestamps', 'Timestamps:'),
            ('filesize', 'File Size:'),
        ]
        
        for key, label_text in fields:
            label = QLabel(f"{label_text} -")
            label.setWordWrap(True)
            self.labels[key] = label
            self.layout.addWidget(label)
        
        self.layout.addStretch()
    
    def update_metadata(self, ser_file: SERFile):
        """Update metadata display.
        
        Args:
            ser_file: SERFile instance
        """
        header = ser_file.get_header()
        
        # Color ID names
        color_names = {
            0: 'MONO', 1: 'BAYER_RGGB', 2: 'BAYER_GRBG', 3: 'BAYER_GBRG',
            4: 'BAYER_BGGR', 8: 'BAYER_CYYM', 9: 'BAYER_YCMY',
            16: 'BAYER_YMCY', 17: 'BAYER_MYYC', 100: 'RGB', 101: 'BGR'
        }
        
        self.labels['file'].setText(f"File: {os.path.basename(ser_file.file_path)}")
        self.labels['dimensions'].setText(
            f"Dimensions: {header.image_width} × {header.image_height}"
        )
        self.labels['frames'].setText(f"Frames: {header.frame_count}")
        self.labels['color'].setText(
            f"Color Format: {header.color_id} ({color_names.get(header.color_id, 'Unknown')})"
        )
        self.labels['depth'].setText(f"Pixel Depth: {header.pixel_depth}-bit")
        
        if header.observer:
            self.labels['observer'].setText(f"Observer: {header.observer}")
        else:
            self.labels['observer'].setText("Observer: -")
        
        if header.instrument:
            self.labels['instrument'].setText(f"Instrument: {header.instrument}")
        else:
            self.labels['instrument'].setText("Instrument: -")
        
        if header.telescope:
            self.labels['telescope'].setText(f"Telescope: {header.telescope}")
        else:
            self.labels['telescope'].setText("Telescope: -")
        
        has_ts = "Yes" if ser_file.parser.has_timestamps() else "No"
        self.labels['timestamps'].setText(f"Timestamps: {has_ts}")
        
        file_size = ser_file.get_file_size()
        size_mb = file_size / (1024 * 1024)
        self.labels['filesize'].setText(f"File Size: {size_mb:.2f} MB")


class MainWindow(QMainWindow):
    """Main application window with high-tech dark theme."""
    
    def __init__(self, auto_open_path: Optional[str] = None):
        super().__init__()
        self.ser_file: Optional[SERFile] = None
        self.nav_controller: Optional[NavigationController] = None
        self.playback_controller: Optional[PlaybackController] = None
        self.auto_open_path = auto_open_path
        
        self.setWindowTitle("Video File Viewer")
        self.setGeometry(100, 100, 1200, 800)
        
        self._setup_ui()
        self._apply_theme()
        self._setup_logging()
        
        # Maximize window on startup
        self.showMaximized()
        
        # Auto-open file if path provided
        if self.auto_open_path:
            # Use QTimer to open file after window is shown
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(100, self._auto_open_file)
    
    def _auto_open_file(self):
        """Auto-open file from specified path."""
        if self.auto_open_path and os.path.exists(self.auto_open_path):
            if os.path.isdir(self.auto_open_path):
                # If it's a directory, find the first video file
                import glob
                video_files = glob.glob(os.path.join(self.auto_open_path, "*.ser"))
                video_files.extend(glob.glob(os.path.join(self.auto_open_path, "*.avi")))
                video_files.extend(glob.glob(os.path.join(self.auto_open_path, "*.mp4")))
                if video_files:
                    self._load_file(video_files[0])
                else:
                    self.logger.warning(f"No video files found in {self.auto_open_path}")
            elif self.auto_open_path.endswith(('.ser', '.avi', '.mp4')):
                # If it's a file, open it directly
                self._load_file(self.auto_open_path)
        else:
            if self.auto_open_path:
                self.logger.warning(f"Auto-open path not found: {self.auto_open_path}")
    
    def _setup_ui(self):
        """Set up user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Image canvas
        self.canvas = ImageCanvas()
        main_layout.addWidget(self.canvas, stretch=3)
        
        # Metadata panel (right side)
        self.metadata_panel = MetadataPanel()
        metadata_dock = QDockWidget("Metadata", self)
        metadata_dock.setWidget(self.metadata_panel)
        metadata_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.addDockWidget(Qt.RightDockWidgetArea, metadata_dock)
        
        # Menu bar
        self._create_menu_bar()
        
        # Toolbar
        self._create_toolbar()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("No file loaded")
        self.status_bar.addWidget(self.status_label)
    
    def _create_menu_bar(self):
        """Create menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        self.stack_action = QAction("&Stack Frames to PNG", self)
        self.stack_action.setShortcut("Ctrl+S")
        self.stack_action.triggered.connect(self._stack_and_save)
        self.stack_action.setEnabled(False)
        file_menu.addAction(self.stack_action)
        
        enhance_image_action = QAction("&Enhance Image...", self)
        enhance_image_action.setShortcut("Ctrl+E")
        enhance_image_action.triggered.connect(self._open_and_enhance_image)
        file_menu.addAction(enhance_image_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings menu
        settings_menu = menubar.addMenu("&Settings")
        
        cyym_pattern_action = QAction("CYYM &Pattern...", self)
        cyym_pattern_action.triggered.connect(self._select_cyym_pattern)
        settings_menu.addAction(cyym_pattern_action)
        
        # About menu
        about_menu = menubar.addMenu("&About")
        
        about_action = QAction("&About SER File Viewer", self)
        about_action.triggered.connect(self._show_about_dialog)
        about_menu.addAction(about_action)
    
    def _show_about_dialog(self):
        """Show about dialog."""
        about_text = """
        <h2 style='color: #00ffff; font-size: 24px;'>Video File Viewer</h2>
        <p style='color: #00ff00; font-size: 18px;'><b>Version:</b> 1.0</p>
        <p style='color: #00ff00; font-size: 18px;'><b>Created by:</b> Andy Kong</p>
        <br>
        <p style='color: #00ffff; font-size: 18px;'>A high-tech Python viewer for astronomical video files.</p>
        <p style='color: #00ffff; font-size: 18px;'>Supports SER, AVI, and MP4 formats.</p>
        <br>
        <p style='color: #888888; font-size: 18px;'>Built with PyQt5, NumPy, OpenCV, and Pillow</p>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About Video File Viewer")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(about_text)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #1a1a1a;
                font-size: 18px;
            }
            QMessageBox QLabel {
                color: #00ffff;
                background-color: #1a1a1a;
                font-size: 18px;
            }
            QPushButton {
                background-color: #2a2a2a;
                color: #00ffff;
                border: 2px solid #00ffff;
                border-radius: 5px;
                padding: 14px 24px;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #003333;
                border-color: #00ff00;
            }
        """)
        msg_box.exec_()
    
    def _select_cyym_pattern(self):
        """Allow user to select CYYM color filter pattern."""
        patterns = ['CYYM', 'YCMY', 'YMCY', 'MYYC']
        pattern_descriptions = [
            'CYYM - Cy Y / Y Mg',
            'YCMY - Y Cy / Mg Y',
            'YMCY - Y Mg / Cy Y',
            'MYYC - Mg Y / Y Cy'
        ]
        
        # Find current pattern index
        current_pattern = ImageProcessor.CYYM_PATTERN
        try:
            current_index = patterns.index(current_pattern)
        except ValueError:
            current_index = 0
        
        # Build dialog text with auto-detection info
        dialog_text = "Choose the color filter arrangement for CYYM Bayer pattern:\n\n"
        
        if self.ser_file and self.ser_file.header.instrument:
            detected = ImageProcessor.detect_cyym_pattern(self.ser_file.header.instrument)
            dialog_text += f"Camera: {self.ser_file.header.instrument}\n"
            dialog_text += f"Auto-detected pattern: {detected}\n\n"
        
        dialog_text += "If your image appears too green, red, or blue, try a different pattern.\n"
        dialog_text += "The correct pattern depends on your camera sensor."
        
        pattern, ok = QInputDialog.getItem(
            self,
            "Select CYYM Pattern",
            dialog_text,
            pattern_descriptions,
            current_index,
            False
        )
        
        if ok and pattern:
            # Extract pattern name from description
            new_pattern = pattern.split(' - ')[0]
            
            # Update the pattern
            ImageProcessor.CYYM_PATTERN = new_pattern
            
            # Clear cache to force re-processing with new pattern
            if self.ser_file:
                self.ser_file.cache.clear()
                
                # Refresh current frame
                self._display_current_frame()
                
                self.logger.info(f"Changed CYYM pattern to: {new_pattern}")
                
                QMessageBox.information(
                    self,
                    "Pattern Changed",
                    f"CYYM pattern changed to: {new_pattern}\n\n"
                    f"The display has been refreshed with the new pattern."
                )
    
    def _prompt_cyym_pattern_on_load(self):
        """Prompt user to select CYYM pattern when loading a CYYM file."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("CYYM Color Filter Detected")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(
            "<b style='font-size: 18px;'>This file uses CYYM color filter pattern.</b><br><br>"
            "<span style='font-size: 18px;'>CYYM has 4 possible arrangements. The default may not be correct for your camera.</span><br><br>"
            "<b style='font-size: 18px;'>If your image appears too green, red, or blue:</b><br>"
            "<span style='font-size: 18px;'>Go to <b>Settings → CYYM Pattern</b> to select the correct arrangement.</span>"
        )
        msg_box.setInformativeText(
            f"<span style='font-size: 18px;'>Current pattern: <b>{ImageProcessor.CYYM_PATTERN}</b><br><br>"
            f"Would you like to select a different pattern now?</span>"
        )
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #1a1a1a;
                font-size: 18px;
            }
            QMessageBox QLabel {
                color: #00ffff;
                background-color: #1a1a1a;
                font-size: 18px;
            }
            QPushButton {
                background-color: #2a2a2a;
                color: #00ffff;
                border: 2px solid #00ffff;
                border-radius: 5px;
                padding: 14px 24px;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #003333;
                border-color: #00ff00;
            }
        """)
        
        reply = msg_box.exec_()
        
        if reply == QMessageBox.Yes:
            self._select_cyym_pattern()
    
    def _create_toolbar(self):
        """Create toolbar with playback controls."""
        toolbar = QToolBar("Controls")
        toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        
        # First frame button
        self.btn_first = QPushButton("⏮ First")
        self.btn_first.setToolTip("Jump to first frame")
        self.btn_first.clicked.connect(self._on_first_frame)
        self.btn_first.setEnabled(False)
        toolbar.addWidget(self.btn_first)
        
        # Previous frame button
        self.btn_prev = QPushButton("⏪ Prev")
        self.btn_prev.setToolTip("Previous frame (Left Arrow)")
        self.btn_prev.clicked.connect(self._on_previous_frame)
        self.btn_prev.setEnabled(False)
        toolbar.addWidget(self.btn_prev)
        
        # Play/Pause button
        self.btn_play = QPushButton("▶ Play")
        self.btn_play.setToolTip("Play/Pause (Space)")
        self.btn_play.clicked.connect(self._on_play_pause)
        self.btn_play.setEnabled(False)
        toolbar.addWidget(self.btn_play)
        
        # Next frame button
        self.btn_next = QPushButton("Next ⏩")
        self.btn_next.setToolTip("Next frame (Right Arrow)")
        self.btn_next.clicked.connect(self._on_next_frame)
        self.btn_next.setEnabled(False)
        toolbar.addWidget(self.btn_next)
        
        # Last frame button
        self.btn_last = QPushButton("Last ⏭")
        self.btn_last.setToolTip("Jump to last frame")
        self.btn_last.clicked.connect(self._on_last_frame)
        self.btn_last.setEnabled(False)
        toolbar.addWidget(self.btn_last)
        
        toolbar.addSeparator()
        
        # Frame slider
        self.frame_slider = QSlider(Qt.Horizontal)
        self.frame_slider.setMinimum(0)
        self.frame_slider.setMaximum(0)
        self.frame_slider.setValue(0)
        self.frame_slider.setEnabled(False)
        self.frame_slider.valueChanged.connect(self._on_slider_changed)
        self.frame_slider.setToolTip("Frame position")
        toolbar.addWidget(self.frame_slider)
    
    def _apply_theme(self):
        """Apply high-tech dark theme."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0a;
                font-size: 18px;
            }
            QMenuBar {
                background-color: #1a1a1a;
                color: #00ffff;
                border-bottom: 2px solid #00ffff;
                font-size: 18px;
                padding: 6px;
            }
            QMenuBar::item {
                padding: 8px 16px;
            }
            QMenuBar::item:selected {
                background-color: #003333;
            }
            QMenu {
                background-color: #1a1a1a;
                color: #00ffff;
                border: 1px solid #00ffff;
                font-size: 18px;
            }
            QMenu::item {
                padding: 10px 40px;
            }
            QMenu::item:selected {
                background-color: #003333;
            }
            QToolBar {
                background-color: #1a1a1a;
                border: 1px solid #00ffff;
                spacing: 8px;
                padding: 8px;
            }
            QPushButton {
                background-color: #2a2a2a;
                color: #00ffff;
                border: 2px solid #00ffff;
                border-radius: 5px;
                padding: 14px 24px;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #003333;
                border-color: #00ff00;
            }
            QPushButton:pressed {
                background-color: #001a1a;
            }
            QPushButton:disabled {
                background-color: #1a1a1a;
                color: #666666;
                border-color: #333333;
            }
            QSlider::groove:horizontal {
                border: 1px solid #00ffff;
                height: 14px;
                background: #1a1a1a;
                margin: 2px 0;
                border-radius: 7px;
            }
            QSlider::handle:horizontal {
                background: #00ffff;
                border: 1px solid #00ff00;
                width: 28px;
                margin: -8px 0;
                border-radius: 14px;
            }
            QSlider::handle:horizontal:hover {
                background: #00ff00;
            }
            QStatusBar {
                background-color: #1a1a1a;
                color: #00ffff;
                border-top: 2px solid #00ffff;
                font-size: 18px;
                padding: 6px;
            }
            QStatusBar QLabel {
                font-size: 18px;
            }
            QDockWidget {
                color: #00ffff;
                font-size: 18px;
                titlebar-close-icon: url(close.png);
                titlebar-normal-icon: url(float.png);
            }
            QDockWidget::title {
                background-color: #1a1a1a;
                border: 1px solid #00ffff;
                padding: 10px;
                font-size: 18px;
                font-weight: bold;
            }
            QMessageBox {
                background-color: #1a1a1a;
                font-size: 18px;
            }
            QMessageBox QLabel {
                color: #00ffff;
                background-color: #1a1a1a;
                font-size: 18px;
            }
            QInputDialog {
                background-color: #1a1a1a;
                font-size: 18px;
            }
            QInputDialog QLabel {
                color: #00ffff;
                font-size: 18px;
            }
            QInputDialog QComboBox {
                background-color: #2a2a2a;
                color: #00ffff;
                border: 2px solid #00ffff;
                border-radius: 5px;
                padding: 10px;
                font-size: 18px;
            }
            QInputDialog QComboBox::drop-down {
                border: none;
            }
            QInputDialog QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid #00ffff;
            }
            QInputDialog QComboBox QAbstractItemView {
                background-color: #2a2a2a;
                color: #00ffff;
                selection-background-color: #003333;
                font-size: 18px;
            }
            QProgressDialog {
                background-color: #1a1a1a;
                color: #00ffff;
                font-size: 18px;
            }
            QProgressBar {
                border: 2px solid #00ffff;
                border-radius: 5px;
                text-align: center;
                background-color: #0a0a0a;
                color: #00ffff;
                font-size: 18px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #00ffff;
            }
        """)
    
    def _setup_logging(self):
        """Set up logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ser_viewer.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def open_file(self):
        """Open video file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video File",
            "",
            "Video Files (*.ser *.avi *.mp4);;SER Files (*.ser);;AVI Files (*.avi);;MP4 Files (*.mp4);;All Files (*.*)"
        )
        
        if file_path:
            self._load_file(file_path)
    
    def _load_file(self, file_path: str):
        """Load video file (SER or AVI).
        
        Args:
            file_path: Path to video file
        """
        try:
            # Close previous file
            if self.ser_file:
                self.ser_file.close()
            
            # Open new file (supports both SER and AVI)
            self.ser_file = SERFile(file_path)
            
            # Check if this is a CYYM file and auto-detect pattern (SER only)
            if hasattr(self.ser_file.header, 'color_id') and self.ser_file.header.color_id == 8:  # CYYM
                # Auto-detect pattern based on camera/instrument
                detected_pattern = ImageProcessor.detect_cyym_pattern(
                    self.ser_file.header.instrument
                )
                ImageProcessor.CYYM_PATTERN = detected_pattern
                
                # Log the detection
                self.logger.info(
                    f"CYYM file detected. Camera: {self.ser_file.header.instrument}, "
                    f"Auto-selected pattern: {detected_pattern}"
                )
                
                # Clear cache to ensure new pattern is used
                self.ser_file.cache.clear()
            
            # Update metadata panel
            self.metadata_panel.update_metadata(self.ser_file)
            
            # Create controllers
            self.nav_controller = NavigationController(
                self.ser_file.header.frame_count,
                self._on_frame_changed
            )
            
            self.playback_controller = PlaybackController(
                self.nav_controller,
                self.ser_file.prefetch_frames
            )
            self.playback_controller.set_timer_callback(self._schedule_timer)
            
            # Update UI
            self.frame_slider.setMaximum(self.ser_file.header.frame_count - 1)
            self.frame_slider.setEnabled(True)
            self._enable_controls(True)
            self.stack_action.setEnabled(True)
            
            # Display first frame
            self._display_current_frame()
            
            # Update window title
            file_type = self.ser_file.file_type
            self.setWindowTitle(f"{file_type} File Viewer - {os.path.basename(file_path)}")
            
            self.logger.info(f"Loaded {file_type} file: {file_path}")
            
        except SERError as e:
            QMessageBox.critical(self, "Error Loading File", str(e))
            self.logger.error(f"Error loading file: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Unexpected Error", f"An unexpected error occurred: {e}")
            self.logger.exception("Unexpected error loading file")
    
    def _enable_controls(self, enabled: bool):
        """Enable/disable playback controls.
        
        Args:
            enabled: True to enable, False to disable
        """
        self.btn_first.setEnabled(enabled)
        self.btn_prev.setEnabled(enabled)
        self.btn_play.setEnabled(enabled)
        self.btn_next.setEnabled(enabled)
        self.btn_last.setEnabled(enabled)
    
    def _display_current_frame(self):
        """Display current frame."""
        if not self.ser_file or not self.nav_controller:
            return
        
        try:
            frame_index = self.nav_controller.get_current_frame()
            pil_image = self.ser_file.get_display_frame(frame_index)
            self.canvas.set_image(pil_image)
            
            # Update status bar
            frame_info = self.ser_file.get_frame_info(frame_index)
            status_text = f"Frame {frame_index + 1} / {self.ser_file.header.frame_count}"
            
            if frame_info['timestamp']:
                status_text += f" | {frame_info['timestamp'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} UTC"
            
            self.status_label.setText(status_text)
            
            # Update slider without triggering signal
            self.frame_slider.blockSignals(True)
            self.frame_slider.setValue(frame_index)
            self.frame_slider.blockSignals(False)
            
        except Exception as e:
            self.logger.error(f"Error displaying frame: {e}")
            QMessageBox.warning(self, "Display Error", f"Error displaying frame: {e}")
    
    def _on_frame_changed(self, frame_index: int):
        """Callback when frame changes.
        
        Args:
            frame_index: New frame index
        """
        self._display_current_frame()
    
    def _on_first_frame(self):
        """Handle first frame button."""
        if self.nav_controller:
            self.nav_controller.first_frame()
    
    def _on_previous_frame(self):
        """Handle previous frame button."""
        if self.nav_controller:
            self.nav_controller.previous_frame()
    
    def _on_next_frame(self):
        """Handle next frame button."""
        if self.nav_controller:
            self.nav_controller.next_frame()
    
    def _on_last_frame(self):
        """Handle last frame button."""
        if self.nav_controller:
            self.nav_controller.last_frame()
    
    def _on_play_pause(self):
        """Handle play/pause button."""
        if not self.playback_controller:
            return
        
        self.playback_controller.toggle_play_pause()
        
        if self.playback_controller.is_playing:
            self.btn_play.setText("⏸ Pause")
        else:
            self.btn_play.setText("▶ Play")
    
    def _on_slider_changed(self, value: int):
        """Handle slider value change.
        
        Args:
            value: New slider value
        """
        if self.nav_controller:
            self.nav_controller.goto_frame(value)
    
    def _schedule_timer(self, interval_ms: int, callback):
        """Schedule timer for playback.
        
        Args:
            interval_ms: Interval in milliseconds
            callback: Callback function
        """
        QTimer.singleShot(interval_ms, callback)
    
    def _open_and_enhance_image(self):
        """Open an existing image and enhance it."""
        # Ask user to select image file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image to Enhance",
            "E:/test/Kiro_ser/image",
            "Image Files (*.png *.jpg *.jpeg *.tif *.tiff);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            # Load image
            import numpy as np
            from PIL import Image
            
            img = Image.open(file_path)
            img_array = np.array(img)
            
            # Convert to RGB if needed
            if len(img_array.shape) == 2:
                # Grayscale to RGB
                img_array = np.stack([img_array] * 3, axis=-1)
            elif img_array.shape[2] == 4:
                # RGBA to RGB
                img_array = img_array[:, :, :3]
            
            # Open enhancement dialog
            dialog = EnhancementDialog(img_array, self)
            if dialog.exec_() == QDialog.Accepted:
                enhanced_image = dialog.get_result()
                if enhanced_image:
                    # Ask where to save
                    save_path, _ = QFileDialog.getSaveFileName(
                        self,
                        "Save Enhanced Image",
                        file_path.replace('.png', '_enhanced.png'),
                        "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*.*)"
                    )
                    
                    if save_path:
                        # Save enhanced image
                        enhanced_image.save(save_path)
                        self.logger.info(f"Saved enhanced image to: {save_path}")
                        
                        QMessageBox.information(
                            self,
                            "Enhancement Complete",
                            f"Enhanced image saved to:\n{save_path}"
                        )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open or enhance image:\n{e}"
            )
            self.logger.error(f"Error enhancing image: {e}")
    
    def _stack_and_save(self):
        """Stack all frames and save to PNG."""
        if not self.ser_file:
            return
        
        # Ask user for stacking method
        methods = ['Average', 'Median', 'Sum']
        method, ok = QInputDialog.getItem(
            self,
            "Select Stacking Method",
            "Choose stacking method:",
            methods,
            0,
            False
        )
        
        if not ok:
            return
        
        method = method.lower()
        
        # Warn about median memory requirements for large files
        if method == 'median':
            header = self.ser_file.get_header()
            first_frame = self.ser_file.parser.get_frame(0)
            # float32 is 4 bytes per pixel
            frame_size_mb = (first_frame.nbytes * 4) / (1024 * 1024)
            total_size_mb = frame_size_mb * header.frame_count
            
            if total_size_mb > 8192:  # More than 8GB
                reply = QMessageBox.question(
                    self,
                    "Large File Warning",
                    f"Median stacking requires approximately {total_size_mb:.1f} MB ({total_size_mb/1024:.1f} GB) of memory.\n\n"
                    f"This may cause out-of-memory errors on your system.\n\n"
                    f"Consider using 'Average' method instead, which uses much less memory.\n\n"
                    f"Do you want to continue with Median stacking?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    return
        
        # Use default save directory
        save_dir = 'E:/test/Kiro_ser/image'
        
        # Create directory if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)
        
        # Generate timestamp for filenames
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = os.path.splitext(os.path.basename(self.ser_file.file_path))[0]
        
        # Create filenames with timestamp
        original_filename = f"{base_filename}_{method}_original_{timestamp}.png"
        enhanced_filename = f"{base_filename}_{method}_enhanced_{timestamp}.png"
        
        original_path = os.path.join(save_dir, original_filename)
        enhanced_path = os.path.join(save_dir, enhanced_filename)
        
        # Create progress dialog
        progress = QProgressDialog(
            "Stacking frames...",
            "Cancel",
            0,
            self.ser_file.header.frame_count,
            self
        )
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle("Stacking Progress")
        progress.setStyleSheet("""
            QProgressDialog {
                background-color: #1a1a1a;
                color: #00ffff;
            }
            QProgressBar {
                border: 2px solid #00ffff;
                border-radius: 5px;
                text-align: center;
                background-color: #0a0a0a;
                color: #00ffff;
            }
            QProgressBar::chunk {
                background-color: #00ffff;
            }
            QPushButton {
                background-color: #2a2a2a;
                color: #00ffff;
                border: 2px solid #00ffff;
                border-radius: 5px;
                padding: 5px 10px;
            }
        """)
        
        # Progress callback
        def update_progress(current, total):
            progress.setValue(current)
            if progress.wasCanceled():
                raise Exception("Stacking cancelled by user")
        
        try:
            # Stack frames
            stacker = FrameStacker()
            stacked_frame = stacker.stack_frames(
                self.ser_file,
                method=method,
                progress_callback=update_progress
            )
            
            # Process stacked frame
            processed_frame = ImageProcessor.process_frame(
                stacked_frame,
                self.ser_file.header.color_id,
                self.ser_file.header.pixel_depth
            )
            
            # Save original (non-enhanced) version
            original_image = Image.fromarray(processed_frame, mode='RGB')
            original_image.save(original_path, 'PNG')
            self.logger.info(f"Saved original stacked image to: {original_path}")
            
            progress.close()
            
            # Ask user if they want to manually enhance the image
            reply = QMessageBox.question(
                self,
                "Enhance Image?",
                "Would you like to manually adjust the stacked image?\n\n"
                "You can adjust:\n"
                "• Brightness\n"
                "• Contrast\n"
                "• Saturation\n"
                "• Sharpness\n\n"
                "Both original and enhanced versions will be saved.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # Open enhancement dialog
                dialog = EnhancementDialog(processed_frame, self)
                if dialog.exec_() == QDialog.Accepted:
                    enhanced_image = dialog.get_result()
                    if enhanced_image:
                        # Save enhanced version
                        enhanced_image.save(enhanced_path, 'PNG')
                        self.logger.info(f"Saved enhanced stacked image to: {enhanced_path}")
                        
                        # Show success message
                        success_msg = (
                            f"Stacking complete! Saved 2 files:\n\n"
                            f"Original:\n{original_path}\n\n"
                            f"Enhanced:\n{enhanced_path}"
                        )
                    else:
                        success_msg = (
                            f"Stacking complete! Saved:\n\n"
                            f"{original_path}"
                        )
                else:
                    success_msg = (
                        f"Stacking complete! Saved:\n\n"
                        f"{original_path}"
                    )
            else:
                success_msg = (
                    f"Stacking complete! Saved:\n\n"
                    f"{original_path}"
                )
            
            QMessageBox.information(
                self,
                "Stacking Complete",
                success_msg
            )
            
            self.logger.info(f"Stacked {self.ser_file.header.frame_count} frames using {method} method")
            
        except Exception as e:
            progress.close()
            if "cancelled" not in str(e).lower():
                QMessageBox.critical(
                    self,
                    "Stacking Error",
                    f"Error stacking frames: {e}"
                )
                self.logger.error(f"Error stacking frames: {e}")
    
    def keyPressEvent(self, event):
        """Handle key press events.
        
        Args:
            event: Key event
        """
        if event.key() == Qt.Key_Space:
            self._on_play_pause()
        elif event.key() == Qt.Key_Left:
            self._on_previous_frame()
        elif event.key() == Qt.Key_Right:
            self._on_next_frame()
        elif event.key() == Qt.Key_Home:
            self._on_first_frame()
        elif event.key() == Qt.Key_End:
            self._on_last_frame()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle window close event.
        
        Args:
            event: Close event
        """
        if self.ser_file:
            self.ser_file.close()
        event.accept()
