#!/usr/bin/env bash
# 글 폴더의 post.md를 주석을 뺀 상태로 클립보드에 복사하고 발행 정보를 보여 준다.
# 사용법: scripts/copy_post.sh posts/2026-10-28-<video_id>
set -euo pipefail

dir="${1:?사용법: scripts/copy_post.sh <글 폴더>}"
post="$dir/post.md"
[ -f "$post" ] || { echo "post.md 없음: $post" >&2; exit 1; }

pending=$(grep -c '확인 필요' "$post" || true)
if [ "$pending" -gt 0 ]; then
  echo "[주의] 확인 필요 표시가 ${pending}개 남아 있음:" >&2
  grep -n '확인 필요' "$post" >&2
  echo >&2
fi

# <!-- ... --> 주석(확인 필요, 내 생각, 왜: 등)은 발행본에서 뺀다
perl -0pe 's/^[ \t]*<!--.*?-->[ \t]*\n//gms; s/[ \t]*<!--.*?-->//gs; s/\n{3,}/\n\n/g' "$post" | pbcopy
echo "본문을 클립보드에 복사함 → 티스토리 글쓰기에서 마크다운 모드로 붙여넣기"
echo "글쓰기: https://moonesok.tistory.com/manage/newpost"
echo
[ -f "$dir/publish.md" ] && cat "$dir/publish.md"
