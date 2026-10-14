# Paired skill A/B: design, power analysis, and why it was not run

Written 2026-10-13, before any answer for this experiment was collected. The requested
experiment was a paired comparison of the baseline and current skill over all 103 scenarios,
206 invocations. This file records the design, the finding that killed it, and what would
have to be true to run it properly.

It is kept rather than deleted because the power analysis is the result. A reader who wants
to run the comparison later needs to know what was measured before spending the budget.

## The experiment as requested

| Field | Value |
| --- | --- |
| Design | Paired, two arms, all 103 scenarios, 206 invocations before retries |
| Arms | Baseline skill versus current skill |
| Primary question | Does the current skill perform better than its pre-remediation predecessor |
| Isolation | To be enforced technically, not by instruction |

## Baseline identification

The handoff named `ecf2ffe` as the pre-remediation state. **That is wrong, and wrong in the
direction that would have faked a null result.**

```text
$ git rev-parse ecf2ffe^
f9d7de8b3556acbd2706577b2fb0ed610a59edd6
```

`ecf2ffe` ("Add handoff document for the next agent") is the **child** of `f9d7de8` ("Review
MED-01..MED-22, fixing twelve defects"), which is itself a remediation commit that changes
the skill. The count of "35 commits since `ecf2ffe`" therefore silently absorbed `f9d7de8`
into the baseline arm. Both arms would have carried the first remediation commit, and the
experiment would have reported a guaranteed null for changes that were present in both.

The correct baseline is the parent of the first remediation commit:

| Field | Value |
| --- | --- |
| Baseline commit | `5b40edd96007eda996d5787b540b1ae51e32394f` |
| Baseline subject | Fix eight defects in the easy and adversarial scenarios |
| Remediation span | `5b40edd..b46a337`, 37 commits |
| Current arm | `b46a337`, pinned |

Both arms must use the corpus, scenarios and packets from `b46a337`. Checking out the
baseline tree wholesale would also roll back 11 cached documentation pages and roughly 20
answer-key rewrites, which would measure "older everything" rather than "older skill".

## The finding that stopped the run

`git diff 5b40edd b46a337 -- .agents/skills/` is **52 changed lines across 2 of 9 files**.

| Path | Baseline | Current | Delta |
| --- | ---: | ---: | --- |
| `apigee-support-core/SKILL.md` | 11,620 | 11,620 | **identical** |
| `apigee-opdk-troubleshooter/SKILL.md` | 8,253 | 8,253 | **identical** |
| `apigee-opdk-upgrader/SKILL.md` | 9,892 | 9,892 | **identical** |
| `references/policy-mechanics.md` | 23,656 | 23,656 | **identical** |
| `references/products.md` | 4,329 | 4,329 | **identical** |
| `references/security.md` | 6,628 | 6,628 | **identical** |
| `references/sources.md` | 3,832 | 3,832 | **identical** |
| `references/hybrid.md` | 5,105 | 5,193 | +3 / -2 |
| `references/error-codes.md` | 103,433 | 112,881 | +42 / -5 |

Two facts dominate:

1. **Every `SKILL.md` is byte-identical.** The always-loaded instruction surface, which is
   what the model reads before anything else, differs by zero bytes between the two arms.

2. **90% of the delta is a generated file.** `references/error-codes.md` says in its own
   first line that it is mechanically extracted by `research/build_error_index.py`. Its 36
   new rows came from re-running a scraper over a corpus that grew by 11 cached pages. That
   is a data refresh, not a skill intervention.

The only hand-written change in the entire skill is three lines in `hybrid.md`, clarifying a
rule that was **already correct at baseline**. The baseline text said checking either
condition alone rules it out wrongly; the current text says both must be present to
implicate it. Same rule, plainer wording.

## Graded surface

Grepping every scenario body for the 36 fault codes that exist at `b46a337` but not at
`5b40edd` returns **2 hits**, both inside MED-16's answer-key prose, neither in a prompt or
a rubric row. MED-16's rubric scores technical correctness, diagnostic method, competing
causes and next-step quality, and never asks the agent to name the fault code.

For the `hybrid.md` change, the MART/workload-identity surface maps to exactly one scenario,
MED-18.

**So of 104 scenario blocks, 2 (1.9%) touch any part of the delta, and one of those two has
zero graded surface on it.**

## Power

206 invocations over 104 two-turn scenarios is roughly one invocation per scenario per arm.
If the true effect is confined to MED-18, then at most 2 of 206 observations can move, and
the largest available swing is bounded by MED-18's rubric rows. Even a real effect on that
one scenario would not clear the noise floor of a 206-sample run.

The experiment would have returned a null, and the null would have been uninformative. It
would also have looked rigorous, because 206 invocations and a paired design are the shape
of a serious evaluation. That is the specific failure mode this project exists to prevent:
a passing or neutral-looking number standing in for a question nobody actually asked.

**The experiment was not run. No answers were collected, so there are no results to
misreport.**

## What the remediation actually changed

The 37 post-baseline commits are overwhelmingly `MED-NN:` fixes to scenarios, answer keys
and rubrics, not to the skill. Roughly 20 of them repaired scenarios found defective by
second review: MED-02's one-cause claim, MED-13's unsatisfiable premise, MED-22's rubric
that scored a wrong answer 20 out of 20, MED-10's key contradicting its own rubric, and so
on.

The interesting question is therefore not "did the skill improve" but "did repairing the
scenarios and answer keys change what the suite measures". That is a different experiment,
it is not the one that was requested, and it has not been run either.

## Isolation capability, established regardless

The requested experiment needed technically enforced isolation. That is now built and
tested, and it holds independently of the decision above.

`tests/make_eval_workspace.py` writes an `opencode.jsonc` whose `external_directory: deny`
rule blocks every read outside the workspace. OpenCode evaluates permissions in the harness
before a tool call executes, a configured deny cannot be overridden by `--auto`, and saved
approvals never override one. `shell`, `edit`, `webfetch`, `websearch` and `subagent` are
all denied.

`tests/test_isolation.py` attempts eight breach routes against a live model with canaries
planted outside the boundary. A run without `--live` reports INCOMPLETE, never PASS, because
a model that was never asked to breach anything has not demonstrated a boundary.

Results are recorded in `evaluation/isolation-report.md`.

## Conditions for running this properly

1. A skill change large enough to matter. The remediation moved 52 lines, 90% of them in a
   generated file, leaving every `SKILL.md` byte-identical. A future comparison needs a
   delta in the instruction surface, not in generated data.
2. Enough scenarios to carry the effect. If the change targets MART/workload-identity,
   MED-18 plus a scenario written to exercise it is the minimum, and repetitions rather than
   breadth.
3. A model that can be pinned. The available free endpoint does not publish a version string
   and does not pin weights, so runs are not bit-reproducible. A paid or self-hosted model
   with a fixed version identifier would make the result durable.
4. Two arms over identical exams. Corpus, scenarios and packets pinned at one commit.

## Release criteria

E5, G1 and G2 remain **UNVERIFIED**. No model evaluation supporting a performance claim
exists, and none was manufactured. The verdict stays PROVISIONAL.
