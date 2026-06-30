from fastapi import HTTPException, Request, status
from clerk_backend_api import Clerk
from clerk_backend_api.models import RequestState
from config import CLERK_SECRET_KEY

_clerk = None


def _get_clerk() -> Clerk:
    global _clerk
    if _clerk is None:
        _clerk = Clerk(bearer_auth=CLERK_SECRET_KEY)
    return _clerk


async def verify_clerk_token(request: Request) -> str:
    """
    FastAPI dependency that verifies the Clerk JWT from the Authorization header.
    Returns the authenticated user_id.
    Raises 401 if the token is missing or invalid.
    """
    if not CLERK_SECRET_KEY:
        return "dev_user"

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )

    token = auth_header.removeprefix("Bearer ").strip()

    try:
        clerk = _get_clerk()
        request_state: RequestState = clerk.authenticate_request(
            request,
            authorized_parties=[
                "http://localhost:5173",
                "http://localhost:3000",
            ],
        )
        if not request_state.is_signed_in or not request_state.payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        return request_state.payload.get("sub", "unknown")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {exc}",
        )
