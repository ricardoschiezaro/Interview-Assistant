"""
Profile Tab — upload CV and Job Description.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFileDialog, QSplitter, QSizePolicy, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QColor

from core.profile import get_profile, extract_text_from_pdf


class ProfileTab(QWidget):
    """Tab for uploading CV and Job Description."""

    save_requested = pyqtSignal()   # emitted when user saves

    def __init__(self, parent=None):
        super().__init__(parent)
        self._profile = get_profile()
        self._setup_ui()
        self._load_existing()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        # ── Info banner ───────────────────────────────────────────────────────
        banner = QLabel(
            "Upload your CV and the Job Description so the AI can "
            "answer using your real experience and match the role's language."
        )
        banner.setObjectName("infoBanner")
        banner.setWordWrap(True)
        layout.addWidget(banner)

        # ── Splitter: CV on top, JD on bottom ────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setChildrenCollapsible(False)

        splitter.addWidget(self._make_section(
            "YOUR CV / RESUME",
            "cv",
            "Paste your resume text here, or click 'Load PDF / TXT'…",
        ))
        splitter.addWidget(self._make_section(
            "JOB DESCRIPTION",
            "jd",
            "Paste the job description for the role you're interviewing for…",
        ))
        splitter.setSizes([300, 200])
        layout.addWidget(splitter)

        # ── Save button ───────────────────────────────────────────────────────
        save_row = QHBoxLayout()
        self.status_label = QLabel("")
        self.status_label.setObjectName("profileStatus")
        save_row.addWidget(self.status_label)
        save_row.addStretch()

        save_btn = QPushButton("Save Profile")
        save_btn.setObjectName("saveProfileBtn")
        save_btn.setFixedHeight(32)
        save_btn.clicked.connect(self._save)
        save_row.addWidget(save_btn)

        layout.addLayout(save_row)

    def _make_section(self, title: str, field: str, placeholder: str) -> QWidget:
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(6)

        header_row = QHBoxLayout()

        lbl = QLabel(title)
        lbl.setObjectName("sectionHeader")
        header_row.addWidget(lbl)
        header_row.addStretch()

        char_lbl = QLabel("0 chars")
        char_lbl.setObjectName("charCount")
        char_lbl.setFixedWidth(70)
        header_row.addWidget(char_lbl)

        load_btn = QPushButton("Load PDF / TXT")
        load_btn.setObjectName("clearBtn")
        load_btn.setFixedHeight(22)
        load_btn.clicked.connect(lambda: self._load_file(field))
        header_row.addWidget(load_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("clearBtn")
        clear_btn.setFixedHeight(22)
        clear_btn.clicked.connect(lambda: self._clear_field(field))
        header_row.addWidget(clear_btn)

        vbox.addLayout(header_row)

        editor = QTextEdit()
        editor.setObjectName(f"profileEditor_{field}")
        editor.setPlaceholderText(placeholder)
        editor.setAcceptRichText(False)

        # Track char count
        def _update_count(text="", lbl=char_lbl):
            count = len(editor.toPlainText())
            lbl.setText(f"{count:,} chars")
            lbl.setStyleSheet("color: #ffffff;")

        editor.textChanged.connect(_update_count)
        vbox.addWidget(editor)

        # Store references
        setattr(self, f"_editor_{field}", editor)
        setattr(self, f"_count_{field}", char_lbl)

        return container

    def _load_existing(self):
        self._editor_cv.setPlainText(self._profile.cv_text)
        self._editor_jd.setPlainText(self._profile.jd_text)

    # ── Slots ─────────────────────────────────────────────────────────────────

    @pyqtSlot()
    def _save(self):
        self._profile.cv_text = self._editor_cv.toPlainText()
        self._profile.jd_text = self._editor_jd.toPlainText()
        self._profile.save()
        self.status_label.setText("Profile saved — responses will use your CV & JD.")
        self.status_label.setStyleSheet("color: #ffffff; font-size: 11px;")
        self.save_requested.emit()

    def _load_file(self, field: str):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open CV or Job Description",
            "", "Documents (*.pdf *.txt *.md);;All Files (*)"
        )
        if not path:
            return
        try:
            if path.lower().endswith(".pdf"):
                text = extract_text_from_pdf(path)
            else:
                with open(path, encoding="utf-8", errors="replace") as f:
                    text = f.read()

            editor: QTextEdit = getattr(self, f"_editor_{field}")
            editor.setPlainText(text)
            self.status_label.setText(f"Loaded: {path.split('/')[-1].split(chr(92))[-1]}")
            self.status_label.setStyleSheet("color: #ffffff; font-size: 11px;")
        except Exception as exc:
            self.status_label.setText(f"Error: {exc}")
            self.status_label.setStyleSheet("color: #ffffff; font-size: 11px;")

    def _clear_field(self, field: str):
        editor: QTextEdit = getattr(self, f"_editor_{field}")
        editor.clear()
