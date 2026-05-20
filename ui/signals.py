"""
Thread-safe Qt signals for cross-thread UI updates.

All pipeline callbacks emit these signals; Qt ensures the actual
UI slot runs on the main thread even when emitted from a background thread.
"""

from PyQt6.QtCore import QObject, pyqtSignal


class AppSignals(QObject):
    """Central signal hub for the application."""

    # Groq streaming: each token emitted as it arrives
    token_received = pyqtSignal(str)

    # Groq: entire response stream completed
    generation_done = pyqtSignal()

    # STT + sanitizer: the (cleaned) transcript shown above the response
    question_received = pyqtSignal(str)

    # Generic status bar update
    status_changed = pyqtSignal(str)

    # Usage and provider stats
    usage_stats_received = pyqtSignal(int) # total_tokens
    provider_status_changed = pyqtSignal(str, str) # provider, status
