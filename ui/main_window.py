"""

Main Application Window.



Frameless, always-on-top, translucent dark overlay.

"""



import logging

from PyQt6.QtWidgets import (

    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,

    QLabel, QPushButton, QTabWidget, QComboBox, QSizeGrip,

    QStatusBar,

)

from PyQt6.QtCore import Qt, QPoint, pyqtSlot, QSize, QEvent, QPointF

from PyQt6.QtGui import QFont, QIcon, QColor, QPixmap, QPainter, QPen, QPainterPath



from ui.copilot_tab import CopilotTab

from ui.scratchpad_tab import ScratchpadTab

from ui.profile_tab import ProfileTab

from ui.prompt_tab import PromptTab

from ui.signals import AppSignals

from core.event_loop import get_event_loop, run_coroutine



logger = logging.getLogger(__name__)





def create_vector_icon(icon_type: str, color=QColor(255, 255, 255)) -> QIcon:
    """Dynamically draw modern, clean white vector-style icons matching the glassmorphic theme."""
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    pen = QPen(color, 2)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    
    if icon_type == "copilot":
        # Draw a gorgeous, modern, clean vector square-shaped robot head in white
        # Head (sharp perfect square with minimal rounding)
        painter.drawRoundedRect(8, 8, 16, 16, 1.5, 1.5)
        # Left Ear (sharp rectangle)
        painter.drawRect(5, 13, 3, 6)
        # Right Ear (sharp rectangle)
        painter.drawRect(24, 13, 3, 6)
        # Antenna Stem
        painter.drawLine(16, 8, 16, 4)
        # Antenna Tip (sharp perfect square)
        painter.drawRect(15, 2, 2, 2)
        # Left Eye (sharp square)
        painter.drawRect(11, 12, 3, 3)
        # Right Eye (sharp square)
        painter.drawRect(18, 12, 3, 3)
        # Mouth (sleek horizontal line)
        painter.drawLine(12, 19, 20, 19)
        
    elif icon_type == "prompt":
        # Draw a modern, sleek vector command line prompt symbol (> _)
        # Chevron '>'
        painter.drawLine(8, 9, 16, 16)
        painter.drawLine(16, 16, 8, 23)
        # Flashing cursor/underline '_'
        painter.drawLine(19, 23, 27, 23)
            
    elif icon_type == "profile":
        # Profile outline
        painter.drawEllipse(12, 7, 8, 8)
        painter.drawArc(6, 18, 20, 14, 0 * 16, 180 * 16)
        painter.drawLine(6, 25, 26, 25)
        
    elif icon_type == "scratchpad":
        # Document outline with lines and folded corner
        painter.drawPolygon([
            QPointF(8, 6),
            QPointF(18, 6),
            QPointF(24, 12),
            QPointF(24, 26),
            QPointF(8, 26)
        ])
        painter.drawLine(18, 6, 18, 12)
        painter.drawLine(18, 12, 24, 12)
        painter.drawLine(12, 17, 20, 17)
        painter.drawLine(12, 22, 20, 22)
        
    painter.end()
    return QIcon(pixmap)


class TitleBar(QWidget):

    """Custom drag-able title bar for the frameless window."""



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

        layout.setSpacing(6)



        # Icon + title

        icon_label = QLabel("✦")

        icon_label.setObjectName("titleIcon")

        layout.addWidget(icon_label)



        title = QLabel("Interview Copilot")

        title.setObjectName("titleText")

        layout.addWidget(title)

        layout.addStretch()



        # Status indicator

        self.status_dot = QLabel("●")

        self.status_dot.setObjectName("statusDot")

        self.status_dot.setToolTip("Pipeline status")

        layout.addWidget(self.status_dot)



        # Window controls

        for sym, tip, slot in [

            ("—", "Minimize", self._minimize),

            ("✕", "Close", self._close),

        ]:

            btn = QPushButton(sym)

            btn.setObjectName("winControlBtn")

            btn.setFixedSize(28, 28)

            btn.setToolTip(tip)

            btn.clicked.connect(slot)

            layout.addWidget(btn)



    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self._drag_pos = event.globalPosition().toPoint() - self._win.frameGeometry().topLeft()



    def mouseMoveEvent(self, event):

        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:

            self._win.move(event.globalPosition().toPoint() - self._drag_pos)



    def mouseReleaseEvent(self, event):

        self._drag_pos = None



    def _minimize(self):

        self._win.showMinimized()



    def _close(self):

        self._win.close()



    def set_status_color(self, color: str):

        self.status_dot.setStyleSheet(f"color: {color};")





