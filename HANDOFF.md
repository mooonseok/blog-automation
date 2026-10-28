# 인수인계: blog-automation

이 문서는 Claude Code에서 진행하던 작업을 Codex(또는 다른 에이전트)로 옮기기 위한 인수인계 문서입니다.
2026-10-28 하루 동안의 대화에서 나온 요구사항, 결정, 현재 상태, 다음 작업을 모두 담았습니다. 마지막 갱신: 주인공 설명 필수 규칙과 `-6` 결과까지.

## 0. 사용법

Codex에서 이 리포를 열고 첫 메시지로 아래를 보내세요.

```
HANDOFF.md와 AGENTS.md를 끝까지 읽어 줘. 읽은 뒤 "4. 현재 상태"와 "7. 로드맵"을 한국어로 요약하고,
다음에 무엇을 할지 제안해 줘.
```

- 공통 지침은 `AGENTS.md`입니다. Codex는 이 파일을 자동으로 읽습니다.
- 스킬은 `.agents/skills/`에 있습니다. `blog-style`과 `youtube-transcript`는 `.claude/skills/`를 가리키는 링크라 내용이 같습니다.
- 글쓰기 파이프라인은 터미널에서 `sh auto <유튜브 링크>`(권장), 대화 중에는 `$write-post` 스킬입니다.
- 역할 6개는 `.codex/agents/*.toml`(Codex 커스텀 에이전트)이고, 각자 `.claude/agents/<역할>.md`를 읽습니다.

---

## 1. 사용자와 목표

- 블로그: https://moonesok.tistory.com (티스토리, 스킨 Odyssey). 글은 `AI` 카테고리에 올립니다. 2026-10-28 당시 이 카테고리의 글은 0개였습니다.
- GitHub: `mooonseok` (o가 3개). 도구 리포는 `mooonseok/blog-automation` (비공개).
- 사용하던 Claude 계정은 회사 계정이고, 사용자는 곧 퇴사합니다. 그래서 이 문서를 만들었습니다.

처음 요청한 세 가지 목표는 다음과 같습니다.

1. 유튜브 링크를 주면 영상 내용을 분석해서 블로그 글 한 편으로 만든다.
2. 글쓰기 스킬로 사람이 읽기 좋은 글을 만들고, 그 스킬을 내 취향에 맞게 계속 고쳐 나간다. 처음엔 남의 스킬을 빌려 오고 점점 바꾼다.
3. 웹 검색으로 팩트체크를 하고, 지금 글이나 예전 글에 빠진 내용이나 업데이트할 내용이 있으면 알림을 받는다.

## 2. 사용자 선호 (반드시 지킬 것)

| 항목 | 선호 |
|---|---|
| 답변 언어 | **무조건 한국어.** 짧은 상태 알림·중간 보고까지 예외 없음. 여러 번 어겨서 지적받았다 |
| 문서 어투 | README 같은 사용자용 문서는 `~합니다` 체 |
| 블로그 어투 | 평서체 `~다`. 해요체 목업을 보고도 평서체로 결정 (2026-10-28) |
| 글의 성격 | 요약이 아니라 **재창조**. 사람이 쓴 것처럼, 숏폼처럼 슥슥 읽히되 **공부가 되는** 글. 사용자 본인도 이 글로 공부한다 |
| 주인공 설명 | **영상의 주인공(예: pstack)이 무엇이고 어떻게 동작하는지는 반드시 설명.** 짧게 줄이다가 주인공 설명을 빼고 일반론으로 바꾼 글에 "pstack이 뭔지 전혀 파악 못 하겠다"는 피드백을 받았다 |
| 설명 방식 | 흥미로운 질문을 먼저 던지고, 설명하고, 예시나 비유로 빠져들게 |
| 분량 | 초기 초안(1만~2만 자)은 너무 길었고, 1,700자대 글은 주인공 설명이 부족했다. 지금 기준은 본문 1,800~3,500자 |
| 문단 | 문단 사이는 한 줄씩 띄운다. 마지막 한 줄만 따로 떨어지는 식의 들쭉날쭉한 줄바꿈은 싫다 |
| 링크 | 영상 링크·타임스탬프 링크는 넣지 않는다. `@핸들`이나 특수문자는 이름에 링크를 거는 편이 낫다 |
| 의미 없는 정보 | "영상 기준 pstack 0.15.28의 구성은 다음과 같다" 같은 내부 정보는 빼 달라 |
| 서식 | 인용 등 티스토리 서식을 다양하게. "연한 파란 배경+굵은 왼쪽 선+회색 글자" 인용 상자는 매우 싫어함. 붙여넣었을 때 깨지는 디자인은 절대 안 됨 |
| 쓸데없는 말 | 출처의 "현재 배포본의 동작은 별도로 확인하지 않았다" 같은 작성 과정·검증 여부 메타 문장 절대 금지 |
| 모델 | `sh auto`는 Codex `gpt-6-astra`, 노력 수준 `high` |
| 긴 설명 | 피치 못하게 길어지면 도식이나 이미지로. 이미지는 생성 프롬프트를 보여 주면 사용자가 직접 생성한다 |
| 저장 | 글은 GitHub에 올리지 않는다. 도구만 올린다 |
| 발행 | 사용자가 직접 한다. 비공식 업로드는 하지 않는다 |
| 위험한 작업 | 강제 푸시·기록 재작성 등은 확인을 받고 한다 (실제로 확인 후 진행했음) |

