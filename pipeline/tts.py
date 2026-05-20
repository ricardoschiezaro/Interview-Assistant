import logging
import asyncio

logger = logging.getLogger(__name__)

class TTSManager:
    def __init__(self):
        self.engine = None
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            # Set properties for PT-BR if possible
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if "brazil" in voice.name.lower() or "portuguese" in voice.languages[0].lower() if voice.languages else False:
                    self.engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            logger.warning("TTS Engine (pyttsx3) initialization failed: %s", e)

    async def say(self, text):
        if not self.engine:
            logger.error("TTS Engine not available. Cannot say: %s", text)
            return

        def _speak():
            self.engine.say(text)
            self.engine.runAndWait()

        await asyncio.to_thread(_speak)
