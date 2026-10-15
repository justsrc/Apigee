#!/usr/bin/env bash
# Fetch a Google Cloud Apigee doc page, record its real status, and extract the article
# body as Markdown.
#
# Three traps this script exists to handle. All three were hit for real during this
# project, and each one produces a wrong answer silently rather than an obvious failure.
#
# 1. Soft 404s. cloud.google.com answers HTTP 200 for paths that do not exist, with a
#    body reading "The equivalent page does not exist in Apigee". A status check alone
#    will index a dead page as live. Eight of these were found in one research sweep.
#
# 2. pandoc truncation. On the full ~840 KB page, pandoc 3.8 exits 0 and emits a few KB,
#    dropping every table after the first. It looks like a successful conversion.
#    Fixed by trimming to <div class="devsite-article-body"> before converting.
#
# 3. Guessed URLs. Nothing here can detect a bad guess except fetching it. Use link-tree
#    discovery (grep -oE '/apigee/docs/[a-zA-Z0-9/._-]+' on a page you already have)
#    instead of constructing paths from a naming pattern.
#
# Usage: ./fetch.sh <doc-path-without-extension> [output-name]
#   ./fetch.sh api-platform/reference/policies/quota-policy
#   ./fetch.sh hybrid/what-is-hybrid hybrid-what-is
#
# A path starting with http is fetched as an absolute URL. Edge for Private Cloud docs
# are NOT under cloud.google.com; they live on docs.apigee.com with the release in the
# path:
#   ./fetch.sh https://docs.apigee.com/private-cloud/v4.53.01/port-requirements
#
# Prints "STATUS<TAB>BYTES<TAB>URL" to stdout.
# Exit 0 ok | 1 not found (hard 404 or soft 404) | 2 extracted, but suspiciously small.

set -uo pipefail

path="${1:?usage: fetch.sh <doc-path-or-url> [out-name]}"
name="${2:-$(printf '%s' "$path" | tr '/:' '__')}"
case "$path" in
  http*) base="$path" ;;
  *) base="https://cloud.google.com/apigee/docs/${path}" ;;
esac
outdir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/pages"
mkdir -p "$outdir"

tmp="$(mktemp)"; body="$(mktemp)"; md="$(mktemp)"
trap 'rm -f "$tmp" "$body" "$md"' EXIT

status=$(curl -sL -o "$tmp" -w "%{http_code}" --max-time 60 "$base")

if [ "$status" != "200" ]; then
  rm -f "$outdir/$name.txt"
  printf '%s\t0\t%s\n' "$status" "$base"
  exit 1
fi

# Trap 1: soft 404.
if grep -qi 'equivalent page does not exist' "$tmp"; then
  rm -f "$outdir/$name.txt"
  printf '404(soft)\t0\t%s\n' "$base"
  exit 1
fi

# Trap 2: trim to the article body before pandoc, matching div nesting.
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

# Drop breadcrumbs by starting at the first H1, stop at the licence footer. If no H1 is
# present keep everything rather than emitting nothing.
awk '
    /^# / && !started { started=1 }
    started { print }
    /Except as otherwise noted, the content of this page is licensed/ { exit }
  ' "$md" > "$outdir/$name.txt"

if [ ! -s "$outdir/$name.txt" ]; then
  cp "$md" "$outdir/$name.txt"
fi

bytes=$(wc -c < "$outdir/$name.txt" | tr -d ' ')

# Normalise any HTML tables pandoc left behind, immediately. Running
# normalize_pages.py once as a separate batch is not enough: any page fetched afterwards
# reintroduces raw HTML tables, and every parser that reads pipe tables then silently
# skips that page's data. The verify-api-key page lost its entire runtime error table this
# way, which is how a real fault code went missing from the generated index.
if grep -q '<table' "$outdir/$name.txt" 2>/dev/null; then
  python3 "$(dirname "${BASH_SOURCE[0]}")/normalize_pages.py" --quiet \
    "$outdir/$name.txt" 2>/dev/null || true
  bytes=$(wc -c < "$outdir/$name.txt" | tr -d ' ')
fi

# Record the real URL. Deriving it back from the filename does not work: fetch.sh
# replaces slashes and colons with underscores, so the mapping is lossy and cannot be
# inverted. A manifest keeps the citation honest.
#
# The third column is the provenance of that URL, which is what the manifest's own
# header documents and what audit_manifest in tests/release_gate.py validates. This is
# the fetch-time recorder, so its value is "recorded". The byte count used to sit here;
# it describes the page, not the URL, and nothing reads it out of this column.
printf '%s\t%s\trecorded\n' "$name" "$base" >> "$outdir/MANIFEST.tsv"

if [ "$bytes" -lt 400 ]; then
  printf '200(SUSPECT %s bytes)\t%s\t%s\n' "$bytes" "$bytes" "$base" >&2
  exit 2
fi

printf '%s\t%s\t%s\n' "$status" "$bytes" "$base"