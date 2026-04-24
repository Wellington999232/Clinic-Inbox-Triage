# app/rules.py
# Regex-based pre-screen for hard red-flag detection.
# This runs BEFORE the LLM on every message.
# If a match is found, the message is escalated immediately.

import re
from app.schemas import Label, Severity


# --- Red Flag Patterns ---
# These patterns match language associated with clinical emergencies.
# Any match forces red_flag_escalation regardless of LLM output.

RED_FLAG_PATTERNS = [
    # Vascular occlusion indicators
    r"\bwhite\b",
    r"\bpale\b",
    r"\bmottl",
    r"\bblanch",
    r"\bvascular\b",

    # Breathing and airway
    r"\bcan'?t\s+breath",
    r"\bdifficult\w*\s+breath",
    r"\bthroat\s+(closing|tight|swollen)",
    r"\bairway\b",

    # Vision
    r"\bcan'?t\s+see\b",
    r"\bvision\s+(loss|gone|blurr|changed)",
    r"\bblurr\w*\s+(vision|sight|eye)",
    r"\bblind\b",

    # Allergic reaction
    r"\banaphyl",
    r"\ballergic\s+reaction",
    r"\bswelling\s+(fast|rapidly|quickly)",
    r"\bhives\b",

    # Chest and cardiac
    r"\bchest\s+pain\b",
    r"\bheart\s+(racing|pounding|pain)",

    # Neurological
    r"\bfacial\s+droop",
    r"\bcan'?t\s+move\b",
    r"\bnumb\w*\s+(face|lip|cheek|nose)",
    r"\bseizure\b",
    r"\bunconsci",
]

# Compile all patterns once at import time for performance
_COMPILED_RED_FLAG = [
    re.compile(p, re.IGNORECASE) for p in RED_FLAG_PATTERNS
]


def check_red_flags(text: str) -> tuple[bool, list[str]]:
    """
    Scan message text for red-flag patterns.

    Returns:
        - matched (bool): True if any red-flag pattern was found
        - matched_tags (list): list of pattern strings that matched
    """
    matched_tags = []
    for pattern in _COMPILED_RED_FLAG:
        if pattern.search(text):
            matched_tags.append(pattern.pattern)

    return len(matched_tags) > 0, matched_tags


def apply_policy_overrides(
    label: Label,
    severity: Severity,
    confidence: float,
    red_flag_matched: bool,
) -> tuple[Label, Severity, bool]:
    """
    Apply post-LLM policy rules.
    Returns the (possibly overridden) label, severity, and a flag
    indicating whether an override was triggered.

    Rules applied in order:
    1. If red flag was matched in pre-screen, force escalation
    2. If confidence is below 0.5, route to urgent_clinical_review
    3. If severity is high, ensure label is at least urgent_clinical_review
    """
    override_triggered = False

    # Rule 1: red flag pre-screen match overrides everything
    if red_flag_matched:
        return Label.red_flag_escalation, Severity.high, True

    # Rule 2: low confidence routes to urgent review
    if confidence < 0.5:
        label = Label.urgent_clinical_review
        severity = Severity.medium
        override_triggered = True

    # Rule 3: high severity must map to a clinical label
    if severity == Severity.high and label not in (
        Label.red_flag_escalation,
        Label.urgent_clinical_review,
    ):
        label = Label.urgent_clinical_review
        override_triggered = True

    return label, severity, override_triggered