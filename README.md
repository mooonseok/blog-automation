# blog-automation

유튜브 링크 하나로 블로그 글 초안을 만드는 Claude Code 프로젝트입니다.

```
/write <유튜브 링크>  →  post.md 직접 수정  →  sh copy-post  →  티스토리에 붙여넣기
```

## 1. 준비물

| 항목 | 용도 | 확인 |
|---|---|---|
| macOS | 클립보드 복사(`pbcopy`) | |
| Python 3.9 이상 | 자막 추출 스크립트 | `python3 --version` |
| Claude Code | `/write` 실행 (CLI, 데스크톱 앱, IDE 어디서든) | |
| git | 버전 기록 | `git --version` |
| GitHub CLI (선택) | 리포 클론·자동 푸시 | `gh auth status` |

## 2. 설치

```bash
gh repo clone mooonseok/blog-automation
cd blog-automation
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

`.venv`는 git에 올라가지 않습니다. 새 컴퓨터에서 클론했다면 아래 두 줄을 다시 실행하세요.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## 3. 글 만들기: `/write`

이 폴더에서 Claude Code를 열고 입력합니다.

```
/write https://www.youtube.com/watch?v=u2oDdU6z4Bw
/write https://youtu.be/u2oDdU6z4Bw 입문자 대상으로, 핵심만 짧게
```

링크 뒤에 적은 말은 이번 글에만 적용되는 추가 요청입니다.

진행 순서는 다음과 같습니다. 역할마다 전문가를 정해 두고 순서대로 넘깁니다.

| 순서 | 역할 | 하는 일 | 만드는 것 |
|---|---|---|---|
| 1 | 수집 (스크립트) | 자막과 영상 정보 | `transcript.md`, `meta.json` |
| 2 | analyst · 기술 리서처 | 자막 보정, 주장·근거·용어 정리 | `analysis.md` |
| 3 | curator · 편집장 | 핵심 1개와 질문 3개 고르기, 버릴 것 정하기, 섹션 설계 | `outline.md` |
| 4 | writer · 숏폼 교육 콘텐츠 작가 | 질문 → 한 줄 답 → 예시 → 한 줄 정리로 작성 | `post.md`, `publish.md` |
| 5 | designer · 에디토리얼 디자이너 | 요약 카드·팁·단계·표 등 부품 배치, 이미지 프롬프트 | `images.md` |
| 6 | 자동 검사 (스크립트) | 메타 문장, 해요체, 긴 문단, 영상 링크 등 검사 | |
| 7 | editor · 교열 기자 | 검사 결과 반영, 문단 쪼개기, 분량 줄이기 | `editor-notes.md` |
| 8 | reader · 독자 테스터 | 영상을 안 본 사람이 글만 읽고 핵심을 맞히는지 확인. 실패하면 writer가 고쳐 씀 | `reader-test.md` |
| 9 | 커밋 (스크립트) | `posts/` 로컬 저장소에 `draft:`로 커밋 | |

결과는 `posts/<날짜>-<영상ID>/` 폴더에 생깁니다. `posts/`는 GitHub에 올라가지 않습니다 ([글 저장 위치와 백업](#글-저장-위치와-백업) 참고).

| 파일 | 내용 |
|---|---|
| `post.md` | **본문**. 직접 고치는 파일 |
| `publish.md` | 카테고리, 제목 후보 3개, 태그 |
| `images.md` | 필요한 이미지와 생성 프롬프트 (있을 때만) |
| `reader-test.md` | 독자 테스트 결과 |
| `editor-notes.md` | 교정 내용과 직접 판단할 점 |
| `outline.md`, `analysis.md` | 글 설계안, 영상 분석 |
| `transcript.md`, `meta.json` | 원본 자막과 영상 정보 |
| `versions/` | 클립보드로 복사한 버전들 (`sh copy-post`가 만듦) |

## 4. 직접 고치기

`post.md`를 편집기로 열어 고칩니다. 아래 주석을 남기면 나중에 문체 학습(`/feedback`, 2단계)에 쓰입니다.
주석은 복사할 때 자동으로 빠지므로 블로그에는 올라가지 않습니다.

| 주석 | 언제 |
|---|---|
| `<!-- 왜: 결론을 먼저 -->` | 고친 이유가 diff만 봐서는 안 보일 때 |
| `<!-- 왜: ... 전체 적용 -->` | 같은 패턴을 글 전체에 적용하라는 뜻 |
| `<!-- 이 글만 -->` | 이 글에만 해당하는 수정 (규칙으로 만들지 않음) |
| `<!-- 좋음: 비유가 딱 맞음 -->` | 마음에 든 부분 |

AI가 남기는 주석도 있습니다.

- `<!-- 확인 필요 -->`: 영상에서만 나온, 아직 확인하지 않은 사실입니다. 확인한 뒤 지우거나 문장을 고치세요
- `<!-- 내 생각: 직접 한두 줄 추가 -->`: 정리 아래 내 의견을 쓸 자리입니다

### 부품 문법

본문의 상자나 단계는 아래 문법으로 쓰면 복사할 때 디자인이 입혀집니다. 자세한 규칙은 `.claude/skills/blog-style/SKILL.md` 5장, 기준 예시는 `examples/pstack-example.md`입니다.

| 부품 | 문법 |
|---|---|
| 한눈에 보기 카드 | `:::summary` 첫 줄=핵심, `- `=체크, `? `=질문, `:::`로 닫기 |
| 한 줄 정리 | `:::takeaway` 한 문장 (`==구절==`은 형광펜) |
| 용어 / 팁 / 주의 | `:::term`, `:::tip`, `:::warn` |
| 인용 | `:::quote 화자` |
| 번호 단계 | `:::steps` 줄마다 `제목 \| 설명` |
| 체크리스트 | `:::checklist` 줄마다 `- 행동` |
| Q 소제목 | `## Q1. 질문?` |
| 이미지 자리 | `[[이미지 1]]` (붙여넣은 뒤 점선 상자를 실제 이미지로 바꿉니다) |

