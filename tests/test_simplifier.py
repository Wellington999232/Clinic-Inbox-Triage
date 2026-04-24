import pytest
from pydantic import ValidationError
from app.simplifier import calculate_fk_grade
from app.simplifier_schemas import SimplifierInput, SMSMessage, ChecklistItem


def test_fk_grade_simple_text():
    text = "Do not touch your lips. Avoid alcohol today. Call us if you have pain."
    grade = calculate_fk_grade(text)
    assert grade < 6.0


def test_fk_grade_complex_text():
    text = "Post-procedural contraindications include periorbital manipulation and strenuous cardiovascular exertion."
    grade = calculate_fk_grade(text)
    assert grade > 6.0


def test_simplifier_input_valid():
    input = SimplifierInput(
        document_id="doc_001",
        title="Lip Filler Aftercare",
        content="Do not touch your lips for 24 hours.",
        treatment_type="lip filler",
    )
    assert input.document_id == "doc_001"
    assert input.treatment_type == "lip filler"


def test_simplifier_input_missing_content():
    with pytest.raises(ValidationError):
        SimplifierInput(
            document_id="doc_001",
            title="Test",
        )


def test_sms_character_count():
    msg = SMSMessage(
        sequence=1,
        text="Day 1: Do not touch your lips.",
        character_count=30,
    )
    assert msg.character_count <= 160


def test_checklist_warning_flag():
    item = ChecklistItem(
        timeframe="First 24 hours",
        instruction="Seek help if skin turns white.",
        is_warning=True,
    )
    assert item.is_warning is True