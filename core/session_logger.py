import json
import os
from datetime import datetime

SESSION_LOGS_DIR = "sessions"

class SessionLogger:
    def __init__(self):
        if not os.path.exists(SESSION_LOGS_DIR):
            os.makedirs(SESSION_LOGS_DIR)
        self.current_log = []
        self.company = "Unknown"

    def start_session(self, company):
        self.company = company
        self.current_log = []

    def log_interaction(self, speaker, text):
        self.current_log.append({
            "timestamp": datetime.now().isoformat(),
            "speaker": speaker,
            "text": text
        })

    def save_session(self):
        filename = f"{self.company}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(SESSION_LOGS_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.current_log, f, indent=4, ensure_ascii=False)
        return path

    def get_transcript_text(self):
        lines = []
        for entry in self.current_log:
            lines.append(f"{entry['speaker']}: {entry['text']}")
        return "\n".join(lines)
