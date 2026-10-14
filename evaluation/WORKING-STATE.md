# Working state

Recoverable note so no work lives only in conversation context.

## Status as of 2026-10-14, harness pass

Branch `audit/evaluation-harness`, based on `75f1997`. Five defects found and fixed, all
recorded as D-038 through D-042 in `evaluation/defect-register.md` with reproduction steps.
Changelog entry at the top of `CHANGELOG.md`.

They were found by checking the harness out fresh and running it. Every one was invisible
from inside the working tree the earlier passes used, because that tree's own file timestamps
happened to be in the order the checkers wanted. This is worth carrying forward: a green
`check_repo.py` in a long-edited working directory is weaker evidence than the same result in
a clone.

- **D-038.** Packet freshness was decided by mtime, which is not in a commit. On a fresh
  clone all 103 packets looked stale, the `valid-repo-baseline` control probe failed, and
  therefore all 33 FAIL-expecting fault probes passed vacuously. `release_gate.py` lost A1,
  F1, F2 and F3. Fixed by comparing rendered packet text.
- **D-039.** Two origin probes anchored a regex with `^` and passed no `re.MULTILINE`, so
  they matched nothing and never mutated anything. They read green only because of D-038.
  `check_origin_integrity` is correct; the coverage claim was not.
- **D-040.** `run_generation.py` tested `rc == -1` instead of `rc != 0`, so a nonzero
  provider exit became a completed answer. This is the first of the two paths `75f1997`
  recorded as deliberately left open.
- **D-041.** `grade_run.py --run` never read the manifest. It wrote `PASS` with
  `normalized_score 1.0` for a scenario recorded `NOT_STARTED` with no answer file. This is
  the grading-side counterpart of what `75f1997` fixed on the generation side.
- **D-042.** An uncomputable score was coerced to `FAIL` when anchors were present, so a
  grader typo became a model failure. PROTOCOL.md forbids this in one line.

### Where the gate stands

`release_gate.py --skip-urls` reports `BLOCKED 1, PASS 28, UNVERIFIED 3`, verdict NOT
QUALIFIED. That is the same verdict as before this pass and is the correct one. C4 is BLOCKED
because no URL audit was run offline, and E5, G1 and G2 stay UNVERIFIED because no recorded
run meets the A/B design. Recovering four criteria did not qualify the project.

Full offline suite after the pass: `check_repo.py --strict` PASS, `fault_probe.py` 35 of 35
with 0 false passes, `test_leakage.py` PASS, `test_release_gate.py` 32 of 32,
`test_isolation_classify.py` 23 of 23, `test_generation_outcomes.py` 15 of 15,
`test_generation_workspace.py` 8 of 8, `test_grading_integrity.py` 8 of 8.

### What this pass does not establish

Run 3 collected nothing. All 103 scenarios in its manifest are `NOT_STARTED` and no answer
file exists, so none of these five defects has touched a recorded score. They are latent
defects in the machinery, not damage to a result, and the register records them that way.

Nothing here is evidence about whether the skills help. A passing probe suite says the
harness classifies the inputs it was given as described. It does not say a live model or
provider cannot produce a stream shape these suites do not model, and it does not move E5,
G1 or G2.

### Still open, deliberately

- The second path `75f1997` named: a policy carrying `continueOnError="true"` that swallows
  a failure contributes no fault to the manifest while its text still reaches the answer
  file. A defect in the fault inventory rather than in the outcome classification.
- The NO MUTATION guard proves each probe changed a file. It cannot prove the probe changed
  the right one, and nothing short of reading all 35 settles that.
- The A/B experiment remains unrun, for the reasons in `evaluation/ab-protocol-and-power.md`.

## Status as of 2026-10-13, later in the day

Re-verified against the repository, not against the previous pass's summary. Three items the
earlier note listed as still open are in fact fixed; the note is corrected below and the
original wording is kept in git history.

- **MED-09's Quota-versus-SpikeArrest characterisation is fixed.** `cb057df` replaced "Keep the
  Quota policy for the long-window allowance" (the Quota in evidence was one minute) with "Move
  the allowance to a longer window and put the bursts in SpikeArrest", and states the comparison
  chart's own wording. Verified at `scenarios/medium.md` "Correct Remediation".
- **MED-20 no longer hands over the discriminator at turn 1.** The `<LoadBalancer>` line sits
  under `#### Diagnostic evidence`, which is turn-2 material. `make_packets.py` emits only the
  initial ticket, initial evidence and diagnostic evidence, so the turn-1 packet carries no
  load-balancer mention. Verified against the generated packet, not the source.
- **MED-27's non-reproduction row has its subject.** "Two maintainers tried to reproduce this"
  is in the turn-2 prompt at line 28, so the row is no longer unscoreable.
