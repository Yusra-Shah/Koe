import uuid
from datetime import datetime, timezone

from google.cloud import firestore
from config import FIRESTORE_PROJECT

_client = None


def _get_client() -> firestore.Client:
    global _client
    if _client is None:
        _client = firestore.Client(project=FIRESTORE_PROJECT)
    return _client


def upsert_user(user_id: str, display_name: str = "", language: str = "en") -> None:
    if not FIRESTORE_PROJECT:
        return
    db = _get_client()
    ref = db.collection("users").document(user_id)
    doc = ref.get()
    now = datetime.now(timezone.utc).isoformat()
    if doc.exists:
        ref.update({"lastActiveAt": now, "languagePreference": language})
    else:
        ref.set({
            "userId": user_id,
            "displayName": display_name,
            "languagePreference": language,
            "createdAt": now,
            "lastActiveAt": now,
        })


def save_notebook_entry(
    user_id: str,
    session_id: str,
    text_en: str,
    text_ur: str,
    sign_label: str,
    confidence: float,
) -> str:
    if not FIRESTORE_PROJECT:
        return ""
    db = _get_client()
    entry_id = str(uuid.uuid4())
    db.collection("notebooks").document(entry_id).set({
        "entryId": entry_id,
        "userId": user_id,
        "textEn": text_en,
        "textUr": text_ur,
        "signsUsed": [sign_label],
        "confidence": confidence,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "sessionId": session_id,
    })
    return entry_id


def get_user_language(user_id: str) -> str:
    if not FIRESTORE_PROJECT:
        return "en"
    db = _get_client()
    doc = db.collection("users").document(user_id).get()
    if doc.exists:
        return doc.to_dict().get("languagePreference", "en")
    return "en"
