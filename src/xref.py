# -*- coding: utf-8 -*-
"""Exegete — 관주(관련 구절) 조회 (openbible.info / TSK, CC BY).

한 구절과 신학적·주제적으로 연결된 구절들을 관련도(votes) 순으로 제시한다.
설교·성경공부 준비에서 '이 구절과 이어지는 말씀'을 빠르게 모은다.

먼저 데이터 생성:  python src/build_xref.py
사용:
    python src/xref.py "요3:16"
    python src/xref.py "요3:16" --top 15
    python src/xref.py "요3:16" --refs      # 구절만(본문 없이)
"""
import argparse
import json
import re
import sys

import lookup

XREF = lookup.BASE / "data" / "xref" / "cross_references.json"

# openbible/SBL osisID 책 약어 — 표준 66권 순서(book_abbrev.json과 1:1)
SBL_ORDER = [
    "Gen", "Exod", "Lev", "Num", "Deut", "Josh", "Judg", "Ruth", "1Sam", "2Sam",
    "1Kgs", "2Kgs", "1Chr", "2Chr", "Ezra", "Neh", "Esth", "Job", "Ps", "Prov",
    "Eccl", "Song", "Isa", "Jer", "Lam", "Ezek", "Dan", "Hos", "Joel", "Amos",
    "Obad", "Jonah", "Mic", "Nah", "Hab", "Zeph", "Hag", "Zech", "Mal", "Matt",
    "Mark", "Luke", "John", "Acts", "Rom", "1Cor", "2Cor", "Gal", "Eph", "Phil",
    "Col", "1Thess", "2Thess", "1Tim", "2Tim", "Titus", "Phlm", "Heb", "Jas",
    "1Pet", "2Pet", "1John", "2John", "3John", "Jude", "Rev",
]


def osis_parts(osis, osis2step):
    """'Rom.5.8' / '1John.4.9-1John.4.10' → (step, ch, v, is_range) 첫 절 기준."""
    first = osis.split("-")[0]
    m = re.match(r"([1-3]?[A-Za-z]+)\.(\d+)\.(\d+)", first)
    if not m:
        return None
    st = osis2step.get(m.group(1))
    if not st:
        return None
    return st, int(m.group(2)), int(m.group(3)), ("-" in osis)


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    p = argparse.ArgumentParser(description="관주(관련 구절) 조회 (openbible.info, CC BY)")
    p.add_argument("ref", help="구절 (예: 요3:16)")
    p.add_argument("--top", type=int, default=12, help="상위 N개 (기본 12)")
    p.add_argument("--refs", action="store_true", help="구절만(본문 없이)")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if not XREF.exists():
        sys.exit("관주 데이터가 없습니다. 먼저:  python src/build_xref.py")
    data = json.loads(XREF.read_text(encoding="utf-8"))

    alias2step, step2ko, step2en, step2test = lookup.load_books()
    books = json.loads(lookup.ABBR.read_text(encoding="utf-8"))["books"]
    osis2step = {SBL_ORDER[i]: books[i]["step"] for i in range(66)}
    name_map = step2en if lookup.is_english_bible() else step2ko

    parsed = lookup.parse_ref(args.ref, alias2step)
    if not parsed:
        sys.exit(f"구절 인식 실패: '{args.ref}' (예: 요3:16)")
    step, ch, vs, ve = parsed

    verses = None
    if not args.refs:
        verses, _ = lookup.load_verses(alias2step)

    out_json = {}
    for v in range(vs, ve + 1):
        key = f"{step}{ch}:{v}"
        xrefs = data.get(key, [])[:args.top]
        items = []
        for to_osis, votes in xrefs:
            pp = osis_parts(to_osis, osis2step)
            if not pp:
                continue
            st, tch, tv, is_range = pp
            disp = f"{name_map.get(st, st)} {tch}:{tv}" + ("…" if is_range else "")
            body = None
            if verses is not None:
                hit = verses.get((st, tch, tv))
                body = hit[1] if hit else None
            items.append((disp, votes, body))

        if args.json:
            out_json[f"{name_map[step]} {ch}:{v}"] = [
                {"ref": d, "votes": vo, "text": b} for (d, vo, b) in items]
            continue

        print(f"── {name_map[step]} {ch}:{v} — 관주 {len(items)}개 (관련도순) ──")
        if not items:
            print("  (관주 없음)")
        for i, (disp, votes, body) in enumerate(items, 1):
            line = f"  {i:2}. {disp} ({votes})"
            if body:
                line += f"  {body[:55]}" + ("…" if len(body) > 55 else "")
            print(line)
        print()

    if args.json:
        print(json.dumps(out_json, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
