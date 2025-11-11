import jwt
from datetime import datetime, timedelta
from app.config import settings  # make sure settings.supabase_jwt_secret exists

# Supabase Auth user info
user_id = "05ccdfa5-6eec-4c3b-86db-28262ce0432f"
audience = "authenticated"

# Build JWT payload
payload = {
    "sub": user_id,                # user UUID from Auth
    "aud": audience,               # must match your verify function
    "exp": datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
}

# Encode the token
token = jwt.encode(payload, settings.supabase_jwt_secret, algorithm="HS256")

print("Swagger-ready token:")
print(f"Bearer {token}")

