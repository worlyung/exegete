# 주해 사실 주장 감사 하네스

이 문서는 `output/<구절>_주해.md` 같은 주해 초안에서 **로컬 데이터와 CLI, 또는 감사자가 실제로 열어 볼 수 있게 보관된 정확한 출처로 다시 확인할 수 있는 사실 주장만** 점검하는 품질 게이트이다. 목적은 그럴듯한 기억 인용을 막고, 본문·원어·사전·관주에 관한 문장을 실행 결과에 연결하는 데 있다.

이 감사는 신학 전통, 교리적 타당성, 설교의 설득력, 적용의 적절성, 해석 중 어느 견해가 더 옳은지를 판단하거나 점수화하지 않는다. 그러한 문장은 이 하네스의 `감사 대상 아님`으로 남긴다. 단, 그 문장 안에 검증 가능한 사실(예: 특정 원어 형태, 본문 인용, “관주가 이 구절을 제시한다”)이 섞이면 그 사실 부분만 Claim Ledger에 분리한다.

## 적용 시점과 저장 위치

- **실행 시점**: 4단계 전체 주해 초안이 완성된 뒤, 사용자에게 완성본으로 제시하기 전과 `.docx` 내보내기 전.
- **대상**: 한 번의 감사는 하나의 Markdown 초안과 하나의 기준 구절만 다룬다.
- **저장 위치**: `output/audit/<안전한-초안이름>/<YYYYMMDD-HHmmss-fff>/`
  - `audit.md`: Claim Ledger, 최종 판정, WARN 동의 기록
  - `00_manifest.md`: 대상 초안 경로·SHA-256·기준 구절·작업 경로·실행 폴더
  - `00_commands.md`: 변수까지 실제 값으로 펼친 실행 명령, 종료 코드, stdout/stderr 파일명
  - `01_bible_source.txt` 이후: 변형하지 않은 CLI 표준 출력. 각 파일의 짝인 `<파일명>.stderr.txt`에는 표준 오류·경고를 따로 보관한다.
- `<안전한-초안이름>`은 감사 대상 파일의 확장자를 뺀 Windows 안전 파일명으로 정한다. 예: `output/요3_16_주해.md`는 `output/audit/요3_16_주해/20260718-153000-123/`에 저장한다.
- 동일 밀리초에 다시 실행되어도 새 폴더 접미사를 붙여 기존 증거를 덮어쓰지 않는다.

## 구조 사전 게이트

Claim Ledger를 쓰기 전에 아래 항목을 먼저 확인한다. 이 게이트는 주해의 구조적 주장 전체를 참·거짓으로 판정하는 절차가 아니라, **어떤 사실을 무엇으로 검증할 수 있는지**를 고정하는 절차이다.

| 게이트 | 반드시 남길 증거 | 통과 조건 | 통과하지 못한 경우 |
|---|---|---|---|
| 대상 식별 | 초안 경로, SHA-256, 기준 구절, 실행 시각 | 초안 파일이 존재하고 경로·해시·기준 구절이 `00_manifest.md`에 함께 기록됨 | `FAIL`: 다른 초안이나 감사 뒤 바뀐 초안과 대조할 위험이 있어 감사 종료 |
| 본문 기준 | `lookup.py --json` 출력과 실제 선택 본문 파일 경로 | 대상 절이 JSON의 `verses`에 있고 `target: true`임 | `FAIL`: 본문 인용·절 범위 사실을 감사할 수 없음 |
| 문맥·단락 근거 | `--context 3` 및 `--pericope`의 표준 출력과 짝 `stderr` 경고 | 초안의 소제목·절 범위·앞뒤 문맥에 관한 사실이 출력과 맞고, 정확 경계 주장에 폴백 경고가 없음 | 근거 없는 정확 경계 주장은 수정·삭제 후 재감사. 그대로면 `FAIL` |
| 정경·원어 분기 | 본문 JSON의 `testament` | `NT`에는 `greek_lookup.py`, `OT`에는 `hebrew_lookup.py`만 사용 | `FAIL`: 다른 정경의 원어 도구를 근거로 삼음 |
| 원어·사전 자료 | 해당 원어 조회의 `--json`, 사전 문장이 있으면 `--lex --json` | 각 원어 사실이 실제 단어 항목과 일치하고, 사전 뜻은 `--lex` 출력에 있음 | 해당 사실 주장이 있으면 `FAIL`; 주장 자체가 없으면 `해당 없음` |
| 관주 자료 | `xref.py --json` 출력 | 관주 사실이 실제 반환된 구절·순위·votes와 일치함 | 관주 사실 주장이 있으면 `FAIL`; 자료 부재를 숨기면 안 됨 |
| 외부 사실 근거(해당 시) | 사본·역사·LXX·문헌에 대한 정확한 판본/쪽수/URL과 실제 열람 가능한 원자료 | 사실 문장이 원자료의 정확한 위치와 일치함 | 출처 없음·불일치면 `FAIL`, 이 환경에서 원자료를 열 수 없으면 `보류(HOLD)` |
| 실행 흔적 | `00_commands.md`의 명령, 종료 코드, 증거 파일명 | 근거마다 재실행 가능한 명령과 원출력이 함께 보관됨 | `FAIL`: 나중에 같은 결과를 대조할 수 없음 |

