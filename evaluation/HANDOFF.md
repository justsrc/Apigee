# Handoff: Apigee scenario library audit

Written 2026-10-12. Repository: `/Users/justinjacob/Projects/Work/Apigee`.

This document is for whoever picks the work up next. It states what was verified, what
changed, what is still wrong, and what has not been done at all. Everything here was run
or read, not inferred. Where a number is a measurement, the command that produced it is
named so you can reproduce it rather than trust it.

Read this file, then `evaluation/audit-medium-A.md` for the per-scenario detail on the most
recent pass. The earlier passes are in `audit-easy-adv.md`, `audit-medium-B.md` and
`audit-hard-reg.md`.

---

## 1. What this repository is

A training and evaluation kit for an Apigee technical support skill.

- Three skills under `.agents/skills/`: `apigee-support-core`, plus the two OPDK skills.
- 103 support scenarios split across five graded files in `scenarios/`.
- Generated reference files the skill points at but does not inline, chiefly
  `references/error-codes.md`.
- A mechanical test suite in `tests/` and an audit trail in `evaluation/`.
- A cached research corpus in `research/`: 295 doc pages and 39 GitHub issue threads,
  fetched once so that review never depends on the network.

Scenario counts, from `grep -c '^### [A-Z]' scenarios/*.md`:

| File | Scenarios | Nature |
| --- | --- | --- |
| `easy.md` | 15 | Narrow cases, short path to an answer |
| `medium.md` | 45 | Two or more live hypotheses, or a component interaction |
| `hard.md` | 22 | Competing causes, some with deliberately insufficient evidence |
| `adversarial.md` | 13 | Built to break a named behaviour. Not incidents |
| `regression.md` | 8 | Cheap to run, sharp to fail on |
| total | 103 | |

`medium.md` has 46 `### ` headings because one is a closing section listing cases
deliberately not converted into scenarios. It holds 45.

---

## 2. Where the project stands

HEAD is `f9d7de8 Review MED-01..MED-22, fixing twelve defects`. Working tree clean.

### Release gate

`python3 tests/release_gate.py`, full run including the live URL audit:

```
counts: PASS 27, UNVERIFIED 3
VERDICT: QUALIFIED
```

**27 PASS, 0 FAIL, 0 BLOCKED, 3 UNVERIFIED.**

Run it offline with `--skip-urls` and you get `BLOCKED 1, PASS 26`, because the live URL
criterion is recorded as blocked rather than passed when skipped. That is the checker being
honest, not a regression. Do not read the offline result as a failure.

### Mechanical checks

| Check | Result |
| --- | --- |
| `python3 tests/check_repo.py --root .` | `RESULT: PASS` |
| `python3 tests/test_leakage.py` | `RESULT: PASS, no ground truth leaks into any prompt packet` |
| `python3 tests/fault_probe.py` | `32 probes, 32 behaved as expected, 0 false passes, 0 skipped` |
| `python3 tests/check_urls.py` | `RESULT: PASS, all 171 unique URLs verified (882 citation occurrences)` |

One caution on the URL check. It is network-dependent. A run during this session reported
`82 URL(s) unverifiable from this environment`, all GitHub and Stack Overflow timeouts.
A later run of the same command against the same commit passed all 171. Transient network
failure, not citation rot. Re-run before drawing conclusions.

### What the gate's three UNVERIFIED items mean

They are the model-evaluation criteria, and they cannot be settled without running a model:

- **E5** Model evaluation executed. The one prior A/B run covers 7 scenarios with a single
  grader and is a smoke test.
- **G1** Representative easy, medium and hard cases evaluated.
- **G2** Adversarial and regression suites evaluated.

They are counted nowhere as passes. This is the largest honest gap in the project and it is
the first thing to pick up. See section 6.

---

## 3. What this session did

### The gap that was open

Your earlier read was right that the errors were fixed. `check_repo.py`, the leakage test
and the fault probes all passed on arrival, and the tree was clean. But the release gate
still reported `NOT QUALIFIED` at **3 of 4 audit files**. Criterion D3 requires every
scenario to have a recorded technical review, and `audit-medium-A.md`, covering MED-01
through MED-22, had never been written. That was the real remaining work.

### How the review was run

Six read-only subagent passes over `scenarios/medium.md`, three or four scenarios each.
Every pass was told to grep the cached corpus and cite `file:line` for each finding, and to
edit nothing. Findings came back to parts files, which were then consolidated into
`evaluation/audit-medium-A.md` and the parts deleted.

