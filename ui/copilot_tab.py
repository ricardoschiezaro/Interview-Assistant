"""
Copilot Tab — streams Groq responses in real-time.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser,
    QLabel, QPushButton, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont, QTextCursor


class CopilotTab(QWidget):
    """Displays the interviewer question and paired AI history."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_question = ""
        self._live_label = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        # ── Header with Export ────────────────────────────────────────────────
        header_row = QHBoxLayout()
        q_header = QLabel("CONVERSATION HISTORY:")
        q_header.setObjectName("sectionHeader")
        header_row.addWidget(q_header)
        header_row.addStretch()

        self.export_btn = QPushButton("Export")
        self.export_btn.setObjectName("toolBtn")
        self.export_btn.setFixedSize(70, 24)
        self.export_btn.clicked.connect(self._on_export)
        header_row.addWidget(self.export_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setObjectName("clearBtn")
        self.clear_btn.setFixedSize(60, 24)
        self.clear_btn.clicked.connect(self.clear_response)
        header_row.addWidget(self.clear_btn)
        
        layout.addLayout(header_row)

        # ── Live Transcription Label ──────────────────────────────────────────
        self.live_label = QLabel("")
        self.live_label.setStyleSheet("color: #ffffff; font-style: italic; font-size: 12px; margin-bottom: 5px;")
        self.live_label.setWordWrap(True)
        layout.addWidget(self.live_label)

        # ── History browser ──────────────────────────────────────────────────
        self.response_browser = QTextBrowser()
        self.response_browser.setObjectName("responseBrowser")
        self.response_browser.setReadOnly(True)
        self.response_browser.setOpenLinks(False)
        self.response_browser.setHtml("<div style='color: #64748b; font-style: italic;'>Waiting for the first question...</div>")
        layout.addWidget(self.response_browser)

    # ── Public slots ──────────────────────────────────────────────────────────

    @pyqtSlot(str)
    def set_question(self, text: str):
        """Called for both live and finalized text."""
        if text.endswith("..."):
            # Live preview
            self.live_label.setText(f"Hearing: {text}")
            return
        
        # Finalized question - commit to history
        self.live_label.setText("")
        if not text.strip(): return
        self._current_question = text
        
        cursor = self.response_browser.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        if "Waiting for the first question" in self.response_browser.toPlainText() or "History cleared" in self.response_browser.toPlainText():
            self.response_browser.clear()

        import datetime
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        
        html = f"""
        <div style="margin-top: 15px; border-left: 3px solid rgba(255,255,255,0.4); padding-left: 10px;">
            <div style="color: #ffffff; font-size: 12px; font-weight: bold;">INTERVIEWER [{ts}]</div>
            <div style="color: #ffffff; font-style: italic; font-size: 15px; margin-top: 2px;">"{text}"</div>
        </div>
        <div style="margin-top: 10px; margin-bottom: 5px; border-left: 3px solid rgba(255,255,255,0.7); padding-left: 10px;">
            <div style="color: #ffffff; font-size: 12px; font-weight: bold;">COPILOT</div>
            <div style="color: #ffffff; font-size: 16px; margin-top: 4px;" id="current_resp_block">
        """
        cursor.insertHtml(html)
        self.response_browser.setTextCursor(cursor)
        self.response_browser.ensureCursorVisible()

    @pyqtSlot(str)
    def append_token(self, token: str):
        cursor = self.response_browser.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(token)
        self.response_browser.setTextCursor(cursor)
        self.response_browser.ensureCursorVisible()

    @pyqtSlot(str)
    def update_status(self, text: str):
        """Show DR attempts inside the copilot history."""
        if "Trying" in text or "Critical" in text:
            cursor = self.response_browser.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertHtml(f"<div style='color: #ffffff; font-size: 11px; font-style: italic; margin-top: 5px;'>{text}</div>")
            self.response_browser.setTextCursor(cursor)
            self.response_browser.ensureCursorVisible()

    @pyqtSlot()
    def on_generation_done(self):
        cursor = self.response_browser.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml("</div></div><br/>")
        self.response_browser.setTextCursor(cursor)
        self.response_browser.ensureCursorVisible()

    @pyqtSlot()
    def clear_response(self):
        self.response_browser.clear()
        self.live_label.setText("")
        self.response_browser.setHtml("<div style='color: #64748b; font-style: italic;'>History cleared. Waiting for audio...</div>")

    def _on_export(self):
        import datetime
        from PyQt6.QtWidgets import QFileDialog
        content = self.response_browser.toPlainText()
        if not content.strip() or "Waiting" in content: return
        ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename, _ = QFileDialog.getSaveFileName(self, "Export History", f"History_{ts}.txt", "Text Files (*.txt)")
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"INTERVIEW SESSION - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*60 + "\n\n")
                f.write(content)