class MainWindow(QMainWindow):

    """Primary application window."""



    def __init__(self):

        super().__init__()

        self._signals = AppSignals()

        self._pipeline = None

        self._is_active = False



        self._configure_window()

        self._setup_ui()

        self._connect_signals()

        self._apply_stylesheet()



    # ── Window Configuration ──────────────────────────────────────────────────



    def _configure_window(self):

        self.setWindowFlags(

            Qt.WindowType.FramelessWindowHint |

            Qt.WindowType.WindowStaysOnTopHint |

            Qt.WindowType.Tool          # hides from taskbar on Windows

        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setWindowOpacity(0.88)

        self.setMinimumSize(600, 650)
        self.resize(800, 850)
        self.setWindowTitle("Interview Copilot")



    # ── UI Construction ───────────────────────────────────────────────────────



    def _setup_ui(self):

        # Root container (gets the opaque background via stylesheet)

        self.root = QWidget()

        self.root.setObjectName("rootContainer")

        self.setCentralWidget(self.root)



        self.root_layout = QVBoxLayout(self.root)

        self.root_layout.setContentsMargins(5, 5, 5, 5) # Margin for resizing

        self.root_layout.setSpacing(0)



        # Title bar

        self.title_bar = TitleBar(self)

        self.root_layout.addWidget(self.title_bar)



        # Toolbar row

        toolbar = self._build_toolbar()

        self.root_layout.addWidget(toolbar)



        # Tabs

        self.tabs = QTabWidget()

        self.tabs.setObjectName("mainTabs")

        self.copilot_tab = CopilotTab()

        self.scratchpad_tab = ScratchpadTab()

        self.profile_tab = ProfileTab()

        self.profile_tab.save_requested.connect(self._on_profile_saved)

        

        self.prompt_tab = PromptTab()

        self.prompt_tab.save_requested.connect(self._on_profile_saved)



        copilot_icon = create_vector_icon("copilot")
        prompt_icon = create_vector_icon("prompt")
        profile_icon = create_vector_icon("profile")
        scratchpad_icon = create_vector_icon("scratchpad")

        self.tabs.addTab(self.copilot_tab, copilot_icon, " Copilot")

        self.tabs.addTab(self.prompt_tab, prompt_icon, " Prompt")

        self.tabs.addTab(self.profile_tab, profile_icon, " Profile")

        self.tabs.addTab(self.scratchpad_tab, scratchpad_icon, " Scratchpad")

        self.root_layout.addWidget(self.tabs)



        # Status bar

        self.status_bar = QStatusBar()

        self.status_bar.setObjectName("appStatusBar")

        self.status_bar.showMessage("● Ready — press Start to begin")

        self.setStatusBar(self.status_bar)



        # Allow mouse tracking for custom resizing

        self.setMouseTracking(True)

        self.root.setMouseTracking(True)

        self._resizing = False

        self._resize_edge = None

        self._MARGIN = 8



    def _get_edge(self, pos):

        w, h = self.width(), self.height()

        m = 10 # detection margin

        

        lx, ly = pos.x(), pos.y()

        

        left = lx < m

        right = lx > w - m

        top = ly < m

        bottom = ly > h - m

        

        if top and left: return "topleft"

        if top and right: return "topright"

        if bottom and left: return "bottomleft"

        if bottom and right: return "bottomright"

        if left: return "left"

        if right: return "right"

        if top: return "top"

        if bottom: return "bottom"

        return None



    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            edge = self._get_edge(event.position().toPoint())

            if edge:

                self._resizing = True

                self._resize_edge = edge

                self._press_pos = event.globalPosition().toPoint()

                self._press_geo = self.geometry()

            else:

                super().mousePressEvent(event)



    def mouseMoveEvent(self, event):

        pos = event.position().toPoint()

        if not self._resizing:

            edge = self._get_edge(pos)

            if edge in ["left", "right"]: self.setCursor(Qt.CursorShape.SizeHorCursor)

            elif edge in ["top", "bottom"]: self.setCursor(Qt.CursorShape.SizeVerCursor)

            elif edge in ["topleft", "bottomright"]: self.setCursor(Qt.CursorShape.SizeFDiagCursor)

            elif edge in ["topright", "bottomleft"]: self.setCursor(Qt.CursorShape.SizeBDiagCursor)

            else: self.setCursor(Qt.CursorShape.ArrowCursor)

        else:

            diff = event.globalPosition().toPoint() - self._press_pos

            new_geo = QSize(self._press_geo.width(), self._press_geo.height())

            rect = self.geometry()

            

            if "right" in self._resize_edge:

                rect.setWidth(max(self.minimumWidth(), self._press_geo.width() + diff.x()))

            if "bottom" in self._resize_edge:

                rect.setHeight(max(self.minimumHeight(), self._press_geo.height() + diff.y()))

            if "left" in self._resize_edge:

                w = max(self.minimumWidth(), self._press_geo.width() - diff.x())

                rect.setX(self._press_geo.right() - w)

                rect.setWidth(w)

            if "top" in self._resize_edge:

                h = max(self.minimumHeight(), self._press_geo.height() - diff.y())

                rect.setY(self._press_geo.bottom() - h)

                rect.setHeight(h)

                

            self.setGeometry(rect)



    def mouseReleaseEvent(self, event):

        self._resizing = False

        self.setCursor(Qt.CursorShape.ArrowCursor)



    def _build_toolbar(self) -> QWidget:

        bar = QWidget()

        bar.setObjectName("toolbar")

        layout = QHBoxLayout(bar)

        layout.setContentsMargins(12, 6, 12, 6)

        layout.setSpacing(8)



        # Source selector

        src_label = QLabel("Source:")

        src_label.setObjectName("toolLabel")

        layout.addWidget(src_label)



        self.source_combo = QComboBox()

        self.source_combo.setObjectName("sourceCombo")

        self.source_combo.addItems(["🎙️ Microphone", "🖥️ System Audio", "🎧 Both (Hybrid)"])

        self.source_combo.currentIndexChanged.connect(self._on_source_changed)

        layout.addWidget(self.source_combo)



        # Auto-Correct toggle

        from PyQt6.QtWidgets import QCheckBox

        self.sanitize_check = QCheckBox("✨ Auto-Correct")

        self.sanitize_check.setObjectName("sanitizeCheck")

        self.sanitize_check.setToolTip("Enable Cloudflare technical term correction")

        self.sanitize_check.setChecked(True)

        self.sanitize_check.stateChanged.connect(self._on_sanitize_toggled)

        layout.addWidget(self.sanitize_check)



        # Language toggle: EN ↔ PT

        from core.profile import get_profile

        profile = get_profile()

        init_lang = profile.language if profile.language in ["en", "pt"] else "pt"

        labels = {"en": "🇬🇧 EN", "pt": "🇧🇷 PT"}

        obj_names = {"en": "langBtnEN", "pt": "langBtnPT"}

        

        self.lang_btn = QPushButton(labels[init_lang])

        self.lang_btn.setObjectName(obj_names[init_lang])

        self.lang_btn.setToolTip("Toggle between English and Portuguese transcription")

        self.lang_btn.setFixedWidth(78)

        self.lang_btn.clicked.connect(self._on_lang_toggle)

        layout.addWidget(self.lang_btn)



        layout.addStretch()



        # Opacity slider label

        opacity_label = QLabel("Opacity:")

        opacity_label.setObjectName("toolLabel")

        layout.addWidget(opacity_label)



        from PyQt6.QtWidgets import QSlider

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)

        self.opacity_slider.setObjectName("opacitySlider")

        self.opacity_slider.setRange(0, 100)

        self.opacity_slider.setValue(88)

        self.opacity_slider.setFixedWidth(80)

        self.opacity_slider.valueChanged.connect(

            lambda v: self.setWindowOpacity(v / 100)

        )

        layout.addWidget(self.opacity_slider)



        layout.addStretch()



        # Clear history button

        self.clear_history_btn = QPushButton("🗑️ Clear")

        self.clear_history_btn.setObjectName("toolBtn")

        self.clear_history_btn.setToolTip("Clear conversation history")

        self.clear_history_btn.clicked.connect(self._on_clear_history)

        layout.addWidget(self.clear_history_btn)



        # Start/Stop button

        self.toggle_btn = QPushButton("▶ Start")

        self.toggle_btn.setObjectName("startBtn")

        self.toggle_btn.setFixedWidth(90)

        self.toggle_btn.clicked.connect(self._toggle_pipeline)

        layout.addWidget(self.toggle_btn)



        return bar



    # ── Signal Wiring ─────────────────────────────────────────────────────────



    def _connect_signals(self):

        self._signals.token_received.connect(self.copilot_tab.append_token)

        self._signals.generation_done.connect(self.copilot_tab.on_generation_done)

        self._signals.question_received.connect(self.copilot_tab.set_question)

        self._signals.status_changed.connect(self._update_status)

        # Tab signals are connected in _setup_ui



    # ── Pipeline Control ──────────────────────────────────────────────────────



    @pyqtSlot()

    def _toggle_pipeline(self):

        if self._is_active:

            self._stop_pipeline()

        else:

            self._start_pipeline()



    def _start_pipeline(self):

        from pipeline.orchestrator import Orchestrator



        loop = get_event_loop()



        self._pipeline = Orchestrator(

            on_token=self._signals.token_received.emit,

            on_done=self._signals.generation_done.emit,

            on_question=self._signals.question_received.emit,

            on_status=self._signals.status_changed.emit,

            on_usage=self._signals.usage_stats_received.emit,

            on_provider=self._signals.provider_status_changed.emit,

            loop=loop,

            use_sanitizer=self.sanitize_check.isChecked(),

        )

        # Set initial source based on UI selection

        mapping = {0: "mic", 1: "system", 2: "both"}

        source = mapping.get(self.source_combo.currentIndex(), "mic")

        self._pipeline.set_audio_source(source)

        

        run_coroutine(self._pipeline.start())

        self._is_active = True

        self.toggle_btn.setText("⏹ Stop")

        self.toggle_btn.setObjectName("stopBtn")

        self.toggle_btn.setStyle(self.toggle_btn.style())  # force re-style

        self.title_bar.set_status_color("#22c55e")

        logger.info("Pipeline started from UI.")



    def _stop_pipeline(self):
        if self._pipeline:
            run_coroutine(self._pipeline.stop())
        self._is_active = False
        self.toggle_btn.setText("▶ Start")
        self.toggle_btn.setObjectName("startBtn")
        self.toggle_btn.setStyle(self.toggle_btn.style())
        self.title_bar.set_status_color("#94a3b8")
        logger.info("Pipeline stopped from UI.")

    @pyqtSlot(int)
    def _on_source_changed(self, index: int):
        mapping = {0: "mic", 1: "system", 2: "both"}
        source = mapping.get(index, "mic")
        if self._pipeline:
            self._pipeline.set_audio_source(source)

    @pyqtSlot(int)
    def _on_sanitize_toggled(self, state: int):
        use_it = (state == 2) # 2 is Checked
        if self._pipeline:
            self._pipeline.set_use_sanitizer(use_it)

    @pyqtSlot()
    def _on_clear_history(self):
        self.copilot_tab.clear_response()
        if self._pipeline:
            self._pipeline.clear_history()

    @pyqtSlot()
    def _on_lang_toggle(self):
        """Cycle language: EN → PT → EN."""
        from core.profile import get_profile
        profile = get_profile()
        
        # Determine current state (handling 'auto' legacy)
        current = profile.language if profile.language in ["en", "pt"] else "pt"
        
        cycle = {"en": "pt", "pt": "en"}
        labels = {"en": "🇬🇧 EN", "pt": "🇧🇷 PT"}
        obj_names = {"en": "langBtnEN", "pt": "langBtnPT"}
        
        new_lang = cycle[current]
        profile.set_language(new_lang)
        
        self.lang_btn.setText(labels[new_lang])
        self.lang_btn.setObjectName(obj_names[new_lang])
        self.lang_btn.setStyle(self.lang_btn.style())
        if self._pipeline:
            self._pipeline.trigger_stt_reconnect()
            self._pipeline.clear_history() # Reset AI context to avoid language bias
            self.statusBar().showMessage(f"Language switched to {new_lang.upper()}", 2000)
        self.status_bar.showMessage(f"Language forced: {new_lang.upper()}")

    @pyqtSlot()
    def _on_profile_saved(self):
        """Profile updated — clear Groq history so new context takes effect."""
        if self._pipeline:
            self._pipeline.clear_history()
        self.status_bar.showMessage("Profile saved — AI will now use your CV & JD for answers.")

    # ── Status ────────────────────────────────────────────────────────────────

    @pyqtSlot(str)
    def _update_status(self, message: str):
        # Color the dot based on status keywords
        if "Error" in message or "⚠️" in message:
            self.title_bar.set_status_color("#ef4444")
        elif "Generating" in message or "🤖" in message:
            self.title_bar.set_status_color("#3b82f6")
        elif "Listening" in message or "🎙️" in message:
            self.title_bar.set_status_color("#22c55e")
        elif "Stopped" in message or "⏹" in message:
            self.title_bar.set_status_color("#94a3b8")

    def _apply_stylesheet(self):
        self.setStyleSheet("""
            /* ── Root ─────────────────────────────────────────────────── */
            #rootContainer {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 rgba(20, 30, 55, 255), 
                    stop:0.5 rgba(15, 23, 42, 255), 
                    stop:1 rgba(40, 20, 60, 255));
                border-radius: 16px;
                border: 1.5px solid rgba(255, 255, 255, 0.16);
            }

            /* ── Title Bar ────────────────────────────────────────────── */
            #titleBar {
                background: rgba(255, 255, 255, 0.04);
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            }
            #titleIcon { font-size: 16px; color: #ffffff; }
            #titleText {
                color: #ffffff;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 0.5px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
            #statusDot {
                color: #94a3b8;
                font-size: 10px;
            }
            #winControlBtn {
                background: transparent;
                color: #94a3b8;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }
            #winControlBtn:hover { background: rgba(239,68,68,0.25); color: #f87171; }

            /* ── Toolbar ──────────────────────────────────────────────── */
            #toolbar {
                background: rgba(255, 255, 255, 0.02);
                border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            }
            #toolLabel {
                color: #ffffff;
                font-size: 11px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-weight: bold;
            }
            #sourceCombo {
                background: rgba(255, 255, 255, 0.06);
                color: #f8fafc;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 8px;
                padding: 4px 10px;
                font-size: 12px;
                min-width: 140px;
            }
            #sourceCombo QAbstractItemView {
                background: #0f172a;
                color: #f8fafc;
                selection-background-color: rgba(59, 130, 246, 0.4);
                outline: none;
            }
            #sanitizeCheck {
                color: #f8fafc;
                font-size: 11px;
                font-weight: bold;
                spacing: 5px;
            }
            #sanitizeCheck::indicator {
                width: 14px;
                height: 14px;
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 4px;
            }
            #sanitizeCheck::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3b82f6, stop:1 #8b5cf6);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            #opacitySlider {
                height: 24px;
                min-width: 90px;
            }
            #opacitySlider::groove:horizontal {
                background: rgba(255, 255, 255, 0.15);
                height: 6px;
                border-radius: 3px;
            }
            #opacitySlider::handle:horizontal {
                background: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.8);
                width: 16px;
                height: 16px;
                border-radius: 8px;
                margin: -5px 0;
            }
            #opacitySlider::handle:horizontal:hover {
                background: rgba(255, 255, 255, 0.85);
                border: 1px solid #ffffff;
            }
            #toolBtn {
                background: rgba(255, 255, 255, 0.12);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 8px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: bold;
            }
            #toolBtn:hover { background: rgba(255, 255, 255, 0.25); }

            /* Language toggle buttons */
            #langBtn {
                background: rgba(255, 255, 255, 0.12);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 8px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: bold;
            }
            #langBtn:hover { background: rgba(255, 255, 255, 0.25); }
            #langBtnEN {
                background: rgba(255, 255, 255, 0.15);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.35);
                border-radius: 8px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: bold;
            }
            #langBtnEN:hover { background: rgba(255, 255, 255, 0.3); }
            #langBtnPT {
                background: rgba(255, 255, 255, 0.15);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.35);
                border-radius: 8px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: bold;
            }
            #langBtnPT:hover { background: rgba(255, 255, 255, 0.3); }

            #startBtn {
                background: rgba(255, 255, 255, 0.18);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.35);
                border-radius: 8px;
                padding: 5px 14px;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.3px;
            }
            #startBtn:hover {
                background: rgba(255, 255, 255, 0.32);
                border-color: rgba(255, 255, 255, 0.5);
            }
            #stopBtn {
                background: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 8px;
                padding: 5px 14px;
                font-size: 12px;
                font-weight: 700;
            }
            #stopBtn:hover {
                background: rgba(239, 68, 68, 0.3);
                border-color: rgba(239, 68, 68, 0.5);
            }

            /* ── Tabs ─────────────────────────────────────────────────── */
            #mainTabs {
                background: transparent;
                border: none;
            }
            QTabBar::tab {
                background: rgba(255, 255, 255, 0.03);
                color: #94a3b8;
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 6px 20px;
                font-size: 13px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                border: 1.5px solid rgba(255, 255, 255, 0.2);
                border-bottom: none;
                font-weight: 700;
            }
            QTabBar::tab:hover:!selected {
                background: rgba(255, 255, 255, 0.07);
                color: #cbd5e1;
            }
            QTabWidget::pane {
                border: none;
                background: transparent;
            }

            /* ── Content widgets ─────────────────────────────────────── */
            #sectionHeader {
                color: #ffffff;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1.5px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                text-transform: uppercase;
            }
            #questionLabel {
                color: #ffffff;
                font-size: 13px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-style: italic;
                padding: 6px 0;
            }
            #divider {
                background: rgba(255, 255, 255, 0.15);
            }
            #clearBtn {
                background: rgba(255, 255, 255, 0.12);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 6px;
                font-size: 11px;
                padding: 1px 6px;
                font-weight: bold;
            }
            #clearBtn:hover { background: rgba(255, 255, 255, 0.25); }

            #responseBrowser {
                background: rgba(15, 23, 42, 100);
                color: #e2e8f0;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                padding: 12px;
                font-size: 15px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                line-height: 1.6;
                selection-background-color: rgba(59, 130, 246, 0.35);
            }
            #scratchpad {
                background: rgba(15, 23, 42, 100);
                color: #e2e8f0;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                padding: 12px;
                font-size: 15px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                selection-background-color: rgba(59, 130, 246, 0.35);
            }
            #profileEditor_cv, #profileEditor_jd, #promptEditor {
                background: rgba(15, 23, 42, 100);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                padding: 12px;
                font-size: 14px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                selection-background-color: rgba(255, 255, 255, 0.25);
            }
            #saveProfileBtn, #savePromptBtn, #resetPromptBtn {
                background: rgba(255, 255, 255, 0.15);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                padding: 5px 18px;
                font-size: 13px;
                font-weight: bold;
            }
            #saveProfileBtn:hover, #savePromptBtn:hover, #resetPromptBtn:hover {
                background: rgba(255, 255, 255, 0.28);
                border-color: rgba(255, 255, 255, 0.45);
            }
            #infoBanner {
                color: #ffffff;
                font-size: 12px;
                font-style: italic;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
            #charCount {
                color: #ffffff !important;
                font-size: 10px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.02);
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.15);
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

            /* ── Status Bar ───────────────────────────────────────────── */
            #appStatusBar {
                background: rgba(255, 255, 255, 0.04);
                color: #94a3b8;
                border-top: 1px solid rgba(255, 255, 255, 0.08);
                font-size: 11px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                border-bottom-left-radius: 16px;
                border-bottom-right-radius: 16px;
            }
            /* ── Profile Tab ──────────────────────────────────────────── */
            #infoBanner {
                background: rgba(59, 130, 246, 0.1);
                color: #93c5fd;
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 11px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
            QTextEdit[objectName^="profileEditor"] {
                background: rgba(15, 23, 42, 100);
                color: #e2e8f0;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                padding: 12px;
                font-size: 12px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                selection-background-color: rgba(59, 130, 246, 0.35);
            }
            #charCount {
                color: #64748b;
                font-size: 10px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
            #profileStatus {
                font-size: 11px;
                color: #64748b;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
            #saveProfileBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #8b5cf6);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 8px;
                padding: 5px 16px;
                font-size: 12px;
                font-weight: 700;
            }
            #saveProfileBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb, stop:1 #7c3aed);
            }

            /* ── Prompt Tab ───────────────────────────────────────────── */
            QTextEdit#promptEditor {
                background: rgba(15, 23, 42, 100);
                color: #e2e8f0;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                padding: 12px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
            #promptStatus {
                font-size: 11px;
                color: #64748b;
            }
            #savePromptBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10b981, stop:1 #06b6d4);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 8px;
                padding: 6px 16px;
                font-size: 12px;
                font-weight: 700;
            }
            #savePromptBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #059669, stop:1 #0891b2);
            }
            #resetPromptBtn {
                background: rgba(255, 255, 255, 0.05);
                color: #94a3b8;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 11px;
            }
            #resetPromptBtn:hover {
                background: rgba(255, 255, 255, 0.15);
                color: #f8fafc;
            }
        """)

    # ── Cleanup ───────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        if self._is_active:
            self._stop_pipeline()
        event.accept()
