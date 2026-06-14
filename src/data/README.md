# 본문 데이터 넣는 법

이 폴더에는 성경 본문 파일이 들어갑니다. **저작권 본문은 저장소에 포함되지 않으므로** 사용자가 직접 넣어야 합니다.

## 파일 포맷

`<번역본>.txt` — UTF-8, **한 줄 = 한 절**:
```
창1:1 <천지 창조> 태초에 하나님이 천지를 창조하시니라
창1:2 땅이 혼돈하고 공허하며 흑암이 깊음 위에 있고 ...
요3:16 하나님이 세상을 이처럼 사랑하사 독생자를 주셨으니 ...
```
- 형식: `<책약어><장>:<절> [<소제목>] 본문`
- `<소제목>`은 선택 (페리코페 경계 힌트로 쓰임)
- 책 약어는 `book_abbrev.json` 참조 (한국어 66권)

## 어떤 본문을 넣나

- **공개 도메인**(WEB·KJV·ASV 등): 자유롭게 사용. `web.txt`, `kjv.txt`, `asv.txt`는 git에 포함 허용(.gitignore 화이트리스트).
- **개역개정 등 저작권 번역**: 개인 연구·설교 준비용으로 **본인이 준비**. `bible_krv.txt` 같은 파일은 git에서 자동 제외됩니다(.gitignore). 공개 배포 금지.
- 자세한 소스·라이선스: `../../docs/DATA_SOURCES.md`

## 사용

```bash
# 기본 파일(bible_krv.txt) 사용
python ../lookup.py "요3:16"

# 다른 본문 파일 지정
EXEGETE_BIBLE=src/data/web.txt python src/lookup.py "John 3:16"   # (영어 약어는 별도 매핑 필요)
```

> 인코딩 주의: 한국어 본문이 CP949/EUC-KR이면 UTF-8로 변환 후 넣으세요.
> `python -c "open('out.txt','w',encoding='utf-8').write(open('in.txt','rb').read().decode('cp949'))"`
