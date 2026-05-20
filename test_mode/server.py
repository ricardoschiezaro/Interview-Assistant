"""
Test Mode local HTTP server.

Serves the AI interviewer page with the Groq API key injected,
so no manual configuration is needed in the browser.

Also detects available audio devices and reports WASAPI loopback status.
"""

import http.server
import socketserver
import webbrowser
import threading
import json
import os
import sys
import logging
from pathlib import Path

sys.path.insert(0, r'C:\pylibs')
from dotenv import load_dotenv

_root = Path(__file__).resolve().parent.parent
load_dotenv(_root / '.env')

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
PORT = 8765
_HTML_TEMPLATE = Path(__file__).parent / 'interviewer.html'


def _check_loopback() -> dict:
    """Check if WASAPI loopback is available."""
    try:
        import pyaudiowpatch as pyaudio  # type: ignore
        p = pyaudio.PyAudio()
        wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
        default_idx = wasapi_info["defaultOutputDevice"]
        default_dev = p.get_device_info_by_index(default_idx)
        found = False
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev.get("isLoopbackDevice") and dev["name"] == default_dev["name"]:
                found = True
                break
        p.terminate()
        return {"available": found, "device": default_dev.get("name", "Unknown")}
    except Exception as e:
        return {"available": False, "error": str(e)}


class _Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress default access log

    def do_GET(self):
        if self.path == '/':
            try:
                template = _HTML_TEMPLATE.read_text(encoding='utf-8')
                content = template.replace('{{GROQ_API_KEY}}', GROQ_API_KEY)
                self._respond(200, 'text/html; charset=utf-8', content.encode('utf-8'))
            except FileNotFoundError:
                self._respond(404, 'text/plain', b'interviewer.html not found')

        elif self.path == '/status':
            data = {
                'groq_key_ok': bool(GROQ_API_KEY),
                'loopback': _check_loopback(),
            }
            self._respond(200, 'application/json', json.dumps(data).encode())

        else:
            self._respond(404, 'text/plain', b'Not found')

    def _respond(self, code: int, content_type: str, body: bytes):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)


_server: socketserver.TCPServer | None = None
_thread: threading.Thread | None = None


def start(open_browser: bool = True) -> int:
    """Start the local test server. Returns the port number."""
    global _server, _thread

    if _server is not None:
        if open_browser:
            webbrowser.open(f'http://localhost:{PORT}')
        return PORT

    socketserver.TCPServer.allow_reuse_address = True
    _server = socketserver.TCPServer(('localhost', PORT), _Handler)

    _thread = threading.Thread(
        target=_server.serve_forever,
        daemon=True,
        name='TestModeServer',
    )
    _thread.start()
    logger.info("Test mode server started at http://localhost:%d", PORT)

    if open_browser:
        # Small delay so browser doesn't hit server before it's ready
        threading.Timer(0.4, lambda: webbrowser.open(f'http://localhost:{PORT}')).start()

    return PORT


def stop():
    """Stop the test mode server."""
    global _server
    if _server:
        _server.shutdown()
        _server = None
        logger.info("Test mode server stopped.")


if __name__ == '__main__':
    # Standalone: python -m test_mode.server
    logging.basicConfig(level=logging.INFO)
    print(f"Starting test interviewer at http://localhost:{PORT}")
    start(open_browser=True)
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        stop()
