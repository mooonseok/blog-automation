#!/usr/bin/env python3
"""post.md(주석 제거본)를 티스토리 HTML 모드에 붙여넣을 HTML로 바꾼다.

티스토리 스킨이 본문을 망가뜨리는 규칙들을 인라인 스타일로 덮어쓴다.
  - 문단 여백 제거 설정: p { margin: 0 !important }      → 문단마다 여백을 !important로 지정
  - .article-view a { display: inline-block }            → 링크가 통째로 다음 줄로 넘어감 → inline
  - li 등의 word-break: break-all                         → 단어 중간 줄바꿈 → keep-all

사용법:
    render_post.py < post.md > post.html
    render_post.py --preview < post.md > preview.html   실제 티스토리 CSS를 입힌 미리보기 페이지
"""
import re
import sys

import markdown

ACCENT = "#3d62ce"
TEXT = "word-break: keep-all; overflow-wrap: break-word;"

STYLE = {
    "p": f"line-height: 1.85; {TEXT}",
    "p_box": f"margin: 0 0 8px !important; padding: 0 !important; line-height: 1.8; {TEXT}",
    "h2": (
        "margin: 64px 0 22px !important; padding: 0 0 12px; border-bottom: 2px solid #222; "
        f"font-size: 24px; font-weight: 700; line-height: 1.4; {TEXT}"
    ),
    "h3": (
        f"margin: 40px 0 14px !important; padding: 0 0 0 12px; border-left: 4px solid {ACCENT}; "
        f"font-size: 19px; font-weight: 700; line-height: 1.5; {TEXT}"
    ),
    "ul": "margin: 0 0 26px !important; padding-left: 1.4em;",
    "ol": "margin: 0 0 26px !important; padding-left: 1.6em;",
    "li": f"margin: 0 0 10px; line-height: 1.8; {TEXT}",
    "blockquote": (
        f"margin: 8px 0 30px; padding: 20px 24px 12px; background: #f3f6fd; "
        f"border: 0; border-left: 4px solid {ACCENT}; border-radius: 0 10px 10px 0; "
        "font-style: normal; color: inherit;"
    ),
    "table": (
        "width: 100%; margin: 8px 0 32px; border-collapse: collapse; border-top: 2px solid #222; "
        "font-size: 15px;"
    ),
    "th": (
        "padding: 13px 14px; background: #f5f7fb; border: 0; border-bottom: 1px solid #d5dae3; "
        f"text-align: left; font-weight: 700; line-height: 1.6; {TEXT}"
    ),
    "td": (
        "padding: 13px 14px; border: 0; border-bottom: 1px solid #e9ecf1; "
        f"vertical-align: top; line-height: 1.7; {TEXT}"
    ),
    "td_first": (
        "padding: 13px 14px; border: 0; border-bottom: 1px solid #e9ecf1; background: #fafbfc; "
        f"vertical-align: top; font-weight: 700; line-height: 1.7; width: 26%; {TEXT}"
    ),
    "a": (
        f"display: inline !important; color: {ACCENT}; text-decoration: underline; "
        f"text-underline-offset: 3px; {TEXT}"
    ),
    "strong": "font-weight: 700; color: #111;",
    "code": (
        "padding: 2px 6px; background: #f1f3f5; border-radius: 4px; "
        "font-size: 0.9em; word-break: break-all;"
    ),
    "pre": (
        "margin: 0 0 28px; padding: 18px 20px; background: #f6f8fa; border-radius: 8px; "
        "overflow-x: auto; font-size: 14px; line-height: 1.6;"
    ),
    "hr": "margin: 48px 0; border: 0; border-top: 1px solid #e5e5e5;",
}

TISTORY_CSS = [
    "https://edge.daumcdn.net/tistory/tistory-admin/userblog/userblog-d688a284249d4b0687a7ec6021c32913af1f92cf/static/style/content.css",
    "https://edge.daumcdn.net/tistory/tistory-admin/userblog/userblog-d688a284249d4b0687a7ec6021c32913af1f92cf/static/style/uselessPMargin.css",
    "https://tistory1.daumcdn.net/tistory/0/Odyssey/style.css",
]


def style_attr(name):
    return f' style="{STYLE[name]}"'


def style_blockquote(match):
    inner = match.group(1).replace("<p>", f"<p{style_attr('p_box')}>")
    return f"<blockquote{style_attr('blockquote')}>{inner}</blockquote>"


def style_cell(match):
    tag, existing = match.group(1), match.group(3) or ""
    return f'<{tag} style="{STYLE[tag]} {existing}">'


# 티스토리 편집기가 "빈 줄"을 만들 때 쓰는 빈 문단. 인라인 여백(margin)은 붙여넣을 때 지워지므로 이것으로 간격을 만든다
SPACER = '<p data-ke-size="size16">&nbsp;</p>'
TOP_BLOCK = r"<(?:p|ul|ol|table|blockquote|pre|h2|h3|hr)\b"


def insert_spacers(html):
    """최상위 블록 사이마다 빈 문단을 하나씩 넣는다. 인용 상자 안쪽은 건드리지 않는다."""
    boxes = []

    def stash(match):
        boxes.append(match.group(0))
        return f"\x00{len(boxes) - 1}\x00"

    html = re.sub(r"<blockquote\b.*?</blockquote>", stash, html, flags=re.S)
    blocks = [b for b in re.split(rf"\n(?=\x00|{TOP_BLOCK})", html) if b.strip()]
    html = f"\n{SPACER}\n".join(blocks)
    return re.sub(r"\x00(\d+)\x00", lambda m: boxes[int(m.group(1))], html)


def render(md_text):
    html = markdown.markdown(md_text, extensions=["tables", "fenced_code", "sane_lists"])

    # 박스 안 문단은 여백을 줄인다 (전체 <p> 치환보다 먼저)
    html = re.sub(r"<blockquote>(.*?)</blockquote>", style_blockquote, html, flags=re.S)
    # 표의 첫 열은 항목 이름이므로 굵게
    html = re.sub(r"<tr>(\s*)<td>", rf"<tr>\1<td{style_attr('td_first')}>", html)
    html = re.sub(r'<(th|td)( style="([^"]*)")?>', style_cell, html)
    html = re.sub(r'<a href="', f'<a target="_blank" rel="noopener"{style_attr("a")} href="', html)
    # pre 안의 code는 인라인 코드 스타일을 받지 않도록 먼저 처리
    html = re.sub(r"<pre><code", f"<pre{style_attr('pre')}><code data-block", html)
    html = re.sub(r"<code>", f"<code{style_attr('code')}>", html)
    html = html.replace(" data-block", "")
    for tag in ("p", "h2", "h3", "ul", "ol", "li", "table", "strong"):
        html = html.replace(f"<{tag}>", f"<{tag}{style_attr(tag)}>")
    html = html.replace("<hr />", f"<hr{style_attr('hr')} />")
    return insert_spacers(html)


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
