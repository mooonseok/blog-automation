#!/usr/bin/env python3
"""유튜브 링크에서 메타데이터와 자막을 가져와 글 작업 폴더에 저장한다.

사용법:
    .venv/bin/python .claude/skills/youtube-transcript/scripts/fetch_transcript.py <URL> [--out posts] [--lang ko,en]

출력:
    <out>/<YYYY-MM-DD>-<video_id>/meta.json       영상 정보 (제목, 채널, 챕터 등)
    <out>/<YYYY-MM-DD>-<video_id>/transcript.md   타임스탬프가 붙은 자막
마지막 줄에 작업 폴더 경로를 출력한다. 자막을 못 가져오면 종료 코드 2.
"""
import argparse
import datetime
import json
import re
import sys
import tempfile
from pathlib import Path

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

ID_PATTERNS = [
    r"(?:v=|/v/)([\w-]{11})",
    r"youtu\.be/([\w-]{11})",
    r"/(?:shorts|embed|live)/([\w-]{11})",
    r"^([\w-]{11})$",
]
BLOCK_SECONDS = 60  # 자막을 이 간격으로 묶어 한 문단으로 만든다


def parse_video_id(url):
    for pattern in ID_PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"유튜브 영상 ID를 찾을 수 없음: {url}")


def fetch_meta(url):
    opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    upload = info.get("upload_date")
    return {
        "id": info["id"],
        "url": info.get("webpage_url", url),
        "title": info.get("title"),
        "channel": info.get("channel") or info.get("uploader"),
        "upload_date": f"{upload[:4]}-{upload[4:6]}-{upload[6:]}" if upload else None,
        "duration_sec": info.get("duration"),
        "chapters": [
            {"title": c["title"], "start": int(c["start_time"])}
            for c in info.get("chapters") or []
        ],
        "tags": info.get("tags") or [],
        "description": info.get("description") or "",
    }


def fetch_with_api(video_id, langs):
    """youtube-transcript-api로 자막을 가져온다. 수동 자막을 자동 자막보다 우선한다."""
    transcripts = YouTubeTranscriptApi().list(video_id)
    try:
        transcript, kind = transcripts.find_manually_created_transcript(langs), "manual"
    except Exception:
        try:
            transcript, kind = transcripts.find_generated_transcript(langs), "auto"
        except Exception:
            transcript = next(iter(transcripts))
            kind = "auto" if transcript.is_generated else "manual"
    snippets = [(s.start, s.text) for s in transcript.fetch()]
    return snippets, transcript.language_code, kind


def parse_vtt(text):
    snippets, start, last = [], None, None
    for line in text.splitlines():
        stamp = re.match(r"(\d+):(\d+):(\d+)\.\d+ -->", line)
        if stamp:
            h, m, s = map(int, stamp.groups())
            start = h * 3600 + m * 60 + s
            continue
        clean = re.sub(r"<[^>]+>", "", line).strip()
        # 자동 자막은 같은 줄이 여러 번 반복되므로 직전 줄과 같으면 건너뛴다
        if start is None or not clean or clean == last:
            continue
        snippets.append((start, clean))
        last = clean
    return snippets


def fetch_with_ytdlp(url, langs):
    """API가 막혔을 때 yt-dlp로 자막 파일(vtt)을 내려받아 파싱한다."""
    # 한 언어가 실패(429 등)해도 다른 언어는 받을 수 있도록 언어별로 따로 요청한다
    for lang in langs:
        with tempfile.TemporaryDirectory() as tmp:
            opts = {
                "quiet": True,
                "no_warnings": True,
                "noprogress": True,
                "skip_download": True,
                "writesubtitles": True,
                "writeautomaticsub": True,
                "subtitleslangs": [lang],
                "subtitlesformat": "vtt",
                "outtmpl": f"{tmp}/%(id)s.%(ext)s",
            }
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
            except yt_dlp.utils.DownloadError:
                continue
            files = list(Path(tmp).glob(f"*.{lang}*.vtt"))
            if files:
                return parse_vtt(files[0].read_text(encoding="utf-8")), lang, "unknown"
    raise RuntimeError("yt-dlp로도 자막을 찾지 못함")


def timestamp(sec):
    sec = int(sec)
    h, m, s = sec // 3600, sec % 3600 // 60, sec % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def to_paragraphs(snippets):
    blocks, current, block_start = [], [], None
    for start, text in snippets:
        if block_start is None:
            block_start = start
        if start - block_start >= BLOCK_SECONDS and current:
            blocks.append((block_start, " ".join(current)))
            current, block_start = [], start
        current.append(text.replace("\n", " "))
    if current:
        blocks.append((block_start, " ".join(current)))
    return blocks


def render_markdown(meta, snippets, lang, kind):
    lines = [
        f"# {meta['title']}",
        "",
        f"- 채널: {meta['channel']}",
        f"- 업로드: {meta['upload_date']}",
        f"- 길이: {timestamp(meta['duration_sec'] or 0)}",
        f"- URL: {meta['url']}",
        f"- 자막: {lang} ({kind})",
        "",
    ]
    if meta["chapters"]:
        lines += ["## 챕터", ""]
        lines += [f"- [{timestamp(c['start'])}] {c['title']}" for c in meta["chapters"]]
        lines.append("")
    lines += ["## 자막", ""]
    for start, text in to_paragraphs(snippets):
        lines += [f"[{timestamp(start)}] {text}", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("url")
    parser.add_argument("--out", default="posts")
    parser.add_argument("--lang", default="ko,en", help="선호 자막 언어, 쉼표로 구분")
    args = parser.parse_args()
    langs = args.lang.split(",")

    video_id = parse_video_id(args.url)
    meta = fetch_meta(args.url)

    try:
        snippets, lang, kind = fetch_with_api(video_id, langs)
    except Exception as api_error:
        print(f"[알림] transcript API 실패, yt-dlp로 재시도: {api_error}", file=sys.stderr)
        try:
            snippets, lang, kind = fetch_with_ytdlp(args.url, langs)
        except Exception as error:
            print(f"[실패] 자막을 가져올 수 없음: {error}", file=sys.stderr)
            print("자막이 없는 영상은 음성 인식(Whisper) 단계가 필요함 (로드맵 참고)", file=sys.stderr)
            sys.exit(2)

    today = datetime.date.today().isoformat()
    workdir = Path(args.out) / f"{today}-{video_id}"
    workdir.mkdir(parents=True, exist_ok=True)
    meta["transcript"] = {"lang": lang, "kind": kind, "snippets": len(snippets)}
    (workdir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (workdir / "transcript.md").write_text(
        render_markdown(meta, snippets, lang, kind), encoding="utf-8"
    )
    print(f"제목: {meta['title']} / 자막 {lang} ({kind}), {len(snippets)}줄")
    print(workdir)


if __name__ == "__main__":
    main()
