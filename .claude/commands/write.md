---
description: 유튜브 링크로 블로그 글 초안을 만든다 (수집 → 분석 → 작성 → 교정)
argument-hint: <유튜브 URL> [추가 요청]
---

유튜브 링크로 moonesok.tistory.com `AI` 카테고리에 올릴 글 초안을 만든다.

입력: $ARGUMENTS
(첫 번째 값이 URL, 나머지는 이번 글에 대한 추가 요청이다. 추가 요청은 blog-style보다 우선한다.)

## 1. 수집
`youtube-transcript` 스킬대로 자막을 가져온다.

```bash
.venv/bin/python .claude/skills/youtube-transcript/scripts/fetch_transcript.py "<URL>"
```

출력 마지막 줄의 작업 폴더 경로를 이후 모든 단계에 넘긴다. 실패하면 이유를 알리고 멈춘다.
같은 영상 폴더가 이미 있고 `post.md`가 있으면 덮어쓰지 말고 사용자에게 먼저 묻는다.

## 2. 분석
`analyst` 서브에이전트에게 작업 폴더 경로를 주고 `analysis.md`를 만들게 한다.

## 3. 작성
`writer` 서브에이전트에게 작업 폴더 경로와 추가 요청을 주고 `post.md`, `publish.md`를 만들게 한다.

## 4. 교정
`editor` 서브에이전트에게 작업 폴더 경로를 주고 `post.md`를 교정하고 `editor-notes.md`를 쓰게 한다.

## 5. 기준점 커밋
작업 폴더만 커밋한다. 이 커밋이 이후 `/feedback`이 "내가 고친 부분"을 찾는 기준점이 된다.

```bash
git add <작업 폴더> && git commit -m "draft: <제목 후보 1번>"
```

## 6. 보고
아래만 짧게 알린다.
- 제목 후보 3개와 태그
- 검증이 필요한 사실 개수, `확인 필요` 표시 위치
- `editor-notes.md`의 "사용자가 판단할 점"
- 다음 할 일
  1. `post.md`를 직접 고친다. 애매한 수정에는 `<!-- 왜: ... -->`, 이 글에만 해당하면 `<!-- 이 글만 -->`
  2. 발행: `scripts/copy_post.sh <작업 폴더>` → 티스토리에서 붙여넣고 카테고리 `AI` 선택 → 비공개 저장 후 확인

블로그에 직접 올리지 않는다. 발행은 항상 사용자가 한다.
