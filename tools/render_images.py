#!/usr/bin/env python3
"""글 폴더 images/image-N.svg를 로컬에서 PNG로 변환한다. API·네트워크 사용 없음."""
import re
import shutil
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree as ET


def render_images(post):
    sources = sorted(p for p in (post / "images").glob("image-*.svg")
                     if re.fullmatch(r"image-[12]\.svg", p.name))
    if not sources:
        print("로컬 이미지: 계획된 SVG 없음")
        return
    converter = shutil.which("rsvg-convert")
    if not converter:
        print("로컬 이미지: SVG 보관 완료. PNG 변환에는 rsvg-convert가 필요합니다 (macOS: brew install librsvg)")
        return
    for source in sources:
        target = source.with_suffix(".png")
        try:
            raw = source.read_text(encoding="utf-8")
            if "<!DOCTYPE" in raw.upper() or "<!ENTITY" in raw.upper():
                raise ValueError("외부 엔티티를 포함한 SVG")
            root = ET.fromstring(raw)
            if root.tag.rsplit("}", 1)[-1] != "svg":
                raise ValueError("SVG 루트가 아님")
            for node in root.iter():
                if node.tag.rsplit("}", 1)[-1] in ("script", "foreignObject", "image", "style"):
                    raise ValueError("외부 리소스·스크립트·스타일 블록은 사용하지 않음")
                for key, value in node.attrib.items():
                    if key.rsplit("}", 1)[-1].startswith("on") or key.rsplit("}", 1)[-1] == "href" and not value.startswith("#"):
                        raise ValueError("외부 참조 또는 이벤트 속성")
                    if any(not ref.strip(" '\"").startswith("#") for ref in re.findall(r"url\(([^)]*)\)", value)):
                        raise ValueError("외부 URL 참조")
            if target.exists() and target.stat().st_mtime >= source.stat().st_mtime:
                print(f"로컬 이미지 재사용: {target}")
                continue
            temp = target.with_suffix(".tmp.png")
            try:
                subprocess.run([converter, "--width", "1400", "--output", str(temp), str(source)],
                               check=True, capture_output=True, timeout=45)
                if temp.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
                    raise ValueError("PNG 출력 확인 실패")
                temp.replace(target)
            finally:
                temp.unlink(missing_ok=True)
            print(f"로컬 이미지 생성: {target}")
        except (ValueError, OSError, ET.ParseError, subprocess.SubprocessError) as exc:
            print(f"이미지 변환 보류: {source.name} ({type(exc).__name__}: {exc})")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("사용법: render_images.py <글 폴더>")
    render_images(Path(sys.argv[1]))
