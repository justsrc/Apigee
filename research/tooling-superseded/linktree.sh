#!/usr/bin/env bash
# Print the doc link tree found in a page's raw HTML (fetched pages are trimmed to
# the article body, which removes the nav sidebar that carries the link tree).
#
# Usage: ./linktree.sh <full-url> [prefix-filter-regex]
#   ./linktree.sh https://cloud.google.com/apigee/docs/api-platform/deploy/ui-deploy-overview '^/apigee/docs/api-platform/deploy'

set -uo pipefail
url="${1:?usage: ./linktree.sh <url> [prefix-regex]}"
filter="${2:-}"
tmp="$(mktemp)"
curl -sL -o "$tmp" "$url"
if [ -n "$filter" ]; then
  grep -oE '(https://cloud.google.com)?/apigee/docs/[a-zA-Z0-9/._-]+' "$tmp"
else
  grep -oE '(https://cloud.google.com)?/apigee/docs/[a-zA-Z0-9/._-]+' "$tmp"
fi | sed -e 's#^https://cloud.google.com##' | sort -u
rm -f "$tmp"
