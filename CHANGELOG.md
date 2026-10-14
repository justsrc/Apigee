# Changelog

## 2026-10-14, evaluation harness audited against a clean checkout

Five defects, all of one kind: something recorded a result that nothing had produced. Four
are in the checks, one is in the run-3 grading script. Full detail in
`evaluation/defect-register.md` as D-038 through D-042.

They were found by checking the harness out fresh and running it, not by reading it. Every
one of them was invisible from inside the working tree the earlier passes used, because that
tree's own file timestamps happened to be in the order the checkers wanted. A reviewer
working in place would not have found any of them.

### The fault-probe suite was reporting nothing

`check_repo.py` decided an answer key was stale by comparing the packet's mtime against the
scenario's. An mtime is not part of a commit, and `git clone` writes every file at checkout
time, so on a pristine checkout all 103 packets looked stale. That is D-038, and the
consequence was worse than the noise.

`fault_probe.py` opens with a control probe whose whole job is to confirm the unmodified
repository passes. It failed. Every other probe runs its mutation inside a copy of that same
repository, so with the baseline already failing, all 33 probes expecting a FAIL saw a nonzero
exit whether or not their mutation had been detected. The suite meant to catch checkers
passing broken repositories was reporting nothing in a fresh clone, and `release_gate.py`,
which reads the probe result, lost A1, F1, F2 and F3 with it.

This was a false FAIL, not a false PASS, and the distinction decides how much the project's
other evidence is worth. A suite that always says PASS is actively misleading. One that
always says FAIL is merely broken, and a reader can see it is broken.

The check now renders every packet and diffs it against what is committed, the way the
fault-code index and the scenario index were already checked. All 309 committed packets are
byte-identical under the new path. It is also stricter: with a ground truth rewritten and
every packet touched ten thousand seconds into the future, the old check reported 0 stale
and the new one names the key.

### Two probes had never tested anything

`origin-field-removed` and `origin-unclassifiable-value` anchored their regex with `^` and
passed no `re.MULTILINE`, so it matched only at the start of the file. The field they meant
to change is a bullet on line 26. `re.sub` found nothing and wrote the file back unchanged.

They read green for the whole life of the suite because the mtime bug was failing the
unmodified sandbox. That is worth dwelling on: a probe that changes nothing looks exactly
like a probe that found something, provided something else is broken. `check_origin_integrity`
turns out to be correct, and nothing shipped is wrong, but the project had no evidence behind
two of the probes covering the check D-018 exists to enforce.

`fault_probe.py` now digests the sandbox before and after each probe's own mutation. A probe
expecting a FAIL that changed no file is reported as NO MUTATION and fails the suite whatever
the checker said. Content is digested rather than timestamps, because a no-op `write_text`
moves an mtime while leaving the bytes alone.

### A nonzero provider exit was a completed answer

`75f1997` fixed an error event being written as the answer and recorded two paths it left
open. This is the first. The failure predicate tested `rc == -1`, which is the harness's own
timeout sentinel, so every other nonzero exit fell through to the OK branch. A provider that
dies partway through still leaves the text it emitted, so a non-empty stream is not evidence
of a complete answer. The predicate reads `rc != 0` now, and the quota branch still runs
first so a 429 is still never retried.

### The scoring script never read the manifest

`grade_run.py --run` took the grader's JSON at face value. It scored whatever it was given
and wrote the result, and only `--list` filtered on `AWAITING_GRADE`. Against run 3's own
state, where all 103 scenarios are NOT_STARTED and no answer file exists, MED-13 came out as
`{"normalized_score": 1.0, "verdict": "PASS"}`.

This is the other end of the sentence in `75f1997`, which hardened generation on the grounds
that a false success produces a score for a turn the model never answered. The grading side
was not hardened, and the outcome stayed reachable with no generation at all.

Three lines away, an uncomputable score was coerced to FAIL whenever any anchors were
supplied, so a grader's typo of 7 on a 0-to-4 scale became a model failure in the counts.
PROTOCOL.md says the opposite in one line. Both are fixed, with `tests/test_grading_integrity.py`
driving the real file: six of its eight cases fail against the previous grader, and the two
that pass are there to show the new gate does not reject a scenario that genuinely ran.

