#!/usr/bin/env python3
"""README의 파이프라인 흐름도(라이트·다크 SVG 두 장)를 만든다.

파이프라인이 바뀌면 아래 ROWS를 고치고 다시 실행한다:
    .venv/bin/python docs/make_pipeline_svg.py

디자인: taste-skill 하우스 규칙(그라데이션·그림자·얇은 테두리 상자·이모지·번호 매기기 없음, 톤 차이로 면 구분)과
awesome-design-md의 Vercel(라이트)·Linear(다크) 토큰, 블로그 강조색 #22456b.
"""
from html import escape
from pathlib import Path

THEMES = {
    "light": {
        "canvas": "#eef0f4", "script": "#ffffff", "codex": "#e9f0fa", "human": "#171717",
        "ink": "#171717", "body": "#4d4d4d", "mute": "#888888", "on_human": "#ffffff", "on_human_mute": "#b4b4b4",
        "accent": "#22456b", "line": "#b8bcc4",
    },
    "dark": {
        "canvas": "#0f1011", "script": "#1c1d20", "codex": "#222a4a", "human": "#f7f8f8",
        "ink": "#f7f8f8", "body": "#c9ced6", "mute": "#8a8f98", "on_human": "#0f1011", "on_human_mute": "#5c6068",
        "accent": "#93b1d0", "line": "#4a4e57",
    },
}

# (종류, 제목, 둘째 줄, 셋째 줄, 아래 설명) — 종류: script / codex / human
ROWS = [
    [
        ("script", "수집", "자막과 영상 정보", "transcript.md", ""),
        ("codex", "분석", "analyst · 리서처", "analysis.md", ""),
        ("codex", "설계", "curator · 편집장", "outline.md", ""),
        ("codex", "작성", "writer · 숏폼 작가", "post.md · publish.md", ""),
        ("codex", "디자인", "designer · 디자이너", "images.md", ""),
    ],
    [
        ("script", "자동 검사", "규칙 위반 찾기", "lint_post.py", ""),
        ("codex", "교정", "editor · 교열 기자", "editor-notes.md", "↺ 검사 오류가 남으면 한 번 더"),
        ("codex", "독자 테스트", "reader · 독자 테스터", "reader-test.md", "↺ 통과 못 하면 작성부터 고쳐 씀"),
        ("script", "draft 커밋", "posts/ 저장소", "고친 부분의 기준점", ""),
    ],
    [
        ("human", "확인·수정", "post.md 직접 고치기", "", ""),
        ("script", "sh copy-post", "검사 → HTML → 클립보드", "버전 v1, v2 … 저장", ""),
        ("human", "붙여넣기", "티스토리 글쓰기", "기본모드 · HTML 모드", ""),
        ("human", "발행", "카테고리 AI", "비공개로 확인 후 공개", ""),
    ],
]

W, M = 1200, 48
COLS, COL_W = 5, 196
GAP = (W - 2 * M - COLS * COL_W) // (COLS - 1)
NODE_H = 96
ROW_Y = [196, 352, 532]
FONT = "-apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Pretendard', 'Noto Sans KR', 'Segoe UI', sans-serif"
H = ROW_Y[-1] + NODE_H + 52

# 오른쪽 아래 결과물 패널: (파일, 설명)
RESULTS = [
    ("post.md", "본문, 직접 고치는 파일"),
    ("publish.md", "제목 후보 · 태그"),
    ("images.md", "이미지 위치 · 캡션"),
    ("reader-test.md", "독자 테스트 결과"),
    ("preview.html", "붙여넣을 모양 미리보기"),
]


def col_x(i):
    return M + i * (COL_W + GAP)


def text(x, y, s, size, fill, weight=400, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}">{escape(s)}</text>')