`--pericope`와 `--context`는 도구가 반환한 소제목·절 범위·본문만 증명한다. 특히 `lookup.py --pericope`의 짝 `stderr`가 같은 장 전체를 **문맥 폴백**으로 표시하고 정확한 단락 경계에 `[확인 필요]`를 붙이면, 그 출력은 정확한 단락 경계의 근거가 아니다. 초안은 그 폴백 범위와 `[확인 필요]`까지만 사실로 쓸 수 있다. 키아즘, 중심 강조점, 문학적 경계의 해석 자체는 신학·문학 판단이므로 숫자나 기계적 합격으로 판정하지 않는다. 출력에 소제목이나 경계 근거가 없으면 그것을 단정적 사실로 쓰지 말고 `확인 필요` 또는 해석적 제안으로 낮춘다.

## 감사 범위와 허용 근거

| 사실 주장 범주 | 허용되는 로컬 근거 | 대조 원칙 |
|---|---|---|
| 본문 인용, 책·장·절, 번역본에서 나온 문구 | `lookup.py <구절> --json`, `01_bible_source.txt` | 글자·절 범위·대상 절을 출력과 대조한다. 번역본 이름은 선택된 실제 본문 파일과 맞아야 한다. |
| 소제목, 도구가 제공한 단락·문맥 범위 | `lookup.py <구절> --pericope --json`, `--context 3 --json` | 출력에 있는 범위·소제목만 사실로 쓴다. |
| 헬라어/히브리어 표기, 음역, gloss, 원형, 스트롱 번호, 형태소 파싱 | 정경에 맞는 `greek_lookup.py` 또는 `hebrew_lookup.py`의 `--json` | 각 필드는 같은 단어 항목의 실제 값과 정확히 대조한다. |
| 사전의 상세 정의 | 같은 원어 도구의 `--lex --json` | `lexicon`에 실제로 들어 있는 정의만 사전 근거로 인용한다. `--lex` 없이 기억한 사전 뜻을 쓰지 않는다. |
| 관주 구절, 도구가 제시한 순위·votes·본문 일부 | `xref.py <구절> --json` | “관주 도구가 제시함”까지만 사실이다. 관주 하나만으로 직접 인용·암시·신학적 필연성을 증명하지 않는다. |
| 한/영/원어 병렬 출력에 실제로 보이는 차이 | `compare.py <구절>` 원출력 | 출력에 보이는 번역·원어만 기술한다. 뜻의 우열이나 신학적 결론은 감사 대상이 아니다. |
| 사본·역사·LXX·외부 문헌의 사실 또는 특정 페이지 인용 | 감사자가 실제로 열 수 있는 원자료와 판본·저자·쪽수/절·URL 등 정확한 위치 | 원자료의 해당 위치와 대조한다. 출처 자체가 없으면 `FAIL`, 출처는 있으나 이 감사 환경에서 열 수 없으면 `보류(HOLD)`이다. |

