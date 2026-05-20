"""
Prompt Configuration Tab — allows manual editing of the system prompt.
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QLabel, QFrame
)
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt
from core.profile import get_profile

logger = logging.getLogger(__name__)

class PromptTab(QWidget):
    """
    Tab for editing the AI system prompt directly.
    """
    save_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Header
        header = QLabel("System Prompt Configuration")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        layout.addWidget(header)

        # Info
        info = QLabel(
            "This prompt defines the AI's personality, rules, and background. "
            "Changes take effect on the next response."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #94a3b8; font-size: 11px;")
        layout.addWidget(info)

        # Editor
        self.editor = QTextEdit()
        self.editor.setObjectName("promptEditor")
        self.editor.setPlaceholderText("Enter system prompt here...")
        self.editor.setAcceptRichText(False)
        layout.addWidget(self.editor)

        # Bottom Bar
        bottom_bar = QHBoxLayout()
        
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("promptStatus")
        bottom_bar.addWidget(self.status_label)
        
        bottom_bar.addStretch()

        self.reset_btn = QPushButton("Reset to Default")
        self.reset_btn.setObjectName("resetPromptBtn")
        self.reset_btn.setFixedWidth(120)
        self.reset_btn.clicked.connect(self._on_reset)
        bottom_bar.addWidget(self.reset_btn)

        self.save_btn = QPushButton("Save Prompt")
        self.save_btn.setObjectName("savePromptBtn")
        self.save_btn.setFixedWidth(120)
        self.save_btn.clicked.connect(self._on_save)
        bottom_bar.addWidget(self.save_btn)

        layout.addLayout(bottom_bar)

    def _load_data(self):
        profile = get_profile()
        self.editor.setPlainText(profile.custom_prompt)

    @pyqtSlot()
    def _on_save(self):
        profile = get_profile()
        profile.custom_prompt = self.editor.toPlainText()
        profile.save()
        self.status_label.setText("Prompt saved and applied!")
        self.status_label.setStyleSheet("color: #ffffff; font-size: 11px;")
        self.save_requested.emit()

    @pyqtSlot()
    def _on_reset(self):
        from core.profile import DEFAULT_SYSTEM_PROMPT
        self.editor.setPlainText(DEFAULT_SYSTEM_PROMPT)
        self.status_label.setText("Reset to default (click Save to apply)")
        self.status_label.setStyleSheet("color: #ffffff; font-size: 11px;")
