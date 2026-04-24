# Risk Policy — Clinic Inbox Triage Assistant

## Purpose
This document defines the hard boundaries the triage system must never cross,
regardless of confidence score, message content, or user instruction.
These rules are enforced by the policy override layer in code — they are not
suggestions, they are constraints.

---

## Hard Boundaries

### 1. Never Diagnose
The system must not state or imply a medical diagnosis.

**Not allowed:**
- "This sounds like vascular occlusion."
- "You may have an infection."
- "This appears to be an allergic reaction."

**Allowed:**
- "Your message has been flagged for urgent clinician review."
- "Please contact the clinic immediately so a clinician can assess this."

---

### 2. Never Provide Medication Dosing
The system must not recommend, confirm, or adjust any medication dose.

**Not allowed:**
- "You can take 400mg of ibuprofen for the pain."
- "Apply the prescribed cream twice daily."
- "Your hyaluronidase dose would typically be..."

**Allowed:**
- "Please follow the aftercare instructions provided by your clinician."
- "Contact the clinic for guidance on any medication questions."

---

### 3. Always Escalate Red Flags
If any red-flag indicator is detected — by the regex pre-screen or the LLM —
the system must route to `red_flag_escalation` and recommend immediate
human review. This rule cannot be overridden by confidence score.

A high confidence score on a non-red-flag label does not cancel escalation
if red-flag keywords are present.

---

### 4. Always Defer Uncertain Medical Advice to Clinician
If the system cannot classify a message with confidence, or if the message
contains clinical content that does not fit cleanly into any label, it must
default to `urgent_clinical_review` and defer to a human.

The system must never guess at medical guidance to fill a gap.

---

### 5. Never Provide False Reassurance
The system must not tell a patient their symptoms are fine when clinical
indicators suggest otherwise.

**Not allowed:**
- "That sounds completely normal, nothing to worry about."
- "You are fine, this is just swelling."

**Allowed:**
- "This is a common post-treatment response, but if symptoms worsen
  please contact the clinic immediately."

---

### 6. Log Every Classification Decision
Every message processed must produce an audit entry containing:
- Input message text
- Primary and secondary label assigned
- Confidence score and method
- Reasoning tags
- Timestamp
- Whether a policy override was triggered

This log is not optional. It exists to support clinical governance and
to enable retrospective review of system decisions.

---

## Policy Override Trigger Conditions

The policy layer in `app/rules.py` must automatically override LLM output
and force escalation when any of the following are detected:

| Trigger | Forced Action |
|---|---|
| Red-flag keyword matched in pre-screen | Force `red_flag_escalation` |
| LLM returns invalid JSON | Route to `urgent_clinical_review`, log failure |
| Confidence score below 0.5 | Route to `urgent_clinical_review` |
| LLM attempts to include a diagnosis | Strip diagnosis, escalate |
| LLM attempts to include medication dosing | Strip dosing, escalate |

---

## What the System Is Permitted to Do

- Classify the intent and urgency of a patient message
- Suggest a safe, pre-approved draft reply
- Recommend a next action for clinic staff
- Provide compact reasoning tags for audit purposes
- Route messages to the appropriate team or workflow

## What the System Is Never Permitted to Do

- Diagnose a condition
- Prescribe or recommend medication or dosing
- Provide a definitive clinical assessment
- Replace clinician judgment
- Send a reply to a patient without human review for any
  `red_flag_escalation` or `urgent_clinical_review` message