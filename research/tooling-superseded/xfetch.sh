#!/usr/bin/env bash
# Fetch + robustly extract, recording a real HTTP status per URL.
# Usage: ./xfetch.sh <doc-path-without-extension> [out-name]
# Prints "STATUS<TAB>BYTES<TAB>HTML_HEADINGS<TAB>MD_HEADINGS<TAB>URL"
# Exits non-zero on non-200 or on heading loss (truncation).
set -uo pipefail

path="${1:?usage: xfetch.sh <doc-path> [out-name]}"
name="${2:-$(printf '%s' "$path" | tr '/' '_')}"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
base="https://cloud.google.com/apigee/docs/${path}"
mkdir -p "$here/.html"
tmp="$here/.html/$name.html"

status=$(curl -sL -o "$tmp" -w "%{http_code}" "$base")
if [ "$status" != "200" ]; then
  rm -f "$tmp" "$here/pages/$name.txt"
  printf '%s\t0\t-\t-\t%s\n' "$status" "$base"
  exit 1
fi

read -r bytes hin hout <<<"$(python3 "$here/extract.py" "$tmp" "$name" | cut -f2-4)"
printf '%s\t%s\t%s\t%s\t%s\n' "$status" "$bytes" "$hin" "$hout" "$base"
[ "$hin" = "$hout" ]