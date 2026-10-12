#!/usr/bin/env bash
# Worker for check_urls.sh. Kept as its own file because inlining this into `xargs sh -c`
# pushes the command past the platform's argument limit, which makes xargs refuse to run
# at all and the parent script report a PASS having checked nothing. A false pass is worse
# than a failure in a tool whose only job is to catch broken citations.
#
# Usage: check_url_one.sh <url>
#
# Prints exactly one line per URL, always. A worker that prints nothing on success makes
# it impossible for the parent to distinguish "everything passed" from "nothing ran",
# which is precisely how the earlier version of this checker reported PASS having
# verified nothing.

set -uo pipefail

url="$1"
page="$(mktemp)" || { printf 'ERROR\tmktemp-failed\t%s\n' "$url"; exit 0; }
trap 'rm -f "$page"' EXIT

code=$(curl -sL -o "$page" -w "%{http_code}" --max-time 25 "$url" 2>/dev/null)

# stackoverflow.com answers 403 to curl via Cloudflare, including for questions that
# demonstrably exist. Verified against three: the Stack Exchange API returns all three.
# 403 is "exists but refuses bots", which is a different claim from 404, so it gets its
# own status and is confirmed through the API rather than reported as a broken citation.
if [ "$code" = "403" ]; then
  case "$url" in
    https://stackoverflow.com/questions/*)
      qid=$(printf '%s' "$url" | sed 's|.*/questions/||; s|/.*||')
      title=$(curl -sL --max-time 20 \
        "https://api.stackexchange.com/2.3/questions/${qid}?site=stackoverflow&filter=default" \
        2>/dev/null \
        | sed -n 's/.*"title":"\([^"]*\)".*/\1/p' | head -1)
      if [ -n "$title" ]; then
        printf 'BLOCKED-VERIFIED\t200\t%s\n' "$url"
      else
        printf 'BLOCKED-UNVERIFIED\t403\t%s\n' "$url"
      fi
      ;;
    *) printf 'BLOCKED\t403\t%s\n' "$url" ;;
  esac
  exit 0
fi

if [ "$code" != "200" ]; then
  printf 'BROKEN\t%s\t%s\n' "$code" "$url"
elif grep -qi 'equivalent page does not exist' "$page"; then
  printf 'SOFT404\t200\t%s\n' "$url"
else
  printf 'OK\t200\t%s\n' "$url"
fi

exit 0