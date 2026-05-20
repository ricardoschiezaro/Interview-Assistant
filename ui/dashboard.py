from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from ui.profile_tab import ProfileTab
from ui.prompt_tab import PromptTab

class DashboardWindow(QMainWindow):
    start_session_requested = pyqtSignal(dict)

    def __init__(self, orchestrator, loop):
        super().__init__()
        self.setWindowTitle("Career & Interview Management Suite")
        self.resize(1100, 750)
        
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #1e1b4b, stop:1 #312e81);
            }
            #sidebar {
                background: rgba(30, 41, 59, 150);
                border-right: 1px solid rgba(255, 255, 255, 0.1);
                min-width: 70px;
                max-width: 70px;
            }
            #sidebar QPushButton {
                background: transparent;
                border: none;
                color: #94a3b8;
                font-size: 20px;
                padding: 15px;
                border-radius: 10px;
            }
            #sidebar QPushButton:hover {
                background: rgba(255, 255, 255, 0.05);
                color: #f8fafc;
            }
            #mainContent {
                background: rgba(255, 255, 255, 0.03);
                border-radius: 24px;
                margin: 10px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: rgba(255, 255, 255, 0.05);
                color: #94a3b8;
                padding: 8px 20px;
                margin: 5px;
                border-radius: 15px;
                font-weight: bold;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background: #f8fafc;
                color: #1e1b4b;
            }
            QLabel { color: #f8fafc; }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(5, 20, 5, 20)
        
        for icon in ["🏠", "💬", "👥", "📅", "⚙️"]:
            btn = QPushButton(icon)
            side_layout.addWidget(btn)
        side_layout.addStretch()
        layout.addWidget(sidebar)

        # Main Content Area
        content = QWidget()
        content.setObjectName("mainContent")
        content_layout = QVBoxLayout(content)
        
        header = QLabel("Career & Interview Management Suite")
        header.setStyleSheet("font-size: 22px; font-weight: bold; padding: 15px; color: #f8fafc;")
        content_layout.addWidget(header)

        self.tabs = QTabWidget()
        
        # Profile/Settings Tabs
        self.profile = ProfileTab()
        self.prompt = PromptTab()

        self.tabs.addTab(self.profile, "👤 Profile")
        self.tabs.addTab(self.prompt, "⚙️ Analysis")
        
        content_layout.addWidget(self.tabs)
        layout.addWidget(content)