다음은 이 하네스가 판정하지 않는다: 특정 교단의 해석이 맞는지, 한 원어의 문맥상 최선 번역인지, 키아즘이 설득력 있는지, Hays 기준의 암시 판정, 설교 대지·적용·기도의 적절성. 다만 이런 문장 안의 출처·원어·본문 인용이 틀렸다면 그 사실 부분은 감사한다.

## Claim Ledger

감사자는 초안의 검증 가능한 사실 문장마다 한 행을 만든다. 한 문장에 본문 인용과 원어 파싱처럼 서로 다른 사실이 섞이면 행을 분리한다. 신학 견해 문장만 있는 경우에는 행을 만들지 않고 `감사 대상 아님`으로 표시한다.

`audit.md`에는 아래 표를 복사해 작성한다.

| ID | 초안 위치·짧은 인용 | 사실 주장 | 범주 | 증거 파일·JSON 경로 또는 출력 위치 | 대조 결과 | 판정 | 조치 |
|---|---|---|---|---|---|---|---|
| C-01 | `## 본문`, “…” | `<구절>`의 본문 문구가 “…”임 | 본문 | `02_lookup_target.json > verses[n].text` | 일치/불일치 및 차이 | PASS/FAIL/보류(HOLD)/해당 없음 | 유지/수정/삭제 |
| C-02 | `## 원어`, “…” | `<단어>`의 Strong·파싱이 “…”임 | 원어 | `05_greek_original.json > words[n]` | 일치/불일치 및 차이 | PASS/FAIL/보류(HOLD)/해당 없음 | 유지/수정/삭제 |
| C-03 | `## 사전`, “…” | 사전이 해당 정의를 제시함 | 사전 | `06_greek_lexicon.json > words[n].lexicon` | 일치/불일치 및 차이 | PASS/FAIL/보류(HOLD)/해당 없음 | 유지/수정/삭제 |
| C-04 | `## 관주`, “…” | 관주 도구가 `<구절>`을 관련 구절로 반환함 | 관주 | `07_xref.json > 실제 최상위 키(예: 요한복음 3:16) > [n]` | 일치/불일치 및 순위·votes | PASS/FAIL/보류(HOLD)/해당 없음 | 유지/수정/삭제 |

증거 파일에는 원출력을 고치거나 요약해 덮어쓰지 않는다. Ledger에는 사람이 읽기 쉬운 JSON 경로·행 위치를 적고, 사실과 다른 부분은 짧게 그대로 기록한다. `WARN`은 사실 행의 판정이 아니라, 모든 사실 행이 `PASS`인 뒤 남은 비사실적 고지에 대한 **최종 상태**이다.

## PASS / WARN / FAIL 기준

판정은 점수나 신학적 등급이 아니다. 아래는 사실 근거의 상태만 뜻한다.

### PASS

다음이 모두 충족되었을 때만 `PASS`이다.

- 적용되는 구조 사전 게이트가 모두 통과했다.
- Ledger의 모든 사실 주장이 저장된 원출력과 일치한다.
- 본문 인용에는 실제 대상 절이 있고, 원어·사전·관주 주장은 각각 필요한 전용 명령의 성공 결과가 있다.
- 정확한 단락 경계를 사실로 썼다면 `04_lookup_pericope.json.stderr.txt`에 문맥 폴백 경고가 없다.
- 사본·역사·LXX·외부 문헌의 사실을 썼다면, 해당 원자료가 실제로 열람되어 Ledger에서 일치 판정을 받았다.
- 원어 또는 사전 데이터가 없는 경우에는 그에 의존한 사실 주장을 새로 만들지 않았고, 초안이 그 부재를 숨기지 않는다.

### WARN

`WARN`은 **모든 Claim Ledger의 사실 주장이 이미 `PASS`인 상태**에서, 사용자가 알아야 할 비사실적 제한·고지·표현 선택만 남았을 때 쓴다. 예를 들어 결과물에 연구·묵상 보조라는 한계 고지를 유지할지, 감사 대상이 아닌 신학적 제안임을 더 분명히 밝힐지를 사용자가 선택해야 하는 경우이다.

