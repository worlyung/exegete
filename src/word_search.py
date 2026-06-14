# -*- coding: utf-8 -*-
"""Exegete — 원어 단어·주제 연구 (스트롱번호/원어/영어뜻으로 전체 검색).

주제별 성경 연구·단어 연구의 핵심 도구. 원어 데이터(STEPBible)에서
특정 단어가 나오는 모든 구절을 찾아 출현 분포를 보여준다.

사용법:
    py word_search.py G26            # 스트롱번호(헬라어 사랑 ἀγάπη)
    py word_search.py H2617          # 스트롱번호(히브리어 헤세드 חֶסֶד)
    py word_search.py --gloss love   # 영어 뜻으로
    py word_search.py G26 --refs     # 구절 ref만 (주해 연결용)
    py word_search.py G26 --limit 30

스트롱번호: G####(헬라어) / H####(히브리어). docs/DATA_SOURCES.md 참조.
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
GREEK_DIR = BASE / "data" / "original" / "greek"
HEB_DIR = BASE / "data" / "original" / "hebrew"
ABBR = BASE / "data" / "book_abbrev.json"


def step2name():
    d = json.loads(ABBR.read_text(encoding="utf-8"))
    return {b["step"]: b["name"] for b in d["books"] if b.get("step")}


def search(strong=None, gloss=None, limit=200):
    s2n = step2name()
    hits = []
    is_greek = strong and strong.upper().startswith("G")
    is_heb = strong and strong.upper().startswith("H")
    dirs = []
    if strong:
        dirs = [GREEK_DIR] if is_greek else [HEB_DIR] if is_heb else [GREEK_DIR, HEB_DIR]
    else:
        dirs = [GREEK_DIR, HEB_DIR]
    target = strong.upper().lstrip("GH") if strong else None

    for d in dirs:
        is_heb_dir = (d == HEB_DIR)
        for f in sorted(d.glob("*.txt")):
            for line in f.read_text(encoding="utf-8").splitlines():
                m = re.match(r"^([0-9A-Za-z]+)\.(\d+)\.(\d+)#\d+\S*\t(.*)$", line)
                if not m:
                    continue
                book, ch, v, rest = m.group(1), int(m.group(2)), int(m.group(3)), m.group(4)
                fields = rest.split("\t")
                if strong:
                    # 주 단어의 스트롱만 매칭 (노이즈 제거): 헬=fields[2], 히=fields[3]
                    raw = (fields[3] if is_heb_dir else fields[2]) if len(fields) > (3 if is_heb_dir else 2) else ""
                    nums = re.findall(r"[GH](\d+)[A-Za-z]?", raw)
                    if target.lstrip("0") not in [n.lstrip("0") for n in nums]:
                        continue
                elif gloss:
                    en = " ".join(fields[:4]).lower()
                    if gloss.lower() not in en:
                        continue
                word = fields[0].strip()
                hits.append((book, ch, v, word))
                if len(hits) >= limit:
                    break
    return hits, s2n


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="원어 단어·주제 검색")
    p.add_argument("strong", nargs="?", help="스트롱번호 G#### / H####")
    p.add_argument("--gloss", help="영어 뜻으로 검색")
    p.add_argument("--refs", action="store_true", help="구절 ref만")
    p.add_argument("--limit", type=int, default=200)
    args = p.parse_args()
    if not args.strong and not args.gloss:
        sys.exit("스트롱번호 또는 --gloss 필요. 예: word_search.py G26")

    hits, s2n = search(args.strong, args.gloss, args.limit)
    if not hits:
        sys.exit("검색 결과 없음")

    if args.refs:
        print(" ".join(f"{s2n.get(b,b)}{c}:{v}" for b, c, v, _ in hits))
        return

    by_book = defaultdict(int)
    for b, c, v, w in hits:
        by_book[s2n.get(b, b)] += 1
    print(f"총 {len(hits)}회 출현 (limit {args.limit})")
    print("책별 분포:", ", ".join(f"{bk}({n})" for bk, n in by_book.items()))
    print("\n출현 구절:")
    for b, c, v, w in hits[:50]:
        print(f"  {s2n.get(b,b)} {c}:{v}  {w}")
    if len(hits) > 50:
        print(f"  ... 외 {len(hits)-50}회")


if __name__ == "__main__":
    main()
