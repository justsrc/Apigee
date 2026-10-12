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
| Fixed and covered by a test | 18 |
| Fixed, coverage recorded, no dedicated probe yet | 6 |
| Open, accepted with documented reason | 8 |
| Open, awaiting external evidence | 2 |

## Later additions

### D-018 HIGH — Origin classification was inflated by 21 scenarios

**Affected** scenario metadata across all five files

**What failed.** The project reported its scenario library as 53.4% real-world, 31.1%
documented, 15.5% synthetic. Measured from the scenarios, it is **33.0% real-world, 31.1%
documented, 35.9% synthetic**.

The difference is exact rather than approximate. Adding the 13 `adversarial.md` and 8
`regression.md` scenarios to real-world gives 55; removing them from synthetic gives 16.
Both match the reported figures to the scenario, and the documented count already matched at
32. Those two suites are constructed evaluations and say so in their own headers.

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
scenarios (34 real-world, 32 documented, 37 synthetic)". All three probes fail without the
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

### D-022 MEDIUM — Two cached URLs cited by scenarios have no local copy

**Affected** 10 URLs in `scenarios/hard.md`

**What failed.** Ten cited URLs, all Edge for Private Cloud operational pages plus
`antipatterns/intro`, have no page in `research/pages/`. A reviewer working only from the
local corpus cannot check what those pages say, which is how HARD-16's invented "eight
central types" survived review.

**Correction.** The reviewer fetched them live. A cache is a convenience, not the source of
truth; `check_urls.py` verifies the live document regardless of whether a copy is cached.

**Status: OPEN, accepted.** Recording which URLs are uncached would be useful but does not
change any verdict, and the URL checker already resolves all of them.

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

## Open items accepted with reason

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

```
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

```
---### MED-32. Six requests admitted where three per minute is configured
```

Every block splitter in this project anchors on `^#{2,4}\s+`. Neither scenario matched, so
MED-32 and MED-40 were invisible to the structural checker, received no evaluation
packets, and appeared in no index. They are not headings in rendered Markdown either.

**Reproduction.** Count scenarios the way the tooling does versus the way a reader does:

```
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

## D-012 MEDIUM — 108 of 168 citations permanently redirect to a new host

**Affected** all cited documentation URLs

**What failed.** Every `cloud.google.com` URL now issues a permanent redirect to
`docs.cloud.google.com`. The citations resolve, so the previous checker reported none as
broken, but 64% of the corpus cites a hostname Google has retired. Separately,
`https://apigee.com/about/support/portal/` redirects to the product home page rather than to
a support portal, which is a citation that no longer points at what it claims.

The rewritten checker is what made this visible: it records the chain rather than following
it silently, and reports `REDIRECTED_AND_VERIFIED` separately from `VERIFIED`.

**Correction.** Recorded rather than rewritten. Bulk-editing 108 inline URLs risks breaking
scenario text that quotes a URL inside prose or code, and the support-portal citation is a
genuine dead reference that should be replaced deliberately rather than by substitution.

**Status: OPEN, accepted with reason.** Nothing shipped is technically wrong because of this.
Tracked so a 64%-redirected citation set is not mistaken for a clean one.

---

## Open items accepted with reason

| ID | Item | Why accepted |
| --- | --- | --- |
| D-013 | The fault-code index truncates cause text at 110 characters | It is an index, and the file says so. The full text is on the source page, cited per row. |
| D-014 | `decode-jws-policy` documents 20 error names in one table cell | Faithful to the source. The names are now split into individual rows and flagged as listed together upstream. |
| D-016 | Ground-truth correctness cannot be checked by script | By design. It needs review by someone who knows Apigee, which is what `evaluation/audit-*.md` records. |
| D-017 | No model evaluation of the scenarios has been run | No model-execution budget in this environment. Structural validation and technical review are reported separately and are never presented as model evaluation. |
| D-024 | 108 of 168 citations permanently redirect `cloud.google.com` to `docs.cloud.google.com` | Resolving is verified and the chain is recorded. Rewriting 108 inline URLs risks breaking scenario text that quotes them, and it is not a correctness defect while the redirects hold. |
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
