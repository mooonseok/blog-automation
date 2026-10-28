#!/usr/bin/env python3
"""post.md(주석 제거본)를 티스토리에 붙여넣을 HTML로 바꾼다.

티스토리 편집기는 붙여넣은 HTML의 인라인 스타일을 대부분 지운다 (기본모드 기준).
발행된 글을 조사해 보면 살아남는 것은 글자색(color), 배경색(background-color), 정렬(text-align) 정도이고,
나머지 서식은 티스토리 자체 서식(data-ke-*)으로 만들어진다.
그래서 이 변환기는
  - 상자·인용은 티스토리 인용 서식(blockquote data-ke-style 1~3), 표는 표 서식(data-ke-style),
    문단은 data-ke-size, 간격은 빈 문단(&nbsp;)으로 만들고
  - 인라인 스타일은 ALLOWED_STYLES만 쓴다. 마지막에 sanitize()가 나머지를 지우므로
    미리보기가 곧 티스토리에서 보일 모습이다.

부품 문법 (post.md 안에서 사용):
  :::summary [라벨]      한눈에 보기 상자. 첫 줄 = 핵심 한 문장, "- " = 체크 항목, "? " = 이 글에서 답할 질문
  :::takeaway [라벨]     한 줄 정리 (가운데 큰따옴표 인용). ==구절== 은 형광펜
  :::tip / :::warn / :::term [라벨]   팁·주의·용어 상자
  :::quote 화자          발언 인용 (세로선)
  :::steps               "제목 | 설명" 줄마다 번호 단계
  :::checklist [라벨]    "- " 줄마다 체크 항목
  :::                    부품 끝
  ## Q1. 질문           소제목 앞에 파란 Q1.
  [[이미지 N]]           이미지 자리 표시 (붙여넣은 뒤 실제 이미지로 바꾼다)

사용법:
    render_post.py < post.md > post.html
    render_post.py --preview < post.md > preview.html   실제 티스토리 CSS를 입힌 미리보기 페이지
"""
import html as htmllib
import re
import sys

import markdown

ACCENT = "#3d62ce"
INK = "#191f28"
BODY = "#333d4b"
SUB = "#4e5968"
CAPTION = "#6b7684"   # 흰 바탕 대비 4.5:1 이상 (작은 글씨 접근성 기준)
HIGHLIGHT = "#dbe3fa"
CHIP_BG = "#eceffa"

ALLOWED_STYLES = {"color", "background-color", "text-align", "list-style-type", "border-collapse", "width"}
TABLE_STYLE = "style11"
NUMBERS = "①②③④⑤⑥⑦⑧⑨⑩"
NOTES = {"tip": ("💡 TIP", "#1a7f37"), "warn": ("⚠️ 주의", "#9a6700"), "term": ("ℹ️ 용어", SUB)}

TISTORY_CSS = [
    "https://edge.daumcdn.net/tistory/tistory-admin/userblog/userblog-d688a284249d4b0687a7ec6021c32913af1f92cf/static/style/content.css",
    "https://edge.daumcdn.net/tistory/tistory-admin/userblog/userblog-d688a284249d4b0687a7ec6021c32913af1f92cf/static/style/uselessPMargin.css",
    "https://tistory1.daumcdn.net/tistory/0/Odyssey/style.css",
]


def P(content, size=16):
    return f'<p data-ke-size="size{size}">{content}</p>'


SPACER = P("&nbsp;")


def color(text, fg, bg=None):
    bg_css = f"background-color: {bg};" if bg else ""
    return f'<span style="color: {fg};{bg_css}">{text}</span>'


def chip(text, fg=ACCENT, bg=CHIP_BG):
    return color(f"<b>&nbsp;{htmllib.escape(text)}&nbsp;</b>", fg, bg)


def inline(text):
    """한 줄짜리 마크다운(굵게, 링크, 코드, ==형광펜==)을 HTML로."""
    out = markdown.markdown(text.strip())
    out = re.sub(r"^<p>(.*)</p>$", r"\1", out, flags=re.S)
    out = re.sub(r"==(.+?)==", lambda m: color(m.group(1), INK, HIGHLIGHT), out)
    return out.replace("<strong>", "<b>").replace("</strong>", "</b>")


def quote_box(style, paragraphs):
    return f'<blockquote data-ke-style="{style}">' + "".join(paragraphs) + "</blockquote>"


# ---------- 부품 ----------

