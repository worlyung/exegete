#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exegete — OpenGNT 데이터 생성 (Louw-Nida 의미영역 + Levinsohn 담화 표지).

신약 2단계(문헌학·담화) 분석의 두 구멍을 데이터로 채운다:
  - Louw-Nida 의미영역 번호(단어별) — 지금까지 기억 추정 + [확인 필요]였던 것
  - Levinsohn 담화 표지(전방 강조·출발점 등) — 지금까지 순수 해석이었던 것

소스: github.com/eliranwong/OpenGNT (CC BY-SA 4.0 — 카피레프트라 이 폴더에 분리 보관,
git에는 넣지 않는다). 본문은 Nestle 1904 기반 OGNT.

사용:
    python src/build_opengnt.py           # 다운로드 + 변환 + 자가검증
    python src/build_opengnt.py --rebuild # 캐시 무시하고 원본 다시 받기

산출: src/data/opengnt/opengnt.txt (TSV: 참조·단어순번·헬라어·원형·파싱·스트롱·LN·구약인용·담화주석)
      src/data/opengnt/morph_korean.tsv (파싱코드 → 한국어 풀이)
"""
import argparse
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
OGNTDIR = BASE / "data" / "opengnt"
RAW = "https://github.com/eliranwong/OpenGNT/raw/master/"

ZIPS = {
    "_base.zip": ("OpenGNT_BASE_TEXT.zip", "OpenGNT_version3_3.csv"),
    "_lev.zip": ("OpenGNT_DictLGNTDF.csv.zip", "OpenGNT_DictLGNTDF.csv"),
}
KO_CSV = "OpenGNT_morphology_Korean.csv"

# OpenGNT 책 번호(40~66) → 우리 step 코드 (book_abbrev.json과 동일)
BOOKS = {40: "Mat", 41: "Mrk", 42: "Luk", 43: "Jhn", 44: "Act", 45: "Rom",
         46: "1Co", 47: "2Co", 48: "Gal", 49: "Eph", 50: "Php", 51: "Col",
         52: "1Th", 53: "2Th", 54: "1Ti", 55: "2Ti", 56: "Tit", 57: "Phm",
         58: "Heb", 59: "Jas", 60: "1Pe", 61: "2Pe", 62: "1Jo", 63: "2Jo",
         64: "3Jo", 65: "Jud", 66: "Rev"}


def download(fname: str, dest: Path):
    url = RAW + fname if fname.endswith(".zip") else \
        f"https://raw.githubusercontent.com/eliranwong/OpenGNT/master/{fname}"
    req = urllib.request.Request(url, headers={"User-Agent": "Exegete-setup"})
    dest.write_bytes(urllib.request.urlopen(req, timeout=300).read())


def fields(bracketed: str):
    """〔a｜b｜c〕 → [a, b, c]"""
    return bracketed.strip().lstrip("〔").rstrip("〕").split("｜")


def strip_html(s: str) -> str:
    s = re.sub(r"</p>\s*<p>", " / ", s)
    s = re.sub(r"<hr\s*/?>", " ∥ ", s)
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", s).strip()


def load_discourse() -> dict:
    """DictLGNTDF: OGNTsort → 담화 주석(태그 제거 텍스트)."""
    notes = {}
    with zipfile.ZipFile(OGNTDIR / "_lev.zip") as z:
        data = z.read(ZIPS["_lev.zip"][1]).decode("utf-8")
    for line in data.splitlines()[1:]:
        f = line.split("\t")
        if len(f) < 4:
            continue
        key = f[2].strip()          # OGNTsort
        note = strip_html(f[3])
        if key and note:
            notes[key] = (notes.get(key, "") + " ∥ " + note).strip(" ∥ ")
    return notes


def build() -> int:
    notes = load_discourse()
    with zipfile.ZipFile(OGNTDIR / "_base.zip") as z:
        data = z.read(ZIPS["_base.zip"][1]).decode("utf-8")
    out, n = [], 0
    word_idx, cur_verse = 0, None
    for line in data.splitlines()[1:]:
        cols = line.split("\t")
        if len(cols) < 13:
            continue
        ognt_sort = cols[0].strip()
        ot_quote = cols[4].strip()
        b, c, v = fields(cols[6])
        book = BOOKS.get(int(b))
        if not book:
            continue
        ref = f"{book}.{int(c)}:{int(v)}"
        if ref != cur_verse:
            cur_verse, word_idx = ref, 0
        word_idx += 1
        w = fields(cols[7])          # OGNTk|OGNTu|OGNTa|lexeme|rmac|sn
        entries = fields(cols[8])    # BDAG|EDNT|Mounce|GK|LN
        greek, lexeme, rmac, strong = w[2], w[3], w[4], w[5]
        ln = entries[4].replace("LN-", "") if len(entries) > 4 else ""
        note = notes.get(ognt_sort, "")
        out.append("\t".join([ref, str(word_idx), greek, lexeme, rmac, strong,
                              ln, "" if ot_quote == "-" else ot_quote, note]))
        n += 1
    (OGNTDIR / "opengnt.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
    return n


def build_morph_ko():
    src = OGNTDIR / "_morph_ko.csv"
    rows = []
    import csv
    with open(src, encoding="utf-8-sig", newline="") as f:
        for r in csv.reader(f):
            if len(r) >= 2:
                rows.append(f"{r[0].strip()}\t{r[1].strip()}")
    (OGNTDIR / "morph_korean.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    return len(rows)


def selfcheck():
    """요3:16으로 조인 검증: 단어·LN·담화 주석이 실제로 붙었는가."""
    text = (OGNTDIR / "opengnt.txt").read_text(encoding="utf-8")
    rows = [l for l in text.splitlines() if l.startswith("Jhn.3:16\t")]
    assert rows, "요3:16 없음 — 변환 오류"
    joined = "\n".join(rows)
    assert "ἠγάπησεν" in joined and "G25" in joined, "요3:16에 ἠγάπησεν(G25) 없음"
    assert re.search(r"\t\d+\.\d+", joined), "요3:16에 LN 번호 없음"
    assert any(r.split("\t")[8] for r in rows), "요3:16에 담화 주석이 하나도 없음"


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Exegete OpenGNT 데이터 생성 (CC BY-SA 4.0)")
    ap.add_argument("--rebuild", action="store_true")
    args = ap.parse_args()

    OGNTDIR.mkdir(parents=True, exist_ok=True)
    print("Exegete — OpenGNT 데이터 생성 (Louw-Nida·Levinsohn 담화, CC BY-SA 4.0)\n")
    targets = dict(ZIPS)
    for local, (remote, _) in targets.items():
        dest = OGNTDIR / local
        if args.rebuild or not (dest.exists() and dest.stat().st_size > 10000):
            print(f"  [get ] {remote} ...", flush=True)
            try:
                download(remote, dest)
            except Exception as e:
                sys.exit(f"        실패: {e}\n        수동: https://github.com/eliranwong/OpenGNT")
    ko = OGNTDIR / "_morph_ko.csv"
    if args.rebuild or not (ko.exists() and ko.stat().st_size > 1000):
        print(f"  [get ] {KO_CSV} ...", flush=True)
        download(KO_CSV, ko)

    n = build()
    m = build_morph_ko()
    selfcheck()
    print(f"  [ok  ] 단어 {n:,}개 -> opengnt.txt / 파싱코드 한국어 풀이 {m:,}개 (자가검증 통과)")

    lic = OGNTDIR / "LICENSE_OpenGNT.txt"
    if not lic.exists():
        lic.write_text(
            "OpenGNT — github.com/eliranwong/OpenGNT\n"
            "License: CC BY-SA 4.0 (copyleft). This directory holds derived data only;\n"
            "it is NOT distributed with the MIT-licensed Exegete repository.\n"
            "Base text: OGNT (Nestle 1904 base). Discourse: Levinsohn GNTDF.\n", encoding="utf-8")

    print("\nDone. 이제 신약 단어의 LN 의미영역·담화 표지를 조회할 수 있습니다:")
    print("  python src/opengnt_lookup.py \"요3:16\"")


if __name__ == "__main__":
    main()