- **HARD-09's reconciliation checks out.** `load-balancing-across-backend-servers.txt:350` says
  Apigee checks health every five minutes and returns the server to rotation, which is the
  sentence the key relies on. The key presents it as one of two readings rather than asserting
  it, which is the right shape.
- **EASY-14's fault code disclosure is accurate.** `messaging.adaptors.http.flow.SslHandshakeFailed`
  is at `mon_fault-codes.txt:77` and `options-configuring-tls.txt:8`, and is correctly absent
  from the policy error index because no policy raises it.

`AM-VerifyToken` was resolved by `8966ded` (now `JWT`). It is listed as live in
`evaluation/outstanding-errors.md`, which is stale on that point.

## Status as of 2026-10-13, end of the earlier pass

Phases 1, 2, 3 and 4 are done. Twenty commits landed on top of the thirteen listed below.
Gate at that point: **PROVISIONAL**, 28 PASS, 0 FAIL, 0 BLOCKED, 3 UNVERIFIED across 31 criteria
on the full run with the URL audit; 27 PASS, 1 BLOCKED offline. E5, G1 and G2 stay UNVERIFIED
because no model has been run under the A/B design, and that is the correct result.

The criterion count was 31 at that point. `de540e5` added F6 as a 32nd, which is why the counts
here and in `evaluation/RELEASE-REPORT.md` section 0 read 29 PASS across 32 today.

Run 2 exists: four scenarios, both turns, one arm, scored and retained in
`evaluation/results/run-2/`. It is a path exercise, declared as such in
`evaluation/model-eval-protocol.md` before a single answer was collected, with its deviation
logged before the run. It does not meet the A/B design and moves nothing on the gate.

Still open for a future pass, none of it blocking. Three of the five were re-checked and are
now closed, as recorded in the section above:

- **MED-27's rubric row** was unscoreable and now has its subject in the diagnostic evidence.
  Re-check whether the turn-2 packet still discriminates; nothing has been re-run since.
- **HARD-09** ground truth now accounts for the minority of successful requests. Worth one
  confirming read against the two source pages, since the reconciliation leans on the
  load-balancing page's five-minute re-check.
- **`references/policy-mechanics.md` carries the HealthMonitor guidance** and no run has
  measured whether a model loads it. Run 2's model did not open a single reference file, which
  is one observation about one model on four cases, not a finding.
- **`AM-VerifyToken`** is still an unsourced trace step name in `scenarios/hard.md`. Recorded
  as a live item in the banner on `evaluation/outstanding-errors.md`.
- **EASY-14's fault code** is still absent from the index. The scenario discloses it now.

## Committed before this pass

| Commit | What |
| --- | --- |
| `c564ee1` | Release gate: three verdicts (QUALIFIED / PROVISIONAL / NOT QUALIFIED); UNVERIFIED no longer yields QUALIFIED; C2 `PASS if unresolved else PASS` tautology fixed; C4 mapped `check_urls.py` exit 2 to PASS, now FAIL; EXECUTED/DERIVED/DECLARED evidence kinds; new `tests/test_release_gate.py` |
| `3e23cfa` | README states `.agents/skills/` is the only tested platform. B4 had been a false PASS |
| `bb5d859` | Cached the 11 missing OPDK pages (the project said "ten"; `view-page` was not a URL, `antipatterns/intro` is not OPDK, and three were missing from the list). Manifest recorded 109 to 120 |
| `12d3f46` | HARD-18: `ANALYZE` attributed to `update-apigee-edge-45202-45301`, not the failover page |
| `444579a` | MED-13: removed the unsatisfiable "fault string is always the same" premise, supplied both fault strings as evidence, added the missing `try`/`catch` |
| `2ffb8bd` | MED-22: added the Causal honesty rubric row and third critical failure; resolved the fresh-vs-upgraded evidence contradiction |
| `c53d527` | MED-10: removed the answer key contradicting its own rubric |
| `7aa47f5` | Leakage test was comparing against an always-empty string (`_blocks` yields `(sid, whole_block)`, so `blocks.get("ground-truth resolution")` was `""`). Fixed, found a real HARD-22 overlap, added `tests/make_eval_workspace.py` |
| `1f23d4c` | Rubric: pass thresholds, scenario-table normalisation, not-applicable handling, two-grader procedure |
| `cb13c73` | `make_packets.py` now emits MED-09 and MED-11's "Not a critical failure" carve-outs, which had never reached the grader |
| `d0115e6` | MED-02: stopped claiming one cause explains both symptoms, against the zero-downtime deployment model its own reference documents |
| `29ec460` | MED-07: cited `runtime-logs` (the page its discriminator lives on) and `service-config`; added the missing Safety row; rubric ceiling 5 to 6 |
| `7bdcefa` | MED-06: Safety row is now a safety scale; fixed an incorrect answer that contradicted its own rationale |

