from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class GuardrailStatus(str, Enum):
    pass_check = "pass"
    fail_check = "fail"
    warn_check = "warn"


class GuardrailCheckResult(BaseModel):
    check_name: str = Field(..., description="Name of the guardrail check")
    status: GuardrailStatus = Field(..., description="pass, fail, or warn")
    reason: str = Field(..., description="Why this check passed, failed, or warned")
    flagged_text: Optional[str] = Field(None, description="The specific text that triggered the flag")


class GuardrailEvalInput(BaseModel):
    message_id: str = Field(..., description="ID of the original patient message")
    patient_message: str = Field(..., description="The original patient message text")
    primary_label: str = Field(..., description="The classification label assigned")
    severity: str = Field(..., description="The severity assigned")
    reply: str = Field(..., description="The draft reply to evaluate")


class GuardrailEvalResult(BaseModel):
    message_id: str
    reply_approved: bool = Field(..., description="True if reply passed all checks")
    checks: list[GuardrailCheckResult] = Field(..., description="Results of each individual check")
    overall_status: GuardrailStatus = Field(..., description="Overall pass, warn, or fail")
    revised_reply: Optional[str] = Field(None, description="Safer alternative reply if original failed")
