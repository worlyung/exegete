# -*- coding: utf-8 -*-
"""Exegete — 교회력(절기) 핵심 본문 조회.

사용법:
    py liturgical.py                 # 전체 절기 목록
    py liturgical.py "부활절"          # 해당 절기의 핵심 구절 + 본문
    py liturgical.py "부활절" --json
    py liturgical.py "부활절" --refs-only   # 구절 ref만 (4단계 주해로 넘길 때)

절기-본문 매칭은 전통(RCL·한국 개신교 관행) 기준이며 교파별로 다를 수 있다.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
LIT = BASE / "data" / "liturgical_readings.json"


def load():
    return json.loads(LIT.read_text(encoding="utf-8"))["seasons"]


def find(seasons, name):
    name = name.strip()
    for s in seasons:
        if s["name"] == name or s["en"].lower() == name.lower():
            return s
    # 부분 매칭
    for s in seasons:
        if name in s["name"] or name.lower() in s["en"].lower():
            return s
    return None


def verse_text(ref):
    """lookup.py로 본문 첫 줄 추출(대표)."""
    res = subprocess.run([sys.executable, str(BASE / "lookup.py"), ref],
                         capture_output=True, text=True, encoding="utf-8")
    return res.stdout.strip() if res.returncode == 0 else "(본문 조회 실패)"


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    p = argparse.ArgumentParser(description="교회력 절기 본문 조회")
    p.add_argument("season", nargs="?", help="절기명 (예: 부활절, Easter)")
    p.add_argument("--json", action="store_true")
    p.add_argument("--refs-only", action="store_true", help="구절 ref만 출력")
    args = p.parse_args()

    seasons = load()

    if not args.season:
        print("교회력 절기 목록:")
        for s in seasons:
            refs = ", ".join(r["ref"] for r in s["readings"])
            print(f"  • {s['name']} ({s['en']}) — {s['desc']}")
            print(f"      대표 본문: {refs}")
        return

    s = find(seasons, args.season)
    if not s:
        names = " / ".join(x["name"] for x in seasons)
        sys.exit(f"절기 '{args.season}' 없음. 가능: {names}")

    if args.refs_only:
        print(" ".join(r["ref"] for r in s["readings"]))
        return

    if args.json:
        print(json.dumps(s, ensure_ascii=False, indent=2))
        return

    print(f"=== {s['name']} ({s['en']}) ===")
    print(f"{s['desc']}\n")
    for r in s["readings"]:
        print(f"▶ {r['ref']} — {r['theme']}")
        print(f"   {verse_text(r['ref'])}\n")


if __name__ == "__main__":
    main()
