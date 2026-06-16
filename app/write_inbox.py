content = '''import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models import PatientMessage, AuditLog
from app.schemas import MessageInput
from app.classifier import classify_message

router = APIRouter(prefix="/inbox", tags=["inbox"])


class PatientSubmission(BaseModel):
    patient_name: str
    patient_email: Optional[str] = None
    patient_phone: Optional[str] = None
    message_text: str


class ReplyRequest(BaseModel):
    message_id: str
    reply_text: str
    replied_by: str


@router.post("/submit")
def submit_message(submission: PatientSubmission, db: Session = Depends(get_db)):
    msg_id = str(uuid.uuid4())
    triage = classify_message(MessageInput(id=msg_id, text=submission.message_text))
    tags = ", ".join(triage.reasoning_tags) if triage.reasoning_tags else ""
    record = PatientMessage(
        id=uuid.UUID(msg_id),
        patient_name=submission.patient_name,
        patient_email=submission.patient_email,
        patient_phone=submission.patient_phone,
        message_text=submission.message_text,
        submitted_at=datetime.utcnow(),
        primary_label=triage.primary_label.value,
        secondary_label=triage.secondary_label.value if triage.secondary_label else None,
        severity=triage.severity.value,
        confidence=triage.confidence,
        recommended_action=triage.recommended_action,
        safe_reply=triage.safe_reply,
        reasoning_tags=tags,
        policy_override_triggered=triage.policy_override_triggered,
        status="pending",
    )
    db.add(record)
    audit = AuditLog(
        id=uuid.uuid4(),
        message_id=msg_id,
        action="classified",
        performed_by="system",
        detail=f"Classified as {triage.primary_label.value} with severity {triage.severity.value}",
        timestamp=datetime.utcnow(),
    )
    db.add(audit)
    db.commit()
    return {
        "message_id": msg_id,
        "status": "received",
        "severity": triage.severity.value,
        "primary_label": triage.primary_label.value,
        "message": "Your message has been received. A member of our team will be in touch shortly."
    }


@router.get("/messages")
def get_messages(db: Session = Depends(get_db)):
    severity_order = {"high": 0, "medium": 1, "low": 2}
    messages = db.query(PatientMessage).all()
    sorted_messages = sorted(
        messages,
        key=lambda m: (severity_order.get(m.severity, 3), m.submitted_at)
    )
    return [
        {
            "id": str(m.id),
            "patient_name": m.patient_name,
            "patient_email": m.patient_email,
            "patient_phone": m.patient_phone,
            "message_text": m.message_text,
            "submitted_at": m.submitted_at.isoformat(),
            "primary_label": m.primary_label,
            "severity": m.severity,
            "confidence": m.confidence,
            "recommended_action": m.recommended_action,
            "safe_reply": m.safe_reply,
            "reasoning_tags": m.reasoning_tags,
            "status": m.status,
            "policy_override_triggered": m.policy_override_triggered,
        }
        for m in sorted_messages
    ]


@router.get("/message/{message_id}")
def get_message(message_id: str, db: Session = Depends(get_db)):
    message = db.query(PatientMessage).filter(
        PatientMessage.id == uuid.UUID(message_id)
    ).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return {
        "id": str(message.id),
        "patient_name": message.patient_name,
        "patient_email": message.patient_email,
        "patient_phone": message.patient_phone,
        "message_text": message.message_text,
        "submitted_at": message.submitted_at.isoformat(),
        "primary_label": message.primary_label,
        "severity": message.severity,
        "confidence": message.confidence,
        "recommended_action": message.recommended_action,
        "safe_reply": message.safe_reply,
        "reasoning_tags": message.reasoning_tags,
        "status": message.status,
        "policy_override_triggered": message.policy_override_triggered,
        "final_reply_sent": message.final_reply_sent,
        "replied_by": message.replied_by,
        "replied_at": message.replied_at.isoformat() if message.replied_at else None,
    }


@router.post("/reply")
def send_reply(request: ReplyRequest, db: Session = Depends(get_db)):
    message = db.query(PatientMessage).filter(
        PatientMessage.id == uuid.UUID(request.message_id)
    ).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    message.final_reply_sent = request.reply_text
    message.replied_by = request.replied_by
    message.replied_at = datetime.utcnow()
    message.status = "replied"
    audit = AuditLog(
        id=uuid.uuid4(),
        message_id=request.message_id,
        action="replied",
        performed_by=request.replied_by,
        detail=f"Reply sent: {request.reply_text[:100]}",
        timestamp=datetime.utcnow(),
    )
    db.add(audit)
    db.commit()
    return {
        "message_id": request.message_id,
        "status": "replied",
        "replied_by": request.replied_by,
        "replied_at": message.replied_at.isoformat(),
    }
'''

with open("app/inbox_router.py", "w") as f:
    f.write(content)
print("Done")