The checklist each pass was given, drawn from defect classes that had actually bitten this
project before:

1. Invented or wrong XML, wrong element names, wrong capitalization.
2. Misattributed fault code, or right code with the wrong HTTP status.
3. Self-contradiction between diagnostic evidence and ground truth.
4. Remediation that cannot produce what its own verification section demands.
5. Unsupported attribution to a maintainer, issue, or doc.
6. Title leakage (later ruled non-actionable, see section 5).
7. Unsatisfiable premise.
8. Wrong difficulty classification.
9. A critical-failure list a technically correct answer could trip.

### Result

**Ten of 22 sound. Twelve defective: five high, four medium, three low.**

| Scenario | Verdict | Defect |
| --- | --- | --- |
| MED-01 | OK | Edge claim stated flatly where `products.md:48-52` hedges. Low, not load-bearing |
| MED-02 | **high** | 404 explained by borrowing MED-01's env-group verdict |
| MED-03 | OK | |
| MED-04 | OK | |
| MED-05 | OK | |
| MED-06 | low | Answer key read "not evidence of applause" |
| MED-07 | **high** | `setSyncAuthorization` scoped per environment; it is org-scoped |
| MED-08 | OK | |
| MED-09 | low | Retry inside same window claimed to succeed |
| MED-10 | **high** | Trace showed `VerifyAccessToken` succeeding on an expired token |
| MED-11 | OK | |
| MED-12 | medium | Metadata called target timeout a 500; docs say 504 |
| MED-13 | medium | Promised two causes, supplied one |
| MED-14 | **high** | Omitted `<CacheExpiryInSeconds>`, the documented lever |
| MED-15 | OK | Prior critical defect confirmed fixed |
| MED-16 | medium | Cited code real but outside the index (see section 4) |
| MED-17 | OK | |
| MED-18 | **high** | Conjunction inverted |
| MED-19 | OK | |
| MED-20 | low | SaaS-scoped defect imported into a hybrid scenario |
| MED-21 | OK | |
| MED-22 | medium | Cassandra verification premised on an upgrade not happening |

### The five high-severity defects

Each asserted a mechanism that cannot produce the fault it describes, and each contradicted
its own ground truth.

**MED-02.** The ground truth required the agent to attribute a 404 to "the environment group
issue from MED-01", meaning `prod` sits in no group. But
`environmentgroups-working-with.txt:95` says an environment in no group has no hostname at
all, while MED-02's own evidence has a colleague using that hostname and analytics showing
`prod` traffic. Rewritten so both symptoms follow from one cause, which is propagation:
an MP still on revision 11 gives the old behaviour, an MP that has not applied revision 12
has no route and returns 404.

**MED-07.** Said sync authorization "was never configured for this environment" while
asserting sibling environments were fine. `hybrid_v1.17_synchronizer-access.txt:94,111`
shows the call is `organizations/{org}:setSyncAuthorization`. An org-scoped grant cannot be
absent for one environment and present for its siblings, so the premise was unsatisfiable.
The scenario now uses a second organization, which is the scope the API actually has. The
scenario also stacked a separate per-environment service-account role defect the
remediation did not fully address; that is gone.

**MED-10.** The diagnostic evidence said `VerifyAccessToken` succeeded on a token the
ground truth calls expired. `oauthv2-policy.txt:1330` makes that step fail 401 for an
expired token, so the request could never have reached the later `SetOAuthV2Info` step. The
underlying thesis, 401 from `VerifyAccessToken` and 500 from `GetOAuthV2Info` or
`SetOAuthV2Info`, was correct and stayed. Only the evidence line was wrong, and the
unsatisfiability is now stated in the ground truth so it cannot be reintroduced.

**MED-14.** The three-minute window is documented. The remediation was not: it offered
upstream IdP revocation, which cannot shorten Apigee's own cache and contradicts the
premise, since Apigee holds the token. `oauthv2-policy.txt:442` documents
`<CacheExpiryInSeconds>`, supported range 1 to 180, and describes exactly this use case:
reducing the window during which revoked tokens are treated as valid. The rubric's top
anchor had rewarded the wrong action, so a correct answer scored at or near zero. Added the
lever, made it a critical failure to assert the window is fixed, and rewrote the rubric.

**MED-18.** Asserted that checking one gating condition, finding it absent, "wrongly closes"
the case. `apigee-known-issues.txt:265` documents WIF **and** an HTTP forward proxy
together, so one negative check correctly excludes it. This rule had been inherited into
`.agents/skills/apigee-support-core/references/hybrid.md:96`, which the skill loads, so both
were corrected.