## 5. 클립보드에 복사: `sh copy-post`

터미널에서 이 폴더로 이동해 실행합니다.

```bash
sh copy-post
```

복사하기 전에 자동 검사(`tools/lint_post.py`)를 먼저 돌립니다. 규칙 오류가 있으면 결과를 보여 주고 그래도 복사할지 묻습니다.

**새 글을 처음 복사할 때**는 바로 복사하고 `versions/v1.md`로 저장합니다.

**이미 복사한 글이면** 메뉴가 뜹니다. 엔터만 누르면 1번이 선택됩니다.

```
새 글이 없습니다. 이미 복사한 글: pstack 해부: ... (마지막 v2)
  1) 현재 글 (수정됨 → v3로 저장)
  2) v2  2026-10-28 19:52
  3) v1  2026-10-28 19:52
  o) 다른 글 고르기
  q) 취소
  (엔터 = 1)
```

- **현재 글**: 마지막 버전 이후 고친 게 있으면 다음 버전으로 저장하고 복사합니다. 고친 게 없으면 버전을 올리지 않습니다
- **예전 버전**: 그 버전을 그대로 복사합니다 (새 버전을 만들지 않음)
- **다른 글 고르기**: 전체 글 목록에서 고릅니다

새 버전이 저장되면 `posts/` 로컬 저장소에 `copy: <폴더> vN`으로 자동 커밋합니다. GitHub에는 올리지 않습니다.

특정 글을 바로 지정할 수도 있습니다.

```bash
sh copy-post u2oDdU6z
```

```bash
sh copy-post "https://www.youtube.com/watch?v=u2oDdU6z4Bw"
```

복사가 끝나면 터미널에 제목 후보, 태그, 카테고리가 나옵니다. "확인 필요" 표시가 남아 있으면 해당 줄 번호를 알려 줍니다.

## 6. 티스토리에 붙여넣기

티스토리 Open API가 종료되어 자동 발행은 할 수 없습니다. 마지막 단계는 직접 진행합니다.

1. 블로그 관리 → **글쓰기** 열기 (`https://<블로그 주소>/manage/newpost`)
2. 편집기 오른쪽 위 모드 메뉴(`기본모드`)에서 **HTML** 선택 (권장)
3. 본문 영역에 붙여넣기 (`Cmd + V`)

`sh copy-post`가 만드는 HTML은 **티스토리 자체 서식만** 씁니다. 상자는 티스토리 인용 서식(style1~3), 표는 표 서식(style11), 간격은 빈 문단, 색은 글자색·배경색입니다. 티스토리 편집기는 붙여넣은 HTML의 다른 스타일(배치, 크기, 테두리, 모서리, 그라데이션 등)을 지우기 때문에, 처음부터 살아남는 것만 씁니다. 그래서 **기본모드와 HTML 모드 어디에 붙여넣어도 같은 모양**이 나옵니다. 마크다운 모드에는 붙여넣지 마세요(태그가 글자로 보입니다).

