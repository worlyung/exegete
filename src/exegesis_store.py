"""Immutable audit-lineage storage for top-level Exegete Markdown drafts."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = REPO_ROOT / "output"
STAGE_NAMES = ("structure", "philology", "theology", "sermon")


class StateError(RuntimeError):
    """Signals a violation of the audited-draft contract."""


class StageStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


class AuditOutcome(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class AuditRequest:
    draft: Path
    reference: str
    expected_sha256: str
    run: Path
    outcome: AuditOutcome
    all_factual_claims_pass: bool
    consent_path: Optional[Path]


def _resolved(path: Path) -> Path:
    return path.resolve()


def _under(path: Path, parent: Path) -> bool:
    try:
        _resolved(path).relative_to(_resolved(parent))
    except ValueError:
        return False
    return True


def _relative(path: Path) -> str:
    try:
        return _resolved(path).relative_to(_resolved(REPO_ROOT)).as_posix()
    except ValueError as error:
        raise StateError("path_outside_repository") from error


def top_level_markdown(path: Path) -> Path:
    """Accept only an existing top-level `output/*.md` file."""
    candidate = path if path.is_absolute() else REPO_ROOT / path
    resolved = _resolved(candidate)
    valid = resolved.parent == _resolved(OUTPUT_ROOT) and resolved.suffix.casefold() == ".md"
    if not valid:
        raise StateError("draft_must_be_top_level_output_markdown")
    if not resolved.is_file():
        raise StateError("draft_missing")
    return resolved


def output_docx_path(path: Path) -> Path:
    """Accept only an adjacent top-level audited-document destination."""
    candidate = path if path.is_absolute() else REPO_ROOT / path
    resolved = _resolved(candidate)
    valid = resolved.parent == _resolved(OUTPUT_ROOT) and resolved.suffix.casefold() == ".docx"
    if not valid:
        raise StateError("docx_must_be_top_level_output_document")
    return resolved


def sha256_file(path: Path) -> str:
    """Hash exact bytes so one changed byte makes the revision stale."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def case_root_for(draft: Path) -> Path:
    return OUTPUT_ROOT / "audit" / top_level_markdown(draft).stem


def lineage_path_for(draft: Path) -> Path:
    return case_root_for(draft) / "lineage.jsonl"


def read_events(draft: Path):
    """Read JSONL without rewriting it; malformed records are rejected."""
    lineage = lineage_path_for(draft)
    if not lineage.exists():
        return ()
    events = []
    for line in lineage.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError as error:
            raise StateError("lineage_is_not_valid_jsonl") from error
        if not isinstance(event, dict):
            raise StateError("lineage_event_is_not_object")
        events.append(event)
    return tuple(events)


def _append_event(draft: Path, event) -> None:
    lineage = lineage_path_for(draft)
    lineage.parent.mkdir(parents=True, exist_ok=True)
    with lineage.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def register_revision(draft: Path, reference: str) -> None:
    """Append a new revision with all four stages reset."""
    checked = top_level_markdown(draft)
    if not reference.strip():
        raise StateError("reference_required")
    stages = {name: StageStatus.NOT_STARTED.value for name in STAGE_NAMES}
    _append_event(checked, {"event": "revision_registered", "draft": _relative(checked), "sha256": sha256_file(checked), "ref": reference, "stages": stages})


def set_stage(draft: Path, stage: str, status: StageStatus) -> None:
    """Append a stage change tied to the present draft hash."""
    checked = top_level_markdown(draft)
    if stage not in STAGE_NAMES:
        raise StateError("unknown_stage")
    _append_event(checked, {"event": "stage_set", "draft": _relative(checked), "sha256": sha256_file(checked), "stage": stage, "status": status.value})


def _audit_run_for(draft: Path, run: Path) -> Path:
    candidate = run if run.is_absolute() else REPO_ROOT / run
    resolved = _resolved(candidate)
    if not _under(resolved, case_root_for(draft)) or not resolved.is_dir():
        raise StateError("audit_run_must_be_inside_draft_case_root")
    return resolved


def _manifest_matches(run: Path, draft: Path, reference: str, digest: str) -> bool:
    manifest = run / "00_manifest.md"
    if not manifest.is_file():
        return False
    text = manifest.read_text(encoding="utf-8")
    return _relative(draft) in text and reference in text and digest.casefold() in text.casefold()


def _consent_hash(run: Path, consent_path: Optional[Path]) -> Tuple[str, str]:
    if consent_path is None:
        raise StateError("warn_requires_consent_file")
    candidate = consent_path if consent_path.is_absolute() else REPO_ROOT / consent_path
    resolved = _resolved(candidate)
    if not _under(resolved, run) or not resolved.is_file():
        raise StateError("consent_must_be_a_file_below_audit_run")
    try:
        consent = json.loads(resolved.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise StateError("consent_must_be_utf8_json") from error
    limitations = consent.get("limitations") if isinstance(consent, dict) else None
    valid = isinstance(consent, dict) and all(
        (isinstance(consent.get("consenter"), str), bool(consent.get("consenter", "").strip()),
         isinstance(consent.get("at_utc"), str), bool(consent.get("at_utc", "").strip()),
         isinstance(limitations, list), bool(limitations),
         all(isinstance(item, str) and item.strip() for item in limitations or ()))
    )
    if not valid:
        raise StateError("consent_schema_invalid")
    return _relative(resolved), sha256_file(resolved)


def finalize_audit(request: AuditRequest) -> None:
    """Write a non-semantic audit sidecar, then append the outcome event."""
    draft = top_level_markdown(request.draft)
    digest = sha256_file(draft)
    if request.expected_sha256.casefold() != digest.casefold():
        raise StateError("supplied_sha256_does_not_match_draft")
    pass_like = request.outcome in (AuditOutcome.PASS, AuditOutcome.WARN)
    if pass_like and not request.all_factual_claims_pass:
        raise StateError("pass_or_warn_requires_all_factual_claims_pass")
    run = _audit_run_for(draft, request.run)
    if not _manifest_matches(run, draft, request.reference, digest):
        raise StateError("manifest_draft_reference_or_sha256_mismatch")
    consent_path, consent_digest = (None, None)
    if request.outcome is AuditOutcome.WARN:
        consent_path, consent_digest = _consent_hash(run, request.consent_path)
    sidecar = {
        "schema": "exegesis_audit_sidecar/v1", "human_audit_semantics_verified": False,
        "draft": _relative(draft), "reference": request.reference, "sha256": digest,
        "manifest": {"path": _relative(run / "00_manifest.md"), "mechanically_matched": True},
        "outcome": request.outcome.value, "all_factual_claims_pass": request.all_factual_claims_pass,
        "consent": {"path": consent_path, "sha256": consent_digest},
    }
    (run / "audit.json").write_text(json.dumps(sidecar, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _append_event(draft, {
        "event": "audit_recorded", "draft": _relative(draft), "sha256": digest,
        "result": request.outcome.value, "audit_run": _relative(run),
        "all_factual_claims_pass": request.all_factual_claims_pass,
        "consent_path": consent_path, "consent_sha256": consent_digest,
    })
