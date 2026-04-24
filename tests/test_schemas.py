import pytest
from pydantic import ValidationError
from app.schemas import MessageInput, TriageResult, Label, Severity, ConfidenceMethod

def test_valid_message_input():
    msg = MessageInput(id="msg_001", text="hello")
    assert msg.id == "msg_001"
    assert msg.text == "hello"

def test_message_input_missing_text():
    with pytest.raises(ValidationError):
        MessageInput(id="msg_001")

def test_message_input_missing_id():
    with pytest.raises(ValidationError):
        MessageInput(text="hello")

def test_valid_triage_result():
    result = TriageResult(
        message_id="msg_001",
        primary_label=Label.red_flag_escalation,
        secondary_label=None,
        severity=Severity.high,
        confidence=0.95,
        confidence_method=ConfidenceMethod.heuristic,
        recommended_action="Call patient immediately",
        safe_reply="Please contact the clinic now",
        reasoning_tags=["skin_pallor"],
        policy_override_triggered=True,
    )
    assert result.primary_label == Label.red_flag_escalation
    assert result.severity == Severity.high
    assert result.confidence == 0.95

def test_confidence_out_of_range():
    with pytest.raises(ValidationError):
        TriageResult(
            message_id="msg_001",
            primary_label=Label.scheduling_admin,
            secondary_label=None,
            severity=Severity.low,
            confidence=1.5,
            confidence_method=ConfidenceMethod.heuristic,
            recommended_action="Pass to front desk",
            safe_reply="We will be in touch",
            reasoning_tags=[],
            policy_override_triggered=False,
        )

def test_invalid_label_rejected():
    with pytest.raises(ValidationError):
        TriageResult(
            message_id="msg_001",
            primary_label="made_up_label",
            secondary_label=None,
            severity=Severity.low,
            confidence=0.9,
            confidence_method=ConfidenceMethod.heuristic,
            recommended_action="Pass to front desk",
            safe_reply="We will be in touch",
            reasoning_tags=[],
            policy_override_triggered=False,
        )