## 3. 지금까지의 경과 (시간순)

1. **설계**: 역할을 수집, 분석, 팩트체크, 작성, 교정, 감시로 나눴습니다. Claude Code의 스킬, 서브에이전트, 슬래시 명령, 예약 작업으로 구성하는 안을 도식으로 보여 드리고 3단계 로드맵을 합의했습니다.
2. **수정 방식에 관한 질문**: 초안을 직접 고칠 때 학습이 잘 되게 하는 방법을 정리했습니다(4장 주석 규칙). 핵심은 "왜 고쳤는지"를 남기는 것입니다.
3. **티스토리 API 조사**: 공식 Open API는 글쓰기를 포함해 종료됐습니다. 비공식 세션 방식은 쓰지 않기로 하고, 클립보드에 복사해 붙여넣는 방식으로 정했습니다.
4. **1단계 구현**:
   - 자막 수집 스크립트: youtube-transcript-api를 쓰고, 실패하면 yt-dlp로 넘어갑니다.
   - `/write` 명령과 analyst, writer, editor 에이전트를 만들었습니다.
   - `blog-style` 스킬은 일반 한국어 글쓰기 원칙에 예전 블로그 말투를 반영해 시작했습니다.
5. **첫 글**: 김플립 - LLM 코딩 채널의 「요즘 자꾸 뜨는 pstack 어설프게 말고 제대로 파헤쳐 보기」(https://www.youtube.com/watch?v=u2oDdU6z4Bw)로 초안을 만들었습니다.
6. **`sh copy-post`**:
   - 인자 없이 실행하면 가장 최근 글을 복사합니다.
   - 복사할 때마다 버전(v1, v2…)을 저장하고 커밋합니다.
   - 이미 복사한 글이면 메뉴에서 현재 글, 예전 버전, 다른 글 중에 고릅니다.
7. **README**: 설치부터 붙여넣기까지 정리했습니다. 어투는 `~합니다`로, 소개 문구는 "블로그 글"로 바꿨습니다.
8. **글을 GitHub에서 분리**:
   - `posts/`를 `.gitignore`에 넣고 별도 로컬 git 저장소로 만들었습니다.
   - 사용자 승인을 받고 GitHub 기록에서 글을 지운 뒤 강제 푸시했습니다. 예전 커밋 `47d54e5`는 ID로 직접 열면 GitHub 캐시에 한동안 남아 있을 수 있습니다.
9. **같은 영상으로 두 번째 초안**: `posts/2026-10-28-u2oDdU6z4Bw-2`에 만들었습니다.
10. **프로젝트 이동**: 임시 폴더에서 `~/blog-automation`으로 옮겼습니다. `.git`, `.claude`, `posts/.git`, `.venv`는 직접 복사하거나 다시 만들었습니다. `copy-post`가 `-2` 폴더를 최근 글로 못 잡던 정렬 버그도 고쳤습니다.
11. **가독성 1차 개편**:
    - 사용자 피드백: 링크가 다음 줄로 넘어감, 문단 간격 없음, 표가 허접함, 영상 링크 불필요, 핵심이 안 보임.
    - 원인은 티스토리 스킨 CSS였습니다(6장).
    - 글쓰기 가이드 14개를 조사해서 `blog-style`을 다시 썼습니다. 출처는 `.claude/skills/blog-style/references.md`에 있습니다.
    - `tools/render_post.py`를 만들었습니다. 인라인 스타일 HTML을 만들고 미리보기 페이지도 만듭니다.
12. **붙여넣기 시행착오**:
    - 처음엔 HTML 소스를 글자로만 복사해서, HTML 모드가 아닌 곳에 붙여넣으면 태그가 그대로 보였습니다. 그래서 클립보드에 서식(HTML)과 소스(텍스트)를 함께 넣도록 바꿨습니다.
    - 사용자가 기본모드로 붙여넣은 결과, 티스토리가 인라인 스타일을 모두 지웠습니다. 이게 2차 개편(5장)의 계기입니다.
13. **2차 개편안 제시 (승인 대기 중)**: 5장 전체입니다. 이 문서를 만든 시점에 사용자는 개편안을 보고 이미지 프롬프트 기능을 추가로 요청한 상태였고, 아직 구현은 시작하지 않았습니다.
14. **Codex 이전 준비**: 이 문서, `AGENTS.md`, `.agents/skills/write-post`를 만들었습니다. 실수로 커밋된 이미지(`output/`)는 사용자 승인을 받아 GitHub 기록에서 지웠습니다.
15. **스크립트만으로 실행**: 사용자는 "1번 방식(CLI를 스크립트에서 호출)"을 Codex로 하기로 정했습니다.
    - 그래서 `sh auto <링크> [추가 요청]`을 만들었습니다. 수집과 커밋은 스크립트가 하고, 분석·작성·교정은 `codex exec --sandbox workspace-write`가 합니다.
    - 이 컴퓨터에는 Codex CLI가 없어서, 가짜 `codex`로 흐름(새 폴더 번호 매기기, 인자 전달, 결과 확인, 커밋, 실패 처리)만 시험했습니다. **실제 Codex로 끝까지 돌려 본 적은 아직 없습니다.**

16. **3차 개편 (구현 완료)**: 사용자가 Codex로 만든 글(`-3`)을 올려 보고 지적한 것들을 반영했습니다.
    - 지적: 인용 디자인이 별로다(연파랑 배경+굵은 왼쪽 선+회색 글자), 글이 뭉텅이로 보인다, 문단 사이 빈 줄이 없다, 출처에 "현재 배포본의 동작은 별도로 확인하지 않았다" 같은 쓸데없는 말이 있다, 숏폼처럼 슥슥 읽히면서 공부가 되는 글이어야 한다.
    - 조사: 인용·박스 디자인(토스, 요즘IT, Next.js, GitHub 알림, Notion, Stripe, 브런치)과 인기 블로그 문체(뉴닉, 토스, 요즘IT, velog, GeekNews, 향로, 브런치 등 9곳). 결론은 "말투보다 문단 길이와 빈 줄", "blockquote는 스킨이 글자를 회색으로 강제하므로 div로".
    - 결정: 말투는 평서체 `~다` (사용자 선택), 요약은 흰 카드+라벨 칩(A안), 인용은 큰따옴표.
    - 구현: 부품 문법(`:::summary` 등)과 새 디자인의 `render_post.py`, 빈 줄은 티스토리 빈 문단, `lint_post.py` 자동 검사, `blog-style` 재작성(재창조·네 박자·Q 소제목·1~2문장 문단·1,000~2,500자), 역할 6개(curator·designer·reader 신규), `sh auto` 역할별 `codex exec` 실행(기본 `gpt-6-astra`/`high`), `.codex/agents/*.toml`, 기준 예시 `examples/pstack-example.md`.
    - 이 덕분에 5장의 2차 개편안 대부분이 구현됐습니다. 남은 것은 5-7의 6번(사용자가 실제 티스토리에서 새 디자인 확인)입니다.

17. **실제 Codex 실행 1회차 (`-4`)**: `sh auto`가 역할 6개를 실제로 돌려 12분 8초 만에 완성. 자동 검사 오류 0개, 독자 테스트 통과.
18. **디자인 재설계: 티스토리 자체 서식만 사용**: 사용자가 `-4`를 붙여넣자 flex 배치·원형 번호·테두리·그라데이션 형광펜이 모두 지워지고 글자색·배경색만 남음 ("좃같은 디자인"이라는 강한 피드백).
    - 발행된 티스토리 글들의 HTML을 조사: 살아남는 인라인 스타일은 `color`, `background-color`, `text-align` 정도. 나머지는 티스토리 자체 서식(`data-ke-*`).
    - `render_post.py`를 다시 만듦: 요약·팁·주의·용어 = 인용 style3 박스, 한 줄 정리 = 인용 style1(가운데 따옴표), 발언 인용 = style2(세로선), 번호 단계 = ①② 문단, 표 = style11, 형광펜 = 배경색. 부품 문법은 그대로.
    - `sanitize()`가 허용 목록(`ALLOWED_STYLES`) 밖의 스타일을 지워서 **미리보기 = 실제 결과**, 기본모드·HTML 모드 결과 동일.
    - 한글이 단어 중간에서 줄바꿈되는 문제는 스킨 CSS로만 고칠 수 있어 README에 스킨 CSS 안내를 넣음 (사용자가 적용했는지는 미확인).
19. **주인공 설명 필수 (`-6`)**: `-4`가 "검증 습관" 일반론으로 빠져 pstack 설명이 없다는 피드백.
    - blog-style에 "주인공 설명" 원칙과 Q1 고정(`<주인공>은 무엇이고 어떻게 동작할까?`) 및 필수 요소(한 줄 정의, 왜 생겼나, 구성 요소, 동작 흐름 :::steps, 비교, 한 줄 정리) 추가. 분량 1,800~3,500자.
    - curator는 설계안 맨 앞에 "주인공" 섹션, editor는 Q1 필수 요소를 자르지 않음, reader는 주인공을 설명 못 하면 FAIL. 기준 예시 Q1 재작성.
    - 실제 Codex 2회차: 20분 48초, 오류 0개, 독자 테스트 통과, 본문 2,413자. 사용자가 확인 후 만족("굿").
20. **한국어 규칙 강화**: 답변이 자꾸 영어로 새어 나가 `~/.claude/CLAUDE.md`(전역, 새로 만듦)와 프로젝트 `CLAUDE.md` 맨 위에 "답변은 무조건 한국어" 규칙을 넣음.

21. **디자인 스킬 설치와 적용**: 쇼츠(게으른빌더, 「무조건 설치해야하는 클로드 디자인 스킬」)가 소개한 5개를 분석·확인 후 전역 설치 (`~/.agents/skills`, `~/.claude/skills`에 링크). 사용자가 "설치 위치: 전역"을 선택.
    - taste-skill(design-taste-frontend), web-design-guidelines, agent-browser(+CLI·Chrome), screenshot-to-code, awesome-design-md(파일 모음 + 직접 만든 SKILL.md)
    - 적용: README의 mermaid 흐름도("말도 안 되게 허접")를 `docs/make_pipeline_svg.py`가 만드는 라이트·다크 SVG로 교체, agent-browser로 렌더링 확인. web-design-guidelines로 블로그 HTML을 검사해 둥근따옴표 변환과 캡션 색 대비(#6b7684) 반영.
    - **im-not-ai(humanize-korean, 한국어 AI 티 제거, MIT)**: 사용자가 설치를 원했으나 이 세션의 권한 설정이 외부 코드 설치를 막아 미설치. 설치 명령: `npx skills add epoko77-ai/im-not-ai -s '*' -g -a claude-code codex -y`. 설치 후 editor 단계에 연결할지는 사용자와 정할 일 (스킬이 작업 폴더에 `_workspace/`를 만든다).

## 4. 현재 상태

### 리포와 파일

```
~/blog-automation/                 도구 리포 → GitHub mooonseok/blog-automation
  AGENTS.md / CLAUDE.md            공통 지침 / Claude용 (AGENTS.md를 불러옴)
  HANDOFF.md                       이 문서
  README.md                        사용자용 사용법 (합니다체)
  auto                             sh auto <링크>: 수집 → 역할 6개를 codex exec로 차례로 → 검사 → draft 커밋
  copy-post                        sh copy-post: 자동 검사 → HTML로 복사 + 버전 기록
  tools/render_post.py             마크다운(+부품 문법) → 티스토리 자체 서식 HTML (+ --preview)
  tools/lint_post.py               blog-style 규칙 자동 검사
  tools/set_clipboard_html.js      클립보드에 HTML·텍스트 두 형식 넣기 (macOS)
  requirements.txt                 yt-dlp, youtube-transcript-api, markdown
  .claude/skills/blog-style/       문체 규칙 (SKILL.md, references.md, changelog.md, examples/)
  .claude/skills/youtube-transcript/  자막 추출
  .claude/agents/                  역할 6개: analyst, curator, writer, designer, editor, reader
  .codex/agents/                   Codex 커스텀 에이전트 (gpt-6-astra/high, 위 역할 파일을 읽음)
  .claude/commands/write.md        Claude Code용 /write
  .claude/launch.json              미리보기 서버 설정 (python http.server 8765)
  .agents/skills/                  Codex용 (blog-style·youtube-transcript는 링크, write-post는 Codex 전용)
  posts/                           글 저장소 (로컬 전용 git, GitHub에 없음)
```

### 글 (`posts/`)

| 폴더 | 제목 후보 1 | 상태 |
|---|---|---|
| `2026-10-28-u2oDdU6z4Bw` | pstack 해부 | 1차 개편 규칙. 현재 규칙으로는 오류 7개 (예전 형식) |
| `-2` | pstack 정리 | 예전 규칙. 오류 32개, 약 9,400자. 사용자가 기본모드로 올려 본 글 |
| `-3` | pstack의 핵심은 완료를 증명하는 절차다 | 첫 `sh auto` 결과. 인용 블록·메타 문장 등 오류 6개 |
| `-4` | AI가 고쳤다는 버그, 같은 조작으로 다시 확인하자 | 3차 개편 첫 실제 실행. 오류 0개지만 pstack 설명 부족 |
| `-5` | AI가 고쳤다는 버그, pstack은 어떻게 확인할까? | 사용자가 직접 실행한 것으로 보임. 오류 0개 |
| `-6` | pstack은 AI에게 어떻게 일하도록 요구할까? | **현재 기준 결과물.** 오류 0개, 독자 테스트 통과, Q1에서 pstack 정의·구성·동작 설명. 사용자가 v1 복사함 |

`-6` 이전 글은 규칙을 다듬는 과정의 기록입니다. 필요 없으면 지워도 되지만, 지우기 전에 사용자에게 확인합니다.

### 현재 blog-style의 핵심 (파일 기준, 자세한 건 SKILL.md)

- 평서체 `~다`, 문단 1~2문장(최대 3), 문단마다 빈 줄, 본문 1,800~3,500자
- 고정 템플릿: 도입 훅 → `:::summary` → **Q1 주인공 설명(필수 요소)** → Q2·Q3(질문 → 굵은 한 줄 답 → 설명·예시 → `:::takeaway`) → `## 오늘부터 바로 써먹기` + `:::checklist` → 마무리 → `## 출처` 한 줄
- 부품 문법: `:::summary`, `:::takeaway`, `:::term`, `:::tip`, `:::warn`, `:::quote 화자`, `:::steps`(`제목 | 설명`), `:::checklist`, `## Q1.`, `[[이미지 N]]`. `>`·`---` 금지
- S0(절대 금지): 작성 과정·검증 여부 메타 문장. 영상·타임스탬프 링크 금지. 사람·저장소는 확인된 주소로 이름에 링크
  - 확인한 주소: Lauren Tan = https://github.com/poteto, gstack = https://github.com/garrytan/gstack, pstack = https://github.com/cursor/plugins/tree/main/pstack
- 기준 예시: `.claude/skills/blog-style/examples/pstack-example.md` (+ `images.md`)

## 5. 2차 개편안 (3차 개편에서 대부분 구현됨, 기록용)

### 5-1. 새 파이프라인

```
1. 수집 (유지)           자막과 영상 정보
2. 분석 (변경)           주장 + 독자가 궁금해할 질문
3. 선별 (신규)           핵심 1개 + 포인트 3개만
4. 재창조 설계 (신규)    포인트마다 질문 훅·예시 정하기, 이미지 후보 정하기
5. 작성 (변경)           2~3천 자, 말 거는 문체, images.md 작성
6. 자동 검사 (신규)      링크·길이·문단 규칙 → 실패하면 5로
7. 독자 테스트 (신규)    처음 본 사람이 핵심을 맞히나 → 실패하면 5로
8. 변환 (변경)           티스토리 기본 서식 HTML
```

### 5-2. 섹션 하나의 네 박자 (재창조의 핵심)

| 박자 | 역할 | pstack 글에 적용한 예 |
|---|---|---|
| 질문 훅 | 궁금증부터 | AI가 "다 됐어요"라고 할 때, 정말 된 걸까? |
| 설명 | 답을 짧게 | pstack은 증거 없이는 일을 끝내지 못하게 순서를 강제한다 |
| 예시·비유 | 익숙한 장면으로 | "끝났어요"라는 신입에게 "눌러 봤어?"라고 묻는 깐깐한 선배 |
| 한 줄 정리 | 인용 상자로 | 끝의 기준을 "썼다"에서 "확인했다"로 바꾸는 도구 |

경험을 지어내지는 않습니다. 사람다운 글은 질문과 일상적인 비유로 만들고, 사용자 경험이 들어갈 자리는 `<!-- 내 생각 -->`으로 남깁니다.

### 5-3. 지금과 바꾼 뒤 비교

| 항목 | 지금 | 바꾼 뒤 |
|---|---|---|
| 목표 | 영상 내용을 빠짐없이 요약 | 핵심 1개와 포인트 3개만 골라 재창조 |
| 분량 | 약 1만2천~2만2천 자 (마크다운 기준) | 2,000~3,000자 (5분 안에 읽힘) |
| 선별 기준 | 분석 결과를 거의 다 반영 | "그래서 독자에게 뭐가 좋은가?"를 통과한 것만 넣음. 버전 번호, 구성 개수, 내부 설정은 빼고 `analysis.md`에만 남김 |
| 설명 방식 | 정보 나열 | 질문 훅 → 설명 → 예시·비유 → 한 줄 정리 |
| 말투 | 요약 보고서 ("화자는 ~라고 본다" 반복) | 독자에게 말을 거는 블로그체. 출처는 도입에서 한 번만 밝힘 |
| 링크 | 규칙에만 있어서 어기기도 함 | 자동 검사가 막음 |
| 문단 간격 | 인라인 스타일 (기본모드에서 지워짐) | 티스토리 방식의 빈 줄 `<p data-ke-size="size16">&nbsp;</p>` |
| 서식 | 직접 만든 박스와 표 | 티스토리 기본 서식 (5-5) |
| 긴 설명 | 글로 길게 | 도식·이미지로 대체하고 생성 프롬프트 제공 (5-6) |
| 검증 | editor 체크리스트 | 자동 검사 스크립트와 독자 테스트 |

### 5-4. 파일별 변경

| 파일 | 변경 |
|---|---|
| `blog-style/SKILL.md` | "재창조" 장(네 박자, 질문 훅·비유 고르는 법, 좋은 예와 나쁜 예), 분량 상한, "쓰지 않을 것" 목록, 티스토리 서식 사용 규칙, "시각 자료" 장 |
| `analyst.md` | 마지막에 **글 설계안** 추가: 핵심 1개, 포인트 3개, 포인트마다 질문 훅과 예시 후보, 이미지 후보, 뺀 내용과 이유 |
| `writer.md` | 설계안만 보고 씀. 자막을 다시 뒤져 덧붙이지 않음. 2~3천 자 상한. `<!-- 이미지 N -->` 표시와 `images.md` 작성 |
| `editor.md` | 자르는 역할 추가: 상한을 넘으면 덜 중요한 문단부터 삭제 |
| `tools/lint_post.py` (신규) | 기계적 검사: 유튜브·타임스탬프 링크, 맨 URL·`@핸들`, 글자 수, 한 문장짜리 문단, 문단당 굵은 글씨 수, 이미지 표시와 `images.md` 항목 수 일치, 이미지 3개 이상 |
| 독자 테스트 (신규 단계) | 맥락 없는 에이전트(또는 새 세션)에게 글만 보여 주고 핵심을 물어 요약 상자와 맞는지 확인 |
| `tools/render_post.py` | 인라인 스타일을 버리고 티스토리 기본 서식으로 출력. 미리보기에서만 이미지 자리를 회색 박스로 표시 |
| `copy-post` | 필요한 이미지 수와 위치 안내 |
| `write.md` / `write-post` 스킬 | 단계 3, 4, 6, 7 추가 |

### 5-5. 티스토리 기본 서식 (스킨 `content.css`에 정의된 것)

| 서식 | 마크업 | 쓰임 |
|---|---|---|
| 문단 | `<p data-ke-size="size16">` | 본문 |
| 빈 줄 | `<p data-ke-size="size16">&nbsp;</p>` | 문단 사이 |
| 인용 style1 | `<blockquote data-ke-style="style1">` | 화자의 말 인용 (큰따옴표) |
| 인용 style2 | `<blockquote data-ke-style="style2">` | 한 줄 정리 (세로선) |
| 인용 style3 | `<blockquote data-ke-style="style3">` | 핵심 요약 상자 (박스) |
| 구분선 | `<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style1~8">` | 큰 주제 전환 |
| 표 | `<table data-ke-style="style1~16">` | 비교 |
| 접은글 | `data-ke-type="moreLess"` | 부가 정보 |
| 글자 크기 | `data-ke-size="size14/16/18"` | 크기 조절 |

정확한 마크업(특히 접은글과 구분선)은 티스토리 편집기에서 해당 서식을 하나 넣고 HTML 모드로 바꿔 확인한 뒤 맞춥니다. 실제 마크업은 아직 확인하지 않았습니다.

### 5-6. 이미지 프롬프트 기능

- **만드는 조건 (글당 최대 2개)**: 4단계 이상의 순서나 흐름, 층이나 계층 구조, 글로 풀면 3문단이 넘는 관계. 단순 비교는 표, 3개 이하 나열은 목록으로 씁니다. 이미지가 없어도 글만으로 이해돼야 합니다.
- **흐름**:
  1. 설계 단계에서 이미지 후보를 정합니다.
  2. 작성 단계에서 본문에 `<!-- 이미지 N -->` 표시를 남기고 `images.md`를 씁니다.
  3. `sh copy-post`가 필요한 이미지와 위치를 안내합니다.
  4. 사용자가 이미지를 생성해 티스토리의 해당 자리에 넣습니다.
- **공통 이미지 스타일**: 플랫 벡터, 파란 계열, 흰 배경, 글자 없음. 이미지 생성 도구가 한글을 자주 깨뜨리므로 글자는 캡션으로 씁니다. 이 스타일을 `blog-style`에 두고 모든 프롬프트에 붙입니다.
- **`images.md` 형식**:

```markdown
## 이미지 1: 하네스 5층 구조
- 위치: "반복하는 잔소리는 더 강한 층에 넣는다" 섹션, 목록 바로 아래
- 목적: 아래층일수록 규칙이 강하게 지켜진다는 것을 한눈에
- 비율: 16:9 (1200×675)
- 대체 텍스트: 코드베이스부터 스타일 가이드까지 다섯 층으로 쌓인 하네스 구조
- 프롬프트 (영문): Flat vector illustration of a five-layer stacked pyramid, viewed slightly
  from the side. The bottom layer is the widest and darkest blue, each layer above gets narrower
  and lighter. Small simple icons on each layer: building blocks, a magnifying glass, a document
  with rules, a wrench, a style palette. Clean white background, soft shadows, modern tech blog
  style, no text.
- 프롬프트 (한글 설명): 옆에서 비스듬히 본 5층 피라미드. 아래층일수록 넓고 진한 파랑…
- 캡션: 아래층일수록 강하다 — 1 코드베이스, 2 린트, 3 규칙 파일, 4 스킬, 5 스타일 가이드
```

### 5-7. 진행 순서 (승인 후)

1. `blog-style/SKILL.md` 개편: 재창조, 분량, 쓰지 않을 것, 티스토리 서식, 시각 자료
2. `analyst.md`, `writer.md`, `editor.md`, `/write`, `write-post` 갱신
3. `tools/lint_post.py` 작성. `copy-post`에서 복사 전에 실행하고 경고를 보여 줌
4. `tools/render_post.py`를 티스토리 기본 서식 출력으로 변경. 미리보기 유지
5. pstack 글을 처음부터 다시 씀. 기존 두 폴더는 그대로 두고 새 폴더나 새 draft 커밋으로 만듦
6. 미리보기와 `images.md`를 보여 주고, 사용자가 HTML 모드로 붙여넣어 실제 화면 확인

## 6. 알아 둘 기술 사항

### 티스토리 스킨 CSS 때문에 생긴 문제

| 증상 | 원인 |
|---|---|
| 문단 간격이 없음 | 블로그 설정의 "문단 여백 제거": `.tt_article_useless_p_margin p { margin: 0 !important }` |
| 링크가 통째로 다음 줄로 넘어감 | `.article-view a { display: inline-block }` |
| 단어 중간에서 줄바꿈 | `.article-view ul li, ol li { word-break: break-all }` |
| 기본모드 붙여넣기 시 스타일 사라짐 | 티스토리 편집기가 인라인 스타일을 지움 (사용자 화면으로 확인) |

CSS 주소는 `tools/render_post.py`의 `TISTORY_CSS`에 있습니다. 미리보기는 이 CSS를 실제로 불러와서 블로그와 같은 조건으로 보여 줍니다.

### 붙여넣기와 디자인 제약 (가장 중요)

티스토리 편집기는 붙여넣은 HTML에서 인라인 스타일 대부분을 지웁니다. 살아남는 것은 `color`, `background-color`, `text-align` 정도이고, 상자·표·간격은 티스토리 자체 서식(`data-ke-*`)으로만 만들 수 있습니다.

- **새 디자인을 추가할 때는 이 제약 안에서만** 만든다. `display`, `flex`, `border`, `border-radius`, `margin`, `padding`, `width/height`, `linear-gradient`, `box-shadow`, `word-break` 등은 지워진다.
- `render_post.py`의 `ALLOWED_STYLES`와 `sanitize()`가 이 제약을 강제한다. 미리보기에서 보이는 것이 곧 실제 결과다.
- 쓸 수 있는 자체 서식: 인용 `blockquote data-ke-style="style1~3"`, 표 `data-ke-style="style1~16"`(지금 style11), 구분선 `hr data-ke-style`, 문단·제목 크기 `data-ke-size`, 접은글 `moreLess`.

| 모드 | 결과 |
|---|---|
| 기본모드 | 미리보기와 같음 |
| HTML 모드 | 미리보기와 같음 |
| 마크다운 모드 | HTML 태그가 글자로 보임. 쓰지 않음 |

### 기타

- 한국어 자동 자막은 오인식이 많습니다. analyst가 `meta.json`의 설명란(제작자가 쓴 챕터와 링크)으로 고유명사를 보정합니다.
- yt-dlp로 자막을 받을 때 언어 하나가 429 오류로 실패하면 다른 언어가 막히지 않도록 언어별로 따로 요청합니다.
- `pbcopy`는 UTF-8 로케일을 지정해야 한글이 깨지지 않습니다 (`LC_ALL=en_US.UTF-8`).
- Claude Code에서는 analyst 서브에이전트의 파일 쓰기가 하네스에 막혀, 메인 세션이 받아서 저장했습니다. Codex에는 해당하지 않습니다.
- 미리보기: `open posts/<폴더>/preview.html`. 또는 `python3 -m http.server 8765`를 띄운 뒤 브라우저로 엽니다.
- 한글이 단어 중간에서 줄바꿈되는 건 스킨 문제라 글 HTML로는 못 고친다. README의 "스킨 CSS 한 번 고치기" 참고.
- `sh auto` 한 번에 12~21분 걸린다 (역할 6개, gpt-6-astra/high). 역할별 로그는 글 폴더의 `logs/`.

## 7. 아직 하지 않은 것 (로드맵)

- [x] 2차·3차 개편: 재창조, 부품 디자인, 역할 6개, 자동 검사, 독자 테스트, 주인공 설명 필수
- [ ] `-6` 글을 실제 티스토리에 붙여넣은 모양 확인 (새 디자인으로는 아직 사용자 확인 전)
- [ ] 다른 영상으로도 `sh auto` 실행해 보기 (지금까지 pstack 영상 하나로만 검증)
- [ ] im-not-ai(humanize-korean) 설치 후 editor 단계에 한국어 윤문으로 연결할지 결정
- [ ] `/feedback`: `draft`와 `copy vN`의 차이, 사용자 주석으로 `blog-style` 규칙 학습. 후보 규칙은 2~3편에서 반복될 때만 확정
- [ ] researcher 팩트체크와 `claims.json`
- [ ] `/audit`: 정기적으로 예전 글을 재검증하고 빈 주제를 찾아 알림
- [ ] 자막 없는 영상용 음성 인식(Whisper)

## 8. 퇴사 전 점검 목록

- [ ] **`posts/` 백업**: 글은 이 컴퓨터에만 있습니다. 회사 노트북이라면 반드시 옮기세요. 예: 개인 비공개 리포를 만들어 연결합니다. 연결해 두면 `sh copy-post`가 새 버전을 자동으로 푸시합니다.
  ```bash
  gh repo create <글 전용 리포 이름> --private --source=posts --push
  ```
- [ ] **개인 컴퓨터로 옮기기**:
  ```bash
  gh repo clone mooonseok/blog-automation
  ```
  옮긴 뒤 `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`를 실행합니다. `posts/`는 위 백업 리포에서 `posts/` 폴더로 클론합니다.
- [ ] **Codex CLI 설치와 로그인 (개인 계정)**: `npm install -g @openai/codex` 후 `codex login`. 그다음 `sh auto <링크>`로 첫 실행을 해 보고, 실패하면 글 폴더의 `logs/`를 확인합니다.
- [ ] **git 설정**: 이 컴퓨터의 전역 git 설정은 회사 계정입니다. 도구 리포는 로컬 설정으로 `mooonseok`과 noreply 이메일을 씁니다. 개인 컴퓨터에서는 개인 설정을 쓰세요.
- [ ] **GitHub 로그인**: `gh`는 개인 계정 `mooonseok`으로 로그인돼 있습니다. 회사 노트북이라면 반납 전에 `gh auth logout`을 실행하세요.
- [ ] **Claude 쪽 기록**: Claude 메모리에 저장된 것은 "항상 한국어로 답변" 하나이며, 2장에 옮겨 두었습니다. 대화 기록은 회사 계정에 남습니다.
- [ ] **전역 한국어 규칙**: 개인 컴퓨터에서 Claude Code를 쓴다면 `~/.claude/CLAUDE.md`에 "답변은 무조건 한국어" 규칙을 다시 만듭니다 (이 컴퓨터의 파일은 리포에 없음). Codex는 `AGENTS.md`의 사용자 선호를 읽습니다.
- [ ] **Codex 기본값**: `sh auto`는 모델을 명령에 직접 넘기므로 설정이 필요 없습니다. Codex 대화 화면도 같은 모델로 쓰려면 `~/.codex/config.toml`에 `model = "gpt-6-astra"`, `model_reasoning_effort = "high"`.
