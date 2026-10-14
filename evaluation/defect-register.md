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
| Fixed and covered by a test | 21 |
| Fixed, coverage recorded, no dedicated probe yet | 7 |
| Open, accepted with documented reason | 8 |
| Open, awaiting external evidence | 2 |

Three entries changed on 2026-10-13. D-035 adds the seventh fixed-without-a-dedicated-probe
entry. D-036 adds two probes for the packet generator. The isolation-route classifier is what
moves fixed-and-covered from 19 to 21 alongside them: `tests/test_isolation_classify.py` is a
test file of its own and `release_gate.py` F6 fails if it regresses.

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
copies of them survive under `research/scratch-pages/` and looked fetched. `bb5d859` re-derived
the list and cached all eleven OPDK pages.

**Status: PARTIALLY FIXED.** As of `bb5d859` the eleven OPDK pages are cached and all eleven
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
cd /Users/justinjacob/Projects/Work/Apigee
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
contained it). `git show 3d6c521:scenarios/adversarial.md` confirms the line, and
`8966ded` changed it. The scenario ID was the only error; the defect, the diagnosis and the
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
   matching heading, so the second never reached the key. The second is the one `cb057df`
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
byte-identical between `3d6c521` and `898d9d4`. Recorded because it is the one case in that
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

**What failed.** The remediation `970e75a` added reads, in the hotfix paragraph: "The same
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

**What failed.** The handoff named `ecf2ffe` as the pre-remediation state. `ecf2ffe` is the
child of `f9d7de8`, which is itself a remediation commit that edits
`references/error-codes.md` and `references/hybrid.md`. The "35 commits since `ecf2ffe`"
count therefore absorbed `f9d7de8` into the baseline arm.

Had this gone unnoticed, both arms would have carried the first remediation commit and the
comparison would have returned a guaranteed null. A null that looks like a measurement and
is an artefact of the baseline choice is the worst available outcome, because it is
indistinguishable from a real finding at reading time.

**Correct baseline** is `5b40edd96007eda996d5787b540b1ae51e32394f`, the parent of `f9d7de8`.
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