def node(t, kind, x, y, title, line2, line3, note):
    fill = t[kind]
    ink, sub = (t["on_human"], t["on_human_mute"]) if kind == "human" else (t["ink"], t["mute"])
    role = t["accent"] if kind == "codex" else (t["on_human_mute"] if kind == "human" else t["body"])
    out = [f'<rect x="{x}" y="{y}" width="{COL_W}" height="{NODE_H}" rx="14" fill="{fill}"/>',
           text(x + 18, y + 36, title, 19, ink, 700),
           text(x + 18, y + 60, line2, 13.5, role, 600 if kind == "codex" else 400)]
    if line3:
        out.append(text(x + 18, y + 80, line3, 13, sub))
    if note:
        out.append(text(x + 4, y + NODE_H + 26, note, 13, t["accent"], 600))
    return "".join(out)


def arrow(t, d):
    return f'<path d="{d}" fill="none" stroke="{t["line"]}" stroke-width="2" stroke-linejoin="round" marker-end="url(#a)"/>'


def build(theme):
    t = THEMES[theme]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">',
        f'<title>sh auto 실행부터 티스토리 발행까지의 흐름</title>',
        f'<defs><marker id="a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
        f'<path d="M1 1 L9 5 L1 9 z" fill="{t["line"]}"/></marker></defs>',
        f'<rect width="{W}" height="{H}" rx="24" fill="{t["canvas"]}"/>',
        text(M, 74, "유튜브 링크 한 줄이 블로그 글이 되기까지", 28, t["ink"], 700),
        text(M, 108, "sh auto 〈링크〉 → 약 12~21분 → 내가 확인 → sh copy-post → 티스토리", 15, t["body"]),
    ]
    # 범례
    lx = W - M - 360
    for i, (kind, label) in enumerate([("script", "스크립트"), ("codex", "Codex 역할"), ("human", "내가 하는 일")]):
        x = lx + i * 124
        parts.append(f'<rect x="{x}" y="60" width="18" height="18" rx="5" fill="{t[kind]}"/>')
        parts.append(text(x + 26, 74, label, 14, t["body"]))
    parts.append(text(M, 172, "sh auto가 하는 일", 15, t["ink"], 700))
    parts.append(text(M + 132, 172, "Codex gpt-6-astra · 노력 수준 high", 14, t["mute"]))

    for r, row in enumerate(ROWS):
        y = ROW_Y[r]
        for c, (kind, title, l2, l3, note) in enumerate(row):
            parts.append(node(t, kind, col_x(c), y, title, l2, l3, note))
            if c:
                parts.append(arrow(t, f"M{col_x(c) - GAP + 6} {y + NODE_H / 2} H{col_x(c) - 6}"))
    # 결과물 패널 (빈 다섯째 칸을 채운다)
    px, py, ph = col_x(4), ROW_Y[1], ROW_Y[2] + NODE_H - ROW_Y[1]
    parts.append(f'<rect x="{px}" y="{py}" width="{COL_W}" height="{ph}" rx="14" fill="{t["script"]}"/>')
    parts.append(text(px + 18, py + 36, "결과물", 19, t["ink"], 700))
    parts.append(text(px + 18, py + 60, "posts/〈날짜〉-〈영상ID〉/", 13, t["mute"]))
    for i, (f, d) in enumerate(RESULTS):
        y = py + 96 + i * 37
        parts.append(text(px + 18, y, f, 14.5, t["ink"], 600))
        parts.append(text(px + 18, y + 17, d, 12.5, t["mute"]))
    # 줄바꿈 연결: 윗줄 마지막 노드 → 아랫줄 첫 노드 (글을 읽듯 다음 줄로)
    for r in range(len(ROWS) - 1):
        last = len(ROWS[r]) - 1
        sx = col_x(last) + COL_W / 2
        y0 = ROW_Y[r] + NODE_H
        mid = (y0 + ROW_Y[r + 1]) / 2 + (14 if r == 1 else 0)
        ex = col_x(0) + COL_W / 2
        parts.append(arrow(t, f"M{sx} {y0 + 6} V{mid} H{ex} V{ROW_Y[r + 1] - 6}"))
    parts.append("</svg>")
    return "".join(parts)


def main():
    out = Path(__file__).parent
    for theme in THEMES:
        (out / f"pipeline-{theme}.svg").write_text(build(theme), encoding="utf-8")
        print(f"docs/pipeline-{theme}.svg")


if __name__ == "__main__":
    main()
