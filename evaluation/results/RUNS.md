# Evaluation run record

Metadata for every evaluation run. A score without its metadata is not reproducible and
cannot be compared against a later run.

## Run 2, 2026-10-13

| Field | Value |
| --- | --- |
| Run ID | `run-2`, see `evaluation/results/run-2/` |
| Scenarios | 4: MED-27, HARD-09, ADV-05, REG-04 |
| Turns released | Both |
| Model | `space-bunny-free`, provider `opencode`, model id `opencode/space-bunny-free`. No version string is published. |
| Skill version | `.agents/skills` digest `baddc6e0c05ef2af`, at commit `8e5d666` |
| Workspace | `tests/make_eval_workspace.py`, no corpus, manifest retained |
| Arms | 1, assisted. **No baseline arm.** |
| Graders | 1, and the same process that produced the answers |
| Protocol | `evaluation/model-eval-protocol.md`, deviation logged before the first answer |
| Date | 2026-10-13 |

### Results as recorded

| Scenario | Score | Verdict | Critical failures |
| --- | --- | --- | --- |
| MED-27 | 10/12, 0.83 | pass | 0 |
| HARD-09 | 16/24, 0.67 | marginal | 0 |
| ADV-05 | 16/16, 1.00 | pass | 0 |
| REG-04 | 12/12, 1.00 | pass | 0 |

No aggregate figure. The protocol declared none in advance, because four scenarios cannot
support one.

### What this run cannot show

No baseline arm, so it cannot say whether the skills help. The model that answered is the model
that reviewed and repaired this library, and the grader is that same process, so nothing here
is a measurement of model quality. The working directory was the repository root, so the
isolation `make_eval_workspace.py` provides was an instruction rather than a mechanism. All of
that was written into the protocol's deviation log before the first answer was collected.

### What it did produce

Three findings about the suite, in `evaluation/results/run-2/grading.md`: a rubric row in
MED-27 whose subject never reaches the agent, HARD-09's ground truth still contradicting its own
evidence about the minority of successful requests, and an assisted arm that opened no
reference file in any of the four runs.

Release-gate criteria E5, G1 and G2 remain UNVERIFIED. This run does not meet the A/B design
they require and is not counted toward any of them.

---

## Run 1, 2026-10-11

| Field | Value |
| --- | --- |
| Run ID | run-1 |
| Scenarios | 7: EASY-04, EASY-08, MED-03, HARD-06, HARD-10, ADV-01, REG-02 |
| Turns released | **1 only.** Diagnostic evidence was never released. See defects below. |
| Model | Subagent via the harness. Exact model id not captured. **This is a gap.** |
| Skill version | Pre-round-3. `references/error-codes.md` was missing all SpikeArrest codes. |
| Graders | 1 |
| Date | 2026-10-11 |

### Results as recorded

| Arm | Raw score | Critical failures | Pass / fail / incomplete |
| --- | --- | --- | --- |
| A, no skill | 205/280 (73.2%) | 4 | 1 / 5 / 1 |
| B, with skill | 236/280 (84.3%) | 3 | 3 / 3 / 1 |

Scores are the raw sum of 10 dimensions at 0 to 4, so the denominator is 280 for 7
scenarios. These predate the weighted rubric, which now produces a total out of 68 per
scenario. Do not mix the two scales.

### What the run showed

Both arms fabricated. The baseline invented `policies.ratelimit.QuotaExceeded` and
`policies.ratelimit.SpikeArrested`, `<Priority>`, `<CircuitBreaker>` and `<Threshold>`, and
a `gcloud apigee apis revisions` group that does not exist. The assisted arm invented the
load-balancing algorithms `leastConnectionsWithHealthCheck` and `weightedRoundRobin`, an
element `<Target enabled="false">`, and cited `organizations.apis.deployments/create`,
which 404s.

The assisted arm's most confident wrong answer came from the skill's own reference file.
`references/error-codes.md` omitted every SpikeArrest runtime code because the parser only
handled pipe tables and that page renders one cell per line. The agent trusted the index
over the page and asserted with false confidence. That is the most useful finding in the
run and it has since been fixed.

### Defects in this run, not in the answers

Diagnostic evidence was never released. The protocol calls for a two-turn exchange and the
turn-2 release was not implemented, so six of seven ground truths were unreachable. Both
arms scored low partly for that reason, which makes the 73% and 84% figures pessimistic in
a way that is not about the skill.

Scores used the unweighted sum. The rubric now specifies weights totalling 68 per
scenario. Regrade before comparing with any future run.

The model identity was not recorded, so this run cannot be reproduced.

### Strength of this evidence

Weak. Seven scenarios, one grader, one unknown model, half the evidence never released.
It is a smoke test that found real defects, which is what it was for. It does not establish
that the skill works.

## Runs not yet performed

No run of the full 103-scenario set has been performed, with or without a baseline arm.
Run 2 covered four scenarios with one arm and one grader who was also the candidate, which
is enough to find defects in the suite and not enough to say anything about the skill.

Any statement that the skill scores above a particular figure, or that it scores better with
the skills than without them, would be invented until an A/B run with the protocol in
`evaluation/model-eval-protocol.md` is carried out.
## Run 3, started 2026-10-13

| Field | Value |
| --- | --- |
| Run ID | `run-3`, see `evaluation/results/run-3/` |
| Purpose | Current-system performance across all 103 scenarios. Not a skill A/B. |
| Scenarios | 103: 15 easy, 45 medium, 22 hard, 13 adversarial, 8 regression |
| Turns | Both, 206 generation requests at full coverage |
| Model | `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free`. No version string published. |
| Skill version | `.agents/skills` digest `ba3500db7ca1755d`, at commit `a25333b` |
| Workspace | `tests/make_eval_workspace.py`, corpus excluded, structural isolation PASS |
| Rubric | Route 1, the scenario's own table, normalised by `4 x rows` |
| Thresholds | 0.75 pass, 0.50 marginal, below fail; critical failure overrides the score |
| Graders | 2, in separate contexts, second grader blinded to the first |
| Second-grader sample | 20, stratified 3/9/4/2/2, fixed by rule before any output |
| Budget | 45 attempts per 05:30-to-05:29 IST window, 337 total at full coverage |
| Protocol | `evaluation/results/run-3/PROTOCOL.md`, frozen before collection |

### Status

**Zero answers collected.** The preflight returned HTTP 429 with
`X-RateLimit-Remaining: 0`; the quota resets 2026-10-14 05:30 IST. One request spent, on the
preflight itself.

No pass rate, critical-failure rate or mean score is reported, because none exists yet.

### Unmet prerequisite

Live isolation is unverified. The live breach tier needs 8 requests and a live model; both
earlier attempts on 2026-10-13 returned 8 `INDETERMINATE` routes on quota errors. An
`INDETERMINATE` is not a denial, so the boundary remains structurally verified and
undemonstrated. A tool-enabled run must not be called leakage-resistant until the live tier
returns something else.

### What this run can and cannot show

It measures the present system on the present suite. It cannot show the skill caused the
result, because the always-loaded `SKILL.md` files were reported byte-identical across the
selected baseline, so no valid comparison exists.
