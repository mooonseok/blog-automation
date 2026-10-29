# blog-automation

유튜브 링크를 받아 블로그 글(티스토리)을 만드는 프로젝트. Codex와 Claude Code가 함께 읽는 공통 지침이다.
처음 이 리포를 여는 에이전트는 `HANDOFF.md`를 먼저 읽는다. 지금까지의 결정과 다음 작업이 정리돼 있다.

## 사용자 선호 (항상 지킨다)

- 사용자에게 하는 모든 답변은 **한국어**로 쓴다.
- 사용자가 읽는 문서(README 등)는 `~합니다` 체로 쓴다. 블로그 본문은 평서체 `~다`.
- 글(`posts/`)은 GitHub에 올리지 않는다. GitHub 리포에는 도구만 올린다.
- 블로그 글에 영상 링크·타임스탬프 링크와 자동 출처 목록을 넣지 않는다. 원재료 기록은 analysis.md·meta.json에 보관한다.
- "오늘부터 바로 써먹기/해볼 것" 같은 마무리 행동 과제를 자동으로 붙이지 않는다. 주제를 설명하는 실제 절차·비교는 유지한다.
- 되돌리기 어려운 작업(강제 푸시, 기록 재작성, 삭제)은 사용자 확인 후에만 한다.
- 블로그 글은 영상을 재창조하되, **영상의 주인공(도구·개념)이 무엇이고 어떻게 동작하는지는 반드시 설명**한다 (blog-style Q1 필수 요소).
- 글 디자인은 **티스토리가 지우지 않는 서식만** 쓴다: `color`, `background-color`, `text-align`과 티스토리 자체 서식(`data-ke-*`). flex·border·radius·margin·gradient 등은 붙여넣을 때 지워진다. `render_post.py`의 `sanitize()`가 이를 강제한다.
- 이미지 자동화에 생성 API 외의 유료 외부 도구·호스팅을 추가하지 않는다. 이미지 파일은 posts/ 아래 로컬에 저장하고 티스토리 기본 업로드를 사용한다.
- 작성 과정·검증 여부에 대한 메타 문장("확인하지 않았다" 등)은 글에 절대 넣지 않는다.

## 파이프라인

수집 → analyst → curator → writer → designer → 자동 검사 → editor → reader (FAIL이면 writer 고쳐 쓰기) → `posts/` 저장소에 draft 커밋

| 역할 | 전문가 | 만드는 것 |
|---|---|---|
| analyst | 기술 리서처 | `analysis.md` (자막 보정, 주장·근거·용어) |
| curator | IT 매거진 편집장 | `outline.md` (핵심 1개, 질문 3개, 버릴 것, 섹션 설계) |
| writer | 숏폼 교육 콘텐츠 작가 | `post.md`, `publish.md` |
| designer | 에디토리얼 디자이너 | 부품 배치, `images.md` (이미지 생성 프롬프트) |
| editor | 교열 기자 | 메타 문장·금지 표현 삭제, 문단 쪼개기, `editor-notes.md` |
| reader | 영상을 안 본 주니어 개발자 | `reader-test.md` (PASS/FAIL) |

- 자동 실행: `sh auto <URL> [추가 요청]`. 역할마다 `codex exec`를 따로 실행한다 (기본 `gpt-6-astra` / `high`, `CODEX_MODEL`·`CODEX_EFFORT`로 변경). 수집·커밋은 스크립트가 한다. 역할별 로그는 글 폴더의 `logs/`
- Claude Code: `/write <URL>` (`.claude/commands/write.md`), 역할은 서브에이전트(`.claude/agents/`)
- Codex 대화: `$write-post` 스킬, 역할은 커스텀 에이전트(`.codex/agents/*.toml`, 각자 `.claude/agents/<역할>.md`를 읽음)

## 폴더

- `.claude/skills/` 스킬 원본. `.agents/skills/`는 Codex용 심볼릭 링크다 (같은 파일)
  - `youtube-transcript/` 자막 추출 스크립트
  - `blog-style/` 문체·구조 규칙. 계속 갱신된다. 변경은 `changelog.md`, 출처는 `references.md`
