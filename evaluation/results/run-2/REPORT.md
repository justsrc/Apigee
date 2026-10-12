# Run 2 report

2026-10-13. Protocol: `evaluation/model-eval-protocol.md`, including the deviation logged
before any answer was collected. Grading: `grading.md` in this directory. Raw responses and
file-read logs: `raw/` and `filereads/`. Workspace manifest: `workspace-manifest.json`.

## What this run is

A path exercise. It establishes that a model can be put in front of this suite inside a
workspace that provably contains no answer key, answer a packet over two turns, and be scored
against the scenario's own rubric with the critical-failure override applied. Nothing more.

## What it is not

The model that answered is the model that reviewed and repaired this scenario library in the
same conversation, the grader is that same process, and the working directory was the
repository root throughout, so the isolation was an instruction rather than a mechanism. The
deviation log says all of this and it was written before the first answer.

There is no baseline arm, so nothing here says whether the skills help. Four scenarios with one
grader who is also the candidate cannot distinguish a real effect from noise. E5, G1 and G2 stay
UNVERIFIED and this run is not evidence against that: it does not meet the A/B design those
criteria ask for.

## Results

| Scenario | Score | Verdict | Critical failures |
| --- | --- | --- | --- |
| MED-27 | 10/12, 0.83 | pass | 0 |
| HARD-09 | 16/24, 0.67 | marginal | 0 |
| ADV-05 | 16/16, 1.00 | pass | 0 |
| REG-04 | 12/12, 1.00 | pass | 0 |

No critical failures in 24 dimension scores. No aggregate, for the reason the protocol gave in
advance.

## What came out of it that is worth keeping

Three findings about the suite, none of them about the model. They are in `grading.md` in full.

1. MED-27 carries a rubric row, "Handling of non-reproduction", whose subject never reaches
   the agent in either turn. It was excluded from the denominator rather than scored zero.
2. HARD-09's ground truth still asserts that every request fails once the target is removed,
   while its own evidence reports 98 percent and its own verification calls the minority
   success a property of the fault. `audit-hard-reg.md` recorded this defect and it has not
   been fixed. The answer flagged the contradiction three times.
3. The assisted arm opened no reference file in any of the four runs. That is an observation
   about one non-random model on four cases and nothing more, but it is the question a real
   A/B run exists to answer.

## What would have to happen for the gate criteria to move

An A/B run per `evaluation/test-protocol.md`: the same model and version on both arms, the same
prompts, a baseline arm with no skill in its workspace, two graders scoring independently, and
retained raw responses for every scenario. That is roughly 206 model answers for the full set
and a second grader for each. This environment has one model, one process and no mechanism for
either the isolation or the second grader, so the criteria stay UNVERIFIED. That is the honest
result and it is the correct one to report.