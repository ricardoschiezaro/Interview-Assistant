"""
Cloudflare Workers AI — text sanitization step.

Corrects Cloud/Engineering technical term misspellings via
@cf/meta/llama-3-8b-instruct.  Falls back transparently to the raw
transcribed text if Cloudflare times out or returns an error.
"""

import asyncio
import logging
import aiohttp

from core.config import (
    CLOUDFLARE_ENDPOINT,
    CLOUDFLARE_API_TOKEN,
    CLOUDFLARE_TIMEOUT_S,
)

logger = logging.getLogger(__name__)

_SANITIZE_PROMPT = (
    "You are a text correction engine for Cloud/Engineering terms. "
    "Rule 1: Correct technical misspellings (e.g., AKS, Azure, Terraform, VNet). "
    "Rule 2: SUPPORT MULTIPLE LANGUAGES (English and Portuguese). "
    "Rule 3: DO NOT TRANSLATE the text. Maintain the original language. "
    "Rule 4: Return ONLY the corrected text, no conversational filler. "
    "Rule 5: If no technical correction is obvious, return the original text EXACTLY."
)


async def sanitize(text: str, session: aiohttp.ClientSession) -> str:
    """
    Send *text* to Cloudflare Workers AI for technical term correction.
    Returns corrected text, or the original on timeout / API error.
    """
    if not CLOUDFLARE_API_TOKEN or not CLOUDFLARE_ENDPOINT:
        return text

    # Speed optimization: don't sanitize very short phrases (less than 3 words)
    if len(text.split()) < 3:
        return text

    payload = {
        "messages": [
            {"role": "system", "content": _SANITIZE_PROMPT},
            {"role": "user", "content": text},
        ],
        "max_tokens": 512,
        "stream": False,
    }
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        timeout = aiohttp.ClientTimeout(total=CLOUDFLARE_TIMEOUT_S)
        async with session.post(
            CLOUDFLARE_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=timeout,
        ) as resp:
            if resp.status != 200:
                body = await resp.text()
                logger.warning(
                    "Cloudflare returned HTTP %d: %s — using raw text.",
                    resp.status,
                    body[:200],
                )
                return text

            data = await resp.json()
            corrected = (
                data.get("result", {})
                .get("response", "")
                .strip()
            )
            if corrected:
                # Safety check: if the model returns a full sentence for a 1-word input, it's chatter.
                if len(corrected) > len(text) * 3 and len(corrected) > 50:
                    logger.warning("Sanitizer returned suspiciously long response (chatter?) — using original.")
                    return text
                logger.info("Sanitized: %r → %r", text, corrected)
                return corrected
            return text

    except asyncio.TimeoutError:
        logger.warning(
            "Cloudflare timed out after %.1f s — falling back to raw text.",
            CLOUDFLARE_TIMEOUT_S,
        )
        return text
    except Exception as exc:
        logger.warning("Cloudflare error (%s) — falling back to raw text.", exc)
        return text
