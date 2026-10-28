---
name: youtube-transcript
description: 유튜브 링크에서 영상 메타데이터와 자막을 가져와 posts/ 아래 작업 폴더에 저장한다. 유튜브 URL을 글의 재료로 쓸 때 사용.
---

# youtube-transcript

## 실행

```bash
.venv/bin/python .claude/skills/youtube-transcript/scripts/fetch_transcript.py "<유튜브 URL>"
```

- 옵션: `--lang ko,en` (선호 자막 언어 순서), `--out posts` (저장 위치)
- 출력 마지막 줄이 작업 폴더 경로다. 이후 단계는 이 폴더에서 진행한다.
- 생성 파일
  - `meta.json`: 제목, 채널, 업로드일, 길이, 챕터, 태그, 설명, 자막 종류
  - `transcript.md`: 1분 단위 문단으로 묶은 자막, 각 문단 앞에 `[mm:ss]`

## 동작 방식

1. `youtube-transcript-api`로 자막을 찾는다. 수동 자막을 자동 자막보다 우선한다.
2. 실패하면 `yt-dlp`로 자막 파일(vtt)을 받아 파싱한다. 언어별로 따로 시도한다.
3. 둘 다 실패하면 종료 코드 2로 끝난다. 이 경우 사용자에게 알리고 멈춘다. (음성 인식은 로드맵)

## 주의

- 자동 자막(`auto`)은 오인식이 많다. 고유명사, 숫자, 전문용어는 그대로 믿지 말고 문맥과 `meta.json`의 설명·태그로 보정한다. 확신이 없으면 "불확실"로 표시한다.
- `.venv`가 없으면 먼저 `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`를 실행한다.
