#!/usr/bin/env python3
"""post.md(주석 제거본)를 티스토리에 붙여넣을 HTML로 바꾼다.

티스토리 편집기는 붙여넣은 HTML의 인라인 스타일을 대부분 지운다 (기본모드 기준).
발행된 글을 조사해 보면 살아남는 것은 글자색(color), 배경색(background-color), 정렬(text-align) 정도이고,
나머지 서식은 티스토리 자체 서식(data-ke-*)으로 만들어진다.
그래서 이 변환기는
  - 상자·인용은 티스토리 인용 서식(blockquote data-ke-style 1~3), 표는 표 서식(data-ke-style),
    문단은 data-ke-size, 간격은 빈 문단(&nbsp;)으로 만들고
  - 인라인 스타일은 ALLOWED_STYLES만 쓴다. 마지막에 sanitize()가 나머지를 지우므로
    실제 스킨 CSS로 미리 확인한다. 저장 후 편집기가 서식을 바꿀 수 있어 실제 글 확인은 별도로 필요하다.

부품 문법 (post.md 안에서 사용):
  :::summary [라벨]      한눈에 보기 상자. 첫 줄 = 핵심 한 문장, "- " = 체크 항목, "? " = 이 글에서 답할 질문
  :::takeaway [라벨]     한 줄 정리. ==구절== 은 형광펜
  :::tip / :::warn / :::term [라벨]   팁·주의·용어 상자
  :::quote 화자          발언 인용 (세로선)
  :::steps               "제목 | 설명" 줄마다 번호 단계
  :::motion [chart-list]  전후를 설명하는 "이름 | 내용" 두 줄. 스킨 CSS로 반복 재생
  :::checklist [라벨]    "- " 줄마다 체크 항목
  :::                    부품 끝
  ## Q1. 질문           소제목 앞에 파란 Q1.
  [[이미지 N]]           이미지 자리 표시 (붙여넣은 뒤 실제 이미지로 바꾼다)

사용법:
    render_post.py < post.md > post.html
    render_post.py --preview < post.md > preview.html   실제 티스토리 CSS를 입힌 미리보기 페이지
    render_post.py --preview --post-dir <글 폴더> < post.md > preview.html   같은 폴더의 PNG 표시
"""
import argparse
import html as htmllib
import re
import sys
from pathlib import Path

import markdown

# 네이비 테마: 본문·부품·표가 같은 팔레트를 공유한다.
ACCENT = "#22456b"
INK = "#18263d"
BODY = "#263244"
SUB = "#475569"
CAPTION = "#64748b"
HIGHLIGHT = "#dce8f6"
TABLE_HEADER_BG = "#e9f0fa"

ALLOWED_STYLES = {"color", "background-color", "text-align", "list-style-type", "border-collapse", "width"}
TABLE_STYLE = "style8"
NUMBERS = "①②③④⑤⑥⑦⑧⑨⑩"
NOTES = {"tip": "팁", "warn": "주의", "term": "용어"}

TISTORY_CSS = [
    "https://edge.daumcdn.net/tistory/tistory-admin/userblog/userblog-d688a284249d4b0687a7ec6021c32913af1f92cf/static/style/content.css",
    "https://edge.daumcdn.net/tistory/tistory-admin/userblog/userblog-d688a284249d4b0687a7ec6021c32913af1f92cf/static/style/uselessPMargin.css",
    "https://tistory1.daumcdn.net/tistory/0/Odyssey/style.css",
]


def P(content, size=18):
    return f'<p data-ke-size="size{size}">{content}</p>'


SPACER = P("&nbsp;", 16)


def color(text, fg, bg=None):
    bg_css = f"background-color: {bg};" if bg else ""
    return f'<span style="color: {fg};{bg_css}">{text}</span>'


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
    paras = [P(color(f"<b>{htmllib.escape(label or '한눈에 보기')}</b>", ACCENT), 18)]
    if title:
        paras += [f'<h3 data-ke-size="size23">{color(f"<b>{inline(title)}</b>", INK)}</h3>']
    if checks:
        items = "".join(f"<li>{P(color(inline(c), BODY))}</li>" for c in checks)
        paras.append(f'<ul data-ke-list-type="disc">{items}</ul>')
    if questions:
        paras += [SPACER, P(color("<b>이 글에서 답할 질문</b>", SUB), 18)]
        paras += [P(color(f"Q{i + 1}. {inline(q)}", SUB), 18) for i, q in enumerate(questions)]
    return quote_box("style3", paras)


