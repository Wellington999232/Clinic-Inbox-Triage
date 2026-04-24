# app/schemas.py
# Defines the input and output data shapes for the triage system.
# Pydantic validates these automatically on every request and response.

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# --- Enums ---
# These are the only values allowed for each field.
# If the LLM returns something outside these values, validation will fail.

class Label(str, Enum):
    red_flag_escalation = "red_flag_escalation"
    urgent_clinical_review = "urgent_clinical_review"
    routine_clinical_question = "routine_clinical_question"
    post_treatment_reassurance = "post_treatment_reassurance"
    scheduling_admin = "scheduling_admin"
    billing_payment = "billing_payment"


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ConfidenceMethod(str, Enum):
    llm_logprob = "llm_logprob"
    softmax = "softmax"
    heuristic = "heuristic"


# --- Input Schema ---
# This is the shape of every message coming into the system.

class MessageInput(BaseModel):
    id: str = Field(..., description="Unique message identifier")
    text: str = Field(..., description="The raw patient message text")


# --- Output Schema ---
# This is the shape of every classification result leaving the system.

class TriageResult(BaseModel):
    message_id: str = Field(..., description="ID of the message that was classified")
    primary_label: Label = Field(..., description="Primary classification label")
    secondary_label: Optional[Label] = Field(None, description="Secondary label if applicable")
    severity: Severity = Field(..., description="Severity score")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    confidence_method: ConfidenceMethod = Field(..., description="Method used to derive confidence score")
    recommended_action: str = Field(..., description="Recommended next action for clinic staff")
    safe_reply: str = Field(..., description="Safe draft reply for the patient")
    reasoning_tags: list[str] = Field(default_factory=list, description="Compact audit tags")
    policy_override_triggered: bool = Field(False, description="Whether a policy rule overrode the LLM output")