`WARN`은 다음을 덮을 수 없다: 근거 없는 직접 인용·암시, 정확한 단락 경계, 틀린 본문/원어/사전/관주, 누락된 출처, 열어 보지 못한 외부 사실. 이런 경우는 `FAIL` 또는 `보류(HOLD)`이다.

`WARN`은 자동 통과가 아니다. 내보내기나 완료 선언 전에 아래 중 하나를 `audit.md`에 남긴다.

1. 문장을 수정·삭제하고 다시 감사하여 `PASS`로 만든다.
2. 사용자가 제한을 읽고 공개를 명시적으로 동의한다. 동의한 사람, 시각, 남기는 문구를 그대로 기록한다.

동의가 없으면 상태는 계속 `WARN`이며 완료·내보내기를 선언하지 않는다.

### FAIL

다음 중 하나라도 있으면 `FAIL`이다.

- 기준 구절·대상 절·본문 인용·선택 번역본이 실제 출력과 다르다.
- 정경에 맞지 않는 원어 도구를 사용했거나, 원어 형태·스트롱·파싱·원형을 출력 없이 또는 다르게 썼다.
- 사전 정의를 `--lex` 증거 없이 사실처럼 썼다.
- 관주 데이터가 없거나 반환하지 않은 내용을 관주 사실·직접 인용·암시의 증거로 썼다.
- 정확한 단락 경계·소제목을 사실로 주장했지만 저장된 문맥/단락 출력이 이를 뒷받침하지 않거나, `--pericope`의 문맥 폴백 경고를 무시했다.
- 사본·역사·LXX·외부 문헌의 사실을 출처 없이, 또는 실제 원자료와 다르게 썼다.
- 재실행 가능한 원출력이나 종료 코드가 보관되지 않았다.

`FAIL`이면 해당 주장을 수정하거나 삭제한 뒤 새 감사 실행을 만든다. `FAIL` 또는 구조 사전 게이트 결함이 남아 있는 초안은 완성본으로 선언·공유하거나 `.docx`로 내보내지 않는다.

## CHAT 또는 로컬 실행 불가 시 평가 보류

채팅 환경에 저장소·본문 데이터·Python 실행 권한이 없거나, Ledger에 든 외부 원자료를 이 환경에서 실제로 열 수 없으면 감사 결과는 `보류(HOLD)`이다. 이 경우에는 다음만 제공한다.

- 실행해야 할 정확한 명령 목록
- 필요한 원출력 파일 목록
- 검증할 Claim Ledger 빈 표
- 보류 사유

채팅에 붙여 넣은 본문, 기억, 화면 캡처 요약, 모델의 일반 지식은 `PASS` 근거가 아니다. 로컬에서 CLI 자체를 실행할 수 없어서 생긴 보류는 `FAIL`과 다르지만, 사용자 동의로 `PASS`나 `WARN`으로 바꿀 수 없다. **보류 중에는 4단계 주해를 완성본으로 선언·공유하거나 내보내지 않는다.**

반대로 로컬 CLI는 실행되었으나 원어·사전·관주 데이터가 설치되지 않아 실패했고 초안이 그 데이터에 의존한 사실 주장을 한다면 `HOLD`가 아니라 `FAIL`이다. 데이터가 없는 사실을 초안이 주장하지 않는 경우에만 그 범주는 `해당 없음`으로 남긴다.

## PowerShell 실행·저장 절차

아래는 저장소 루트에서 실행한다. `$ref`와 실제 `$draft` 경로만 바꾸며, 명령의 원출력은 손대지 않는다.

