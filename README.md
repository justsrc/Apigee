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
| `scenarios/medium.md` | 43 | Two or more live hypotheses, or a component interaction |
| `scenarios/hard.md` | 22 | Competing causes, some with deliberately insufficient evidence |
| `scenarios/adversarial.md` | 13 | Built to break a specific behaviour. Not incidents. |
| `scenarios/regression.md` | 8 | Cheaper to run, sharp to fail on. Rerun after any skill change. |

`scenarios/index.md` is generated from those files. 101 scenarios in total.

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
python3 tests/check_repo.py    # structure, IDs, sections, frontmatter, local links
./tests/check_urls.sh          # every cited URL resolves to real content
```

`check_repo.py` checks what a script can honestly check: files exist, scenario IDs are
unique, each graded file has at least 15 scenarios, every scenario has its required
sections with real content, skill frontmatter is well formed, and relative links resolve.

It does not and cannot check whether a scenario's technical content is correct. It prints
a separate block listing what needs human or model review, so a clean run is never mistaken
for a correct suite. Read that block. Add `--strict` to fail on warnings.

`evaluation/` holds the rubric, the A/B test protocol, generated packets, the eval runs with
their grading and metadata, the hostile reviews of the scenario library, and
`baseline.md`, which records the measured correctness baseline.

The honest current numbers: 101 scenarios, and `baseline.md` records what blind review found
and what it did not. Roughly a quarter of the library was materially wrong at first review.
Read `baseline.md` before trusting any single scenario as ground truth.

`check_urls.sh` fetches every URL cited anywhere in the skills, references, scenarios,
README and changelog, and checks both the status and the body. It found two broken
citations during setup, which is why it exists. A 200 is not enough on its own here,
because `cloud.google.com` serves a stub page at HTTP 200 for paths that do not exist.

Both scripts were wrong before they were right. The URL checker's first version reported
PASS having checked nothing, and the repo checker's section matcher silently skipped every
scenario whose title contained a section name. Both now fail loudly instead, and
`check_urls.sh` was tested against known-bad URLs to confirm it still fails.

## Adding a scenario

1. Find the fault code in `research/official-documentation-index.md`, or add the page and
   re-run the fetch. Do not write a code from memory.
2. Write the ticket so it reads like a person wrote it and does not reveal the cause.
3. Give the ground truth a source. If you cannot source it, mark the scenario synthetic
   and say the mechanism is unverified.
4. Fill every required section. The harness will tell you which are missing.
5. Run `python3 tests/check_repo.py`.

The section that catches the most bad scenarios is common incorrect answers. Writing the
plausible wrong answer is how you find out whether the case actually discriminates.

## Research and sources

`research/` holds the evidence.

`RESEARCH-RECIPE.md` explains how to verify a URL and how to find real ones instead of
guessing. Read it before citing anything.

`fetch.sh` fetches a documentation page, records its real HTTP status, and extracts the
article body. It handles three traps that produce wrong answers silently: soft 404s that
return HTTP 200, pandoc truncating large pages, and URLs guessed from a naming pattern.

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

Verified: every URL cited in a skill or scenario was fetched and returned real content.
Every fault code was extracted from a policy page that was read.

Not verified: that every documented behavior is correctly described in a scenario, which
needs review by someone who knows Apigee. Whether any skill improves an answer in practice,
which needs running the scenarios against real models. Any claim about Edge for Private
Cloud from the `cloud.google.com` policy pages, which carry an "Apigee and Apigee hybrid"
banner and do not describe Edge.

Two documentation defects found during research are recorded because they will otherwise
cause errors. The VerifyJWT policy page is truncated upstream and ends mid-table with no
error reference, so `steps.jwt.*` codes could not be verified anywhere. The OAuth HTTP
status code page is marked deprecated and its `keymanagement.service.*` codes disagree
with the `steps.oauth.v2.*` codes on the OAuthV2 page for the same conditions.

## Contributing

Change the skill, rerun `python3 tests/check_repo.py`, rerun `scenarios/regression.md`.
The regression file exists to catch a skill that got longer and less accurate.

If you find a citation that no longer resolves, check it before fixing it, then record it
in `notes-known-404.txt` if it is genuinely gone.