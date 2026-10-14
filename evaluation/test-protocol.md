# Evaluation protocol

How to run a scenario against a model and record what happened, so two people get
comparable numbers and a result can be re-examined later.

## The A/B design

The question is whether the skills improve an answer. That needs two arms over the same
scenarios:

**Run A, baseline.** The model answers with no skill and no reference material. No file
reading, no web search. This measures what it would have said on its own.

**Run B, assisted.** The same model answers the same scenarios having loaded
`apigee-support-core` and its six reference files.

Same model, same scenarios, same prompt. The only difference is the skill. Anything else
that differs confuses the result.

Keeping the model fixed matters. A comparison where B used a stronger model measures the
model, not the skill.

## Preparing

```bash
python3 tests/make_packets.py --all --turn 1
python3 tests/make_packets.py --all --turn 2
```

That writes three files per scenario into `evaluation/packets/`:

- `<ID>.prompt.md` is turn 1: the initial ticket and initial evidence.
- `<ID>.turn2.prompt.md` is turn 2: the diagnostic evidence.
- `<ID>.key.md` is the ground truth, remediation, verification, incorrect answers and
  rubric. Never shown to the agent.

**Both turns matter.** The first run released only turn 1. Six of its seven ground truths
were therefore unreachable, and both arms scored low for reasons that had nothing to do
with the skill. Any medium or hard scenario given only turn 1 is usually underdetermined,
so a one-turn run understates scores and flatters nobody.

`tests/check_repo.py` verifies that both turns exist for every scenario and that no key
leaked into any prompt. Run it before interpreting a result.

## Running

Give the model the prompt file contents verbatim for run A. For run B, tell it to read
the skill and references first, then give the same prompt file. In both cases write each
answer to its own results file, one `## <SCENARIO-ID>` section per scenario.

Record at the top of each results file: model name and version, date, skill version or
commit, and anything unusual about the run.

## Grading

Grade each answer against `<ID>.key.md` using `evaluation/rubric.md` and the scenario's own
rubric table, which is narrower and wins where they differ.

Two graders are better than one, and they should not see each other's scores until both
have finished. Disagreement between graders is a finding about the rubric, not just about
the answer.

Score the ten dimensions 0 to 4, then record critical failures separately. A critical
failure fails the scenario regardless of total, and is reported separately from the score
so a high total never hides one.

## Recording

Per scenario: scenario ID, skill version, model, date, raw response, dimension scores,
critical failure yes or no, pass or fail, and a one line note on anything the score does
not capture.

Keep the raw responses. A score without the response behind it cannot be re-examined, and
disagreements almost always live in the response rather than the number.

## What a result means

A useful result is directional. With seven scenarios you cannot establish that the skill
works, only whether it is worth continuing to develop.

Worth watching for:

- Critical failures in A that do not appear in B. This is the clearest evidence of value.
- B being worse anywhere, especially on length. The skill tells the model to write less,
  and a rubric that rewards verbosity would hide that.
- Both arms failing the same scenario. Usually means the scenario is ambiguous, which is
  a defect in the scenario, not in either answer.

## Current status

One run has been performed, 7 scenarios, single grader, single model. Results are in
`evaluation/results/`. It is a smoke test, not evidence. Seven scenarios with one grader
cannot distinguish a real effect from noise, and no comparison across models has been
made. Treat the numbers as a starting point for a larger run, not as a result.
