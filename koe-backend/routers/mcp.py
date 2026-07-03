"""
MCP proxy route — backend calls the Koe MCP server on the user's behalf.
Only executes after the user has explicitly confirmed in the frontend dialog.
Logs every tool event (confirmed or cancelled) to BigQuery.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from fastmcp import Client

from config import MCP_SERVER_URL
from middleware.auth import verify_clerk_token
from services import bigquery_service

router = APIRouter()

TOOL_DEFAULTS = {
    "emergency_contact": {
        "contact_type": "family",
        "message": "I need help. Please come.",
    },
    "form_fill": {
        "form_type": "general",
        "fields": {},
    },
    "appointment_request": {
        "department": "general",
        "date": "TBD",
        "notes": "",
    },
}

TOOL_LABELS = {
    "emergency_contact": "Send emergency contact message",
    "form_fill": "Fill form",
    "appointment_request": "Request appointment",
}


class MCPExecuteRequest(BaseModel):
    tool_name: str
    tool_args: dict = {}
    confirmed: bool
    session_id: str = ""


class MCPExecuteResponse(BaseModel):
    status: str
    message: str
    result: dict = {}


@router.post("/execute", response_model=MCPExecuteResponse)
async def execute_mcp_tool(
    request: MCPExecuteRequest,
    user_id: str = Depends(verify_clerk_token),
):
    if request.tool_name not in TOOL_DEFAULTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown tool: {request.tool_name}",
        )

    # Log the event regardless of outcome
    try:
        bigquery_service.log_tool_event(
            tool_name=request.tool_name,
            confirmed=request.confirmed,
            session_id=request.session_id,
        )
    except Exception:
        pass

    if not request.confirmed:
        return MCPExecuteResponse(
            status="cancelled",
            message="Action cancelled by user.",
        )

    # Merge caller args over defaults, always set confirmed=True
    args = {**TOOL_DEFAULTS[request.tool_name], **request.tool_args, "confirmed": True}

    try:
        async with Client(f"{MCP_SERVER_URL}/mcp") as client:
            result = await client.call_tool(request.tool_name, args)
        result_dict = result[0].text if result else {}
        if isinstance(result_dict, str):
            import json
            try:
                result_dict = json.loads(result_dict)
            except Exception:
                result_dict = {"raw": result_dict}

        return MCPExecuteResponse(
            status="executed",
            message=result_dict.get("message", "Action completed."),
            result=result_dict,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"MCP server error: {exc}",
        )
