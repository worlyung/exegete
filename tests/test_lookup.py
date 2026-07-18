from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
LOOKUP = ROOT / "src" / "lookup.py"


def run_lookup(
    data_file: Path, reference: str, *options: str
) -> subprocess.CompletedProcess[str]:
    """Run lookup.py against one isolated Bible-data fixture."""
    environment = os.environ.copy()
    environment["EXEGETE_BIBLE"] = str(data_file)
    return subprocess.run(
        [sys.executable, str(LOOKUP), reference, "--pericope", *options],
        capture_output=True,
        check=False,
        cwd=ROOT,
        encoding="utf-8",
        env=environment,
        text=True,
    )


class LookupPericopeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.fixture_dir = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_data(self, name: str, contents: str) -> Path:
        data_file = self.fixture_dir / name
        data_file.write_text(contents, encoding="utf-8")
        return data_file

    def test_pericope_uses_chapter_fallback_without_headings(self) -> None:
        # Given: a default-style data file with no pericope headings.
        data_file = self.write_data(
            "headingless.txt",
            "요3:1 첫 절\n요3:2 대상 절\n요3:3 셋째 절\n요4:1 다음 장\n",
        )

        # When: the user asks for the pericope containing John 3:2.
        result = run_lookup(data_file, "요3:2")

        # Then: the result stays within the chapter and discloses the fallback.
        self.assertEqual(result.returncode, 0)
        self.assertIn("요한복음 3:1", result.stdout)
        self.assertIn("요한복음 3:3", result.stdout)
        self.assertNotIn("요한복음 4:1", result.stdout)
        self.assertIn("요청 절 앞 같은 장의 소제목 경계", result.stderr)

    def test_pericope_keeps_heading_boundaries_when_available(self) -> None:
        # Given: data with explicit pericope headings.
        data_file = self.write_data(
            "headed.txt",
            "요3:1 <첫 단락> 첫 절\n요3:2 둘째 절\n"
            "요3:3 <둘째 단락> 대상 절\n요3:4 넷째 절\n요3:5 다섯째 절\n",
        )

        # When: the user asks for the pericope containing John 3:3.
        result = run_lookup(data_file, "요3:3")

        # Then: the existing heading-based boundary is preserved without a fallback warning.
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("요한복음 3:1", result.stdout)
        self.assertIn("요한복음 3:3", result.stdout)
        self.assertIn("요한복음 3:5", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_pericope_uses_chapter_fallback_when_only_another_chapter_has_headings(
        self,
    ) -> None:
        # Given: a book whose previous chapter has headings but the requested chapter does not.
        data_file = self.write_data(
            "mixed-headings.txt",
            "요2:1 <이전 단락> 이전 절\n요2:2 이전 장 끝\n"
            "요3:1 첫 절\n요3:2 대상 절\n요3:3 셋째 절\n요4:1 다음 장\n",
        )

        # When: the user asks for a verse in the headingless chapter.
        result = run_lookup(data_file, "요3:2")

        # Then: unrelated headed chapters do not widen the requested pericope.
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("요한복음 2:1", result.stdout)
        self.assertIn("요한복음 3:1", result.stdout)
        self.assertIn("요한복음 3:3", result.stdout)
        self.assertNotIn("요한복음 4:1", result.stdout)
        self.assertIn("요청 절 앞 같은 장의 소제목 경계", result.stderr)

    def test_pericope_fallback_keeps_json_on_stdout(self) -> None:
        data_file = self.write_data(
            "json-headingless.txt",
            "John3:1 First\nJohn3:2 Target\nJohn3:3 Third\nJohn4:1 Next\n",
        )

        result = run_lookup(data_file, "John 3:2", "--json")

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual([verse["ref"] for verse in payload["verses"]], ["Jhn3:1", "Jhn3:2", "Jhn3:3"])
        self.assertEqual(
            [verse["ref"] for verse in payload["verses"] if verse["target"]],
            ["Jhn3:2"],
        )
        self.assertIn("문맥 폴백", result.stderr)


if __name__ == "__main__":
    unittest.main()
