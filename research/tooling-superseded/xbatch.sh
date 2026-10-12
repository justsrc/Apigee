#!/usr/bin/env bash
# Fetch many doc paths in parallel through xfetch.sh and log real statuses.
# Usage: ./xbatch.sh path1 path2 ...
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

for path in "$@"; do
  ( ./xfetch.sh "$path" ) &
  while [ "$(jobs -rp | wc -l | tr -d ' ')" -ge 6 ]; do wait -n; done
done
wait