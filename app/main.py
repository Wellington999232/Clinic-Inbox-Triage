from fastapi import FastAPI, HTTPException
from app.schemas import MessageInput, TriageResult
from app.classifier import classify_message
from app.guardrail_schemas import GuardrailEvalInput, GuardrailEvalResult
from app.guardrails import evaluate_reply
from app.simplifier_schemas import SimplifierInput, SimplifierResult
from app.simplifier import simplify_document
from app.doc_structurer_schemas import DocStructurerInput, DocStructurerResult
from app.doc_structurer import structure_document
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Clinic Inbox Triage Assistant",
    description="Classifies patient messages, evaluates replies, simplifies documents, and structures clinical SOPs.",
    version="4.0.0",
)


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Clinic Inbox Triage Assistant",
        "version": "4.0.0",
    }


@app.post("/classify", response_model=TriageResult)
def classify(message: MessageInput):
    try:
        result = classify_message(message)
        return result
    except Exception as e:
        logger.error(f"Unhandled error classifying message {message.id}: {e}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@app.post("/classify/batch", response_model=list[TriageResult])
def classify_batch(messages: list[MessageInput]):
    if len(messages) > 50:
        raise HTTPException(status_code=400, detail="Batch size cannot exceed 50 messages.")
    results = []
    for message in messages:
        try:
            result = classify_message(message)
            results.append(result)
        except Exception as e:
            logger.error(f"Batch classification error for {message.id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Batch classification failed on message {message.id}: {str(e)}"
            )
    return results


@app.post("/guardrail", response_model=GuardrailEvalResult)
def guardrail(input: GuardrailEvalInput):
    try:
        result = evaluate_reply(input)
        return result
    except Exception as e:
        logger.error(f"Unhandled error in guardrail evaluation for {input.message_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Guardrail evaluation failed: {str(e)}")


@app.post("/classify-and-evaluate", response_model=dict)
def classify_and_evaluate(message: MessageInput):
    try:
        triage = classify_message(message)
        guardrail_input = GuardrailEvalInput(
            message_id=message.id,
            patient_message=message.text,
            primary_label=triage.primary_label.value,
            severity=triage.severity.value,
            reply=triage.safe_reply,
        )
        guardrail_result = evaluate_reply(guardrail_input)
        return {
            "triage": triage.model_dump(),
            "guardrail": guardrail_result.model_dump(),
        }
    except Exception as e:
        logger.error(f"Pipeline error for {message.id}: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")


@app.post("/simplify", response_model=SimplifierResult)
def simplify(input: SimplifierInput):
    """
    Convert a clinical aftercare document into five simplified formats:
    plain language, Grade 6 reading level, checklist, FAQ, and SMS messages.
    """
    try:
        result = simplify_document(input)
        return result
    except Exception as e:
        logger.error(f"Simplifier error for {input.document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Simplification failed: {str(e)}")


@app.post("/structure", response_model=DocStructurerResult)
def structure(input: DocStructurerInput):
    """
    Convert an unstructured clinical SOP or protocol draft into a
    standardised document with sections, action table, escalation rules,
    and version metadata.
    """
    try:
        result = structure_document(input)
        return result
    except Exception as e:
        logger.error(f"Doc structurer error for {input.document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Document structuring failed: {str(e)}")