# -*- coding: utf-8 -*-
"""Exegete — 사전 정의 조회 (Abbott-Smith / BDB, STEPBible TBESG·TBESH, CC BY 4.0).

원어 스트롱번호로 사전의 상세 정의를 붙인다. 환각 방지 도구의 일부:
정의를 기억으로 지어내지 않고 데이터(사전)에서 꺼낸다.

- 확장번호(예: H1254A, G0025) **정확 매칭**을 우선한다(동음이의어 오류 방지).
- 정확 매칭 실패 시 기본번호로 폴백하되, 후보가 여럿(동음이의어)이면
  단정하지 않고 `[확인 필요]`로 넘긴다.
- 사전에 없으면 None → 호출측이 `[확인 필요]`로 표시.

데이터: src/data/lexicon/{greek,hebrew}_lexicon.json (build_lexicon.py로 생성)
헬라어=Abbott-Smith(TBESG), 히브리어=BDB기반(TBESH). 둘 다 STEPBible CC BY 4.0.
"""
import json
import re
from pathlib import Path

LEXDIR = Path(__file__).resolve().parent / "data" / "lexicon"
_STRONG = re.compile(r"[GH]\d+[A-Za-z]?")


def _base(strong: str):
    m = re.match(r"[GH]0*(\d+)", strong or "")
    return m.group(1) if m else None


def strong_num(strong: str):
    """숫자값. 문법요소(≥9000: 전치사·관사·접속사·부호) 판별용."""
    b = _base(strong)
    return int(b) if b else None


class Lexicon:
    """언어별 사전. lang = 'greek' | 'hebrew'."""

    def __init__(self, lang: str):
        self.lang = lang
        self.path = LEXDIR / f"{lang}_lexicon.json"
        self.ok = self.path.exists()
        self.entries, self.by_base = {}, {}
        if self.ok:
            d = json.loads(self.path.read_text(encoding="utf-8"))
            self.entries = d.get("entries", {})
            self.by_base = d.get("by_base", {})

    def get(self, strong: str):
        """(entry|None, note|None). 확장번호 정확 매칭 우선 → 기본번호 폴백."""
        if not self.ok:
            return None, "사전 미설치 (python src/build_lexicon.py 실행)"
        s = (strong or "").upper()
        if s in self.entries:
            return self.entries[s], None
        cands = self.by_base.get(_base(s) or "", [])
        if len(cands) == 1:
            return self.entries[cands[0]], None
        if len(cands) > 1:
            return None, f"동음이의어 {len(cands)}개({', '.join(cands)}) — [확인 필요]"
        return None, "사전에 없음 — [확인 필요]"

    def extract(self, strong_field: str):
        """복합 스트롱 필드에서 개별 번호. 'H9003/{H7225G' → ['H9003','H7225G']."""
        return _STRONG.findall(strong_field or "")


def annotate_word(lex: "Lexicon", strong_field: str):
    """--json용: 단어의 각 구성 스트롱에 대한 사전 조회 결과 리스트."""
    out = []
    for st in lex.extract(strong_field):
        entry, note = lex.get(st)
        out.append({"query": st, "entry": entry, "note": note})
    return out


def format_word_lex(lex: "Lexicon", strong_field: str, indent: str = "      ") -> str:
    """--lex용: 단어 아래 붙일 사전 정의 텍스트.

    어간(<9000)은 상세 정의 전체, 문법요소(≥9000)는 한 줄만.
    사전에 없거나 모호한 어간은 [확인 필요]로 남긴다.
    """
    lines = []
    for st in lex.extract(strong_field):
        entry, note = lex.get(st)
        num = strong_num(st) or 0
        if entry:
            lines.append(
                f"{indent}▸ {entry['lemma']} ({entry['translit']}) "
                f"{entry['strong']} — {entry['gloss']}"
            )
            if num < 9000 and entry.get("definition"):
                for dl in entry["definition"].split("\n"):
                    dl = dl.strip()
                    if dl:
                        lines.append(f"{indent}  {dl}")
        elif num < 9000:  # 실제 단어인데 사전에 없거나 동음이의어로 모호
            lines.append(f"{indent}▸ {st} — {note}")
    return "\n".join(lines)
