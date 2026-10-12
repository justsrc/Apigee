#!/usr/bin/env bash
# Verify every URL cited in a skill, reference, or scenario.
#
# Why this is a script and not a habit. Fabricated and stale citations are the failure
# this project is built to prevent, and they are easy to miss by eye across 55 scenarios
# and three skills. A 200 is also not sufficient on its own: cloud.google.com serves a
# stub page reading "The equivalent page does not exist in Apigee" at HTTP 200, so every
# URL is fetched and its body checked too.
#
# The worker runs in check_url_one.sh. Two earlier versions of this script failed in
# instructive ways, and both guards below exist because of them:
#   - inlining the worker into `sh -c` exceeded the argument limit, xargs ran nothing, and
#     the script reported PASS having checked zero URLs
#   - a worker that printed only on failure made "all passed" and "nothing ran" identical
# So the worker always prints one line per URL, and the count is checked against the
# input count before any PASS is reported.
#
# Usage:
#   tests/check_urls.sh              # skills, references, scenarios, README, CHANGELOG
#   tests/check_urls.sh scenarios    # one path
#
# Exit 0 all good, 1 broken URLs found, 2 the checker itself failed.

set -uo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root" || exit 2

targets=(".agents/skills" "scenarios" "README.md" "CHANGELOG.md")
if [ "$#" -gt 0 ]; then targets=("$@"); fi

tmp_urls="$(mktemp)"
tmp_out="$(mktemp)"
trap 'rm -f "$tmp_urls" "$tmp_out"' EXIT

extract_urls() {
  # Skip fenced code blocks. A citation lives in prose, and a URL inside a code sample is
  # part of a string literal: a JavaScript sample containing
  # httpClient.send('https://example.net/x') was extracted as a citation with a trailing
  # apostrophe, which broke the xargs invocation with "unterminated quote" and made the
  # checker report a tooling failure instead of a result.
  awk '
    /^[[:space:]]*(```|~~~)/ { fence = !fence; next }
    fence { next }
    { print }
  ' | grep -ohE "https?://[^)\`>\"]+" \
    | sed "s/['\"]*$//; s/[.,]$//" \
    | grep -vE '[<>{}]|\$[A-Z_]+|YOUR_[A-Z_]+|<host>|\bORG_NAME\b' \
    | sort -u
}

for t in "${targets[@]}"; do
  if [ -d "$t" ]; then
    find "$t" -name '*.md' -exec cat {} +
  elif [ -f "$t" ]; then
    cat "$t"
  fi
done | extract_urls > "$tmp_urls"

# Placeholder URLs are illustrative, not citable, so they are filtered above rather than
# reported as broken. Two forms occur in practice: bracketed templates like
# http://<host>:8080/v1/o/<org>, and SCREAMING_CASE substitutions such as
# .../organizations/YOUR_ORG_NAME:setSyncAuthorization, and shell-style
# .../organizations/$ORG/environments/$ENV/... . Both are real documented API paths with
# the identifiers substituted, and the endpoints they name do exist, so fetching them
# without substitution returns 401 rather than 404 and tells us nothing.

total=$(wc -l < "$tmp_urls" | tr -d ' ')
if [ "$total" -eq 0 ]; then
  echo "no URLs found to check"
  exit 0
fi

echo "checking $total URLs"
xargs -P 8 -I{} "$root/tests/check_url_one.sh" {} < "$tmp_urls" > "$tmp_out"

checked=$(wc -l < "$tmp_out" | tr -d ' ')
if [ "$checked" -ne "$total" ]; then
  echo "RESULT: ERROR, checked $checked of $total URLs. The checker is broken, not the URLs."
  exit 2
fi

broken=$(grep -c -E '^(BROKEN|SOFT404|ERROR)' "$tmp_out" || true)
[ "$broken" -eq 0 ] || true

# 403 from a bot-blocking host is not a broken citation. Confirm each one through the
# Stack Exchange API, and fail if any cannot be confirmed.
blocked_unverified=$(grep -c '^BLOCKED-UNVERIFIED' "$tmp_out" || true)
[ "$blocked_unverified" -eq 0 ] || true
blocked_verified=$(grep -c '^BLOCKED-VERIFIED' "$tmp_out" || true)
[ "$blocked_verified" -eq 0 ] || true

if [ "$blocked_verified" -gt 0 ] || [ "$blocked_unverified" -gt 0 ]; then
  echo
  echo "bot-blocked, verified through the Stack Exchange API instead of curl:"
  grep -E '^BLOCKED' "$tmp_out" | sort | sed 's/^/  /'
  echo
fi

if [ "$blocked_unverified" -gt 0 ]; then
  echo "RESULT: FAIL, $blocked_unverified blocked URL(s) could not be confirmed to exist"
  exit 1
fi

if [ "$broken" -gt 0 ]; then
  echo
  echo "FAILURES ($broken of $total):"
  grep -E '^(BROKEN|SOFT404|ERROR)' "$tmp_out" | sort
  echo
  echo "RESULT: FAIL"
  exit 1
fi

echo "RESULT: PASS, all $total URLs resolved ($blocked_verified verified via API because curl is blocked)"