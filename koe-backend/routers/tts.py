from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class TTSRequest(BaseModel):
    text: str
    language: str = "en"


@router.post("/")
async def text_to_speech(request: TTSRequest):
    # TODO: Wire to Google Cloud TTS
    return {"status": "tts_placeholder", "text": request.text, "language": request.language}
