# Label Schema — Clinic Inbox Triage Assistant

## Overview
This document defines the six classification labels used by the triage system.
Each label has a precise definition, example messages, and boundary rules.
When a message is ambiguous, the tiebreaker rule at the bottom applies.

---

## Labels

### 1. `red_flag_escalation`
**Definition:** Messages describing symptoms that may indicate a medical emergency
or serious complication requiring immediate clinical attention.

**Examples:**
- "I had lip filler yesterday and one side is completely white and painful"
- "I can't breathe properly after my procedure"
- "My vision has gone blurry since the injection this morning"
- "I think I'm having an allergic reaction, my throat feels tight"

**Key indicators:**
- Vascular occlusion signs: skin pallor, mottling, blanching, severe unilateral pain
- Anaphylaxis signs: throat tightness, swelling, difficulty breathing
- Neurological signs: vision changes, facial drooping, confusion
- Chest pain of any kind

**Severity:** Always `high`

---

### 2. `urgent_clinical_review`
**Definition:** Messages describing symptoms that are concerning but not immediately
life-threatening. Require same-day review by a clinician.

**Examples:**
- "My filler area has been swelling for 3 days and it's getting worse not better"
- "I have a hard lump that appeared 2 weeks after my treatment"
- "The bruising on my face looks infected, it's hot and oozing"
- "I've had a headache for 4 days straight since my Botox"

**Key indicators:**
- Worsening symptoms beyond expected recovery window
- Signs of infection: heat, redness spreading, discharge
- Persistent or unusual pain beyond 48 hours
- Unexpected nodules or asymmetry developing after initial healing

**Severity:** `medium` to `high`

---

### 3. `routine_clinical_question`
**Definition:** Messages asking standard questions about recovery, aftercare,
or treatment outcomes. No red-flag indicators present.

**Examples:**
- "Is it normal to have swelling on day 2 after lip filler?"
- "Can I wear makeup tomorrow after my treatment?"
- "How long until I see the full results of my Botox?"
- "I have a small bruise on my cheek, is that expected?"

**Key indicators:**
- Questions about expected symptoms within normal recovery range
- Aftercare clarification questions
- Timeline questions about results
- No urgency language, no worsening trajectory

**Severity:** `low`

---

### 4. `scheduling_admin`
**Definition:** Messages related to appointment booking, changes, cancellations,
clinic location, opening hours, or general administrative queries.

**Examples:**
- "Can I move my appointment from Tuesday to Thursday?"
- "What time does the clinic open on Saturdays?"
- "I need to cancel my booking for next week"
- "What's the address of your clinic?"

**Key indicators:**
- Appointment or booking language
- Location or hours queries
- No clinical content present

**Severity:** `low`

---

### 5. `billing_payment`
**Definition:** Messages about invoices, payment, refunds, pricing, or
financial transactions.

**Examples:**
- "I haven't received my receipt for last week's appointment"
- "Can I pay in instalments for my treatment?"
- "I was charged twice, can you look into this?"
- "How much does a top-up appointment cost?"

**Key indicators:**
- Payment, invoice, refund, or pricing language
- No clinical content present

**Severity:** `low`

---

### 6. `post_treatment_reassurance`
**Definition:** Messages describing symptoms that are common, expected, and
within normal recovery range. Patient is seeking reassurance, not clinical review.

**Examples:**
- "I have some swelling and tenderness after my lip filler, is this okay?"
- "My forehead feels a bit heavy after Botox, is that normal?"
- "There's some redness around the injection sites, should I be worried?"
- "I feel a bit bruised around my eyes after filler, is that expected?"

**Key indicators:**
- Symptoms consistent with normal post-treatment response
- No worsening trajectory mentioned
- No red-flag indicators present
- Patient tone is calm or mildly anxious, not distressed

**Severity:** `low`

---

## Tiebreaker Rules

When a message fits more than one label, apply these rules in order:

1. If ANY red-flag indicator is present → assign `red_flag_escalation` regardless of other content
2. If clinical symptoms are present alongside admin or billing content → assign the clinical label
3. If symptoms are ambiguous between `urgent_clinical_review` and `routine_clinical_question` → assign `urgent_clinical_review`
4. If tone is distressed but symptoms are routine → assign `post_treatment_reassurance` with a note

**Default rule: always escalate to the higher-severity label when in doubt.**