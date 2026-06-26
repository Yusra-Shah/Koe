from fastapi import APIRouter
from schemas.landmarks import TranslateRequest, TranslateResponse

router = APIRouter()


@router.post("/", response_model=TranslateResponse)
async def translate_sign(request: TranslateRequest):
    # TODO: Wire to ADK agent pipeline
    return TranslateResponse(
        text="Sign translation placeholder",
        sign_label="unknown",
        confidence=0.0,
        language=request.language,
    )
