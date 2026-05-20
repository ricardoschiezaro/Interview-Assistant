from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QLabel, QTabWidget, QInputDialog, QTabBar
)
from PyQt6.QtCore import pyqtSlot, Qt, QSize
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QIcon
import datetime


def create_close_icon(color=QColor(255, 255, 255, 160)) -> QIcon:
    """Draw a clean, elegant, thin vector-style close 'X' icon."""
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    pen = QPen(color, 1.5)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    
    # Draw '✕' lines (slightly smaller and centered for a modern sleek look)
    painter.drawLine(5, 5, 11, 11)
    painter.drawLine(11, 5, 5, 11)
    
    painter.end()
    return QIcon(pixmap)

class EditableTabBar(QTabBar):
    """TabBar that allows renaming tabs on double-click."""
    def mouseDoubleClickEvent(self, event):
        index = self.tabAt(event.position().toPoint())
        if index >= 0:
            current_text = self.tabText(index)
            new_text, ok = QInputDialog.getText(
                self, "Rename Tab", "Enter new name:", 
                text=current_text
            )
            if ok and new_text:
                self.setTabText(index, new_text)
        super().mouseDoubleClickEvent(event)

class ScratchpadTab(QWidget):
    """Multi-tab note-taking area."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 10, 12, 10)
        self.main_layout.setSpacing(8)

        # Header row
        header_row = QHBoxLayout()
        header = QLabel("SCRATCHPAD")
        header.setObjectName("sectionHeader")
        header_row.addWidget(header)
        header_row.addStretch()

        add_btn = QPushButton("+ New Tab")
        add_btn.setObjectName("clearBtn")
        add_btn.setFixedSize(80, 22)
        add_btn.clicked.connect(lambda: self.add_new_tab())
        header_row.addWidget(add_btn)

        clear_btn = QPushButton("Clear Current")
        clear_btn.setObjectName("clearBtn")
        clear_btn.setFixedSize(100, 22)
        clear_btn.clicked.connect(self._clear_current)
        header_row.addWidget(clear_btn)

        self.main_layout.addLayout(header_row)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabBar(EditableTabBar())
        self.tab_widget.setTabsClosable(False)  # Using custom close buttons for perfect aesthetic control
        self.tab_widget.setStyleSheet("""
            QTabWidget {
                background-color: transparent !important;
                border: none !important;
            }
            QTabWidget::pane { 
                border: none !important;
                background-color: transparent !important;
                margin: 0px !important;
                padding: 0px !important;
            }
            QTabBar {
                background-color: transparent !important;
            }
            QTabBar::tab { 
                background: rgba(255, 255, 255, 0.03); 
                color: #cbd5e1; 
                padding: 6px 32px 6px 14px; 
                font-size: 11px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 4px;
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-bottom: none;
            }
            QTabBar::tab:selected { 
                background: rgba(255, 255, 255, 0.1); 
                color: #ffffff; 
                font-weight: bold; 
                border: 1.5px solid rgba(255, 255, 255, 0.2);
                border-bottom: none;
                padding: 6px 32px 6px 14px;
            }
            QTabBar::tab:hover:!selected {
                background: rgba(255, 255, 255, 0.07);
                color: #f8fafc;
                padding: 6px 32px 6px 14px;
            }
        """)
        
        self.main_layout.addWidget(self.tab_widget)
        
        # Add initial tab
        self.add_new_tab("General")

    def add_new_tab(self, name=None):
        if not name:
            name = f"Notes {self.tab_widget.count() + 1}"
            
        editor = QTextEdit()
        editor.setObjectName("scratchpad")
        editor.setPlaceholderText("Type your notes here...")
        
        index = self.tab_widget.addTab(editor, name)
        self.tab_widget.setCurrentWidget(editor)
        
        # Create a beautiful custom close button on the tab
        close_btn = QPushButton()
        close_btn.setIcon(create_close_icon())
        close_btn.setIconSize(QSize(16, 16))
        close_btn.setFixedSize(16, 16)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setToolTip("Delete this note")
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 8px;
                margin-right: 8px;
                margin-top: 1px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.15);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.25);
            }
        """)
        close_btn.clicked.connect(lambda _, w=editor: self.close_tab_by_widget(w))
        self.tab_widget.tabBar().setTabButton(index, QTabBar.ButtonPosition.RightSide, close_btn)

    def close_tab_by_widget(self, widget):
        index = self.tab_widget.indexOf(widget)
        if index >= 0:
            self._close_tab(index)

    @pyqtSlot(int)
    def _close_tab(self, index):
        self.tab_widget.removeTab(index)
        if self.tab_widget.count() == 0:
            self.add_new_tab("General")

    @pyqtSlot()
    def _clear_current(self):
        current = self.tab_widget.currentWidget()
        if isinstance(current, QTextEdit):
            current.clear()

    @pyqtSlot()
    def _insert_timestamp(self):
        current = self.tab_widget.currentWidget()
        if isinstance(current, QTextEdit):
            ts = datetime.datetime.now().strftime("[%H:%M:%S] ")
            cursor = current.textCursor()
            cursor.insertText(ts)
            current.setTextCursor(cursor)

    def get_notes(self) -> str:
        notes = []
        for i in range(self.tab_widget.count()):
            title = self.tab_widget.tabText(i)
            content = self.tab_widget.widget(i).toPlainText()
            notes.append(f"=== {title} ===\n{content}")
        return "\n\n".join(notes)
