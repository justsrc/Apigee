# Run 3 protocol: current-system performance evaluation

Frozen 2026-10-13 before any answer was collected. Commit the protocol before results, so
the rules that decide a verdict cannot be written after the verdicts are known.

## Research question

When the current Apigee support system handles the 103 scenarios in its own suite, what
percentage does it resolve under the project's documented grading rules?

This measures the **present system on the present suite**. It is not a skill A/B. The
selected skill baseline and the current skill were reported byte-identical in their always-
loaded `SKILL.md` files, so a comparison between them could not have produced a meaningful
effect, and no request is spent on one.

## Primary metric

    strict pass rate = PASS / (all scorable, completed) x 100

`MARGINAL` is not a strict pass. A scenario with a critical failure is failed regardless of
its numerical score.

Four more numbers are reported, never merged into a composite:

- **critical-failure-free rate** = no critical failure / (scorable, completed) x 100
- **mean normalized score**, unweighted mean across scorable completed scenarios
- **full-suite pass yield** = PASS / 103 x 100, the conservative figure
- **evaluability counts**: attempted, complete, graded, unscorable, infra-blocked

Mechanical test success is reported on its own. 34/34 mutation probes means the probes
detected the mutations they test. It does not mean the system answers 34 of 103 cases.

## Scoring route, resolved from the repository

`evaluation/rubric.md` documents two routes. Both are verified as present.

**Route 1 is canonical for this run.** `evaluation/model-eval-protocol.md` line 58 requires
"the scenario's own table, which wins where it differs from the general rubric", and
`rubric.md` "Running a scenario" step 4 repeats the precedence. Since all 103 scenarios ship
their own table, Route 1 applies everywhere and Route 2 is never used.

    scenario score = sum of anchors scored / (4 x number of rows in the table)

Verified before freezing:

| Property | Result |
|---|---|
| Scenarios with an `Evaluation rubric` section | 103 of 103 |
| Keys carrying `## Evaluation Rubric` | 103 of 103 |
| Table header shape | `Dimension \| 0 \| 2 \| 4` in all 103 |
| Malformed rows (wrong column count) | 0 |
| Row-count distribution | 3 rows: 5, 4 rows: 65, 5 rows: 28, 6 rows: 4, 7 rows: 1 |
| Keys with a critical-failure section | 103 of 103 |
| Keys carrying a `Not a critical failure` ruling | 2 scenarios (MED-09 and MED-11, 3 rulings between them) |

Thresholds, verified rather than assumed: **0.75 or above pass, 0.50 to 0.74 marginal, below
0.50 fail** (`rubric.md` Route 1 table, lines 133-137). These are the same 0.75 / 0.50 as
Route 2's weighted total, so a scenario-table result and a weighted result read against each
other.

Critical-failure override: mechanical, per `rubric.md` lines 186-194. Grade the dimensions
first, record them, then apply the override and report both. A grader reporting a pass on a
response with a recorded critical failure has made an error.

## Population

All 103 scenarios, both turns. Counts verified from the repository, not copied:

| Suite | Count |
|---| ---: |
| Easy | 15 |
| Medium | 45 |
| Hard | 22 |
| Adversarial | 13 |
| Regression | 8 |
| **Total** | **103** |

206 answer-generation requests if every scenario runs both turns. No scenario is dropped for
being hard, slow, or likely to fail. Adversarial and regression suites are included.

## Execution path

`opencode run` per turn, `cwd` set to the isolated workspace built by
`tests/make_eval_workspace.py`. The prompt is the generated turn packet, verbatim.

The workspace contains `.agents/skills/`, `prompts/`, `WORKSPACE.md`, `MANIFEST.json` and
`opencode.jsonc`. It does not contain `evaluation/`, `scenarios/`, `research/`, `archive/` or
`tests/`. Verified for this run: no structural failures, no leaks, no `*.key.md` anywhere.

Isolation configuration, written by the builder and part of the hashed artifact:

```jsonc
{ "action": "external_directory", "resource": "*", "effect": "deny" }
{ "action": "shell",             "resource": "*", "effect": "deny" }
{ "action": "edit",              "resource": "*", "effect": "deny" }
{ "action": "webfetch",          "resource": "*", "effect": "deny" }
{ "action": "websearch",         "resource": "*", "effect": "deny" }
{ "action": "subagent",          "resource": "*", "effect": "deny" }
```

One scenario per conversation. Turn 2 runs in the same conversation with the turn-2 packet as
a follow-up, so context carries within a scenario and does not leak across scenarios.

