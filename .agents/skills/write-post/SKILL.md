---
name: write-post
description: 유튜브 링크로 블로그 글 초안을 만든다 (수집 → 분석 → 작성 → 교정 → draft 커밋). 사용자가 유튜브 링크를 주며 블로그 글을 써 달라고 할 때 사용. Claude Code의 /write와 같은 파이프라인의 Codex판.
---

# write-post

입력: 유튜브 URL과 (선택) 이번 글에 대한 추가 요청. 추가 요청은 `blog-style`보다 우선한다.

Codex에는 Claude Code의 서브에이전트가 없으므로, 아래 단계마다 **역할 파일을 처음부터 끝까지 읽고 그 역할로서** 직접 수행한다. 단계 사이에 이전 역할의 판단을 섞지 않는다. 특히 writer 단계에서는 `analysis.md`만 보고 쓰고, 자막을 다시 뒤져 내용을 덧붙이지 않는다.

## 1. 수집

`youtube-transcript` 스킬대로 자막을 가져온다.

```bash
.venv/bin/python .claude/skills/youtube-transcript/scripts/fetch_transcript.py "<URL>"
```

- 출력 마지막 줄이 작업 폴더다. 실패하면 이유를 알리고 멈춘다.
- 같은 영상 폴더에 이미 `post.md`가 있으면 덮어쓰지 말고 사용자에게 먼저 묻는다. (새 폴더로 쓰려면 `--out`으로 임시 폴더에 받은 뒤 `posts/<날짜>-<ID>-2`로 옮긴다.)
- `.venv`가 없으면 `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.

## 2. 분석 — `.claude/agents/analyst.md`

역할 파일대로 작업 폴더에 `analysis.md`를 쓴다.

## 3. 작성 — `.claude/agents/writer.md`

`blog-style` 스킬을 전부 읽은 뒤, 역할 파일대로 `post.md`와 `publish.md`를 쓴다.

## 4. 교정 — `.claude/agents/editor.md`

역할 파일의 체크리스트대로 `post.md`를 고치고 `editor-notes.md`를 쓴다.

## 5. 기준점 커밋

글은 도구 리포가 아니라 `posts/` 전용 로컬 저장소에 커밋한다 (GitHub에 올리지 않음).

```bash
# posts/.git이 없으면 먼저: git -C posts init -q -b main
git -C posts add <폴더 이름> && git -C posts commit -m "draft: <제목 후보 1번>"
```

`<폴더 이름>`은 `posts/`를 뺀 이름이다. 도구 리포에는 글을 커밋하지 않는다.

## 6. 보고 (한국어로, 짧게)

- 제목 후보 3개와 태그
- `확인 필요` 표시 개수와 위치
- `editor-notes.md`의 "사용자가 판단할 점"
- 다음 할 일
  1. `post.md`를 직접 고친다. 애매한 수정에는 `<!-- 왜: ... -->`, 이 글에만 해당하면 `<!-- 이 글만 -->`
  2. 터미널에서 `sh copy-post` → 티스토리 글쓰기에서 **HTML 모드**로 붙여넣기 → 카테고리 `AI` → 비공개 저장 후 확인

블로그에 직접 올리지 않는다. `sh copy-post`는 대화형이라 에이전트가 대신 실행하지 않는다.
