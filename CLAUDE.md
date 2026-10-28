# blog-automation

유튜브 링크를 받아 moonesok.tistory.com `AI` 카테고리에 올릴 블로그 글을 만드는 프로젝트.

## 파이프라인

`/write <유튜브 URL>` → 수집(youtube-transcript 스킬) → analyst → writer → editor → 기준점 커밋

## 폴더

- `.claude/commands/` 슬래시 명령 (`/write`)
- `.claude/agents/` analyst, writer, editor
- `.claude/skills/youtube-transcript/` 자막 추출 스크립트
- `.claude/skills/blog-style/` 문체 규칙. 계속 갱신된다. 변경은 `changelog.md`에 기록
- `posts/<YYYY-MM-DD>-<video_id>/` 글 하나당 폴더
  - `meta.json`, `transcript.md` 원재료
  - `analysis.md` 분석, `post.md` 본문, `publish.md` 제목·태그·카테고리, `editor-notes.md` 교정 메모
  - `versions/vN.md` 클립보드로 복사한(=발행용) 버전, `versions/log.tsv` 버전별 저장 시각
- `copy-post` (`sh copy-post`) 주석을 뺀 본문을 클립보드에 복사하고 버전을 남긴다. 대화형 메뉴가 있으므로 Claude가 대신 실행하지 않고 사용자에게 안내한다

`git log`에서 `draft:` 커밋은 AI 초안, `copy: ... vN` 커밋은 사용자가 실제로 복사한 버전이다. 둘의 차이가 사용자의 수정이다.

## 규칙

- 티스토리 공식 Open API는 종료됐다. 블로그에 자동으로 올리지 않는다. 발행은 사용자가 붙여넣기로 한다.
- 비공식 세션·쿠키 기반 업로드는 쓰지 않는다 (계정 제재·정책 변경 위험).
- 글을 쓰거나 고칠 때는 항상 `blog-style` 스킬을 따른다.
- `blog-style`은 사용자의 승인 없이 바꾸지 않는다.
- Python은 `.venv/bin/python`을 쓴다. 의존성은 `requirements.txt`.

## 사용자가 남기는 주석

`post.md`를 고칠 때 사용자가 남기는 주석. `/feedback`(2단계)이 이것을 근거로 규칙을 만든다.

- `<!-- 왜: ... -->` 이렇게 고친 이유. `전체 적용`이 붙으면 같은 패턴을 글 전체에 적용한 것으로 본다
- `<!-- 이 글만 -->` 이 글에만 해당하는 수정. 규칙으로 만들지 않는다
- `<!-- 좋음: ... -->` 마음에 든 부분. 예시 후보
- `<!-- 확인 필요 -->` 작성 단계에서 붙는 미검증 표시