def takeaway(label, lines):
    heading = P(color(htmllib.escape(label), SUB), 16) if label else ""
    return heading + P(color(f"<b>{inline(' '.join(lines))}</b>", INK))


def note(kind, label, lines):
    return quote_box("style3", [P(color(f"<b>{htmllib.escape(label or NOTES[kind])}</b>", INK))]
                     + [P(color(inline(l), BODY)) for l in lines])


def quote(speaker, lines):
    paras = [P(color(f"<b>{inline(' '.join(lines))}</b>", INK), 18)]
    if speaker:
        paras.append(P(color(f"— {htmllib.escape(speaker)}", CAPTION), 16))
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


def motion(variant, lines):
    rows = []
    for line in lines:
        label, sep, detail = line.partition("|")
        content = f"<b>{htmllib.escape(label.strip())}</b> · {htmllib.escape(detail.strip())}" if sep else htmllib.escape(line)
        rows.append(P(content))
    sketch = ""
    if variant == "chart-list":
        sketch = '<div aria-hidden="true" class="ba-motion-chart"><i></i><i></i><i></i></div>'
    return '<div class="ba-motion">' + sketch + "".join(rows) + "</div>"


def checklist(label, lines):
    head = [P(color(f"<b>{htmllib.escape(label)}</b>", SUB), 18)] if label else []
    return "".join(head + [P(f'{color("<b>☐</b>", ACCENT)}&nbsp; {inline(l[2:])}') for l in lines if l.startswith("- ")])


COMPONENTS = {
    "summary": summary, "takeaway": takeaway, "quote": quote, "steps": steps, "checklist": checklist, "motion": motion,
    "tip": lambda a, l: note("tip", a, l), "warn": lambda a, l: note("warn", a, l), "term": lambda a, l: note("term", a, l),
}


def image_slot(n):
    return P(color(f"[이미지 {n} 자리]", CAPTION), 16)


def preview_image_slots(post_dir):
    """preview.html 옆의 최신 PNG만 읽고, 발행용 렌더링에는 전달하지 않는다."""
    spec = post_dir / "images.md"
    sections = {}
    if spec.is_file():
        text = spec.read_text(encoding="utf-8")
        for block in re.split(r"(?=^## 이미지 \d+)", text, flags=re.M):
            head = re.match(r"## 이미지 (\d+)[ \t]*[:：]?[ \t]*([^\n]*)", block)
            if head:
                fields = dict(re.findall(r"^- (캡션|대체 텍스트):[ \t]*(.+)$", block, flags=re.M))
                sections[head[1]] = (head[2].strip(), fields)
    slots = {}
    for n in ("1", "2"):
        png = post_dir / "images" / f"image-{n}.png"
        svg = png.with_suffix(".svg")
        if not png.is_file() or (svg.is_file() and png.stat().st_mtime_ns < svg.stat().st_mtime_ns):
            continue
        title, fields = sections.get(n, ("", {}))
        alt = htmllib.escape(fields.get("대체 텍스트") or title or f"이미지 {n}")
        caption = htmllib.escape(fields.get("캡션", ""))
        figcaption = f"<figcaption>{caption}</figcaption>" if caption else ""
        slots[n] = f'<figure class="post-preview-figure"><img src="images/{png.name}" alt="{alt}">{figcaption}</figure>'
    return slots


def extract_components(md_text, image_slots):
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
                n = img.group(1)
                stash.append(image_slots.get(n) or image_slot(n))
                out += ["", f"@@C{len(stash) - 1}@@", ""]
            else:
                out.append(line)
    return "\n".join(out), stash


