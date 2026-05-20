import asyncio
import logging
from groq import AsyncGroq
from core.config import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger(__name__)

class InterviewAnalyzer:
    def __init__(self):
        self._client = AsyncGroq(api_key=GROQ_API_KEY)

    async def analyze(self, transcript_text):
        """
        Analyzes the interview transcript and returns a Markdown report.
        """
        prompt = (
            "Act as a Principal Cloud Architect Mentor. Analyze this interview transcript. "
            "Output a Markdown report with 3 sections:\n"
            "1) Strong Points (Where the architecture/methodology was solid).\n"
            "2) Technical Gaps (Concepts missed or poorly explained, especially regarding Azure best practices, FinOps, or DR).\n"
            "3) Action Plan (What to study before the next round).\n\n"
            f"TRANSCRIPT:\n{transcript_text}"
        )

        try:
            resp = await self._client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            return resp.choices[0].message.content
        except Exception as e:
            logger.error("Analysis failed: %s", e)
            return f"Error during analysis: {e}"
