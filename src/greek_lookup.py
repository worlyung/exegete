# -*- coding: utf-8 -*-
"""Exegete — 헬라어 신약 원어 형태소 조회 (STEPBible TAGNT, CC BY 4.0).

성경 분석 2단계(문헌학)에서 원어를 기억이 아니라 데이터로 정확히 추출한다.
각 단어의 원어·음역·뜻·스트롱번호·문법파싱·출처사본을 제공한다.

사용법:
    py greek_lookup.py "요3:16"
    py greek_lookup.py "엡2:8-9"
    py greek_lookup.py "엡2:8" --json

데이터: src/data/original/greek/ (STEPBible TAGNT, CC BY 4.0)
파싱코드 해석: docs/MORPH_CODES.md 참조 (분석 AI가 해석)
"""
import argparse
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
GREEK_DIR = BASE / "data" / "original" / "greek"
ABBR = BASE / "data" / "book_abbrev.json"


def load_step_map():
    d = json.loads(ABBR.read_text(encoding="utf-8"))
    ko2step, step2name = {}, {}
    for b in d["books"]:
        if b.get("step"):
            ko2step[b["abbr"]] = b["step"]
            ko2step[b["name"]] = b["step"]
            step2name[b["step"]] = b["name"]
    return ko2step, step2name


def parse_ref(ref, ko2step):
    ref = ref.replace(" ", "")
    m = re.match(r"^([가-힣]+)(\d+):(\d+)(?:-(\d+))?$", ref)
    if not m:
        return None
    book, ch, vs, ve = m.group(1), int(m.group(2)), int(m.group(3)), m.group(4)
    step = ko2step.get(book)
    if not step:
        return None
    return step, ch, vs, int(ve) if ve else vs


def load_words(step, ch, vs, ve):
    """TAGNT 파일에서 해당 절들의 단어 추출."""
    words = []
    for f in sorted(GREEK_DIR.glob("*.txt")):
        for line in f.read_text(encoding="utf-8").splitlines():
            # 형식: Eph.2.8#05=NKO \t σεσῳσμένοι (..) \t saved \t G4982=V-RPP-NPM \t σῴζω=to save \t 사본...
            m = re.match(rf"^{re.escape(step)}\.(\d+)\.(\d+)#(\d+)\S*\t(.*)$", line)
            if not m:
                continue
            c, v = int(m.group(1)), int(m.group(2))
            if c != ch or not (vs <= v <= ve):
                continue
            fields = m.group(4).split("\t")
            greek = fields[0].strip() if len(fields) > 0 else ""
            gloss = fields[1].strip() if len(fields) > 1 else ""
            strong_parse = fields[2].strip() if len(fields) > 2 else ""
            lemma = fields[3].strip() if len(fields) > 3 else ""
            strong, parse = "", ""
            if "=" in strong_parse:
                strong, parse = strong_parse.split("=", 1)
            words.append({
                "ref": f"{step}.{c}.{v}", "chapter": c, "verse": v, "word_idx": int(m.group(3)),
                "greek": greek, "gloss_en": gloss, "strong": strong, "parse": parse, "lemma": lemma,
            })
    words.sort(key=lambda w: (w["chapter"], w["verse"], w["word_idx"]))
    return words


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="헬라어 신약 원어 조회 (STEPBible TAGNT)")
    p.add_argument("ref", help="구절 (예: 요3:16, 엡2:8-9)")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    ko2step, step2name = load_step_map()
    parsed = parse_ref(args.ref, ko2step)
    if not parsed:
        sys.exit(f"구절 형식 인식 실패 또는 구약(헬라어 없음): '{args.ref}'")
    step, ch, vs, ve = parsed
    if step not in {b for b in step2name}:
        pass
    words = load_words(step, ch, vs, ve)
    if not words:
        sys.exit(f"원어 데이터 없음: {args.ref} (신약만 지원. 데이터 설치 확인: src/data/original/greek/)")

    name = step2name.get(step, step)
    if args.json:
        print(json.dumps({"query": args.ref, "book": name, "words": words}, ensure_ascii=False, indent=2))
    else:
        cur = None
        for w in words:
            vk = (w["chapter"], w["verse"])
            if vk != cur:
                print(f"\n── {name} {w['chapter']}:{w['verse']} ──")
                cur = vk
            print(f"  {w['greek']:20} {w['gloss_en']:18} [{w['strong']} {w['parse']}]  ← {w['lemma']}")


if __name__ == "__main__":
    main()
