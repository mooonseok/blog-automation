#!/usr/bin/env bash
# 글 폴더의 post.md를 주석을 뺀 상태로 클립보드에 복사하고 발행 정보를 보여 준다.
# 사용법:
#   scripts/copy_post.sh            가장 최근 글
#   scripts/copy_post.sh u2oDdU6z   폴더 이름 일부(영상 ID, 날짜 등)로 찾기
set -euo pipefail

cd "$(dirname "$0")/.."

if [ $# -eq 0 ]; then
  dir=$(ls -d posts/*/ 2>/dev/null | sort | tail -1)
elif [ -d "$1" ]; then
  dir="$1"
else
  matches=$(ls -d posts/*"$1"*/ 2>/dev/null || true)
  count=$(printf '%s' "$matches" | grep -c . || true)
  if [ "$count" -gt 1 ]; then
    echo "여러 글이 일치함, 더 구체적으로 입력:" >&2
    echo "$matches" >&2
    exit 1
  fi
  dir="$matches"
fi
[ -n "$dir" ] || { echo "글 폴더를 찾을 수 없음: ${1:-posts/}" >&2; exit 1; }
dir="${dir%/}"
echo "대상: $dir"

post="$dir/post.md"
[ -f "$post" ] || { echo "post.md 없음: $post" >&2; exit 1; }

pending=$(grep -o '확인 필요' "$post" | wc -l | tr -d ' ')
if [ "$pending" -gt 0 ]; then
  echo "[주의] 확인 필요 표시가 ${pending}개 남아 있음:" >&2
  grep -n '확인 필요' "$post" >&2
  echo >&2
fi

# <!-- ... --> 주석(확인 필요, 내 생각, 왜: 등)은 발행본에서 뺀다
perl -0pe 's/^[ \t]*<!--.*?-->[ \t]*\n//gms; s/[ \t]*<!--.*?-->//gs; s/\n{3,}/\n\n/g' "$post" | LC_ALL=en_US.UTF-8 pbcopy
echo "본문을 클립보드에 복사함 → 티스토리 글쓰기에서 마크다운 모드로 붙여넣기"
echo "글쓰기: https://moonesok.tistory.com/manage/newpost"
echo
[ -f "$dir/publish.md" ] && cat "$dir/publish.md"
