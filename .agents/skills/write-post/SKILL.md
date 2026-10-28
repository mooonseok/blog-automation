---
name: write-post
description: 유튜브 링크로 블로그 글 초안을 만든다 (수집 → 분석 → 설계 → 작성 → 디자인 → 교정 → 독자 테스트 → draft 커밋). 사용자가 유튜브 링크를 주며 블로그 글을 써 달라고 할 때 사용.
---

# write-post

터미널에서 한 번에 돌리려면 `sh auto <유튜브 링크> [추가 요청]`이 같은 일을 한다 (역할마다 `codex exec`를 따로 실행). 대화 중에 직접 진행할 때는 아래 순서를 따른다.

입력: 유튜브 URL과 (선택) 추가 요청. 추가 요청은 `blog-style`보다 우선한다.

## 1. 수집

```bash
.venv/bin/python .claude/skills/youtube-transcript/scripts/fetch_transcript.py "<URL>"
```

출력 마지막 줄이 작업 폴더다. 같은 영상 폴더에 이미 `post.md`가 있으면 덮어쓰지 말고 사용자에게 먼저 묻는다.

## 2~7. 역할

역할마다 `.codex/agents/<역할>.toml`의 커스텀 에이전트를 쓰거나, 서브에이전트를 쓸 수 없으면 `.claude/agents/<역할>.md`를 처음부터 끝까지 읽고 그 역할로서 직접 수행한다. 앞 역할의 판단을 다음 역할에 섞지 않는다.

| 순서 | 역할 | 만드는 것 |
|---|---|---|
| 2 | analyst (기술 리서처) | `analysis.md` |
| 3 | curator (편집장) | `outline.md` |
| 4 | writer (숏폼 교육 콘텐츠 작가) | `post.md`, `publish.md` |
| 5 | designer (에디토리얼 디자이너) | 부품 정리, 필요하면 `images.md` |
| 6 | editor (교열 기자) | `post.md` 교정, `editor-notes.md` |
| 7 | reader (독자 테스터, `post.md`만 읽음) | `reader-test.md` |

- editor 전에 `.venv/bin/python tools/lint_post.py <작업 폴더>`를 돌려 결과를 넘긴다. 오류가 남으면 editor를 한 번 더.
- reader가 FAIL이면 writer가 한 번 고쳐 쓰고 다시 검사한다.

## 8. 기준점 커밋

```bash
git -C posts add <폴더 이름> && git -C posts commit -m "draft: <제목 후보 1번>"
```

workspace-write 샌드박스에서 `.git`이 읽기 전용이면 커밋 명령을 사용자에게 안내한다.

## 9. 보고 (한국어로 짧게)

제목 후보, 본문 글자 수, 자동 검사·독자 테스트 결과, 필요한 이미지 수, 다음 할 일 (`sh copy-post` → 티스토리에 붙여넣기, 기본모드·HTML 모드 모두 가능).
