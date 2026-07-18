"""Conservative, local-only request preflight for the router."""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class SafetyPriority(str, Enum):
    NONE = "none"
    CARE_AWARE = "care_aware"
    PRIVACY_REVIEW = "privacy_review"
    SAFETY_FIRST = "safety_first"


@dataclass(frozen=True)
class SafetyAssessment:
    """Classifies routing risk; it does not diagnose a person or situation."""

    priority: SafetyPriority
    care_aware: bool
    has_identifiers: bool


_CRISIS_TERMS = (
    "자살", "자해", "죽고 싶", "죽고싶", "목숨을 끊", "죽여버",
    "죽이겠", "자타해", "해치고 싶", "살해", "폭행", "학대",
    "가정폭력", "성폭력", "강간", "때리고 있", "맞고 있", "당장 위험", "지금 위험",
)
_CARE_TERMS = ("사별", "상실", "애도", "투병", "병상", "암 치료", "중환자")
_EMAIL = re.compile(r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![A-Za-z0-9.-])")
_PHONE = re.compile(r"(?<!\d)(?:\+?82[- ]?)?0?1[0-9][- ]?\d{3,4}[- ]?\d{4}(?!\d)")
_RESIDENT = re.compile(r"(?<!\d)\d{6}[- ]?[1-4]\d{6}(?!\d)")


def assess_request(request: str) -> SafetyAssessment:
    """Return a deliberately conservative preflight without retaining input."""
    lowered = request.casefold()
    crisis = any(term in lowered for term in _CRISIS_TERMS)
    identifiers = bool(_EMAIL.search(request) or _PHONE.search(request) or _RESIDENT.search(request))
    care_aware = any(term in lowered for term in _CARE_TERMS)
    if crisis:
        priority = SafetyPriority.SAFETY_FIRST
    elif identifiers:
        priority = SafetyPriority.PRIVACY_REVIEW
    elif care_aware:
        priority = SafetyPriority.CARE_AWARE
    else:
        priority = SafetyPriority.NONE
    return SafetyAssessment(priority=priority, care_aware=care_aware, has_identifiers=identifiers)