### Medium and low

**MED-16** correctly cites `steps.oauth.v2.InvalidRequest`, documented at
`oauthv2-policy.txt:1340` with HTTP 400, but that code was absent from the index
`medium.md` calls authoritative. Root cause in section 4.

**MED-20** imported known issue 246774745, whose register `affects` column reads `Apigee`,
into a hybrid scenario, then made it load-bearing in both remediation and verification.
Confirmed by reading `research/ki-scored.json`. Removed as a compounding cause and kept as
an explicit near miss, since excluding it by checking the register's own `affects` column is
the diagnostic work.

**MED-22** required verifying Cassandra backup and restore "because [it] cannot work with
mixed hybrid versions", while the scenario states twice that both clusters run the same
version with no upgrade in progress. The remediation never touches Cassandra, so a correct
answer could not justify the step. Step replaced with the certificate check that the
remediation actually produces, and the Cassandra claim is now named as the wrong turn.

**MED-12** metadata claimed a callout timeout and a target timeout "both present as a
500". A ServiceCallout `<Timeout>` expiry is HTTP 500 per `service-callout-policy.txt:416`;
a target read or write timeout is 504 per `endpoint-properties-reference.txt:85,276` and
the 504 playbook. Metadata corrected and the status split made explicit, since seeing 500
is itself the evidence for which timeout fired. The scenario body was already right.

**MED-13** promised two conditions producing one error code and supplied one, contradicting
its own evaluation objective. Rewritten to genuinely supply two, sharing the error
description from `javascript-runtime-errors.txt:537`, where the discriminator is the policy
name and source line inside the fault string rather than the code or the prose. The
documented message is `Cannot read property "length" from undefined`; the scenario had
written "of undefined" and dropped the `Execution of <Policy> failed with error:` wrapper.

**MED-09.** Evidence claimed a retry inside the same quota window succeeds. `quota-policy.txt:591`
says "If the counter for the policy reaches this limit value, subsequent calls are rejected
until the counter resets", repeated at line 421 and line 1020. Corrected.

**MED-06.** The answer key read "The absence of a deploy is not evidence of applause". The
word appears nowhere else in the corpus. The argument was sound, the wording was not.

---

## 4. The suite-level defect

Worth separating from the twelve, because it was in the tooling rather than the content and
it had been hiding since the project began.

`medium.md` instructs agents to treat `references/error-codes.md` as authoritative. MED-16
correctly cited `steps.oauth.v2.InvalidRequest` and the index did not contain it.

The cause was in `research/build_error_index.py`. The page parser matched its section marker
with:

```python
m = re.search(r"^## Error reference\s*$", text, re.MULTILINE)
```

Two policy pages publish that heading as `## <span id="errorcodes"></span>Error reference`.
The match failed, the function returned `None`, and both pages were discarded whole:

- `api-platform_reference_policies_oauthv2-policy.txt`, losing 18 runtime codes
- `api-platform_reference_policies_verify-iam-policy.txt`, losing its runtime and
  deployment tables

Nothing reported the loss. A page that fails to parse is indistinguishable from a page with
no error section, so the coverage guard had nothing to complain about. This is the failure
mode the project had already written down about itself in `evaluation/outstanding-errors.md`:
a generated reference that is quietly incomplete is worse than none, because it is trusted.

Fixed by tolerating leading inline markup. Counts moved:

| | before | after |
| --- | --- | --- |
| Runtime codes | 173 | 195 |
| Deployment errors | 107 | 116 |
| Fault variables | 28 | 33 |

Covered by probe `error-index-generator-drops-anchored-error-sections` in
`tests/fault_probe.py`. The probe reverts the regex in a sandbox copy and asserts the
checker catches the resulting stale index. Verified it behaves as expected, and that it is
not a silent pass.

---

## 5. Two findings that are not defects

Recorded so the next pass does not re-raise them.

**Scenario titles never reach the agent.** `tests/make_packets.py:206-217` writes
`# Support case <ID>` into the prompt and deliberately omits the title, with a comment
explaining that regression titles are statements of the correct disposition and handing
those over would hand over the grading criterion. Verified: `MED-02.prompt.md` line 13 reads
`# Support case MED-02`. Titles survive only in the answer key, for the grader. Two
reviewers reported title leakage as a defect anyway. Those findings are superseded, and the
note is recorded in both `audit-medium-A.md` and the defect register.

