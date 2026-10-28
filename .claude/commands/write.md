---
description: 유튜브 링크로 블로그 글 초안을 만든다 (수집 → 분석 → 설계 → 작성 → 디자인 → 교정 → 독자 테스트)
argument-hint: <유튜브 URL> [추가 요청]
---

유튜브 링크로 블로그 글 초안을 만든다. 규칙은 `blog-style` 스킬, 기준 예시는 `.claude/skills/blog-style/examples/pstack-example.md`.

입력: $ARGUMENTS
(첫 번째 값이 URL, 나머지는 이번 글에 대한 추가 요청이다. 추가 요청은 blog-style보다 우선한다.)

## 1. 수집
```bash
.venv/bin/python .claude/skills/youtube-transcript/scripts/fetch_transcript.py "<URL>"
```
출력 마지막 줄이 작업 폴더다. 같은 영상 폴더에 이미 `post.md`가 있으면 덮어쓰지 말고 사용자에게 먼저 묻는다.

## 2~7. 역할 (서브에이전트를 순서대로, 각자 작업 폴더 경로와 추가 요청을 넘긴다)

| 순서 | 서브에이전트 | 만드는 것 |
|---|---|---|
| 2 | `analyst` (기술 리서처) | `analysis.md` |
| 3 | `curator` (편집장) | `outline.md` |
| 4 | `writer` (숏폼 교육 콘텐츠 작가) | `post.md`, `publish.md` |
| 5 | `designer` (에디토리얼 디자이너) | `post.md` 부품 정리, 필요하면 `images.md` |
| 6 | `editor` (교열 기자) | `post.md` 교정, `editor-notes.md` |
| 7 | `reader` (독자 테스터) | `reader-test.md` |

- editor 전에 자동 검사를 돌리고 결과를 넘긴다: `.venv/bin/python tools/lint_post.py <작업 폴더>`. 교정 후에도 오류가 남으면 editor를 한 번 더 부른다.
- reader 결과가 FAIL이면 writer에게 `reader-test.md`를 주고 한 번 고쳐 쓰게 한 뒤 자동 검사를 다시 돌린다.
- 서브에이전트의 파일 쓰기가 막히면 결과를 텍스트로 받아 메인 세션이 저장한다.

## 8. 기준점 커밋
글은 `posts/` 전용 로컬 저장소에만 커밋한다 (GitHub에 올리지 않음).
```bash
git -C posts add <폴더 이름> && git -C posts commit -m "draft: <제목 후보 1번>"
```

## 9. 보고 (짧게)
- 제목 후보 3개와 태그, 본문 글자 수
- 자동 검사 결과, 독자 테스트 결과, 필요한 이미지 수
- `editor-notes.md`의 "사용자가 판단할 점"
- 다음 할 일: `post.md` 확인·수정 → `sh copy-post` → 티스토리에 붙여넣기(기본모드·HTML 모드) → 이미지 자리 교체 → 비공개 저장 후 확인

블로그에 직접 올리지 않는다.
