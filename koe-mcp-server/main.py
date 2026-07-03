"""
Koe MCP Server — FastMCP on Cloud Run

Exposes three tools for external action:
  - form_fill
  - emergency_contact
  - appointment_request

All tools require confirmed=True (Safety/Consent Agent — Day 4 ADK pattern).
Human-in-the-loop: the Koe frontend shows a confirmation dialog before
the backend ever calls these tools with confirmed=True.

Transport: streamable HTTP so the backend can call tools via fastmcp.Client.
"""

import logging

from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP(
    "Koe MCP Server",
    instructions=(
        "You are the Koe external action server for deaf and mute users. "
        "Never execute any tool without confirmed=True. "
        "Always surface a confirmation step before any external action."
    ),
)


def _require_confirmation(confirmed: bool, action_description: str) -> dict | None:
    if not confirmed:
        return {
            "status": "awaiting_confirmation",
            "message": f"Please confirm: {action_description}",
            "requires_user_action": True,
        }
    return None


@mcp.tool()
async def form_fill(
    form_type: str,
    fields: dict,
    confirmed: bool = False,
) -> dict:
    """
    Fill a form on behalf of the user.

    Args:
        form_type: Type of form (e.g. hospital_registration, bank_account, id_card)
        fields: Dictionary of field names to values
        confirmed: Must be True for the action to execute (human-in-the-loop)
    """
    gate = _require_confirmation(confirmed, f"Fill a {form_type} form")
    if gate:
        return gate

    logger.info("Executing form_fill: %s", form_type)
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
        contact_type: Who to contact: family, ambulance, police, hospital_staff
        message: The message to send
        confirmed: Must be True for the action to execute (human-in-the-loop)
    """
    gate = _require_confirmation(confirmed, f"Send emergency message to {contact_type}")
    if gate:
        return gate

    logger.info("Executing emergency_contact: %s", contact_type)
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
        department: Department or service (e.g. emergency, cardiology, general)
        date: Requested date in YYYY-MM-DD format
        notes: Optional additional notes
        confirmed: Must be True for the action to execute (human-in-the-loop)
    """
    gate = _require_confirmation(confirmed, f"Request appointment with {department} on {date}")
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
    mcp.run(transport="http", host="0.0.0.0", port=8081)
