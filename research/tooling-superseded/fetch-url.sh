#!/usr/bin/env bash
# Same contract as fetch.sh, but takes a FULL url instead of an /apigee/docs/ path.
# Needed because the gcloud reference lives under /sdk/gcloud/reference/apigee and
# fetch.sh hardcodes the /apigee/docs/ prefix.
#
# Logic mirrors the hardened fetch.sh: devsite returns HTTP 200 for paths that do not
# exist in the selected version, with a "The equivalent page does not exist" body.
# A bare 200 is therefore NOT proof a page exists, so this script checks for that stub.
#
# Usage: ./fetch-url.sh <full-url> [output-name]
# Prints "STATUS<TAB>BYTES<TAB>URL". Exits 0 on 200-with-content, 1 otherwise.

set -uo pipefail

url="${1:?usage: fetch-url.sh <full-url> [out-name]}"
name="${2:-$(printf '%s' "$url" | sed -e 's#^https://##' -e 's#[/?&=]#_#g' -e 's#.*/##')}"
outdir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/pages"
mkdir -p "$outdir"
tmp="$(mktemp)"

status=$(curl -sL -o "$tmp" -w "%{http_code}" "$url")

if [ "$status" != "200" ]; then
  rm -f "$tmp" "$outdir/$name.txt"
  printf '%s\t0\t%s\n' "$status" "$url"
  exit 1
fi

if grep -q 'The equivalent page does not exist in the selected' "$tmp"; then
  rm -f "$tmp" "$outdir/$name.txt"
  printf '200-STUB\t0\t%s\n' "$url"
  exit 1
fi

# pandoc 3.8 silently truncates very large pages; trim to the article body first.
body="$(mktemp)"
python3 - "$tmp" "$body" <<'PY'
import sys, re
html = open(sys.argv[1], encoding="utf-8", errors="replace").read()
m = re.search(r'<div[^>]*class="[^"]*devsite-article-body[^"]*"[^>]*>', html)
if m:
    start = m.end()
    depth, i = 1, start
    for t in re.finditer(r'<(/?)div\b[^>]*>', html[start:]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            i = start + t.start()
            break
    else:
        i = len(html)
    html = html[start:i]
open(sys.argv[2], "w", encoding="utf-8", errors="replace").write(html)
PY

md="$(mktemp)"
pandoc -f html -t gfm --wrap=none "$body" 2>/dev/null > "$md"

awk '
    /^# / && !started { started=1 }
    started { print }
    /Except as otherwise noted, the content of this page is licensed/ { exit }
  ' "$md" > "$outdir/$name.txt"

if [ ! -s "$outdir/$name.txt" ]; then
  cp "$md" "$outdir/$name.txt"
fi

rm -f "$tmp" "$body" "$md"
printf '%s\t%s\t%s\n' "$status" "$(wc -c < "$outdir/$name.txt" | tr -d ' ')" "$url"
