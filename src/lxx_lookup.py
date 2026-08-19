# -*- coding: utf-8 -*-
"""Exegete — 70인역(LXX) 구약 헬라어 본문 조회 (Swete 1887-94, Public Domain).

용도: 신약의 구약 인용 연구, 구약 본문의 헬라어 대조 (분석 3단계 상호본문).
본문을 기억이 아니라 데이터에서 추출한다.

사용법:
    py lxx_lookup.py "시23:1"          # 개역 기준 참조 → LXX 번호로 자동 변환
    py lxx_lookup.py "렘31:31-34"      # 예레미야는 장 매핑 후 경고와 함께 표시
    py lxx_lookup.py --raw "Psa.151:1" # LXX 자체 참조로 직접 조회(외경 포함)
    py lxx_lookup.py "창1:1" --json

주의(절 번호 체계):
  - LXX 시편은 개역과 편 번호가 다르다(대부분 -1). 자동 변환하며 두 번호를 모두 표시.
  - 시편 표제("다윗의 시")가 LXX에선 절 번호(1~2절)를 차지해 절이 0~2절 뒤로
    밀릴 수 있다 → 시편은 요청 절 뒤 2절을 함께 표시한다.
  - 예레미야는 26장 이후 장 배열이 다르다. 표준 장 매핑으로 변환하되 경고를 붙인다.
  - 다니엘은 데오도티온(Dat)이 기본(교회 표준·MT 순서). 옛헬라어판은 --raw "Dan...".

데이터: src/data/lxx/lxx_swete.txt — 최초 1회 python src/build_lxx.py 로 생성.
"""
import argparse
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
LXX_FILE = BASE / "data" / "lxx" / "lxx_swete.txt"
ABBR = BASE / "data" / "book_abbrev.json"

# 우리 step 코드와 Swete 파일 코드가 다른 책
STEP2SWETE = {"Ezk": "Eze", "Jol": "Joe", "Nam": "Nah", "Sng": "Sol", "Dan": "Dat"}

# 예레미야 MT장 → LXX장 (표준 대응표. 49장은 여러 곳에 흩어져 자동 변환 불가)
JER_MT2LXX = {**{c: c for c in range(1, 26)},
              **{c: c + 7 for c in range(26, 46)},   # 렘31:31(새 언약) → LXX 38:31
              46: 26, 47: 29, 48: 31, 50: 27, 51: 28, 52: 52}


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
    ch, vs, ve = int(m.group(2)), int(m.group(3)), m.group(4)
    return book, ch, vs, int(ve) if ve else vs


def psalm_mt_to_lxx(ch):
    """개역(MT) 시편 편 번호 → (LXX 편 번호 목록, 통째 표시 여부, 메모)."""
    if ch <= 8 or 148 <= ch <= 150:
        return [ch], False, None
    if ch in (9, 10):
        return [9], True, "개역 9·10편은 LXX에서 9편 하나로 합쳐져 있어 편 전체를 표시합니다."
    if 11 <= ch <= 113:
        return [ch - 1], False, None
    if ch in (114, 115):
        return [113], True, "개역 114·115편은 LXX 113편 하나로 합쳐져 있어 편 전체를 표시합니다."
    if ch == 116:
        return [114, 115], True, "개역 116편은 LXX 114·115편으로 나뉘어 있어 두 편 전체를 표시합니다."
    if 117 <= ch <= 146:
        return [ch - 1], False, None
    if ch == 147:
        return [146, 147], True, "개역 147편은 LXX 146·147편으로 나뉘어 있어 두 편 전체를 표시합니다."
    return [], False, f"개역 시편 {ch}편에 대응하는 LXX 편 없음"


def load_verses():
    if not LXX_FILE.exists():
        sys.exit("LXX 데이터 없음. 먼저 실행: python src/build_lxx.py")
    verses = {}
    for line in LXX_FILE.read_text(encoding="utf-8").splitlines():
        ref, text = line.split("\t", 1)
        m = re.match(r"^(\w+)\.(\d+):(\d+)$", ref)
        if m:
            verses[(m.group(1), int(m.group(2)), int(m.group(3)))] = text
    return verses


