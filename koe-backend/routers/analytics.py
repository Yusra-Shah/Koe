from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class AnalyticsEvent(BaseModel):
    event_type: str
    metadata: dict = {}


@router.post("/")
async def log_event(event: AnalyticsEvent):
    # TODO: Wire to BigQuery
    return {"status": "logged", "event_type": event.event_type}