붙여넣기 전에 모양을 보고 싶다면 미리보기를 엽니다. 실제 티스토리 스킨 CSS를 입히고, 티스토리가 지우는 스타일을 미리 지운 페이지라 붙여넣은 결과와 같습니다.

```bash
open posts/<글 폴더>/preview.html
```

이어서 나머지 항목을 입력합니다.


4. **카테고리**: `publish.md`의 카테고리 선택 (현재 기본값 `AI`)
5. **제목**: 터미널에 나온 제목 후보 중 하나를 입력하거나 직접 작성
6. **태그**: 본문 아래 태그 칸에 터미널에 나온 태그 입력
7. **완료** → 공개 설정을 **비공개**로 저장
8. 블로그에서 비공개 글을 열어 표, 코드 블록, 링크가 제대로 보이는지 확인
9. 문제가 없으면 공개로 바꿔 발행

> 붙여넣은 뒤 티스토리 편집기에서 글을 고쳤다면, 같은 내용을 `post.md`에도 반영해 두세요. 그래야 다음 버전과 학습 기록이 어긋나지 않습니다.

### 스킨 CSS 한 번 고치기 (선택)

티스토리는 글 HTML에 넣은 줄바꿈 설정(`word-break`)과 링크 표시 방식을 지웁니다. 블로그 스킨에 한 번만 넣어 두면 모든 글에 적용됩니다.

블로그 관리 → 꾸미기 → 스킨 편집 → html 편집 → CSS 탭의 맨 아래에 붙여넣고 적용합니다.

```css
/* 한글을 단어 단위로 줄바꿈하고, 링크가 통째로 다음 줄로 넘어가지 않게 */
.article-view p, .article-view li, .article-view td { word-break: keep-all; overflow-wrap: break-word; }
.article-view a { display: inline; }
```

## 7. 버전 기록 보기

글의 버전 기록은 `posts/` 저장소에 있으므로 `git -C posts`로 봅니다.

```bash
git -C posts log --oneline -- <글 폴더>
```

- `draft: ...` AI가 만든 초안
- `copy: ... vN` 직접 고쳐서 실제로 복사해 간 버전

둘을 비교하면 직접 고친 부분이 나옵니다.

```bash
git -C posts diff <draft 커밋> <copy 커밋> -- <글 폴더>/post.md
```

## 글 저장 위치와 백업

GitHub 리포에는 **도구만** 올라갑니다. 글은 내 컴퓨터에만 저장됩니다.

| | 도구 리포 (이 폴더) | 글 저장소 (`posts/`) |
|---|---|---|
| 내용 | 스크립트, 스킬, 에이전트, 문서 | 자막, 분석, 본문, 버전 |
| git | GitHub `mooonseok/blog-automation`에 푸시 | 로컬 전용 (원격 없음) |
| 커밋하는 곳 | 도구를 고칠 때 | `/write`(draft), `sh copy-post`(copy vN) |

`posts/`는 도구 리포의 `.gitignore`에 들어 있어서 실수로 올라갈 일이 없습니다.
도구를 새로 클론하면 `posts/`는 비어 있고, 첫 `/write`나 `sh copy-post` 때 자동으로 만들어집니다.

**백업이 필요하다면**, 글 전용 비공개 리포를 따로 만들어 `posts/`에 연결하세요. 연결해 두면 `sh copy-post`가 새 버전을 저장할 때 그 리포로 자동 푸시합니다.

```bash
gh repo create <글 전용 리포 이름> --private --source=posts --push
```

## 8. 문제 해결

| 증상 | 해결 |
|---|---|
| `/write`가 명령으로 인식되지 않음 | 이 폴더에서 Claude Code를 열었는지 확인하세요. 이미 열려 있었다면 새 세션을 여세요 |
| `.venv/bin/python: No such file` | 2번 설치의 `venv`, `pip install`을 실행하세요 |
| 자막을 가져올 수 없음 (종료 코드 2) | 자막이 없는 영상입니다. 음성 인식은 아직 지원하지 않습니다 |
| `HTTP Error 429` | 유튜브 요청 제한입니다. 몇 분 뒤 다시 시도하세요 |
| "여러 글이 일치함" | `sh copy-post`에 폴더 이름을 더 길게 입력하세요 |
| "푸시 실패" (백업 리포를 연결한 경우) | 커밋은 됐습니다. 네트워크와 로그인을 확인한 뒤 `git -C posts push`를 실행하세요 |
| 붙여넣었는데 `<p style=...>` 같은 태그가 글자로 보임 | 마크다운 모드에 붙여넣은 경우입니다. 본문을 모두 지우고 HTML 모드로 바꾼 뒤 다시 붙여넣으세요 |
| 문단 간격이나 표 모양이 미리보기와 다름 | 어떤 부분이 다른지 캡처해서 알려 주세요. `tools/render_post.py`의 `ALLOWED_STYLES`를 조정합니다 |
| 한글이 단어 중간에서 줄바꿈됨 (`새로고침하/니`) | 블로그 스킨의 문제라 글 HTML로는 고칠 수 없습니다. 아래 "스킨 CSS 한 번 고치기"를 참고하세요 |

