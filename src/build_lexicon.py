#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exegete — 사전 데이터 생성 (Abbott-Smith / BDB via STEPBible, CC BY 4.0).

원어 단어에 '상세 사전 정의'를 붙이기 위한 데이터를 만든다. 환각 방지의 일부:
정의를 기억으로 지어내지 않고, 실제 사전 데이터에서 꺼내 쓰기 위함이다.

STEPBible에서 아래 둘을 받아 확장 스트롱번호(예: H1254A, G0025)를 키로 하는
JSON으로 변환한다. 확장번호는 우리 원어 데이터(TAGNT/TAHOT)와 정확히 맞아
동음이의어(예: בָּרָא '창조하다' H1254A vs '살찌다' H1254B) 오류를 막는다.

  - 헬라어: TBESG (Abbott-Smith 기반)
  - 히브리어: TBESH (BDB 기반)

사용:
    python src/build_lexicon.py           # 다운로드 + 변환
    python src/build_lexicon.py --rebuild # 캐시 무시하고 원본 다시 받기

산출: src/data/lexicon/{greek,hebrew}_lexicon.json
데이터 라이선스: CC BY 4.0 © Tyndale House (github.com/STEPBible/STEPBible-Data)
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
LEXDIR = BASE / "data" / "lexicon"
RAW = "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/master/Lexicons/"

SOURCES = {
    "greek": "TBESG - Translators Brief lexicon of Extended Strongs for Greek - STEPBible.org CC BY.txt",
    "hebrew": "TBESH - Translators Brief lexicon of Extended Strongs for Hebrew - STEPBible.org CC BY.txt",
}


def download(fname: str, dest: Path):
    url = RAW + urllib.parse.quote(fname)
    req = urllib.request.Request(url, headers={"User-Agent": "Exegete-setup"})
    dest.write_bytes(urllib.request.urlopen(req, timeout=180).read())


def clean_html(s: str) -> str:
    """STEPBible 정의의 태그를 읽기 좋은 텍스트로 정리."""
    s = re.sub(r"<ref[^>]*>(.*?)</ref>", r"\1", s, flags=re.S)   # 성경참조: 안 텍스트만
    s = re.sub(r"<BR\s*/?>", "\n", s, flags=re.I)                 # 줄바꿈
    s = re.sub(r"</?(b|i|em|re|sup|sub|foreign|gr|heb|note)[^>]*>", "", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)                                 # 남은 태그
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n[ \t]*", "\n", s)
    s = re.sub(r"\n{2,}", "\n", s)
    return s.strip()


def base_num(strong: str):
    m = re.match(r"[GH]0*(\d+)", strong or "")
    return m.group(1) if m else None


def build(path: Path) -> dict:
    """TBESG/TBESH 텍스트 → {entries, by_base}. 키=확장 스트롱번호(두번째 필드)."""
    entries, by_base = {}, {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line[:1] not in ("H", "G"):
            continue
        f = line.split("\t")
        if len(f) < 8:
            continue
        m = re.match(r"\s*([GH]\d+[A-Za-z]?)", f[1])   # "H1254A =" → H1254A
        if not m:
            continue
        ext = m.group(1).upper()                        # 원어 데이터(대문자)와 통일
        base = base_num(ext)
        if not base:
            continue
        entries[ext] = {
            "strong": ext, "lemma": f[3].strip(), "translit": f[4].strip(),
            "pos": f[5].strip(), "gloss": f[6].strip(),
            "definition": clean_html("\t".join(f[7:])),
        }
        by_base.setdefault(base, [])
        if ext not in by_base[base]:
            by_base[base].append(ext)
    return {"entries": entries, "by_base": by_base}


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Exegete 사전 데이터 생성 (STEPBible, CC BY 4.0)")
    ap.add_argument("--rebuild", action="store_true", help="원본 캐시를 무시하고 다시 받기")
    args = ap.parse_args()

    LEXDIR.mkdir(parents=True, exist_ok=True)
    print("Exegete — 사전 데이터 생성 (Abbott-Smith / BDB, STEPBible CC BY 4.0)\n")
    ok = True
    for lang, fname in SOURCES.items():
        raw = LEXDIR / f"_{lang}_src.txt"
        if args.rebuild or not (raw.exists() and raw.stat().st_size > 1000):
            print(f"  [get ] {lang} 원본 내려받는 중 ...", flush=True)
            try:
                download(fname, raw)
            except Exception as e:
                ok = False
                print(f"        실패: {e}")
                print("        수동 다운로드: https://github.com/STEPBible/STEPBible-Data/tree/master/Lexicons")
                continue
        data = build(raw)
        out = LEXDIR / f"{lang}_lexicon.json"
        out.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        print(f"  [ok  ] {lang}: entries={len(data['entries']):,}  base={len(data['by_base']):,}  -> {out.name}")

    lic = LEXDIR / "LICENSE_STEPBible.txt"
    if not lic.exists():
        lic.write_text(
            "TBESG (Abbott-Smith) / TBESH (BDB) — STEPBible.org © Tyndale House, CC BY 4.0\n"
            "https://github.com/STEPBible/STEPBible-Data\n", encoding="utf-8")

    if ok:
        print("\nDone. 이제 원어 조회에 --lex 를 붙이면 사전 정의가 나옵니다:")
        print("  python src/greek_lookup.py \"요3:16\" --lex")
        print("  python src/hebrew_lookup.py \"창1:1\" --lex")


if __name__ == "__main__":
    main()
