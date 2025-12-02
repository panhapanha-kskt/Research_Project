from fastapi import FastAPI, Depends, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import time
import logging

from .db import Base, engine, SessionLocal
from .models import User, APIAuditLog, APIUsageAnalytics
from .schemas import UserCreate
from .crypto_utils import encrypt_text, decrypt_text
from .config import RATE_LIMIT_PERIOD, RATE_LIMIT_REQUESTS, LOG_LEVEL
from .security import require_api_key, require_zero_trust, ZeroTrustGateway
from .secrets_manager import SecretsManager

# Create database tables
Base.metadata.create_all(bind=engine)

zero_trust = ZeroTrustGateway()

app = FastAPI()

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("secure-backend")


# -----------------------------------------------------
# DATABASE SESSION
# -----------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------------------------------
# Utility: Collect client ID
# -----------------------------------------------------
def client_id_from_request(request: Request):
    return request.headers.get("x-api-key", "anonymous")


# -----------------------------------------------------
# TOKEN GENERATION
# -----------------------------------------------------
@app.post("/auth/token")
def generate_token(
    ok: bool = Depends(require_api_key)     # fixed signature
):
    permissions = [
        "read:users",
        "write:users",
        "read:secrets",
        "manage:secrets"
    ]

    # For demo: pretend user_id=1
    token = zero_trust.generate_service_token(user_id=1, permissions=permissions)
    return {"access_token": token, "token_type": "bearer"}


# -----------------------------------------------------
# USERS
# -----------------------------------------------------
@app.get("/users/me")
def get_current_user(payload: dict = Depends(require_zero_trust)):
    db = SessionLocal()
    user = db.query(User).filter(User.id == int(payload['sub'])).first()
    db.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user.as_dict(decrypt_fn=decrypt_text)


@app.post("/user", dependencies=[Depends(require_api_key)])
def create_user(payload: UserCreate, db: Session = Depends(get_db), request: Request = None):
    email_enc = encrypt_text(payload.email)
    user = User(name=payload.name, email_enc=email_enc, age=payload.age)
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info("user created id=%s by=%s", user.id, client_id_from_request(request))
    return {"message": "User saved successfully!", "user": user.as_dict(decrypt_fn=decrypt_text)}


@app.get("/users", dependencies=[Depends(require_api_key)])
def get_users(db: Session = Depends(get_db), request: Request = None):
    users = db.query(User).all()
    return [u.as_dict(decrypt_fn=decrypt_text) for u in users]


# -----------------------------------------------------
# ANALYTICS
# -----------------------------------------------------
@app.get("/analytics/overview", dependencies=[Depends(require_api_key)])
def get_analytics_overview(db: Session = Depends(get_db)):

    today = datetime.utcnow().strftime('%Y-%m-%d')

    total_today = db.query(APIAuditLog).filter(
        APIAuditLog.timestamp >= datetime.utcnow().date()
    ).count()

    avg_response = db.query(func.avg(APIAuditLog.response_time_ms)).scalar() or 0

    top_endpoints = db.query(
        APIAuditLog.endpoint,
        func.count(APIAuditLog.id)
    ).group_by(APIAuditLog.endpoint).limit(5).all()

    return {
        "date": today,
        "total_requests": total_today,
        "avg_response_time_ms": round(avg_response, 2),
        "top_endpoints": [{"endpoint": e, "count": c} for e, c in top_endpoints]
    }


@app.get("/analytics/logs", dependencies=[Depends(require_api_key)])
def get_audit_logs(db: Session = Depends(get_db), limit: int = 100):
    logs = db.query(APIAuditLog).order_by(APIAuditLog.timestamp.desc()).limit(limit).all()
    return [log.as_dict() for log in logs]


# -----------------------------------------------------
# SECRETS MANAGEMENT
# -----------------------------------------------------
@app.post("/secrets", dependencies=[Depends(require_zero_trust)])
def create_secret(
    name: str, value: str, description: str = "",
    db: Session = Depends(get_db),
    payload: dict = Depends(require_zero_trust)
):
    if "manage:secrets" not in payload["permissions"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    manager = SecretsManager(db)
    secret = manager.create_secret(name, value, description, int(payload['sub']))
    return {"message": "Secret created", "secret": secret}


@app.get("/secrets/{name}", dependencies=[Depends(require_zero_trust)])
def get_secret(name: str, db: Session = Depends(get_db), payload: dict = Depends(require_zero_trust)):
    manager = SecretsManager(db)
    return manager.get_secret(name)


@app.post("/secrets/{name}/rotate", dependencies=[Depends(require_zero_trust)])
def rotate_secret(name: str, new_value: str, db: Session = Depends(get_db), payload: dict = Depends(require_zero_trust)):
    manager = SecretsManager(db)
    return manager.rotate_secret(name, new_value)