### What did not change

The release gate still reads NOT QUALIFIED, and that is the correct result rather than a
regression. C4 is BLOCKED because no URL audit was run, and E5, G1 and G2 stay UNVERIFIED
because no run meets the A/B design. Recovering four criteria did not qualify the project and
is not presented as though it had.

Run 3 collected nothing, so no recorded score moves because of any of this. All five are
latent defects in the machinery rather than damage to a result, and the register records them
that way. Nothing here is evidence about whether the skills help. A passing probe suite says
the harness classifies the inputs it was given as described, and says nothing about whether a
live model or provider can produce a shape these suites do not model.

### Still open

The second path `75f1997` named is untouched: a policy carrying `continueOnError="true"`
that swallows a failure contributes no fault to the manifest while its text still reaches the
answer file. It is a defect in the fault inventory rather than in the outcome
classification, it is not what produced the run-3 artifact, and it is not fixed here.

## 2026-10-12, medium.md reviewed and repaired

`evaluation/audit-medium-A.md` records a technical review of MED-01 through MED-22, closing
the last of the four audit files the release gate requires. Twelve of the 22 scenarios
carried a defect: five high, four medium, three low. Ten were sound.

The five high-severity defects all asserted a mechanism that cannot produce the stated
fault, and each contradicted its own ground truth. MED-02 explained a 404 by borrowing
MED-01's environment-group verdict, though an environment in no group has no hostname at
all. MED-07 claimed `setSyncAuthorization` was unconfigured "for this environment", when
the API is org-scoped. MED-10 traced an expired token passing `VerifyAccessToken`. MED-14
omitted `<CacheExpiryInSeconds>`, the lever the OAuthV2 page documents for precisely this
situation. MED-18 inverted a conjunction, so one negative check was scored as insufficient;
that rule had been inherited into `references/hybrid.md` and was corrected there too.

Two of those were worse than misinforming, because the rubric's top anchor rewarded the
wrong action, so a correct answer scored near zero.

### Fixed, high

- **The fault-code index was missing every error on two policy pages.** The generator
  matched its section marker as `^## Error reference$`, but two pages publish that heading
  as `## <span id="errorcodes"></span>Error reference`. Both were discarded whole, which
  included 18 documented OAuthV2 runtime codes such as `steps.oauth.v2.InvalidRequest`.
  The match now tolerates leading inline markup: 173 → 195 runtime codes, 107 → 116
  deployment errors, 28 → 33 fault variables. A probe reverts the fix and confirms the
  checker catches it. Nothing had reported the loss, because a page that fails to parse
  looks exactly like a page with no error section.

### Fixed, medium and low

- MED-16, MED-20, MED-22 and MED-12 carried true quotations placed outside the scope their
  source gives them. MED-20 imported a defect the register scopes to Apigee into a hybrid
  scenario and made it load-bearing; MED-22 demanded a Cassandra check premised on a
  version upgrade it also said was not happening; MED-12's metadata called a target timeout
  a 500 where the docs say 504. Each boundary is now stated where the fact is used.
- MED-09's evidence claimed a retry inside the same quota window succeeds, against
  "subsequent calls are rejected until the counter resets".
- MED-13 promised two conditions producing one error code and supplied one. It now supplies
  two, sharing a description whose discriminator is the policy name inside the fault string.
- MED-06's answer key read "not evidence of applause".

### Not defects

Scenario titles never reach the agent: `make_packets.py` writes `# Support case <ID>` and
omits the title deliberately. Two reviewers reported title leakage anyway. Those findings
are recorded as superseded rather than outstanding, so the next pass does not re-raise them.

## 2026-10-12, audit and repair

An audit of the whole project found two critical defects, several high ones, and eight
checker false passes. Full detail, with reproduction steps, in
`evaluation/defect-register.md`.

### Fixed, critical

- **The fault-code index asserted one HTTP status for a code documented with two.**
  Apigee documents many fault codes on several policy pages, and the pages disagree. The
  generator kept only the first occurrence, so `steps.oauth.v2.invalid_access_token` was
  published as HTTP 401 when `get-oauth-v2-info-policy` documents the same code as HTTP 500.
  82 codes were affected. Records are now merged, every source page is listed, and a status
  disagreement renders as `CONFLICT` rather than being resolved by sort order.

