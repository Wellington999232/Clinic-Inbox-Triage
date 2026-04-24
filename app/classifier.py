# app/classifier.py
# Orchestrates the full triage pipeline.
# This is the main entry point for classifying a patient message.
#
# Pipeline order:
# 1. Regex red-flag pre-screen
# 2. LLM classification
# 3. Policy override layer
# 4. Pydantic output validation
# 5. Return structured TriageResult

import logging
from app.schemas import MessageInput, TriageResult, Label, Severity, ConfidenceMethod
from app.rules import check_red_flags, apply_policy_overrides
from app.prompts import SYSTEM_PROMPT, build_user_message
from app.llm_client import call_llm

# Set up logging so every classification decision is recorded
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)
logger = logging.getLogger(__name__)


def classify_message(message: MessageInput) -> TriageResult:
    """
    Run the full triage pipeline on a single patient message.

    Args:
        message: A MessageInput object containing id and text

    Returns:
        A validated TriageResult object
    """

    logger.info(f"Classifying message: {message.id}")

    # --- Step 1: Regex red-flag pre-screen ---
    red_flag_matched, matched_tags = check_red_flags(message.text)

    if red_flag_matched:
        logger.warning(
            f"Red flag matched for message {message.id}. "
            f"Patterns: {matched_tags}"
        )

    # --- Step 2: LLM classification ---
    user_message = build_user_message(message.text)

    try:
        llm_response = call_llm(SYSTEM_PROMPT, user_message)
    except ValueError as e:
        # LLM returned invalid JSON — route to urgent review
        logger.error(f"LLM JSON parse failure for {message.id}: {e}")
        return _fallback_result(message.id, str(e))

    # --- Step 3: Extract LLM output fields ---
    try:
        primary_label = Label(llm_response.get("primary_label"))
        secondary_label_raw = llm_response.get("secondary_label")
        secondary_label = Label(secondary_label_raw) if secondary_label_raw else None
        severity = Severity(llm_response.get("severity", "low"))
        confidence = float(llm_response.get("confidence", 0.5))
        recommended_action = llm_response.get("recommended_action", "")
        safe_reply = llm_response.get("safe_reply", "")
        reasoning_tags = llm_response.get("reasoning_tags", [])

    except (ValueError, KeyError) as e:
        logger.error(f"LLM response field error for {message.id}: {e}")
        return _fallback_result(message.id, str(e))

    # --- Step 4: Apply policy overrides ---
    final_label, final_severity, override_triggered = apply_policy_overrides(
        label=primary_label,
        severity=severity,
        confidence=confidence,
        red_flag_matched=red_flag_matched,
    )

    if override_triggered:
        logger.warning(
            f"Policy override triggered for message {message.id}. "
            f"Original label: {primary_label}, "
            f"Final label: {final_label}"
        )

    # Merge matched red-flag tags into reasoning tags
    if matched_tags:
        reasoning_tags = list(set(reasoning_tags + ["red_flag_keyword_match"]))

    # --- Step 5: Build and validate the result ---
    result = TriageResult(
        message_id=message.id,
        primary_label=final_label,
        secondary_label=secondary_label,
        severity=final_severity,
        confidence=confidence,
        confidence_method=ConfidenceMethod.heuristic,
        recommended_action=recommended_action,
        safe_reply=safe_reply,
        reasoning_tags=reasoning_tags,
        policy_override_triggered=override_triggered,
    )

    logger.info(
        f"Message {message.id} classified as {final_label} "
        f"with severity {final_severity} and confidence {confidence}"
    )

    return result


def _fallback_result(message_id: str, error_detail: str) -> TriageResult:
    """
    Returns a safe fallback result when the LLM fails.
    Always routes to urgent_clinical_review so no message is lost.
    """
    return TriageResult(
        message_id=message_id,
        primary_label=Label.urgent_clinical_review,
        secondary_label=None,
        severity=Severity.medium,
        confidence=0.0,
        confidence_method=ConfidenceMethod.heuristic,
        recommended_action="LLM classification failed. Manual review required.",
        safe_reply="Thank you for your message. A member of our team will review this shortly.",
        reasoning_tags=["llm_failure", "fallback_applied"],
        policy_override_triggered=True,
    )