from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import ExpiredSignatureError, PyJWTError, InvalidTokenError
from app.config import settings

security = HTTPBearer()

SUPABASE_JWT_SECRET = settings.supabase_jwt_secret
SUPABASE_AUDIENCE = getattr(settings, "supabase_aud", "authenticated")

def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    """
    Validates a Supabase JWT and returns user UUID (sub).
    Works in Swagger, Postman, and frontend (Authorization header).
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience=SUPABASE_AUDIENCE,
        )
        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenError("Missing 'sub' in JWT payload")
        return user_id

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
