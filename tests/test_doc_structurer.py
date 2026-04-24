import pytest
from pydantic import ValidationError
from app.doc_structurer_schemas import (
    DocStructurerInput,
    DocStructurerResult,
    VersionMetadata,
    ActionTableRow,
    EscalationRule,
    DocumentSection,
)


def test_valid_doc_structurer_input():
    input = DocStructurerInput(
        document_id="sop_001",
        title="Vascular Occlusion Protocol",
        content="If patient reports white skin after filler call clinician immediately.",
        author="Sarah",
    )
    assert input.document_id == "sop_001"
    assert input.author == "Sarah"
    assert input.previous_version is None


def test_doc_structurer_input_missing_content():
    with pytest.raises(ValidationError):
        DocStructurerInput(
            document_id="sop_001",
            title="Test Protocol",
        )


def test_version_metadata_valid():
    meta = VersionMetadata(
        version_number="1.0",
        author="Clinic Team",
        review_date="2026-01-01",
        status="Draft",
    )
    assert meta.version_number == "1.0"
    assert meta.status == "Draft"


def test_action_table_row_valid():
    row = ActionTableRow(
        who="Receptionist",
        what="Transfer call to clinician immediately",
        when="Immediately",
    )
    assert row.who == "Receptionist"
    assert row.when == "Immediately"


def test_escalation_rule_valid():
    rule = EscalationRule(
        trigger="Patient reports skin blanching",
        action="Contact clinician immediately",
        escalate_to="Senior Clinician",
        timeframe="Immediate",
    )
    assert rule.trigger == "Patient reports skin blanching"
    assert rule.escalate_to == "Senior Clinician"


def test_document_section_valid():
    section = DocumentSection(
        heading="Purpose",
        content="This protocol defines the response to suspected vascular occlusion.",
    )
    assert section.heading == "Purpose"
    assert len(section.content) > 0


def test_doc_structurer_result_valid():
    result = DocStructurerResult(
        document_id="sop_001",
        title="Test Protocol",
        version_metadata=VersionMetadata(
            version_number="1.0",
            author="Test Author",
            review_date="2026-01-01",
            status="Draft",
        ),
        sections=[
            DocumentSection(heading="Purpose", content="Test purpose.")
        ],
        action_table=[
            ActionTableRow(who="Clinician", what="Review patient", when="Immediately")
        ],
        escalation_rules=[
            EscalationRule(
                trigger="Skin blanching",
                action="Call clinician",
                escalate_to="Senior Clinician",
                timeframe="Immediate",
            )
        ],
        change_summary=None,
        structured_document="# Test Protocol\n\n## Purpose\nTest purpose.",
    )
    assert result.document_id == "sop_001"
    assert len(result.sections) == 1
    assert len(result.action_table) == 1
    assert len(result.escalation_rules) == 1
    assert result.change_summary is None