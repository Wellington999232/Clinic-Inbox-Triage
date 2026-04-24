# Clinic Inbox Triage Assistant

An AI-powered clinical operations toolkit for aesthetic clinics. Built across four projects, each adding a new layer of capability on top of a shared foundation.

---

## What It Does

| Endpoint | What it does |
|---|---|
| `POST /classify` | Classifies incoming patient messages into 6 urgency categories |
| `POST /classify/batch` | Classifies up to 50 messages in one request |
| `POST /guardrail` | Evaluates draft replies against 5 safety checks before sending |
| `POST /classify-and-evaluate` | Full pipeline — classify and evaluate in one call |
| `POST /simplify` | Converts clinical documents into plain language, Grade 6, checklist, FAQ, and SMS |
| `POST /structure` | Converts messy SOPs into structured documents with action tables and escalation rules |
| `GET /` | Health check |

---

## Projects

### Project 1 — Clinic Inbox Triage Classifier

Classifies patient messages into six categories with severity scoring, recommended actions, safe draft replies, and audit tags. Uses a rules plus LLM hybrid pipeline with a policy override layer that enforces safety constraints regardless of model confidence.

Labels: `red_flag_escalation`, `urgent_clinical_review`, `routine_clinical_question`, `post_treatment_reassurance`, `scheduling_admin`, `billing_payment`

### Project 2 — Prompt Evaluation and Guardrails

Evaluates LLM-generated replies against five safety checks before they reach a patient. Catches unsafe medical advice, overconfident language, missing escalation, tone violations, and hallucinated policy claims. Generates a corrected reply automatically when a check fails.

### Project 3 — Patient Education Simplification

Takes clinical aftercare documents and converts them into five formats: plain language, Flesch-Kincaid Grade 6 reading level, structured aftercare checklist, FAQ pairs, and SMS follow-up messages under 160 characters each.

### Project 4 — Clinical Documentation Structuring

Converts unstructured clinic notes and protocol drafts into standardised documents with Purpose, Scope, Procedure, Escalation, and Review sections, a Who/What/When action table, explicit escalation rules, and version metadata.

---

## Safety Design

This system is optimised for recall on safety-critical message classes. A missed red flag is a more serious failure than a false positive.

- Regex pre-screen runs before the LLM on every message
- Policy override layer enforces hard boundaries post-LLM
- Every classification decision is logged for audit
- Red-flag and urgent messages require human approval before any reply is sent
- Guardrail layer blocks unsafe replies before they reach patients

See `docs/risk-policy.md` for full safety constraints.

---

## Tech Stack

| Component | Choice |
|---|---|
| Language | Python 3.11+ |
| API framework | FastAPI |
| Schema validation | Pydantic v2 |
| LLM | Google Gemini (swappable via llm_client.py) |
| Testing | pytest |
| Interface | HTML/CSS frontend + Streamlit |

---

## Setup

1. Clone the repo and navigate into it
2. Create and activate a virtual environment: `python -m venv venv` then `venv\Scripts\activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add your API key
5. Run the API: `uvicorn app.main:app --reload`
6. Open the frontend: `app/frontend.html` in your browser

---

## Evaluation Results

| Metric | Result |
|---|---|
| Overall accuracy | 100% on 9-message gold set |
| Safety-class recall | 100% (4/4 safety messages) |
| JSON validity rate | 100% |
| Policy violation rate | 0% |

---

## Test Suite

Run all tests with:
python -m pytest tests/ -v --ignore=tests/test_guardrails.py -p no:gltest
28 tests passing across all four projects.

---

## Status

Version 4.0.0 — All four projects complete.