## Remaining work, in priority order

### 1. Scenario fixes from the second review

**MED-09** `scenarios/medium.md` ~line 1077 and ~1016.

- The `Technical correctness` 0-anchor is "Says quota miscounts", which fails a
  documented correct answer. `<Distributed>` defaults to `false` and `<Synchronous>`
  defaults to `false`, and the Quota policy page says calls may exceed the quota on the
  default configuration. An agent raising that scores 0 on the highest-weight dimension.
  Re-anchor, or add a line to the initial evidence stating those are known-good.
- The remediation calls a one-minute Quota a "long-window allowance". The comparison page
  assigns Quota to "days, weeks, or months" and SpikeArrest to "seconds or minutes". Fix the
  remediation to move the allowance to a longer window as well.

**MED-20** `scenarios/medium.md` ~line 2266 and ~2288.
The Initial evidence gives "The TargetEndpoint uses a `<LoadBalancer>` with more than one
target server", while the metadata and ground truth both say the `<LoadBalancer>` presence
"is the structural signal the symptom does not reveal". The discriminator is handed over at
turn 1. Move it to the Diagnostic evidence. Also align the Origin label with the convention
the other register-sourced scenarios use.

**MED-18** `scenarios/medium.md` ~line 2100.
The remediation stops at writing `overrides.yaml`. The documented procedure is
`helm upgrade operator apigee-operator/ --install --namespace APIGEE_NAMESPACE --atomic -f overrides.yaml --dry-run=server`
then the same without `--dry-run`. Source: `research/pages/hybrid_release-notes.txt:2320-2340`.
Also re-anchor the rubric to the behaviour rather than the register's phrasing, and name
`gcp.federatedWorkloadIdentity.enabled` as the property to read on EKS.

**MED-12, MED-14, MED-16** — minor, described in
`evaluation/audit-medium-B.md` context and in the second reviewer's findings. MED-12: the
ticket's "We raised its timeout" has an ambiguous antecedent; seeing 500 narrows to the
callout rather than proving it. MED-14: the turn-2 evidence is redundant and spoils the
answer by saying "the window matches the documented cache". MED-16: disclose that the
deployment-base-path to flow-selection link is an inference from the report, and cite the
deprecated OAuth HTTP status page.

**MED-13** may still carry one residue: the fourth "common incorrect answer" about fixing
"the policy named in the first fault string pasted". Verify the rewrite reads cleanly.

### 2. Phase 2, documentation drift

`evaluation/RELEASE-REPORT.md` is the worst. Section 1 is titled "Verdict", says
**NOT QUALIFIED**, and quotes figures that are all stale: 26 PASS / 30 criteria, 168 unique
URLs / 842 occurrences, 108 redirects, 53 of 103 scenarios reviewed, 289 of 294 cached
pages, 109 recorded, 82 codes, 25 fault probes, 34 real-world. Live values: 31 criteria,
171 unique URLs / 883 occurrences, 111 redirects, 103 of 103 reviewed, 300 of 305 cached,
120 recorded, 99 merged codes, 32 probes, 33 real-world.

Treat it as a dated record: prepend a supersession banner naming commit `832bbca` and the
commits that moved the ground, then restate the current verdict in a clearly separated
section. Do not rewrite the historical content into looking like the project qualified
earlier.

Also:

- `evaluation/defect-register.md` D-012 and D-024: 108 of 168 to 111 of 171. D-022: restate
  as twelve URLs, eleven of them OPDK.
- `evaluation/outstanding-errors.md`: add a superseded banner pointing at
  `evaluation/defect-register.md` and `evaluation/RELEASE-REPORT.md`. Its two still-live
  items are `AM-VerifyToken` as an unsourced trace step name, and EASY-14's out-of-index
  fault code (now disclosed in the scenario). Do not edit the finding bodies.
- `README.md`: probe counts 25 to 32; "three skills and two scenario suites" to five;
  `test-protocol.md` "four reference files" to six.
- `evaluation/audit-hard-reg.md:528` and `audit-medium-B.md:24`: the 12 versus 10
  discrepancy, and the superseded title-leak claim. Annotate, do not rewrite.

### 3. Phase 5, model execution

**Not attempted.** Establish what is actually available and either run a declared
evaluation or document precisely why not. `.agents/skills/` is discovered by the opencode
host, so a model can load the skill. `tests/make_eval_workspace.py` now provides the
isolation the protocol assumes. A protocol must still pin: model and version, the workspace
path, the tool allow-list, whether `research/pages` is present, the skill directory hash
from `MANIFEST.json`, per-turn prompt SHA-256, the file-read log, and the grading pass.

