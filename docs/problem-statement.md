# Problem Statement — Clinic Inbox Triage Assistant

## The Problem

Aesthetic clinics receive a high volume of inbound patient messages daily
across email, SMS, and messaging platforms. These messages range from
routine booking requests to genuine clinical emergencies.

Currently, these messages land in a shared inbox and are triaged manually
by front desk staff or clinical coordinators. This creates three risks:

1. **Missed urgency** — A red-flag message sits unread alongside routine
   admin queries. A staff member without clinical training may not
   recognise the severity.

2. **Delayed response** — High message volume means urgent messages do
   not always receive a same-day response.

3. **Inconsistent handling** — Different staff members apply different
   judgment. There is no standardised triage logic or audit trail.

---

## The Solution

The Clinic Inbox Triage Assistant is an AI-powered classification layer
that sits between the incoming message and the human responder.

It does not replace human judgment. It organises and prioritises the
inbox so that the right messages reach the right people faster, and
no red-flag message is buried under routine queries.

---

## Who Uses This Tool

| User | Role |
|---|---|
| Front desk staff | View triage output, send pre-approved draft replies for routine messages |
| Clinical coordinators | Review urgent and red-flag escalations flagged by the system |
| Clinicians | Respond to all `red_flag_escalation` and `urgent_clinical_review` messages |
| Clinic managers | Review audit logs, monitor system performance |

---

## What Decisions the System Can Make Autonomously

- Classify an incoming message into one of six labels
- Assign a severity score
- Generate a safe draft reply for low-severity messages
- Recommend a next action for clinic staff
- Flag a message for human review

---

## What Decisions Must Remain Human-Only

- Sending any reply to a `red_flag_escalation` message
- Sending any reply to an `urgent_clinical_review` message
- Any clinical assessment or diagnosis
- Any medication guidance
- Overriding a red-flag escalation

---

## Constraints

- The system operates on text messages only — no image analysis
- It does not have access to patient records or treatment history
- It does not integrate with booking systems in this version
- All outputs are recommendations — a human must approve before acting
  on any safety-critical classification

---

## Success Criteria

The system is considered successful if it achieves:

- Recall of 0.95 or above on `red_flag_escalation` messages
- Recall of 0.90 or above on `urgent_clinical_review` messages
- Overall classification accuracy of 0.85 or above
- JSON validity rate of 0.99 or above
- Zero policy violations in the held-out eval set