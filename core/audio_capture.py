"""
Audio capture pipeline for Windows.

Two capture sources:
  • SystemLoopback  – WASAPI loopback via pyaudiowpatch (interviewer audio)
  • Microphone      – Default input device via sounddevice (user voice)

Both produce int16 mono 16 kHz chunks and push them into the shared asyncio Queue.
"""

import asyncio
import logging
import threading
import numpy as np
from typing import Optional

from core.config import (
    AUDIO_SAMPLE_RATE,
    AUDIO_CHANNELS,
    AUDIO_CHUNK_MS,
    AUDIO_DTYPE,
)

logger = logging.getLogger(__name__)

# Samples per chunk = sample_rate * chunk_duration_s
CHUNK_SAMPLES = int(AUDIO_SAMPLE_RATE * AUDIO_CHUNK_MS / 1000)


class AudioCaptureWorker:
    """
    Manages both system-loopback and microphone capture.
    Pushes raw PCM bytes (int16, mono, 16 kHz) into *audio_queue*.
    """

    def __init__(self, audio_queue: asyncio.Queue, loop: asyncio.AbstractEventLoop):
        self._queue = audio_queue
        self._loop = loop
        self._running = False
        self._threads: list[threading.Thread] = []
        self._active_source = "system"  # "system" | "mic"

    # ── Public API ────────────────────────────────────────────────────────────

    def set_source(self, source: str):
        """Switch active capture source ('system' or 'mic')."""
        self._active_source = source
        logger.info("Audio source set to: %s", source)

    def start(self):
        self._running = True
        self._list_devices()
        self._start_system_loopback()
        self._start_microphone()

    def _list_devices(self):
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            logger.info("Available Audio Devices:\n%s", devices)
            default_in = sd.default.device[0]
            logger.info("Default Input Device ID: %s", default_in)
        except Exception as e:
            logger.warning("Could not list audio devices: %s", e)

    def stop(self):
        self._running = False
        logger.info("AudioCaptureWorker stopping…")

    # ── System Loopback (WASAPI via pyaudiowpatch) ────────────────────────────

    def _start_system_loopback(self):
        t = threading.Thread(
            target=self._run_system_loopback,
            daemon=True,
            name="SystemLoopbackCapture",
        )
        self._threads.append(t)
        t.start()

    def _run_system_loopback(self):
        try:
            import pyaudiowpatch as pyaudio  # type: ignore
        except ImportError:
            logger.warning(
                "pyaudiowpatch not installed — system loopback unavailable. "
                "Install it with: pip install pyaudiowpatch"
            )
            return

        try:
            p = pyaudio.PyAudio()
            # Find the default WASAPI loopback device
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_speakers_idx = wasapi_info["defaultOutputDevice"]
            default_speakers = p.get_device_info_by_index(default_speakers_idx)

            # Find the loopback counterpart.
            # The loopback device name may have a suffix like " [Loopback]",
            # so we use a substring match on the output device name.
            default_name = default_speakers["name"]
            loopback_device = None
            for i in range(p.get_device_count()):
                dev = p.get_device_info_by_index(i)
                if dev.get("isLoopbackDevice") and default_name in dev["name"]:
                    loopback_device = dev
                    break

            # Fallback: pick any loopback device if the above didn't match
            if loopback_device is None:
                for i in range(p.get_device_count()):
                    dev = p.get_device_info_by_index(i)
                    if dev.get("isLoopbackDevice") and dev["maxInputChannels"] > 0:
                        loopback_device = dev
                        logger.info("Using fallback loopback device: %s", dev["name"])
                        break

            if loopback_device is None:
                logger.warning("No WASAPI loopback device found.")
                p.terminate()
                return

            native_rate = int(loopback_device["defaultSampleRate"])
            native_channels = loopback_device["maxInputChannels"]
            device_idx = int(loopback_device["index"])

            logger.info(
                "System loopback: device='%s' rate=%d ch=%d",
                loopback_device["name"],
                native_rate,
                native_channels,
            )

            frame_count = int(native_rate * AUDIO_CHUNK_MS / 1000)

            stream = p.open(
                format=pyaudio.paInt16,
                channels=native_channels,
                rate=native_rate,
                input=True,
                input_device_index=device_idx,
                frames_per_buffer=frame_count,
            )

            while self._running:
                if self._active_source not in ("system", "both"):
                    # Drain but discard
                    stream.read(frame_count, exception_on_overflow=False)
                    continue

                raw = stream.read(frame_count, exception_on_overflow=False)
                pcm = self._process_raw(
                    raw, native_channels, native_rate, np.int16
                )
                if pcm is not None:
                    asyncio.run_coroutine_threadsafe(
                        self._queue.put(pcm), self._loop
                    )

            stream.stop_stream()
            stream.close()
            p.terminate()

        except Exception as exc:
            logger.error("System loopback capture error: %s", exc, exc_info=True)

    # ── Microphone (sounddevice) ──────────────────────────────────────────────

    def _start_microphone(self):
        t = threading.Thread(
            target=self._run_microphone,
            daemon=True,
            name="MicrophoneCapture",
        )
        self._threads.append(t)
        t.start()

    def _run_microphone(self):
        try:
            import sounddevice as sd  # type: ignore
        except ImportError:
            logger.warning(
                "sounddevice not installed — microphone unavailable. "
                "Install with: pip install sounddevice"
            )
            return

        logger.info("Microphone capture started (sounddevice).")

        def callback(indata: np.ndarray, frames: int, time_info, status):
            if status:
                logger.debug("sounddevice status: %s", status)
            if self._active_source not in ("mic", "both"):
                return
            # indata is (frames, channels) float32
            mono = indata[:, 0] if indata.ndim > 1 else indata.flatten()
            pcm16 = (mono * 32767).clip(-32768, 32767).astype(np.int16)
            asyncio.run_coroutine_threadsafe(
                self._queue.put(pcm16.tobytes()), self._loop
            )

        try:
            with sd.InputStream(
                samplerate=AUDIO_SAMPLE_RATE,
                channels=AUDIO_CHANNELS,
                dtype="float32",
                blocksize=CHUNK_SAMPLES,
                callback=callback,
            ):
                while self._running:
                    threading.Event().wait(0.1)
        except Exception as exc:
            logger.error("Microphone capture error: %s", exc, exc_info=True)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _process_raw(
        self,
        raw: bytes,
        src_channels: int,
        src_rate: int,
        dtype,
    ) -> Optional[bytes]:
        """Downsample & convert to int16 mono 16 kHz."""
        try:
            arr = np.frombuffer(raw, dtype=np.int16)
            # Reshape to (frames, channels)
            if src_channels > 1:
                arr = arr.reshape(-1, src_channels)
                arr = arr[:, 0]  # take left channel

            # Resample if needed
            if src_rate != AUDIO_SAMPLE_RATE:
                ratio = AUDIO_SAMPLE_RATE / src_rate
                new_len = int(len(arr) * ratio)
                arr = np.interp(
                    np.linspace(0, len(arr) - 1, new_len),
                    np.arange(len(arr)),
                    arr.astype(np.float32),
                ).astype(np.int16)

            return arr.tobytes()
        except Exception as exc:
            logger.debug("Audio processing error: %s", exc)
            return None
