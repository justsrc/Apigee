# Run 3 working state

Authoritative record of what has been collected: `manifest.json`. This file is a human
summary and never overrides it. The raw responses under `raw/` are the evidence.

## Status: BLOCKED before collection. Zero answers collected.

**No performance number exists yet, and none is reported.** The free-model quota was
exhausted at the moment of the preflight, before a single scenario ran.

## Frozen base

| Field | Value |
|---|---|
| Base commit | `a25333b55b2f7e90b44b2313927be2331db5a9fb` (pre-rewrite history) |
| Branch | `v0.1` |
| Skill digest | `ba3500db7ca1755d` |
| Rubric | `evaluation/rubric.md`, Route 1 canonical |
| Protocol | `evaluation/results/run-3/PROTOCOL.md`, frozen 2026-10-13 before collection |
| Artifact hashes | `artifact-hashes.json` |

## Model

| Field | Value |
|---|---|
| Model id | `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free` |
| Version string | None published |
| Bit-reproducible | No. The provider does not pin weights. |

## The blocker

Preflight at 2026-10-13 23:26 IST, one request:

```
provider.rate-limit, HTTP 429
X-RateLimit-Limit: 50   X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1791936000000  = 2026-10-14 05:30 IST
```

Quota resets in about 6 hours from the preflight. Rules for this run: a 429 stops the window,
is never retried, and never triggers a paid route. Requests spent so far: **1 of 45**
(the preflight itself).

## What is done, at zero request cost

| Item | State |
|---|---|
| Artifact freeze and hash manifest | done, `artifact-hashes.json` |
| Scenario counts verified | 15 / 45 / 22 / 13 / 8 = 103 |
| Scoring route resolved from repo docs | Route 1, required by protocol and rubric precedence |
| Pass and marginal thresholds verified | 0.75 pass, 0.50 marginal |
| All 103 rubric tables present and well-formed | verified, `Dimension \| 0 \| 2 \| 4` |
| Critical-failure sections present in keys | 103 of 103 |
| Grading math unit-tested against fixtures | 11 cases, including the 0.75 edge and the override |
| Second-grader sample fixed by rule | 20 cases, stratified, chosen before any output |
| Workspace isolation, structural | no leaks, no answer keys reachable |
| Generation harness | `run_generation.py`, manifest-backed, resumable |
| Grading scaffold | `grade_run.py`, computes only what the rubric computes |
| Protocol frozen and committed | `PROTOCOL.md` |

## What is NOT done

- **Zero of 103 scenarios generated.** Nothing to grade.
- **Live isolation unverified.** The live tier costs 8 requests and needs a live model. It is
  a prerequisite for a tool-enabled run and it is currently unmet. The two earlier attempts,
  on 2026-10-13, returned 8 `INDETERMINATE` routes each on provider quota errors. An
  `INDETERMINATE` is not a denial.
- No pass rate, no critical-failure rate, no mean score, no per-suite breakdown. All of those
  require answers.

## Prerequisite before resumption

1. Quota window has reset (after 2026-10-14 05:30 IST).
2. Run the live isolation probe first and require a result that is not a breach:
   ```bash
   python3 tests/test_isolation.py --live --raw-dir /tmp/iso-evidence-run-3
   ```
   If it is again `INDETERMINATE` for quota reasons, the tool-enabled run is not
   leakage-resistant and must not be reported as if it were. Record that and stop.
3. Verify artifacts have not moved:
   ```bash
   python3 evaluation/results/run-3/freeze_artifacts.py \
       --verify evaluation/results/run-3/artifact-hashes.json
   ```

## Next command, in order

```bash
python3 tests/test_isolation.py --live --raw-dir /tmp/iso-evidence-run-3   # 8 requests
python3 evaluation/results/run-3/run_generation.py --list                   # free
python3 evaluation/results/run-3/run_generation.py --batch 5               # up to 10
```

Then grade, in a separate context, once answers exist:

```bash
python3 evaluation/results/run-3/grade_run.py --list
python3 evaluation/results/run-3/grade_run.py --run --grader primary --scores <file>
```

## Budget reality

Full suite, both turns: 206 generation requests. Live isolation: 8. Primary grading: 103.
Second grading: 20. **337 total**, against 45 per window, so roughly eight windows. This
cannot be finished in one session and is not meant to be. Each session adds a batch,
checkpoints, and stops.

## Rules for whoever resumes

- Do not re-run a completed scenario because its answer looks inconvenient.
- Do not edit scenarios, keys, rubric or the skill during collection. A defect goes in
  `defects-found-during-run.md` and the scenario is marked `UNSCORABLE`.
- Do not report a partial run as a full-suite percentage. Give the denominator.
- Do not convert an infra failure into a model failure.