"""
Koe Sign Language Translation Pipeline — Google ADK Multi-Agent System

6 specialized agents running in sequence:
  1. InputValidationAgent   — validates landmark structure
  2. GestureRecognitionAgent — TFLite model inference
  3. ConfidenceAgent         — threshold gating, analytics logging
  4. GlossToSentenceAgent    — Gemini: sign label → natural sentence
  5. TranslationAgent        — Gemini: English → Urdu if needed
  6. OutputAgent             — intent detection, response formatting

Each non-LLM step is a FunctionTool called by a lightweight LlmAgent,
satisfying the ADK multi-agent pipeline pattern for the Kaggle submission.
"""

import json
import logging

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.genai import types as genai_types

from models.gesture_classifier import classify
from services import bigquery_service, gemini_service

logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = 0.75

# ---------------------------------------------------------------------------
# Tool functions — each agent delegates its core logic to one of these
# ---------------------------------------------------------------------------

def validate_landmarks(landmarks_json: str) -> str:
    """Validate incoming landmark JSON. Returns OK or an error message."""
    try:
        data = json.loads(landmarks_json)
        if not isinstance(data, list) or len(data) == 0:
            return json.dumps({"valid": False, "reason": "No hands detected"})
        for hand in data:
            if len(hand) != 21:
                return json.dumps({"valid": False, "reason": f"Expected 21 landmarks, got {len(hand)}"})
            for pt in hand:
                if not all(k in pt for k in ("x", "y", "z")):
                    return json.dumps({"valid": False, "reason": "Landmark missing x/y/z"})
        return json.dumps({"valid": True, "num_hands": len(data)})
    except Exception as exc:
        return json.dumps({"valid": False, "reason": str(exc)})


def run_gesture_recognition(landmarks_json: str) -> str:
    """Run TFLite MLP inference and return sign label with confidence."""
    try:
        landmarks = json.loads(landmarks_json)
        label, confidence = classify(landmarks)
        return json.dumps({"sign_label": label, "confidence": confidence})
    except Exception as exc:
        logger.error("Gesture recognition error: %s", exc)
        return json.dumps({"sign_label": "unknown", "confidence": 0.0, "error": str(exc)})


def evaluate_confidence(recognition_json: str, session_id: str, language: str) -> str:
    """
    Gate on confidence threshold. Log to BigQuery.
    Returns pass/fail with instruction for the user if low confidence.
    """
    data = json.loads(recognition_json)
    label = data.get("sign_label", "unknown")
    confidence = data.get("confidence", 0.0)
    recognized = confidence >= CONFIDENCE_THRESHOLD

    try:
        bigquery_service.log_gesture_event(
            sign_label=label,
            confidence=confidence,
            recognized=recognized,
            language=language,
            session_id=session_id,
        )
    except Exception as exc:
        logger.warning("BigQuery logging failed: %s", exc)

    return json.dumps({
        "sign_label": label,
        "confidence": confidence,
        "recognized": recognized,
        "repeat_requested": not recognized,
    })


def format_output(text_en: str, text_ur: str, sign_label: str, confidence: float, mcp_intent: str | None) -> str:
    """Assemble the final response payload."""
    return json.dumps({
        "text_en": text_en,
        "text_ur": text_ur,
        "sign_label": sign_label,
        "confidence": confidence,
        "mcp_intent": mcp_intent,
        "repeat_requested": False,
    })


# ---------------------------------------------------------------------------
# Agent definitions
# ---------------------------------------------------------------------------

input_validation_agent = LlmAgent(
    name="InputValidationAgent",
    model="gemini-2.5-flash",
    description="Validates that the incoming hand landmark data is structurally correct.",
    instruction=(
        "You are the first agent in the Koe sign language pipeline. "
        "Use the validate_landmarks tool with the landmarks_json from the user message. "
        "If validation fails, respond with: INVALID: <reason>. "
        "If validation passes, respond with: VALID"
    ),
    tools=[FunctionTool(validate_landmarks)],
    output_key="validation_result",
)

gesture_recognition_agent = LlmAgent(
    name="GestureRecognitionAgent",
    model="gemini-2.5-flash",
    description="Runs the TFLite gesture classification model on hand landmarks.",
    instruction=(
        "You are the gesture recognition agent in the Koe pipeline. "
        "The previous agent validated the input. "
        "Use the run_gesture_recognition tool with the landmarks_json from the original user message. "
        "Respond with the JSON result from the tool, unchanged."
    ),
    tools=[FunctionTool(run_gesture_recognition)],
    output_key="recognition_result",
)

