import logging
from app.doc_structurer_schemas import (
    DocStructurerInput,
    DocStructurerResult,
    VersionMetadata,
    ActionTableRow,
    EscalationRule,
    DocumentSection,
)
from app.doc_structurer_prompts import DOC_STRUCTURER_SYSTEM_PROMPT, build_structurer_message
from app.llm_client import call_llm

logger = logging.getLogger(__name__)


def structure_document(input: DocStructurerInput) -> DocStructurerResult:
    """
    Convert an unstructured clinical document into a standardised format.

    Args:
        input: DocStructurerInput containing document id, title, and content

    Returns:
        DocStructurerResult with all structured components
    """
    logger.info(f"Structuring document: {input.document_id}")

    user_message = build_structurer_message(
        title=input.title,
        content=input.content,
        author=input.author,
        previous_version=input.previous_version,
    )

    try:
        llm_response = call_llm(DOC_STRUCTURER_SYSTEM_PROMPT, user_message)
    except ValueError as e:
        logger.error(f"Doc structurer LLM failure for {input.document_id}: {e}")
        raise

    try:
        version_metadata = VersionMetadata(
            version_number=llm_response["version_metadata"].get("version_number", "1.0"),
            author=llm_response["version_metadata"].get("author", "Clinic Team"),
            review_date=llm_response["version_metadata"].get("review_date", "TBD"),
            status=llm_response["version_metadata"].get("status", "Draft"),
        )

        sections = [
            DocumentSection(
                heading=s["heading"],
                content=s["content"],
            )
            for s in llm_response.get("sections", [])
        ]

        action_table = [
            ActionTableRow(
                who=row["who"],
                what=row["what"],
                when=row["when"],
            )
            for row in llm_response.get("action_table", [])
        ]

        escalation_rules = [
            EscalationRule(
                trigger=rule["trigger"],
                action=rule["action"],
                escalate_to=rule["escalate_to"],
                timeframe=rule["timeframe"],
            )
            for rule in llm_response.get("escalation_rules", [])
        ]

        result = DocStructurerResult(
            document_id=input.document_id,
            title=input.title,
            version_metadata=version_metadata,
            sections=sections,
            action_table=action_table,
            escalation_rules=escalation_rules,
            change_summary=llm_response.get("change_summary"),
            structured_document=llm_response.get("structured_document", ""),
        )

        logger.info(
            f"Document {input.document_id} structured. "
            f"Sections: {len(sections)} | "
            f"Action rows: {len(action_table)} | "
            f"Escalation rules: {len(escalation_rules)}"
        )

        return result

    except (ValueError, KeyError) as e:
        logger.error(f"Doc structurer parse error for {input.document_id}: {e}")
        raise