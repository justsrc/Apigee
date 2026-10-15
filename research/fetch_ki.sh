#!/usr/bin/env bash
# Robust fetch for the known-issues research pass.
# Usage: ./fetch_ki.sh <doc-path-or-url> [out-name]
# Retries up to 3 times with backoff. Distinguishes network failure from a genuine 404.
set -uo pipefail

path="${1:?usage: fetch_ki.sh <doc-path-or-url> [out-name]}"
name="${2:-$(printf '%s' "$path" | tr '/:' '__')}"
case "$path" in
  http*) base="$path" ;;
  *) base="https://cloud.google.com/apigee/docs/${path}" ;;
esac
outdir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/pages"
mkdir -p "$outdir"

tmp="$(mktemp)"; body="$(mktemp)"; md="$(mktemp)"
trap 'rm -f "$tmp" "$body" "$md"' EXIT

status=""
for attempt in 1 2 3; do
  status=$(curl -sL -o "$tmp" -w "%{http_code}" --max-time 90 "$base" 2>/dev/null)
  rc=$?
  if [ "$rc" -eq 0 ] && [ "$status" = "200" ]; then break; fi
  echo "attempt $attempt: curl_rc=$rc status=$status for $base" >&2
  sleep $((attempt * 3))
done

if [ "$status" != "200" ]; then
  rm -f "$outdir/$name.txt"
  printf '%s\t0\t%s\n' "${status:-NETFAIL}" "$base"
  exit 1
fi

if grep -qi 'equivalent page does not exist' "$tmp"; then
  rm -f "$outdir/$name.txt"
  printf '404(soft)\t0\t%s\n' "$base"
  exit 1
fi

python3 - "$tmp" "$body" <<'PY'
import sys, re
html = open(sys.argv[1], encoding="utf-8", errors="replace").read()
m = re.search(r'<div[^>]*class="[^"]*devsite-article-body[^"]*"[^>]*>', html)
if m:
    start = m.end()
    depth, end = 1, len(html)
    for t in re.finditer(r'<(/?)div\b[^>]*>', html[start:]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            end = start + t.start()
            break
    html = html[start:end]
open(sys.argv[2], "w", encoding="utf-8").write(html)
PY

pandoc -f html -t gfm --wrap=none "$body" 2>/dev/null > "$md"

awk '
    /^# / && !started { started=1 }
    started { print }
    /Except as otherwise noted, the content of this page is licensed/ { exit }
  ' "$md" > "$outdir/$name.txt"

if [ ! -s "$outdir/$name.txt" ]; then cp "$md" "$outdir/$name.txt"; fi

bytes=$(wc -c < "$outdir/$name.txt" | tr -d ' ')
if grep -q '<table' "$outdir/$name.txt" 2>/dev/null; then
  python3 "$(dirname "${BASH_SOURCE[0]}")/normalize_pages.py" --quiet \
    "$outdir/$name.txt" 2>/dev/null || true
  bytes=$(wc -c < "$outdir/$name.txt" | tr -d ' ')
fi

printf '%s\t%s\trecorded\n' "$name" "$base" >> "$outdir/MANIFEST.tsv"
printf '%s\t%s\t%s\n' "$status" "$bytes" "$base"
