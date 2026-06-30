import google.genai as genai
from config import GOOGLE_API_KEY

_client = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=GOOGLE_API_KEY)
    return _client


async def gloss_to_sentence(sign_label: str, language: str = "en") -> str:
    """Convert a raw sign label (e.g. 'letter_H') into a natural sentence."""
    client = _get_client()

    prompt = (
        "You are an assistive communication helper for deaf and mute users. "
        "Convert the following sign language label into a short, natural, helpful phrase "
        "that communicates what the user is expressing. "
        "If the label is a fingerspelling letter like 'letter_A', interpret it as the letter A. "
        "If it is a word sign like 'help' or 'water', express it naturally. "
        "Respond with only the phrase, no explanation.\n\n"
        f"Sign label: {sign_label}"
    )

    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text.strip()


async def translate_to_urdu(text: str) -> str:
    """Translate English text to Urdu."""
    client = _get_client()

    prompt = (
        "Translate the following English text to Urdu. "
        "Use clear, simple Urdu appropriate for everyday communication. "
        "Respond with only the Urdu translation.\n\n"
        f"English: {text}"
    )

    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text.strip()


async def detect_mcp_intent(text: str) -> str | None:
    """
    Check if the translated sentence expresses an intent to trigger an MCP tool.
    Returns one of: 'form_fill', 'emergency_contact', 'appointment_request', or None.
    """
    client = _get_client()

    prompt = (
        "Does the following sentence express a need to: fill a form, contact emergency services, "
        "or request an appointment? "
        "Respond with exactly one of these words if yes: form_fill, emergency_contact, appointment_request. "
        "Respond with 'none' if no MCP action is needed.\n\n"
        f"Sentence: {text}"
    )

    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    result = response.text.strip().lower()
    if result in ("form_fill", "emergency_contact", "appointment_request"):
        return result
    return None