**MED-15 was previously recorded as unsatisfiable.** That defect was genuinely fixed in an
earlier round. Re-read and confirmed clean.

---

## 6. Disagreements between reviewers

Two scenarios were audited twice, independently, and the passes did not agree. Both
disagreements are recorded in `evaluation/audit-medium-A.md` with evidence, rather than
resolved silently.

**MED-09.** One pass called it clean. The other found the retry claim. I checked
`quota-policy.txt:591` myself: the second reviewer was right, the defect was real, and the
fix stands. The later pass then re-read the corrected text and found it sound.

**MED-10.** Both passes found a defect, and disagreed only on severity, medium against
high. Recorded at high, because the premise was unsatisfiable and an answer that reasoned
correctly could not have satisfied it.

One process note. Two of the six review agents returned an empty result and wrote no file.
The work was redone by resuming one session and relaunching the other. If you fan out review
work, verify each agent actually wrote its output rather than trusting the launch.

---

## 7. What was changed

Commit `f9d7de8`, 28 files, +2349 / -262.

| Area | Change |
| --- | --- |
| `scenarios/medium.md` | 12 scenarios rewritten. +348 / -262 lines net across the file |
| `research/build_error_index.py` | Heading match tolerates leading inline markup |
| `.agents/.../references/error-codes.md` | Regenerated. 22 runtime codes, 9 deployment errors and 5 fault variables recovered |
| `.agents/.../references/hybrid.md` | Conjunction rule corrected (MED-18) |
| `tests/fault_probe.py` | +1 probe, 31 to 32 |
| `evaluation/audit-medium-A.md` | New, 1688 lines, 22 scenarios |
| `evaluation/defect-register.md` | +D-028 through +D-031 and a title-leak note. Status table updated to 18 fixed-with-test, 6 fixed-with-coverage-recorded |
| `evaluation/packets/` | Regenerated for 12 scenarios, both turns |
| `CHANGELOG.md` | New dated entry |
| `README.md` | Fault code count 173 to 195, plus why |

Every one of the twelve rewrites is recorded in the commit message with the source citation
that justifies it.

---

## 8. What is still wrong, or unproven

### Open, blocking release

**None.** The register's status table reads 0 open blocking.

### Open, accepted with a documented reason (8)

These are deliberate and recorded, not oversights.

| ID | Item | Why accepted |
| --- | --- | --- |
| D-013 | Fault-code index truncates cause text at 110 characters | It is an index and says so. Full text is on the source page, cited per row |
| D-014 | `decode-jws-policy` documents 20 error names in one table cell | Faithful to source. Now split into rows and flagged as listed together upstream |
| D-016 | Ground-truth correctness cannot be script-checked | By design. This is what the audit files are for |
| D-017 | No model evaluation run | No execution budget in this environment |
| D-024 | Most citations permanently redirect `cloud.google.com` to `docs.cloud.google.com` | Resolving is verified and the chain is recorded. Rewriting risks breaking scenario prose that quotes URLs |
| D-025 | `docs.apigee.com` Edge slugs carry the release | Real and unavoidable. Recorded in `notes-known-404.txt` |
| D-026 | Known-issues register has no OPDK entries | By design, it scopes itself to "Apigee and Apigee hybrid" |
| D-027 | Two current official pages contradict each other on load-balanced target rotation | Unresolvable from the sources. Both recorded verbatim in `source-conflicts-loadbalancing.md`, neither chosen |

### Open, awaiting external evidence (2)

The status table counts 2 but does not name them. From the entries that describe themselves
as unresolvable, these are D-027, the load-balanced target rotation contradiction, and the
related unverified claim in `evaluation/source-conflicts-loadbalancing.md`. Worth confirming
against the register before relying on that identification, since the table itself is not
itemised.

### Stale figures you should fix first

**`D-024`'s redirect count is now wrong.** It says "108 of 168 citations redirect".
Measured today: **111 of 171 unique URLs** redirect and verify, across 882 citation
occurrences. The count moved because MED-07 and MED-13 added reference URLs during this
session. Same problem in `evaluation/RELEASE-REPORT.md` lines 121 and 205. Low severity,
but it is exactly the prose-drift class this project already logged as defect D3.

**`evaluation/outstanding-errors.md` is a dated record** and still describes 65 and 72
scenarios, 165 and 174 runtime codes, and lists HARD-07, HARD-14, REG-06, HARD-03,
HARD-05, HARD-11, EASY-12 and MED-15 as unfixed. Most of those were fixed in later rounds.
The file says at the top that it is a dated record, so leaving it is defensible, but anyone
reading it cold will draw wrong conclusions. Either update it or mark it superseded in its
first paragraph.

