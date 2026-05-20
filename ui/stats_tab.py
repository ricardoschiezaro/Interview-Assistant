"""
Usage and System Statistics Tab.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont

class StatsTab(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("SYSTEM HEALTH & USAGE")
        title.setObjectName("sectionHeader")
        layout.addWidget(title)

        # Scroll Area for stats
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        self.container_layout = QVBoxLayout(container)
        self.container_layout.setSpacing(20)

        # ── Groq Usage ────────────────────────────────────────────────────────
        self.groq_card = self._create_card("Groq (Free Tier)", "100k tokens/day limit")
        self.groq_bar = QProgressBar()
        self.groq_bar.setRange(0, 100000)
        self.groq_bar.setValue(0)
        self.groq_bar.setTextVisible(True)
        self.groq_bar.setFormat("%v / %m tokens")
        self.groq_bar.setStyleSheet("""
            QProgressBar {
                background: rgba(30, 41, 59, 150);
                border: 1px solid rgba(100, 116, 139, 0.3);
                border-radius: 4px;
                text-align: center;
                color: white;
                height: 20px;
            }
            QProgressBar::chunk {
                background: rgba(255, 255, 255, 0.45);
                border-radius: 3px;
            }
        """)
        self.groq_card.layout().addWidget(self.groq_bar)
        self.container_layout.addWidget(self.groq_card)

        # ── Providers Status ──────────────────────────────────────────────────
        status_card = self._create_card("Provider Status", "Real-time connectivity")
        self.status_layout = QVBoxLayout()
        self.providers = {
            "GROQ": self._create_status_row("Groq Cloud", "Online"),
            "CEREBRAS": self._create_status_row("Cerebras Inference", "Online"),
            "OPENROUTER": self._create_status_row("OpenRouter", "Online"),
            "GEMINI": self._create_status_row("Google Gemini", "Online"),
        }
        for row in self.providers.values():
            self.status_layout.addLayout(row)
        status_card.layout().addLayout(self.status_layout)
        self.container_layout.addWidget(status_card)

        # ── Session Info ──────────────────────────────────────────────────────
        session_card = self._create_card("Current Session", "Stats for this interview")
        self.token_label = QLabel("Tokens used: 0")
        self.token_label.setStyleSheet("color: #e2e8f0; font-size: 13px;")
        session_card.layout().addWidget(self.token_label)
        
        self.container_layout.addWidget(session_card)

        self.container_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

    def _create_card(self, title, subtitle):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: rgba(30, 41, 59, 120);
                border: 1px solid rgba(100, 116, 139, 0.2);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        card_layout = QVBoxLayout(card)
        
        t = QLabel(title)
        t.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 14px; border: none;")
        card_layout.addWidget(t)
        
        st = QLabel(subtitle)
        st.setStyleSheet("color: #94a3b8; font-size: 11px; border: none; margin-bottom: 5px;")
        card_layout.addWidget(st)
        
        return card

    def _create_status_row(self, name, status):
        row = QHBoxLayout()
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet("color: #cbd5e1; font-size: 12px; border: none;")
        status_lbl = QLabel(status)
        status_lbl.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 11px; border: none;")
        row.addWidget(name_lbl)
        row.addStretch()
        row.addWidget(status_lbl)
        return row

    @pyqtSlot(int)
    def update_usage(self, tokens):
        self.groq_bar.setValue(min(tokens, 100000))
        self.token_label.setText(f"Tokens used: {tokens}")

    @pyqtSlot(str, str)
    def update_provider_status(self, provider, status):
        if provider in self.providers:
            # Update status label in row
            # (Simplification: just finding the label by index)
            layout = self.providers[provider]
            lbl = layout.itemAt(2).widget()
            lbl.setText(status)
            if "Offline" in status or "Limit" in status:
                lbl.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 11px; border: none;")
            else:
                lbl.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 11px; border: none;")
