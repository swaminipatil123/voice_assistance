import os
from backend.config import Config
from backend.utils.logger import logger

class SpeechToTextService:
    """Service to handle Speech-To-Text conversion."""

    def __init__(self, provider: str = None, api_key: str = None):
        self.provider = provider or Config.STT_PROVIDER
        self.api_key = api_key or Config.STT_API_KEY

    def speech_to_text(self, audio_data) -> str:
        """
        Convert speech audio into text.
        audio_data can be:
        - A string representing direct transcript (e.g. from Telephony SpeechResult)
        - A file path to a recorded audio file
        - Raw audio bytes
        """
        if not audio_data:
            return ""

        # If audio_data is already a transcribed text string passed from telephony provider:
        if isinstance(audio_data, str) and not os.path.exists(audio_data):
            return audio_data.strip()

        if self.provider == "mock":
            logger.info("Using mock Speech-to-Text provider.")
            return "What courses are available in Computer Engineering?"

        # If using external API (e.g. Google Cloud Speech or Whisper)
        try:
            return self._external_stt_transcribe(audio_data)
        except Exception as e:
            logger.error(f"STT conversion failed: {e}")
            return ""

    def _external_stt_transcribe(self, audio_data) -> str:
        # Placeholder for external speech APIs when required
        logger.info(f"External STT provider {self.provider} called.")
        return ""

speech_to_text_service = SpeechToTextService()
