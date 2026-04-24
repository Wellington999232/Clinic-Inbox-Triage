from pydantic import BaseModel, Field
from typing import Optional


class SimplifierInput(BaseModel):
    document_id: str = Field(..., description="Unique identifier for the document")
    title: str = Field(..., description="Title of the document")
    content: str = Field(..., description="The clinical document text to simplify")
    treatment_type: Optional[str] = Field(None, description="Type of treatment e.g. lip filler, botox")


class SMSMessage(BaseModel):
    sequence: int = Field(..., description="Message number in sequence")
    text: str = Field(..., description="SMS message text under 160 characters")
    character_count: int = Field(..., description="Character count of the message")


class FAQItem(BaseModel):
    question: str = Field(..., description="Patient question")
    answer: str = Field(..., description="Plain language answer")


class ChecklistItem(BaseModel):
    timeframe: str = Field(..., description="When to do this e.g. first 24 hours")
    instruction: str = Field(..., description="What to do")
    is_warning: bool = Field(False, description="True if this is a warning or red flag")


class SimplifierResult(BaseModel):
    document_id: str
    title: str
    treatment_type: Optional[str]
    plain_language: str = Field(..., description="Clear jargon-free version")
    grade6_version: str = Field(..., description="Flesch-Kincaid Grade 6 reading level version")
    checklist: list[ChecklistItem] = Field(..., description="Structured aftercare checklist")
    faq: list[FAQItem] = Field(..., description="FAQ format question and answer pairs")
    sms_messages: list[SMSMessage] = Field(..., description="SMS follow-up messages under 160 chars each")
    flesch_kincaid_grade: Optional[float] = Field(None, description="Calculated FK grade of grade6_version")