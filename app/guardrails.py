import logging
from app.guardrail_schemas import (
    GuardrailEvalInput,
    GuardrailEvalResult,
    GuardrailCheckResult,
    GuardrailStatus,
)
from app.guardrail_prompts import GUARDRAIL_SYSTEM_PROMPT, build_guardrail_message
from app.llm_client import call_llm

logger = logging.getLogger(__name__)


def evaluate_reply(input: GuardrailEvalInput) -> GuardrailEvalResult:
    """
    Run all five guardrail checks on a draft reply.

    Args:
        input: GuardrailEvalInput containing the message, label, severity, and reply

    Returns:
        GuardrailEvalResult with check results and approval status
    """
    logger.info(f"Evaluating reply for message: {input.message_id}")

    user_message = build_guardrail_message(
        patient_message=input.patient_message,
        primary_label=input.primary_label,
        severity=input.severity,
        reply=input.reply,
    )

    try:
        llm_response = call_llm(GUARDRAIL_SYSTEM_PROMPT, user_message)
    except ValueError as e:
        logger.error(f"Guardrail LLM failure for {input.message_id}: {e}")
        return _fallback_result(input.message_id)

    try:
        checks = []
        for check in llm_response.get("checks", []):
            checks.append(GuardrailCheckResult(
                check_name=check["check_name"],
                status=GuardrailStatus(check["status"]),
                reason=check["reason"],
                flagged_text=check.get("flagged_text"),
            ))

        reply_approved = llm_response.get("reply_approved", False)
        overall_status = GuardrailStatus(llm_response.get("overall_status", "fail"))
        revised_reply = llm_response.get("revised_reply")

        result = GuardrailEvalResult(
            message_id=input.message_id,
            reply_approved=reply_approved,
            checks=checks,
            overall_status=overall_status,
            revised_reply=revised_reply,
        )

        logger.info(
            f"Guardrail result for {input.message_id}: "
            f"{overall_status} | approved={reply_approved}"
        )

        return result

    except (ValueError, KeyError) as e:
        logger.error(f"Guardrail response parse error for {input.message_id}: {e}")
        return _fallback_result(input.message_id)


def _fallback_result(message_id: str) -> GuardrailEvalResult:
    """
    Safe fallback when the guardrail LLM fails.
    Blocks the reply from being sent until manual review.
    """
    return GuardrailEvalResult(
        message_id=message_id,
        reply_approved=False,
        checks=[
            GuardrailCheckResult(
                check_name="system_error",
                status=GuardrailStatus.fail_check,
                reason="Guardrail evaluation failed. Manual review required.",
                flagged_text=None,
            )
        ],
        overall_status=GuardrailStatus.fail_check,
        revised_reply=None,
    )