- **Two scenarios were invisible to every tool.** MED-32 and MED-40 had their heading
  jammed onto a `---` rule (`---### MED-32. ...`). Every block splitter anchors on
  `^#{2,4}\s+`, so both were skipped by the structural checker, received no packets, and
  appeared in no index. The library has always held 103 scenarios; the tooling saw 101.

### Fixed, high

- `check_repo.py` had eight false passes, found by `tests/fault_probe.py`. Deleting one
  turn-2 prompt or one answer key, deleting a reference file still listed in a skill table,
  deleting `scenarios/regression.md`, deleting `evaluation/packets/`, emptying
  `research/pages/`, and corrupting the fault-code index all exited 0. Six were warnings
  rather than failures; two were simply unchecked.

- `check_urls.sh` reported a passing URL audit having checked nothing when given an empty
  corpus, and could not distinguish a 403 from a missing page, a timeout from a dead link,
  or a redirect from a citation resolving to the wrong article. Replaced by
  `tests/check_urls.py`, which classifies each URL into one of ten states, records redirect
  chains, checks the body is the document it claims to be, and exits 2 on no input.

- MED-26 taught the opposite of the documented cause of `JavaCalloutInstantiationFailed`
  and used a fault code that does not exist. HARD-20's remediation shipped a
  `<LoadBalancer><Server>` listing Message Processors, which names proxy targets and cannot
  work. HARD-19 and HARD-21 both cited fault codes absent from the reference.

- Regression titles state the correct disposition ("Root cause cannot be established"), and
  the packet generator put them in the prompt. The suite meant to catch skill drift was
  handing over its own grading criterion. Titles are no longer released.

### Changed

- Origin classification was inflated by 21 scenarios. The reported 53.4% real-world figure
  counts the 13 adversarial and 8 regression constructed cases as incident reports; measured
  from the scenarios it is 33.0% real-world, 31.1% documented, 35.9% synthetic.
  `check_repo.py` now enforces the controlled vocabulary.

- 185 of 294 cached pages had no manifest entry, so the documentation index published a URL
  guessed from a lossy filename. `research/repair_manifest.py` confirms every page live and
  records provenance per row: 109 recorded, 172 guess-verified, 8 corrected, 5 declared
  UNRESOLVED rather than guessed.

### Added

- `tests/fault_probe.py`, 29 controlled mutations proving the checkers detect them.
- `tests/check_urls.py`, with 15 offline classifier fixtures.
- `tests/test_leakage.py`, checking 206 prompt packets plus a deliberate canary leak.
- `tests/release_gate.py`, a machine-readable PASS/FAIL/BLOCKED/UNVERIFIED verdict.
- `tests/find_duplicates.py`, four-axis similarity across all 103 scenarios. No duplicates
  found at any threshold.
- `evaluation/source-conflicts-loadbalancing.md`, recording two current official pages that
  contradict each other, without picking one.
- `evaluation/source-notes-opdk-knownissues.md`, establishing that the known-issues register
  scopes itself to "Apigee and Apigee hybrid" and so excludes OPDK by design.
- `evaluation/MAINTENANCE.md`.

### Not verified

No model evaluation was executed in this environment. Structural validation and technical
review are reported separately and are never counted as model evaluation.

## 2026-10-11, first working version

### Added

`apigee-support-core`, the main skill. It carries the workflow: identify the product and
version before prescribing anything, take intake by symptom class, separate runtime errors
from deployment errors, run a diagnostic loop, keep a hypothesis ledger with explicit
status labels, cite sources, and sort proposed actions into five risk tiers.

Four reference files under the core skill, generated or written from verified
documentation:

- `error-codes.md`, generated by `research/build_error_index.py`. 165 runtime fault codes
  with HTTP statuses, 102 deployment error names, 28 fault variables.
- `products.md`, on telling X, hybrid, and Edge for Private Cloud apart.
- `security.md`, on OAuth, JWT, API keys and TLS.
- `sources.md`, on verifying a URL before citing it.

Scenarios: 15 easy, 15 medium, 15 hard, 12 adversarial, 8 regression. 65 in total. All 45
graded scenarios carry the required sections. Every fault code in them was extracted from
a real policy page.