confidence_agent = LlmAgent(
    name="ConfidenceAgent",
    model="gemini-2.5-flash",
    description="Evaluates gesture confidence score and logs the event to BigQuery analytics.",
    instruction=(
        "You are the confidence evaluation agent. "
        "Use the evaluate_confidence tool with the recognition JSON, session_id, and language from context. "
        "If repeat_requested is true in the result, stop the pipeline and respond: "
        "REPEAT_SIGN: Please sign again more clearly. "
        "Otherwise, pass the result forward."
    ),
    tools=[FunctionTool(evaluate_confidence)],
    output_key="confidence_result",
)

gloss_to_sentence_agent = LlmAgent(
    name="GlossToSentenceAgent",
    model="gemini-2.5-flash",
    description="Converts raw sign gloss labels into natural English sentences using Gemini.",
    instruction=(
        "You are the natural language generation agent for Koe. "
        "You receive a sign label (e.g. 'letter_H', 'water', 'help'). "
        "Convert it into a short, clear, natural English phrase that expresses what the user is communicating. "
        "For fingerspelling letters, say 'The letter [X]'. "
        "For word signs, express the meaning naturally (e.g. 'help' → 'I need help'). "
        "Respond with ONLY the English phrase."
    ),
    output_key="sentence_en",
)

translation_agent = LlmAgent(
    name="TranslationAgent",
    model="gemini-2.5-flash",
    description="Translates the English sentence to Urdu when the user has selected Urdu output.",
    instruction=(
        "You are the translation agent. "
        "If the language is 'ur', translate the English sentence to clear, simple Urdu. "
        "If the language is 'en', return the English sentence unchanged. "
        "Respond with ONLY the translated (or unchanged) text."
    ),
    output_key="sentence_final",
)

output_agent = LlmAgent(
    name="OutputAgent",
    model="gemini-2.5-flash",
    description="Detects MCP tool intent and assembles the final structured response.",
    instruction=(
        "You are the output formatting agent for Koe. "
        "You receive the final English and translated sentences. "
        "Detect if the sentence expresses a need to: fill a form, contact emergency services, "
        "or request an appointment. "
        "If yes, set mcp_intent to one of: form_fill, emergency_contact, appointment_request. "
        "Otherwise set mcp_intent to null. "
        "Respond with a JSON object: "
        '{"text_en": "...", "text_ur": "...", "sign_label": "...", "confidence": 0.0, '
        '"mcp_intent": null, "repeat_requested": false}'
    ),
    output_key="final_output",
)

# ---------------------------------------------------------------------------
# Sequential pipeline
# ---------------------------------------------------------------------------

koe_pipeline = SequentialAgent(
    name="KoeSignPipeline",
    description=(
        "End-to-end sign language translation pipeline. "
        "Validates input, classifies gesture, checks confidence, "
        "generates natural sentence, translates, and formats output."
    ),
    sub_agents=[
        input_validation_agent,
        gesture_recognition_agent,
        confidence_agent,
        gloss_to_sentence_agent,
        translation_agent,
        output_agent,
    ],
)

# ---------------------------------------------------------------------------
# Runner (shared across requests, sessions are per-request)
# ---------------------------------------------------------------------------

_session_service = InMemorySessionService()

_runner = Runner(
    agent=koe_pipeline,
    app_name="koe",
    session_service=_session_service,
)

# Cache: (sign_label, language) -> result dict. Avoids repeat Gemini calls for same sign.
_translation_cache: dict[tuple[str, str], dict] = {}


def _label_to_sentence(sign_label: str) -> str:
    label_lower = sign_label.lower()
    if label_lower.startswith("letter_"):
        letter = label_lower.replace("letter_", "").upper()
        return f"The letter {letter}"
    overrides = {
        "help": "I need help",
        "water": "I need water",
        "yes": "Yes",
        "no": "No",
        "thank_you": "Thank you",
        "please": "Please",
        "sorry": "I'm sorry",
        "hello": "Hello",
        "goodbye": "Goodbye",
        "emergency": "This is an emergency",
        "doctor": "I need a doctor",
        "pain": "I am in pain",
        "food": "I need food",
        "bathroom": "I need the bathroom",
    }
    if label_lower in overrides:
        return overrides[label_lower]
    return sign_label.replace("_", " ").title()


def _sentence_to_urdu(text_en: str, sign_label: str) -> str:
    label_lower = sign_label.lower()
    if label_lower.startswith("letter_"):
        letter = label_lower.replace("letter_", "").upper()
        return f"حرف {letter}"
    ur_map = {
        "I need help": "مجھے مدد چاہیے",
        "I need water": "مجھے پانی چاہیے",
        "Yes": "ہاں",
        "No": "نہیں",
        "Thank you": "شکریہ",
        "Please": "براہ کرم",
        "I'm sorry": "مجھے معاف کریں",
        "Hello": "ہیلو",
        "Goodbye": "خدا حافظ",
        "This is an emergency": "یہ ایک ہنگامی صورتحال ہے",
        "I need a doctor": "مجھے ڈاکٹر چاہیے",
        "I am in pain": "مجھے درد ہو رہا ہے",
        "I need food": "مجھے کھانا چاہیے",
        "I need the bathroom": "مجھے واش روم چاہیے",
    }
    return ur_map.get(text_en, text_en)