def tistory_table(match):
    """티스토리 기본 표에 열·행 제목을 구분해 읽는 순서를 명시한다."""
    rows = re.findall(r"<tr>(.*?)</tr>", match.group(0), flags=re.S)
    out = []
    for r, row in enumerate(rows):
        cells = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, flags=re.S)
        rendered_cells = []
        for i, c in enumerate(cells):
            if r == 0:
                text = P(color(c, INK))
                # 설명이 긴 2열 표에서도 첫 열 항목명이 한 글자씩 쪼개지지 않게 한다.
                width = " width: 4em;" if len(cells) == 2 and i == 0 else ""
                rendered_cells.append(f'<th scope="col" style="text-align: left; background-color: {TABLE_HEADER_BG};{width}">{text}</th>')
            elif i == 0:
                text = P(color(c, ACCENT))
                rendered_cells.append(f'<th scope="row" style="text-align: left;">{text}</th>')
            else:
                rendered_cells.append(f"<td>{P(color(c, BODY))}</td>")
        out.append(f"<tr>{''.join(rendered_cells)}</tr>")
    if not out:
        return match.group(0)
    # style8의 첫 행 서식이 첫 데이터 행에 걸리지 않게 열 제목도 같은 행 그룹에 둔다.
    return (
        f'<table style="border-collapse: collapse; width: 100%;" border="1" rules="rows" '
        f'data-ke-align="alignLeft" data-ke-style="{TABLE_STYLE}"><tbody>{"".join(out)}</tbody></table>'
    )


def style_blocks(html):
    html = re.sub(r"<h2>Q(\d+)\.\s*(.*?)</h2>", lambda m: f'<h2 data-ke-size="size26">{color(f"Q{m.group(1)}.", ACCENT)} {m.group(2)}</h2>', html)
    html = html.replace("<h2>", '<h2 data-ke-size="size26">').replace("<h3>", '<h3 data-ke-size="size23">')
    html = html.replace("<p>", '<p data-ke-size="size18">')
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


def render(md_text, image_slots=None):
    md_text, stash = extract_components(md_text, image_slots or {})
    html = markdown.markdown(md_text, extensions=["tables", "fenced_code", "sane_lists"])
    html = style_blocks(html)
    html = insert_spacers(re.sub(r'<p data-ke-size="size18">@@C(\d+)@@</p>', r"@@C\1@@", html))
    html = re.sub(r"@@C(\d+)@@", lambda m: stash[int(m.group(1))], html)
    return sanitize(smart_typography(html))


def preview_page(body):
    links = "\n".join(f'<link rel="stylesheet" href="{href}">' for href in TISTORY_CSS)
    motion_css = ""
    if 'class="ba-motion"' in body:
        motion_css = Path(__file__).with_name("tistory-motion.css").read_text(encoding="utf-8")
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>미리보기 (티스토리 스킨 CSS 적용)</title>
{links}
<style>
{motion_css}
body {{ max-width: 760px; margin: 40px auto; padding: 0 20px; background: #fff; }}
#article-view .post-preview-figure {{ margin: 0 0 24px; }}
#article-view .post-preview-figure img {{ display: block; max-width: 100%; height: auto; }}
#article-view .post-preview-figure figcaption {{ margin-top: 8px; color: {SUB}; font-size: 16px; line-height: 1.6; text-align: left; }}
</style>
</head><body>
<div class="article-view" id="article-view">
<div class="tt_article_useless_p_margin contents_style">
{body}
</div></div>
</body></html>
"""


def main():
    parser = argparse.ArgumentParser(description="마크다운을 티스토리 HTML로 바꿉니다.")
    parser.add_argument("--preview", action="store_true", help="티스토리 스킨 미리보기를 출력합니다.")
    parser.add_argument("--post-dir", type=Path, help="미리보기와 이미지가 저장되는 글 폴더입니다.")
    args = parser.parse_args()
    if args.post_dir and not args.preview:
        parser.error("--post-dir은 --preview와 함께 사용합니다.")
    slots = preview_image_slots(args.post_dir) if args.post_dir else {}
    body = render(sys.stdin.read(), slots)
    sys.stdout.write(preview_page(body) if args.preview else body)


if __name__ == "__main__":
    main()
