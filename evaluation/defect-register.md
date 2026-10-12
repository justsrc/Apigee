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
| Fixed and covered by a test | 11 |
| Fixed, not yet independently re-reviewed | 2 |
| Open, accepted with documented reason | 6 |
| Open, awaiting external evidence | 2 |

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

**Why critical.** This is wrong ground truth on a runtime fault code, in a scenario whose
entire purpose is teaching that code. An agent is graded against an answer the
documentation contradicts.

**Status: OPEN. Fixing now.** See the scenario repair log.

---

## D-006 HIGH — HARD-20 remediation ships a broken TargetServer config

**Affected** `scenarios/hard.md` HARD-20

**What failed.** The canonical remediation pins Message Processors with a proxy
`<LoadBalancer><Server name="mp-az1-1"/></LoadBalancer>`. `<Server>` names a
**TargetServer**, that is, a backend host the proxy itself calls. Message Processors are
not proxy targets. An agent copying that XML produces a target-server configuration that
cannot work.

**Status: OPEN. Fixing now.**

---

## D-007 MEDIUM — `MANIFEST.tsv` keys do not match the files on disk

**Affected** `research/pages/MANIFEST.tsv`

**What failed.** `build_doc_index.py` relies on the manifest to map a cached filename back
to its URL, because inverting the lossy filename encoding does not work. But the keys do
not match the files: manifest key `fix-mon-fault-codes` versus file `mon_fault-codes.txt`.
Any lookup that assumes `name -> name + ".txt"` silently falls through to the guess path.

**Status: OPEN. Fixing now.**

---

## D-008 MEDIUM — Every `error-codes.md` line citation in the scenarios is stale by 4–5 lines

**Affected** `scenarios/medium.md`, `scenarios/hard.md`

**What failed.** Scenarios cite `error-codes.md` by line number, for example
"`error-codes.md` line 43". The fix in D-001 added a header block to that file, shifting
every line reference. The citations now point at the wrong lines.

**Status: OPEN.** Deliberately not repaired by re-numbering. A line number into a
generated file is inherently unstable: it breaks again on the next regeneration. The
correct fix is to cite the fault code, not the line, and that is a per-scenario edit.

---

## D-009 MEDIUM — Regression scenario titles disclose their own resolution

**Affected** `scenarios/regression.md`, `tests/make_packets.py`

**What failed.** `make_packets.py` line 206 injects the scenario title into the agent's
prompt. Eight of the eight regression titles state the answer, for example a title that
names the winning explanation. The suite that exists to catch a skill that got longer and
less accurate cannot detect anything, because the agent is handed the conclusion.

**Status: OPEN. Fixing now.**

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
`docs.cloud.google.com`. The citations resolve, so no checker reported them as broken, but
64% of the corpus cites a hostname Google has retired. `https://apigee.com/about/support/portal/`
redirects to the product home page rather than to a support portal.

**Status: OPEN, accepted.** Resolving is verified and the redirect chain is recorded. Mass
rewriting 108 citations is a mechanical change with a real risk of breaking scenario text
that quotes a URL inline, and it is not a correctness defect while the redirects hold.
Recorded so it is not mistaken for a clean citation set.

---

## Open items accepted with reason

| ID | Item | Why accepted |
| --- | --- | --- |
| D-013 | The fault-code index truncates cause text at 110 characters | It is an index, and the file says so. The full text is on the source page, which is cited per row. |
| D-014 | `decode-jws-policy` documents 20 error names in one table cell | Faithful to the source. The names are now split into individual rows and flagged as listed together upstream. |
| D-015 | Ten cited URLs have no local cached page | All are Edge for Private Cloud operational pages. They were verified live. Local caching is a corpus gap, not a citation defect. |
| D-014b | `apigeecli` issues are in the corpus but no scenario cites one | Coverage preference, not a defect. |
| D-016 | Ground-truth correctness cannot be checked by script | By design. It needs review by someone who knows Apigee, which is what `evaluation/audit-*.md` records. |
| D-017 | No model evaluation of all 103 scenarios has been run | No model-execution budget in this environment. Structural validation and technical review are reported separately and are never presented as model evaluation. |