## 폴더 구조

```
.claude/
  commands/write.md          /write 명령
  agents/                    analyst, writer, editor
  skills/youtube-transcript/ 자막 추출 스크립트
  skills/blog-style/         문체 규칙 (계속 갱신, changelog.md에 기록)
posts/                       글 저장소 (로컬 전용 git, GitHub에 안 올라감)
  <날짜>-<영상ID>/           글 하나당 폴더
copy-post                    클립보드 복사 + 버전 기록
CLAUDE.md                    Claude가 따르는 프로젝트 규칙
```

## Codex에서 쓰기

### 한 줄로 자동 실행: `sh auto`

Codex CLI가 설치돼 있으면, 대화 없이 터미널 명령 하나로 초안을 만들 수 있습니다.

```bash
sh auto "https://www.youtube.com/watch?v=..."
```

```bash
sh auto "https://youtu.be/..." "입문자 대상으로, 핵심만 짧게"
```

3장의 순서를 그대로 자동으로 돌립니다. 역할마다 `codex exec`를 따로 실행해서 역할이 섞이지 않습니다. 진행 상황이 터미널에 단계별로 나오고, 역할별 로그는 글 폴더의 `logs/`에 남습니다. 마지막에 자동 검사와 독자 테스트 결과, 필요한 이미지 수를 알려 줍니다.

Codex는 네트워크가 막히고 `.git`이 읽기 전용인 환경에서 실행되기 때문에, 수집과 커밋은 스크립트가 맡습니다.

**모델과 노력 수준**: 기본값은 `gpt-6-astra`, 노력 수준 `high`입니다. 바꾸려면 명령 앞에 붙입니다.

```bash
CODEX_EFFORT=xhigh sh auto "https://youtu.be/..."
```

```bash
CODEX_MODEL=gpt-6.1-sol CODEX_EFFORT=medium sh auto "https://youtu.be/..."
```

노력 수준은 `low`, `medium`, `high`, `xhigh`, `max`, `ultra` 중에서 고르며, 모델마다 쓸 수 있는 값이 다릅니다. Codex 대화 화면의 기본값까지 바꾸려면 `~/.codex/config.toml`에 `model = "gpt-6-astra"`, `model_reasoning_effort = "high"`를 넣습니다.

처음 한 번만 설치와 로그인이 필요합니다. 로그인은 개인 ChatGPT 계정으로 하면 구독에 포함된 사용량으로 동작합니다.

```bash
npm install -g @openai/codex
```

```bash
codex login
```

### 대화하면서 쓰기

이 리포는 Codex 대화 화면에서도 쓸 수 있습니다. Codex는 `AGENTS.md`(공통 지침)를 자동으로 읽고, `.agents/skills/`의 스킬을 씁니다.

- 글 만들기: `$write-post <유튜브 링크>` (CLI에서 `/skills`로 목록 확인)
- 역할은 `.codex/agents/`의 커스텀 에이전트로 정의돼 있습니다. 역할별로 모델이나 노력 수준을 바꾸려면 해당 `.toml` 파일의 `model`, `model_reasoning_effort`를 고칩니다.
- 처음 옮겨 왔다면 첫 메시지로 "HANDOFF.md와 AGENTS.md를 끝까지 읽어 줘"를 보내세요. 지금까지의 결정과 다음 작업이 정리돼 있습니다.

## 로드맵

- [x] 1단계: 자막 수집, `/write` (분석 → 작성 → 교정), 문체 스킬 초기 버전, `copy-post` 버전 관리
- [ ] 2단계: `/feedback` (수정 내용으로 문체 규칙 학습), researcher 팩트체크 + `claims.json`
- [ ] 3단계: `/audit` 정기 점검, 업데이트 알림
- [ ] 기타: 자막 없는 영상용 음성 인식(Whisper)
