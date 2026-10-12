# Audit and release report

Date: 2026-10-12. Baseline: git tag `baseline-v0.1` at `ce3d96d`.

## 1. Verdict

**NOT QUALIFIED.**

The release gate (`python3 tests/release_gate.py`) reports **26 PASS, 0 FAIL, 1 BLOCKED, 3
UNVERIFIED** across 30 criteria, on the full run including the live URL audit. (Run offline
with `--skip-urls` it reports 25 PASS and 2 BLOCKED, because the live URL criterion is then
skipped and recorded as BLOCKED rather than passed.) Nothing failed. Qualification is withheld
because one mandatory criterion is BLOCKED and three cannot be settled by machine.

| Blocker | Why it blocks |
| --- | --- |
| **D3** Technical ground-truth review of every scenario | Two of four audit files are not yet written. 53 of 103 scenarios have a recorded technical review. A partial review is not a completed review, and reporting it as one would be the exact error this project exists to prevent. |
| **E5** Model evaluation | No model-execution budget in this environment. |
| **G1**, **G2** Easy/medium/hard and adversarial/regression model runs | Same. |

None of the three UNVERIFIED items is counted as a pass anywhere in this project.

**A 100% score on the defined test suite was reached. That is not a claim of 100% correctness
across all Apigee configurations and future incidents, and nothing in this repository asserts
one.**

## 2. Defects

| Severity | Found | Resolved | Remaining |
| --- | --- | --- | --- |
| Critical | 2 | 2 | 0 |
| High | 4 | 4 | 0 |
| Medium | 10 | 6 | 4, all accepted with a stated reason |
| Low | 3 | 3 | 0 |
| **Total** | **19** | **15** | **4 accepted** |

Full detail with reproduction steps in `evaluation/defect-register.md`.

### The two critical defects

**The fault-code index asserted one HTTP status for a code documented with two.** Apigee
documents many fault codes on several policy pages and the pages disagree. The generator kept
the first occurrence, so the published index said `steps.oauth.v2.invalid_access_token` is
HTTP 401 while `get-oauth-v2-info-policy` documents the same code as HTTP 500. 82 codes were
affected, and for 2 of them the discarded value was the one a support engineer needed.
Reproduce:

```bash
grep 'invalid_access_token' research/pages/api-platform_reference_policies_get-oauth-v2-info-policy.txt
grep 'invalid_access_token' .agents/skills/apigee-support-core/references/error-codes.md
```

**Two scenarios were invisible to every tool.** MED-32 and MED-40 had their heading jammed
onto a horizontal rule:

```
---### MED-32. Six requests admitted where three per minute is configured
```

Every block splitter anchors on `^#{2,4}\s+`, so both were skipped by the structural checker,
received no evaluation packets, and appeared in no index. The library has always held 103
scenarios; the tooling only ever saw 101. **This is the entire explanation of the 101-versus-103
discrepancy in the original report**, and it means the original count was right and the
instrument was wrong.

## 3. Before and after

| Measure | Before | After |
| --- | --- | --- |
| Scenarios the tooling can see | 101 | 103 |
| Checker false passes (of 25 fault-injection probes) | 8 | 0 |
| Fault-injection probes | 25 | 31 |
| URL result states | 4 (OK / BROKEN / SOFT404 / BLOCKED) | 10 |
| URL audit on zero inputs | exit 0, "no URLs found" | exit 2, explicit error |
| URL classifier fixtures | 0 | 15, offline |
| Cached pages with a verified URL and recorded provenance | 109 of 294 | 289 of 294, 5 declared UNRESOLVED |
| Fault codes whose conflicting HTTP statuses are visible | 0 of 2 | 2 of 2, marked CONFLICT |
| Prompt packets with a verified no-leak result | not checked | 206, plus a canary leak |
| Origin classification | 53.4% real-world (reported) | 33.0% real-world (measured and enforced) |
| Duplicate scenarios | not checked | none at any similarity threshold |
| Ground-truth fault codes verified against source | not checked | 73 of 73 |
| Release gate | did not exist | 30 criteria, machine-readable |

## 4. Scenario report

The categories below are deliberately separate and are not summed into a single number.

| Category | Count |
| --- | --- |
| Defined in `scenarios/*.md` | 103 |
| Structurally valid (required sections, real content, unique IDs, parseable XML/JSON) | 103 |
| Have a complete packet set (turn 1, turn 2, answer key) | 103 |
| Carry non-empty critical-failure conditions | 103 |
| Every cited fault code verified against the source corpus | 103 |
| Technically reviewed against source pages, recorded | **53 of 103** |
| Source-verified provenance, individually confirmed | 34 real-world cases; remainder are documented or synthetic by construction |
| Evaluated with an actual model | **0** |
| Blocked or unverified | 50 unreviewed; all 103 unevaluated by model |

Per-suite origin, measured not reported: easy 15 documented; medium 11 documented, 30
real-world, 4 synthetic; hard 6 documented, 4 real-world, 12 synthetic; adversarial 13
synthetic; regression 8 synthetic.

## 5. Source and research report

Live audit, 2026-10-12: **168 unique URLs from 842 citation occurrences.**

