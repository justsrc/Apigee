# Defect register

Every defect found in the audit, how it was reproduced, what caused it, what changed, and
which regression test now detects it. A defect is only closed when a test fails without the
fix and passes with it. Changing the file is not the evidence; the test is.

Severity, as defined for this project:

- **Critical** — can cause materially false technical advice, a fabricated claim, incorrect
  ground truth, or a false release qualification.
- **High** — omits important information, misdiagnoses a significant class of issue,
  invalidates an evaluation, or silently bypasses required validation.
- **Medium** — reduces coverage, maintainability, or the reliability of noncritical output.
- **Low** — minor, limited impact.

## Status summary

| Status | Count |
| --- | --- |
| Open, blocking release | 0 |
| Fixed and covered by a test | 31 |
| Fixed, coverage recorded, no dedicated probe yet | 9 |
| Open, accepted with documented reason | 9 |
| Open, awaiting external evidence | 2 |
| Open, reproduced and not yet fixed | 2 |

Three entries changed on 2026-10-13. D-035 adds the seventh fixed-without-a-dedicated-probe
entry. D-036 adds two probes for the packet generator. The isolation-route classifier is what
moves fixed-and-covered from 19 to 21 alongside them: `tests/test_isolation_classify.py` is a
test file of its own and `release_gate.py` F6 fails if it regresses.

Three entries were added on 2026-10-14, D-038 through D-040, all found by running the
evaluation harness against a clean checkout rather than against the working tree the
earlier passes left behind. D-038 and D-039 are both about the fault-probe suite reporting
green without evidence: D-038 made every FAIL-expecting probe vacuous, and D-039 records two
probes that had never mutated anything. D-040 is the one remaining path that could still write
a failure into an answer file. Fixed-and-covered moves from 21 to 24.

Two more were added on 2026-10-14, D-041 and D-042, both in the run-3 grading script. D-041 is
the most consequential defect this pass found after D-038: the component that writes a score
never read the manifest, so a scenario recorded as never run could be written out as a pass.
Neither was reachable from a real run, because run 3 collected nothing, and both are recorded
as latent rather than as damage to a recorded result. Fixed-and-covered moves from 24 to 26.

A third review pass added eleven more, D-043 through D-053. Nine are now fixed: D-043, D-047
and D-051 carry a probe or a suite each, D-049 and D-050 are fixed with 13 new cases between
them, and D-044 and D-046 are fixed with the behaviour itself as the evidence rather than a
dedicated test. Fixed-and-covered goes from 26 to 31 and the coverage-recorded row from 7 to 9.
Two are reproduced and open, D-045 in part and D-052, and D-053 is a disagreement between two
documents about a sample size, recorded rather than fixed because the sample was declared in
advance and editing it after the fact is the thing the freeze exists to prevent.

The summary gains a row for findings that are reproduced and not yet fixed. "Open" previously
meant either something somebody had decided to live with or something nobody had looked at, and
the table could not tell them apart.

## Later additions

### D-018 HIGH — Origin classification was inflated by 21 scenarios

**Affected** scenario metadata across all five files

**What failed.** The project reported its scenario library as 53.4% real-world, 31.1%
documented, 15.5% synthetic. Measured from the scenarios, it is **33.0% real-world, 30.1%
documented, 36.9% synthetic**.

The gap is explained by two constructed suites, not by measurement noise. Adding the 13
`adversarial.md` and 8 `regression.md` scenarios to the 34 real-world gives 55, which is the
reported figure exactly. Those two suites are constructed evaluations and say so in their own
headers.

Two of the three reported counts no longer reproduce to the scenario, and this entry no
longer claims they do. Documented measures 31 against a reported 32, because MED-20 was
relabelled on 2026-10-13 from documented to reported real-world case: it is built from known
issue 471125841, and every other register-sourced scenario in the library already said
reported real-world case. Synthetic measures 17 after removing the constructed suites against
a reported 16. Both were already off before that relabelling, by the same one scenario in the
opposite direction. The inflation finding does not depend on either number: 55 reported against
34 measured is the twenty-one-scenario gap, and that gap is what the correction fixes.

**Why it matters.** Counting synthetic cases as real incidents is one of the specific errors
this project exists to prevent, and it was inflating the library's apparent provenance by
twenty-one scenarios. Anyone reading the reported split would conclude roughly a fifth more
of the library is grounded in real reports than actually is.

**Correction.** `tests/check_repo.py::check_origin_integrity` classifies each scenario from a
controlled vocabulary, fails on a missing or unclassifiable `Origin` field, and refuses
`real-world` on the constructed suites.

**Regression test.** Probes `synthetic-scenario-relabelled-real-world`,
`origin-field-removed`, `origin-unclassifiable-value`.

**Evidence.** `check_repo.py` reports "origin classification is unambiguous across 103
scenarios (34 real-world, 31 documented, 38 synthetic)". All three probes fail without the
fix.

**Status: FIXED.**

---

### D-019 MEDIUM — 185 of 294 cached pages had a guessed URL presented as fact

**Affected** `research/pages/MANIFEST.tsv`, `research/build_doc_index.py`

**What failed.** `fetch.sh` records `name -> URL` as it fetches, and `build_doc_index.py`
depends on that manifest because inverting the lossy filename encoding does not work. The
manifest had drifted badly: 52 recorded names had no matching file, and **185 cached pages
had no manifest entry at all**. For those, `build_doc_index.py` fell back to re-deriving a
URL from the filename and published it in `official-documentation-index.md` as though it had
been fetched.

**Why this is worse than it looks.** `research/notes-known-404.txt` documents that 22 of the
first 39 plausible paths guessed during setup returned 404. Guessing the project's own
corpus is the same move at a much larger scale, and the index gave no sign which URLs were
recorded and which were inferred.

Five pages were cached under scratch names (`rt_spike`, `rt_java`, `rt_py`, `dbg_trace`,
`ui-deploy-new`, `mon_fault-codes`) whose derived URLs 404. The page bodies are real and
useful; only the provenance was wrong.

**Correction.** See D-019, which supersedes this entry.
`research/repair_manifest.py` resolves every cached page live and rewrites the manifest
with a provenance column:

| Provenance | Count | Meaning |
| --- | --- | --- |
| `recorded` | 109 | URL captured by `fetch.sh` at fetch time |
| `guess` | 172 | derived from the lossy filename encoding, confirmed live |
| `corrected` | 8 | scratch filename, real URL confirmed by fetching |
| `UNRESOLVED` | 5 | no confirmed URL, stated with a reason rather than guessed |

**Regression test.** `check_repo.py` requires `research/pages` to be non-empty and reports the
manifest provenance distribution in the release gate (criterion C1).

**Status: FIXED.** The five unresolved pages are declared rather than guessed.

---

### D-020 MEDIUM — `check_repo.py` reported the wrong scenario count

**What failed.** `MIN_PER_DIFFICULTY = 15` is a floor, so it cannot detect a scenario file
losing scenarios down to fifteen. `check_scenarios` also only walked the three graded files,
so a structural problem in `adversarial.md` or `regression.md` was invisible.

**Correction.** Packet completeness is now asserted per scenario ID against `scenarios/*.md`
rather than by counting files, and both additional suites are required to exist.

**Status: FIXED.** Covered by probes `scenario-file-deleted`, `packet-turn2-deleted`,
`packet-key-deleted`.

---

### D-021 LOW — The corpus contains pages cached from paths that never resolved

**Affected** `research/pages/`

**What failed.** Five cached pages have no confirmed URL (D-019). Separately, three playbook
pages were fetched from a guessed path missing the `runtime/` path segment; their content is
real but the URL recorded for them redirects to Google's soft-404 support page.

**Status: OPEN, accepted.** These pages are not cited by any scenario or skill, so they
affect nothing that ships. They are declared `UNRESOLVED` in the manifest. Left in place
because the cached content is genuine documentation and re-fetching costs nothing worth the
time; the honest manifest entry is what matters.

---

### D-022 MEDIUM — Twelve cached URLs cited by scenarios had no local copy

**Affected** 12 URLs, eleven of them Edge for Private Cloud pages cited from `scenarios/hard.md`, plus `antipatterns/intro`

**What failed.** Twelve cited URLs had no page in `research/pages/`: eleven Edge for Private
Cloud operational pages and `antipatterns/intro`, which is a cloud.google.com page scoped to
Apigee and hybrid rather than OPDK. A reviewer working only from the local corpus could not
check what those pages said, which is how HARD-16's invented "eight central types" survived
review.

This entry originally said ten. `evaluation/audit-hard-reg.md:528` is where the ten came from,
and the list it carried was wrong three ways: its tenth item, `view-page`, is not a URL and
appears nowhere else in the repository; its ninth, `antipatterns/intro`, is not an OPDK page;
and three genuinely uncached OPDK pages were missing from the list altogether, because raw
copies of them survive under `research/scratch-pages/` and looked fetched. `9c02e0a` re-derived
the list and cached all eleven OPDK pages.

**Status: PARTIALLY FIXED.** As of `9c02e0a` the eleven OPDK pages are cached and all eleven
answered HTTP 200 under the pinned v4.53.01 release. Five cited documentation URLs still have
no local copy:

| URL | Cited from |
| --- | --- |
| `api-platform/antipatterns/intro` | `hard.md` |
| `api-platform/antipatterns/reusing-quota` | `medium.md` |
| `api-platform/get-started/compare-apigee-products` | `hard.md`, `medium.md`, `regression.md` |
| `api-platform/troubleshoot/playbooks/ingressgateway/api-calls-fail-timeout-errors` | `medium.md` |
| `docs.apigee.com/api-platform/develop/comparing-quota-spike-arrest-and-concurrent-rate-limit-policies` | `medium.md` |

The last one is an `docs.apigee.com` URL whose slug carries the Edge release, so the pinned
release copy is not interchangeable with it (D-025). The rest are cloud.google.com pages the
fetch recipe did not reach. `check_urls.py` resolves all five live, so nothing shipped is
wrong because of this.

---

### D-023 LOW — Six provenance-bearing fields are free text, not a controlled vocabulary

**Affected** scenario metadata

