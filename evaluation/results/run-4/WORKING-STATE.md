# Run 4 pilot: state

Written 2026-10-14 00:00 IST, before any answer was collected. Protocol:
`evaluation/results/run-4/PILOT-PROTOCOL.md`.

## Status: NO PERFORMANCE RESULT. Blocked before generation.

Zero answers collected. No pass rate exists and none is reported.

## Why

| Route | State | Evidence |
|---|---|---|
| `openrouter/*:free` | **Closed** | Daily window resets 2026-10-14 05:30 IST; 5.5 hours away at time of writing |
| `opencode/space-bunny-free` | **Usable but burst-limited** | Works when requests are spaced; returns a misleading `provider.auth` rate-limit error when they are not |
| Subagent | **NO-GO** | Earlier probe: 4 reads attempted, 4 succeeded, answer key returned in full, 0 denials |

## Requests spent on this pilot

**Zero.** Every route investigation was either a local command or a provider-availability
probe, and the provider probes were not scenario generation. No prompt packet was sent to any
model.

## What is complete and costs nothing

| Item | State |
|---|---|
| Pilot protocol, frozen before collection | `PILOT-PROTOCOL.md` |
| Sample of 12 fixed by rule, spanning all 5 suites | done |
| All 12 verified gradable: packets, key, rubric table, critical failures | done, row counts 3 to 7 |
| Thresholds verified against the frozen rubric | 0.75 pass, 0.50 marginal |
| 12 deterministic isolation checks on the real production path | pass |
| Multi-turn session continuity defect found and fixed | commit `cbe11b8` |
| Workspace banner leak of the ID-to-title lookup removed | commit `4098ec4` |
| Provider-error misclassification pinned | 429 and the misleading `provider.auth` both INDETERMINATE |

## Isolation position

**Structurally isolated. NOT leakage-resistant.**

12 deterministic checks pass on the real production path: no protected path present, no
answer key anywhere in the tree, the real structural checker clean, the enforcing config
denying `external_directory`/`shell`/`edit`/`webfetch`/`websearch`/`subagent`, no `.git`, the
skill byte-identical, manifest checksums pinning the build, and no prompt containing its own
scenario title.

**Live breach testing is INCONCLUSIVE.** Three attempts to breach the boundary against the
working route all returned a provider error. A provider error is not a denial. The boundary
has not been demonstrated to hold against a model trying to cross it, and the pilot report
must not use the word "leakage-resistant".

## Next commands, in order, once a route is available

```bash
python3 tests/test_isolation.py --live --raw-dir /tmp/iso-evidence-run-4   # must not BREACH
python3 evaluation/results/run-3/freeze_artifacts.py \
    --verify evaluation/results/run-3/artifact-hashes.json
```

Then a paced single-scenario smoke test before the 12-case batch:

```bash
python3 evaluation/results/run-3/run_generation.py --only MED-13 \
    --model opencode/space-bunny-free
```

Verify the turn-2 response builds on turn 1 before spending the remaining 11. If turn 2 comes
back cold, the session-continuity fix did not take and the batch must not run.

## Rules for resumption

- Pace requests. The route is burst-limited and reports it as `provider.auth`.
- A rate-limited response closes the attempt. Do not retry inside the window.
- Never record a provider error, empty response, or ungradable answer as a pass.
- If gradeable answers end up zero, report the pass rate as **unmeasured**, not 0%.
- Do not widen the sample or swap scenarios once results are visible.