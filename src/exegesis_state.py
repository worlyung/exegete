"""CLI and replayed status for append-only Exegete audit lineage."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple, TypedDict

from exegesis_store import AuditOutcome, AuditRequest, REPO_ROOT, STAGE_NAMES
from exegesis_store import StateError, StageStatus, _relative, read_events, sha256_file
from exegesis_store import finalize_audit, output_docx_path, register_revision, set_stage, top_level_markdown


class StatusPayload(TypedDict):
    draft: str
    sha256: str
    stale: bool
    stages: Dict[str, str]
    audit_outcome: Optional[str]
    exportable: bool
    reason: str


@dataclass(frozen=True)
class DraftStatus:
    draft: str
    sha256: str
    stale: bool
    stages: Tuple[Tuple[str, str], ...]
    audit_outcome: Optional[str]
    exportable: bool
    reason: str

    def as_dict(self) -> StatusPayload:
        return {"draft": self.draft, "sha256": self.sha256, "stale": self.stale, "stages": dict(self.stages), "audit_outcome": self.audit_outcome, "exportable": self.exportable, "reason": self.reason}


def _latest_revision(events):
    index, revision = -1, None
    for position, event in enumerate(events):
        if event.get("event") == "revision_registered":
            index, revision = position, event
    return index, revision


def _warn_consent_matches(event) -> bool:
    path, digest = event.get("consent_path"), event.get("consent_sha256")
    if not isinstance(path, str) or not isinstance(digest, str):
        return False
    candidate = REPO_ROOT / path
    return candidate.is_file() and sha256_file(candidate).casefold() == digest.casefold()


def status_for(draft: Path) -> DraftStatus:
    """Replay lineage and block stale, incomplete, failed, or unconsented revisions."""
    checked = top_level_markdown(draft)
    digest = sha256_file(checked)
    events = read_events(checked)
    index, revision = _latest_revision(events)
    initial = {name: StageStatus.NOT_STARTED.value for name in STAGE_NAMES}
    if revision is None:
        return DraftStatus(_relative(checked), digest, True, tuple(initial.items()), None, False, "revision_not_registered")
    revision_hash = revision.get("sha256")
    if not isinstance(revision_hash, str) or revision_hash.casefold() != digest.casefold():
        return DraftStatus(_relative(checked), digest, True, tuple(initial.items()), None, False, "draft_bytes_changed")
    raw_stages = revision.get("stages")
    stages = dict(raw_stages) if isinstance(raw_stages, dict) else initial
    audit = None
    for event in events[index + 1:]:
        if event.get("sha256") != digest:
            continue
        if event.get("event") == "stage_set" and event.get("stage") in STAGE_NAMES:
            stages[event["stage"]] = event.get("status")
        if event.get("event") == "audit_recorded":
            audit = event
    complete = all(stages.get(name) == StageStatus.COMPLETE.value for name in STAGE_NAMES)
    outcome = audit.get("result") if audit else None
    factual = bool(audit and audit.get("all_factual_claims_pass"))
    passed = outcome == AuditOutcome.PASS.value and factual
    warned = bool(audit) and outcome == AuditOutcome.WARN.value and factual and _warn_consent_matches(audit)
    exportable = complete and (passed or warned)
    reason = "exportable" if exportable else "stages_or_audit_gate_incomplete"
    return DraftStatus(_relative(checked), digest, False, tuple(stages.items()), outcome, exportable, reason)


def record_export(draft: Path, document: Path) -> None:
    """Record a document only if the current source revision remains exportable."""
    checked, destination = top_level_markdown(draft), output_docx_path(document)
    if not status_for(checked).exportable:
        raise StateError("draft_is_not_exportable")
    from exegesis_store import _append_event
    _append_event(checked, {"event": "export_recorded", "draft": _relative(checked), "sha256": sha256_file(checked), "docx": _relative(destination)})


def _emit(value: StatusPayload) -> None:
    print(json.dumps(value, ensure_ascii=False, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description="Exegete append-only audit state")
    commands = parser.add_subparsers(dest="command", required=True)
    register = commands.add_parser("register")
    register.add_argument("draft", type=Path)
    register.add_argument("--ref", required=True)
    stage = commands.add_parser("stage")
    stage.add_argument("draft", type=Path)
    stage.add_argument("stage", choices=STAGE_NAMES)
    stage.add_argument("status", choices=tuple(item.value for item in StageStatus))
    finalize = commands.add_parser("finalize-audit")
    finalize.add_argument("--draft", type=Path, required=True)
    finalize.add_argument("--ref", required=True)
    finalize.add_argument("--sha256", required=True)
    finalize.add_argument("--run", type=Path, required=True)
    finalize.add_argument("--outcome", choices=tuple(item.value for item in AuditOutcome), required=True)
    finalize.add_argument("--all-factual-claims-pass", action="store_true")
    finalize.add_argument("--consent", type=Path)
    status = commands.add_parser("status")
    status.add_argument("draft", type=Path)
    exported = commands.add_parser("record-export")
    exported.add_argument("draft", type=Path)
    exported.add_argument("docx", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "register":
            register_revision(args.draft, args.ref)
            _emit(status_for(args.draft).as_dict())
            return 0
        if args.command == "stage":
            set_stage(args.draft, args.stage, StageStatus(args.status))
            _emit(status_for(args.draft).as_dict())
            return 0
        if args.command == "finalize-audit":
            request = AuditRequest(args.draft, args.ref, args.sha256, args.run, AuditOutcome(args.outcome), args.all_factual_claims_pass, args.consent)
            finalize_audit(request)
            _emit(status_for(args.draft).as_dict())
            return 0
        if args.command == "status":
            _emit(status_for(args.draft).as_dict())
            return 0
        record_export(args.draft, args.docx)
        _emit(status_for(args.draft).as_dict())
    except StateError as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
