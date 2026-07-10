#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exegete — 관주(cross-reference) 데이터 생성 (openbible.info, CC BY).

한 구절에 대한 '관련 구절'을 자동 연결한다(설교·성경공부 준비). 데이터는
Treasury of Scripture Knowledge 기반 openbible.info 관주(약 34만 개, CC BY).

  - 소스: https://a.openbible.info/data/cross-references.zip
  - 변환: openbible osisID(John.3.16) → Exegete step 키(Jhn3:16), votes 내림차순
  - 산출: src/data/xref/cross_references.json

사용:
    python src/build_xref.py

라이선스: Cross-reference data © openbible.info, CC BY. 출처를 밝혀 사용할 것.
"""
import io
import json
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
ABBR = BASE / "data" / "book_abbrev.json"
OUTDIR = BASE / "data" / "xref"
URL = "https://a.openbible.info/data/cross-references.zip"

# openbible/SBL osisID 책 약어 — 표준 개신교 66권 순서(book_abbrev.json과 1:1)
SBL_ORDER = [
    "Gen", "Exod", "Lev", "Num", "Deut", "Josh", "Judg", "Ruth", "1Sam", "2Sam",
    "1Kgs", "2Kgs", "1Chr", "2Chr", "Ezra", "Neh", "Esth", "Job", "Ps", "Prov",
    "Eccl", "Song", "Isa", "Jer", "Lam", "Ezek", "Dan", "Hos", "Joel", "Amos",
    "Obad", "Jonah", "Mic", "Nah", "Hab", "Zeph", "Hag", "Zech", "Mal", "Matt",
    "Mark", "Luke", "John", "Acts", "Rom", "1Cor", "2Cor", "Gal", "Eph", "Phil",
    "Col", "1Thess", "2Thess", "1Tim", "2Tim", "Titus", "Phlm", "Heb", "Jas",
    "1Pet", "2Pet", "1John", "2John", "3John", "Jude", "Rev",
]


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    print("Exegete — 관주 데이터 생성 (openbible.info, CC BY)\n")

    books = json.loads(ABBR.read_text(encoding="utf-8"))["books"]
    if len(books) != 66:
        sys.exit(f"book_abbrev.json 책 수 이상: {len(books)}")
    osis2step = {SBL_ORDER[i]: books[i]["step"] for i in range(66)}

    def stepkey(osis):
        """단일 osisID(John.3.16) → 'Jhn3:16'. 매핑 실패 시 None."""
        m = re.match(r"([1-3]?[A-Za-z]+)\.(\d+)\.(\d+)$", osis)
        if not m:
            return None
        st = osis2step.get(m.group(1))
        return f"{st}{m.group(2)}:{m.group(3)}" if st else None

    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "Exegete-setup"})
        raw = urllib.request.urlopen(req, timeout=180).read()
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            name = next(n for n in z.namelist() if n.endswith(".txt"))
            text = z.read(name).decode("utf-8")
    except Exception as e:
        sys.exit(f"다운로드 실패: {e}\n수동: {URL}")

    xref, skipped = {}, 0
    for line in text.splitlines()[1:]:            # 첫 줄은 헤더
        p = line.split("\t")
        if len(p) < 3:
            continue
        key = stepkey(p[0])
        if not key:
            skipped += 1
            continue
        try:
            votes = int(p[1 + 1])  # p[2] = Votes
        except ValueError:
            votes = 0
        xref.setdefault(key, []).append([p[1], votes])  # [to_osisID, votes]

    for k in xref:
        xref[k].sort(key=lambda x: -x[1])

    OUTDIR.mkdir(parents=True, exist_ok=True)
    out = OUTDIR / "cross_references.json"
    out.write_text(json.dumps(xref, ensure_ascii=False), encoding="utf-8")
    (OUTDIR / "LICENSE.txt").write_text(
        "Cross-reference data © openbible.info — CC BY.\n"
        "Based on Treasury of Scripture Knowledge (public domain).\n"
        "https://www.openbible.info/labs/cross-references/\n", encoding="utf-8")
    print(f"  [ok] 출발 구절 {len(xref):,}개 → {out.name}  (건너뜀 {skipped})")
    print("이제 관주 조회 가능:  python src/xref.py \"요3:16\"")


if __name__ == "__main__":
    main()
