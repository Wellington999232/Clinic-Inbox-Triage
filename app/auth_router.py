import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import Clinician
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    setup_key: str


class LoginRequest(BaseModel):
    email: str
    password: str


SETUP_KEY = "wellington-clinic-setup-2026"


@router.post("/register")
def register_clinician(request: RegisterRequest, db: Session = Depends(get_db)):
    if request.setup_key != SETUP_KEY:
        raise HTTPException(status_code=403, detail="Invalid setup key")

    existing = db.query(Clinician).filter(Clinician.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="A clinician with this email already exists")

    clinician = Clinician(
        id=uuid.uuid4(),
        name=request.name,
        email=request.email,
        hashed_password=hash_password(request.password),
        is_active=True,
        created_at=datetime.utcnow(),
    )
    db.add(clinician)
    db.commit()

    return {"status": "created", "email": clinician.email}


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    clinician = db.query(Clinician).filter(Clinician.email == request.email).first()

    if not clinician or not verify_password(request.password, clinician.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    if not clinician.is_active:
        raise HTTPException(status_code=401, detail="This account has been deactivated")

    clinician.last_login = datetime.utcnow()
    db.commit()

    token = create_access_token(str(clinician.id), clinician.email)

    return {
        "access_token": token,
        "token_type": "bearer",
        "name": clinician.name,
        "email": clinician.email,
    }
