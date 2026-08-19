#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exegete — 70인역(LXX) 본문 데이터 생성 (Swete 1887-94, Public Domain).

구약 헬라어(70인역) 본문을 기억이 아니라 데이터에서 조회하기 위한 준비 단계.
eliranwong/LXX-Swete-1930 저장소의 단어별 CSV 두 개를 받아
절 단위 TSV(참조<TAB>본문)로 합친다.

원문: H. B. Swete, The Old Testament in Greek (1887-1894) — 저작권 만료(PD).
(표준 비평본인 Rahlfs 1935는 저작권이 살아 있어 쓰지 않는다.)

사용:
    python src/build_lxx.py           # 다운로드 + 변환 + 자가검증
    python src/build_lxx.py --rebuild # 캐시 무시하고 원본 다시 받기

산출: src/data/lxx/lxx_swete.txt  (형식: "Psa.22:1\t본문")
"""
import argparse
import sys
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
LXXDIR = BASE / "data" / "lxx"
RAW = "https://raw.githubusercontent.com/eliranwong/LXX-Swete-1930/master/"

SOURCES = {
    "_words_src.csv": "01-Swete_word_with_punctuations.csv",
    "_vers_src.csv": "00-Swete_versification.csv",
}


def download(fname: str, dest: Path):
    req = urllib.request.Request(RAW + fname, headers={"User-Agent": "Exegete-setup"})
    dest.write_bytes(urllib.request.urlopen(req, timeout=180).read())


def build() -> int:
    words = {}
    for line in (LXXDIR / "_words_src.csv").read_text(encoding="utf-8").splitlines():
        idx, word = line.split("\t", 1)
        words[int(idx)] = word
    marks = []
    for line in (LXXDIR / "_vers_src.csv").read_text(encoding="utf-8").splitlines():
        idx, ref = line.split("\t", 1)
        marks.append((int(idx), ref.strip()))
    marks.sort()
    last = max(words) + 1
    out = []
    for k, (start, ref) in enumerate(marks):
        end = marks[k + 1][0] if k + 1 < len(marks) else last
        text = " ".join(words[j] for j in range(start, end) if j in words)
        out.append(f"{ref}\t{text}")
    (LXXDIR / "lxx_swete.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
    return len(out)


def selfcheck():
    """잘 알려진 절 두 개로 조인 결과 검증 (환각 방지 도구의 최소 안전판)."""
    import unicodedata
    nfc = lambda s: unicodedata.normalize("NFC", s)
    text = {}
    for line in (LXXDIR / "lxx_swete.txt").read_text(encoding="utf-8").splitlines():
        ref, t = line.split("\t", 1)
        text[ref] = nfc(t)
    assert nfc("ποιμαίνει") in text["Psa.22:1"], "LXX 시22:1(=개역 시23:1)에 '목자' 없음 — 조인 오류"
    assert nfc("παρθένος") in text["Isa.7:14"], "사7:14에 '파르테노스' 없음 — 조인 오류"
    assert "Dat.1:1" in text, "다니엘 데오도티온(Dat) 없음"


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Exegete 70인역(LXX) 데이터 생성 (Swete, PD)")
    ap.add_argument("--rebuild", action="store_true", help="원본 캐시를 무시하고 다시 받기")
    args = ap.parse_args()

    LXXDIR.mkdir(parents=True, exist_ok=True)
    print("Exegete — 70인역(LXX) 본문 데이터 생성 (Swete 1887-94, Public Domain)\n")
    for local, remote in SOURCES.items():
        dest = LXXDIR / local
        if args.rebuild or not (dest.exists() and dest.stat().st_size > 10000):
            print(f"  [get ] {remote} 내려받는 중 ...", flush=True)
            try:
                download(remote, dest)
            except Exception as e:
                sys.exit(f"        실패: {e}\n        수동 다운로드: https://github.com/eliranwong/LXX-Swete-1930")
    n = build()
    selfcheck()
    print(f"  [ok  ] 절 {n:,}개 -> lxx_swete.txt (자가검증 통과)")

    lic = LXXDIR / "LICENSE_LXX.txt"
    if not lic.exists():
        lic.write_text(
            "LXX text: H. B. Swete, The Old Testament in Greek (1887-1894) — Public Domain.\n"
            "Digital source: github.com/eliranwong/LXX-Swete-1930\n", encoding="utf-8")

    print("\nDone. 이제 70인역을 조회할 수 있습니다:")
    print("  python src/lxx_lookup.py \"시23:1\"")


if __name__ == "__main__":
    main()
