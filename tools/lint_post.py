#!/usr/bin/env python3
"""post.md가 blog-style 규칙을 지키는지 기계적으로 검사한다.

사용법: lint_post.py <글 폴더 또는 post.md>
오류가 하나라도 있으면 종료 코드 1. 경고만 있으면 0.
"""
import re
import sys
from pathlib import Path

BODY_MIN, BODY_MAX = 1800, 3500
MAX_SENTENCES = 3
MAX_IMAGES = 2

# S0: 작성 과정이나 검증 여부에 대한 메타 문장
META = [
    r"확인하지 않았", r"별도로 확인", r"확인되지 않았", r"검증하지 않았", r"자막 기준", r"자막을 바탕",
    r"영상(에서|의) (설명한 )?내용을 (바탕|정리)", r"정리했으며", r"이 글은", r"이번 글(에서|은)", r"본 글",
    r"알아보(겠|자)", r"살펴보(겠|자)", r"결론부터 말하면",
]
ENDINGS = [(r"(?<![\"“'‘])[가-힣]요[.?!](\s|$)", "해요체"), (r"[가-힣](습|입)니다[.?!](\s|$)", "합니다체")]


def strip_quoted(text):
    return re.sub(r"\"[^\"]*\"|“[^”]*”|'[^']*'|‘[^’]*’", "", text)


def plain(text):
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return re.sub(r"[*`=#|>]|^[-?]\s|^\d+\.\s", "", text, flags=re.M)


def sentences(paragraph):
    text = strip_quoted(plain(paragraph))
    return len(re.findall(r"[.!?](?=\s|$)", text))


def lint(post_path):
    errors, warns = [], []
    lines = post_path.read_text(encoding="utf-8").splitlines()
    err = lambda n, msg: errors.append(f"[오류] {n}행: {msg}")
    warn = lambda n, msg: warns.append(f"[경고] {n}행: {msg}")

    in_comp, comp_name, comps, images = False, "", [], []
    in_source, body_chars = False, 0
    paragraph, para_start = [], 0

    def flush():
        nonlocal paragraph
        if paragraph:
            text = " ".join(paragraph)
            n = sentences(text)
            if n > MAX_SENTENCES:
                err(para_start, f"문단이 {n}문장이다. 1~2문장, 최대 {MAX_SENTENCES}문장으로 쪼갠다")
            if text.count("**") >= 4:
                warn(para_start, "한 문단에 굵은 글씨가 2개 이상이다")
        paragraph = []

    for i, raw in enumerate(lines, 1):
        line = raw.strip()
        no_comment = re.sub(r"<!--.*?-->", "", line).strip()

        # 링크·메타 문장·말투는 모든 줄에서 검사 (주석 제외)
        if re.search(r"youtube\.com|youtu\.be", no_comment):
            err(i, "영상 링크는 넣지 않는다")
        if re.search(r"[?&]t=\d+s|\[\d{1,2}:\d{2}(:\d{2})?\]", no_comment):
            err(i, "타임스탬프 링크·표기는 넣지 않는다")
        if re.search(r"(?<!\()https?://\S+", re.sub(r"\]\([^)]+\)", "]", no_comment)):
            warn(i, "맨 URL이 보인다. 이름에 링크를 건다")
        if re.search(r"(?<![\w.(/])@[A-Za-z0-9_]{2,}", no_comment):
            warn(i, "@핸들이 보인다. 이름에 링크를 건다")
        meta = next((m.group(0) for m in (re.search(p, no_comment) for p in META) if m), None)
        if meta:
            err(i, f"메타 문장(S0·S1): '{meta}'")
        if not (in_comp and comp_name == "quote"):
            for pattern, name in ENDINGS:
                if re.search(pattern, strip_quoted(no_comment)):
                    err(i, f"{name} 문장이다. 평서체 '~다'로 쓴다")

        # 부품
        start = re.match(r"^:::(\w+)", line)
        if not in_comp and start:
            in_comp, comp_name = True, start.group(1)
            comps.append(comp_name)
            flush()
            continue
        if in_comp:
            if line == ":::":
                in_comp = False
            else:
                body_chars += len(plain(no_comment))
            continue

        if line.startswith(">"):
            if not (lines[i - 2].strip().startswith(">") if i > 1 else False):
                err(i, "인용 블록(>)은 쓰지 않는다. :::summary, :::takeaway 등 부품을 쓴다")
            flush()
            continue
        if line == "---":
            warn(i, "구분선(---)은 쓰지 않는다")
        image = re.match(r"^\[\[이미지\s*(\d+)\]\]$", line)
        if image:
            images.append((i, image.group(1)))
            flush()
            continue

        if line.startswith("## "):
            flush()
            in_source = line[3:].strip() == "출처"
            continue
        if in_source:
            if no_comment and not re.match(r"^- 영상: .+, 「.+」 \(\d{4}-\d{2}-\d{2}\)$", no_comment):
                err(i, "출처에는 '- 영상: 채널명, 「제목」 (YYYY-MM-DD)' 한 줄만 쓴다")
            continue

        if not no_comment:
            flush()
            continue
        if re.match(r"^(\||[-*] |\d+\. )", no_comment):
            flush()
            body_chars += len(plain(no_comment))
            continue
        if not paragraph:
            para_start = i
        paragraph.append(no_comment)
        body_chars += len(plain(no_comment))
    flush()

    if in_comp:
        err(len(lines), f":::{comp_name} 부품이 ':::'로 닫히지 않았다")
    if "summary" not in comps:
        err(1, ":::summary (한눈에 보기)가 없다")
    if "checklist" not in comps:
        warn(1, ":::checklist (바로 써먹기)가 없다")
    if "## 출처" not in [l.strip() for l in lines]:
        err(len(lines), "## 출처 섹션이 없다")
    if not BODY_MIN <= body_chars <= BODY_MAX:
        warn(1, f"본문이 약 {body_chars}자다. {BODY_MIN}~{BODY_MAX}자를 목표로 한다")

    if len(images) > MAX_IMAGES:
        err(images[MAX_IMAGES][0], f"이미지가 {len(images)}개다. 최대 {MAX_IMAGES}개")
    if images:
        spec = post_path.with_name("images.md")
        listed = re.findall(r"^## 이미지 (\d+)", spec.read_text(encoding="utf-8"), re.M) if spec.exists() else []
        for n, num in images:
            if num not in listed:
                err(n, f"[[이미지 {num}]]의 설명이 images.md에 없다")

    return errors, warns, body_chars


def main():
    if len(sys.argv) != 2:
        sys.exit("사용법: lint_post.py <글 폴더 또는 post.md>")
    path = Path(sys.argv[1])
    post = path / "post.md" if path.is_dir() else path
    errors, warns, chars = lint(post)
    for line in errors + warns:
        print(line)
    print(f"검사 결과: 오류 {len(errors)}개, 경고 {len(warns)}개, 본문 약 {chars}자")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
