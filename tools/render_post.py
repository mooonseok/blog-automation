#!/usr/bin/env python3
"""post.md(주석 제거본)를 티스토리 HTML 모드에 붙여넣을 HTML로 바꾼다.

티스토리 스킨이 본문을 망가뜨리는 규칙을 피한다.
  - p { margin: 0 !important }      → 블록 사이에 티스토리식 빈 문단을 넣어 간격을 만든다
  - blockquote 글자를 회색으로 강제  → 상자는 전부 <div>로 만든다 (blockquote 쓰지 않음)
  - a { display: inline-block }      → 링크를 inline으로
  - li { word-break: break-all }      → keep-all

부품 문법 (post.md 안에서 사용):
  :::summary [라벨]      핵심 요약 카드. 첫 줄 = 핵심 한 문장, "- " = 체크 항목, "? " = 이 글에서 답할 질문
  :::takeaway [라벨]     한 줄 정리. ==구절== 은 형광펜
  :::tip / :::warn / :::term [라벨]   팁·주의·용어 상자
  :::quote 화자          큰따옴표 인용
  :::steps               "제목 | 설명" 줄마다 번호 단계
  :::checklist [라벨]    "- " 줄마다 체크박스
  :::                    부품 끝
  ## Q1. 질문           소제목 위에 Q1 라벨
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
INK = "#191f28"        # 제목·강조
BODY = "#333d4b"       # 본문
SUB = "#4e5968"        # 보조
CAPTION = "#8b95a1"    # 캡션
LINE = "#e5e8eb"
KEEP = "word-break:keep-all;overflow-wrap:break-word;"

SPACER = '<p data-ke-size="size16">&nbsp;</p>'
TOP_BLOCK = r"<(?:p|ul|ol|table|pre|h2|h3|hr|div|figure)\b"

CHIP = (
    "display:inline-block;padding:4px 10px;border-radius:999px;background:#eceffa;"
    f"color:{ACCENT};font-size:12px;font-weight:700;line-height:1.4;"
)
NOTES = {
    "tip": ("💡 TIP", "background:#edf7f0;", "#1a7f37"),
    "warn": ("⚠️ 주의", "background:#fff7e0;border:1px solid #f3e1a8;", "#9a6700"),
    "term": ("ℹ️ 용어", "background:#f2f4f6;", SUB),
}

TISTORY_CSS = [
    "https://edge.daumcdn.net/tistory/tistory-admin/userblog/userblog-d688a284249d4b0687a7ec6021c32913af1f92cf/static/style/content.css",
    "https://edge.daumcdn.net/tistory/tistory-admin/userblog/userblog-d688a284249d4b0687a7ec6021c32913af1f92cf/static/style/uselessPMargin.css",
    "https://tistory1.daumcdn.net/tistory/0/Odyssey/style.css",
]


def inline(text):
    """한 줄짜리 마크다운(굵게, 링크, 코드, ==형광펜==)을 HTML로."""
    out = markdown.markdown(text.strip())
    out = re.sub(r"^<p>(.*)</p>$", r"\1", out, flags=re.S)
    out = re.sub(r"==(.+?)==", r'<span style="background:linear-gradient(transparent 58%,#dbe3fa 58%);">\1</span>', out)
    return style_inline(out)


def style_inline(html):
    html = re.sub(r"<strong>", f'<b style="color:{INK};">', html).replace("</strong>", "</b>")
    html = re.sub(
        r'<a href="',
        f'<a target="_blank" rel="noopener" style="display:inline;color:{ACCENT};'
        f'text-decoration:underline;text-underline-offset:3px;{KEEP}" href="',
        html,
    )
    return re.sub(
        r"<code>",
        '<code style="padding:2px 6px;background:#f1f3f5;border-radius:4px;font-size:0.9em;word-break:break-all;">',
        html,
    )


# ---------- 부품 ----------

def summary(label, lines):
    label = label or "📌 한눈에 보기"
    title = next((l for l in lines if not l.startswith(("- ", "? "))), "")
    checks = [l[2:] for l in lines if l.startswith("- ")]
    questions = [l[2:] for l in lines if l.startswith("? ")]
    parts = [f'<span style="{CHIP}">{htmllib.escape(label)}</span>']
    if title:
        parts.append(f'<div style="margin-top:12px;font-size:18px;font-weight:700;line-height:1.55;color:{INK};">{inline(title)}</div>')
    for i, c in enumerate(checks):
        parts.append(
            f'<div style="margin-top:{14 if i == 0 else 8}px;display:flex;gap:10px;font-size:15.5px;line-height:1.7;color:{BODY};">'
            f'<span style="flex:none;color:{ACCENT};font-weight:800;">✓</span><span>{inline(c)}</span></div>'
        )
    if questions:
        qs = "<br>".join(f"Q{i + 1}. {inline(q)}" for i, q in enumerate(questions))
        parts.append(
            f'<div style="margin-top:16px;padding-top:14px;border-top:1px dashed {LINE};font-size:13px;font-weight:700;color:{CAPTION};">이 글에서 답할 질문</div>'
            f'<div style="margin-top:6px;font-size:15px;line-height:1.8;color:{SUB};">{qs}</div>'
        )
    return (
        f'<div style="margin:0;padding:22px 20px;background:#fff;border:1px solid {LINE};border-radius:16px;'
        f'box-shadow:0 2px 8px rgba(0,0,0,.04);{KEEP}">' + "".join(parts) + "</div>"
    )


def takeaway(label, lines):
    label = label or "한 줄 정리"
    return (
        f'<div style="margin:0;padding:20px 4px;border-top:1px solid {LINE};border-bottom:1px solid {LINE};{KEEP}">'
        f'<span style="{CHIP}">{htmllib.escape(label)}</span>'
        f'<div style="margin-top:10px;font-size:18px;font-weight:700;line-height:1.6;color:{INK};">{inline(" ".join(lines))}</div></div>'
    )


def note(kind, label, lines):
    default, box, color = NOTES[kind]
    body = "<br>".join(inline(l) for l in lines)
    return (
        f'<div style="margin:0;padding:14px 16px;{box}border-radius:10px;font-size:15px;line-height:1.7;color:{BODY};{KEEP}">'
        f'<div style="font-size:13px;font-weight:700;color:{color};margin-bottom:4px;">{htmllib.escape(label or default)}</div>{body}</div>'
    )


def quote(speaker, lines):
    who = f'<div style="margin-top:10px;font-size:13px;color:{CAPTION};">— {htmllib.escape(speaker)}</div>' if speaker else ""
    return (
        f'<div style="margin:0;padding:0 4px;{KEEP}">'
        f'<div style="font-size:44px;line-height:1;color:{ACCENT};font-weight:800;font-family:Georgia,serif;">“</div>'
        f'<div style="margin-top:2px;font-size:18px;font-weight:600;line-height:1.7;color:{INK};">{inline(" ".join(lines))}</div>{who}</div>'
    )


def steps(_label, lines):
    rows = []
    for i, line in enumerate(l for l in lines if l.strip()):
        line = re.sub(r"^\d+[.)]\s*", "", line)
        title, _, desc = line.partition("|")
        desc_html = f'<div style="margin-top:2px;font-size:15px;color:{SUB};line-height:1.7;">{inline(desc)}</div>' if desc.strip() else ""
        rows.append(
            f'<div style="display:flex;gap:12px;margin-top:{0 if i == 0 else 16}px;">'
            f'<span style="flex:none;width:26px;height:26px;border-radius:50%;background:{ACCENT};color:#fff;font-size:13px;'
            f'font-weight:700;line-height:26px;text-align:center;">{i + 1}</span>'
            f'<div><div style="font-size:16px;font-weight:700;color:{INK};line-height:1.6;">{inline(title)}</div>{desc_html}</div></div>'
        )
    return f'<div style="margin:0;{KEEP}">' + "".join(rows) + "</div>"


def checklist(label, lines):
    items = [l[2:] for l in lines if l.startswith("- ")]
    head = f'<div style="font-size:13px;font-weight:700;color:{SUB};margin-bottom:10px;">{htmllib.escape(label)}</div>' if label else ""
    rows = "".join(
        f'<div style="display:flex;gap:10px;margin-top:{0 if i == 0 else 8}px;"><span style="flex:none;">☐</span><span>{inline(t)}</span></div>'
        for i, t in enumerate(items)
    )
    return f'<div style="margin:0;padding:18px 20px;background:#f9fafb;border-radius:12px;font-size:15.5px;line-height:1.7;color:{BODY};{KEEP}">{head}{rows}</div>'


COMPONENTS = {
    "summary": summary, "takeaway": takeaway, "quote": quote, "steps": steps, "checklist": checklist,
    "tip": lambda a, l: note("tip", a, l), "warn": lambda a, l: note("warn", a, l), "term": lambda a, l: note("term", a, l),
}


def image_slot(n):
    return (
        f'<div style="margin:0;padding:28px 16px;border:2px dashed #c9cfd8;border-radius:12px;text-align:center;'
        f'font-size:14px;line-height:1.6;color:{CAPTION};">🖼 이미지 {n} 자리 — images.md의 이미지 {n}을 여기에 넣고 이 상자는 지운다</div>'
    )


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


def style_blocks(html):
    html = re.sub(
        r"<h2>Q(\d+)\.\s*(.*?)</h2>",
        lambda m: (
            f'<h2 style="margin:0;font-size:22px;font-weight:700;line-height:1.45;color:{INK};{KEEP}">'
            f'<span style="display:block;margin-bottom:4px;font-size:13px;font-weight:800;color:{ACCENT};letter-spacing:.04em;">Q{m.group(1)}</span>{m.group(2)}</h2>'
        ),
        html,
    )
    html = html.replace("<h2>", f'<h2 style="margin:0;font-size:22px;font-weight:700;line-height:1.45;color:{INK};{KEEP}">')
    html = html.replace("<h3>", f'<h3 style="margin:0;font-size:18px;font-weight:700;line-height:1.5;color:{INK};{KEEP}">')
    html = html.replace("<p>", f'<p data-ke-size="size16" style="line-height:1.85;color:{BODY};{KEEP}">')
    html = html.replace("<li>", f'<li style="margin:0 0 8px;line-height:1.8;color:{BODY};{KEEP}">')
    html = html.replace("<ul>", '<ul style="margin:0;padding-left:1.3em;">').replace("<ol>", '<ol style="margin:0;padding-left:1.5em;">')
    html = re.sub(r"<pre><code", '<pre style="margin:0;padding:18px 20px;background:#f6f8fa;border-radius:8px;overflow-x:auto;font-size:14px;line-height:1.6;"><code data-block', html)
    html = style_inline(html).replace(" data-block", "")
    # 코드 블록 안의 code에는 인라인 코드 스타일이 붙지 않게 되돌린다
    html = re.sub(r'(<pre[^>]*>)<code style="[^"]*"', r"\1<code", html)
    return style_tables(html)


def style_tables(html):
    th = f"background:#f9fafb;color:{SUB};font-size:13px;font-weight:600;text-align:left;padding:12px 14px;border:0;border-bottom:1px solid {LINE};"
    td = f"padding:12px 14px;border:0;border-bottom:1px solid #f2f4f6;color:{BODY};vertical-align:top;{KEEP}"
    td_first = f"padding:12px 14px;border:0;border-bottom:1px solid #f2f4f6;color:{INK};font-weight:600;vertical-align:top;{KEEP}"
    html = re.sub(r"<tr>(\s*)<td>", rf'<tr>\1<td style="{td_first}">', html)
    html = re.sub(r'<th( style="[^"]*")?>', f'<th style="{th}">', html)
    html = re.sub(r'<td( style="text-align[^"]*")?>', f'<td style="{td}">', html)
    html = html.replace(
        "<table>",
        f'<div style="margin:0;overflow-x:auto;border:1px solid {LINE};border-radius:12px;">'
        '<table style="width:100%;min-width:420px;border-collapse:separate;border-spacing:0;font-size:14.5px;line-height:1.6;margin:0;">',
    )
    return html.replace("</table>", "</table></div>")


def insert_spacers(html):
    """최상위 블록 사이에 빈 문단 하나, 소제목 앞에는 두 개."""
    blocks = [b.strip() for b in re.split(rf"\n(?={TOP_BLOCK}|@@C)", html) if b.strip()]
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
    # 부품 자리표시를 감싼 문단을 벗기고, 블록 사이에 빈 문단을 넣은 뒤 부품 HTML로 되돌린다
    html = insert_spacers(re.sub(r'<p data-ke-size="size16"[^>]*>@@C(\d+)@@</p>', r"@@C\1@@", html))
    return re.sub(r"@@C(\d+)@@", lambda m: stash[int(m.group(1))], html)


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
