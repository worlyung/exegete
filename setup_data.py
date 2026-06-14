#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exegete — download original-language data (STEPBible TAGNT/TAHOT, CC BY 4.0).

원어(헬라어·히브리어) 형태소 데이터는 용량이 커서 저장소에 포함하지 않는다.
이 스크립트를 한 번 실행하면 STEPBible에서 자동으로 받아 설치한다.

    python setup_data.py

데이터 라이선스: CC BY 4.0 © Tyndale House (https://github.com/STEPBible/STEPBible-Data)
"""
import sys
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
RAW = "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/master/Translators Amalgamated OT+NT/"

FILES = {
    "src/data/original/greek/tagnt_mat-jhn.txt":
        "TAGNT Mat-Jhn - Translators Amalgamated Greek NT - STEPBible.org CC-BY.txt",
    "src/data/original/greek/tagnt_act-rev.txt":
        "TAGNT Act-Rev - Translators Amalgamated Greek NT - STEPBible.org CC-BY.txt",
    "src/data/original/hebrew/tahot_1.txt":
        "TAHOT Gen-Deu - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt",
    "src/data/original/hebrew/tahot_2.txt":
        "TAHOT Jos-Est - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt",
    "src/data/original/hebrew/tahot_3.txt":
        "TAHOT Job-Sng - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt",
    "src/data/original/hebrew/tahot_4.txt":
        "TAHOT Isa-Mal - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt",
}


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "Exegete-setup"})
    data = urllib.request.urlopen(req, timeout=180).read()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    print("Exegete — downloading original-language data (STEPBible, CC BY 4.0)\n")
    for rel, fname in FILES.items():
        dest = BASE / rel
        if dest.exists() and dest.stat().st_size > 1000:
            print(f"  [skip] {rel} (already present)")
            continue
        print(f"  [get ] {rel} ...", flush=True)
        try:
            download(RAW + urllib.parse.quote(fname), dest)
            print(f"        -> {dest.stat().st_size:,} bytes")
        except Exception as e:
            print(f"        FAILED: {e}")
            print("        수동 다운로드: https://github.com/STEPBible/STEPBible-Data")
    # 라이선스 파일
    lic = BASE / "src/data/original/LICENSE_STEPBible.txt"
    if not lic.exists():
        lic.parent.mkdir(parents=True, exist_ok=True)
        lic.write_text(
            "STEPBible-Data (TAGNT/TAHOT) © Tyndale House — CC BY 4.0\n"
            "https://github.com/STEPBible/STEPBible-Data\n", encoding="utf-8")
    print("\nDone. 원어 분석 도구(greek_lookup.py / hebrew_lookup.py) 사용 가능.")


if __name__ == "__main__":
    main()
