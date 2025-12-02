# backend/app/security.py

from fastapi import Header, HTTPException, status
from datetime import datetime, timedelta
import jwt

# Load keys from config
from .config import API_KEY, FERNET_KEY


# =====================================================================
# 1. SIMPLE API KEY CHECK  (Normal API Authentication)
# =====================================================================
def require_api_key(
    api_key: str = Header(None),
    x_api_key: str = Header(None)
):
    """
    Validates API key using either:
    - api_key header
    - x_api_key header
    """
    key = api_key or x_api_key
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return True


# =====================================================================
# 2. ZERO-TRUST GATEWAY (Cloudflare Access-style JWT System)
# =====================================================================
class ZeroTrustGateway:
    def __init__(self):
        # In real production → replace with Redis or database store
        self.service_tokens = {}

    def generate_service_token(
        self,
        user_id: int,
        permissions: list,
        expires_hours: int = 24
    ):
        """
        Generates a signed JWT token that includes:
        - user ID
        - permissions array
        - issued-at timestamp
        - expiration timestamp
        """
        payload = {
            "sub": str(user_id),
            "permissions": permissions,
            "exp": datetime.utcnow() + timedelta(hours=expires_hours),
            "iat": datetime.utcnow(),
            "iss": "zero-trust-gateway"
        }

        token = jwt.encode(payload, FERNET_KEY, algorithm="HS256")

        # Optional runtime tracking
        self.service_tokens[token] = payload

        return token

    def verify_service_token(self, token: str, required_permission: str = None):
        """
        Decodes + verifies a JWT service token.
        Optionally checks if a specific permission is included.
        """
        try:
            payload = jwt.decode(token, FERNET_KEY, algorithms=["HS256"])

            # Check permission if required
            if required_permission:
                if required_permission not in payload.get("permissions", []):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Insufficient permissions"
                    )

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")

        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")


# =====================================================================
# 3. DEPENDENCY FOR FASTAPI ROUTES USING ZERO-TRUST TOKENS
# =====================================================================
async def require_zero_trust(
    token: str = Header(None),
    required_permission: str = None
):
    """
    FastAPI dependency to require a Zero-Trust JWT token.
    Usage:
        @app.get("/admin")
        def admin(payload = Depends(lambda: require_zero_trust(required_permission="admin"))):
            ...
    """
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")

    gateway = ZeroTrustGateway()
    return gateway.verify_service_token(token, required_permission)