```powershell
$ref = '요3:16'
$draft = 'output/요3_16_주해.md'
if (-not (Test-Path -LiteralPath $draft -PathType Leaf)) {
    throw "감사 대상 파일이 없습니다: $draft"
}
$case = [System.IO.Path]::GetFileNameWithoutExtension($draft)
if ([string]::IsNullOrWhiteSpace($case) -or
    $case.IndexOfAny([System.IO.Path]::GetInvalidFileNameChars()) -ge 0) {
    throw "안전하지 않은 대상 파일명입니다: $draft"
}
$draftHash = (Get-FileHash -LiteralPath $draft -Algorithm SHA256).Hash
$repoRoot = (Get-Location).Path
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$caseRoot = Join-Path 'output/audit' $case
New-Item -ItemType Directory -Force -Path $caseRoot | Out-Null
$runBase = Join-Path $caseRoot $stamp
$run = $runBase
$suffix = 2
while (Test-Path -LiteralPath $run) {
    $run = "$runBase-$suffix"
    $suffix++
}
New-Item -ItemType Directory -Path $run -ErrorAction Stop | Out-Null
$utf8 = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = $utf8
$OutputEncoding = $utf8

@(
    '# 감사 실행 메타데이터'
    ''
    "- 대상: $draft"
    "- 기준 구절: $ref"
    "- 감사 당시 SHA256: $draftHash"
    "- 저장소 작업 경로: $repoRoot"
    "- 실행 폴더: $run"
) | Set-Content -Encoding utf8 (Join-Path $run '00_manifest.md')

function Save-ExegeteEvidence {
    param(
        [string]$Name,
        [string]$ExpandedCommand,
        [string]$PythonArguments
    )
    $stdoutPath = Join-Path $run $Name
    $stderrName = "$Name.stderr.txt"
    $stderrPath = Join-Path $run $stderrName
    # PowerShell의 오류 레코드를 섞지 않도록 Python 자식 프로세스의 두 스트림을 직접 파일로 보낸다.
    $process = Start-Process -FilePath 'python' -ArgumentList $PythonArguments `
        -WorkingDirectory $repoRoot -RedirectStandardOutput $stdoutPath `
        -RedirectStandardError $stderrPath -PassThru -Wait -NoNewWindow
    $exitCode = $process.ExitCode
    if (-not (Test-Path -LiteralPath $stdoutPath -PathType Leaf)) {
        [System.IO.File]::WriteAllBytes($stdoutPath, [byte[]]@())
    }
    if (-not (Test-Path -LiteralPath $stderrPath -PathType Leaf)) {
        [System.IO.File]::WriteAllBytes($stderrPath, [byte[]]@())
    }
    "- $Name | stderr=$stderrName | exit_code=$exitCode | command=$ExpandedCommand" |
        Add-Content -Encoding utf8 (Join-Path $run '00_commands.md')
    return $exitCode
}

# 본문 기준과 문맥/단락 근거
$sourceExit = Save-ExegeteEvidence '01_bible_source.txt' `
    'python -c "import sys; sys.path.insert(0, ''src''); import lookup; print(lookup.DATA)"' `
    '-c "import sys; sys.path.insert(0, ''src''); import lookup; print(lookup.DATA)"'
$lookupExit = Save-ExegeteEvidence '02_lookup_target.json' `
    "python src/lookup.py `"$ref`" --json" `
    "src/lookup.py `"$ref`" --json"
$contextExit = Save-ExegeteEvidence '03_lookup_context.json' `
    "python src/lookup.py `"$ref`" --context 3 --json" `
    "src/lookup.py `"$ref`" --context 3 --json"
$pericopeExit = Save-ExegeteEvidence '04_lookup_pericope.json' `
    "python src/lookup.py `"$ref`" --pericope --json" `
    "src/lookup.py `"$ref`" --pericope --json"

if ($sourceExit -ne 0 -or $lookupExit -ne 0 -or
    $contextExit -ne 0 -or $pericopeExit -ne 0) {
    throw '본문·문맥 증거를 만들지 못했습니다. 구조 사전 게이트 FAIL입니다.'
}
try {
    $lookup = Get-Content -Raw -Encoding utf8 "$run/02_lookup_target.json" |
        ConvertFrom-Json -ErrorAction Stop
} catch {
    throw '기준 본문 JSON을 읽지 못했습니다. 구조 사전 게이트 FAIL입니다.'
}
if ($lookup.query -ne $ref) {
    throw "기준 본문 JSON의 query 값이 기준 구절과 다릅니다: $($lookup.query)"
}
$targetVerses = @($lookup.verses | Where-Object { $_.target -eq $true })
if ($targetVerses.Count -eq 0) {
    throw '기준 본문 JSON에 target: true 절이 없습니다. 구조 사전 게이트 FAIL입니다.'
}
if ($lookup.testament -notin @('NT', 'OT')) {
    throw "알 수 없는 testament 값: $($lookup.testament)"
}

# 기준 본문의 정경을 읽어 올바른 원어 도구만 실행
$testament = $lookup.testament
if ($testament -eq 'NT') {
    Save-ExegeteEvidence '05_greek_original.json' `
        "python src/greek_lookup.py `"$ref`" --json" `
        "src/greek_lookup.py `"$ref`" --json" | Out-Null
    Save-ExegeteEvidence '06_greek_lexicon.json' `
        "python src/greek_lookup.py `"$ref`" --lex --json" `
        "src/greek_lookup.py `"$ref`" --lex --json" | Out-Null
} elseif ($testament -eq 'OT') {
    Save-ExegeteEvidence '05_hebrew_original.json' `
        "python src/hebrew_lookup.py `"$ref`" --json" `
        "src/hebrew_lookup.py `"$ref`" --json" | Out-Null
    Save-ExegeteEvidence '06_hebrew_lexicon.json' `
        "python src/hebrew_lookup.py `"$ref`" --lex --json" `
        "src/hebrew_lookup.py `"$ref`" --lex --json" | Out-Null
}

# 관주와 병렬 비교: 관주 실패도 원출력·종료 코드로 남겨 Ledger에서 판정
Save-ExegeteEvidence '07_xref.json' `
    "python src/xref.py `"$ref`" --json" `
    "src/xref.py `"$ref`" --json" | Out-Null
Save-ExegeteEvidence '08_compare.txt' `
    "python src/compare.py `"$ref`"" `
    "src/compare.py `"$ref`"" | Out-Null
```

