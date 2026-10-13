# Run 4 pilot protocol: smallest defensible success-rate estimate

Written 2026-10-13 before any answer was collected, in response to a request for the
cheapest experiment that measures how often the harness produces a passing answer.

Run 3 is left intact. This is a separate, smaller run with a different question and a
different execution route. `evaluation/results/RUNS.md` records both.

## The question this pilot can and cannot answer

**Can.** For a declared sample of 12 scenarios, how often does the current harness produce an
answer that passes the frozen rubric, and how often does it fail for operational reasons
rather than technical ones.

**Cannot.** Anything about all 103 scenarios, and anything about the skill. The always-loaded
`SKILL.md` files were byte-identical across the selected remediation baseline, so there is no
comparison to run and no request will be spent pretending otherwise.

Twelve cases cannot produce a tight interval. At an observed 50% pass rate the 95% Wilson
interval spans roughly 25 to 75 points. That is the honest precision and the report will say
so rather than quoting a point estimate alone.

## Why this route

`opencode/*` works from the headless CLI and is a different provider from the OpenRouter free
tier whose daily quota is exhausted. Evidence is in `evaluation/WORKING-STATE.md` and the
addendum to `evaluation/isolation-report.md`.

The constraint is burst rate limiting, not entitlement. Requests are therefore paced, and a
rate-limited request is recorded and the batch is stopped rather than retried inside the
window.

## Sample: 12 scenarios, fixed by rule, chosen before any output exists

One scenario per suite band, spread across the ID range so difficulty is not clustered.
Deterministic selection, recorded here so it cannot be adjusted once results are known.

| Suite | Scenarios |
|---|---|
| Easy | EASY-01, EASY-08, EASY-15 |
| Medium | MED-13, MED-27, MED-34 |
| Hard | HARD-04, HARD-13, HARD-22 |
| Adversarial | ADV-04, ADV-12 |
| Regression | REG-01, REG-08 |

This spans all five suites, includes the adversarial and regression bands that a
model-reports-only sample would miss, and includes MED-13 and MED-27 specifically because
run 2 graded them and MED-13 was rebuilt after a review. It is **not** a random sample and
the report must not describe it as representative of the 103.

## Execution

`opencode run` per turn, `cwd` in the isolated workspace built by
`tests/make_eval_workspace.py`. Turn 2 continues the turn-1 session via `--session`, so the
scenario's two-turn design is real. Fixed on 2026-10-13 after the harness was found starting
a fresh conversation for turn 2, which would have scored the diagnostic evidence cold.

Model: `opencode/space-bunny-free`. No version string is published, so the run is not
bit-reproducible and a provider routing change mid-run would not be detectable from the model
id alone. Timestamps are recorded per request regardless.

## Metrics, fixed before collection

All three are reported and none substitutes for another.

| Metric | Definition |
|---|---|
| Strict pass rate | passes / gradeable answers |
| Operational completion rate | gradeable answers / scenarios attempted |
| End-to-end yield | passes / scenarios scheduled |

Plus the critical-failure count and its categories, and a 95% Wilson interval on the strict
pass rate.

A provider error, timeout, empty response or ungradable answer is **never** a pass and is
never counted in the strict pass rate's denominator. It is an operational non-completion and
is reported as one. For zero gradeable answers the pass rate is **unmeasured**, not 0%.

## Scoring

Frozen `evaluation/rubric.md`, Route 1: the scenario's own table, `sum of anchors / (4 x
rows)`, 0.75 pass, 0.50 marginal, critical failure overrides. Verified: all 12 selected
scenarios carry an Evaluation Rubric section and a critical-failure section in their key.

No threshold, no rubric text and no scenario content changes during this run. A defect found
mid-run goes in the run's defect log and the scenario is marked `UNSCORABLE`. It is not
repaired and re-scored.

## Isolation position, stated plainly

`tests/test_answering_isolation.py` passes 12 deterministic checks on the real production
path: no protected path present, no answer key anywhere, the real structural checker clean,
the enforcing config denying `external_directory`/`shell`/`edit`/`webfetch`/`websearch`/
`subagent`, no `.git`, the skill byte-identical, and no prompt containing its own scenario
title.

**Live breach testing is still INCONCLUSIVE.** Every attempt to breach the boundary against
the working route returned a provider error, which is INDETERMINATE. So this pilot may be
described as *structurally isolated*. It may **not** be described as *leakage-resistant*, and
the report will not use that word.

Subagents are excluded from answering. The earlier probe showed a subagent reading an answer
key in full with zero denials, because child sessions do not apply the parent's loaded
project configuration. That finding does not depend on any provider and was not retested.

## Budget

12 scenarios x 2 turns = 24 requests maximum, plus retries allowed only for a non-rate-limit
transient failure and only within the pacing interval. A rate-limited response closes the
attempt and stops the batch.

At the observed pacing this pilot needs roughly 25 to 30 successful requests. The route
allows that only if requests are spaced. It does not fit in the exhausted OpenRouter quota at
all, which is why the route change was necessary.

## Stopping rules

Stop and checkpoint on: any rate-limit response, a BREACHED isolation route, a moved artifact
hash, a provider route change, or a critical-failure dispute that cannot be settled from the
sources.

## What gets recorded per scenario

Run ID, scenario ID, suite, model id, both prompt hashes, the skill digest, request
timestamps, provider outcome, raw response path, grading status, raw anchors, normalised
score, critical-failure ruling with evidence, final verdict, and error detail. Raw responses
are stored separately from grading output, and a provider error produces an attempt record
but never an answer artefact.

## Decision after the pilot

Expand only if the route proved reliable enough to answer a larger question. A pilot that is
mostly operational failures says the bottleneck is throughput, not model quality, and the
right next move is pacing rather than more scenarios. That is a real result and would be
reported as one.