"""
Configuration loader — reads from .env and exposes typed settings.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env from the project root (parent of this file's directory)
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)


def _require(key: str) -> str:
    value = os.getenv(key, "").strip()
    if not value:
        logger.warning("Environment variable '%s' is not set.", key)
    return value


# ── API Keys ──────────────────────────────────────────────────────────────────
DEEPGRAM_API_KEY: str = _require("DEEPGRAM_API_KEY")
GROQ_API_KEY: str = _require("GROQ_API_KEY")
CEREBRAS_API_KEY: str = _require("CEREBRAS_API_KEY")
GOOGLE_API_KEY: str = _require("GOOGLE_API_KEY")
CLOUDFLARE_ACCOUNT_ID: str = _require("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN: str = _require("CLOUDFLARE_API_TOKEN")
OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "").strip()

# ── Cloudflare Workers AI ─────────────────────────────────────────────────────
CLOUDFLARE_MODEL: str = "@cf/meta/llama-3-8b-instruct"
CLOUDFLARE_ENDPOINT: str = (
    f"https://api.cloudflare.com/client/v4/accounts/"
    f"{CLOUDFLARE_ACCOUNT_ID}/ai/run/{CLOUDFLARE_MODEL}"
)
CLOUDFLARE_TIMEOUT_S: float = 0.8  # fall back to Groq if CF exceeds this

# ── LLM Models ────────────────────────────────────────────────────────────────
GROQ_MODEL: str = "llama-3.3-70b-versatile"
CEREBRAS_MODEL: str = "llama3.1-8b"
GROQ_LIGHT_MODEL: str = "llama-3.1-8b-instant"
GOOGLE_MODEL: str = "gemini-2.5-flash"  # Use 2.5 flash as 2.0 is deprecated/unavailable
OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct").strip()

GROQ_SYSTEM_PROMPT: str = (
    "You are acting as my internal voice and thought process during a "
    "professional job interview.\n"
    "Rule 1: If the question is technical or domain-specific, provide structured execution steps, "
    "best practices, or core domain principles.\n"
    "Rule 2: If the question is behavioral or situational, answer with soft skills, "
    "problem-solving mindset, and professional delivery.\n"
    "Rule 3: Match the interviewer's language (English or Portuguese).\n"
    "Rule 4: DO NOT write paragraphs. Output 3-5 short bullet points max.\n"
    "Rule 5: Write exactly as I would speak it naturally, including "
    "conversational fillers like 'Well...', 'In my experience...', "
    "'Actually...'. Keep it brief so I can read it aloud naturally."
)

# ── Deepgram ──────────────────────────────────────────────────────────────────
DEEPGRAM_SAMPLE_RATE: int = 16_000
DEEPGRAM_CHANNELS: int = 1
DEEPGRAM_ENCODING: str = "linear16"
DEEPGRAM_LANGUAGE: str = "en"  # Deepgram auto-detects; keep permissive

# ── Audio ─────────────────────────────────────────────────────────────────────
AUDIO_CHUNK_MS: int = 20          # milliseconds per audio chunk sent to STT
AUDIO_SAMPLE_RATE: int = 16_000
AUDIO_CHANNELS: int = 1
AUDIO_DTYPE: str = "int16"
