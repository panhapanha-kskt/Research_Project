from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from datetime import datetime
from .db import Base  # <-- IMPORT BASE

class APIAuditLog(Base):
    __tablename__ = 'api_audit_logs'
    
    id = Column(Integer, primary_key=True)
    client_id = Column(String(255))
    endpoint = Column(String(255))
    method = Column(String(10))
    status_code = Column(Integer)
    request_headers = Column(JSON)
    response_time_ms = Column(Integer)
    user_agent = Column(String(500))
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    def as_dict(self):
        return {
            "id": self.id,
            "client_id": self.client_id,
            "endpoint": self.endpoint,
            "method": self.method,
            "status_code": self.status_code,
            "response_time_ms": self.response_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "user_agent": self.user_agent,
            "ip_address": self.ip_address
        }


class APIUsageAnalytics(Base):
    __tablename__ = 'api_usage_analytics'

    id = Column(Integer, primary_key=True)
    date = Column(String(10))
    client_id = Column(String(255))
    endpoint = Column(String(255))
    request_count = Column(Integer, default=0)
    total_response_time = Column(Integer, default=0)

    def as_dict(self):
        return {
            "date": self.date,
            "client_id": self.client_id,
            "endpoint": self.endpoint,
            "request_count": self.request_count,
            "avg_response_time": (
                self.total_response_time / self.request_count
                if self.request_count > 0 else 0
            )
        }


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email_enc = Column(String, nullable=False)
    age = Column(Integer, nullable=False)

    def as_dict(self, decrypt_fn=None):
        return {
            "id": self.id,
            "name": self.name,
            "email": decrypt_fn(self.email_enc) if decrypt_fn else self.email_enc,
            "age": self.age,
        }


class Secret(Base):
    __tablename__ = 'secrets'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, index=True)
    encrypted_value = Column(Text, nullable=False)
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
