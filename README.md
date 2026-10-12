# Apigee support skills

A skill set for triaging and diagnosing Apigee problems, plus an evaluation suite that
tests whether the skills actually help.

The premise is that Apigee support answers go wrong in a specific way. A model reads a
ticket, produces a confident explanation, and the explanation is wrong because it applied
an Apigee X instruction to a hybrid install, or matched a fault code to a cause it never
opened the page for, or recommended a change to production before establishing what was
broken. These skills exist to make those failures harder.

## What is here

Three skills and two scenario suites, all under `.agents/skills/` and `scenarios/`.

| Skill | What it does |
| --- | --- |
| `apigee-support-core` | The workflow. Product identification, intake, the diagnostic loop, the hypothesis ledger, source discipline, and action safety. Loads the others. |
| `apigee-opdk-troubleshooter` | Edge for Private Cloud runtime faults. Pre-existing, audited and updated, see the changelog. |
| `apigee-opdk-upgrader` | Edge for Private Cloud upgrades and rollbacks. Pre-existing, audited and updated. |

The two OPDK skills were already in this repository. They are good and they were kept.
The audit changed their version pins and added a warning about a URL trap that had already
cost us once.

Six reference files hang off the core skill and load on demand, not with it:
`error-codes.md`, `hybrid.md`, `policy-mechanics.md`, `products.md`, `security.md` and
`sources.md`. They are listed in the core skill so the agent knows what exists and when to
reach for it.

## Installing

The skills live in `.agents/skills/<name>/SKILL.md`. An agent platform that discovers
skills from that path will pick them up. If yours uses a different path, copy the three
skill directories there. Each `SKILL.md` carries YAML frontmatter with `name` and
`description`, and the name matches its directory.

There is no plugin, hook or runtime dependency. The skills are Markdown plus reference
files. The Python scripts under `research/` and `tests/` are development tools and are not
needed to use the skills.

## How the skills find their references

The core skill names its reference files in a table near the end. They are not inlined into
the skill, so an agent that does not read them will not have fault codes or product
differences available. That is deliberate. Inlining 173 fault codes into the skill would
bloat every prompt and make the workflow instructions harder to find.

If your platform does not support reference files, inline them manually and accept the
prompt cost.

## Scenarios

| File | Count | What it is for |
| --- | --- | --- |
| `scenarios/easy.md` | 15 | Narrow cases with a short path to an answer |
| `scenarios/medium.md` | 45 | Two or more live hypotheses, or a component interaction |
| `scenarios/hard.md` | 22 | Competing causes, some with deliberately insufficient evidence |
| `scenarios/adversarial.md` | 13 | Built to break a specific behaviour. Not incidents. |
| `scenarios/regression.md` | 8 | Cheaper to run, sharp to fail on. Rerun after any skill change. |

`scenarios/index.md` is generated from those files. 103 scenarios in total.

Every scenario in the three graded files carries the same sections: metadata, the initial
ticket, initial evidence, expected investigation, diagnostic evidence, ground truth,
remediation, verification, common incorrect answers, a rubric, and references.

Every fault code quoted in a scenario was extracted from a real policy page. The list is
`research/official-documentation-index.md` and the extraction is generated, not typed. If
you add a code to a scenario, add it to the index first.

The adversarial and regression files are labelled as evaluations rather than incident
reports, because they are constructed. Do not let them be presented as things that
happened to anyone.

## Running the checks

```bash
python3 tests/check_repo.py          # structure, IDs, sections, frontmatter, links, freshness
./tests/check_urls.sh                # classify every cited URL (network required)
python3 tests/fault_probe.py         # prove the checkers detect broken projects
python3 tests/test_leakage.py        # prove no answer key reaches a prompt
./tests/release_gate.py              # run everything and emit a machine-readable verdict
```

`check_repo.py` checks what a script can honestly check: files exist, scenario IDs are
unique, each graded file has at least 15 scenarios, every scenario has its required
sections with real content, skill frontmatter is well formed, relative links resolve, every
reference path a skill lists points at a real file, and both generated indexes match what
their generators produce from the current sources.

It does not and cannot check whether a scenario's technical content is correct. It prints
a separate block listing what needs human or model review, so a clean run is never mistaken
for a correct suite. Read that block. Add `--strict` to fail on warnings.

`check_urls.py` classifies each cited URL as one of `VERIFIED`,
`REDIRECTED_AND_VERIFIED`, `SOFT_404`, `NOT_FOUND`, `ACCESS_RESTRICTED`, `RATE_LIMITED`,
`TRANSIENT_FAILURE`, `INVALID_URL`, `CONTENT_MISMATCH` or `UNVERIFIED`. It records redirect
chains, checks that the body is actually the document it claims to be, retries only what a
retry could change, and exits non-zero if it finds no URLs at all. `--fixtures` runs the
classifier over recorded responses with no network, which is what makes the soft-404
detection testable at all.

`fault_probe.py` is the one that matters most. It copies the repository to a throwaway
directory, breaks one thing at a time, runs the checker, and records whether the checker
noticed. A checker that passes a broken project is worse than no checker, because it turns
an unknown into a known-good. Reading the checker is not evidence about its behaviour and
neither is its docstring. **Add a probe here for every defect you fix.**

