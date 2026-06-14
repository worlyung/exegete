# -*- coding: utf-8 -*-
"""Exegete — 성경 배경 연구 주제 조회 (인물·사건·여정·제도).

주제를 고르면 관련 핵심 구절과 논쟁도를 알려준다. 실제 정리는 분석 AI가
3층(① 성경 본문 ② 역사·지리 ③ 신학)으로, 논쟁도 high면 보수·비평 양쪽 병기.

사용법:
    py background.py                 # 전체 주제 목록
    py background.py "출애굽"         # 주제 정보 + 핵심 구절 + 논쟁도
    py background.py --type 여정      # 유형별(인물/사건/여정/제도)
    py background.py "출애굽" --refs  # 핵심 구절만
"""
import argparse
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
TOPICS = BASE / "data" / "background_topics.json"

CONTROVERSY = {
    "low": "낮음 (본문 기반, 비교적 안전)",
    "medium": "중간 (일부 견해차 — 병기 권장)",
    "high": "높음 ⚠️ (역사성·연대 학계 격론 — 보수·비평 양쪽 반드시 병기)",
}


def load():
    return json.loads(TOPICS.read_text(encoding="utf-8"))["topics"]


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="성경 배경 연구 주제")
    p.add_argument("topic", nargs="?", help="주제명 (예: 출애굽, 바울 1차 선교여행)")
    p.add_argument("--type", help="유형 필터 (인물/사건/여정/제도)")
    p.add_argument("--refs", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    topics = load()

    if not args.topic:
        shown = [t for t in topics if not args.type or t["type"] == args.type]
        print("성경 배경 연구 주제:")
        cur = None
        for t in sorted(shown, key=lambda x: x["type"]):
            if t["type"] != cur:
                print(f"\n[{t['type']}]")
                cur = t["type"]
            mark = {"low": "", "medium": " (견해차 일부)", "high": " ⚠️논쟁"}[t["controversy"]]
            print(f"  • {t['name']}{mark}")
        return

    match = next((t for t in topics if t["name"] == args.topic or args.topic in t["name"]), None)
    if not match:
        sys.exit(f"주제 '{args.topic}' 없음. (목록: 인자 없이 실행)")

    if args.refs:
        print(" ".join(match["refs"]))
        return
    if args.json:
        print(json.dumps(match, ensure_ascii=False, indent=2))
        return

    print(f"=== {match['name']} ({match['type']}) ===")
    print(f"핵심 구절: {', '.join(match['refs'])}")
    print(f"논쟁도: {CONTROVERSY[match['controversy']]}")
    if match.get("note"):
        print(f"비고: {match['note']}")
    print("\n→ 3층 정리(① 본문 lookup ② 역사·지리 ③ 신학)로 전개. 논쟁도 높으면 보수·비평 병기 필수.")


if __name__ == "__main__":
    main()
