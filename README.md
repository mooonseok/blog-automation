# blog-automation

유튜브 링크 하나로 [moonesok.tistory.com](https://moonesok.tistory.com) `AI` 카테고리에 올릴 글 초안을 만드는 Claude Code 프로젝트.

## 설치

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## 사용

이 폴더에서 Claude Code를 열고:

```
/write https://www.youtube.com/watch?v=...
/write https://youtu.be/... 입문자 대상으로 써줘
```

결과는 `posts/<날짜>-<영상ID>/`에 생긴다.

1. `post.md`를 직접 고친다 (주석 규칙은 `CLAUDE.md` 참고)
2. `sh copy-post` 실행 → 본문(주석 제외)이 클립보드에 복사됨
   - 처음 복사하는 새 글이면 바로 복사하고 `versions/v1.md`로 저장
   - 이미 복사한 글이면 메뉴가 뜬다: 현재 글(수정됐으면 다음 버전으로 저장) / 예전 버전 / 다른 글
   - 새 버전이 저장될 때마다 그 글 폴더를 자동 커밋·푸시 (`copy: <폴더> vN`)
   - 글 지정: `sh copy-post u2oDdU6z` 또는 `sh copy-post <유튜브 링크>`
3. 티스토리 글쓰기 → 마크다운 모드로 붙여넣기 → 제목·태그 입력, 카테고리 `AI` → 비공개 저장 후 확인 → 발행

## 티스토리 자동 발행을 하지 않는 이유

티스토리 Open API(글쓰기 포함)는 종료되어 공식적인 자동 발행 방법이 없다.
로그인 세션을 흉내 내는 비공식 방법은 정책 변경에 깨지기 쉽고 계정 위험이 있어 쓰지 않는다.

## 로드맵

- [x] 1단계: 자막 수집, `/write` (분석 → 작성 → 교정), 문체 스킬 초기 버전
- [ ] 2단계: `/feedback` (수정 내용으로 문체 규칙 학습), researcher 팩트체크 + `claims.json`
- [ ] 3단계: `/audit` 정기 점검, 업데이트 알림
- [ ] 기타: 자막 없는 영상용 음성 인식(Whisper)
