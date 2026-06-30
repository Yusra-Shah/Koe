import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from schemas.landmarks import TranslateRequest, TranslateResponse
from agents.pipeline import run_pipeline
from services import firestore_service
from middleware.auth import verify_clerk_token

router = APIRouter()


@router.post("/", response_model=TranslateResponse)
async def translate_sign(
    request: TranslateRequest,
    http_request: Request,
    user_id: str = Depends(verify_clerk_token),
):
    session_id = request.session_id or str(uuid.uuid4())

    result = await run_pipeline(
        landmarks=[[p.model_dump() for p in hand] for hand in request.landmarks],
        language=request.language,
        session_id=session_id,
        user_id=user_id,
    )

    if result.get("repeat_requested"):
        return TranslateResponse(
            text="Please sign again more clearly.",
            text_ur="",
            sign_label="",
            confidence=0.0,
            language=request.language,
            repeat_requested=True,
            mcp_intent=None,
        )

    text_en = result.get("text_en", "")
    text_ur = result.get("text_ur", "")
    sign_label = result.get("sign_label", "unknown")
    confidence = result.get("confidence", 0.0)
    mcp_intent = result.get("mcp_intent")

    display_text = text_ur if request.language == "ur" and text_ur else text_en

    try:
        firestore_service.save_notebook_entry(
            user_id=user_id,
            session_id=session_id,
            text_en=text_en,
            text_ur=text_ur,
            sign_label=sign_label,
            confidence=confidence,
        )
    except Exception:
        pass

    return TranslateResponse(
        text=display_text,
        text_ur=text_ur,
        sign_label=sign_label,
        confidence=confidence,
        language=request.language,
        repeat_requested=False,
        mcp_intent=mcp_intent,
    )
