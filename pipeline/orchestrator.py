import asyncio
import logging
import aiohttp

from core.audio_capture import AudioCaptureWorker
from pipeline.stt import DeepgramSTT
from pipeline.sanitizer import sanitize
from pipeline.responder import Responder

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self, on_token, on_done, on_question, on_status, on_usage, on_provider, loop, use_sanitizer=True):
        self._on_token = on_token
        self._on_done = on_done
        self._on_question = on_question
        self._on_status = on_status
        self._on_usage_cb = on_usage
        self._on_provider_cb = on_provider
        self._loop = loop
        self._use_sanitizer = use_sanitizer

        self._audio_queue = asyncio.Queue()
        self._text_queue = asyncio.Queue()
        self._sanitized_queue = asyncio.Queue()

        self._audio_worker = AudioCaptureWorker(self._audio_queue, self._loop)
        self._stt = DeepgramSTT(self._audio_queue, self._text_queue, on_status)
        
        # New Responder with DR and Stats
        self._responder = Responder(
            on_token=on_token,
            on_done=on_done,
            status_cb=on_status,
            usage_cb=self._on_usage_cb,
            provider_cb=self._on_provider_cb
        )
        
        self._tasks = []
        self._running = False
        self._http_session = None

    async def start(self, **kwargs):
        self._running = True
        self._http_session = aiohttp.ClientSession()
        self._audio_worker.start()
        self._tasks = [
            asyncio.ensure_future(self._stt.run(), loop=self._loop),
            asyncio.ensure_future(self._sanitize_loop(), loop=self._loop),
        ]
        self._on_status("🚀 Session started")

    async def stop(self):
        self._running = False
        self._audio_worker.stop()
        for t in self._tasks: t.cancel()
        if self._http_session: await self._http_session.close()
        self._on_status("⏹️ Session stopped")

    def set_audio_source(self, source):
        self._audio_worker.set_source(source)

    def set_use_sanitizer(self, use_it):
        self._use_sanitizer = use_it

    def clear_history(self):
        self._responder.clear_history()

    def trigger_stt_reconnect(self):
        """Force STT to reconnect (useful when language changes)."""
        self._stt.trigger_reconnect()

    def _on_usage(self, tokens):
        self._on_usage_cb(tokens)

    def _on_provider(self, provider, status):
        self._on_provider_cb(provider, status)

    async def _sanitize_loop(self):
        buffer = []
        last_receive_time = 0
        
        while self._running:
            try:
                # Wait for text with a timeout to check for silence
                try:
                    text = await asyncio.wait_for(self._text_queue.get(), timeout=1.0)
                    buffer.append(text)
                    last_receive_time = asyncio.get_event_loop().time()
                    # Show partial progress in UI
                    self._on_question(" ".join(buffer) + "...")
                except asyncio.TimeoutError:
                    # No text for 1s, check if we have a buffer and enough silence
                    if buffer and (asyncio.get_event_loop().time() - last_receive_time >= 3.0):
                        full_text = " ".join(buffer).strip()
                        if full_text:
                            self._on_question(full_text) # Final finalized text
                            if self._use_sanitizer:
                                corrected = await sanitize(full_text, self._http_session)
                                await self._responder.generate(corrected)
                            else:
                                await self._responder.generate(full_text)
                        buffer = [] # Clear for next question
            except Exception as e:
                logger.error(f"Error in sanitize loop: {e}")
                await asyncio.sleep(1)
