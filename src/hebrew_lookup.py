# -*- coding: utf-8 -*-
"""Exegete — 히브리어 구약 원어 형태소 조회 (STEPBible TAHOT, CC BY 4.0).

성경 분석 2단계(문헌학)에서 히브리어 원어를 기억이 아니라 데이터로 정확히 추출한다.
각 단어의 히브리어·음역·뜻·스트롱번호·문법파싱·원형을 제공한다.

사용법:
    py hebrew_lookup.py "창1:1"
    py hebrew_lookup.py "시23:1-3"
    py hebrew_lookup.py "창1:1" --json

데이터: src/data/original/hebrew/ (STEPBible TAHOT, CC BY 4.0)
파싱코드: H + V(동사)qp3ms 등. 분석 AI가 해석(예: HVqp3ms=칼 완료 3인칭남성단수).
"""
import argparse
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
HEB_DIR = BASE / "data" / "original" / "hebrew"
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
    """TAHOT 파일에서 해당 절들의 단어 추출. 히브리어 필드 위치 기준."""
    words = []
    for f in sorted(HEB_DIR.glob("*.txt")):
        for line in f.read_text(encoding="utf-8").splitlines():
            m = re.match(rf"^{re.escape(step)}\.(\d+)\.(\d+)#(\d+)\S*\t(.*)$", line)
            if not m:
                continue
            c, v = int(m.group(1)), int(m.group(2))
            if c != ch or not (vs <= v <= ve):
                continue
            fields = m.group(4).split("\t")
            # 필드: 0=히브리어 1=음역 2=영어뜻 3=스트롱 4=파싱 ... 11=렘마정의
            heb = fields[0].strip() if len(fields) > 0 else ""
            translit = fields[1].strip() if len(fields) > 1 else ""
            gloss = fields[2].strip() if len(fields) > 2 else ""
            strong = fields[3].strip().strip("{}") if len(fields) > 3 else ""
            parse = fields[4].strip() if len(fields) > 4 else ""
            lemma = ""
            for fld in fields[5:]:
                if "=" in fld and fld.strip().startswith("{H"):
                    lemma = fld.strip().strip("{}")
                    break
            words.append({
                "ref": f"{step}.{c}.{v}", "chapter": c, "verse": v, "word_idx": int(m.group(3)),
                "hebrew": heb, "translit": translit, "gloss_en": gloss,
                "strong": strong, "parse": parse, "lemma": lemma,
            })
    words.sort(key=lambda w: (w["chapter"], w["verse"], w["word_idx"]))
    return words


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="히브리어 구약 원어 조회 (STEPBible TAHOT)")
    p.add_argument("ref", help="구절 (예: 창1:1, 시23:1-3)")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    ko2step, step2name = load_step_map()
    parsed = parse_ref(args.ref, ko2step)
    if not parsed:
        sys.exit(f"구절 형식 인식 실패 또는 신약(히브리어 없음): '{args.ref}'")
    step, ch, vs, ve = parsed
    words = load_words(step, ch, vs, ve)
    if not words:
        sys.exit(f"원어 데이터 없음: {args.ref} (구약만 지원. 데이터 설치 확인: src/data/original/hebrew/)")

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
            print(f"  {w['hebrew']:16} {w['translit']:14} {w['gloss_en']:18} [{w['strong']} {w['parse']}]  ← {w['lemma']}")


if __name__ == "__main__":
    main()