**What failed.** The `Origin:` field carries the classification and a whole citation in one
free-text value, so "reported real-world case (apigee/apigeelint#526, closed and shipped in
v2.67.0)" is a single unqueryable string. Recomputing the library's provenance required
parsing English.

**Correction.** `check_origin_integrity` parses the leading keyword and requires it to be
one of the three classes, so the detail can stay free text while the classification cannot
drift.

**Status: FIXED.** A separate `Origin class:` field would be cleaner but is not necessary
while the check enforces the prefix.

---

## Open items accepted with reason (D-001–D-012)

---

## D-001 CRITICAL — Fault-code index asserted one HTTP status for a code documented with two

**Affected** `research/build_error_index.py`, `.agents/skills/apigee-support-core/references/error-codes.md`

**What failed.** The index deduped by fault code, keeping the first occurrence and
discarding the rest. Apigee documents the same code on several policy pages, and the pages
disagree. Sorted by filename, `delete-oauth-v2-info` came before `get-oauth-v2-info-policy`,
so the index published:

| `steps.oauth.v2.invalid_access_token` | `401` | ... | [delete-oauth-v2-info] |

while `get-oauth-v2-info-policy` documents the same code as HTTP **500**. An agent
triaging a 500 from `GetOAuthV2Info` would be told the documented status was 401. The
same held for `steps.oauth.v2.invalid_request-authorization_code_invalid`.

**Reproduction.**

```text
cd /path/to/this/repository
grep 'invalid_access_token' research/pages/api-platform_reference_policies_get-oauth-v2-info-policy.txt
# `steps.oauth.v2.invalid_access_token` | `500` | ...
grep 'invalid_access_token' .agents/skills/apigee-support-core/references/error-codes.md
# | `steps.oauth.v2.invalid_access_token` | `401` | ...
```

**Cause.** `dedupe(runtime, lambda r: r[0])` with no notion of whether the duplicate
records agreed.

**Correction.** Records are now merged, not dropped. Every source page is listed, and a
status disagreement is rendered as `401, 500 **CONFLICT**` with a dedicated conflict list,
rather than being resolved by sort order.

**Regression test.** `tests/fault_probe.py` probe `error-codes-index-stale`, plus
`tests/check_repo.py::check_generated_freshness`, which regenerates and diffs.

**Evidence of the fix.** Both conflicting codes now appear in the index conflict section;
82 merged codes now list every page that documents them.

**Status: FIXED.**

---

## D-002 CRITICAL — Two scenarios were invisible to every tool

**Affected** `scenarios/medium.md` (MED-32, MED-40)

**What failed.** Both headings were jammed onto a horizontal rule:

```text
---### MED-32. Six requests admitted where three per minute is configured
```

Every block splitter in this project anchors on `^#{2,4}\s+`. Neither scenario matched, so
MED-32 and MED-40 were invisible to the structural checker, received no evaluation
packets, and appeared in no index. They are not headings in rendered Markdown either.

**Reproduction.** Count scenarios the way the tooling does versus the way a reader does:

```text
grep -c '^### ' scenarios/medium.md            # 45 headings
grep -c '^---###' scenarios/medium.md          # 2 more, invisible to every tool
```

**Cause.** An authoring slip in the source Markdown, undetected because every downstream
consumer silently skipped the result rather than reporting the gap.

**Correction.** `---` and the heading are now separate lines. Both scenarios have full
packet sets.

**Regression test.** `tests/fault_probe.py` probe `scenario-id-numbering-gap`, and
`tests/check_repo.py::check_packets`, which now asserts per-scenario packet completeness
against discovered scenario IDs rather than comparing counts.

**Evidence.** Scenario count went 101 → 103, which matches the owner's original report.
`check_repo.py` reports "all 103 scenarios have a turn-1 prompt, a turn-2 prompt and an
answer key".

**Status: FIXED.** This was the entire explanation of the 101-versus-103 discrepancy.

---

## D-003 HIGH — check_repo.py had eight false passes

**Affected** `tests/check_repo.py`

**What failed.** `tests/fault_probe.py` applies 25 controlled mutations to a disposable copy
of the repository and records whether the checker catches each one. Eight mutations passed
a checker that should have failed them:

| Mutation | Old behaviour | Why |
| --- | --- | --- |
| delete one turn-2 prompt | exit 0 | Counts stayed plausible: 103 turn-2 files became 102, and nothing compared them |
| delete one answer key | exit 0 | Same |
| delete a reference file still listed in the skill table | exit 0 | The skill lists references as backticked table paths, not markdown links, so the relative-link check never saw them; the name check is a substring match |
| delete `scenarios/regression.md` | exit 0 | Warned, not failed |
| delete `evaluation/packets/` entirely | exit 0 | Warned, not failed |
| empty `research/pages/` | exit 0 | Warned, not failed, and every generated index then became vacuous |
| corrupt the fault-code index | exit 0 | No freshness check existed; only a raw-HTML check |
| delete a required section from `adversarial.md` | caught only incidentally | Full section checks only walked the three graded files |

**Correction.** Six of the eight were downgraded warnings and are now failures. Packet
completeness is asserted per scenario ID against `scenarios/*.md`, not by count. The
listed reference paths are resolved. A generated-index freshness check regenerates
`error-codes.md` and `scenarios/index.md` into memory and diffs.

**Regression test.** `tests/fault_probe.py` itself. It is the artefact that found these and
it now runs clean.

**Evidence.** 25/25 probes behave as expected, 0 false passes, 0 skipped. Before the
repairs: 17/25, 8 false passes.

**Status: FIXED.**

---

## D-004 HIGH — The URL checker reported a passing audit having checked nothing

**Affected** `tests/check_urls.sh`, `tests/check_url_one.sh`

**What failed.** Four distinct problems.

1. `exit 0` on an empty corpus, printing only `no URLs found to check`. Verified:
   `./tests/check_urls.sh <file-with-no-urls>` exits 0.
2. Four statuses only. A 403 from a bot-blocking host, a timeout, and a genuine 404 all
   reported as `BROKEN`, so a blocked host and a dead citation were indistinguishable.
3. Redirects were followed silently, so a citation that had moved to a page saying
   something else reported `OK`.
4. A 200 carrying unrelated content was `OK`. Only one exact phrase was checked for
   soft-404 detection.

**Correction.** `tests/check_urls.py` classifies every URL into exactly one of
`VERIFIED`, `REDIRECTED_AND_VERIFIED`, `SOFT_404`, `NOT_FOUND`, `ACCESS_RESTRICTED`,
`RATE_LIMITED`, `TRANSIENT_FAILURE`, `INVALID_URL`, `CONTENT_MISMATCH`, `UNVERIFIED`. It
records redirect chains, checks that the body actually mentions the document it claims to
be, retries only what a retry could change, and exits 2 on an empty corpus. An empty
corpus is now an error, not a pass.

**Regression test.** `tests/check_urls.py --fixtures`: 15 offline fixtures with known
answers, including Google's soft-404 stub, a capitalisation variant, a genuine 404, a
redirect, a 403, a 429, a 503, a timeout, a wrong-document 200, and a malformed URL.

**Evidence.** 15/15 fixtures classify correctly. The live audit reports 168 unique URLs
from 842 citation occurrences, all verified or redirected-and-verified.

**Status: FIXED.**

---

## D-005 HIGH — MED-26 asserts a fault code and cause that contradict the source

**Affected** `scenarios/medium.md` MED-26

**What failed.** The ground truth states `JavaCalloutInstantiationFailed` means the class
was found but could not be constructed, and adds that an absent class would be a resource
error. The Java Callout policy page states the opposite: the cause is "The class file
specified in the `<ClassName>` element is not in the jar". The code
`steps.javacallout.JavaCalloutInstantiationFailed` does not exist; the only
`steps.javacallout.*` code documented is `ExecutionError`. `ResourceDoesNotExist` refers to
`<ResourceURL>`, not the class.

**Why critical.** This is wrong ground truth on a deployment fault code, in a scenario whose
entire purpose is teaching that code. An agent is graded against an answer the
documentation contradicts.

