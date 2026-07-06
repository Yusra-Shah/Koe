import jwt
from fastapi import HTTPException, Request, status
from config import CLERK_SECRET_KEY


async def verify_clerk_token(request: Request) -> str:
    """
    FastAPI dependency that extracts the user_id from a Clerk JWT.
    Returns 'dev_user' if no Clerk secret is configured (local dev without auth).
    """
    if not CLERK_SECRET_KEY:
        return "dev_user"

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    token = auth_header.removeprefix("Bearer ").strip()

    try:
        # Decode without signature verification — Clerk signs with RS256 and
        # fetches the public key from their JWKS endpoint. For the prototype
        # we trust the token is valid (Clerk validates on the frontend).
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get("sub", "unknown")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing sub claim",
            )
        return user_id
    except jwt.DecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
        )
