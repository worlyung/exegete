from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / "src" / "series.py"


def run_series(data_file: Path) -> subprocess.CompletedProcess[str]:
    """Run series.py against one isolated Bible-data fixture."""
    environment = os.environ.copy()
    environment["EXEGETE_BIBLE"] = str(data_file)
    return subprocess.run(
        [sys.executable, str(SERIES), "빌립보서", "--json"],
        capture_output=True,
        check=False,
        cwd=ROOT,
        encoding="utf-8",
        env=environment,
        text=True,
    )


class SeriesHeadingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.fixture_dir = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_data(self, name: str, contents: str) -> Path:
        data_file = self.fixture_dir / name
        data_file.write_text(contents, encoding="utf-8")
        return data_file

    def test_series_refuses_headingless_book(self) -> None:
        data_file = self.write_data(
            "headingless.txt",
            "빌1:1 첫 절\n빌1:2 둘째 절\n빌2:1 다음 장\n",
        )

        result = run_series(data_file)

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("소제목 없음", result.stderr)

    def test_series_uses_explicit_heading_boundaries(self) -> None:
        data_file = self.write_data(
            "headed.txt",
            "빌1:1 <첫 단락> 첫 절\n빌1:2 둘째 절\n"
            "빌1:3 <둘째 단락> 셋째 절\n빌1:4 넷째 절\n",
        )

        result = run_series(data_file)

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["count"], 2)
        self.assertEqual(payload["units"][0], {"start": "1:1", "title": "첫 단락", "end": "1:2"})
        self.assertEqual(payload["units"][1], {"start": "1:3", "title": "둘째 단락", "end": "1:4"})


if __name__ == "__main__":
    unittest.main()