**Correction.** The scenario now states the documented cause ("The class file specified in
the `<ClassName>` element is not in the jar"), drops the invented `steps.javacallout.` prefix,
identifies it as a deployment error, and removes the claim that an absent class would be a
resource error. `ResourceDoesNotExist` is correctly described as referring to `<ResourceURL>`.

**Note on the original reasoning.** The corrupted-jar conclusion still holds, and holds
better: a text-filtered jar means the class file bytes are wrong, which is exactly what the
documented cause describes. The scenario arrived at the right answer from a wrong premise,
which is a useful reminder that a correct conclusion is not evidence of correct reasoning.

**Regression test.** `tests/fault_probe.py` plus the review pass that found it; a wrong fault
code is not mechanically checkable, which is why `evaluation/audit-medium-B.md` exists.

**Status: FIXED.**

---

## D-006 HIGH — HARD-20 remediation ships a broken TargetServer config

**Affected** `scenarios/hard.md` HARD-20

**What failed.** The canonical remediation pinned Message Processors with a proxy
`<LoadBalancer><Server name="mp-az1-1"/></LoadBalancer>`. `<Server>` names a
**TargetServer**: a named backend the proxy itself calls. Message Processors are not proxy
targets. An agent copying that XML ships a target-server configuration that cannot work, in
a scenario whose entire subject is Cassandra consistency across zones.

**Correction.** The XML block is removed. The remediation now says explicitly that session
affinity belongs in the load balancer in front of the Routers, and states why putting those
hostnames in a proxy `<LoadBalancer>` would be wrong.

**Status: FIXED.**

---

## D-007 MEDIUM — `MANIFEST.tsv` keys do not match the files on disk

**Affected** `research/pages/MANIFEST.tsv`

**What failed.** `build_doc_index.py` relies on the manifest to map a cached filename back
to its URL, because inverting the lossy filename encoding does not work. But the keys do
not match the files: manifest key `fix-mon-fault-codes` versus file `mon_fault-codes.txt`.
Any lookup that assumes `name -> name + ".txt"` silently falls through to the guess path.

**Status: FIXED, by D-019.** The manifest now carries a provenance column for every cached
page, and `repair_manifest.py` is the reproducible way to regenerate it.

---

## D-008 MEDIUM — Every `error-codes.md` line citation in the scenarios is stale by 4–5 lines

**Affected** `scenarios/medium.md`, `scenarios/hard.md`

**What failed.** Scenarios cite `error-codes.md` by line number, for example
"`error-codes.md` line 43". The fix in D-001 added a header block to that file, shifting
every line reference. The citations now point at the wrong lines.

**Correction.** Deliberately not repaired by re-numbering. A line number into a generated
file is inherently unstable: it breaks again on the next regeneration, and "fixing" it now
would hide the problem until the next change. The correct fix is to cite the fault code
rather than the line, which is a per-scenario edit across several files.

**Status: OPEN, accepted with reason.** No scenario's technical conclusion depends on a line
number, so nothing shipped is wrong because of this; the citations are simply less useful
than they look. Recorded so it is not mistaken for verified provenance.

---

## D-009 MEDIUM — Regression scenario titles disclose their own resolution

**Affected** `scenarios/regression.md`, `tests/make_packets.py`

**What failed.** `make_packets.py` line 206 injects the scenario title into the agent's
prompt. Eight of the eight regression titles state the answer, for example a title that
names the winning explanation. The suite that exists to catch a skill that got longer and
less accurate could not detect anything, because the agent was handed the conclusion. All
eight regression titles are affected, and the adversarial set has the same problem.

**Correction.** `make_packets.py` no longer puts the scenario title in the prompt at all.
The prompt carries the scenario ID and nothing else identifying. The title stays in the
answer key for the grader. This is also more realistic: a support request arrives as a
ticket, not as a headline stating the expected disposition.

**Regression test.** `tests/test_leakage.py` checks all 206 prompt packets for scenario
titles, ground-truth sentences, incorrect-answer text and held-back section headings, and
runs a deliberate canary leak to prove the generator actually holds material back. Verified
to have teeth: reintroducing the title injection produces 206 findings.

**Status: FIXED.**

---

## D-010 LOW — A custom User-Agent caused 154 false rate-limit classifications

**Affected** `tests/check_urls.py` (introduced and caught within this audit)

**What failed.** The rewritten checker sent
`Mozilla/5.0 (compatible; apigee-support-audit/1.0; ...)`, which is exactly the shape
Google's bot detection looks for. 154 of 168 valid citations came back as interstitials.
Compounding it, the interstitial detector matched the bare word `captcha`, which appears in
Google's own feature-flag blobs on ordinary article pages.

**Correction.** curl's default User-Agent is used. Interstitial detection keys on prose
that cannot occur in an article body.

**Regression test.** Fixtures `normal-page-mentions-captcha-word` and `real-interstitial`.

**Status: FIXED.** Recorded because it is the clearest example in this audit of a checker
looking for evidence with a marker that does not discriminate.

---

## D-011 MEDIUM — curl's `000` was treated as an uninterpretable HTTP status

**Affected** `tests/check_urls.py` (introduced and caught within this audit)

**What failed.** curl writes `000` when it never received a response. The parser accepted
it as an integer status, so a DNS failure or refused connection fell through to
`UNVERIFIED` instead of `TRANSIENT_FAILURE`, and was not retried. One GitHub issue was
reported unconfirmed on a URL that returns 200.

**Correction.** Normalised to `None` in the fetcher and defended again in `classify`.

**Regression test.** Fixture `curl-zero-no-response`.

**Status: FIXED.**

---

## D-012 MEDIUM — 112 of 172 citations permanently redirect to a new host

**Affected** all cited documentation URLs

**What failed.** Every `cloud.google.com` URL now issues a permanent redirect to
`docs.cloud.google.com`. The citations resolve, so the previous checker reported none as
broken, but 65% of the corpus cites a hostname Google has retired. Separately,
`https://apigee.com/about/support/portal/` redirects to the product home page rather than to
a support portal, which is a citation that no longer points at what it claims.

The rewritten checker is what made this visible: it records the chain rather than following
it silently, and reports `REDIRECTED_AND_VERIFIED` separately from `VERIFIED`.

**Correction.** Recorded rather than rewritten. Bulk-editing 112 inline URLs risks breaking
scenario text that quotes a URL inside prose or code, and the support-portal citation is a
genuine dead reference that should be replaced deliberately rather than by substitution.

**Status: OPEN, accepted with reason.** Nothing shipped is technically wrong because of this.
Tracked so a 65%-redirected citation set is not mistaken for a clean one.

---

## Open items accepted with reason (D-013 and later)

| ID | Item | Why accepted |
| --- | --- | --- |
| D-013 | The fault-code index truncates cause text at 110 characters | It is an index, and the file says so. The full text is on the source page, cited per row. |
| D-014 | `decode-jws-policy` documents 20 error names in one table cell | Faithful to the source. The names are now split into individual rows and flagged as listed together upstream. |
| D-016 | Ground-truth correctness cannot be checked by script | By design. It needs review by someone who knows Apigee, which is what `evaluation/audit-*.md` records. |
| D-017 | No model evaluation of the scenarios has been run | No model-execution budget in this environment. Structural validation and technical review are reported separately and are never presented as model evaluation. |
| D-024 | 112 of 172 citations permanently redirect `cloud.google.com` to `docs.cloud.google.com` | Resolving is verified and the chain is recorded. Rewriting 112 inline URLs risks breaking scenario text that quotes them, and it is not a correctness defect while the redirects hold. |
| D-025 | `docs.apigee.com` Edge slugs carry the release, so a page verified at one release 404s at another | Real and unavoidable. Recorded in `notes-known-404.txt`; the OPDK skills pin a release. |
| D-026 | The known-issues register contains no OPDK entries | By design: it scopes itself to "Apigee and Apigee hybrid". Recorded in `evaluation/source-notes-opdk-knownissues.md` rather than worked around. |
| D-027 | Two current official pages contradict each other on load-balanced target rotation | Unresolvable from the sources. Both statements are recorded verbatim in `evaluation/source-conflicts-loadbalancing.md`; neither is chosen. |

---

## Audit of medium.md, MED-01 through MED-22

Added by `evaluation/audit-medium-A.md`, which closes release-gate criterion D3. Twelve of
the 22 scenarios carried a defect. Recorded here as one entry each, because the pattern
matters more than the individual instances.

### D-028 HIGH — Scenario ground truth asserted mechanisms that cannot produce the stated fault

- **Affected** `scenarios/medium.md` — MED-02, MED-07, MED-10, MED-14, MED-18

**What failed.** Five scenarios stated a mechanism that is impossible or inverted, and in
each case the scenario's own ground truth contradicted it.

| Scenario | The assertion | What the source says |
| --- | --- | --- |
| MED-02 | The 404 is "the environment group issue from MED-01" | `environmentgroups-working-with.txt:95` — an environment in no group has no hostname at all. MED-02's own evidence has that hostname serving traffic. |
| MED-07 | `setSyncAuthorization` "was never configured for this environment" | `hybrid_v1.17_synchronizer-access.txt:94,111` — the call is `organizations/{org}:setSyncAuthorization`, org-scoped. It cannot be absent for one environment and present for its siblings. |
| MED-10 | A trace shows `VerifyAccessToken` succeeded on an expired token | `oauthv2-policy.txt:1330` — an expired token makes that step fail 401, so the request never reaches the later policy. |
| MED-14 | Remediation is upstream IdP revocation; the lever is never mentioned | `oauthv2-policy.txt:442` — `<CacheExpiryInSeconds>` exists and is documented for exactly this case: "if you sometimes revoke tokens, and you want to reduce the time window". |
| MED-18 | One gating check coming back negative does not rule the issue out | `apigee-known-issues.txt:265` — WIF **and** a forward proxy, together. A missing condition excludes it. |

MED-14 and MED-18 are the worst shape, because in both the rubric's top anchor rewarded the
wrong action. A correct answer scored at or near the zero anchor, and MED-18's wrong rule had
been inherited into `references/hybrid.md:96`, which the skill loads.

**Why it matters.** A scenario whose ground truth describes an impossible mechanism does not
just misinform; it actively penalises the answer the documentation supports. That is worse
than a gap, because a gap can be noticed.

**Fix.** All five rewritten so the ground truth names only what the cited source supports.
MED-07's premise moved from "a new environment" to "a second organization", which is the
scope the API actually has. MED-18's inverted conjunction was corrected in
`references/hybrid.md` as well, since the scenario inherited it. MED-14 now names
`<CacheExpiryInSeconds>` with its documented 1–180 range.

**Status: FIXED**, covered by `evaluation/audit-medium-A.md`.

### D-029 HIGH — The fault-code generator silently dropped every error on two policy pages

- **Affected** `research/build_error_index.py` → `.agents/skills/apigee-support-core/references/error-codes.md`

**What failed.** The page parser matched its section marker with `^## Error reference$`.
Two policy pages publish that heading as `## <span id="errorcodes"></span>Error reference`,
so the match failed and the function returned `None`, discarding the page whole:

- `api-platform_reference_policies_oauthv2-policy.txt` — 18 runtime codes
- `api-platform_reference_policies_verify-iam-policy.txt` — its runtime and deployment tables

The index went from 173 to 195 runtime codes, 107 to 116 deployment errors, and 28 to 33
fault variables once the match tolerated leading inline markup.

**Why it matters.** `medium.md` tells agents the index is authoritative and that codes not
in it should not be used. `steps.oauth.v2.InvalidRequest` is documented on the OAuthV2 page
and was absent from the index, so MED-16 broke the suite's own rule while being correct.
The project had already recorded the principle: a generated reference that is quietly
incomplete is worse than none, because it is trusted. Nothing reported the loss, because
the page-level failure is indistinguishable from a page that has no error section.

**Fix.** The heading match now tolerates leading inline markup.

**Status: FIXED and covered.** `tests/fault_probe.py` probe
`error-index-generator-drops-anchored-error-sections` reverts the regex and confirms the
checker catches the resulting stale index.

### D-030 MEDIUM — Quoted facts carried outside the scope their source gives them

- **Affected** `scenarios/medium.md` — MED-16, MED-20, MED-22, MED-12

**What failed.** Four scenarios moved a correct quotation out of the boundary its source
sets. MED-20 imported known issue 246774745 into a hybrid scenario, and made it
load-bearing in both remediation and verification, though the register scopes it to Apigee
and not hybrid at all. MED-22 required verifying Cassandra backup and restore "because
[it] cannot work with mixed hybrid versions", while stating twice that both clusters run
the same version with no upgrade in progress. MED-12's metadata claimed a callout timeout
and a target timeout "both present as a 500", where the target timeout is 504 in
`endpoint-properties-reference.txt:85,276` and in the 504 playbook. MED-16's fault code is
real but was outside the index, which D-029 explains.

**Why it matters.** Quote-matching review cannot catch this class. Each sentence is
verbatim and each is false, because a true statement about one scope was placed in another.

**Fix.** Each boundary is now stated where the fact is used, so an agent applying it has to
notice the scope. MED-20 keeps 246774745 as an explicit near miss, with the register's own
Affects column as the thing that rules it out, because excluding it is the diagnostic work.

**Status: FIXED.**

### D-031 LOW — Prose corruption inside a graded answer-key block

- **Affected** `scenarios/medium.md` MED-06

**What failed.** The "Common incorrect answers" block read "The absence of a deploy is not
evidence of applause; it is the absence of one class of cause." The word appears nowhere
else in the corpus. The sentence's argument is sound and its wording is not.

**Fix.** Rewritten. Recorded separately because it is the only defect found that no source
check could catch: it contradicts nothing, it is simply not English that anyone wrote.

**Status: FIXED.**

### Note on titles, recorded so the next pass does not re-raise it

Two reviewers reported title leakage as a defect. `tests/make_packets.py` writes
`# Support case <ID>` into the prompt and omits the scenario title deliberately, so a title
phrased as a conclusion cannot reach the agent. Titles survive only in the answer key, for
the grader. The probes `title-leak-reintroduced` and the comment at `make_packets.py:206`
cover this; `audit-hard-reg.md` and `audit-medium-B.md` predate the change and their
title-leak findings are superseded rather than outstanding.

### D-032 MEDIUM — An invented trace-step name was presented as an Apigee product term

- **Affected** `scenarios/hard.md` HARD-04 and HARD-13; `scenarios/adversarial.md` ADV-07

Corrected 2026-10-13: this entry recorded ADV-05, which was wrong. `AM-Enrich` appeared at
`scenarios/adversarial.md:529` in the pre-fix tree, inside the block that opens at
`509: ### ADV-07. Symptom points at the wrong component` (ADV-05 runs 351-435 and never
contained it). `git show b780d8f:scenarios/adversarial.md` confirms the line, and
`512311d` changed it. The scenario ID was the only error; the defect, the diagnosis and the
fix are as recorded below.

**What failed.** `AM-VerifyToken` appeared in HARD-04's diagnostic evidence and
verification steps and in HARD-13's diagnostic evidence, described as the VerifyJWT step in
an API Monitoring trace. It is not an Apigee trace step name. Zero hits across all 345 files
of `research/pages/` and `research/issues/`.

The prefix makes it worse than a merely fictional name. Every `AM-` token in the
documentation belongs to an AssignMessage policy: `assign-message-policy.txt:332`,
`fault-handling.txt:714`, `verify-api-key-policy.txt:572`, and the fault-rule examples in
`javascript-policy.txt:459`, `oauthv2-policy.txt:1460`, `populate-cache-policy.txt:402` and
others. A real customer bundle in `research/issues/devrel-267.txt:180-189` follows the same
per-type convention, giving JavaScript policies a `JS-` prefix. Attaching `AM-` to a
VerifyJWT policy asserts a meaning the prefix does not carry.

`hard.md` was also the only scenario file with no note that trace step names are whatever
the team named each policy. `easy.md:994-995` and `medium.md:697` both carry one, and
`evaluation/fix-medium.md:142-144` records the decision to generalise this exact pattern
rather than invent a name.

**Fix.** `AM-VerifyToken` to `JWT`, a real policy name from
`api-platform_reference_policies_verify-jwt-policy.txt:315`, chosen because it does not pin
the algorithm the way `JWT-Verify-RS256` would at HARD-04. The customer-defined-step note
added, matching `easy.md:994-995`. `AM-Enrich` in `adversarial.md` had the same defect on a
JavaScript policy and is now `JS-Enrich`.

**Status: FIXED.**

### D-036 HIGH — The packet generator silently dropped a "not a critical failure" ruling

- **Affected** `tests/make_packets.py`, `evaluation/packets/MED-09.key.md`,
  `evaluation/packets/MED-11.key.md`

Found 2026-10-13 by the same blinded review as D-035, and the more mechanical of the two.

**What failed.** Two separate losses, both invisible in every existing check.

1. MED-09 carries two `#### Not a critical failure:` rulings. `section()` returns the first
   matching heading, so the second never reached the key. The second is the one `b19d34a`
   added to stop the grader failing a documented-correct caveat, so the generator was
   reinstating exactly the defect that commit fixed, and the key still looked complete.
2. A `#### Not a critical failure: <subject>` heading carries its subject in the heading line.
   The generator stripped the heading to `## Not A Critical Failure` and kept only the body, so
   MED-11's key opened with "finding, not a wrong answer. It becomes wrong only when ..." with
   no antecedent. A grader cannot apply a ruling that does not name what it exempts.

**Why it matters.** These are load-bearing. A critical failure fails the scenario whatever the
score, so the ruling that exempts an answer from one is the difference between a documented-
correct answer passing and failing. Neither loss was covered: the existing critical-failure
completeness check only reads the bold `**Critical failures:**` form, and nothing looked at the
`Not a critical failure` headings at all.

**Fix.** `make_packets.py` gained `sections()`, which returns every match with the heading's
own subject carried in, and `KEY_EXTRA` now goes through it. `check_repo.py` gained
`check_not_a_critical_failure_completeness`, which reads the source block and requires each
ruling's opening to appear in the key.

**Status: FIXED and covered.** Two probes: `answer-key-not-a-critical-failure-loses-subject`
and `answer-key-second-ruling-dropped`. The second probe initially reported a **false pass**
against the first version of the new check, which validated only the first ruling and would
have left the dropped-ruling case undetected. The check was corrected to inspect every ruling
and both probes now fire. That false pass is recorded here because a check written to catch a
class of silent loss, which itself silently lost one of them, is the part worth keeping.

### D-035 HIGH — A critical failure rested on a claim the corpus does not support

- **Affected** `scenarios/easy.md` EASY-15

Found 2026-10-13 by a blinded review of the 12 scenarios whose model-visible prompts are
byte-identical between `b780d8f` and `bc44b04`. Recorded because it is the one case in that
review where the current key was worse than the historical one.

**What failed.** The remediation added a critical failure for "proposing a shared flow as an
aggregate limit while presenting it as one", and justified it by asserting that "a shared flow
executes once per proxy that invokes it, each with its own counter". Nothing in the 305-page
corpus supports that. `quota-policy.txt` never mentions shared flows; `shared-flows.txt`
describes deployment and reuse and does not state how a policy inside a shared flow is
instantiated per calling proxy. The key cites the Quota page and the Quota/SpikeArrest
comparison page, and neither is the source of the instantiation claim.

The documented part is real and still there: `quota-policy.txt:14` says quotas apply to
individual API proxies and are not distributed among them, and `:138` scopes counters to the
API proxy containing the policy. What the sources do not settle is what a Quota policy in a
parent shared flow does to that scope.

**Why it matters.** A critical failure fails the scenario whatever the score. This one failed
every answer that proposed a shared flow, on the strength of a mechanism the documentation in
reach does not state, and the review could not find a page that would settle it. It is the
same shape as D-028: a scenario penalising the answer the documentation supports, except that
here the penalty was added rather than removed, and by the same class of reasoning.

**Fix.** The critical failure is gone. The key now states the documented scope rule, says
plainly that the shared-flow case is unsettled by the documentation in reach, and grades only
the documented part. Proposing a parent shared flow while flagging the gap is explicitly **not**
a critical failure. Presenting it as a documented guarantee still scores 0 on technical
correctness, so the work the scenario sets is unchanged; what is removed is the unfounded
penalty.

The remediation, ground truth and prompts were not otherwise touched, and the turn-1 and turn-2
prompts are byte-identical to the pre-fix packets, so the task's difficulty is unchanged.

**Status: FIXED.** No dedicated probe; the defect is in prose and the corpus search that
demonstrates it is the evidence.

### D-037 MEDIUM — MED-18's remediation contradicted the scenario's own evidence

- **Affected** `scenarios/medium.md` MED-18

Found 2026-10-13 by the same blinded review as D-035 and D-036, and recorded because it is
the second case of a current key being worse than the historical one it replaced.

**What failed.** The remediation `c68e207` added reads, in the hotfix paragraph: "The same
property, read as `false` on this cluster, is what excludes the MART defect". The scenario's
turn-2 diagnostic evidence says the opposite: MART is on `1.16.0` **and** "the installation
has both Workload Identity Federation enabled and an HTTP forward proxy configured". WIF is
therefore present, the property would read `true`, and the sentence asserts an exclusion the
evidence contradicts.

Checked directly, the key's "Ground-Truth Resolution" states both conditions are required and
that either being absent is enough to exclude the issue, while the remediation paragraph says
this cluster is excluded. A grader cannot score an answer consistently against both.

**Fix.** The paragraph now says what the evidence supports: MART being affected means WIF and
the forward proxy are both present here, so the guardrails ServiceAccount absence is a real
thing to check for on this installation rather than something already ruled out, and
`gcp.federatedWorkloadIdentity.enabled` is worth reading directly because the two defects gate
on overlapping but different facts.

**Status: FIXED.** No dedicated probe. MED-18's changed sections are held back rather than
prompt-visible, and the corpus read is the evidence.

### D-033 HIGH — The recorded baseline commit was downstream of the remediation it was meant to precede

- **Affected** the proposed paired A/B evaluation; no file defect

**What failed.** The handoff named `e63d130` as the pre-remediation state. `e63d130` is the
child of `80e8009`, which is itself a remediation commit that edits
`references/error-codes.md` and `references/hybrid.md`. The "35 commits since `e63d130`"
count therefore absorbed `80e8009` into the baseline arm.

Had this gone unnoticed, both arms would have carried the first remediation commit and the
comparison would have returned a guaranteed null. A null that looks like a measurement and
is an artefact of the baseline choice is the worst available outcome, because it is
indistinguishable from a real finding at reading time.

**Correct baseline** is `3e78f5f5126627d499c53c3b2bfc5f7747bacf78`, the parent of `80e8009`.
The remediation span is 37 commits, not 35.

**Why it matters beyond this experiment.** Any comparison that reconstructs its baseline
from a stated commit hash without checking the ancestry will make the same mistake. The check
is `git rev-parse <claimed-baseline>^` and reading that commit's subject.

**Status: FIXED.** Recorded in `evaluation/ab-protocol-and-power.md`.

### D-034 HIGH — Evaluation isolation was an instruction, and the packet check did not test it

- **Affected** `tests/test_leakage.py`, `evaluation/test-protocol.md`

**What failed.** Run 2's own deviation log states that its working directory was the
repository root, that `evaluation/packets/<ID>.key.md` was reachable from it, and that
isolation was "an instruction rather than a mechanism". The protocol said "never shown to
the agent", which described the generator rather than the filesystem.

`tests/test_leakage.py` verified that prompt *files* contain no held-back text. It could not
and did not verify that an evaluating process could not *reach* an answer key. Three paths
existed: the keys sit under the same root as the skill; `make_packets.py` writes the
scenario ID into every prompt as `# Support case <ID>`; and `scenarios/index.md` maps that
ID to a title, restoring the one thing the generator deliberately drops.

**Fix.** `tests/make_eval_workspace.py` builds a tree containing the skill and the prompts
and writes an `opencode.jsonc` whose `external_directory: deny` rule blocks every read
outside it. The rule is enforced by the harness before a tool call executes and is not
overridable by `--auto`. `tests/test_isolation.py` attempts eight breach routes against a
live model with canaries planted outside the boundary, and reports INCOMPLETE rather than
PASS when no model was asked to breach anything.

**Status: FIXED**, with the live-test results recorded in `evaluation/isolation-report.md`.

---

## Audit of the evaluation harness, 2026-10-14

Found by checking the harness out fresh and running it, rather than by reading it. The three
entries below were all invisible from inside the working tree the earlier passes used,
because the working tree's own file timestamps happened to be in the order the checkers
wanted.

### D-038 HIGH — Packet freshness was decided by file timestamps, which a commit does not record

- **Affected** `tests/check_repo.py` (`check_packets`), `tests/make_packets.py`
- **Remediation** `b2e06db`

**What failed.** `check_repo.py` decided an answer key was stale by asking whether the
packet's mtime was older than the mtime of the scenario file containing that scenario id. An
mtime is not part of a commit. `git clone` and `git worktree add` write every file at checkout
time, in whatever order the index hands them over, and on a pristine checkout every one of the
103 scenarios came out with an mtime slightly newer than its packets. The reported result was:

```text
FAIL (1)
  - 103 packet(s) are older than their scenario and hold a stale answer key: ADV-01, ADV-02, ...
RESULT: FAIL
```

**Why it matters well beyond the noise.** `tests/fault_probe.py` has a control probe,
`valid-repo-baseline`, whose entire job is to confirm that the unmodified repository passes.
It failed. Every other probe runs its mutation inside a copy of that same repository, so with
the baseline already failing, all 33 probes that expect a FAIL saw a nonzero exit whether or
not their mutation had been detected. The suite that exists to catch a checker passing a
broken repository was reporting nothing in a fresh clone. `release_gate.py` reads the probe
result and inherits it, and lost four criteria: A1, F1, F2 and F3.

It is worth being precise about what this is not. It is not a false PASS. The gate returned
NOT QUALIFIED throughout, and the four criteria failed loudly. The harm is the opposite one:
a project whose checkers are sound looks broken, and a suite whose passing means nothing looks
green.

**Cause.** Verified, not inferred. mtime is a property of the working tree, not of the commit
history, and nothing in `git` reconstructs the order in which two files were last written.

**Reproduction.** On any fresh clone, with no edits at all:

```bash
git clone <this repo> fresh && cd fresh
python3 tests/check_repo.py --strict | tail -3   # RESULT: FAIL, 103 stale packets
python3 tests/fault_probe.py | tail -3            # FALSE PASS: valid-repo-baseline
```

That the cause is timestamps and not real staleness is shown by changing nothing else. In one
copy of the repository, setting every packet's mtime to a shared instant without touching a
single byte of content, `check_repo.py --strict` went from FAIL to PASS and
`release_gate.py --skip-urls` went from `BLOCKED 1, FAIL 4, PASS 24, UNVERIFIED 3` to
`BLOCKED 1, PASS 28, UNVERIFIED 3`.

The check was also wrong in the other direction, which the earlier passes had not noticed
because they did not look. The old predicate missed a genuinely stale key whenever the packet
was newer than its scenario, which is the normal state after regenerating and committing. With
EASY-01's ground truth rewritten and every packet touched ten thousand seconds ahead, the old
predicate reported 0 stale.

**Fix.** `make_packets.py` gained `packet_texts()`, which renders every packet to text without
writing anything, and `main()` writes what it is handed. `check_repo.py` gained
`check_packets_current()`, which renders and diffs, the way `check_generated_freshness`
already did for the fault-code index and the scenario index. The comparison is now strictly
stronger: it catches the stale key the old check missed, and no longer fires on a correct tree.

**Regression test.** Probe `packets-touched-after-checkout`, which sets every packet's mtime
to the epoch and every scenario's to a later instant with no content changed, and expects a
PASS. Probe `stale-packet-answer-key` was rewritten: it previously aged the packets in order
to force the timestamp comparison, so it only ever tested timestamps, and it now rewrites a
ground truth and leaves the packets newer.

**Test results.** `check_repo.py --strict` PASS, `fault_probe.py` 35 of 35 with 0 false passes,
`test_leakage.py` PASS, `test_generation_workspace.py` 8 of 8,
`test_generation_outcomes.py` 15 of 15, `test_isolation_classify.py` 23 of 23,
`test_release_gate.py` 32 of 32. All 309 committed packets are byte-identical under the new
render, verified by regenerating into a copy and diffing, so the change alters no output.

**Status: FIXED and covered.** The gate verdict is unchanged at NOT QUALIFIED. C4 stays BLOCKED
because `--skip-urls` was used, and E5, G1 and G2 stay UNVERIFIED because no run meets the A/B
design. Recovering four criteria did not qualify the project and was not used to suggest it had.

### D-039 MEDIUM — Two fault probes matched nothing and had never tested anything

- **Affected** `tests/fault_probe.py` probes `origin-field-removed` and
  `origin-unclassifiable-value`
- **Remediation** `eed6808`

**What failed.** Both probes anchored their regex with `^` and passed no `re.MULTILINE` flag,
so the pattern matched only at the start of the file. The field they meant to change is a
bullet on line 26 of `scenarios/easy.md`:

```python
>>> len(re.findall(r"^- Origin: [^\n]+", text, re.M))   # 15
>>> len(re.findall(r"^- Origin: [^\n]+", text))          #  0
```

`re.sub` found nothing, `write_text` wrote the file back byte-identical, and the probe ran the
checker against an unmodified repository. The checker then reported
"origin classification is unambiguous across 103 scenarios" and the probe, which expected a
FAIL, was scored as having caught the defect it never introduced.

**Why it matters.** `check_origin_integrity` is the check D-018 exists to enforce, that
counting constructed suites as incident reports did not inflate the library's apparent
provenance by twenty-one scenarios. Its two most direct probes had no evidence behind them.
The checker turns out to be correct, and applying the mutations by hand names the defect
correctly ("origin classification: EASY-01: no Origin field"), so nothing shipped is wrong.
What was wrong is the project's confidence in its own coverage of that checker.

**Cause.** Verified. The missing flag, and nothing else: the same file's other `^`-anchored
`re.sub` already passed `flags=re.M`, and those two were the only ones that did not.

**Reproduction.** Drop `flags=re.M` from either probe and run the suite. Both are reported as
false passes.

**Fix.** Both probes pass `flags=re.M`. Every `^`-anchored `re.sub` in the file was checked
for the same mistake; these were the only two.

**Status: FIXED and covered**, but the coverage claim here is weaker than the other two
entries and is why D-039 was closed with a second commit. Fixing the probes leaves the suite
unable to notice a probe that stops working, which is the defect itself. `95a84aa` adds the
missing guard: each probe digests the sandbox before and after its own mutation, and a probe
expecting a FAIL that changed no file is reported as NO MUTATION and fails the suite whatever
the checker said. Content is digested rather than timestamps because a no-op `write_text`
moves an mtime while leaving the bytes alone, which is exactly the case being caught. With
the missing flag reintroduced, the suite now names both probes twice, once as a false pass and
once as no mutation.

**Remaining uncertainty.** The guard proves each probe changed a file. It does not prove the
change was the intended one. A probe that corrupted some other file would satisfy it. Nothing
short of reading each probe settles that, and the suite has 35 of them.

### D-040 HIGH — A nonzero exit from the provider was recorded as a completed answer

- **Affected** `evaluation/results/run-3/run_generation.py` (`one_turn`)
- **Remediation** `90a0901`

**What failed.** The harness's failure predicate read `rc == -1`. That value is the harness's
own sentinel for a `subprocess.TimeoutExpired`, not a real exit status, so every other nonzero
exit passed the test and fell through to the OK branch. `6600a19` fixed the sibling defect
where an error event's message was appended to the answer text, and recorded this path
deliberately untouched.

A provider that dies partway through still leaves the text it managed to emit in the event
stream, so a stream that is not empty is not evidence that the turn finished. Driven through
the real `one_turn` and the real workspace builder with a provider exiting 1 and
"provider stream aborted" on stderr, the harness recorded `TURN1_COMPLETE`, booked the request
`OK`, and wrote this to `raw/<sid>.turn1.md`:

```text
The Quota policy rejects the revision at upload, because the interval
```

**Why it matters.** `grade_run.py` selects every scenario the manifest marks
`AWAITING_GRADE`, and a grader reads `raw/<sid>.turn<N>.md`. A truncated sentence presented as
a finished answer is scored against the rubric exactly like a whole one, and a critical-failure
condition that a complete answer would have tripped can be missed on a partial one. This is the
same false-success shape `6600a19` was written to close, reached by a different route.

**Cause.** Verified. The predicate enumerated one sentinel value rather than testing for
success.

**Reproduction.** Through the project's own harness plumbing, replacing only the provider call:

```python
h.script(Step(turn_stream(TRUNCATED), rc=1, err="provider stream aborted"))
h.mod.one_turn(m, ALPHA, 1, "fake/model", 30)   # TURN1_COMPLETE before the fix
```

**Fix.** The predicate reads `rc != 0`, which subsumes the timeout sentinel and every other
failure exit. The quota branch still runs first, so a 429 is still classified as a quota error
and is still not retried, rather than burning the one retry against a provider that has already
refused; a case pins that ordering, because the fix would otherwise have turned a 429 into a
generic failure and retried it. The recorded reason now names the exit code when the exit code
is the only thing that went wrong. Previously a turn that returned text, exited 2 and wrote
nothing to stderr was recorded as "empty response", which is the opposite of what happened.

**Regression test.** Three cases in `tests/test_generation_outcomes.py`. Two fail against the
previous harness: a nonzero exit carrying text is not an answer, and a nonzero exit is reported
as a nonzero exit rather than as an empty response. The third, a 429 exit still being a quota
error, passed before the fix and guards the ordering the fix could have broken.

**Test results.** `test_generation_outcomes.py` 15 of 15. `test_generation_workspace.py` 8 of
8, `test_release_gate.py` 32 of 32, `test_isolation_classify.py` 23 of 23 and `check_repo.py
--strict` PASS, so widening the predicate changed nothing else in the harness.

**Status: FIXED and covered.**

**Remaining uncertainty.** Run 3 never reached a turn. All 103 scenarios in its manifest are
NOT_STARTED, so nothing in `evaluation/results/run-3/` was produced by the harness this commit
changed, and no recorded score is affected either way. The second path `6600a19` left open is
untouched: a policy carrying `continueOnError="true"` that swallows a failure contributes no
fault to the manifest while its text still reaches the answer file. It is a defect in the fault
inventory rather than in the outcome classification, it is not what produced the run-3
artifact, and it is not fixed here.

**What these three entries are not.** All three are deterministic orchestration findings. A
passing probe suite is evidence that the harness classifies the inputs it was given as
described. It is not evidence that a live model or a live provider cannot produce a stream
shape these suites do not model, and none of it bears on whether the skills help. The gate
still reads NOT QUALIFIED, and the three criteria that would change that, E5, G1 and G2, are
unverified for the same reason they were before this pass.

### D-041 HIGH — `grade_run.py` scored scenarios the manifest said were never run

- **Affected** `evaluation/results/run-3/grade_run.py`
- **Remediation** `19419c4`
- **Regression test** `tests/test_grading_integrity.py`

**What failed.** `--run` took the grader's JSON at face value. It read the answer key, scored
the supplied anchors and wrote the result. It never opened `manifest.json`. Only `--list`
filtered on `AWAITING_GRADE`, and `--list` is the command that costs nothing and writes
nothing.

Driven against run 3's own state, where all 103 scenarios are `NOT_STARTED` and no answer
file exists, a scores file naming MED-13 produced:

```json
{"scenario": "MED-13", "normalized_score": 1.0, "verdict": "PASS"}
```

Nothing had been generated. The number was arithmetic on the caller's own input, and the only
thing that made it look like a result was that it was written into the same directory as real
grades, where `_summary.json` reported `mean_normalized_score: 1.0` and `critical_failure_free: 1`.

**Why it matters.** This is the other end of the sentence in `6600a19`, which stopped the
generation harness from writing a provider error into an answer file on the grounds that a
false success "produces a score for a turn the model never answered". The generation path was
hardened; the component that writes the score was not. The outcome that commit set out to
prevent stayed reachable from the grading side, with no generation at all, and it would have
been reachable by a stale or mis-transcribed scores file rather than by a provider fault.

PROTOCOL.md is explicit and was not followed: "manifest.json is authoritative for collection
state."

**Cause.** Verified. The loop iterates `supplied.items()` and never references the manifest,
the run's status fields, or the answer files.

**Reproduction.** Drive the real file against a manifest in which a scenario is `NOT_STARTED`:

```bash
echo '{"MED-13": {"anchors": {"a": 4}, "critical": false}}' > /tmp/s.json
python3 evaluation/results/run-3/grade_run.py --run --scores /tmp/s.json
cat evaluation/results/run-3/grades/primary/MED-13.json   # PASS, 1.0, before the fix
```

The under-count guard does not help here. It fires when the grader supplies fewer anchors than
the table has rows, so a careless score is caught and a well-formed score for the wrong
scenario is not.

**Fix.** `why_ungradeable()` gates every scenario. A scenario may be graded only when the
manifest marks it `AWAITING_GRADE` and both turn answer files exist. A refusal names the
scenario and the reason, writes no grade file, appears in the summary under `refused`, and
makes the process exit nonzero so the rest of the summary cannot be read as complete. Other
scenarios in the same scores file are still graded, because a stale entry should not cost the
run everything.

**Regression test.** `tests/test_grading_integrity.py`, eight cases driving the real file in a
subprocess against a scratch manifest and the real answer keys. Six fail against the previous
grader. The two that pass are the ordinary path and the critical-failure override, which are
there to show the new gate does not reject a scenario that genuinely ran.

**Status: FIXED and covered.**

### D-042 MEDIUM — A grading input error was recorded as a model failure

- **Affected** `evaluation/results/run-3/grade_run.py`
- **Remediation** `19419c4`
- **Regression test** `tests/test_grading_integrity.py`

**What failed.** Three lines coerced a score that could not be computed into a FAIL, whenever
the grader had supplied any anchors at all:

```text
verdict FAIL, normalized_score None, unscorable_reason None
```

Reproduced with one anchor of `7` where the rubric scale is 0 to 4. The file's own docstring
says it "refuses to guess a verdict it cannot derive", and PROTOCOL.md says "An invalid
grading reference is never counted as a model failure." Both were contradicted by the same
three lines.

**Why it matters.** The count that matters most in this project is the count of model
failures. A grader typo, a stale anchor carried from an earlier key, or a rubric row that
disappeared between two turns all land in `by_verdict["FAIL"]`, indistinguishable from a
model answering wrongly. Nothing recorded that it was an input error, so the grade file could
not be re-examined later, which is the one thing `test-protocol.md` insists a result must
allow.

**Cause.** Verified. `normalized()` returns `None` for an out-of-range anchor, an empty anchor
set, or a key with no rubric table, and the caller treated all three as a model failure.

**Fix.** The verdict stays `UNSCORABLE` and `unscorable_reason` is computed rather than left
null, naming the offending input: the out-of-range anchors and their values, the empty anchor
set, or the missing rubric table. A grader who declares a scenario unscorable themselves is
still taken at their word.

**Regression test.** The case
"an anchor outside the 0-to-4 scale is unscorable, not a model failure", which asserts the
verdict, the null score, a non-empty reason naming the value 7, and `by_verdict["FAIL"] == 0`.

**Status: FIXED and covered.**

**Note on the relationship between these two.** D-041 and D-042 are three lines apart in the
same function and were found together, but they are separate defects with separate causes and
separate tests, and only D-041 required a new gate. A grader's own data being wrong and a
scenario never having run are different problems, and a fix for either one does not address
the other.

---

## Open findings from the 2026-10-14 review pass, recorded not fixed

A second and third review pass ran over the checkers and over the run-3 freeze and
resumption machinery. The two defects already fixed from that work are D-043 and D-044
below. Everything after them is recorded here as OPEN, with the evidence each rests
on, and none of it is fixed on this branch.

Two labels are used throughout and they mean different things.

- **Reproduced here** means the reviewer or I ran the demonstration and saw the output on
  this branch. The command is given so a reader can repeat it.
- **From the review pass** means the evidence is the reviewer's captured output, relayed
  here rather than independently re-run by me. The reasoning is checkable against the code
  and the cited line numbers; the run is not one I performed.

Seven of the entries below have been fixed since they were written, and each says so at
its own heading rather than being moved: D-043, D-044, D-046, D-047, D-049, D-050 and
D-051. D-046, D-047 and D-051 were found in the review pass and fixed on this branch after
the evidence was reproduced here, so they carry the stronger label. D-043 and D-044 were
reproduced here before being fixed, as were D-049 and D-050. The rest are open: D-045,
D-048 and D-052, plus D-053 which is recorded and accepted rather than open or fixed.
D-051 is fixed but carries a human step that is deliberately not done, which its entry
spells out.

Nothing in this section is a claim about model quality or about whether the skills help. All
of it is about machinery. Run 3 collected nothing, so no recorded score depends on any of it.

### D-043 HIGH — The fault-code check was switched off by the ordinary word "Rejected"

- **Affected** `tests/check_repo.py::check_scenario_codes`
- **Remediation** `4bc016d`
- **Regression test** probe `scenario-invents-fault-code-in-a-scenario-naming-rejected`
- **Evidence** reproduced here

**What failed.** The guard that skips scenarios carrying the "cases deliberately not converted"
appendix was `if "NOT converted into scenarios" in block or "Rejected" in block`. That is a
bare substring search over the whole scenario, so any scenario whose prose contains the word
was exempt from the fault-code check entirely. HARD-22 uses "Rejected" as a label in a list
of LDAP symptoms, so it was exempt, and MED-39 was exempt for the intended reason.

**Why it matters.** This is the check the project was built around. `ac23304` exists to check
every fault code cited in a scenario against the source corpus, and D-001 is the defect it
was written for. One scenario out of 103 had that check silently disabled.

**Reproduction.**

```bash
# inject a code that exists in no source page into HARD-22's ground truth,
# then inject the identical code into HARD-21, which lacks the word
python3 tests/check_repo.py --strict --root .
```

Before the fix, HARD-22 was reported clean and HARD-21 was caught. After, both are caught.

**Fix.** The exemption matches a heading containing "not converted into scenarios" rather
than a word anywhere in the block, and the number of exempt scenarios is reported in the
check's own pass line so a future one has to be explained.

**Test results.** 37 probes, 37 behaved as expected, 0 false passes. The new probe reports a
false pass against the previous check once packets are re-synced, which they have to be: see
D-046.

**Status: FIXED and covered.**

### D-044 HIGH — A5 passed on a git error string, claiming a tag it could not see

- **Affected** `tests/release_gate.py`
- **Remediation** `829a199`
- **Evidence** reproduced here

**What failed.** A5 asserts the baseline tag is present. It read the stdout of
`git tag -l baseline-v0.1` and tested whether the string was non-empty, ignoring the exit
code. `run()` answers a missing or failing binary with `(-2, "ERROR FileNotFoundError: ...")`,
and that string is not empty.

**Reproduction.** With git off `PATH`, the gate printed "git tag baseline-v0.1 present",
reported A5 as PASS, and printed a line character-for-character identical to the one it
prints when git works. Nothing in the report distinguished the two.

**Fix.** The exit code is checked. A5 is BLOCKED when git cannot answer, and the reason is
recorded.

**Status: FIXED.** No dedicated regression test; the gate's own suite covers its verdict
logic, and this path is exercised by running the gate without git.

### D-045 MEDIUM — Two probes can pass on packet staleness rather than on the check they target

- **Affected** `tests/fault_probe.py`
- **Evidence** reproduced here

**What failed.** Any probe that edits a file under `scenarios/` makes every packet stale, and
`check_packets_current` then fails the checker for a reason unrelated to the check the probe
aimed at. The probe reads green either way, so the targeted check is never exercised.

`scenario-empty-required-section` is the clearest case and is worse than that. Its declared
purpose is "keep the heading but empty its body", and it computes the scenario span into
unused locals before doing something else entirely: it replaces `#### Verification\n` with
`#### Verification\n\nPLACEHOLDER_MARKER\n`, which *inserts* a line. The body was 2317
characters before the "emptying" edit and 2337 after. It then re-syncs the packets and the
checker returns PASS, because the scenario the probe claims to have broken is intact.

The trap is self-defeating in a way worth stating plainly: the failure message tells the
operator to run `make_packets.py`, and following the project's own advice restores a green
build over the defect.

`failed_lines`, the list of failure lines that would distinguish "caught by the check I
targeted" from "caught by something else", was computed at `fault_probe.py:527` and never
used. The typing pass removed the binding, so the name is no longer in the file; the
mechanism is still unwired, which is why this entry stays open.

**Partially addressed.** `Sandbox.sync_packets()` was added and is used by the new probe in
D-043, which is why that probe is sound. The other scenario-editing probes still do not call
it, and the mechanism to report *which* check fired is still unwired.

**Status: OPEN, partially addressed.** Recorded rather than completed because fixing it means
touching the probes one at a time and proving each against its own check, and the first
attempt at that is D-043's probe, which needed two corrections before it proved anything.

### D-046 HIGH — `test_leakage.py` returns success when the isolation half cannot run

- **Affected** `tests/test_leakage.py`
- **Evidence** from the review pass

**What failed.** The workspace-isolation check returns `True, "SKIPPED (not importable)"` when
`make_eval_workspace` cannot be imported. `True` is success, so deleting the builder makes the
entire isolation half of the leakage test disappear while the script still reports
`RESULT: PASS` and exits 0. `release_gate.py` maps exit 0 to PASS for its leakage criterion.

This is the same shape as D-044 in a different file, and the same failure the gate was written
to catch.

**Fix.** The workspace check answers with one of three verdicts rather than a bool, because a
bool cannot say the third thing and every way the check could not run used to say the first.
`OK`, `LEAK` and `UNRUNNABLE` are now distinct, and an unrunnable check is reported separately
from a finding, because a leak is a result and a non-run is not. Both exit nonzero. Two further
ways the check could not run were found while changing it: a build returning 2 was being
reported as a leak, which it is not, and an empty scenario sample would build an empty
workspace, find nothing in it, and call that clean.

**Remediation** `7749c30`. **Test results.** `test_leakage.py` PASS with exit 0 on a clean
tree, `INCOMPLETE` and exit 1 with the builder deleted. **Status: FIXED.**

### D-047 MEDIUM — "Every reference path resolves" passes when no path was found

- **Affected** `tests/check_repo.py::check_reference_discovery`
- **Remediation** `f552fed`
- **Regression test** probe `reference-paths-no-longer-listed`
- **Evidence** reproduced here

**What failed.** The orphan check is guarded by `if total and not orphans`, but the
unresolvable check is guarded only by `if not unresolvable`. The list is empty both when
every listed path resolves and when the regex that collects paths matched nothing at all.

**Reproduction.** Strip the backticks from every reference path in every `SKILL.md` and delete
`.agents/skills/apigee-support-core/references/hybrid.md`. Before the fix the check still
reported "every reference path listed in a SKILL.md resolves to a file" and `check_repo
--strict` returned PASS. The deleted file is precisely what the `reference-path-unresolvable`
probe protects; the probe passed today only because the repository happens to use backticks.

The orphan check does not catch it either, which is the part worth recording. `hybrid.md`'s
name is still in the `SKILL.md` body, so nothing looks orphaned. Both checks go quiet at once
for one edit, which is why this needed a probe rather than a reading of the code.

**Fix.** The count of paths the regex actually found now gates the ok the way `total` gates
the one above it, and a repository with no reference files at all still stays silent. The ok
line gained its count, so a reader can tell a check that ran from one that did not.

**Regression test.** Probe `reference-paths-no-longer-listed` asserts both preconditions, so
it cannot go inert the way the origin probes did. It touches no scenario, so it needs no
packet re-sync. **Test results.** Reports a false pass against the previous check, passes
against this one. `check_repo.py --strict` PASS, 37 probes with 0 false passes.
**Status: FIXED and covered.**

### D-048 MEDIUM — A workspace with no prompts still reports `structural: PASS`

- **Affected** `tests/make_eval_workspace.py`, `tests/test_isolation.py`, `tests/test_leakage.py`
- **Evidence** from the review pass

**What failed.** `make_eval_workspace.build()` returns `1 if missing else 0`, but both callers
test only `rc == 2`. A missing packet therefore yields exit 1, which no caller recognises, and
`release_gate.py` decides F6 by looking for the string `structural: PASS` while ignoring the
exit code.

**Reproduction.** Delete MED-13's two prompt packets and build a workspace for it: the builder
reports `0 packets (2 missing)` and returns 1, and the isolation run still reports
`structural: PASS`. F6 therefore passes on a workspace containing no prompts at all.

Two things make this worse than a cosmetic exit-code mismatch. The coverage is 12 of 103
scenarios, chosen by the even sample `ids[:: max(1, len(ids) // 12)][:12]`, which happened
not to include a scenario with a missing
packet. And the same blindness is in `test_leakage.py:127`.

**Status: OPEN.**

### D-049 HIGH — A run cannot resume past its own quota error

- **Affected** `evaluation/results/run-3/run_generation.py`
- **Evidence** from the review pass

**What failed.** Work is selected with `status == "NOT_STARTED"` only. Every failure path
writes `BLOCKED_BY_INFRASTRUCTURE` and a completed turn 1 writes `TURN1_COMPLETE`, and neither
is ever selected again. Demonstrated: a scenario blocked by a 429 is not picked up after the
window resets, and a scenario stranded at `TURN1_COMPLETE` by a crash or a turn-2 429 never
receives its turn 2. A second invocation prints "nothing pending in this selection" and spends
nothing.

The budget window itself does reset correctly, so the machinery is half-built. The window is
resumable and the scenario is not. That contradicts `PROTOCOL.md`'s "manifest.json is
authoritative for collection state" and the recovery procedure in `evaluation/WORKING-STATE.md`,
which budgets 337 requests across roughly eight windows and expects each session to add a
batch and checkpoint.

**Why it matters now.** The free provider quota resets on a wall-clock boundary, so the state
of the world is the trigger. Running `--batch` before the reset would strand those scenarios
for the whole run, and only a hand-edit of `manifest.json` would revive them, which no
document describes.

**Remediation** `b27bbea`, with D-050 and the turn-2 half of D-052 in the same commit because
the three are interlocked in the same two functions and splitting them would leave
intermediate states that do not run.

**Fix.** `BLOCKED_BY_INFRASTRUCTURE` stays one status, and a new `block_kind` field says which
situation it was. `BLOCK_WINDOW` covers a 429, the attempt cap and an already-closed window,
all of which the protocol itself scopes to the window, so the next window re-queues them.
`BLOCK_TERMINAL` covers an unusable workspace, an exhausted retry and a turn 2 with no session
id, none of which a later window can change. The turn owed is read off `rec["turns"]` rather
than off a remembered status, so a scenario the quota blocked during turn 2 comes back for
turn 2 and does not spend a second request re-collecting turn 1. `pending_turn()` is the single
predicate, so `--list` and a resuming run cannot disagree about what will happen.

**Why it is not re-offered forever.** Structurally, not by counter. Every window block also
closes the window, `main` refuses to start a batch in a closed window, and `one_turn`
re-checks before spending. A scenario is therefore offered at most once per window, and a
window costs at most `MAX_ATTEMPTS` either way. Terminal blocks have no timer at all.

**Test results.** 8 of the 23 cases in `tests/test_generation_outcomes.py` fail against the
previous harness. **Status: FIXED and covered.**

### D-050 HIGH — A stale workspace is reused with nothing checking what is inside it

- **Affected** `evaluation/results/run-3/run_generation.py`
- **Remediation** `b27bbea`
- **Regression test** `tests/test_generation_workspace.py`
- **Evidence** reproduced here

**What failed.** `scenario_ws()` rebuilt only when the workspace's own `MANIFEST.json` was
absent, then checked that `missing_packets` was empty and that the scenario id was present. It
never compared `skill_dir_sha256` or `permission_config_sha256`, both of which the builder
writes for exactly this purpose.

**Reproduction.** Build a workspace with the real builder, empty its `opencode.jsonc`, replace a
skill file, and recompute both digests in the workspace's own manifest to match the tampered
material. The turn records `TURN1_COMPLETE` with every isolation deny stripped, no request
refused, no warning. Two forgeries were run, because each defeats a different single check:
corrupted digests defeat comparing the workspace against itself, and recomputed digests defeat
comparing it against its own recorded provenance.

**Why it matters.** The module docstring's claim that the workspace carries an enforcing
`opencode.jsonc` held only for a workspace the current builder produced, and nothing
re-established it on resume. A run whose isolation is silently absent still produces scores,
and nothing downstream would say those scores came from a tree the model could read answer
keys out of.

Compounding it, `ws_path()` hashes only the scenario ids and `WS_ROOT` defaulted under `/tmp`,
so two checkouts of this repository resolved a scenario to the same directory.

**Fix.** `verify_material()` runs on every use and fails closed, with four gates: the isolation
material is present, the recorded digests match what the workspace holds, the recorded skills
digest matches the current source tree, and `opencode.jsonc`'s permissions are compared rule by
rule against the `PERMISSIONS` imported from the builder itself. The last one needs no stored
digest to trust, so it catches an emptied config even when the digest was regenerated to match.
It blocks rather than rebuilds, because a scenario whose turn 1 was collected inside that
workspace would answer turn 2 against different material, and PROTOCOL says mixing versions
inside one result is worse than an incomplete run.

The default workspace root moves under a per-checkout suffix for the reason above.
**Operational note:** a workspace left at the old fixed path by a previous run is orphaned and
will not be reused.

**Test results.** 5 of the 15 cases in `tests/test_generation_workspace.py` fail against the
previous harness. A sixth guards against over-correction, asserting that an untampered
workspace is accepted on a resumed turn and not silently rewritten. **Status: FIXED and
covered.**

**Residual risk, accepted deliberately.** A mid-run edit to `.agents/skills/` now blocks every
scenario rather than silently collecting against mixed material. That is the direction the
protocol asks for, but it is a total failure rather than a partial one, and three separate
gates can each halt a whole run. Each names its remedy in the recorded error. The harness
deliberately does not rebuild its way out, because `scenario_ws` cannot see what the manifest
has already collected for that scenario.

### D-051 HIGH — The freeze verified deletions, additions, and almost nothing else

- **Affected** `evaluation/results/run-3/freeze_artifacts.py`
- **Evidence** reproduced here

**What failed.** Three separate problems, all demonstrated.

- `--verify` skips any file that is *absent*, because the comparison is guarded by
  `now is not None`. Deleting `evaluation/rubric.md`, `tests/make_eval_workspace.py`, an
  answer key, a turn-2 packet or a scenario file all leave the exit at 0. Adding a whole new
  scenario is also undetected, because the comparison iterates only the old file set.
- `collect()` hashes five files. `grade_run.py`, `run_generation.py`, `PROTOCOL.md`,
  `manifest.json` and `evaluation/model-eval-protocol.md` are all outside the freeze, and
  `git_head` is collected but never compared. `grade_run.py` is the only thing that turns
  anchors into PASS or FAIL, and `PROTOCOL.md`'s stated reason for the freeze is "so the
  rules that decide a verdict cannot be written after the verdicts are known".
- The hash file is self-certifying: `--write` rewrites it from the current tree, deleting a
  section un-verifies everything that section covered, and `--verify` accepts any path.

**Why it matters.** The freeze is what makes a recorded result mean anything, and a deleted
packet is both invisible to it and fatal to the harness, which reads the packet outside any
error handling and dies with a bare traceback.

**Remediation** `e880235`. **Regression test** `tests/test_freeze_artifacts.py`, 28 cases of
which 24 fail against the previous script. The 4 that pass both ways are two controls, the
deliberate exclusion of `manifest.json`, and a case the old script caught for a different
reason.

**Decisions taken, and one left open.** A missing declared artifact is recorded as the
sentinel `MISSING` rather than dropped, so a freeze taken on an incomplete tree says so and
can never verify clean. An *addition* is treated as drift, not as a weaker signal: the
population is pinned at 103 and yield is reported as PASS over 103, so a 104th scenario moves
the denominator silently. `manifest.json` is deliberately **excluded**, because the harness
rewrites it on every batch and PROTOCOL.md makes it authoritative for collection state rather
than for rules; freezing it would fail every batch and teach the run to ignore a verifier that
is always red. `git_head` is reported on every verify and gated only behind an opt-in
`--strict-head`, because a commit comparison is weaker than the content hashes where it
matters (a working-tree edit moves bytes, not HEAD) and noisier for no gain.

**What is still open, deliberately.** The manifest is now anchored.
`artifact-hashes.json.sha256` is committed beside it and carries the digest of the manifest as
recorded in `d5656b7`, which has not been edited since. `--verify` therefore exits 1 and names
eleven moved artifacts, instead of exiting 2 because nothing anchored it. The manifest is
unchanged: adding the sidecar records what was already true rather than re-blessing the tree.

The drift is real and is what the freeze exists to catch. The freeze predates the harness work
on this branch, including its own first three fixes, and `artifact-hashes.json` has no entries
for the four files that decide a verdict, so those now read as added. Re-writing the manifest
would re-bless whatever is on disk at the moment it is written, so the re-freeze remains a human
decision, taken at an agreed commit, with the harness edits either accepted or reverted on
purpose. It is not done on this branch. `PROTOCOL.md` also still needs a line about the sidecar
and `--strict-head`, and `evaluation/results/run-4/` invokes this script, so both runs stop on
the moved artifacts until the freeze is reset.

**Status: FIXED and covered**, with the re-freeze recorded above as a separate human step.

### D-052 MEDIUM — A recorded result that would not survive being re-examined

- **Affected** `evaluation/results/run-3/grade_run.py`, `run_generation.py`
- **Evidence** from the review pass

Two smaller integrity gaps, recorded together because they are both about a recorded result
not being checkable after the fact. Both are open; the run-3 half of `b27bbea` edited
`run_generation.py` but neither of these is what that commit fixed, and both are cheap.

- `run_generation.py` records `response_sha256` per turn. `grade_run.py` never reads it, and
  the grade file records `key_sha256` but not the response hash. Replacing an answer file after
  collection is undetectable. `evaluation/WORKING-STATE.md` says "Do not re-run a completed
  scenario because its answer looks inconvenient", and the record that would make that
  auditable exists and is unused.
- A refused scenario keeps its earlier grade file. When `grade_run.py` refuses a scenario it
  writes nothing for it in that pass but removes nothing from the previous one, so the
  directory a report would read still holds the old PASS. The summary and the exit code are
  correct; the artifact on disk is not.

**Status: OPEN.** The second is the more pressing of the two. A refusal that leaves the thing
it refused sitting in the directory is a refusal a reader of that directory will not see, and
`grade_run.py` now refuses scenarios as a matter of routine.

### D-053 LOW — Recorded and accepted, with the disagreement written down

`evaluation/results/run-4/PILOT-PROTOCOL.md` lists 3 easy, 3 medium, 3 hard, 2 adversarial
and 2 regression in its sample table, which is 13, while the prose says 12 and the budget says
"12 scenarios x 2 turns = 24 requests maximum". `evaluation/results/RUNS.md` hedges to "1
regression + REG-08", which is 13 under a 12 label. The denominator for a strict pass rate is
fixed by that list. Not fixed: the sample is declared in advance, so editing it after the fact
would be exactly the thing the freeze exists to prevent. Recorded so a reader does not have to
rediscover which number is authoritative.

### D-054 MEDIUM — The freeze manifest has never been anchored on any branch

`freeze_artifacts.py` writes two files: `artifact-hashes.json`, and `artifact-hashes.json.sha256`,
a sha256sum-format digest of the first held in a second file. The module docstring says the
point of the split is that the manifest cannot vouch for itself, and that "the file has to be
committed next to the manifest for either to mean anything."

The sidecar has never been committed. Not here, not at `f95cd33`, not at `a7f4449`, not at
`b962bf5`, not on `main`. Every `--verify` therefore opens with

```
UNANCHORED MANIFEST, nothing below is anchored to anything:
  .../artifact-hashes.json.sha256 is missing, so artifact-hashes.json is not bound to
  anything outside itself
```

and ends `against a manifest nothing anchors`. The recorded hashes are still checked and the
moved count is still reported, so this is not a silent pass. What it removes is the ability to
tell an edited manifest from an untouched one: rewriting `artifact-hashes.json` to describe
whatever is on disk produces the same exit code as leaving it alone.

**Reproduction.** Six refs, each in a detached worktree, one command:

```
for ref in b27bbea f95cd33 b2e06db a7f4449 c6a9fd1 b962bf5; do
  git checkout --detach "$ref"
  python3 evaluation/results/run-3/freeze_artifacts.py --verify
done
```

`f95cd33` and `b27bbea` report 8 moved at exit 2, `a7f4449` reports 8, `b962bf5` reports 11.
Running `f95cd33` twice gives the same 8, so the count is not noise. That 8 is what D-051's
"What is still open" paragraph claims, so the claim holds. `b2e06db` and `c6a9fd1` predate the
`--verify` flag taking a default, so they exit 2 on an argparse error and are not evidence of
anything.

**Status: OPEN, blocked on the D-051 re-freeze.** The sidecar cannot be created honestly
before the re-freeze, because writing it now would bind the current manifest, which D-051
records as stale and scheduled for replacement. `freeze_artifacts.py --write` emits both files
together and is the fix, but it also re-blesses whatever is on disk at the moment it runs,
which D-051 reserves as a human decision at an agreed commit. Doing it here would answer a
question this repository has already decided is not a script's to answer.

The narrower fix, committing only the digest of the manifest as it stands, was rejected for
the same reason: it asserts that this manifest is the anchored one, which is the contested
claim. **Next action:** a maintainer decides whether the current harness edits are accepted,
then runs `python3 evaluation/results/run-3/freeze_artifacts.py --write` and commits both
files, recording the reason. Nothing else is waiting on it except D-051's human step.
