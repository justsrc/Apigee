#!/usr/bin/env bash
# Fetch a GitHub issue and ALL of its comments as plain text, so the note cites
# something that was actually read rather than a search snippet.
#
# Usage: ./gh-issue.sh OWNER/REPO NUMBER [out-name]
#
# Prints "STATUS<TAB>comments<TAB>url" to stdout.
# Exit 0 ok | 1 issue not fetchable.

set -uo pipefail
ref="${1:?usage: gh-issue.sh OWNER/REPO NUMBER [out-name]}"
num="${2:?usage: gh-issue.sh OWNER/REPO NUMBER [out-name]}"
name="${3:-$(printf '%s' "$ref-$num" | tr '/' '_')}"
outdir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/issues"
mkdir -p "$outdir"

issue=$(gh api "repos/$ref/issues/$num" 2>/dev/null) || {
  printf '404\t0\thttps://github.com/%s/issues/%s\n' "$ref" "$num"; exit 1; }

comments=$(gh api "repos/$ref/issues/$num/comments?per_page=100" 2>/dev/null)
ncomments=$(printf '%s' "$comments" | python3 -c 'import json,sys; print(len(json.load(sys.stdin)))' 2>/dev/null || echo 0)

out="$outdir/$name.txt"
{
  printf '%s\n' "$issue" | python3 -c '
import json,sys
d=json.load(sys.stdin)
print("URL:", d.get("html_url"))
print("TITLE:", d.get("title"))
print("STATE:", d.get("state"), "state_reason:", d.get("state_reason"))
print("AUTHOR:", (d.get("user") or {}).get("login"), "association:", (d.get("author_association")))
print("CREATED:", d.get("created_at"), "CLOSED:", d.get("closed_at"))
print("LABELS:", ", ".join(l.get("name","") for l in d.get("labels",[])))
print("MILESTONE:", (d.get("milestone") or {}).get("title"))
print("--- BODY ---")
print(d.get("body") or "")
'
  printf '\n--- COMMENTS (%s) ---\n' "$ncomments"
  printf '%s' "$comments" | python3 -c '
import json,sys
for c in json.load(sys.stdin):
    print("\n### comment by %s (association=%s) at %s" % ((c.get("user") or {}).get("login"), c.get("author_association"), c.get("created_at")))
    print(c.get("body") or "")
'
} > "$out"

printf '%s\t%s\thttps://github.com/%s/issues/%s\n' "$(printf '%s' "$issue" | python3 -c 'import json,sys;print(json.load(sys.stdin).get("state"))')" "$ncomments" "$ref" "$num"