`tests/check_repo.py`, a mechanical checker. It separates what a script can check from
what needs review, and says so in its output.

`tests/check_urls.sh` and `tests/check_url_one.sh`, which fetch every cited URL and check
both status and body. It found two broken citations during setup:
`api-platform/deploy/manage-api-versions` and `api-platform/develop/shared-flows` both
return 404. They were replaced with `api-platform/deploy/ui-deploy-overview` and
`api-platform/fundamentals/shared-flows`, both verified.

Research tooling: `fetch.sh`, `build_error_index.py`, `build_doc_index.py`,
`normalize_pages.py`, `RESEARCH-RECIPE.md`, `notes-known-404.txt`. 276 documentation pages
fetched and indexed.

### Changed in the pre-existing skills

`apigee-opdk-troubleshooter` and `apigee-opdk-upgrader` were audited rather than
rewritten. All 27 URLs they cited resolved, and the guidance is sound, so both were kept
and only corrected in two places.

Version pins moved from 4.53.00 to 4.53.01, which is the current release. `v4.54.00`
returns 404 and 4.53.01 resolves, so it is the latest.

Added a warning that page slugs on `docs.apigee.com` carry the release number, so
replacing `45300` with `45301` in a URL is not universally safe. Three paths that look
version-swappable 404 when swapped: `nginx-45301` and `rollback-45301` are real, but
`nginx-45300` and `rollback-45300` do not exist on the 4.53.01 tree, and the upgrade page
is `update-apigee-edge-45202-45301` rather than `update-apigee-edge-45300-45301`.

Added the verified upgrade constraint from the 4.53.01 upgrade paths page: to reach 4.53.x
you must first be on 4.52.02. This is the most common cause of an upgrade failing partway
through with a split cluster.

### Findings worth keeping

`cloud.google.com` returns HTTP 200 for pages that do not exist. The body reads "The
equivalent page does not exist in Apigee." Eight such pages were found in one sweep, and
three of the four troubleshooting entry points named in the original brief are stubs. A
status check alone is not sufficient to cite a page.

pandoc silently truncates these pages. On an 840 KB page it exits 0 and emits a few
kilobytes, keeping the first table and dropping the rest. `fetch.sh` now trims to the
article container before converting.

pandoc also leaves HTML tables unconverted on 137 of 276 pages. `normalize_pages.py`
converts them, which took the fault code count from 129 to 165.

The `compare-apigee-products` page was rewritten. It is now a feature overview comparing
X and hybrid and no longer contains an unsupported feature or API list. The Edge to X
comparison moved to `docs.apigee.com/migration-to-x/compare-apigee-edge-to-apigee-x`.

There is no Apigee X prose page for keystores or aliases. The Management API reference is
the only authoritative source. The richer prose on `docs.apigee.com` is Apigee Edge, a
different product.

Environment groups exist on X and hybrid and not on Edge. This refutes the common
assumption that they are Apigee X only. For Edge the evidence is absence rather than a
statement, so it is recorded as strongly supported rather than documented.

### Tools that were wrong before they were right

Recorded because each one failed silently, which is the failure mode this project exists
to prevent, and the fixes are why the tools are trustworthy now.

`tests/check_urls.sh` reported PASS having checked zero URLs. Inlining the worker into
`xargs sh -c` exceeded the platform argument limit, so xargs ran nothing and the empty
result read as success. It now uses a separate worker file, the worker always prints one
line per URL, and the script compares the number of checks run against the number of URLs
before reporting PASS. It was then tested against known-bad URLs and still fails.

`tests/check_repo.py` skipped the section check for any scenario whose title contained a
section name, so EASY-13, titled with the word "verification", was reported as missing its
verification section. It now skips only the title heading and prefers an exact match.

`research/fetch.sh` reported HTTP 200 for pages that do not exist, because
`cloud.google.com` answers 200 with a stub body. Eight such pages were found in one
sweep, including three of the four troubleshooting entry points named in the original
brief.

`pandoc` truncated the large documentation pages and left HTML tables unconverted on 137 of
276 pages. Both fail without an error.

### Known problems, not fixed

