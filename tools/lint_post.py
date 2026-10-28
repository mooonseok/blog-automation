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


# AI 티 신호 (im-not-ai humanize-korean 규칙 차용, 우리 블로그 스타일과 맞는 것만. E-1 장문 섞기는 제외)
CONNECTIVE_COMMA = re.compile(r"[가-힣](고|며|지만|면서|아서|어서|려고)\s*,")   # C-11
CONJUNCTION = re.compile(r"(그리고|그러고|그러면서|그러며|하지만|그러나|그래서)\s*,")   # 문두 접속사는 C-11이 아님
CONTRAST = re.compile(r"아니라|것은 아니다|인가,")                                           # C-8
OUGHT_END = re.compile(r"(해야|어야|아야|여야) 한다[.!]?$")                                   # I-4
CLEFT = re.compile(r"(^|[.!?]\s+)(결국\s+)?(핵심은|중요한 것은|필요한 것은|관건은|문제는 바로)")   # D-8
SUMMING = re.compile(r"결론적으로|따라서|이를 통해|그러므로|요약하면|정리하자면")               # D-1
LIST_INTRO = re.compile(r"다음과 같")                                                       # D-3


def ends_with_n_da(sentence):
    """현재형 '~ㄴ다/~는다' 종결인지 (E-2). '다' 앞 글자의 받침이 ㄴ이면 해당."""
    s = re.sub(r"[\s\"”’)\]]+$", "", sentence).rstrip(".!?")
    if len(s) < 2 or not s.endswith("다"):
        return False
    ch = ord(s[-2]) - 0xAC00
    return 0 <= ch < 11172 and ch % 28 == 4


def ai_tells(prose, all_lines, paragraphs, err, warn):
    """prose: 문단·상자 글 [(행, 글)], all_lines: 목록·단계 포함 전부, paragraphs: [(시작 행, 문단 글)]"""
    for n, s in all_lines:
        if CONNECTIVE_COMMA.search(CONJUNCTION.sub("", strip_quoted(s))):
            err(n, "연결어미 뒤 쉼표다 (C-11). 쉼표를 지운다")
        if CLEFT.search(s):
            warn(n, "'핵심은 ~다' 분열문이다 (D-8). 주어-서술로 바로 쓴다")
        if LIST_INTRO.search(s):
            warn(n, "'다음과 같다' 열거 도입이다 (D-3). 무엇을 보여 주는지 구체적으로 쓴다")
    contrasts = [n for n, s in prose if CONTRAST.search(s)]
    if len(contrasts) >= 2:
        warn(contrasts[1], f"'A가 아니라 B' 대구가 {len(contrasts)}번이다 (C-8). 가장 좋은 1번만 남긴다 ({', '.join(map(str, contrasts))}행)")
    ought = [n for n, p in paragraphs if OUGHT_END.search(p.strip())]
    if len(ought) >= 2:
        warn(ought[1], f"'~해야 한다'로 끝나는 문단이 {len(ought)}개다 (I-4). 첫 번째 말고는 그 문장을 문단 앞·중간으로 옮긴다 ({', '.join(map(str, ought))}행)")
    summing = [n for n, s in all_lines if SUMMING.search(s)]
    if len(summing) > 3:
        warn(summing[3], f"'따라서·이를 통해' 같은 결산어가 {len(summing)}번이다 (D-1). 1~2번만 남긴다")
    run, start = 0, 0
    for n, s in prose:
        for sentence in re.split(r"(?<=[.!?])\s+", strip_quoted(s)):
            if not sentence.strip():
                continue
            if ends_with_n_da(sentence):
                run, start = run + 1, start if run else n
                if run == 4:
                    warn(start, "'~ㄴ다/~는다'로 끝나는 문장이 4번 이상 이어진다 (E-2). 종결을 바꿔 리듬을 깬다 (체언 종결, '~이다', 짧은 질문)")
            else:
                run = 0


def lint(post_path):
    errors, warns = [], []
    lines = post_path.read_text(encoding="utf-8").splitlines()
    err = lambda n, msg: errors.append(f"[오류] {n}행: {msg}")
    warn = lambda n, msg: warns.append(f"[경고] {n}행: {msg}")
    prose, all_lines, paragraphs = [], [], []   # prose: 문단·상자 글 (E-2·C-8용), all_lines: 목록·단계까지 전부

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
            paragraphs.append((para_start, plain(text)))
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
            elif no_comment:
                body_chars += len(plain(no_comment))
                text = plain(no_comment.split("|")[-1] if comp_name == "steps" else no_comment)
                all_lines.append((i, text))
                if comp_name in ("takeaway", "term", "tip", "warn", "quote"):
                    prose.append((i, text))
                    paragraphs.append((i, text))
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
            if not no_comment.startswith("|"):
                all_lines.append((i, plain(no_comment)))
            continue
        if not paragraph:
            para_start = i
        paragraph.append(no_comment)
        body_chars += len(plain(no_comment))
        prose.append((i, plain(no_comment)))
        all_lines.append((i, plain(no_comment)))
    flush()
    ai_tells(prose, all_lines, paragraphs, err, warn)

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
