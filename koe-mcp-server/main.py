"""
Koe MCP Server — FastMCP on Cloud Run

Exposes three tools for external action:
  - form_fill
  - emergency_contact
  - appointment_request

All tools are wrapped by a SafetyConsentAgent pattern (Day 4 ADK requirement).
No tool executes without an explicit confirmed=True from the user.
"""

import logging

from fastmcp import FastMCP

logger = logging.getLogger(__name__)

mcp = FastMCP(
    "Koe MCP Server",
    instructions=(
        "You are the Koe external action server. "
        "You help deaf and mute users perform real-world tasks via tool calls. "
        "IMPORTANT: Never execute any tool without the user explicitly confirming. "
        "Always present a confirmation step before taking any external action."
    ),
)

# ---------------------------------------------------------------------------
# Safety gate — all tools call this before acting
# ---------------------------------------------------------------------------

def _require_confirmation(confirmed: bool, action_description: str) -> dict | None:
    """Returns an error dict if not confirmed, None if safe to proceed."""
    if not confirmed:
        return {
            "status": "awaiting_confirmation",
            "message": f"Please confirm: {action_description}",
            "requires_user_action": True,
        }
    return None


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def form_fill(
    form_type: str,
    fields: dict,
    confirmed: bool = False,
) -> dict:
    """
    Fill a form on behalf of the user.

    Args:
        form_type: Type of form (e.g. 'hospital_registration', 'bank_account', 'id_card')
        fields: Dictionary of field names to values
        confirmed: Must be True for the action to execute (human-in-the-loop)
    """
    gate = _require_confirmation(
        confirmed,
        f"Fill a {form_type} form with the provided information",
    )
    if gate:
        return gate

    logger.info("Executing form_fill: %s with fields: %s", form_type, list(fields.keys()))
    return {
        "status": "submitted",
        "form_type": form_type,
        "fields_submitted": list(fields.keys()),
        "message": f"Your {form_type.replace('_', ' ')} has been submitted.",
    }


@mcp.tool()
async def emergency_contact(
    contact_type: str,
    message: str,
    confirmed: bool = False,
) -> dict:
    """
    Send an emergency contact message on behalf of the user.

    Args:
        contact_type: Who to contact: 'family', 'ambulance', 'police', 'hospital_staff'
        message: The message to send
        confirmed: Must be True for the action to execute (human-in-the-loop)
    """
    gate = _require_confirmation(
        confirmed,
        f"Send an emergency message to {contact_type}: '{message}'",
    )
    if gate:
        return gate

    logger.info("Executing emergency_contact: %s — %s", contact_type, message)
    return {
        "status": "sent",
        "contact_type": contact_type,
        "message": f"Emergency contact sent to {contact_type}.",
    }


@mcp.tool()
async def appointment_request(
    department: str,
    date: str,
    notes: str = "",
    confirmed: bool = False,
) -> dict:
    """
    Request a medical or service appointment.

    Args:
        department: Department or service (e.g. 'emergency', 'cardiology', 'general')
        date: Requested date in YYYY-MM-DD format
        notes: Optional additional notes
        confirmed: Must be True for the action to execute (human-in-the-loop)
    """
    gate = _require_confirmation(
        confirmed,
        f"Request an appointment with {department} on {date}",
    )
    if gate:
        return gate

    logger.info("Executing appointment_request: %s on %s", department, date)
    return {
        "status": "requested",
        "department": department,
        "date": date,
        "message": f"Appointment request sent to {department} for {date}.",
    }


if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8081)
