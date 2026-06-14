# Exegete

**[English](README.md) | 🌐 한국어**

**환각 없는 성경 주해 도구 (Claude 전용) — 헬라어·히브리어·영어·한국어 지원.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Data: CC BY 4.0](https://img.shields.io/badge/Bible%20data-CC%20BY%204.0-green.svg)](docs/DATA_SOURCES.md)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

구절 하나를 입력하면 Exegete가 **4단계 주해**를 만들어냅니다 — 구조·문맥 → 원어·담화 분석 → 신학·역사·상호본문 → 설교 프레임워크. 대부분의 AI 성경 도구와 달리, **본문도 원어 문법도 지어내지 않습니다.** 모든 구절은 실제 데이터에서 추출하고, 헬라어·히브리어 파싱은 AI의 기억이 아니라 태그된 데이터에서 가져옵니다.

---

## Exegete가 다른 이유

🛡️ **성경 본문을 환각하지 않음** — 본문은 `lookup.py`로 추출하며 기억으로 떠올리지 않습니다. 원어 파싱은 STEPBible 태그 데이터 기반. 불확실한 추론은 `[확인 필요]`로 명시합니다.

🔬 **진짜 원어** — 헬라어·히브리어 단어마다 뜻·스트롱번호·문법파싱·원형 제공.

🌏 **다국어** — 영어·한국어 입력 모두 인식. 공개 도메인 WEB 성경 기본 포함, 원하는 번역본(개역개정 등) 추가 가능.

⛪ **신학 전통 존중, 편향에 정직** — 신학 전통을 설정할 수 있고, 논쟁적인 역사 문제(출애굽 연대 등)는 **보수·비평 양쪽 견해를 병기**하며 한쪽으로 단정하지 않습니다.

---

## 무엇을 할 수 있나 (데모)

> 아래는 도구가 하는 일의 예시입니다. **이런 명령어를 직접 외울 필요는 없어요** — Claude Code에게 한국어로 말하면 AI가 대신 실행해줍니다. (직접 쳐보고 싶은 분을 위해 명령어도 같이 적어둡니다.)

```bash
$ python src/lookup.py "요3:16"
▶ 요한복음 3:16  하나님이 세상을 이처럼 사랑하사 독생자를 주셨으니 이는 그를
                 믿는 자마다 멸망하지 않고 영생을 얻게 하려 하심이라

$ python src/greek_lookup.py "요3:16"
  ἠγάπησεν (ēgapēsen)  loved   [G0025 V-AAI-3S]  ← ἀγαπάω = 사랑하다 (부정과거)
  μονογενῆ (monogenē)  only    [G3439 A-ASM]     ← μονογενής = 유일한
  πιστεύων (pisteuōn)  believing [G4100 V-PAP-NSM] ← πιστεύω = 믿다 (현재분사)

$ python src/word_search.py G26          # ἀγάπη(사랑)가 나오는 모든 구절
총 114회 출현 — 요한일서(18), 고린도전서(14), 로마서(9) ...

$ python src/liturgical.py "부활절"       # 교회력 절기 본문
$ python src/series.py "빌립보서"          # 강해 설교 시리즈 골격
$ python src/background.py "출애굽"        # 역사적 배경 (논쟁도 표시)
```

그 다음 Claude Code에서 그냥 **"요한복음 3:16 주해해줘"**라고 하면, `CLAUDE.md` 지침에 따라 4단계 분석이 진행됩니다.

---

## 시작하기 (코딩 전혀 몰라도 됩니다 🙆)

> 이 도구는 **Claude Code**(앤트로픽의 AI 프로그램) 안에서 씁니다. 어려운 명령어를 외울 필요 없어요. **AI에게 한국어로 말만 하면** 됩니다. 아래가 막히면, 그 화면을 그대로 Claude에게 보여주고 **"이거 대신 해줘"**라고 하세요.

**1단계 — 내려받기**
Claude Code에게 이렇게 말하세요:
> "https://github.com/worlyung/exegete 이거 내 컴퓨터에 받아줘"

(직접 하고 싶으면: 터미널에 `git clone https://github.com/worlyung/exegete.git` 입력 — 인터넷에서 도구를 통째로 받아오는 명령이에요.)

**2단계 — 바로 써보기**
받고 나면, Claude Code에게 그냥 말하면 됩니다:
> "요한복음 3:16 주해해줘"
> "이번 부활절 설교 본문 추천해줘"
> "빌립보서 강해 시리즈 짜줘"

→ AI가 알아서 본문을 찾고, 원어를 분석하고, 4단계 주해를 만들어줍니다. **영어 성경(WEB)은 처음부터 들어있어서 곧바로 됩니다.**

**원어(헬라어·히브리어)까지 보려면** — Claude에게 "원어 데이터 받아줘"라고 하거나, `python setup_data.py`를 한 번 실행하면 자동으로 받아옵니다(약 100MB, 무료·CC BY).

**한국어 개역개정으로 보고 싶으면** 🇰🇷
개역개정은 대한성서공회 저작권이라 이 도구에 같이 넣을 수 없어요. 그래서 **본인이 가진 개역개정 파일을 직접 넣어야** 합니다(개인 연구·설교 준비용은 괜찮아요).
→ 가장 쉬운 방법: Claude Code에게 **"개역개정 성경 파일 있는데, 이걸로 한국어로 보게 설정해줘"**라고 하고 파일을 주세요. AI가 알아서 맞춰줍니다.
(직접 하려면: 한 줄에 한 절씩 적은 `data/bible_krv.txt` 파일을 넣고, `EXEGETE_BIBLE=data/bible_krv.txt`를 명령 앞에 붙이면 한국어로 나옵니다.)

---

## 모드

| 모드 | 명령어 / 트리거 | 기능 |
|------|----------------|------|
| **4단계 주해** | "○○ 주해해줘" | 구조 → 원어 → 신학 → 설교 |
| **단어·주제 연구** | `word_search.py G26` | 원어 단어 전체 출현·분포 |
| **교회력 절기** | `liturgical.py "부활절"` | 13개 절기 핵심 본문 |
| **강해 시리즈** | `series.py "빌립보서"` | 책을 설교 단락으로 분할 |
| **성경 배경 연구** | `background.py "출애굽"` | 인물·사건·여정 (논쟁도 표시) |
| **큐티 / 성경공부 교재 / 통독 / 병행본문** | `CLAUDE.md` 참조 | 가벼운 형식들 |

---

## 데이터와 라이선스

- **코드·프롬프트·방법론**: MIT
- **WEB 영어 성경** (기본 포함): Public Domain
- **원어** (`setup_data.py`로 받기): STEPBible TAGNT/TAHOT, **CC BY 4.0** © Tyndale House, 교파 중립
- **저작권 번역본** (개역개정·NA28·BHS·Louw-Nida): **절대 포함 안 함** — 본인이 준비. [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) 참조

## 한국 교회·신학생을 위해 🇰🇷

Exegete는 한국어를 1급으로 지원합니다 — `요3:16` 입력, 한국어 책 이름, 개역개정(직접 준비) 완전 통합. 방법론과 프롬프트가 한·영 양쪽으로 작성돼 있어, 한국 목회자·신학생이 정확한 원어·주해를 손쉽게 할 수 있습니다.

## 감사의 글

4단계 구조는 [bible_analyze](https://github.com/mitmirsein/bible_analyze)의 방법론에서 영감을 받아 재작성했습니다. 표준 주해 방법론(페리코페·담화분석·정경적 궤적·강해설교)은 성서학계의 공유 자산입니다. 원어 데이터는 [STEPBible](https://github.com/STEPBible/STEPBible-Data) / Tyndale House.

## 라이선스

MIT (코드) — [LICENSE](LICENSE)와 [NOTICE](NOTICE) 참조.
