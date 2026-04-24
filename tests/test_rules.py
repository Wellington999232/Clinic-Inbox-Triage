import pytest
from app.rules import check_red_flags, apply_policy_overrides
from app.schemas import Label, Severity

def test_white_lip_triggers_red_flag():
    text = "my lip has gone completely white after filler"
    matched, tags = check_red_flags(text)
    assert matched is True

def test_cant_breathe_triggers_red_flag():
    text = "I cant breathe properly since my treatment"
    matched, tags = check_red_flags(text)
    assert matched is True

def test_vision_loss_triggers_red_flag():
    text = "I cant see out of my left eye since this morning"
    matched, tags = check_red_flags(text)
    assert matched is True

def test_chest_pain_triggers_red_flag():
    text = "I have chest pain since my appointment"
    matched, tags = check_red_flags(text)
    assert matched is True

def test_appointment_no_red_flag():
    text = "can I move my appointment to Thursday please"
    matched, tags = check_red_flags(text)
    assert matched is False

def test_swelling_no_red_flag():
    text = "I have some swelling after my lip filler is that normal"
    matched, tags = check_red_flags(text)
    assert matched is False

def test_red_flag_forces_escalation():
    label, severity, override = apply_policy_overrides(label=Label.routine_clinical_question, severity=Severity.low, confidence=0.9, red_flag_matched=True)
    assert label == Label.red_flag_escalation
    assert severity == Severity.high
    assert override is True

def test_low_confidence_routes_to_urgent():
    label, severity, override = apply_policy_overrides(label=Label.post_treatment_reassurance, severity=Severity.low, confidence=0.3, red_flag_matched=False)
    assert label == Label.urgent_clinical_review
    assert override is True

def test_high_confidence_no_override():
    label, severity, override = apply_policy_overrides(label=Label.scheduling_admin, severity=Severity.low, confidence=0.95, red_flag_matched=False)
    assert label == Label.scheduling_admin
    assert override is False
