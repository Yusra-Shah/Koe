import base64

from google.cloud import texttospeech
from config import TTS_LANGUAGE_CODES

_client = None

LANGUAGE_CONFIG = {
    "en": {
        "language_code": "en-US",
        "name": "en-US-Neural2-F",
        "speaking_rate": 0.9,
    },
    "ur": {
        "language_code": "ur-PK",
        "name": "ur-PK-Standard-A",
        "speaking_rate": 0.85,
    },
}


def _get_client() -> texttospeech.TextToSpeechClient:
    global _client
    if _client is None:
        _client = texttospeech.TextToSpeechClient()
    return _client


async def synthesize(text: str, language: str = "en") -> str:
    """
    Synthesize text to speech.
    Returns base64-encoded MP3 audio content.
    """
    client = _get_client()
    cfg = LANGUAGE_CONFIG.get(language, LANGUAGE_CONFIG["en"])

    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=cfg["language_code"],
        name=cfg["name"],
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=cfg["speaking_rate"],
        pitch=0.0,
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config,
    )

    return base64.b64encode(response.audio_content).decode("utf-8")
