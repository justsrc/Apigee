# Working state

Recoverable note so no work lives only in conversation context.

## Status as of 2026-10-13, end of this pass

Phases 1, 2, 3 and 4 are done. Twenty commits landed on top of the thirteen listed below.
Final gate: **PROVISIONAL**, 28 PASS, 0 FAIL, 0 BLOCKED, 3 UNVERIFIED across 31 criteria on the
full run with the URL audit; 27 PASS, 1 BLOCKED offline. E5, G1 and G2 stay UNVERIFIED because
no model has been run under the A/B design, and that is the correct result.

Run 2 exists: four scenarios, both turns, one arm, scored and retained in
`evaluation/results/run-2/`. It is a path exercise, declared as such in
`evaluation/model-eval-protocol.md` before a single answer was collected, with its deviation
logged before the run. It does not meet the A/B design and moves nothing on the gate.

Still open for a future pass, none of it blocking:

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
|---|---|
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
