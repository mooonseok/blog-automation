@AGENTS.md

## Claude Code 전용

- `/write`는 `.claude/commands/write.md`, 역할은 `.claude/agents/`의 서브에이전트로 실행한다.
- 서브에이전트(특히 analyst)의 파일 쓰기가 하네스에 막히면, 결과를 텍스트로 받아 메인 세션이 해당 파일로 저장한다.
