import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class PatientMessage(Base):
    __tablename__ = "patient_messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_name = Column(String(255), nullable=False)
    patient_email = Column(String(255), nullable=True)
    patient_phone = Column(String(50), nullable=True)
    message_text = Column(Text, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    primary_label = Column(String(100), nullable=True)
    secondary_label = Column(String(100), nullable=True)
    severity = Column(String(20), nullable=True)
    confidence = Column(Float, nullable=True)
    recommended_action = Column(Text, nullable=True)
    safe_reply = Column(Text, nullable=True)
    reasoning_tags = Column(Text, nullable=True)
    policy_override_triggered = Column(Boolean, default=False)
    status = Column(String(20), default="pending")
    reviewed_at = Column(DateTime, nullable=True)
    replied_at = Column(DateTime, nullable=True)
    final_reply_sent = Column(Text, nullable=True)
    replied_by = Column(String(255), nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(String(255), nullable=False)
    action = Column(String(100), nullable=False)
    performed_by = Column(String(255), nullable=True)
    detail = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Clinician(Base):
    __tablename__ = "clinicians"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