마지막으로 `$run/audit.md`에 다음을 반드시 적는다.

```markdown
# 감사 기록

- 대상: `output/<초안파일>.md`
- 기준 구절: `<구절>`
- 감사 당시 SHA256: `<00_manifest.md의 값>`
- 실행 폴더: `<$run의 실제 경로>`
- 최종 상태: `PASS` / `WARN` / `FAIL` / `보류(HOLD)`

## Claim Ledger

<!-- 위 Claim Ledger 표를 채운다. -->

## WARN 동의 기록

<!-- WARN이 없으면 '해당 없음'. WARN이 있으면 사용자, 시각, 동의한 제한 문구를 그대로 적는다. -->

## 다음 조치

<!-- PASS면 내보내기 가능, WARN이면 동의 전 대기, FAIL/HOLD면 수정 또는 증거 수집을 명시한다. -->
```

## 내보내기 게이트

- 이 게이트는 **운영 규칙**이다. 현재 `export_docx.py`는 `audit.md`나 상태를 검사하지 않으므로, 호출자가 내보내기 직전에 직접 확인해야 한다.
- `PASS`: `audit.md`와 원증거를 저장하고, 내보내기 직전 `(Get-FileHash -LiteralPath $draft -Algorithm SHA256).Hash`가 `00_manifest.md`의 감사 당시 SHA-256과 같은 경우에만 대상 Markdown을 `.docx`로 내보낼 수 있다. 해시가 다르면 내용이 바뀐 것이므로 새 감사가 필요하다.
- `WARN`: 모든 Ledger 사실 행이 `PASS`이고, 사용자 동의가 `audit.md`에 남은 경우에만 내보낼 수 있으며, 남은 비사실적 제한도 함께 고지한다.
- `FAIL` 또는 `보류(HOLD)`: 완성본으로 선언·공유하거나 `.docx`로 내보내지 않는다. 수정 또는 로컬 증거 수집 뒤 새 감사 실행을 만든다.
- `python src/export_docx.py --all`을 쓸 때도 각 대상 Markdown마다 위 감사 기록이 있어야 한다. 한 파일의 `PASS`가 다른 파일의 근거가 되지 않는다.