The VerifyJWT policy page is truncated upstream, ending mid-table with no element
reference and no error reference. `steps.jwt.*` fault codes appear in no verified source,
so they are not used in any scenario.

The OAuth HTTP status code page is deprecated and its `keymanagement.service.*` codes
disagree with the `steps.oauth.v2.*` codes on the OAuthV2 page for the same conditions.
Scenarios use the codes from the current policy page and note the discrepancy.

`policies.ratelimit.InvalidMessageWeight` is documented on both the Quota and SpikeArrest
pages, so the code alone cannot identify which policy failed. MED-08 tests this.

Nothing has been run against a live model. The scenarios are built and structurally valid,
but no evaluation run has happened, so no claim is made about how the skills perform.

The scenario content has not been reviewed by someone who knows Apigee well. Every fault
code is real and every URL resolves. Whether each scenario's expected investigation is the
best one is a review question this project cannot answer on its own.

## 2026-10-11, round 3, correctness pass

### Fixed

Every material error found by two blind review passes over 72 scenarios. Recorded in
`evaluation/baseline.md` and the per-scenario fix reports. Highlights:

**HARD-07 was inverted.** It asserted no in-place certificate update exists and scored
inventing one as a critical failure, while the page it cited documents an `update` method
and the TLS page names two methods literally called "In-place update". It would have
failed a correct answer twice. The trap now runs the other way: claiming in-place update is
impossible is the critical failure.

**EASY-06 was backwards.** It asserted header flow variables are case-sensitive; the
documentation uses both `request.header.authorization` and `request.header.Authorization` as
documented defaults for the same wire header. Rebuilt on the documented cause, an
out-of-scope variable.

Several scenarios named invented elements as the thing to go and add, which is worse than
naming one as present: EASY-10 pointed at `<SecretVariable>` and
`<VerificationOutputVariableToVerify>`, MED-04 at `<Key>` for ResponseCache, HARD-03 at
`<ClientCertStore>` and `<ClientCertAlias>`. MED-04 also had `expiryInSeconds`, the real
element being `<TimeoutInSeconds>` inside `<ExpirySettings>`.

HARD-14 named Postgres as the rolled-back store; the documented coordinated-restore trio is
OpenLDAP, ZooKeeper and Cassandra. MED-05's key-value map claim was documented, but on the
wrong page and for a policy write rather than a Management API write. MED-15 asserted a
deployment-only fault at runtime.

The error payload shape was invented suite-wide: a flat `errorcode`/`status` body rather
than the documented nested `fault` object, which has no status field at all.

### Three corrections to my own instructions

I told the fix agents `<LoadBalancing>` was invented when `<LoadBalancer>` is the real
element and the reverse is true. I told them to replace `context.request.getValue` with
`context.request.header.getValue`; `getValue` does not exist in any form, and the
documented forms are `context.getVariable` and `context.proxyRequest`. I gave a four-element
`<SSLInfo>` child list that was truncated. Each would have been baked into scenarios.

A fix report also carried a caveat claiming MED-07's `setSyncAuthorization` was not
locally verifiable. It is, in six places. Retracted in place, because a wrong caveat in a
fix report invites a later pass to break working content.

### Tools

`tests/make_packets.py` now implements the two-turn release the protocol always described
and the first run never performed. `check_repo.py` fails if either turn is missing for any
scenario or if a key heading appears in any prompt.

`check_repo.py` also parses every fenced XML and JSON block in the scenarios. Invented and
malformed markup is the most common defect class and a script can catch a missing bracket
even though it cannot tell a real element name from a plausible one.

`tests/fix_error_shape.py` had a counting bug: it compared the inner JSON against the full
fenced match, so every already-converted block counted as changed and would have had its
fences stripped. Idempotent now.

`tests/check_urls.sh` treats `$VAR` and `YOUR_ORG_NAME` style API paths as placeholders
rather than broken links, since fetching them unsubstituted returns 401 and tells us
nothing.

### Measured

`evaluation/baseline.md` records the count and, more usefully, the four error classes that
every review finds in the same order. The class that worries most: a ground truth wrong in
a way that makes a correct answer score as a critical failure. No mechanical check can see
that. Only review can, and review is what gets skipped when everything looks green.
