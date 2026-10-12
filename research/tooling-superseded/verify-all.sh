#!/usr/bin/env bash
# Final verification pass: re-check every URL cited in the notes file and print
# "STATUS  BYTES  URL". Uses the same fetch logic (including stub detection) as
# fetch.sh / fetch-url.sh so a 200 that is really a devsite stub shows as 200-STUB.

set -uo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$here"

while IFS= read -r url; do
  [ -z "$url" ] && continue
  name="vfy-$(printf '%s' "$url" | md5 -q 2>/dev/null || printf '%s' "$url" | md5sum | cut -c1-8)"
  ./fetch-url.sh "$url" "$name" 2>/dev/null || echo "FAILED $url"
done
