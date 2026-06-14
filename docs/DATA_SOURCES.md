# 본문·원어·사전 데이터 소스 가이드

> Exegete는 **코드와 방법론만** MIT로 배포한다. 성경 본문·원어·사전 데이터는 각자의 저작권/라이선스를 따르며, 저장소에 포함되지 않는다.
> 사용자는 아래 표를 참고해 **합법적으로 사용 가능한 자료**를 `src/data/`에 직접 넣는다.

## ✅ 저장소에 포함/번들 가능 (Public Domain 또는 오픈 라이선스)

| 자료 | 종류 | 라이선스 | 출처 |
|------|------|----------|------|
| **WEB** (World English Bible) | 영어 번역 | Public Domain | github.com/scrollmapper/bible_databases |
| **KJV** (King James, 1769) | 영어 번역 | Public Domain (대부분 국가) | github.com/scrollmapper/bible_databases |
| **ASV** (American Standard, 1901) | 영어 번역 | Public Domain | github.com/scrollmapper/bible_databases |
| **Westcott-Hort** (1881) | 헬라어 신약 | Public Domain | github.com/morphgnt/westcott-hort |
| **Tischendorf** (8th ed.) | 헬라어 신약 | Public Domain | 여러 repo (LICENSE 확인) |
| **MorphGNT 형태소 태그** | 헬라어 형태소 | CC BY-SA (태그) | github.com/morphgnt/sblgnt |
| **OSHB / MorphHB** | 히브리어 구약 + 형태소 | CC BY 4.0 | github.com/openscriptures/morphhb |
| **Strong's 번호 + 최소 정의** | 사전(PD판) | Public Domain | github.com/openscriptures/strongs |

> ⚠️ CC BY-SA 자료(OSHB 등)는 copyleft라 **별도 디렉터리 + 해당 라이선스 명기**로 분리해 둘 것. MIT 코드와 섞지 말 것.

## ❌ 저장소에 넣으면 안 됨 (저작권 보호 — 사용자가 개인 라이선스로만 사용)

| 자료 | 저작권자 | 비고 |
|------|----------|------|
| **개역개정** | 대한성서공회 | 한국 표준 번역. **개인 연구·설교 준비용만**, 공개 배포·번들 금지 |
| **NA28** (Nestle-Aland 28판) | Deutsche Bibelgesellschaft | 신약 헬라어 비평본. 번들 불가, 사용자 보유분 연동만 |
| **BHS** (Biblia Hebraica Stuttgartensia) | Deutsche Bibelgesellschaft | 구약 히브리어 비평본. 번들 불가 |
| **SBLGNT** | SBL & Logos | 텍스트 번들 재배포 위험. 형태소 태그(MorphGNT)는 별개 |
| **WLC** (Westminster Leningrad Codex) | Westminster Seminary | 번들 비권장 → OSHB로 대체 |
| **Louw-Nida 사전** | United Bible Societies | 정의·도메인 텍스트 번들 금지. 도메인 번호 참조만 신중히 |

> ⚠️ archive.org 등에 스캔본이 올라와 있어도, NA28·BHS·Louw-Nida는 현행 저작권이므로 그 출처가 합법이 아닐 수 있다. 저장소에 넣지 말 것.

## 본문 파일 포맷 (Exegete 표준)

`src/data/<번역본>.txt` — UTF-8, **한 줄 = 한 절**:
```
창1:1 <천지 창조> 태초에 하나님이 천지를 창조하시니라
창1:2 땅이 혼돈하고 공허하며 ...
요3:16 하나님이 세상을 이처럼 사랑하사 ...
```
- 형식: `<책약어><장>:<절> [<소제목>] 본문`
- 소제목 `< >`는 선택(페리코페 경계 힌트로 사용)
- 책 약어는 `src/data/book_abbrev.json` 참조 (한국어 66권 기준)
- 환경변수 `EXEGETE_BIBLE`로 사용할 본문 파일 지정 가능

## 권위 자료 (분석 시 "참조 기준"으로 인용, 데이터 번들 아님)

분석 AI가 원어·신학을 다룰 때 아래를 **기준으로 삼되**, 확신 없으면 `[확인 필요]` 표시:
- 본문비평: BHS·BHQ·NA28·UBS5·Göttingen LXX
- 사전·문법: BDAG·HALOT·NIDNTTE·Wallace·BDF
- 주석: ICC·WBC·NICOT·NICNT·Hermeneia·KEK·EKK
