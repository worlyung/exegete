# -*- coding: utf-8 -*-
"""Exegete — Bible verse lookup (multilingual: Korean + English).

분석 AI가 본문을 기억이 아니라 데이터에서 정확히 추출하게 한다(환각 1차 방어선).
입력은 한국어("요3:16", "요한복음 3:16")와 영어("John 3:16", "Jhn 3:16") 모두 인식.
본문 파일은 한국어(개역개정 등)·영어(WEB 등) 자동 감지.

Usage:
    py lookup.py "요3:16"            py lookup.py "John 3:16"
    py lookup.py "창1:1-5"           py lookup.py "Gen 1:1-5"
    py lookup.py "요3:16" --context 3
    py lookup.py "창1:1" --pericope
    py lookup.py "요3:16" --json

본문 데이터: data/<번역본>.txt (UTF-8, 한 줄=한 절, "약어장:절 [<소제목>] 본문").
  기본: bible_krv.txt(있으면) → 없으면 web.txt(World English Bible, PD).
  EXEGETE_BIBLE 환경변수로 본문 파일 지정 가능.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
ABBR = BASE / "data" / "book_abbrev.json"


def default_bible():
    """본문 자동 선택: 사용자 개역개정 > 내장 개역한글 > 영어 WEB.

    bible_krv.txt(사용자가 직접 넣은 개역개정)가 있으면 최우선,
    없으면 기본 내장된 bible_korean.txt(개역한글, PD), 그것도 없으면 web.txt.
    """
    data = BASE / "data"
    for name in ("bible_krv.txt", "bible_korean.txt", "web.txt"):
        f = data / name
        if f.exists():
            return f
    return data / "web.txt"


DATA = Path(os.environ.get("EXEGETE_BIBLE", default_bible()))


def load_books():
    d = json.loads(ABBR.read_text(encoding="utf-8"))
    alias2step, step2ko, step2en, step2test = {}, {}, {}, {}
    for b in d["books"]:
        s = b["step"]
        step2ko[s] = b["name"]
        step2en[s] = b.get("en", s)
        step2test[s] = b["testament"]
        for a in (b["abbr"], b["name"], s, b.get("en", "")):
            if a:
                alias2step[a.lower().replace(" ", "")] = s
    return alias2step, step2ko, step2en, step2test


def to_step(token, alias2step):
    return alias2step.get(token.strip().lower().replace(" ", ""))


def parse_ref(ref, alias2step):
    ref = ref.strip()
    m = re.match(r"^(.+?)\s*(\d+):(\d+)(?:-(\d+))?$", ref)
    if not m:
        return None
    step = to_step(m.group(1), alias2step)
    if not step:
        return None
    ch, vs, ve = int(m.group(2)), int(m.group(3)), m.group(4)
    return step, ch, vs, int(ve) if ve else vs


def load_verses(alias2step, data=None):
    """본문 파일 → {(step,ch,v): (heading,text)} + 순서. 책 약어를 step으로 정규화.

    data=None이면 기본 본문(DATA), 파일 경로를 주면 그 본문을 읽는다(번역 비교용).
    """
    verses, order = {}, []
    src = data if data is not None else DATA
    for line in src.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^(.+?)(\d+):(\d+)\s+(.*)$", line)
        if not m:
            continue
        step = to_step(m.group(1), alias2step)
        if not step:
            continue
        ch, v, body = int(m.group(2)), int(m.group(3)), m.group(4)
        heading = None
        hm = re.match(r"^<([^>]+)>\s*(.*)$", body)
        if hm:
            heading, body = hm.group(1), hm.group(2)
        key = (step, ch, v)
        verses[key] = (heading, body)
        order.append(key)
    return verses, order


def is_english_bible():
    n = DATA.name.lower()
    return any(t in n for t in ("web", "kjv", "asv", "esv", "niv", "_en"))


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
        sys.stderr.reconfigure(encoding="utf-8")

    p = argparse.ArgumentParser(description="Bible verse lookup (KO/EN)")
    p.add_argument("ref", help="구절/verse (요3:16, John 3:16, 창1:1-5)")
    p.add_argument("--context", type=int, default=0, help="앞뒤 N절 / surrounding verses")
    p.add_argument("--pericope", action="store_true", help="소제목 단락 전체 / whole pericope")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    alias2step, step2ko, step2en, step2test = load_books()
    parsed = parse_ref(args.ref, alias2step)
    if not parsed:
        sys.exit(f"Cannot parse reference: '{args.ref}' (e.g. 요3:16 / John 3:16 / 창1:1-5)")
    step, ch, vs, ve = parsed
    name = step2en[step] if is_english_bible() else step2ko[step]

    verses, order = load_verses(alias2step)
    idxs = [i for i, k in enumerate(order) if k[0] == step and k[1] == ch and vs <= k[2] <= ve]
    if not idxs:
        sys.exit(f"Verse not found: {name} {ch}:{vs} (check data file: {DATA.name})")
    lo, hi = min(idxs), max(idxs)

    if args.pericope:
        has_start_heading = any(
            key[0] == step
            and key[1] == ch
            and key[2] <= vs
            and verses[key][0] is not None
            for key in order
        )
        if has_start_heading:
            s = lo
            while s > 0 and order[s][0] == step:
                if verses[order[s]][0]:
                    break
                s -= 1
            e = hi
            while e + 1 < len(order) and order[e + 1][0] == step and not verses[order[e + 1]][0]:
                e += 1
            lo, hi = s, e
        else:
            chapter_idxs = [
                i for i, key in enumerate(order) if key[0] == step and key[1] == ch
            ]
            lo, hi = min(chapter_idxs), max(chapter_idxs)
            print(
                f"⚠ 요청 절 앞 같은 장의 소제목 경계를 찾지 못해 {name} {ch}장 전체를 문맥 폴백으로 표시합니다. "
                "정확한 단락 경계는 [확인 필요].",
                file=sys.stderr,
            )
    elif args.context:
        lo = max(0, lo - args.context)
        hi = min(len(order) - 1, hi + args.context)
        while lo < hi and order[lo][0] != step:
            lo += 1
        while hi > lo and order[hi][0] != step:
            hi -= 1

    block = []
    for i in range(lo, hi + 1):
        k = order[i]
        if k[0] != step:
            continue
        heading, text = verses[k]
        block.append({
            "ref": f"{step}{k[1]}:{k[2]}", "book": name, "chapter": k[1], "verse": k[2],
            "heading": heading, "text": text, "target": (k[1] == ch and vs <= k[2] <= ve),
        })

    if args.json:
        print(json.dumps({
            "query": args.ref, "book": name, "step": step, "testament": step2test[step],
            "original_language": "Hebrew" if step2test[step] == "OT" else "Greek",
            "verses": block,
        }, ensure_ascii=False, indent=2))
    else:
        for b in block:
            mark = "▶ " if b["target"] else "  "
            h = f"<{b['heading']}> " if b["heading"] else ""
            print(f"{mark}{b['book']} {b['chapter']}:{b['verse']} {h}{b['text']}")


if __name__ == "__main__":
    main()
