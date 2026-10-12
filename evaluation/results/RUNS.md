# Evaluation run record

Metadata for every evaluation run. A score without its metadata is not reproducible and
cannot be compared against a later run.

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

Run 2, with the two-turn release, the weighted rubric, the corrected `error-codes.md`, and
the new `policy-mechanics.md` reference, has not been run. Any statement that the skill
scores above any particular figure would be invented until it is.