If a real run is not possible, leave E5/G1/G2 UNVERIFIED and say so. **Do not fabricate
outputs, scores or grader transcripts.**

### 4. Final validation

```bash
python3 research/build_error_index.py
python3 research/build_scenario_index.py
python3 tests/make_packets.py --all --turn 1
python3 tests/make_packets.py --all --turn 2
python3 tests/check_repo.py --root .
python3 tests/test_leakage.py
python3 tests/fault_probe.py
python3 tests/check_urls.py
python3 tests/test_release_gate.py
python3 tests/release_gate.py
```

Expected verdict: **PROVISIONAL** (not QUALIFIED), because E5, G1 and G2 are UNVERIFIED until
a model has actually been run. That is the correct outcome, not a problem to engineer away.

## Rules

- One concern per commit. Scenario fixes, documentation fixes and test changes do not go
  together.
- Regenerate packets and run `check_repo.py` plus `test_leakage.py` after ANY `scenarios/*.md`
  edit. Stale packets fail the build.
- Write commit bodies explaining the consequence, not the diff. Read the `$unslop` skill
  first. No em dashes. No "Co-Authored-By" trailers.
- Never make a criterion PASS to turn the gate green. The gate returning PROVISIONAL is the
  honest result.

## Phase 2b — paired A/B: not run, and why

The requested experiment was a 206-invocation paired comparison. It was not run.
`evaluation/ab-protocol-and-power.md` holds the full record.

The baseline was wrong. `ecf2ffe` is the **child** of `f9d7de8`, which is itself a
remediation commit that edits two skill files, so the "35 commits since ecf2ffe" count
absorbed it into the baseline arm. Correct baseline: `5b40edd`, parent of `f9d7de8`,
making the span 37. Logged as D-033.

The treatment is too small to measure. Against `5b40edd` the skill differs by 52 lines in
2 of 9 files. All three `SKILL.md` files are byte-identical, so the always-loaded
instruction surface differs by zero bytes. 47 of 52 lines are in `error-codes.md`, a
generated file. The only hand-written change in the skill is 3 lines in `hybrid.md`
restating a rule that was already correct. Two of 104 scenarios touch the delta and one has
no graded surface on it.

## Isolation: mechanism built and structurally verified, not yet demonstrated

- `tests/make_eval_workspace.py` now writes an enforcing `opencode.jsonc`
  (`external_directory`, `shell`, `edit`, `webfetch`, `websearch`, `subagent` all denied).
  The rule is resolved by the harness before the tool call and is not overridable by
  `--auto`.
- `tests/test_isolation.py` runs 8 breach routes with canaries. It distinguishes
  BREACHED, BLOCKED, ATTEMPTED and INDETERMINATE, retains raw provider streams, and
  reports INCONCLUSIVE rather than PASS when a route never reached a model.
- **Current result: structural PASS, live INCONCLUSIVE.** The free provider quota
  (50/day) ran out mid-run on 2026-10-13 and resets 2026-10-14 05:30 local.
- One manual probe before the harness existed was refused with `external_directory`.
  Recorded as a single data point, not a test result.
- No isolation claim is made. Full write-up in `evaluation/isolation-report.md`.

## Model execution, established

**Corrected 2026-10-13 later.** The claim below that `opencode/*` returns 403 from the CLI
is wrong. It works. Probed repeatedly on 2026-10-13:

```text
opencode run --auto --model opencode/space-bunny-free --format json "Reply with exactly: PONG"
```

returned `PONG` on many separate occasions, from the repository root and from an unrelated
temporary directory. `opencode/*` is a different provider from `openrouter/*`, so it is
capacity the exhausted OpenRouter daily quota does not touch.

The real constraint is not an auth wall. It is **burst rate limiting**, and the provider
reports it badly: a rate-limited call returns

```text
provider.auth: OpenCode's free tier can only be used from within OpenCode.
```

which reads as an entitlement refusal and is not one. Two requests fired in quick succession
behave differently from two spaced 90 seconds apart, and repeated probes of an unchanged
configuration flip between success and this error. Anyone treating the message as proof that
the route is unavailable will conclude the run is impossible while a working route sits in
front of them. Treat `provider.auth` with that message as INDETERMINATE, never as evidence.

The original text is preserved below.

---
Headless CLI works for `openrouter/<model>:free` entries only. `opencode/*` free-tier
models return 403 from the CLI ("free tier can only be used from within OpenCode"), and
paid OpenRouter models return 402 because OpenCode requests `max_tokens: 128000` while the
account affords about 79k; `limit.output`, `options.maxTokens` and `body.max_tokens` were
all ignored. `sandbox-exec` does not enforce `deny file-read*` on macOS 27 (verified twice).
Docker has no daemon; podman has no VM.
