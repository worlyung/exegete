"""Gated Word export for audited Exegete Markdown drafts only."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence, Tuple

import exegesis_state as state


@dataclass(frozen=True)
class ExportTarget:
    source: Path
    destination: Path


def convert_document(source: Path, destination: Path) -> None:
    """Load the optional python-docx dependency only after state preflight."""
    from export_docx import convert
    convert(str(source), str(destination))


def _preflight(drafts: Sequence[Path], requested_output: Optional[Path], overwrite: bool) -> Tuple[ExportTarget, ...]:
    if requested_output is not None and len(drafts) != 1:
        raise state.StateError("custom_output_requires_single_draft")
    targets = []
    for draft in drafts:
        source = state.top_level_markdown(draft)
        if not state.status_for(source).exportable:
            raise state.StateError("draft_is_not_exportable")
        destination = requested_output if requested_output is not None else source.with_suffix(".docx")
        checked_destination = state.output_docx_path(destination)
        if checked_destination.exists() and not overwrite:
            raise state.StateError("existing_docx_requires_overwrite")
        targets.append(ExportTarget(source, checked_destination))
    return tuple(targets)


def export_targets(drafts: Sequence[Path], requested_output: Optional[Path], overwrite: bool) -> Tuple[Path, ...]:
    """Preflight every target before converting any target, then record each export."""
    targets = _preflight(drafts, requested_output, overwrite)
    for target in targets:
        convert_document(target.source, target.destination)
        state.record_export(target.source, target.destination)
    return tuple(target.destination for target in targets)


def main() -> int:
    parser = argparse.ArgumentParser(description="Gated Exegete Markdown to Word export")
    parser.add_argument("draft", nargs="?", type=Path)
    parser.add_argument("-o", "--out", type=Path)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.all and args.draft is not None:
        parser.error("draft_and_all_are_exclusive")
    if not args.all and args.draft is None:
        parser.error("draft_or_all_required")
    drafts = tuple(sorted(state.OUTPUT_ROOT.glob("*.md"))) if args.all else (args.draft,)
    if not drafts:
        parser.error("no_top_level_output_markdown")
    try:
        completed = export_targets(drafts, args.out, args.overwrite)
    except state.StateError as error:
        parser.error(str(error))
    for destination in completed:
        print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