def summary(label, lines):
    title = next((l for l in lines if not l.startswith(("- ", "? "))), "")
    checks = [l[2:] for l in lines if l.startswith("- ")]
    questions = [l[2:] for l in lines if l.startswith("? ")]
    paras = [P(chip(label or "📌 한눈에 보기"), 14), SPACER]
    if title:
        paras += [P(color(f"<b>{inline(title)}</b>", INK), 18), SPACER]
    paras += [P(f'{color("<b>✓</b>", ACCENT)}&nbsp; {color(inline(c), BODY)}') for c in checks]
    if questions:
        paras += [SPACER, P(color("<b>이 글에서 답할 질문</b>", CAPTION), 14)]
        paras += [P(color(f"Q{i + 1}. {inline(q)}", SUB), 14) for i, q in enumerate(questions)]
    return quote_box("style3", paras)


def takeaway(label, lines):
    return quote_box("style1", [
        P(chip(label or "한 줄 정리"), 14),
        P(color(f"<b>{inline(' '.join(lines))}</b>", INK), 18),
    ])


def note(kind, label, lines):
    default, fg = NOTES[kind]
    return quote_box("style3", [P(color(f"<b>{htmllib.escape(label or default)}</b>", fg), 14)]
                     + [P(color(inline(l), BODY)) for l in lines])


def quote(speaker, lines):
    paras = [P(color(f"<b>{inline(' '.join(lines))}</b>", INK), 18)]
    if speaker:
        paras.append(P(color(f"— {htmllib.escape(speaker)}", CAPTION), 14))
    return quote_box("style2", paras)


def steps(_label, lines):
    rows = []
    for i, line in enumerate(l for l in lines if l.strip()):
        line = re.sub(r"^\d+[.)]\s*", "", line)
        title, _, desc = line.partition("|")
        num = NUMBERS[i] if i < len(NUMBERS) else f"{i + 1}."
        desc_html = f" {color('—', CAPTION)} {color(inline(desc), SUB)}" if desc.strip() else ""
        rows.append(P(f"{color(f'<b>{num}</b>', ACCENT)}&nbsp; <b>{inline(title)}</b>{desc_html}"))
    return "".join(rows)


def checklist(label, lines):
    head = [P(color(f"<b>{htmllib.escape(label)}</b>", SUB), 14)] if label else []
    return "".join(head + [P(f'{color("<b>☐</b>", ACCENT)}&nbsp; {inline(l[2:])}') for l in lines if l.startswith("- ")])


COMPONENTS = {
    "summary": summary, "takeaway": takeaway, "quote": quote, "steps": steps, "checklist": checklist,
    "tip": lambda a, l: note("tip", a, l), "warn": lambda a, l: note("warn", a, l), "term": lambda a, l: note("term", a, l),
}


def image_slot(n):
    return quote_box("style3", [P(color(f"🖼 이미지 {n} 자리 — images.md의 이미지 {n}을 여기에 넣고 이 상자는 지운다", CAPTION), 14)])


def extract_components(md_text):
    """:::부품 블록을 HTML로 만들어 자리표시로 바꾼다 (마크다운 변환 뒤에 되돌린다)."""
    stash, out, block = [], [], None
    for line in md_text.splitlines():
        start = re.match(r"^:::(\w+)\s*(.*)$", line.strip())
        if block is None and start and start.group(1) in COMPONENTS:
            block = (start.group(1), start.group(2).strip(), [])
        elif block is not None and line.strip() == ":::":
            name, arg, lines = block
            stash.append(COMPONENTS[name](arg, [l.strip() for l in lines if l.strip()]))
            out += ["", f"@@C{len(stash) - 1}@@", ""]
            block = None
        elif block is not None:
            block[2].append(line)
        else:
            img = re.match(r"^\s*\[\[이미지\s*(\d+)\]\]\s*$", line)
            if img:
                stash.append(image_slot(img.group(1)))
                out += ["", f"@@C{len(stash) - 1}@@", ""]
            else:
                out.append(line)
    return "\n".join(out), stash


def tistory_table(match):
    """마크다운 표를 티스토리 표 서식으로. 머리줄도 일반 행으로 두고 굵게, 첫 열도 굵게."""
    rows = re.findall(r"<tr>(.*?)</tr>", match.group(0), flags=re.S)
    out = []
    for r, row in enumerate(rows):
        cells = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, flags=re.S)
        tds = "".join(f"<td>{f'<b>{c}</b>' if (r == 0 or i == 0) and c else c}</td>" for i, c in enumerate(cells))
        out.append(f"<tr>{tds}</tr>")
    return (
        f'<table style="border-collapse: collapse; width: 100%;" data-ke-align="alignLeft" data-ke-style="{TABLE_STYLE}">'
        f"<tbody>{''.join(out)}</tbody></table>"
    )


