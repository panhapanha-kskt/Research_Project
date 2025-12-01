import time
import logging
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .db import Base, engine, SessionLocal
from .models import User
from .schemas import UserCreate, UserOut
from .security import require_api_key, client_id_from_request
from .crypto_utils import encrypt_text, decrypt_text
from .config import RATE_LIMIT_PERIOD, RATE_LIMIT_REQUESTS, LOG_LEVEL

# Create tables
Base.metadata.create_all(bind=engine)

# Simple in-memory rate limiter (for exam/demo only)
_rate_store = {}

app = FastAPI()

# Logging
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("secure-backend")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.middleware("http")
async def audit_and_rate_limit(request: Request, call_next):
    client_id = client_id_from_request(request)
    now = int(time.time())
    window = now // RATE_LIMIT_PERIOD
    key = f"{client_id}:{window}"

    count = _rate_store.get(key, 0) + 1
    _rate_store[key] = count

    if count > RATE_LIMIT_REQUESTS:
        logger.warning("Rate limit exceeded for %s", client_id)
        return JSONResponse(status_code=429, content={"detail": "rate limit exceeded"})

    # Basic audit log
    logger.info("request %s %s by %s", request.method, request.url.path, client_id)

    response = await call_next(request)
    return response


@app.post("/user", dependencies=[Depends(require_api_key)])
def create_user(payload: UserCreate, db: Session = Depends(get_db), request: Request = None):
    # Encrypt sensitive field (email)
    email_enc = encrypt_text(payload.email)
    user = User(name=payload.name.strip(), email_enc=email_enc, age=payload.age)
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("user created id=%s by=%s", user.id, client_id_from_request(request))
    return {
       "message": "User saved successfully!",
       "user": user.as_dict(decrypt_fn=decrypt_text)
    }


@app.get("/users", dependencies=[Depends(require_api_key)])
def get_users(db: Session = Depends(get_db), request: Request = None):
    users = db.query(User).all()
    result = [u.as_dict(decrypt_fn=decrypt_text) for u in users]
    logger.info("users fetched count=%d by=%s", len(result), client_id_from_request(request))
    return result