async def _run_pipeline_direct(
    landmarks: list[list[dict]],
    language: str,
    session_id: str,
    user_id: str,
) -> dict:
    import json as _json

    landmarks_json = _json.dumps(landmarks)

    validation = _json.loads(validate_landmarks(landmarks_json))
    if not validation.get("valid"):
        return {
            "text_en": "Invalid sign detected",
            "text_ur": "",
            "sign_label": "unknown",
            "confidence": 0.0,
            "mcp_intent": None,
            "repeat_requested": False,
        }

    recognition = _json.loads(run_gesture_recognition(landmarks_json))
    sign_label = recognition.get("sign_label", "unknown")
    confidence = recognition.get("confidence", 0.0)

    conf_result = _json.loads(evaluate_confidence(_json.dumps(recognition), session_id, language))
    if conf_result.get("repeat_requested"):
        return {
            "text_en": "Please sign again more clearly.",
            "text_ur": "",
            "sign_label": sign_label,
            "confidence": confidence,
            "mcp_intent": None,
            "repeat_requested": True,
        }

    text_en = _label_to_sentence(sign_label)
    text_ur = _sentence_to_urdu(text_en, sign_label) if language == "ur" else ""

    mcp_intent = None
    label_lower = sign_label.lower()
    if label_lower in ("emergency", "doctor", "pain"):
        mcp_intent = "emergency_contact"
    elif label_lower in ("help",):
        mcp_intent = "form_fill"

    return {
        "text_en": text_en,
        "text_ur": text_ur,
        "sign_label": sign_label,
        "confidence": confidence,
        "mcp_intent": mcp_intent,
        "repeat_requested": False,
    }


async def run_pipeline(
    landmarks: list[list[dict]],
    language: str,
    session_id: str,
    user_id: str = "anonymous",
) -> dict:
    """
    Run the full 6-agent Koe pipeline for a single sign recognition request.
    Returns a dict with: text_en, text_ur, sign_label, confidence, mcp_intent, repeat_requested.
    Falls back to direct TFLite-only mode if Gemini quota is exhausted.
    """
    import json as _json

    # Fast path: run TFLite first so we know the sign label before hitting Gemini
    landmarks_json = _json.dumps(landmarks)
    validation = _json.loads(validate_landmarks(landmarks_json))
    if not validation.get("valid"):
        return {"text_en": "Invalid sign", "text_ur": "", "sign_label": "unknown",
                "confidence": 0.0, "mcp_intent": None, "repeat_requested": False}

    recognition = _json.loads(run_gesture_recognition(landmarks_json))
    sign_label = recognition.get("sign_label", "unknown")
    confidence = recognition.get("confidence", 0.0)

    conf_result = _json.loads(evaluate_confidence(_json.dumps(recognition), session_id, language))
    if conf_result.get("repeat_requested"):
        return {"text_en": "Please sign again more clearly.", "text_ur": "",
                "sign_label": sign_label, "confidence": confidence,
                "mcp_intent": None, "repeat_requested": True}

    # Return cached translation if we've seen this sign+language before
    cache_key = (sign_label, language)
    if cache_key in _translation_cache:
        cached = dict(_translation_cache[cache_key])
        cached["confidence"] = confidence  # update confidence for this reading
        return cached

    try:
        session = await _session_service.create_session(
            app_name="koe",
            user_id=user_id,
            session_id=session_id,
            state={
                "language": language,
                "session_id": session_id,
            },
        )

        landmarks_json = _json.dumps(landmarks)
        user_message = genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=landmarks_json)],
        )

        final_text = ""
        async for event in _runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=user_message,
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if part.text:
                        final_text = part.text.strip()

        try:
            result = _json.loads(final_text)
            if "text_en" not in result:
                raise ValueError("Missing text_en")
            _translation_cache[cache_key] = result
            return result
        except Exception:
            fallback = {
                "text_en": final_text or "Could not translate sign",
                "text_ur": "",
                "sign_label": sign_label,
                "confidence": confidence,
                "mcp_intent": None,
                "repeat_requested": False,
            }
            _translation_cache[cache_key] = fallback
            return fallback

    except Exception as exc:
        err = str(exc)
        if "429" in err or "RESOURCE_EXHAUSTED" in err or "quota" in err.lower():
            logger.warning("Gemini quota exhausted — falling back to direct TFLite pipeline")
            result = await _run_pipeline_direct(landmarks, language, session_id, user_id)
            _translation_cache[cache_key] = result
            return result
        raise
