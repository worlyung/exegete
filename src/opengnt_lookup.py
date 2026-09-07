# -*- coding: utf-8 -*-
"""Exegete — 신약 Louw-Nida 의미영역·Levinsohn 담화 표지 조회 (OpenGNT, CC BY-SA 4.0).

2단계(문헌학·담화)에서 지금까지 기억·해석에 기대던 두 가지를 데이터로 제공한다:
  - 단어별 Louw-Nida 의미영역 번호 (예: ἀγαπάω → 25.43)
  - Levinsohn 담화 표지 (출발점 PoD·전방 강조 등, 영문 주석)
파싱코드는 한국어 풀이(OpenGNT 한국어 형태소 표)를 함께 표시한다.

greek_lookup.py(STEPBible)와 본문 계열이 달라(OGNT=Nestle 1904 기반) 단어가
다를 수 있다 — 원어 파싱·사전은 greek_lookup.py가 기준이고, 이 도구는
의미영역·담화 보조 자료다.

사용법:
    py opengnt_lookup.py "요3:16"
    py opengnt_lookup.py "엡2:8-9" --json

데이터: src/data/opengnt/ — 최초 1회 python src/build_opengnt.py 로 생성.
"""
import argparse
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "opengnt" / "opengnt.txt"
MORPH_KO = BASE / "data" / "opengnt" / "morph_korean.tsv"
ABBR = BASE / "data" / "book_abbrev.json"


def load_step_map():
    d = json.loads(ABBR.read_text(encoding="utf-8"))
    ko2book = {}
    for b in d["books"]:
        if b.get("step"):
            ko2book[b["abbr"]] = b
            ko2book[b["name"]] = b
    return ko2book


def parse_ref(ref, ko2book):
    ref = ref.replace(" ", "")
    m = re.match(r"^([가-힣]+)(\d+):(\d+)(?:-(\d+))?$", ref)
    if not m:
        return None
    book = ko2book.get(m.group(1))
    if not book:
        return None
    return book, int(m.group(2)), int(m.group(3)), int(m.group(4) or m.group(3))


def load_morph_ko():
    if not MORPH_KO.exists():
        return {}
    d = {}
    for line in MORPH_KO.read_text(encoding="utf-8").splitlines():
        if "\t" in line:
            k, v = line.split("\t", 1)
            d[k] = v
    return d


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Louw-Nida·담화 표지 조회 (OpenGNT)")
    p.add_argument("ref", help="신약 구절 (예: 요3:16, 엡2:8-9)")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if not DATA.exists():
        sys.exit("OpenGNT 데이터 없음. 먼저 실행: python src/build_opengnt.py")
    parsed = parse_ref(args.ref, load_step_map())
    if not parsed:
        sys.exit(f"구절 형식 인식 실패: '{args.ref}'")
    book, ch, vs, ve = parsed
    if book["testament"] != "NT":
        sys.exit(f"{book['name']}은(는) 구약입니다. 이 도구는 신약 전용입니다. "
                 f"(구약 원어: hebrew_lookup.py / 구약 헬라어: lxx_lookup.py)")
    step = book["step"]

    morph_ko = load_morph_ko()
    words = []
    prefix = f"{step}.{ch}:"
    for line in DATA.read_text(encoding="utf-8").splitlines():
        if not line.startswith(prefix):
            continue
        f = line.split("\t")
        v = int(f[0].split(":")[1])
        if not (vs <= v <= ve):
            continue
        words.append({
            "verse": v, "word_idx": int(f[1]), "greek": f[2], "lemma": f[3],
            "parse": f[4], "parse_ko": morph_ko.get(f[4], ""), "strong": f[5],
            "louw_nida": f[6], "ot_quotation": f[7], "discourse": f[8],
        })
    if not words:
        sys.exit(f"데이터 없음: {args.ref}")
    words.sort(key=lambda w: (w["verse"], w["word_idx"]))

    notes = [
        "LN=Louw-Nida 의미영역 번호(정의 텍스트는 저작권으로 미포함 — 번호는 도메인 분류 참조용).",
        "담화 표지는 Levinsohn GNTDF 주석(영문). PoD=출발점, Focus=초점 등.",
        "본문은 OGNT(Nestle 1904 기반)라 STEPBible(greek_lookup.py)과 단어가 다를 수 있다 — 파싱·사전 기준은 greek_lookup.py.",
        "데이터: OpenGNT © eliranwong, CC BY-SA 4.0.",
    ]
    if args.json:
        print(json.dumps({"query": args.ref, "book": book["name"], "words": words,
                          "notes": notes}, ensure_ascii=False, indent=2))
        return
    cur, in_quote = None, False
    for w in words:
        if w["verse"] != cur:
            cur, in_quote = w["verse"], False
            print(f"\n── {book['name']} {ch}:{cur} (OpenGNT) ──")
        ln = f"LN {w['louw_nida']}" if w["louw_nida"] else "LN -"
        ko = f" 〈{w['parse_ko']}〉" if w["parse_ko"] else ""
        print(f"  {w['greek']:20} [{w['strong']} {w['parse']}]{ko}  {ln}  ← {w['lemma']}")
        if bool(w["ot_quotation"]) != in_quote:
            in_quote = bool(w["ot_quotation"])
            print(f"      ◦ 구약 인용 {'시작' if in_quote else '끝'} (이 단어{'부터' if in_quote else ' 앞까지'})")
        if w["discourse"]:
            print(f"      ◦ 담화: {w['discourse']}")
    print()
    for n in notes:
        print(f"⚠ {n}")


if __name__ == "__main__":
    main()