`test_leakage.py` checks all 206 prompt packets for held-back sections, ground-truth
sentences, incorrect-answer text and scenario titles, and then deliberately injects a
canary phrase into held-back material to prove the generator actually holds it back.

`release_gate.py` runs all of the above and prints PASS, FAIL, BLOCKED or UNVERIFIED per
criterion. BLOCKED and UNVERIFIED are real answers; a gate with none of them on a project
like this one would be a gate that is not looking hard enough.

## What the checks found

The project's history records several checkers that reported success while checking nothing.
`fault_probe.py` found eight more in the previous version of `check_repo.py`, including a
corrupted fault-code index passing cleanly. All eight are fixed and the probe now runs
25/25. `evaluation/defect-register.md` has the full list with reproduction steps and the
test that now covers each one.

## Adding a scenario

1. Find the fault code in `research/official-documentation-index.md`, or add the page and
   re-run the fetch. Do not write a code from memory. If the code does not appear in
   `references/error-codes.md`, say so explicitly rather than guessing.
2. Write the ticket so it reads like a person wrote it and does not reveal the cause. The
   scenario title is not shown to the agent, so a title that states the answer is harmless
   for leakage, but it still makes the scenario read like a conclusion.
3. Give the ground truth a source. If you cannot source it, mark the scenario synthetic
   and say the mechanism is unverified.
4. Fill every required section. The harness will tell you which are missing.
5. Add critical-failure conditions specific to this case. A generic list copied into every
   scenario is worse than none, because it teaches a grader to rubber-stamp.
6. `python3 tests/make_packets.py <ID> --turn 1 && python3 tests/make_packets.py <ID> --turn 2`
7. `python3 tests/check_repo.py`
8. `python3 tests/release_gate.py --skip-urls`

The section that catches the most bad scenarios is common incorrect answers. Writing the
plausible wrong answer is how you find out whether the case actually discriminates.

## Research and sources

`research/` holds the evidence.

`RESEARCH-RECIPE.md` explains how to verify a URL and how to find real ones instead of
guessing. Read it before citing anything.

`fetch.sh` fetches a documentation page, records its real HTTP status, and extracts the
article body. It handles three traps that produce wrong answers silently: soft 404s that
return HTTP 200, pandoc truncating large pages, and URLs guessed from a naming pattern.

`repair_manifest.py` confirms every cached page resolves and rewrites
`research/pages/MANIFEST.tsv` with a provenance column: `recorded` (the URL was captured by
fetch.sh at fetch time), `guess` (derived from the lossy filename encoding and confirmed
live), `corrected` (the filename was a scratch name and the real URL was confirmed), or
`UNRESOLVED` (no confirmed URL, stated rather than guessed). Run it after adding pages.

`evaluation/outstanding-errors.md` lists scenario defects found by review and not yet
fixed, highest severity first. Read it before trusting any scenario as ground truth.

`build_error_index.py` regenerates `references/error-codes.md` from the fetched pages.
`build_doc_index.py` regenerates the documentation index and can re-verify every URL.
`normalize_pages.py` converts HTML tables that pandoc leaves behind, which is what took the
fault code count from 129 to 173.
`build_scenario_index.py` regenerates `scenarios/index.md` from the scenario files.

`notes-*.md` are the research write-ups. They are where the "could not verify" lists live,
which is the part worth reading.

`notes-known-404.txt` records URLs that do not exist. Twenty-two of the first thirty-nine
plausible paths tried during setup failed. That file is the argument against guessing.

## What has and has not been verified

Verified by machine, in this repository, re-runnable: every scenario is structurally valid
and has a complete packet set; no answer key reaches a prompt; both generated indexes match
a fresh run of their generators; every cited URL resolves to the document it claims to be.

Verified by review, recorded in `evaluation/audit-*.md`: the fault codes, HTTP statuses,
config elements and citations in the scenario library, against the source pages.

Not verified, and not claimed anywhere: that a model answers these better with the skills
than without. That needs a model evaluation run, and the only one on record covers seven
scenarios with a single grader. Whether any skill improves an answer in practice is an open
question, not a finding.

Two documentation problems are recorded rather than resolved, because the sources do not
resolve them. `evaluation/source-conflicts-loadbalancing.md` documents two current official
pages contradicting each other on whether a failed load-balanced target returns to rotation;
the project records both and does not pick one. `evaluation/source-notes-opdk-knownissues.md`
records that the official known-issues register scopes itself to "Apigee and Apigee hybrid"
and so contains no Edge for Private Cloud entries by design, which is a statement about the
register's scope and not about whether any OPDK issue exists.

## Contributing

Change the skill, rerun `python3 tests/check_repo.py`, rerun `scenarios/regression.md`, then
`python3 tests/release_gate.py --skip-urls`. The regression file exists to catch a skill
that got longer and less accurate.

If you fix a defect in the tooling, add a probe to `tests/fault_probe.py` for it. If you fix
a scenario defect, record it in `evaluation/defect-register.md` with the reproduction and
the test that now covers it.

If you find a citation that no longer resolves, check it before fixing it, then record it
in `notes-known-404.txt` if it is genuinely gone.

`research/tooling-superseded/` holds scripts this project wrote and then replaced. They are
kept for provenance and must not be reintroduced; read the README there before adding a new
script that overlaps an existing one.