**`evaluation/RELEASE-REPORT.md` says `NOT QUALIFIED`** and lists "write the two
outstanding audit files" as the next step. That is now done and the gate says `QUALIFIED`.
The report is stale at the top.

### Not done at all

**The model evaluation.** No scenario has been evaluated by a model under a predeclared
rubric with retained outputs. This is criteria E5, G1 and G2, the three UNVERIFIED items,
and it is the most substantive gap left. `evaluation/rubric.md` exists but the project
records that it says "weighted total" while specifying no weights, and its per-scenario
tables score 3 to 5 of its 10 dimensions.

**The ten uncached OPDK URLs.** `RELEASE-REPORT.md` item 3 recommends fetching them so the
corpus is self-contained. Not attempted.

**No second reviewer for any of the twelve fixes.** Every fix in this session was verified
against the source by the agent that made it, and the mechanical checks pass, but a correct
grep is not the same as a correct reading. MED-13 in particular was substantially rewritten
in structure rather than corrected, and is the one most worth a second pair of eyes.

---

## 9. Recommended next steps

In the order I would take them.

1. **Fix the three stale figures** above: D-024's redirect count, `RELEASE-REPORT.md`'s
   verdict and outstanding-files list, and the status of `outstanding-errors.md`. Cheap, and
   leaving them means the repo contradicts itself in four places.

2. **Run the model evaluation.** Predeclare the rubric, including fixing the weighting gap in
   `evaluation/rubric.md`, then execute over a stratified sample: some easy, medium, hard,
   adversarial and regression. Retain raw outputs and the grader transcript. This closes
   E5, G1 and G2 and is the only work that tests whether any of this content actually
   teaches anything. Everything so far establishes that the scenarios are correct, not that
   they work.

3. **Second-review the twelve fixes**, MED-13 first. The mechanical checks cannot tell a
   correct fix from a plausible one.

4. **Fetch the ten uncached OPDK URLs** so the corpus is self-contained and a future review
   never needs the network.

5. **Consider a guard for the D-029 class.** The bug was a heading match that assumed a
   format Google does not always publish. A check that every page with an error section
   contributes at least one row would catch the next instance. The coverage guard mentioned
   in `outstanding-errors.md` did not catch this one.

---

## 10. Reproducing the verification

```bash
cd /Users/justinjacob/Projects/Work/Apigee

# Structural and content checks. Offline, fast.
python3 tests/check_repo.py --root .          # RESULT: PASS
python3 tests/test_leakage.py                 # no ground truth leaks
python3 tests/fault_probe.py                  # 32 probes, 32 as expected

# Full gate. Needs network, several minutes.
python3 tests/release_gate.py                 # 27 PASS, 3 UNVERIFIED, QUALIFIED
python3 tests/release_gate.py --skip-urls     # offline; BLOCKED 1 is expected
python3 tests/check_urls.py                   # 171 unique URLs, 882 occurrences

# Regenerate derived files after any edit to scenarios/ or research/pages/.
python3 research/build_error_index.py
python3 research/build_scenario_index.py
python3 tests/make_packets.py --all --turn 1
python3 tests/make_packets.py --all --turn 2
```

Order matters if you edit scenarios. `check_repo.py` fails on stale packets, which is the
guard working, not a problem. Regenerate both turns before running the checker.

---

## 11. Things worth knowing before you trust a green check

The project's own finding, from `evaluation/outstanding-errors.md`, and it has not been
retracted: round one passed every mechanical check and every URL check while roughly a
quarter of its scenarios had a material defect. A passing harness in this repository says
almost nothing about content correctness.

What that means practically:

- The fault probes test the checkers, not the scenarios. All 32 passing means the tooling
  detects what it is designed to detect. It does not mean the scenarios are right.
- `check_repo.py` verifies structure, IDs, section presence, packet freshness, and that
  fault codes quoted in scenarios exist in the corpus. It cannot verify that a quoted code
  has the right HTTP status attached to it, which is how MED-12 and MED-10 got through.
- The only defence found so far against that class is a human or model reading the scenario
  against the cached page and citing lines. That is what the four audit files are, and why
  they are written per scenario rather than summarised.
- Reviewer disagreement is normal here. MED-09 and MED-10 each produced two conflicting
  verdicts. Resolve disagreements against the source and record both readings. Do not quietly
  drop one.