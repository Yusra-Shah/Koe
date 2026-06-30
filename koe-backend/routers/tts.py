from fastapi import APIRouter, Depends
from pydantic import BaseModel
from services.tts_service import synthesize
from middleware.auth import verify_clerk_token

router = APIRouter()


class TTSRequest(BaseModel):
    text: str
    language: str = "en"


class TTSResponse(BaseModel):
    audio_base64: str
    language: str


@router.post("/", response_model=TTSResponse)
async def text_to_speech(
    request: TTSRequest,
    user_id: str = Depends(verify_clerk_token),
):
    audio_b64 = await synthesize(request.text, request.language)
    return TTSResponse(audio_base64=audio_b64, language=request.language)