def style_blocks(html):
    html = re.sub(r"<h2>Q(\d+)\.\s*(.*?)</h2>", lambda m: f'<h2 data-ke-size="size26">{color(f"Q{m.group(1)}.", ACCENT)} {m.group(2)}</h2>', html)
    html = html.replace("<h2>", '<h2 data-ke-size="size26">').replace("<h3>", '<h3 data-ke-size="size23">')
    html = html.replace("<p>", '<p data-ke-size="size16">')
    html = html.replace("<ul>", '<ul style="list-style-type: disc;" data-ke-list-type="disc">')
    html = html.replace("<ol>", '<ol style="list-style-type: decimal;" data-ke-list-type="decimal">')
    html = html.replace("<strong>", "<b>").replace("</strong>", "</b>")
    html = re.sub(r'<pre><code class="language-(\w+)">', r'<pre data-ke-language="\1" data-ke-type="codeblock"><code>', html)
    html = html.replace("<pre><code>", '<pre data-ke-type="codeblock"><code>')
    return re.sub(r"<table>.*?</table>", tistory_table, html, flags=re.S)


def smart_typography(html):
    """본문 글자의 곧은따옴표를 둥근따옴표로, ...를 …로 바꾼다. 태그와 코드 안은 건드리지 않는다."""
    out, in_code = [], 0
    for part in re.split(r"(<[^>]+>)", html):
        if part.startswith("<"):
            tag = re.match(r"</?(\w+)", part)
            if tag and tag.group(1) in ("code", "pre"):
                in_code += -1 if part.startswith("</") else 1
            out.append(part)
            continue
        if in_code:
            out.append(part)
            continue
        part = part.replace("...", "…")
        part = re.sub(r'(^|[\s(\[“‘]|&nbsp;)"', r"\1“", part).replace('"', "”")
        part = re.sub(r"(^|[\s(\[“‘]|&nbsp;)'", r"\1‘", part).replace("'", "’")
        out.append(part)
    return "".join(out)


def sanitize(html):
    """티스토리가 지우는 인라인 스타일을 미리 지운다. 남는 것이 곧 티스토리에서 보일 모습이다."""
    def clean(match):
        kept = [d.strip() for d in match.group(1).split(";")
                if ":" in d and d.split(":", 1)[0].strip().lower() in ALLOWED_STYLES]
        return f' style="{"; ".join(kept)};"' if kept else ""
    return re.sub(r'\sstyle="([^"]*)"', clean, html)


def insert_spacers(html):
    """최상위 블록 사이에 빈 문단 하나, 소제목 앞에는 두 개."""
    top = r"<(?:p|ul|ol|table|pre|h2|h3|hr|blockquote)\b"
    blocks = [b.strip() for b in re.split(rf"\n(?={top}|@@C)", html) if b.strip()]
    out = []
    for i, block in enumerate(blocks):
        if i:
            out.append(SPACER)
            if block.startswith("<h2"):
                out.append(SPACER)
        out.append(block if block.startswith("<pre") else block.replace("\n", ""))
    return "\n".join(out)


def render(md_text):
    md_text, stash = extract_components(md_text)
    html = markdown.markdown(md_text, extensions=["tables", "fenced_code", "sane_lists"])
    html = style_blocks(html)
    html = insert_spacers(re.sub(r'<p data-ke-size="size16">@@C(\d+)@@</p>', r"@@C\1@@", html))
    html = re.sub(r"@@C(\d+)@@", lambda m: stash[int(m.group(1))], html)
    return sanitize(smart_typography(html))


def preview_page(body):
    links = "\n".join(f'<link rel="stylesheet" href="{href}">' for href in TISTORY_CSS)
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>미리보기 (티스토리 스킨 CSS 적용)</title>
{links}
<style>body {{ max-width: 760px; margin: 40px auto; padding: 0 20px; background: #fff; }}</style>
</head><body>
<div class="article-view" id="article-view">
<div class="tt_article_useless_p_margin contents_style">
{body}
</div></div>
</body></html>
"""


def main():
    body = render(sys.stdin.read())
    sys.stdout.write(preview_page(body) if "--preview" in sys.argv[1:] else body)


if __name__ == "__main__":
    main()
