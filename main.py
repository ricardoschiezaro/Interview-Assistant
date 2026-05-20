import sys
import os

# Add the short-path site-packages dir (workaround for Windows Long Path restriction)
# Only inject if the directory actually exists on this machine
_LIBS = r"C:\pylibs"
if os.path.isdir(_LIBS) and _LIBS not in sys.path:
    sys.path.insert(0, _LIBS)

import asyncio
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Configure logging before any other imports
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

from ui.main_window import MainWindow
from core.event_loop import setup_asyncio_event_loop


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Interview Assistant")
    app.setOrganizationName("Interview Assistant")

    # Setup asyncio integration with Qt
    loop = setup_asyncio_event_loop(app)

    # Create and show the main window
    window = MainWindow()
    window.show()

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
