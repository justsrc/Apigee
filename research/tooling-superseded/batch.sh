#!/usr/bin/env bash
# Fetch many doc paths in parallel through fetch.sh and log real statuses.
# Usage: ./batch.sh path1 path2 ...   (one path per arg)
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

for path in "$@"; do
  ( ./fetch.sh "$path" ) &
  while [ "$(jobs -rp | wc -l | tr -d ' ')" -ge 6 ]; do wait -n; done
done
wait