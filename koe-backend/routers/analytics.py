from fastapi import APIRouter, Depends
from pydantic import BaseModel
from services import bigquery_service
from middleware.auth import verify_clerk_token

router = APIRouter()


class AnalyticsEvent(BaseModel):
    event_type: str
    metadata: dict = {}
    session_id: str = ""


@router.post("/")
async def log_event(
    event: AnalyticsEvent,
    user_id: str = Depends(verify_clerk_token),
):
    if event.event_type == "tool_event":
        bigquery_service.log_tool_event(
            tool_name=event.metadata.get("tool_name", "unknown"),
            confirmed=event.metadata.get("confirmed", False),
            session_id=event.session_id,
        )
    return {"status": "logged", "event_type": event.event_type}
