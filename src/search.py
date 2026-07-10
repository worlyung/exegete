# -*- coding: utf-8 -*-
"""Exegete — 본문 단어 검색 (번역 본문에서 직접, 한국어/영어).

'은혜'·'사랑'처럼 번역 본문에 나오는 단어를 성경 전체에서 찾는다.
※ 원어(헬라어·히브리어) 스트롱번호 검색은 word_search.py.
   이건 번역 본문(개역한글·개역개정·WEB 등, 현재 설정된 본문) 검색이다.

사용:
    python src/search.py "은혜"
    python src/search.py "은혜" --count       # 분포(책별 횟수)만
    python src/search.py "믿음" --book 롬      # 특정 책만
    python src/search.py "사랑" --json

본문은 lookup.py와 동일 우선순위(개역개정 > 개역한글 > WEB).
"""
import argparse
import json
import sys
from collections import OrderedDict

import lookup

LIMIT = 200


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    p = argparse.ArgumentParser(description="성경 본문 단어 검색 (번역 본문 기준)")
    p.add_argument("word", help="찾을 단어 (예: 은혜, 사랑, love)")
    p.add_argument("--book", default=None, help="특정 책만 (예: 롬, 시)")
    p.add_argument("--count", action="store_true", help="구절 없이 분포(책별 횟수)만")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    word = args.word.strip()
    if not word:
        sys.exit("검색어가 비어 있습니다.")

    alias2step, step2ko, step2en, step2test = lookup.load_books()
    name_map = step2en if lookup.is_english_bible() else step2ko

    book_filter = None
    if args.book:
        book_filter = lookup.to_step(args.book, alias2step)
        if not book_filter:
            sys.exit(f"책 이름 인식 실패: '{args.book}' (예: 롬, 로마서, 시)")

    verses, order = lookup.load_verses(alias2step)

    hits, dist = [], OrderedDict()
    for k in order:
        step, ch, v = k
        if book_filter and step != book_filter:
            continue
        text = verses[k][1]
        if word in text:
            hits.append((step, ch, v, text))
            dist[step] = dist.get(step, 0) + 1

    scope = f" — {args.book}" if args.book else ""
    if args.json:
        print(json.dumps({
            "word": word, "total": len(hits),
            "by_book": {name_map.get(s, s): c for s, c in dist.items()},
            "verses": [
                {"ref": f"{name_map.get(s, s)} {c}:{vv}", "step": s,
                 "chapter": c, "verse": vv, "text": t}
                for (s, c, vv, t) in hits[:LIMIT]
            ],
        }, ensure_ascii=False, indent=2))
        return

    print(f"'{word}' — 총 {len(hits)}회 출현{scope}")
    if dist:
        print("책별 분포:", ", ".join(f"{name_map.get(s, s)}({c})" for s, c in dist.items()))
    if args.count or not hits:
        return

    print("\n출현 구절:")
    for step, ch, v, text in hits[:LIMIT]:
        hl = text.replace(word, f"《{word}》")
        print(f"  {name_map.get(step, step)} {ch}:{v}  {hl}")
    if len(hits) > LIMIT:
        print(f"  … 외 {len(hits) - LIMIT}개 더 (--count 로 분포만, --book 으로 범위 좁히기)")


if __name__ == "__main__":
    main()
