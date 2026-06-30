import hashlib
import uuid
from datetime import datetime, timezone

from google.cloud import bigquery
from config import BIGQUERY_DATASET, GOOGLE_CLOUD_PROJECT

_client = None


def _get_client() -> bigquery.Client:
    global _client
    if _client is None:
        _client = bigquery.Client(project=GOOGLE_CLOUD_PROJECT)
    return _client


def _hash_session(session_id: str) -> str:
    return hashlib.sha256(session_id.encode()).hexdigest()[:16]


def log_gesture_event(
    sign_label: str,
    confidence: float,
    recognized: bool,
    language: str,
    session_id: str,
    country_code: str = "XX",
) -> None:
    if not GOOGLE_CLOUD_PROJECT or not BIGQUERY_DATASET:
        return

    client = _get_client()
    table_id = f"{GOOGLE_CLOUD_PROJECT}.{BIGQUERY_DATASET}.gesture_events"

    row = {
        "event_id": str(uuid.uuid4()),
        "event_timestamp": datetime.now(timezone.utc).isoformat(),
        "sign_label": sign_label,
        "confidence_score": confidence,
        "recognized": recognized,
        "language_selected": language,
        "session_hash": _hash_session(session_id),
        "country_code": country_code,
    }

    client.insert_rows_json(table_id, [row])


def log_tool_event(
    tool_name: str,
    confirmed: bool,
    session_id: str,
) -> None:
    if not GOOGLE_CLOUD_PROJECT or not BIGQUERY_DATASET:
        return

    client = _get_client()
    table_id = f"{GOOGLE_CLOUD_PROJECT}.{BIGQUERY_DATASET}.tool_events"

    row = {
        "event_id": str(uuid.uuid4()),
        "event_timestamp": datetime.now(timezone.utc).isoformat(),
        "tool_name": tool_name,
        "confirmed": confirmed,
        "session_hash": _hash_session(session_id),
    }

    client.insert_rows_json(table_id, [row])
