#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exegete — 개역한글 본문 생성 (개역한글판 1961, 저작권 만료 → Public Domain).

한국어 사용자가 아무것도 준비하지 않아도 곧바로 한국어로 주해할 수 있도록
개역한글판을 기본 본문으로 내장한다. 이 스크립트는 그 본문을 재생성한다
(저장소에는 이미 생성된 bible_korean.txt가 포함되어 있어, 보통 실행할 필요 없음).

  - 소스: open-bibles의 한국어 OSIS (Public Domain)
  - 변환: OSIS → Exegete 형식(`창1:1 본문`), '!' 인용마커 제거, 태그 정리
  - 순서로 OSIS책 → 한국어약어 매핑 (표준 개신교 66권)

저작권: 개역한글판은 대한성서공회 저작재산권 보호기간(50년) 경과로 자유 사용 가능.
        단 인격저작권(동일성유지·성명표시) 준수 — 본문을 변경하지 말고 출처를 밝힐 것.
        (대한성서공회 저작권 FAQ 참조)

사용:
    python src/build_korean_bible.py
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
ABBR = DATA / "book_abbrev.json"
SRC_URL = "https://raw.githubusercontent.com/seven1m/open-bibles/master/kor-korean.osis.xml"
OUT = DATA / "bible_korean.txt"

VERSE_RE = re.compile(r"<verse osisID='([^']+)'>(.*?)</verse>", re.S)


def clean(t: str) -> str:
    t = re.sub(r"<[^>]+>", " ", t)                 # 내부 태그 제거
    t = (t.replace("&quot;", '"').replace("&amp;", "&")
           .replace("&lt;", "<").replace("&gt;", ">").replace("&apos;", "'"))
    t = re.sub(r"\s*!\s*", " ", t)                 # 인용 끝 마커 '!' 제거(원문에 없음)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    print("Exegete — 개역한글 본문 생성 (open-bibles OSIS, Public Domain)\n")

    books = json.loads(ABBR.read_text(encoding="utf-8"))["books"]
    try:
        req = urllib.request.Request(SRC_URL, headers={"User-Agent": "Exegete-setup"})
        xml = urllib.request.urlopen(req, timeout=180).read().decode("utf-8")
    except Exception as e:
        sys.exit(f"다운로드 실패: {e}\n수동: {SRC_URL}")

    order_books, rows = [], []
    for m in VERSE_RE.finditer(xml):
        parts = m.group(1).split(".")
        if len(parts) != 3:
            continue
        bk, ch, v = parts[0], int(parts[1]), int(parts[2])
        if bk not in order_books:
            order_books.append(bk)
        rows.append((bk, ch, v, m.group(2)))

    if len(order_books) != 66:
        sys.exit(f"책 개수 이상: {len(order_books)} (66권이어야 함)")
    osis2ko = {osis: books[i]["abbr"] for i, osis in enumerate(order_books)}

    lines = []
    for bk, ch, v, body in rows:
        text = clean(body)
        if text:
            lines.append(f"{osis2ko[bk]}{ch}:{v} {text}")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  [ok] {len(lines):,}절 → {OUT.name}")
    print("\n개역한글판 © 대한성서공회 (저작재산권 만료, 자유 사용 / 본문 변경 금지·출처 표시).")
    print("이제 한국어로 바로 조회됩니다:  python src/lookup.py \"요3:16\"")


if __name__ == "__main__":
    main()
