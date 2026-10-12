# Model evaluation protocol

Declared before any answer was collected, so that what the run was going to be decided by
the protocol and not by the numbers it produced. `evaluation/test-protocol.md` describes the
A/B design in general terms. This file pins the specific choices for one run.

## What is pinned

| Field | Value |
| --- | --- |
| Run ID | `run-2` |
| Model | `space-bunny-free`, provider `opencode`, model id `opencode/space-bunny-free` |
| Model version string | None is published by the provider. The model id is the only identifier available and it is recorded verbatim. |
| Skill version | `.agents/skills` digest `baddc6e0c05ef2af`, at commit `8e5d666` |
| Workspace | built by `tests/make_eval_workspace.py`, no corpus |
| Corpus present | No. `research/pages` is not in the workspace, so the agent cannot read a cached documentation page. |
| Scenarios | MED-27, HARD-09, ADV-05, REG-04 |
| Turns | Both. Turn 1 then turn 2, scored together. |
| Arms | One, assisted. |
| Graders | One |
| Date | 2026-10-13 |

## Why these four

Chosen before the run and not replaced afterwards. One from each of the suites that G1 and
G2 name, so the run touches both: MED-27 from `medium.md`, HARD-09 from `hard.md`, ADV-05
from `adversarial.md`, REG-04 from `regression.md`. None of the four appears in run 1, so no
result here is a re-run of something already scored.

## Why one arm and not two

Run A, the no-skill baseline, needs a second workspace with no `.agents/skills` and a
different prompt to the model, which is a second execution of the same size. This run is a
path exercise: it establishes that a model can be put in front of the suite under the
isolation `make_eval_workspace.py` provides and produce answerable output. It does not
establish whether the skills help, because without arm A there is nothing to compare against.

## Isolation, and where it stops

`tests/make_eval_workspace.py` builds a tree holding `.agents/skills/` and `prompts/` and
nothing else. `tests/test_leakage.py` proves no answer key, scenario file or ID-to-title
index is reachable inside that tree.

That is a property of the tree, not of the process. Every session this harness runs has its
working directory at the repository root, and the repository root is the parent of the
workspace. The workspace's `WORKSPACE.md` tells the agent not to read outside itself, and
the agent is asked to list every file it read, but neither is enforcement. A model that
wanted the answer key could reach `evaluation/packets/<ID>.key.md` from where it starts.

This is recorded as a limitation of the run rather than presented as isolation. A harness
that could place the session's working directory inside the workspace would close it. The
file-read log is the only evidence available here, and it is self-reported.

## Scoring

Exactly as `evaluation/rubric.md` specifies, unchanged:

- Score the scenario's own table, which wins where it differs from the general rubric.
- `scenario score = sum of anchors scored / (4 x number of rows)`.
- 0.75 or above passes, 0.50 to 0.74 is marginal, below 0.50 fails.
- A critical failure listed in the scenario's own key fails the scenario whatever the score,
  and is reported alongside the score rather than instead of it.

No aggregate pass mark is declared for the run as a whole. Four scenarios cannot support one,
and setting it now would only create a number to defend afterwards.

## Artifacts kept

All of these, in `evaluation/results/run-2/`:

- `workspace/MANIFEST.json`, the built-from commit, the skill digest and the SHA-256 of
  every prompt file
- `raw/<ID>.turn1.md` and `raw/<ID>.turn2.md`, the responses verbatim
- `filereads/<ID>.txt`, the agent's own list of the files it opened
- `grading.md`, per-dimension anchors, the critical-failure decision, the normalised score
- `REPORT.md`, the summary, including what this run cannot show

## What this run cannot do, declared in advance

1. It cannot show that the skills help. There is no baseline arm.
2. It cannot support a claim about any model but this one, at this model id, on this date.
3. It cannot separate a rubric artefact from a model failure with one grader.
4. It cannot verify the isolation, only report it.
5. It cannot move release-gate criteria E5, G1 or G2 to PASS. Those ask for an evaluation
   meeting the A/B design in `evaluation/test-protocol.md`, with retained outputs and a
   declared protocol. This run has no arm A, so it does not meet them and the criteria stay
   UNVERIFIED.

## Deviation log

Any departure from the above gets a dated line here before the result is read.