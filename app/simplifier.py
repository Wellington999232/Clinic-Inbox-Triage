import logging
from app.simplifier_schemas import (
    SimplifierInput,
    SimplifierResult,
    ChecklistItem,
    FAQItem,
    SMSMessage,
)
from app.simplifier_prompts import SIMPLIFIER_SYSTEM_PROMPT, build_simplifier_message
from app.llm_client import call_llm

logger = logging.getLogger(__name__)


def calculate_fk_grade(text: str) -> float:
    """
    Calculate an approximate Flesch-Kincaid Grade Level score.
    FK Grade = 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
    """
    sentences = max(1, text.count('.') + text.count('!') + text.count('?'))
    words = text.split()
    word_count = max(1, len(words))

    def count_syllables(word):
        word = word.lower().strip(".,!?;:")
        if len(word) <= 3:
            return 1
        count = 0
        vowels = "aeiouy"
        prev_was_vowel = False
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                count += 1
            prev_was_vowel = is_vowel
        if word.endswith('e'):
            count -= 1
        return max(1, count)

    syllable_count = sum(count_syllables(w) for w in words)
    asl = word_count / sentences
    asw = syllable_count / word_count
    fk_grade = 0.39 * asl + 11.8 * asw - 15.59
    return round(fk_grade, 1)


def simplify_document(input: SimplifierInput) -> SimplifierResult:
    """
    Convert a clinical aftercare document into five simplified formats.

    Args:
        input: SimplifierInput containing document id, title, and content

    Returns:
        SimplifierResult with all five output formats
    """
    logger.info(f"Simplifying document: {input.document_id}")

    user_message = build_simplifier_message(
        title=input.title,
        content=input.content,
        treatment_type=input.treatment_type,
    )

    try:
        llm_response = call_llm(SIMPLIFIER_SYSTEM_PROMPT, user_message)
    except ValueError as e:
        logger.error(f"Simplifier LLM failure for {input.document_id}: {e}")
        raise

    try:
        checklist = [
            ChecklistItem(
                timeframe=item["timeframe"],
                instruction=item["instruction"],
                is_warning=item.get("is_warning", False),
            )
            for item in llm_response.get("checklist", [])
        ]

        faq = [
            FAQItem(
                question=item["question"],
                answer=item["answer"],
            )
            for item in llm_response.get("faq", [])
        ]

        sms_messages = [
            SMSMessage(
                sequence=item["sequence"],
                text=item["text"],
                character_count=len(item["text"]),
            )
            for item in llm_response.get("sms_messages", [])
        ]

        grade6_text = llm_response.get("grade6_version", "")
        fk_grade = calculate_fk_grade(grade6_text)

        result = SimplifierResult(
            document_id=input.document_id,
            title=input.title,
            treatment_type=input.treatment_type,
            plain_language=llm_response.get("plain_language", ""),
            grade6_version=grade6_text,
            checklist=checklist,
            faq=faq,
            sms_messages=sms_messages,
            flesch_kincaid_grade=fk_grade,
        )

        logger.info(
            f"Document {input.document_id} simplified. "
            f"FK grade: {fk_grade} | "
            f"Checklist items: {len(checklist)} | "
            f"FAQ items: {len(faq)} | "
            f"SMS messages: {len(sms_messages)}"
        )

        return result

    except (ValueError, KeyError) as e:
        logger.error(f"Simplifier response parse error for {input.document_id}: {e}")
        raise


def _fallback_result(document_id: str, title: str) -> SimplifierResult:
    """
    Safe fallback when the simplifier LLM fails.
    """
    return SimplifierResult(
        document_id=document_id,
        title=title,
        treatment_type=None,
        plain_language="Simplification failed. Please review the original document.",
        grade6_version="Simplification failed. Please review the original document.",
        checklist=[],
        faq=[],
        sms_messages=[],
        flesch_kincaid_grade=None,
    )