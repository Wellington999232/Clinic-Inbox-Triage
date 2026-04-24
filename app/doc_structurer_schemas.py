from pydantic import BaseModel, Field
from typing import Optional


class VersionMetadata(BaseModel):
    version_number: str = Field(..., description="Document version e.g. 1.0, 2.1")
    author: str = Field(..., description="Document author or department")
    review_date: str = Field(..., description="Next scheduled review date")
    status: str = Field(..., description="Draft, Active, or Archived")


class ActionTableRow(BaseModel):
    who: str = Field(..., description="Who is responsible")
    what: str = Field(..., description="What action they must take")
    when: str = Field(..., description="When they must take it")


class EscalationRule(BaseModel):
    trigger: str = Field(..., description="What condition triggers escalation")
    action: str = Field(..., description="What action must be taken")
    escalate_to: str = Field(..., description="Who to escalate to")
    timeframe: str = Field(..., description="How quickly escalation must happen")


class DocumentSection(BaseModel):
    heading: str = Field(..., description="Section heading")
    content: str = Field(..., description="Section content in plain prose")


class DocStructurerInput(BaseModel):
    document_id: str = Field(..., description="Unique document identifier")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="The raw unstructured document text")
    author: Optional[str] = Field(None, description="Document author if known")
    previous_version: Optional[str] = Field(None, description="Previous version content for change summary")


class DocStructurerResult(BaseModel):
    document_id: str
    title: str
    version_metadata: VersionMetadata
    sections: list[DocumentSection] = Field(..., description="Structured sections of the document")
    action_table: list[ActionTableRow] = Field(..., description="Who does what and when")
    escalation_rules: list[EscalationRule] = Field(..., description="Extracted escalation rules")
    change_summary: Optional[str] = Field(None, description="Summary of changes from previous version")
    structured_document: str = Field(..., description="Full structured document as formatted text")