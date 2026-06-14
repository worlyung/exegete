# -*- coding: utf-8 -*-
"""Exegete — 강해 설교 시리즈 기획 (책을 페리코페 단위로 분할).

한 권의 책을 소제목(단락) 단위로 나눠 연속 강해 설교/성경공부 시리즈의
골격을 만든다. 각 단락은 4단계 주해로 연결할 수 있다.

사용법:
    py series.py "빌립보서"      # 단락(설교 회차) 목록
    py series.py "빌"
    py series.py "엡" --json

본문 데이터(소제목 포함)가 필요하다(data/<번역본>.txt). 개역개정의 <소제목>을
단락 경계로 사용한다.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = Path(os.environ.get("EXEGETE_BIBLE", BASE / "data" / "bible_krv.txt"))
ABBR = BASE / "data" / "book_abbrev.json"


def load_books():
    d = json.loads(ABBR.read_text(encoding="utf-8"))
    a2n, n2a = {}, {}
    for b in d["books"]:
        a2n[b["abbr"]] = b["name"]
        n2a[b["name"]] = b["abbr"]
    return a2n, n2a


def norm_book(tok, a2n, n2a):
    tok = tok.strip()
    if tok in a2n:
        return tok
    if tok in n2a:
        return n2a[tok]
    return None


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="강해 시리즈 기획 (책→단락)")
    p.add_argument("book", help="책명 (예: 빌립보서, 빌)")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    a2n, n2a = load_books()
    abbr = norm_book(args.book, a2n, n2a)
    if not abbr:
        sys.exit(f"책 인식 실패: '{args.book}'")
    if not DATA.exists():
        sys.exit(f"본문 데이터 없음: {DATA} (data/README.md 참조)")

    name = a2n[abbr]
    units = []      # [(start_ref, title, [verses...])]
    cur = None
    for line in DATA.read_text(encoding="utf-8").splitlines():
        m = re.match(rf"^{re.escape(abbr)}(\d+):(\d+)\s+(.*)$", line)
        if not m:
            continue
        ch, v, body = int(m.group(1)), int(m.group(2)), m.group(3)
        hm = re.match(r"^<([^>]+)>", body)
        if hm or cur is None:
            title = hm.group(1) if hm else "(서두)"
            cur = {"start": f"{ch}:{v}", "title": title, "end": f"{ch}:{v}"}
            units.append(cur)
        else:
            cur["end"] = f"{ch}:{v}"

    if not units:
        sys.exit(f"{name} 본문/소제목 없음 (해당 번역본에 소제목이 있는지 확인)")

    if args.json:
        print(json.dumps({"book": name, "count": len(units), "units": units}, ensure_ascii=False, indent=2))
    else:
        print(f"=== {name} 강해 시리즈 골격 — 총 {len(units)}회 ===\n")
        for i, u in enumerate(units, 1):
            sc, ec = u["start"].split(":")[0], u["end"].split(":")[0]
            ev = u["end"].split(":")[1]
            if u["start"] == u["end"]:
                rng = u["start"]
            elif sc == ec:
                rng = f"{u['start']}-{ev}"          # 같은 장: 1:3-11
            else:
                rng = f"{u['start']}-{u['end']}"     # 장 넘김: 3:17-4:1
            print(f"{i:2}회  {name} {rng}  — {u['title']}")
        print(f"\n각 회차를 4단계 주해로 전개하려면: 해당 구절로 주해 요청")


if __name__ == "__main__":
    main()
