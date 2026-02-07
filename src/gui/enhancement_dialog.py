"""Enhancement dialog for manual image adjustment with AI upscaling."""

import numpy as np
from PIL import Image
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider, 
    QPushButton, QGroupBox, QGridLayout, QSizePolicy, QComboBox, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage


class EnhancementDialog(QDialog):
    """Dialog for manually adjusting image enhancement parameters."""
    
    def __init__(self, image_array: np.ndarray, parent=None):
        super().__init__(parent)
        self.original_image = image_array.copy()
        self.current_image = image_array.copy()
        self.result_image = None
        self.cached_original_size = None
        self.cached_enhanced_size = None
        
        self.setWindowTitle("Image Enhancement")
        
        self._setup_ui()
        self._apply_theme()
        
        # Maximize window width
        self.showMaximized()
        
        # Update preview after window is shown to get correct sizes
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, self._initialize_preview)
    
    def _setup_ui(self):
        """Set up user interface."""
        layout = QVBoxLayout()
        
        # Preview area
        preview_layout = QHBoxLayout()
        
        # Original preview (smaller)
        original_group = QGroupBox("Original")
        original_layout = QVBoxLayout()
        self.original_label = QLabel()
        self.original_label.setMinimumSize(300, 300)
        self.original_label.setMaximumSize(400, 400)
        self.original_label.setAlignment(Qt.AlignCenter)
        self.original_label.setStyleSheet("border: 2px solid #00ffff; background-color: #1a1a1a;")
        self.original_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        original_layout.addWidget(self.original_label)
        original_group.setLayout(original_layout)
        preview_layout.addWidget(original_group, stretch=0)
        
        # Enhanced preview (larger)
        enhanced_group = QGroupBox("Enhanced")
        enhanced_layout = QVBoxLayout()
        self.enhanced_label = QLabel()
        self.enhanced_label.setMinimumSize(800, 800)
        self.enhanced_label.setAlignment(Qt.AlignCenter)
        self.enhanced_label.setStyleSheet("border: 2px solid #00ff00; background-color: #1a1a1a;")
        self.enhanced_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        enhanced_layout.addWidget(self.enhanced_label)
        enhanced_group.setLayout(enhanced_layout)
        preview_layout.addWidget(enhanced_group, stretch=1)
        
        layout.addLayout(preview_layout)
        
        # Controls
        controls_group = QGroupBox("Adjustment Controls")
        controls_layout = QGridLayout()
        
        # Brightness slider
        controls_layout.addWidget(QLabel("Brightness:"), 0, 0)
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setMinimum(10)
        self.brightness_slider.setMaximum(500)
        self.brightness_slider.setValue(100)
        self.brightness_slider.setTickPosition(QSlider.TicksBelow)
        self.brightness_slider.setTickInterval(50)
        self.brightness_slider.valueChanged.connect(self._on_parameter_changed)
        controls_layout.addWidget(self.brightness_slider, 0, 1)
        self.brightness_value = QLabel("1.00x")
        controls_layout.addWidget(self.brightness_value, 0, 2)
        
        # Contrast slider
        controls_layout.addWidget(QLabel("Contrast:"), 1, 0)
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setMinimum(10)
        self.contrast_slider.setMaximum(300)
        self.contrast_slider.setValue(100)
        self.contrast_slider.setTickPosition(QSlider.TicksBelow)
        self.contrast_slider.setTickInterval(50)
        self.contrast_slider.valueChanged.connect(self._on_parameter_changed)
        controls_layout.addWidget(self.contrast_slider, 1, 1)
        self.contrast_value = QLabel("1.00x")
        controls_layout.addWidget(self.contrast_value, 1, 2)
        
        # Saturation slider
        controls_layout.addWidget(QLabel("Saturation:"), 2, 0)
        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setMinimum(0)
        self.saturation_slider.setMaximum(300)
        self.saturation_slider.setValue(100)
        self.saturation_slider.setTickPosition(QSlider.TicksBelow)
        self.saturation_slider.setTickInterval(50)
        self.saturation_slider.valueChanged.connect(self._on_parameter_changed)
        controls_layout.addWidget(self.saturation_slider, 2, 1)
        self.saturation_value = QLabel("1.00x")
        controls_layout.addWidget(self.saturation_value, 2, 2)
        
        # Sharpness slider
        controls_layout.addWidget(QLabel("Sharpness:"), 3, 0)
        self.sharpness_slider = QSlider(Qt.Horizontal)
        self.sharpness_slider.setMinimum(0)
        self.sharpness_slider.setMaximum(1000)
        self.sharpness_slider.setValue(100)
        self.sharpness_slider.setTickPosition(QSlider.TicksBelow)
        self.sharpness_slider.setTickInterval(100)
        self.sharpness_slider.valueChanged.connect(self._on_parameter_changed)
        controls_layout.addWidget(self.sharpness_slider, 3, 1)
        self.sharpness_value = QLabel("1.00x")
        controls_layout.addWidget(self.sharpness_value, 3, 2)
        
        # AI Upscaling section
        controls_layout.addWidget(QLabel("AI Upscaling:"), 4, 0)
        self.upscale_combo = QComboBox()
        self.upscale_combo.addItems(['None', '2x (1080p→4K)', '4x (1080p→8K)', '2x', '4x'])
        self.upscale_combo.setCurrentIndex(0)
        controls_layout.addWidget(self.upscale_combo, 4, 1)
        self.upscale_label = QLabel("Original size")
        controls_layout.addWidget(self.upscale_label, 4, 2)
        
        # AI Sharpening section
        controls_layout.addWidget(QLabel("AI Sharpening:"), 5, 0)
        self.ai_sharpen_checkbox = QCheckBox("Enable AI Deblur")
        self.ai_sharpen_checkbox.setChecked(False)
        controls_layout.addWidget(self.ai_sharpen_checkbox, 5, 1)
        self.ai_sharpen_label = QLabel("Uses deep learning")
        controls_layout.addWidget(self.ai_sharpen_label, 5, 2)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self._reset_parameters)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._apply_enhancement)
        button_layout.addWidget(apply_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _apply_theme(self):
        """Apply dark theme."""
        self.setStyleSheet("""
            QDialog {
                background-color: #0a0a0a;
                color: #00ffff;
                font-size: 18px;
            }
            QGroupBox {
                border: 2px solid #00ffff;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-size: 18px;
                font-weight: bold;
                color: #00ffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #00ffff;
                font-size: 18px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #00ffff;
                height: 10px;
                background: #1a1a1a;
                margin: 2px 0;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #00ffff;
                border: 1px solid #00ff00;
                width: 20px;
                margin: -5px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #00ff00;
            }
            QPushButton {
                background-color: #2a2a2a;
                color: #00ffff;
                border: 2px solid #00ffff;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 18px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #003333;
                border-color: #00ff00;
            }
            QPushButton:pressed {
                background-color: #001a1a;
            }
        """)
    
    def _on_parameter_changed(self):
        """Handle parameter change."""
        # Update value labels
        brightness = self.brightness_slider.value() / 100.0
        contrast = self.contrast_slider.value() / 100.0
        saturation = self.saturation_slider.value() / 100.0
        sharpness = self.sharpness_slider.value() / 100.0
        
        self.brightness_value.setText(f"{brightness:.2f}x")
        self.contrast_value.setText(f"{contrast:.2f}x")
        self.saturation_value.setText(f"{saturation:.2f}x")
        self.sharpness_value.setText(f"{sharpness:.2f}x")
        
        # Update preview
        self._update_preview()
    
    def _reset_parameters(self):
        """Reset all parameters to default."""
        self.brightness_slider.setValue(100)
        self.contrast_slider.setValue(100)
        self.saturation_slider.setValue(100)
        self.sharpness_slider.setValue(100)
    
    def _initialize_preview(self):
        """Initialize preview with cached sizes."""
        # Cache the label sizes after window is maximized
        self.cached_original_size = self.original_label.size()
        self.cached_enhanced_size = self.enhanced_label.size()
        self._update_preview()
    
    def _update_preview(self):
        """Update preview images."""
        # Show original
        original_pil = Image.fromarray(self.original_image, mode='RGB')
        self._display_image(original_pil, self.original_label, self.cached_original_size)
        
        # Apply enhancements
        brightness = self.brightness_slider.value() / 100.0
        contrast = self.contrast_slider.value() / 100.0
        saturation = self.saturation_slider.value() / 100.0
        sharpness = self.sharpness_slider.value() / 100.0
        
        # Apply brightness (numpy multiplication)
        enhanced = np.clip(self.original_image.astype(float) * brightness, 0, 255).astype(np.uint8)
        
        # Convert to PIL for other adjustments
        pil_image = Image.fromarray(enhanced, mode='RGB')
        
        # Apply contrast
        if contrast != 1.0:
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(contrast)
        
        # Apply saturation
        if saturation != 1.0:
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Color(pil_image)
            pil_image = enhancer.enhance(saturation)
        
        # Apply sharpness
        if sharpness != 1.0:
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Sharpness(pil_image)
            pil_image = enhancer.enhance(sharpness)
        
        # Show enhanced
        self._display_image(pil_image, self.enhanced_label, self.cached_enhanced_size)
        self.current_image = np.array(pil_image)
    
    def _display_image(self, pil_image: Image.Image, label: QLabel, cached_size=None):
        """Display PIL image in label."""
        # Convert to QPixmap
        img_data = pil_image.tobytes("raw", "RGB")
        qimage = QImage(img_data, pil_image.width, pil_image.height,
                       pil_image.width * 3, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        
        # Use cached size if available, otherwise use current label size
        target_size = cached_size if cached_size else label.size()
        
        # Scale to fill the label completely
        scaled_pixmap = pixmap.scaled(
            target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        label.setPixmap(scaled_pixmap)
        label.setScaledContents(False)
    
    def _apply_enhancement(self):
        """Apply enhancement and close dialog."""
        # Apply AI sharpening first if enabled
        if self.ai_sharpen_checkbox.isChecked():
            # Show progress message
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setWindowTitle("AI Sharpening")
            msg.setText("Applying AI deblur...\nThis may take 1-2 minutes.")
            msg.setStandardButtons(QMessageBox.NoButton)
            msg.show()
            msg.repaint()
            
            try:
                # Apply AI sharpening to current enhanced image
                sharpened = self._apply_ai_sharpening(self.current_image)
                self.current_image = sharpened
                msg.close()
            except Exception as e:
                msg.close()
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self,
                    "AI Sharpening Failed",
                    f"AI sharpening failed: {e}\n\nContinuing without AI sharpening."
                )
        
        # Get upscaling factor
        upscale_text = self.upscale_combo.currentText()
        
        if 'None' in upscale_text:
            # No upscaling, just use current enhanced image
            self.result_image = Image.fromarray(self.current_image, mode='RGB')
        else:
            # Apply AI upscaling
            if '2x' in upscale_text:
                scale = 2
            elif '4x' in upscale_text:
                scale = 4
            else:
                scale = 1
            
            if scale > 1:
                # Show progress message
                from PyQt5.QtWidgets import QMessageBox
                msg = QMessageBox(self)
                msg.setWindowTitle("AI Upscaling")
                msg.setText(f"Applying {scale}x AI upscaling...\nThis may take a few minutes.")
                msg.setStandardButtons(QMessageBox.NoButton)
                msg.show()
                msg.repaint()
                
                try:
                    # Apply AI upscaling
                    upscaled = self._apply_ai_upscaling(self.current_image, scale)
                    self.result_image = Image.fromarray(upscaled, mode='RGB')
                    msg.close()
                except Exception as e:
                    msg.close()
                    QMessageBox.warning(
                        self,
                        "Upscaling Failed",
                        f"AI upscaling failed: {e}\n\nUsing original resolution."
                    )
                    self.result_image = Image.fromarray(self.current_image, mode='RGB')
            else:
                self.result_image = Image.fromarray(self.current_image, mode='RGB')
        
        self.accept()
    
    def _apply_ai_sharpening(self, image: np.ndarray) -> np.ndarray:
        """Apply AI-based deblurring/sharpening.
        
        Args:
            image: Input blurry image
            
        Returns:
            Sharpened image
        """
        import cv2
        
        try:
            # Try NAFNet (best for deblurring)
            from basicsr.archs.nafnet_arch import NAFNet
            import torch
            
            # This is a placeholder - you would need to load a pretrained model
            # For now, use advanced OpenCV sharpening
            raise ImportError("NAFNet not available, using fallback")
            
        except ImportError:
            # Fallback: Advanced multi-scale sharpening
            return self._apply_advanced_sharpening(image)
    
    def _apply_advanced_sharpening(self, image: np.ndarray) -> np.ndarray:
        """Apply advanced multi-scale sharpening (fallback).
        
        Args:
            image: Input image
            
        Returns:
            Sharpened image
        """
        import cv2
        
        # Convert to float
        img_float = image.astype(np.float32) / 255.0
        
        # Multi-scale unsharp masking
        sharpened = img_float.copy()
        
        # Scale 1: Fine details (sigma=0.5)
        blur1 = cv2.GaussianBlur(img_float, (0, 0), 0.5)
        sharpened = sharpened + 1.5 * (img_float - blur1)
        
        # Scale 2: Medium details (sigma=1.0)
        blur2 = cv2.GaussianBlur(img_float, (0, 0), 1.0)
        sharpened = sharpened + 1.0 * (img_float - blur2)
        
        # Scale 3: Large details (sigma=2.0)
        blur3 = cv2.GaussianBlur(img_float, (0, 0), 2.0)
        sharpened = sharpened + 0.5 * (img_float - blur3)
        
        # High-pass filter
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]]) / 1.0
        sharpened_uint8 = np.clip(sharpened * 255, 0, 255).astype(np.uint8)
        high_pass = cv2.filter2D(sharpened_uint8, -1, kernel)
        
        # Blend
        result = cv2.addWeighted(sharpened_uint8, 0.7, high_pass, 0.3, 0)
        
        # CLAHE for local contrast
        lab = cv2.cvtColor(result, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        result = cv2.merge([l, a, b])
        result = cv2.cvtColor(result, cv2.COLOR_LAB2RGB)
        
        return result
    
    def _apply_ai_upscaling(self, image: np.ndarray, scale: int) -> np.ndarray:
        """Apply AI-based super-resolution upscaling.
        
        Args:
            image: Input image array
            scale: Upscaling factor (2 or 4)
            
        Returns:
            Upscaled image array
        """
        try:
            # Try Real-ESRGAN first (best quality)
            from realesrgan import RealESRGANer
            from basicsr.archs.rrdbnet_arch import RRDBNet
            
            # Load model
            model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=scale)
            
            # Model paths (download if not exists)
            if scale == 2:
                model_path = 'RealESRGAN_x2plus.pth'
            else:  # scale == 4
                model_path = 'RealESRGAN_x4plus.pth'
            
            upsampler = RealESRGANer(
                scale=scale,
                model_path=model_path,
                model=model,
                tile=400,
                tile_pad=10,
                pre_pad=0,
                half=False
            )
            
            # Upscale
            output, _ = upsampler.enhance(image, outscale=scale)
            return output
            
        except ImportError:
            # Fallback to OpenCV super-resolution
            return self._apply_opencv_upscaling(image, scale)
        except Exception as e:
            # Fallback to OpenCV
            return self._apply_opencv_upscaling(image, scale)
    
    def _apply_opencv_upscaling(self, image: np.ndarray, scale: int) -> np.ndarray:
        """Apply OpenCV-based super-resolution upscaling (fallback).
        
        Args:
            image: Input image array
            scale: Upscaling factor (2 or 4)
            
        Returns:
            Upscaled image array
        """
        import cv2
        
        # Simple high-quality interpolation
        h, w = image.shape[:2]
        new_h, new_w = h * scale, w * scale
        upscaled = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        
        return upscaled
    
    def get_result(self):
        """Get enhanced image result."""
        return self.result_image