def collect(verses, code, targets):
    """targets: (장, 시작절 or None, 끝절 or None) 목록. None이면 장 전체."""
    out = []
    for ch, vs, ve in targets:
        vv = sorted(v for (b, c, v) in verses if b == code and c == ch)
        for v in vv:
            if vs is not None and not (vs <= v <= ve):
                continue
            out.append({"lxx_ref": f"{code}.{ch}:{v}", "chapter": ch, "verse": v,
                        "greek": verses[(code, ch, v)]})
    return out


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="70인역(LXX) 조회 (Swete, PD)")
    p.add_argument("ref", help="구절 (예: 시23:1, 렘31:31-34) 또는 --raw와 LXX 참조")
    p.add_argument("--raw", action="store_true", help="LXX 자체 참조로 직접 조회 (예: Psa.151:1, Dan.1:1)")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    verses = load_verses()
    notes = []

    if args.raw:
        m = re.match(r"^(\w+)\.(\d+):(\d+)(?:-(\d+))?$", args.ref.replace(" ", ""))
        if not m:
            sys.exit(f"--raw 참조 형식 인식 실패: '{args.ref}' (예: Psa.151:1)")
        code, ch = m.group(1), int(m.group(2))
        vs, ve = int(m.group(3)), int(m.group(4) or m.group(3))
        name = code
        rows = collect(verses, code, [(ch, vs, ve)])
        notes.append("LXX 자체 참조 기준입니다(개역 번호 아님).")
    else:
        parsed = parse_ref(args.ref, load_step_map())
        if not parsed:
            sys.exit(f"구절 형식 인식 실패: '{args.ref}' (LXX 자체 참조는 --raw 사용)")
        book, ch, vs, ve = parsed
        if book["testament"] != "OT":
            sys.exit(f"{book['name']}은(는) 신약입니다. 70인역은 구약 헬라어 번역입니다. (신약 원어: greek_lookup.py)")
        step = book["step"]
        code = STEP2SWETE.get(step, step)
        name = book["name"]

        if step == "Psa":
            lxx_chs, whole, note = psalm_mt_to_lxx(ch)
            if note:
                notes.append(note)
            if not lxx_chs:
                sys.exit(note)
            if whole:
                targets = [(c, None, None) for c in lxx_chs]
            else:
                # 표제가 절 번호를 차지해 0~2절 뒤로 밀릴 수 있음 → 뒤 2절 포함
                targets = [(lxx_chs[0], vs, ve + 2)]
                notes.append("LXX 시편은 표제가 절 번호(1~2절)를 차지해 개역보다 0~2절 뒤로 밀릴 수 "
                             "있습니다. 요청 절 뒤 2절을 함께 표시했으니 내용으로 대조하십시오.")
            notes.append(f"편 번호 변환: 개역 시{ch}편 → LXX {'·'.join(map(str, lxx_chs))}편")
        elif step == "Jer":
            if ch == 49:
                sys.exit("개역 렘49장은 LXX에서 여러 장(25·30·31장 등)에 흩어져 자동 변환이 안전하지 "
                         "않습니다. --raw로 LXX 참조를 직접 지정해 조회하십시오.")
            lxx_ch = JER_MT2LXX.get(ch)
            if lxx_ch is None:
                sys.exit(f"렘{ch}장의 LXX 대응 장 없음")
            targets = [(lxx_ch, vs, ve)]
            notes.append(f"장 번호 변환: 개역 렘{ch}장 → LXX {lxx_ch}장. 예레미야는 MT와 LXX의 "
                         "배열·분량 차이가 커서 절 단위 대응이 어긋날 수 있습니다. 내용으로 대조하십시오.")
        else:
            targets = [(ch, vs, ve)]
            if step == "Dan":
                notes.append("다니엘은 데오도티온 판(Dat, 교회 표준)입니다. "
                             "옛헬라어판(OG)은 --raw \"Dan.장:절\"로 조회.")

        rows = collect(verses, code, targets)

    if not rows:
        sys.exit(f"본문 없음: {args.ref} (LXX에 해당 절이 없거나 번호 체계가 다를 수 있음. "
                 f"--raw로 직접 조회하거나 범위를 넓혀 보십시오.)")

    notes.append("본문: Swete 판(1887-94, PD). 표준 비평본(Rahlfs·괴팅겐)과 세부 독법이 다를 수 "
                 "있으니 본문비평 논증에는 비평본 대조를 권장합니다.")

    if args.json:
        print(json.dumps({"query": args.ref, "book": name, "verses": rows, "notes": notes},
                         ensure_ascii=False, indent=2))
    else:
        print(f"=== 70인역(LXX) — {name} {args.ref if args.raw else ''} ===".rstrip())
        cur = None
        for r in rows:
            if r["chapter"] != cur:
                cur = r["chapter"]
                print(f"\n── LXX {cur}장 ──")
            print(f"  [{r['lxx_ref']}] {r['greek']}")
        print()
        for n in notes:
            print(f"⚠ {n}")


if __name__ == "__main__":
    main()