| Classification | Count |
| --- | --- |
| Verified | 60 |
| Redirected and verified | 108 |
| Soft 404 | 0 |
| Broken / not found | 0 |
| Access restricted | 0 |
| Rate limited | 0 |
| Transient failure | 0 |
| Content mismatch | 0 |
| Unverified | 0 |
| Invalid URL | 0 |

108 of 168 resolve through a permanent `cloud.google.com` to `docs.cloud.google.com` redirect
and are reported separately rather than followed silently. One citation,
`apigee.com/about/support/portal/`, redirects to the product home page rather than to a
support portal and is a genuine dead reference; it is recorded rather than quietly rewritten.

The raw count of cached pages is not a measure of research completeness and is not used as
one. What is measured is provenance: 109 pages have a URL recorded by `fetch.sh` at fetch
time, 172 had a URL derived from the lossy filename encoding and confirmed live, 8 were
corrected, and 5 are declared UNRESOLVED with a reason instead of being given a plausible
guess.

### Unresolved source conflicts

**`evaluation/source-conflicts-loadbalancing.md` — status DOCUMENTATION_CONFLICT.** Two
current official pages, both scoped to "Apigee and Apigee hybrid" and both last updated
2026-10-09, contradict each other on whether a failed load-balanced target returns to
rotation when `<MaxFailures>` is non-zero and no health monitor is configured. The
load-balancing page says Apigee re-checks every five minutes and returns it; the
antipatterns page says it is not returned and the proxy must be redeployed. Each candidate
explanation was tested and none holds. The Edge mirror renders both sentences on one page.
Both statements are recorded verbatim; neither is chosen. The sources establish that the
documentation contradicts itself, not what the runtime does.

**`evaluation/source-notes-opdk-knownissues.md` — status RESOLVED.** The known-issues
register scopes itself to "Apigee and Apigee hybrid" and offers no Edge for Private Cloud
filter, so it contains no OPDK entries by design. 102 cached entries, 0 matching OPDK. This
is a statement about the register's scope, not evidence that any OPDK issue does not exist,
and the report says so explicitly.

## 6. Evaluation report

| | |
| --- | --- |
| Model and configuration | **None executed** |
| Scenarios executed with a model | 0 of 103 |
| Outputs graded | 0 |
| Structural validation | 103 of 103 |
| Technical review | 53 of 103 |
| Prior A/B run on record | 7 scenarios, one model, one grader |

The prior run cannot support a general effectiveness claim and is not used for one. Critical
failures are declared in `evaluation/rubric.md` and per scenario, every answer key carries
its own conditions, and all 103 reach the grader intact. Whether the critical-failure
override holds *in practice* is an E5/G1 question this project has not answered.

## 7. Reproduction

```bash
python3 tests/check_repo.py --strict    # offline, ~20s
python3 tests/check_urls.py --fixtures  # offline, ~1s
python3 tests/test_leakage.py           # offline, ~90s
python3 tests/fault_probe.py            # offline, ~20min
./tests/check_urls.sh                   # network, ~10min
python3 tests/release_gate.py           # everything, machine-readable
```

Requirements: Python 3.9+, `curl` on PATH, network for the URL checks. No credentials, no
services, no environment variables. The offline subset is sufficient to reproduce every
mechanical finding in this report.

## 8. Limitations

These are material and are not appendix material.

1. **No model evaluation.** The central claim this project would want to make — that the
   skills improve an answer — is entirely unevidenced. Everything here establishes that the
   suite is sound and the ground truth is right, not that the skills work.
2. **53 of 103 scenarios have a recorded technical review.** The 50 unreviewed ones have
   passed every mechanical check, which is not the same as being correct. MED-26, HARD-19,
   HARD-20 and HARD-21 were all found wrong by review, and all four were mechanically
   undetectable until the code check was added. The remaining unreviewed scenarios should be
   assumed to contain a comparable rate of the same class of defect.
3. **Ten cited URLs have no local cached copy.** They were verified live during review. A
   future reviewer working only from the corpus cannot check what they say.
4. **The fault-code index is still an index.** Cause text is truncated at 110 characters and
   the policy page is authoritative. It also lists every page that documents a code rather
   than choosing one, which is correct but means an agent must still open the page.
5. **Content matching in the URL checker is heuristic.** A 200 whose body does not mention
   the cited slug is reported `CONTENT_MISMATCH` for a human, not auto-failed. A page that
   200s with the right slug but wrong content would pass.
6. **The load-balancing conflict is unresolved** and is likely to stay that way without a
   runtime test on a real org.
7. **The OPDK conclusion covers only the register's scope.** Whether OPDK issues are
   documented anywhere else was not exhaustively searched.
8. **108 of 168 citations redirect**, so the corpus will break if Google changes them again.

## 9. What it would take to qualify

1. Write the two outstanding audit files so all 103 scenarios have a recorded technical
   review, and fix what they find.
2. Execute a model evaluation over the full set with a predeclared rubric and retained
   outputs, and report it separately from structural validation.
3. Fetch and cache the ten uncached OPDK URLs so the corpus is self-contained.
4. Re-run the gate. Qualification requires every mandatory criterion to be PASS.
