from __future__ import annotations

import json
import importlib
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

state = importlib.import_module("exegesis_state")
store = importlib.import_module("exegesis_store")
exporter = importlib.import_module("export_exegesis_docx")


class ExegesisStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.repo = Path(self.temp_dir.name)
        self.output = self.repo / "output"
        self.output.mkdir()
        self.root_patch = patch.object(state, "REPO_ROOT", self.repo)
        self.store_root_patch = patch.object(store, "REPO_ROOT", self.repo)
        self.store_output_patch = patch.object(store, "OUTPUT_ROOT", self.output)
        self.root_patch.start()
        self.store_root_patch.start()
        self.store_output_patch.start()

    def tearDown(self) -> None:
        self.root_patch.stop()
        self.store_output_patch.stop()
        self.store_root_patch.stop()
        self.temp_dir.cleanup()

    def write_draft(self, name: str = "draft.md") -> Path:
        draft = self.output / name
        draft.write_text("# Draft\n", encoding="utf-8")
        return draft

    def register_complete(self, draft: Path) -> None:
        state.register_revision(draft, "John 3:16")
        for stage_name in state.STAGE_NAMES:
            state.set_stage(draft, stage_name, state.StageStatus.COMPLETE)

    def create_audit_run(self, draft: Path) -> Path:
        draft_hash = state.sha256_file(draft)
        run = store.case_root_for(draft) / "20260718-120000-000"
        run.mkdir(parents=True)
        manifest = "\n".join(
            [
                "# audit",
                "- draft: output/" + draft.name,
                "- ref: John 3:16",
                "- sha256: " + draft_hash,
            ]
        )
        (run / "00_manifest.md").write_text(manifest, encoding="utf-8")
        return run

    def finalize(self, draft: Path, outcome: state.AuditOutcome) -> None:
        run = self.create_audit_run(draft)
        request = state.AuditRequest(
            draft=draft,
            reference="John 3:16",
            expected_sha256=state.sha256_file(draft),
            run=run,
            outcome=outcome,
            all_factual_claims_pass=True,
            consent_path=None,
        )
        state.finalize_audit(request)

    def test_creates_append_only_lineage_in_case_root(self) -> None:
        draft = self.write_draft()

        state.register_revision(draft, "John 3:16")
        lineage = store.lineage_path_for(draft)
        first_line = lineage.read_text(encoding="utf-8").splitlines()[0]
        state.set_stage(draft, "structure", state.StageStatus.IN_PROGRESS)

        lines = lineage.read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[0], first_line)
        self.assertEqual(len(lines), 2)
        self.assertEqual(Path(json.loads(first_line)["draft"]), Path("output/draft.md"))

    def test_marks_revision_stale_after_one_byte_change(self) -> None:
        draft = self.write_draft()
        self.register_complete(draft)
        self.finalize(draft, state.AuditOutcome.PASS)
        draft.write_text("# Draft!\n", encoding="utf-8")

        status = state.status_for(draft)

        self.assertTrue(status.stale)
        self.assertFalse(status.exportable)

    def test_blocks_fail_and_hold(self) -> None:
        for outcome in (state.AuditOutcome.FAIL, state.AuditOutcome.HOLD):
            with self.subTest(outcome=outcome.value):
                draft = self.write_draft(outcome.value + ".md")
                self.register_complete(draft)
                self.finalize(draft, outcome)

                self.assertFalse(state.status_for(draft).exportable)

    def test_blocks_warn_without_consent_and_allows_matching_consent(self) -> None:
        draft = self.write_draft()
        self.register_complete(draft)
        run = self.create_audit_run(draft)

        with self.assertRaises(state.StateError):
            state.finalize_audit(
                state.AuditRequest(
                    draft=draft,
                    reference="John 3:16",
                    expected_sha256=state.sha256_file(draft),
                    run=run,
                    outcome=state.AuditOutcome.WARN,
                    all_factual_claims_pass=True,
                    consent_path=None,
                )
            )
        consent = run / "consent.json"
        consent.write_text(
            json.dumps(
                {
                    "consenter": "reviewer",
                    "at_utc": "2026-07-18T12:00:00Z",
                    "limitations": ["review required"],
                }
            ),
            encoding="utf-8",
        )
        state.finalize_audit(
            state.AuditRequest(
                draft=draft,
                reference="John 3:16",
                expected_sha256=state.sha256_file(draft),
                run=run,
                outcome=state.AuditOutcome.WARN,
                all_factual_claims_pass=True,
                consent_path=consent,
            )
        )

        self.assertTrue(state.status_for(draft).exportable)

    def test_blocks_incomplete_stages(self) -> None:
        draft = self.write_draft()
        state.register_revision(draft, "John 3:16")
        self.finalize(draft, state.AuditOutcome.PASS)

        self.assertFalse(state.status_for(draft).exportable)


class ExportExegesisDocxTests(ExegesisStateTests):
    def test_exports_passed_draft_and_records_event(self) -> None:
        draft = self.write_draft()
        self.register_complete(draft)
        self.finalize(draft, state.AuditOutcome.PASS)
        destination = draft.with_suffix(".docx")

        def convert(source: Path, target: Path) -> None:
            target.write_bytes(b"docx")

        with patch.object(exporter, "convert_document", side_effect=convert) as convert_mock:
            exporter.export_targets([draft], destination, overwrite=False)

        self.assertTrue(destination.exists())
        self.assertEqual(convert_mock.call_count, 1)
        events = state.read_events(draft)
        self.assertEqual(events[-1]["event"], "export_recorded")

    def test_all_preflight_blocks_every_conversion(self) -> None:
        passed = self.write_draft("passed.md")
        blocked = self.write_draft("blocked.md")
        self.register_complete(passed)
        self.finalize(passed, state.AuditOutcome.PASS)

        with patch.object(exporter, "convert_document") as convert_mock:
            with self.assertRaises(state.StateError):
                exporter.export_targets([passed, blocked], None, overwrite=False)

        convert_mock.assert_not_called()

    def test_refuses_existing_docx_without_overwrite(self) -> None:
        draft = self.write_draft()
        self.register_complete(draft)
        self.finalize(draft, state.AuditOutcome.PASS)
        destination = draft.with_suffix(".docx")
        destination.write_bytes(b"existing")

        with patch.object(exporter, "convert_document") as convert_mock:
            with self.assertRaises(state.StateError):
                exporter.export_targets([draft], destination, overwrite=False)

        convert_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
