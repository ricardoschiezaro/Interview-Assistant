import asyncio
import json
import logging
from urllib.parse import urlencode

from core.config import (
    DEEPGRAM_API_KEY,
    DEEPGRAM_SAMPLE_RATE,
    DEEPGRAM_ENCODING,
)

logger = logging.getLogger(__name__)

_DG_WS_URL = "wss://api.deepgram.com/v1/listen"

class DeepgramSTT:
    def __init__(self, audio_queue: asyncio.Queue, text_queue: asyncio.Queue, status_callback=None):
        self._audio_q = audio_queue
        self._text_q = text_queue
        self._status_cb = status_callback or (lambda msg: None)
        self._running = False
        self._ws = None

    async def run(self):
        self._running = True
        while self._running:
            try:
                await self._connect_and_stream()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Deepgram error: %s — reconnecting…", exc)
                await asyncio.sleep(3)

    def stop(self):
        self._running = False
        if self._ws:
            asyncio.ensure_future(self._ws.close())

    def trigger_reconnect(self):
        """Force close the current WS to trigger a reconnect with new profile settings."""
        if self._ws:
            logger.info("STT Reconnect triggered (language change).")
            asyncio.ensure_future(self._ws.close())

    async def _connect_and_stream(self):
        import websockets
        from core.profile import get_profile
        profile = get_profile()

        params = {
            "model": "nova-2",
            "encoding": DEEPGRAM_ENCODING,
            "sample_rate": DEEPGRAM_SAMPLE_RATE,
            "channels": 1,
            "interim_results": "true",
            "smart_format": "true",
            "punctuate": "true",
            "utterance_end_ms": "2000",
            "vad_events": "true",
        }

        if profile.language == "en":
            params["language"] = "en-US"
        else:
            # Streaming doesn't support detect_language=true reliably.
            # Default to pt-BR for auto/pt.
            params["language"] = "pt-BR"

        url = f"{_DG_WS_URL}?{urlencode(params)}"
        headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}"}

        async with websockets.connect(url, additional_headers=headers) as ws:
            self._ws = ws
            self._buffer = []
            await asyncio.gather(
                self._receive_loop(ws),
                self._send_loop(ws),
                self._keepalive_loop(ws),
            )

    async def _receive_loop(self, ws):
        async for raw in ws:
            msg = json.loads(raw)
            if msg.get("type") == "Results":
                alts = msg.get("channel", {}).get("alternatives", [])
                if not alts: continue
                transcript = alts[0].get("transcript", "").strip()
                if not transcript: continue

                if msg.get("is_final"):
                    self._buffer.append(transcript)
                
                if msg.get("speech_final"):
                    full_text = " ".join(self._buffer).strip()
                    if full_text:
                        await self._text_q.put(full_text)
                        self._buffer = []

    async def _send_loop(self, ws):
        while self._running:
            chunk = await self._audio_q.get()
            await ws.send(chunk)

    async def _keepalive_loop(self, ws):
        while self._running:
            await asyncio.sleep(8)
            await ws.send(json.dumps({"type": "KeepAlive"}))
