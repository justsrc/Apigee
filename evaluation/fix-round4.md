# Fix round 4

Final defect pass over `scenarios/hard.md`, `scenarios/adversarial.md` and
`scenarios/regression.md`. Five defects fixed, all verified against the local cache in
`research/pages/`. No web fetches. Scenario IDs, the 11-section structure and the nested
`{"fault":{"detail":{"errorcode":"..."}}}` payloads are unchanged.

Files edited: `hard.md`, `adversarial.md`. `regression.md` needed no change — none of the
defect classes below appear in it (checked by grep for `DEPLOYING`, `return 401`,
`credentials from any origin`, `nginx-453`, `Identifies double counting`).

---

## HARD-02 (MATERIAL): invented enum value

**Defect.** `hard.md` Diagnostic evidence used `DEPLOYING` as a deployment state. No such
value exists in the documentation.

**Verified.** `grep -rn "PROGRESSING" pages/` returns the documented pair, e.g.
`api-platform_fundamentals_configure-proxy-with-yaml-example.txt:395`: "Poll the revision's
deployment status, which reports `PROGRESSING` until it becomes `READY`". HARD-05 already
used "a progressing state", so the file was internally inconsistent with itself.

**Fix.** `DEPLOYING` -> `PROGRESSING`. One occurrence, in HARD-02 Diagnostic evidence.

---

## HARD-08 (MATERIAL): out-of-context quote plus a self-contradictory rubric

Two separate defects in one scenario.

### (a) The ground truth quoted half a documented statement

**Defect.** The ground truth quoted "a Quota policy referenced in multiple places in a proxy
maintains a single counter updated by all instances of the policy" and concluded "the
duplicate placement does not multiply anything". It omitted the page's own next sentence,
which says the opposite about the consequence. Worse, the diagnostic evidence asserted
"Replaying a single request through the proxy moves the counter by that request's weight and
not by two", which is not what the cited worked example shows.

**Verified.** `pages/api-platform_reference_policies_quota-policy.txt`, section "How quotas
are counted if no API products are in use":

- The worked example increments **once per policy execution**: "Flow A is executed ->
  MyQuotaPolicy is executed and its counter = 1", then Flow B, Flow A, Flow C, Flow A.
- The sentence immediately after it: "Using the same Quota policy in more than one place in
  an API proxy flow, **which can unintentionally cause Quota to run out faster than you
  expected**, is an anti-pattern".

So "single counter" is a claim about the counter, not about how many times one request
counts. With the policy attached to both the ProxyEndpoint PreFlow and the ProxyEndpoint
Request flow, a single request traverses both and moves the one counter twice. The old
scenario asserted the opposite.

**Fix.** Restored the whole documented statement and rebuilt the arithmetic so it closes:

- The PreFlow attachment now carries `<Condition>request.header.x-tier == "enterprise"</Condition>`,
  found in the Diagnostic evidence. A replayed non-enterprise request moves the counter by
  one weight; a replayed enterprise request moves it by two. One counter, two different
  increments.
- Weight mix changed to 5,000 at weight 1 and 2,000 at weight 2 -> 9,000 weighted units
  from 7,000 requests. The 1,000 enterprise requests are all weight-1 and are counted
  twice, adding 1,000. Total 10,000, which is the configured limit.
- Both wrong readings are now arithmetically refuted: count every request twice -> 18,000;
  ignore the second attachment entirely -> 9,000. Neither equals the counter that was read.
- The ticket's claim now fails for a specific, checkable reason rather than by assertion:
  the duplicate attachment is a real finding worth 1,000 of the 10,000 units, and it is not
  the main one. `<MessageWeight>` accounts for 9,000.
- Added the antipatterns page to References; that URL is the one the cached Quota page
  itself links to.

**Why this keeps the scenario hard.** It is now harder than before. There is one counter,
there is per-execution counting, there is a documented antipattern, and there is a
conditional that has to be read out of the XML. Three of the four combinations of "counted
once/twice" and "weighted/unweighted" are wrong, and only the one the evidence supports
closes the arithmetic.

### (b) The rubric paid marks for a critical failure

**Defect.** In exactly the inversion class being hunted:

- Technical correctness, 2 marks: "Identifies double counting"
- Handling of competing explanations, 0 marks: "Accepts the ticket's story" (the same claim)
- Critical failures: "asserting double counting from the two attachments alone"

So an answer asserting double counting was paid 2 marks and failed the scenario, while the
same claim scored 0 on the adjacent dimension.

**Fix.** The 2-mark descriptors were rewritten so neither one restates a critical failure:

| Dimension | 2 marks (was) | 2 marks (now) |
| --- | --- | --- |
| Technical correctness | Identifies double counting | Finds `<MessageWeight>` and states the limit is a unit count |
| Handling of competing explanations | Suspects the placement | Notices that weight and placement are both in play |

The 0-mark cell for "Handling of competing explanations" is now the critical-failure text
itself, so 0 marks and failure are the same verdict. Added an explicit **Not a critical
failure** line stating that naming the duplicate attachment as a contributing factor,
conditioned or not, is correct and worth 1,000 units; only asserting it as the whole
explanation fails. Added "Counting every request twice (18,000)" and "Removing the second
attachment and expecting 7,000 requests" to Common incorrect answers.

**Post-fix check.** A correct, honest answer says the ticket's blanket claim is wrong,
closes the arithmetic at 10,000, and does not raise the limit. It trips neither listed
critical failure, and the "Not a critical failure" line explicitly protects the part of it
that names the duplicate attachment.

---

## HARD-09 (MINOR): invented harm for a wildcard CORS origin

**Defect.** Common incorrect answers said a wildcard origin "accepts credentials from any
origin". Invented, and wrong twice over.

