# -*- coding: utf-8 -*-
"""Exegete — 여러 번역 나란히 비교 (한국어 + 영어 + 원어).

한 구절을 개역한글(또는 사용자 개역개정)·WEB(영어)·원어(헬라어/히브리어)로
한눈에 나란히 본다. 번역마다 강조점이 다른 곳을 빠르게 포착할 수 있다.

사용:
    python src/compare.py "요3:16"
    python src/compare.py "창1:1-2"

본문: 한국어=현재 설정(개역개정>개역한글), 영어=web.txt(PD), 원어=STEPBible.
"""
import argparse
import sys
from pathlib import Path

import lookup

BASE = Path(__file__).resolve().parent
WEB = BASE / "data" / "web.txt"


def _ko_label():
    n = lookup.DATA.name.lower()
    if "krv" in n:
        return "개역개정"
    if "korean" in n:
        return "개역한글"
    return lookup.DATA.stem


def _verse(alias2step, path, step, ch, v):
    if not path or not path.exists():
        return None
    verses, _ = lookup.load_verses(alias2step, data=path)
    hit = verses.get((step, ch, v))
    return hit[1] if hit else None


def _original(step, ch, v, testament):
    """해당 절의 원어 원문(단어 이어붙이기). 데이터 없으면 None."""
    try:
        if testament == "NT":
            import greek_lookup
            words = greek_lookup.load_words(step, ch, v, v)
            key = "greek"
        else:
            import hebrew_lookup
            words = hebrew_lookup.load_words(step, ch, v, v)
            key = "hebrew"
        text = " ".join(w[key] for w in words if w.get(key))
        return text or None
    except Exception:
        return None


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    p = argparse.ArgumentParser(description="여러 번역 나란히 비교 (한/영/원어)")
    p.add_argument("ref", help="구절 (예: 요3:16, 창1:1-2)")
    args = p.parse_args()

    alias2step, step2ko, step2en, step2test = lookup.load_books()
    parsed = lookup.parse_ref(args.ref, alias2step)
    if not parsed:
        sys.exit(f"구절 인식 실패: '{args.ref}' (예: 요3:16 / 창1:1-2)")
    step, ch, vs, ve = parsed
    testament = step2test[step]
    ko_name = step2ko[step]
    ko_label = _ko_label()
    orig_label = "헬라어" if testament == "NT" else "히브리어"

    for v in range(vs, ve + 1):
        print(f"── {ko_name} {ch}:{v} ──")
        ko = _verse(alias2step, lookup.DATA, step, ch, v)
        if ko:
            print(f"  [{ko_label}] {ko}")
        en = _verse(alias2step, WEB, step, ch, v)
        if en:
            print(f"  [WEB]      {en}")
        orig = _original(step, ch, v, testament)
        if orig:
            print(f"  [{orig_label}]   {orig}")
        if not (ko or en or orig):
            print("  (본문 없음)")
        print()

    print("※ 원어 단어별 파싱·사전 정의는:  python src/"
          + ("greek_lookup.py" if testament == "NT" else "hebrew_lookup.py")
          + f" \"{args.ref}\" --lex")


if __name__ == "__main__":
    main()
