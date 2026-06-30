from pydantic import BaseModel, field_validator


class LandmarkPoint(BaseModel):
    x: float
    y: float
    z: float


class TranslateRequest(BaseModel):
    landmarks: list[list[LandmarkPoint]]
    language: str = "en"
    session_id: str = ""

    @field_validator("language")
    @classmethod
    def validate_language(cls, v):
        if v not in ("en", "ur"):
            raise ValueError("language must be 'en' or 'ur'")
        return v

    @field_validator("landmarks")
    @classmethod
    def validate_landmarks(cls, v):
        for hand in v:
            if len(hand) != 21:
                raise ValueError("Each hand must have exactly 21 landmark points")
        return v


class TranslateResponse(BaseModel):
    text: str
    text_ur: str = ""
    sign_label: str
    confidence: float
    language: str
    repeat_requested: bool = False
    mcp_intent: str | None = None