## Model

| Field | Value |
|---|---|
| Model id | `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free` |
| Version string | None published. The id is the only identifier. |
| Reproducibility | **Not bit-reproducible.** The provider does not pin weights. |
| Settings | `opencode run --auto --format json`. No other setting is exposed or pinned. |

The model id is recorded per request in `manifest.json` alongside timestamps, so a mid-run
routing change would be visible rather than silently averaged in.

## Budget

| Rule | Value |
|---|---|
| Attempts per 05:30-to-05:29 IST window | **45**, five below the reported 50 |
| On HTTP 429 | Stop the window. Never retry. No alternate route. |
| Retry | At most one, non-quota transient failures only |
| Paid routes | None exist in this harness. Not used, not offered |

Requests that fail still count. Provider failures are recorded as infrastructure, never as
model failures.

## Grading

Separate context from answer generation. The grader receives the turn-1 packet, both
responses, the frozen key and the frozen rubric, plus corpus access to settle disputed
claims. The answering model never receives any of it.

Second grader on a difficulty-stratified 20: 3 Easy, 9 Medium, 4 Hard, 2 Adversarial, 2
Regression. Chosen by fixed rule in `SECOND_GRADER_SAMPLE` of `grade_run.py`, before any
output or primary score is examined. Blinded to the primary grades.

Second grading is the lowest-priority consumer of the budget. If the quota cannot cover it
after primary grading, it is skipped and recorded as skipped. Never bought, never assumed.

Same model family on both sides means shared biases are not controlled. Stated as a
limitation, not smoothed over.

## Unscorable, and the freeze rule

If grading reveals an answer-key or rubric defect that materially prevents a verdict:

1. Record it in `defects-found-during-run.md`.
2. Mark the scenario `UNSCORABLE`.
3. **Do not edit the frozen material.**
4. Report it for repair in a later revision.

An invalid grading reference is never counted as a model failure, and a key is never repaired
mid-run and then graded as though it were always correct.

## Second-grader sample rule

Deterministic: sort each suite's scenario IDs, take every `n`-th so the spread covers easy,
medium and hard, and pin the resulting list in `grade_run.py` before grading starts.

## Resumption

`manifest.json` is authoritative for collection state. `WORKING-STATE.md` is a human summary
and never overrides it.

```bash
python3 evaluation/results/run-3/run_generation.py --list      # costs nothing
python3 evaluation/results/run-3/freeze_artifacts.py --verify \
    evaluation/results/run-3/artifact-hashes.json              # stops if artifacts moved
python3 evaluation/results/run-3/run_generation.py --batch 5   # spends requests
python3 evaluation/results/run-3/grade_run.py --list
python3 evaluation/results/run-3/grade_run.py --run
```

If the artifact verification fails, the run stops. Mixing material versions inside one result
is worse than an incomplete run.

## Limitations declared before collection

- An unpinned free model may change during a multi-window run. The same alias does not
  guarantee the same weights throughout.
- The 103 cases are deliberately authored, not a random sample of production tickets. The
  observed rate is a descriptive score for these cases, not a real-world incident rate.
- A separate grading context does not remove shared model bias.
- Current keys and rubric may still hold defects the checker suite cannot see. `check_repo.py`
  states this itself: ground-truth correctness and citation support need human review.
- Nothing here shows the skill caused the result.

## Pre-collection verification

Run before the first request. All executed 2026-10-13, zero model requests.

| Check | Result |
|---|---|
| `check_repo.py --root .` | exit 0, 26 passed, 0 failed, 0 warnings |
| `test_leakage.py` | exit 0, 206 prompt packets across 103 scenarios, no leak |
| `test_release_gate.py` | exit 0, 32 cases, 32 passed |
| `fault_probe.py` | exit 0, 34 probes, 34 behaved as expected, 0 false passes |
| `test_isolation_classify.py` | exit 0, 23 cases, 23 passed |
| `test_isolation.py` (structural) | structural PASS, exit 1 (live tier skipped by design) |
| Workspace leak scan | no failures, no `*.key.md`, no `evaluation/` or `scenarios/` |
| Rubric-route resolution | Route 1 required by protocol and rubric precedence |
| Key-section completeness | 103/103 rubric tables and critical-failure sections present |

**Not verified: live isolation.** The live tier needs 8 model requests and the free quota is
exhausted. It is a prerequisite and it is unmet. See `WORKING-STATE.md`.