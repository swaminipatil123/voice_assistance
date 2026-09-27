import re
import hashlib
from pathlib import Path
from backend.config import Config
from backend.utils.logger import logger


def sanitize_for_speech(text: str, lang: str = "en") -> str:
    """
    Normalizes complex words, URLs, and acronyms into clear phonetic pronunciations for TTS.
    Specifically ensures the university domain svkmnmimsgu.ac.in is pronounced accurately letter-by-letter.
    Handles typos like svkmnmimsngu.ac.in as well.
    """
    if not text:
        return ""

    l = (lang or "en").lower().strip()
    spoken = text

    if l.startswith("hi"):
        # Hindi pronunciation
        spoken = re.sub(r"https?://(www\.)?svkmnmimsn?gu\.ac\.in/?", " एस वी के एम, एन एम आई एम एस, एस एन जी यू, डॉट एसी डॉट इन ", spoken, flags=re.I)
        spoken = re.sub(r"svkmnmimsn?gu\.ac\.in\s*\([^)]*\)", " एस वी के एम, एन एम आई एम एस, एस एन जी यू, डॉट एसी डॉट इन ", spoken, flags=re.I)
        spoken = re.sub(r"svkmnmimsn?gu\.ac\.in", " एस वी के एम, एन एम आई एम एस, एस एन जी यू, डॉट एसी डॉट इन ", spoken, flags=re.I)
    elif l.startswith("mr"):
        # Marathi pronunciation
        spoken = re.sub(r"https?://(www\.)?svkmnmimsn?gu\.ac\.in/?", " एस व्ही के एम, एन एम आय एम एस, एस एन जी यू, डॉट एसी डॉट इन ", spoken, flags=re.I)
        spoken = re.sub(r"svkmnmimsn?gu\.ac\.in\s*\([^)]*\)", " एस व्ही के एम, एन एम आय एम एस, एस एन जी यू, डॉट एसी डॉट इन ", spoken, flags=re.I)
        spoken = re.sub(r"svkmnmimsn?gu\.ac\.in", " एस व्ही के एम, एन एम आय एम एस, एस एन जी यू, डॉट एसी डॉट इन ", spoken, flags=re.I)
    else:
        # English pronunciation
        spoken = re.sub(r"svkmnmimsn?gu\.ac\.in\s*,?\s*\(?pronounced as\s+[^)]+\)?", " S V K M, N M I M S, S N G U, dot A C, dot I N ", spoken, flags=re.I)
        spoken = re.sub(r"https?://(www\.)?svkmnmimsn?gu\.ac\.in/?", " S V K M, N M I M S, S N G U, dot A C, dot I N ", spoken, flags=re.I)
        spoken = re.sub(r"svkmnmimsn?gu\.ac\.in\s*\([^)]*\)", " S V K M, N M I M S, S N G U, dot A C, dot I N ", spoken, flags=re.I)
        spoken = re.sub(r"svkmnmimsn?gu\.ac\.in", " S V K M, N M I M S, S N G U, dot A C, dot I N ", spoken, flags=re.I)

    spoken = re.sub(r"\s+", " ", spoken).strip()
    return spoken


class TextToSpeechService:
    """Service to convert text into speech audio or phone-ready audio files."""

    def __init__(self, provider: str = None, api_key: str = None):
        self.provider = provider or Config.TTS_PROVIDER
        self.api_key = api_key or Config.TTS_API_KEY
        self.output_dir = Config.STATIC_DIR / "audio"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def text_to_speech(self, text: str, lang: str = "en") -> str:
        """
        Converts text to an audio file (.mp3) and returns the relative or absolute filepath.
        In mock mode or if gTTS fails, returns empty string or a placeholder audio path.
        """
        if not text or not text.strip():
            return ""

        if self.provider == "mock":
            logger.info("Using mock Text-to-Speech provider.")
            return ""

        if self.provider == "gtts":
            try:
                from gtts import gTTS
                spoken_text = sanitize_for_speech(text, lang=lang)
                # Create a deterministic filename based on content hash of spoken text + lang
                text_hash = hashlib.md5(f"{lang}_{spoken_text}".encode("utf-8")).hexdigest()[:12]
                filename = f"tts_{text_hash}.mp3"
                file_path = self.output_dir / filename

                if not file_path.exists():
                    tts = gTTS(text=spoken_text, lang=lang, slow=False)
                    tts.save(str(file_path))
                    logger.info(f"Saved TTS audio to {file_path}")

                return str(file_path)
            except Exception as e:
                logger.warning(f"gTTS conversion failed ({e}), falling back to telephony native voice.")
                return ""

        return ""


text_to_speech_service = TextToSpeechService()
