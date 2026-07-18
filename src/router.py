"""Plan-only Korean request router; it never executes tools or writes requests."""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, TypedDict

import background
import lookup
from safety import SafetyPriority, assess_request


class RouteMode(str, Enum):
    FULL_EXEGESIS = "full_exegesis"
    DEVOTION = "devotion"
    ORIGINAL_LANGUAGE_LEXICON = "original_language_lexicon"
    TRANSLATED_WORD_SEARCH = "translated_word_search"
    LITURGICAL = "liturgical"
    SERIES_PLANNING = "series_planning"
    BACKGROUND_RESEARCH = "background_research"
    BIBLE_STUDY_MATERIAL = "bible_study_material"
    READING_GUIDE = "reading_guide"
    EXPORT_DOCX = "export_docx"
    SERMON_FROM_TOPIC = "sermon_from_topic"
    NEEDS_SCOPE = "needs_scope"
    SAFETY_FIRST = "safety_first"
    PRIVACY_REVIEW = "privacy_review"


class PlanPayload(TypedDict):
    mode: str
    status: str
    direct_output: bool
    store_request: bool
    actions: List[str]
    questions: List[str]
    safety_review_required: bool
    care_aware: bool


@dataclass(frozen=True)
class RoutePlan:
    """Serializable plan that deliberately excludes the original request."""

    mode: RouteMode
    status: str
    actions: Tuple[str, ...]
    questions: Tuple[str, ...]
    safety_review_required: bool
    care_aware: bool

    def as_dict(self) -> PlanPayload:
        return {
            "mode": self.mode.value,
            "status": self.status,
            "direct_output": False,
            "store_request": False,
            "actions": list(self.actions),
            "questions": list(self.questions),
            "safety_review_required": self.safety_review_required,
            "care_aware": self.care_aware,
        }


_EXEGESIS = ("python src/lookup.py <reference> --pericope", "four_stage_audit")
_ORIGINAL = ("canonical_original_language_lookup", "lexicon_data_gate")
_CARE_ACTIONS = ("avoid_cause_claims", "avoid_treatment_or_recovery_guarantees")
_SERMON = ("python src/search.py <theme>", "topic_to_text_to_sermon")


def _has_reference(request: str) -> bool:
    aliases, _, _, _ = lookup.load_books()
    compact = re.sub(r"\s+", "", request.casefold())
    for alias in sorted(aliases, key=len, reverse=True):
        pattern = re.escape(alias) + r"\d+:\d+(?:-\d+)?"
        for match in re.finditer(pattern, compact):
            if lookup.parse_ref(match.group(), aliases):
                return True
    return False


def _background_is_high(request: str) -> bool:
    for topic in background.load():
        if topic["name"] in request and topic["controversy"] == "high":
            return True
    return False


def _ready(mode: RouteMode, actions: Tuple[str, ...], care_aware: bool, review: bool = False) -> RoutePlan:
    care_actions = _CARE_ACTIONS if care_aware else ()
    return RoutePlan(mode, "ready", actions + care_actions, (), review, care_aware)


def plan_request(request: str) -> PlanPayload:
    """Classify a Korean request into a JSON-safe execution plan only."""
    assessment = assess_request(request)
    if assessment.priority is SafetyPriority.SAFETY_FIRST:
        plan = RoutePlan(
            RouteMode.SAFETY_FIRST,
            "safety_first",
            ("seek_immediate_local_help", "contact_trusted_person", "connect_professional_support"),
            (),
            True,
            assessment.care_aware,
        )
        return plan.as_dict()
    if assessment.priority is SafetyPriority.PRIVACY_REVIEW:
        plan = RoutePlan(
            RouteMode.PRIVACY_REVIEW,
            "privacy_review",
            ("privacy_minimize", "request_anonymized_scope"),
            (),
            False,
            assessment.care_aware,
        )
        return plan.as_dict()
    return _route_content(request, assessment.care_aware).as_dict()


def _route_content(request: str, care_aware: bool) -> RoutePlan:
    """Route content after safety and privacy preflight has passed."""
    has_reference = _has_reference(request)
    if any(word in request for word in ("워드", "docx", "문서로", "내보내")):
        return RoutePlan(RouteMode.EXPORT_DOCX, "needs_clarification", ("python src/export_exegesis_docx.py <draft>",), ("draft_required",), False, care_aware)
    if any(word in request for word in ("시리즈", "연속 설교", "강해 계획")):
        return _ready(RouteMode.SERIES_PLANNING, ("python src/series.py <book>",), care_aware)
    if any(word in request for word in ("부활절", "성탄절", "사순절", "절기", "교회력")):
        return _ready(RouteMode.LITURGICAL, ("python src/liturgical.py <season>",), care_aware)
    if any(word in request for word in ("설교문", "주제로 설교", "설교 만들", "기사로 설교", "자료로 설교", "논문으로 설교")):
        return _ready(RouteMode.SERMON_FROM_TOPIC, _SERMON, care_aware)
    background_request = any(word in request for word in ("배경", "역사성", "고고학", "광야 경로", "선교여행"))
    if background_request:
        review = _background_is_high(request)
        return _ready(RouteMode.BACKGROUND_RESEARCH, ("python src/background.py <topic>",), care_aware, review)
    if any(word in request for word in ("성경공부", "워크북", "인도안", "소그룹")):
        if has_reference:
            return _ready(RouteMode.BIBLE_STUDY_MATERIAL, _EXEGESIS, care_aware)
        return RoutePlan(RouteMode.BIBLE_STUDY_MATERIAL, "needs_clarification", (), ("reference_required",), False, care_aware)
    if any(word in request for word in ("통독", "통독 가이드")):
        return _ready(RouteMode.READING_GUIDE, ("python src/lookup.py <chapter_range>",), care_aware)
    if any(word in request for word in ("묵상", "큐티", "QT", "오늘 말씀")):
        if has_reference:
            return _ready(RouteMode.DEVOTION, ("python src/lookup.py <reference>",), care_aware)
        return RoutePlan(RouteMode.DEVOTION, "needs_clarification", (), ("reference_required",), False, care_aware)
    if any(word in request for word in ("원어", "헬라어", "히브리어", "사전 뜻", "사전 풀이")):
        if has_reference:
            return _ready(RouteMode.ORIGINAL_LANGUAGE_LEXICON, _ORIGINAL, care_aware)
        return RoutePlan(RouteMode.NEEDS_SCOPE, "needs_clarification", (), ("reference_and_language_required",), False, care_aware)
    if any(word in request for word in ("몇 번", "빈도", "단어 검색", "어디에 나")):
        return _ready(RouteMode.TRANSLATED_WORD_SEARCH, ("python src/search.py <word> --count",), care_aware)
    if has_reference and any(word in request for word in ("주해", "분석", "강해")):
        return _ready(RouteMode.FULL_EXEGESIS, _EXEGESIS, care_aware)
    return RoutePlan(RouteMode.NEEDS_SCOPE, "needs_clarification", (), ("scope_or_reference_required",), False, care_aware)


def main() -> None:
    parser = argparse.ArgumentParser(description="Exegete plan-only request router")
    parser.add_argument("request")
    args = parser.parse_args()
    print(json.dumps(plan_request(args.request), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