- `.claude/agents/` 역할 6개의 정의 원본 (analyst, curator, writer, designer, editor, reader)
- `.codex/agents/` Codex 커스텀 에이전트 (역할 정의 원본을 읽게 하는 얇은 설정)
- `.claude/commands/write.md` Claude Code용 `/write`
- `.agents/skills/write-post/` Codex용 글쓰기 파이프라인 스킬
- `posts/` 글 저장소. 도구 리포에서 `.gitignore`로 제외된 **별도 로컬 git 저장소**다 (원격 없음)
- `posts/<YYYY-MM-DD>-<video_id>/` 글 하나당 폴더
  - `meta.json`, `transcript.md` 원재료
  - `analysis.md` 분석, `outline.md` 설계, `post.md` 본문, `publish.md` 제목·태그, `images.md` 이미지 프롬프트, `editor-notes.md` 교정 메모, `reader-test.md` 독자 테스트, `logs/` 역할별 로그
  - `versions/vN.md` 클립보드로 복사한(=발행용) 버전, `versions/log.tsv` 버전별 저장 시각
  - `preview.html` 티스토리 스킨 CSS를 입힌 미리보기 (git 제외)
- `auto` (`sh auto`) 유튜브 링크 하나로 초안까지 자동 실행 (Codex CLI 필요)
- `copy-post` (`sh copy-post`) 발행본을 HTML로 바꿔 클립보드에 넣고 버전을 남긴다. 대화형 메뉴가 있으므로 에이전트가 대신 실행하지 않고 사용자에게 안내한다
- `tools/render_post.py` 마크다운(+부품 문법 `:::summary` 등) → 티스토리용 HTML 변환기. 티스토리 자체 서식(data-ke-*)과 글자색·배경색만 쓴다. 티스토리 편집기가 나머지 인라인 스타일(display, border, radius, gradient, margin, word-break 등)을 지우기 때문이며, `sanitize()`가 허용 목록 밖의 스타일을 미리 지운다. `--preview`는 미리보기 페이지
- `tools/lint_post.py` blog-style 규칙 자동 검사 (메타 문장, 해요체, 문단 길이, 영상 링크, 필수 부품, 불필요한 마무리 섹션, 이미지)
- `tools/set_clipboard_html.js` 클립보드에 서식(HTML)과 소스(텍스트)를 함께 넣는다 (macOS)

`git -C posts log`에서 `draft:` 커밋은 AI 초안, `copy: ... vN` 커밋은 사용자가 실제로 복사한 버전이다. 둘의 차이가 사용자의 수정이다.

## git 규칙

- 도구 리포(이 폴더의 `git`)에는 도구만 커밋한다. 글 파일은 절대 도구 리포에 커밋하지 않는다.
- 글 관련 커밋은 모두 `git -C posts ...`로 한다.
- 도구 리포 커밋 작성자는 `mooonseok` (리포 로컬 설정).

## 규칙

- 티스토리 공식 Open API는 종료됐다. 블로그에 자동으로 올리지 않는다. 발행은 사용자가 붙여넣기로 한다.
- 비공식 세션·쿠키 기반 업로드는 쓰지 않는다 (계정 제재·정책 변경 위험).
- 글을 쓰거나 고칠 때는 항상 `blog-style` 스킬을 따른다.
- `blog-style`은 사용자의 승인 없이 바꾸지 않는다.
- Python은 `.venv/bin/python`을 쓴다. 의존성은 `requirements.txt`.
- 사람·저장소 링크는 직접 열어서 확인한 주소만 쓴다. 주소를 지어내지 않는다.

## 사용자가 남기는 주석

`post.md`를 고칠 때 사용자가 남기는 주석. `/feedback`(예정)이 이것을 근거로 규칙을 만든다. 주석은 발행본에서 자동으로 빠진다.

- `<!-- 왜: ... -->` 이렇게 고친 이유. `전체 적용`이 붙으면 같은 패턴을 글 전체에 적용한 것으로 본다
- `<!-- 이 글만 -->` 이 글에만 해당하는 수정. 규칙으로 만들지 않는다
- `<!-- 좋음: ... -->` 마음에 든 부분. 예시 후보
- `<!-- 확인 필요 -->` 작성 단계에서 붙는 미검증 표시
- `<!-- 내 생각: ... -->` 사용자가 직접 의견을 쓸 자리
