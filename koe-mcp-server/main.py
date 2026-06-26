from fastmcp import FastMCP

mcp = FastMCP("Koe MCP Server")


@mcp.tool()
async def form_fill(form_type: str, fields: dict) -> dict:
    """Fill a form on behalf of the user. Requires user confirmation."""
    return {"status": "pending_confirmation", "form_type": form_type, "fields": fields}


@mcp.tool()
async def emergency_contact(contact_type: str, message: str) -> dict:
    """Send an emergency contact message. Requires user confirmation."""
    return {"status": "pending_confirmation", "contact_type": contact_type, "message": message}


@mcp.tool()
async def appointment_request(department: str, date: str, notes: str = "") -> dict:
    """Request an appointment. Requires user confirmation."""
    return {"status": "pending_confirmation", "department": department, "date": date, "notes": notes}


if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8081)
