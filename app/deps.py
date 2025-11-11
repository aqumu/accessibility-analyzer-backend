# app/deps.py
from fastapi import HTTPException, Header
from jwt import InvalidTokenError
from .auth import verify_token


def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        payload = verify_token(authorization)
        return {
            "id": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get(
                "role", payload.get("app_metadata", {}).get("role", "authenticated")
            ),
            "claims": payload,
        }
    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=str(e))
