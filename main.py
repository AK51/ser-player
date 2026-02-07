"""Main entry point for SER File Viewer application."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from PyQt5.QtWidgets import QApplication
except ImportError:
    print("ERROR: PyQt5 is not installed.")
    print("Please install it using: pip install PyQt5")
    sys.exit(1)

from src.gui.main_window import MainWindow


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("SER File Viewer")
    app.setOrganizationName("Astronomy Tools")
    
    # Check if file path provided via command line
    auto_open_path = None
    if len(sys.argv) > 1:
        auto_open_path = sys.argv[1]
    
    window = MainWindow(auto_open_path=auto_open_path)
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
