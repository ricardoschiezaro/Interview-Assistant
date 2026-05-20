"""
Asyncio + Qt integration using a QTimer-driven event loop tick.
This allows asyncio tasks to run on the main thread alongside the Qt event loop,
or we use a dedicated thread for the asyncio loop with thread-safe callbacks.
"""

import asyncio
import logging
import threading
from PyQt6.QtCore import QTimer

logger = logging.getLogger(__name__)

# The global asyncio event loop that runs in a background daemon thread.
_background_loop: asyncio.AbstractEventLoop | None = None
_loop_thread: threading.Thread | None = None


def get_event_loop() -> asyncio.AbstractEventLoop:
    """Return the shared background asyncio event loop."""
    global _background_loop
    if _background_loop is None or _background_loop.is_closed():
        raise RuntimeError("Background asyncio event loop is not running.")
    return _background_loop


def run_coroutine(coro) -> asyncio.Future:
    """
    Schedule a coroutine on the background loop from any thread.
    Returns a concurrent.futures.Future that can be awaited or ignored.
    """
    loop = get_event_loop()
    return asyncio.run_coroutine_threadsafe(coro, loop)


def setup_asyncio_event_loop(app) -> asyncio.AbstractEventLoop:
    """
    Start a background thread running a dedicated asyncio event loop.
    The Qt UI stays on the main thread; all async tasks run in the background loop.
    """
    global _background_loop, _loop_thread

    _background_loop = asyncio.new_event_loop()

    def _run_loop(loop: asyncio.AbstractEventLoop):
        asyncio.set_event_loop(loop)
        logger.info("Background asyncio event loop started.")
        loop.run_forever()
        logger.info("Background asyncio event loop stopped.")

    _loop_thread = threading.Thread(
        target=_run_loop,
        args=(_background_loop,),
        daemon=True,
        name="AsyncioBackgroundLoop",
    )
    _loop_thread.start()

    # Cleanly stop the loop when Qt exits
    app.aboutToQuit.connect(_stop_loop)

    return _background_loop


def _stop_loop():
    """Stop the background asyncio event loop gracefully."""
    global _background_loop
    if _background_loop and _background_loop.is_running():
        _background_loop.call_soon_threadsafe(_background_loop.stop)
        logger.info("Requested asyncio event loop shutdown.")
