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
2. `scripts/copy_post.sh` 실행 → 가장 최근 글 본문이 클립보드에 복사됨
   - 예전 글은 폴더 이름 일부로 지정: `scripts/copy_post.sh u2oDdU6z`
3. 티스토리 글쓰기 → 마크다운 모드로 붙여넣기 → 제목·태그 입력, 카테고리 `AI` → 비공개 저장 후 확인 → 발행

## 티스토리 자동 발행을 하지 않는 이유

티스토리 Open API(글쓰기 포함)는 종료되어 공식적인 자동 발행 방법이 없다.
로그인 세션을 흉내 내는 비공식 방법은 정책 변경에 깨지기 쉽고 계정 위험이 있어 쓰지 않는다.

## 로드맵

- [x] 1단계: 자막 수집, `/write` (분석 → 작성 → 교정), 문체 스킬 초기 버전
- [ ] 2단계: `/feedback` (수정 내용으로 문체 규칙 학습), researcher 팩트체크 + `claims.json`
- [ ] 3단계: `/audit` 정기 점검, 업데이트 알림
- [ ] 기타: 자막 없는 영상용 음성 인식(Whisper)
