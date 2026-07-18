from __future__ import annotations

import json
import importlib
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

router = importlib.import_module("router")


class RouterTests(unittest.TestCase):
    def test_routes_reference_request_without_direct_output(self) -> None:
        request = "요한복음 3:16을 4단계 주해해줘"

        plan = router.plan_request(request)

        self.assertEqual(plan["mode"], "full_exegesis")
        self.assertFalse(plan["direct_output"])
        self.assertFalse(plan["store_request"])
        self.assertNotIn(request, json.dumps(plan, ensure_ascii=False))

    def test_prioritizes_safety_without_echoing_request(self) -> None:
        request = "지금 자살하고 싶어요. 요한복음 3:16을 알려줘"

        plan = router.plan_request(request)

        self.assertEqual(plan["mode"], "safety_first")
        self.assertTrue(plan["safety_review_required"])
        self.assertNotIn(request, json.dumps(plan, ensure_ascii=False))

    def test_prioritizes_immediate_violence_without_echoing_request(self) -> None:
        request = "남편이 지금 나를 때리고 있어요"

        plan = router.plan_request(request)

        self.assertEqual(plan["mode"], "safety_first")
        self.assertNotIn(request, json.dumps(plan, ensure_ascii=False))

    def test_marks_privacy_without_echoing_identifier(self) -> None:
        request = "제 이메일 person@example.com으로 묵상 보내줘"

        plan = router.plan_request(request)

        self.assertEqual(plan["mode"], "privacy_review")
        self.assertFalse(plan["store_request"])
        self.assertNotIn("person@example.com", json.dumps(plan, ensure_ascii=False))

    def test_flags_high_controversy_background(self) -> None:
        plan = router.plan_request("출애굽의 역사성과 광야 경로 배경을 정리해줘")

        self.assertEqual(plan["mode"], "background_research")
        self.assertTrue(plan["safety_review_required"])

    def test_requires_scope_for_unresolved_original_language_request(self) -> None:
        plan = router.plan_request("원어 뜻을 알려줘")

        self.assertEqual(plan["mode"], "needs_scope")
        self.assertEqual(plan["status"], "needs_clarification")


if __name__ == "__main__":
    unittest.main()
