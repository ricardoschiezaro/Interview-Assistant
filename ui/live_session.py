import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QComboBox, QSizeGrip,
    QStatusBar,
)
from PyQt6.QtCore import Qt, QPoint, pyqtSlot, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QColor

from ui.copilot_tab import CopilotTab
from ui.scratchpad_tab import ScratchpadTab
from ui.signals import AppSignals
from core.event_loop import get_event_loop, run_coroutine

logger = logging.getLogger(__name__)

class TitleBar(QWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self._win = parent
        self._drag_pos: QPoint | None = None
        self.setObjectName("titleBar")
        self.setFixedHeight(36)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)
        
        icon_label = QLabel("🔴")
        icon_label.setStyleSheet("font-size: 10px; color: #ef4444;")
        layout.addWidget(icon_label)

        title = QLabel("LIVE SESSION")
        title.setStyleSheet("color: #ef4444; font-weight: bold; letter-spacing: 1px; font-size: 11px;")
        layout.addWidget(title)
        
        self.company_label = QLabel("")
        self.company_label.setStyleSheet("color: #94a3b8; font-size: 11px; margin-left: 10px;")
        layout.addWidget(self.company_label)
        
        layout.addStretch()

        # Status indicator
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #22c55e;")
        layout.addWidget(self.status_dot)

        close_btn = QPushButton("✕")
        close_btn.setObjectName("winControlBtn")
        close_btn.setFixedSize(28, 28)
        close_btn.clicked.connect(self._win.request_close)
        layout.addWidget(close_btn)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self._win.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self._win.move(event.globalPosition().toPoint() - self._drag_pos)

class LiveSessionWindow(QMainWindow):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._signals = AppSignals()
        self._pipeline = None
        self._is_active = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(1.0) # We handle opacity in QSS
        self.setMinimumSize(400, 500)
        self.resize(450, 600)

        root = QWidget()
        root.setObjectName("rootContainer")
        root.setStyleSheet("""
            #rootContainer {
                background: rgba(15, 23, 42, 160);
                border-radius: 30px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            #titleBar {
                background: transparent;
            }
            #sessionLabel {
                font-size: 20px;
                font-weight: bold;
                color: #f8fafc;
                padding-left: 10px;
            }
            #statusToggle {
                background: rgba(34, 197, 94, 0.2);
                color: #4ade80;
                border: 1px solid #22c55e;
                border-radius: 12px;
                padding: 4px 12px;
                font-weight: bold;
                font-size: 11px;
            }
            #responseArea {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 20px;
                color: #e2e8f0;
                padding: 20px;
                margin: 10px;
                border: 1px solid rgba(255, 255, 255, 0.05);
                font-size: 13px;
                line-height: 1.6;
            }
            #inputArea {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                color: #f8fafc;
                padding: 10px 15px;
                margin: 10px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header Row
        header = QHBoxLayout()
        self.session_title = QLabel("Session Mode")
        self.session_title.setObjectName("sessionLabel")
        header.addWidget(self.session_title)
        
        header.addStretch()
        
        self.status_toggle = QLabel("ON")
        self.status_toggle.setObjectName("statusToggle")
        header.addWidget(self.status_toggle)
        
        close_btn = QPushButton("✕")
        close_btn.setStyleSheet("background: transparent; color: #94a3b8; font-size: 18px; border: none;")
        close_btn.clicked.connect(self.request_close)
        header.addWidget(close_btn)
        
        layout.addLayout(header)

        # AI Response Area (Replacing tabs for a cleaner look like the image)
        from ui.copilot_tab import CopilotTab
        self.response_browser = CopilotTab() # We keep the logic but style it
        self.response_browser.setObjectName("responseArea")
        layout.addWidget(self.response_browser)

        # Input Area at bottom
        from PyQt6.QtWidgets import QLineEdit
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message...")
        self.input_field.setObjectName("inputArea")
        layout.addWidget(self.input_field)

        self._signals.token_received.connect(self.response_browser.append_token)
        self._signals.generation_done.connect(self.response_browser.on_generation_done)
        self._signals.question_received.connect(self.response_browser.set_question)

    def set_company(self, name):
        self.session_title.setText(f"Session Mode: {name}")

    def request_close(self):
        self.closed.emit()
        self.hide()
