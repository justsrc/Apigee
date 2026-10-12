#!/usr/bin/env bash
# Verify every URL cited in a skill, reference, or scenario.
#
# This is now a thin wrapper. The classification lives in tests/check_urls.py, which
# distinguishes a soft 404 from a genuine 404, an access restriction from a missing page,
# and a transient failure from a broken citation, and which records redirect chains.
#
# Two earlier versions of this script failed in instructive ways, and the guards they
# needed are now properties of the Python checker:
#   - inlining the worker into `sh -c` exceeded the argument limit, xargs ran nothing, and
#     the script reported PASS having checked zero URLs
#   - a worker that printed only on failure made "all passed" and "nothing ran" identical
#   - a corpus with zero URLs exited 0, which is a passing URL audit that verified nothing
#
# Usage:
#   tests/check_urls.sh                  # skills, references, scenarios, README, CHANGELOG
#   tests/check_urls.sh scenarios        # one or more paths
#   tests/check_urls.sh --fixtures       # offline classifier fixtures, no network
#
# Exit 0 all verified, 1 broken or unconfirmed, 2 the checker itself could not run.

set -uo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

exec python3 "$root/tests/check_urls.py" "$@"