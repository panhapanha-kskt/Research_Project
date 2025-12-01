from fastapi import Header, HTTPException, status, Request
from .config import API_KEY
from typing import Optional

async def require_api_key(x_api_key: Optional[str] = Header(None)):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )
def client_id_from_request(request: Request):
    api_key = request.headers.get("x-api-key")
    if api_key:
        return f"api:{api_key}"
    client = request.client.host if request.client else "unknown"
    return f"ip:{client}"