**Verified.** `pages/api-platform_reference_policies_cors-policy.txt:18` (Caution) and the
identical Caution at the `<AllowOrigins>` element:

> "If a proxy developer sets the `Access-Control-Allow-Origin` header to allow all (`*`), it
> effectively disables the same-origin protection."

Line 20 adds "The `AllowOrigins` field is a required policy element and the default should
not be set to allow all (`*`)". Credentials are a separate element: `<AllowCredentials>`
"indicates whether the caller is allowed to send the actual request (not the preflight)
using credentials" (line 153). A wildcard origin alone does not enable credentials.

**Fix.** Replaced the invented harm with the documented one, and said explicitly that this
is not a credentials story. The rubric and critical-failure text already keyed off
"weakens a security control", so they are now consistent with the evidence rather than
with a different claim.

---

## ADV-11 (MINOR): a false claim that undermined the scenario's own premise

**Defect.** Expected investigation said "A 404 to all clients is not an OAuth failure, since
OAuth failures return 401." ADV-11 exists on the premise that 404 is not an auth failure, so
this line undercuts the case, and it is false.

**Verified.** `pages/api-platform_reference_policies_oauth-http-status-code-reference.txt`
documents 400, 401, 404 and 500 for different OAuth conditions: 404 for an invalid refresh
token (`keymanagement.service.invalid_refresh_token`) and an invalid access token
(`keymanagement.service.invalid_access_token`), 500 for an expired access token
(`keymanagement.service.access_token_expired`), 401 for an invalid client id, 400
throughout for authorization-code and token-request errors. The page is also marked
deprecated in favour of per-policy references, which is itself worth noting.

**Fix.** Reworded so the contrast holds for the specific case used, and so the scenario
gets sharper rather than merely correct: the status code alone does not exclude OAuth,
because 404 is a documented OAuth status. What excludes it is the ticket's own account of
what changed — the failure began with a rollback that did not touch OAuth. Reasoning from
the status code alone is now visibly insufficient, which is the behaviour the scenario is
meant to punish. Added the OAuth status code reference to ADV-11's References.

**Post-fix check.** Critical failure remains "diagnosing the title's subject when the
evidence contradicts it". A correct answer rejects the title and identifies environment
addressing; it does not trip it.

---

## ADV-08 (MINOR): evidence with no supporting artefact in the cache

**Defect.** The Diagnostic evidence claimed "The 4.53.01 tree serves `nginx-45301` and
`rollback-45301`" and that "the `nginx-45301` page itself links onward to the 4.53.00 slug
`update-apigee-edge-45202-45300`". No such page is cached.

**Verified.** `ls pages/ | grep -i nginx` returns nothing. `pages/MANIFEST.tsv` lists
`rev-opdk-nginx-45301`, `rev-opdk-rollback-45301` and `rev-opdk-update-apigee-edge-45202-45301`
with byte sizes, but the corresponding `.txt` files are absent from `pages/`. The manifest
entry is not evidence; the scenario was asserting facts that cannot be checked locally.

Rewrote the evidence using two pages that are cached:

1. `https___docs.apigee.com_private-cloud_versions.txt` — the "Get started with 4.53.01
   (latest version)" block links 4.53.01 content under `/private-cloud/latest/...`
   (`overview`, `installation-overview`, `how-configure-edge`) with release notes at
   `/release/notes/45301-edge-private-cloud-release-notes`, while the previous-versions table
   lists v4.53.00 under `/private-cloud/v4.53.00/how-configure-edge` with release notes at
   `/release/notes/45300-edge-private-cloud-release-notes`. Identical topic names, different
   paths, on one page.
2. `https___docs.apigee.com_private-cloud_v4.53.01_upgrade-paths.txt` — the procedure link
   is `/private-cloud/v4.53.01/update-apigee-edge-45202-45301`, whose slug carries both
   endpoints, and the page's own upgrade-requirement note is about a different version: to
   reach 4.53.00 you must first be on 4.52.02.
3. `https___docs.apigee.com_private-cloud_v4.53.01_how-perform-backup.txt` links onward to
   `/private-cloud/v4.53.01/backup-and-restore`, showing that links inside the release tree
   carry the release number.

A first draft asserted that `latest` also served the backup pages. That was not checkable —
the versions landing page does not list backup-and-restore under `latest` — so the paragraph
was rewritten to the verified intra-tree link instead.

**Rubric consistency.** "Checks one URL" at 2 marks was reworded to "Verifies the URLs it
quotes, but does not pin the release", and the critical failure to "quoting a URL as current
for the target release without checking it on that release's tree". Partial credit now
means diligence, not an unchecked quote, so 2 marks and a critical failure can no longer
co-occur.

**Strength.** The replacement is a stronger trap than the original. `latest` is correct
today because 4.53.01 is current and will silently repoint after the next release, so an
answer that quotes it is not wrong today and is still wrong. That is the "looks right" case
the scenario was reaching for, and it is fully supported by the cached versions page.

---

## Structural verification after the round

- Scenario counts unchanged: hard 15, adversarial 12, regression 8.
- All five edited scenarios re-checked for the 11 sections: Scenario metadata, Initial
  support ticket, Initial evidence, Expected investigation, Diagnostic evidence,
  Ground-truth resolution, Correct remediation, Verification, Common incorrect answers,
  Evaluation rubric, References.
- No error payloads were added or altered, so the nested
  `{"fault":{"detail":{"errorcode":"..."}}}` shape is untouched.
- Re-read Common incorrect answers and Evaluation rubric for every edited scenario and
  confirmed no 2- or 4-mark descriptor restates a critical failure. Added explicit
  "Not a critical failure" clarifiers to HARD-08 and tightened ADV-08's 2-mark cell.