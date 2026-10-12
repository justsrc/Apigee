# Technical audit — scenarios/medium.md, MED-23..MED-46

> **Annotation, 2026-10-13.** The seven title-leak findings in this file (MED-23, MED-33,
> MED-36, MED-38, MED-39, MED-42, MED-44, MED-46) are superseded, not outstanding. At the time
> of this audit `tests/make_packets.py` injected the scenario title into the agent prompt. It no
> longer does: the prompt carries the scenario ID and nothing else identifying, and the title
> survives only in the answer key for the grader. See D-009 and the note at the end of
> `evaluation/defect-register.md`. The substantive findings in this file are unaffected.

Scope note: the brief said MED-32 and MED-40 do not exist. They **do** exist in the file
(`medium.md` line 4250 and line 3529, both recovered by commit `77e7ac8` "Recover MED-32 and
MED-40"). They are inside the MED-23..MED-46 range, so they are audited here. 23 scenarios
audited.

A cross-cutting defect affects five scenarios and is recorded per scenario but originates in one
place: every `error-codes.md` line citation in `medium.md` is stale. The index gained a 4-line
header paragraph (lines 8-14, commit `97510f0` "Index: merge duplicate fault codes instead of
dropping them") after the scenarios were written, so all cited line numbers are off by 4-5.

---

### MED-23 A linter rule demands a cache populate that would break the cache it is protecting
- Verdict: DEFECT
- Defect: Two problems.
  (a) Unsupported attribution to the maintainers. The scenario's "Common incorrect answers"
  states: *"A global scope widens the key namespace across every proxy in the environment, and
  **the maintainers state that its counting and behaviour differ from the default**"*. Nothing of
  the kind appears in apigee/apigeelint#480. The only maintainer statements are DinoChiesa
  2026-04-12 ("Ya, I am of the mind to just leave it alone. People can disable it in their
  .apigeelintrc file or on the command line.") and mldelaney94 2026-03-24 (an external plugin can
  be used to disable it). Neither mentions `Global`, counting, or differing behaviour.
  (b) Title leakage: "**would break the cache it is protecting**" states the ground truth
  ("the linter's finding is correct on the merits even though the customer did not break
  anything recently") in the title.
- Severity: medium (a), low (b)
- Evidence: research/issues/apigee_apigeelint-480.txt — comment by DinoChiesa (COLLABORATOR) at
  2026-04-12T23:18:05Z says "Ya, I am of the mind to just leave it alone. People can disable it in
  their .apigeelintrc file or on the command line. It's not useful in a sufficiently complex
  environment." Nothing else.

The substantive technical content is correct and well sourced:
- Default scope `Exclusive` — `api-platform_reference_policies_lookup-cache-policy.txt` line 232:
  `| **Default:** | "Exclusive" |`; line 249 gives the prefix form.
- Prefix composition as quoted — line 236: "a cache key would take the following form when scope
  is set to `Exclusive` : *orgName\_\_envName\_\_applicationName\_\_proxy|TargetName\_\_*
  \[ *serializedCacheKey* \]".
- `<Prefix>` overrides `<Scope>` — line 238: "If a `<Prefix>` element is present in `<CacheKey>`,
  it supersedes a `<Scope>` element value."
- `Global` shares across the environment — line 244: "Cache key is shared across all API proxies
  deployed in the environment."
- Unset variable on miss — line 253: "(if no value is retrieved, the variable will not be set)".

### MED-24 A linter release breaks every working rate limit policy in the estate
- Verdict: OK
- Defect: n/a
- Severity: n/a
- Evidence: The diagnostic claim about the documented restriction is accurate.
  `api-platform_reference_policies_spike-arrest-policy.txt` line 52 lists `<UseEffectiveCount>`
  as a child element; line 599: "**Note:** Although the default value is `false`, Apigee
  organizations should set this element to `true`."; line 462: "The use of
  [`<UseEffectiveCount>`] with a value or `false` is not supported for *any* Apigee organizations
  or for Apigee hybrid organizations running production workloads." The origin claim is exact:
  research/issues/apigee_apigeelint-590.txt shows v2.76.0 regression, PO042 message verbatim,
  v2.77.1 release, and reporter confirmation 23 minutes after filing
  (CREATED 00:01:28Z, CLOSED 00:24:23Z).

### MED-25 The linter says a quota is used twice, and the quota is used once per request
- Verdict: DEFECT
- Defect: Stale index citation. The scenario and the fault-code ledger both say
  `policies.ratelimit.QuotaViolation` is "verified at `error-codes.md` line 42". It is on line
  **46**. (Same root cause as MED-33/34/36/38; the index header grew by 4 lines.)
- Severity: low
- Evidence: `.agents/skills/apigee-support-core/references/error-codes.md` line 46:
  `| \`policies.ratelimit.QuotaViolation\` | 500 | The quota limit was exceeded. | [quota-policy](...) |`

Everything substantive is correct and matches the real thread:
- research/issues/apigee_apigeelint-168.txt: maintainer ssvaidyanathan 2023-03-11 — "Released
  v2.36.0 with a fix for this... It looks for the policy and checks if its across flows or across
  ProxyEndpoint or TargetEndpoint. If its within the same flow, it checks if the Condition tag is
  same." Two reporter confirmations 2023-03-14. Matches the scenario's three-way description
  (different flows / different endpoints / different `<Condition>`).

### MED-26 A deployment fails with a Java callout error, and the build tool corrupted the artifact
- Verdict: DEFECT
- Defect: **The scenario contradicts the page it cites, twice, on the meaning of the fault code.**
  (a) "Expected investigation": *"`JavaCalloutInstantiationFailed` means the class was found but
  could not be constructed. That has a small number of causes, and one of them is not 'the jar is
  missing from the bundle'."* The JavaCallout policy reference states the opposite: the documented
  cause of `JavaCalloutInstantiationFailed` **is** that the class file is not in the jar.
  (b) "Common incorrect answers" doubles down: *"If the class were absent the fault would be a
  resource error rather than an instantiation failure."* Directly contradicted by the same table,
  which separately documents `ResourceDoesNotExist` as being about the `<ResourceURL>` file, not
  the class.
  (c) Secondary: the scenario says "The deployments API ... reports
  `steps.javacallout.JavaCalloutInstantiationFailed`". No such prefixed code exists in the
  documentation. `steps.javacallout.` is the prefix of the only runtime fault code,
  `steps.javacallout.ExecutionError`. `JavaCalloutInstantiationFailed` is a bare **deployment
  error name** with an "N/A" HTTP status, not a `steps.`-prefixed fault code.
- Severity: critical
- Evidence: research/pages/api-platform_reference_policies_java-callout-policy.txt line 231:
  `| \`JavaCalloutInstantiationFailed\` | \`Failed to instantiate the JavaCallout Class
  [classname]\` | N/A | The class file specified in the \`<ClassName>\` element is not in the jar. |`
  and line 230: `| \`ResourceDoesNotExist\` | ... | N/A | The file specified in the
  \`<ResourceURL>\` element does not exist. |`. Line 222 shows the only `steps.javacallout.*` code
  is `steps.javacallout.ExecutionError` (500); line 259 shows the example response errorcode is
  `javacallout.ExecutionError`.

The packaging root cause itself is well evidenced:
research/issues/apigee_apigee-deploy-maven-plugin-155.txt, comment by rad264 2021-06-10: "it was
because I had enabled filtering for the maven-resources-plugin (`<filtering>true</filtering>`) on
the entire apiproxy folder, which included the jar... once I disabled filtering, it deployed
successfully." Note the scenario's remediation ("Scope resource filtering to the directories that
actually contain text templates") also glosses over that modern `maven-resources-plugin` treats
`.jar` as non-filtered by default; the original poster's case may differ from rad264's.

### MED-27 The deployment tool says it succeeded, and the revision is in ERROR
- Verdict: OK
- Defect: n/a
- Severity: n/a
- Evidence: research/issues/apigee_apigeecli-276.txt confirms every element. Path prefix `./`:
  "Deployment will fail with the following error on the console: `Status: instance "us-east1"
  reported error repository.FailedToLoadFile: "Failed to load file : /sharedflows/fromscratch.xml"`"
  — note the path begins at the root of the sharedflows directory, exactly as the scenario states.
  Two maintainers failed to reproduce (srinandan 2023-08-23, ssvaidyanathan 2023-08-28, same
  version 1.122). Reporter's discriminating experiment: "I cloned this repo and deployed the test
  shared flow EXACTLY the same way you did and it worked for me, too. However, when I copied the
  test shared flow into my repo - not even doing anything else to it - the behavior was the same as
  the issue I'm dealing with." Fix confirmed on `v1.124.0-beta`; maintainer: "We will release the
  version in a few days as we consolidate other fixes". Duplicate #273 carries label `duplicate`.

### MED-28 Provisioning over mutual TLS succeeds, then the tool fails its own verification
- Verdict: DEFECT
- Defect: The second reference does not support the claim it is attached to. It is captioned
  "Provisioning a tenant with Edge for Private Cloud" but points at the hybrid **upgrade** page
  (`https://cloud.google.com/apigee/docs/hybrid/latest/upgrade`), which contains **zero**
  occurrences of "provision" and nothing about mutual TLS client certificates. The scenario's
  entire diagnostic and remediation content (mTLS provisioning, `--tls-cert/--tls-key/--tls-ca`)
  has no support in either cited page.
- Severity: medium
- Evidence: research/pages/MANIFEST.tsv maps `hybrid_latest_upgrade` to
  `https://cloud.google.com/apigee/docs/hybrid/latest/upgrade`; `grep -c -i "provision"
  research/pages/hybrid_latest_upgrade.txt` returns **0**.

The technical content is otherwise sound and honestly labelled, and is corroborated by the
researcher's own independent source read in research/notes-rw-github.md lines 142-160
(`createAuthorizedClient` sets only `InsecureSkipVerify`, never calls `tls.LoadX509KeyPair`;
`verifyRemoteServiceProxy` tolerates 401/500; `if !p.IsGCPManaged || p.isCloud() { return
verifyErrors }` means hybrid prints warnings and exits 0). The scenario's own text correctly
states the evidence level ("no maintainer has replied, and the thread has zero comments").

### MED-29 The same TLS error, two different causes, and the accepted fix works for one of them
- Verdict: DEFECT
- Defect: Three problems; the first is the serious one.
  (a) **The ground truth invents a root cause and a working remedy that the evidence cannot
  support.** It asserts the interception case is a *hostname identity* failure — "Chain validation
  and hostname identity are separate checks, and the presented certificate fails the identity
  check regardless of how much chain validation is relaxed" — and that "Adding the corporate root
  CA to the host trust store works because it makes the proxy's own certificate legitimately
  valid for the connection." Neither claim is in the cited issue, and the first is wrong on the
  merits: the reporter's error is `"Error: unable to verify the first certificate"`, a
  **chain-verification** failure, and the `insecure` / `-k` option the reporter tried
  (`rejectUnauthorized: false`) disables the hostname identity check as well, so the scenario's
  mechanistic explanation for why the flag "does not address hostname identity" does not hold.
  The reporter's own conclusion in the thread is that **no fix was found**: "the bottom line is
  that I need to use apigeetool outside my corporate firewall to make it work."
  (b) Reference mismatch: "Protecting credentials with TLS in Edge for Private Cloud" points at
  `https://cloud.google.com/apigee/docs/hybrid/latest/scale-and-autoscale`, a scaling page with
  **zero** occurrences of "TLS" or "truststore".
  (c) Origin label: apigeetool-node#6 is `STATE: open`, not "merged"; the fix landed via a
  different PR (#7) and was confirmed by the reporter ("I think, this problem has been resolved
  in #7").
- Severity: high (a), medium (b), low (c)
- Evidence: research/issues/apigee_apigeetool-node-33.txt — reporter tmarrs 2015-12-31 body:
  `"Error: unable to verify the first certificate"`; and 2016-01-06: "I've also tried to use the
  `-k` option to turn off ssl checking, and it still doesn't work - I get other errors. So, the
  bottom line is that I need to use apigeetool outside my corporate firewall to make it work."
  research/pages/hybrid_v1.17_scale-and-autoscale.txt — `grep -c -i "protecting
  credentials|TLS"` returns **0**.

Correctly sourced parts: issue #33 is `STATE: open`; the reporter did ask whether #6's fix
applied ("The solution to .../issues/6 doesn't fix the problem."); the `cafile`/PEM request and
the eventual fix are in #6.

### MED-30 The token endpoint is correct and the client is sending a malformed header
- Verdict: OK
- Defect: n/a
- Severity: n/a
- Evidence: research/pages/api-platform_reference_policies_oauthv2-policy.txt lines 925-930 give
  exactly the four documented differences the scenario enumerates — Cache-Control header (line
  927), `"token_type"` `BearerToken` → `Bearer` (line 928), quoted vs numeric `expires_in` /
  `refresh_token_expires_in` (line 929), and the expired-refresh-token error shape (line 930).
  Line 936: "**Default** | `false`: By default, the policy will exhibit certain non-RFC-compliant
  behaviors as described above." Origin is exact:
  research/issues/apigee_apigee-api-catalog-drupal-46.txt shows behaviour reported 2019-10-01,
  documentation linked 2019-11-06, and "doc bug b/141752334 is now fixed" on 2020-12-08.

### MED-31 *(not present)*
- Verdict: n/a — no such block in the file.
- Defect: n/a
- Severity: n/a
- Evidence: `grep -n "^### MED-" scenarios/medium.md` returns no MED-31.

### MED-32 Six requests admitted where three per minute is configured
- Verdict: DEFECT
- Defect: Source misattribution. "Diagnostic evidence" states: *"The current spike-arrest policy
  reference states that per-minute rates are 'smoothed into intervals of seconds', that the
  smoothing algorithm 'smooths traffic spikes by dividing the rate limit that you specify into
  smaller intervals', **and that 'Smoothing is not coordinated across Message Processors.'**"*
  The first two quotes are in the SpikeArrest page; the third is **not**. The string appears only
  on the *Comparing Quota and SpikeArrest* page. The SpikeArrest policy page contains zero
  occurrences of "coordinat" and zero occurrences of "Message Processor".
- Severity: medium
- Evidence: research/pages/api-platform_develop_comparing-quota-and-spike-arrest-policies.txt
  line 23: "Lets you choose between a smoothing algorithm or an effective count algorithm...
  **Smoothing is not coordinated across Message Processors.**";
  `grep -c -i "coordinat" research/pages/api-platform_reference_policies_spike-arrest-policy.txt`
  returns **0**.

Secondary: `policies.ratelimit.SpikeArrestViolation` is cited as "error-codes.md line 43"; it is
on line **47**.

Also unaddressed, though not stated as fact: the same SpikeArrest page carries a flat
contradiction the scenario never surfaces — line 601, in the `false (default)` tab, reads
"**Rate smoothing is not supported for Apigee organizations.**" and line 599 reads "Apigee
organizations should set this element to `true`", on an Apigee (X) org, which is the product this
scenario targets. A scenario whose whole ground truth is "the default smooths per processor" on
Apigee should acknowledge or answer that line.

Everything else checks out: the accepted SO answer is quoted verbatim
("SpikeArrest has no ability to be distributed across message processors"); 60/3 = 20s; the
`failed` variable caveat is quoted exactly; SpikeArrest-before-Quota is confirmed on the comparing
page line 21; and `docs.apigee.com/...comparing-quota-spike-arrest-and-concurrent-rate-limit-policies`
really does resolve to Edge documentation (`research/so/legacy_comparing.html` title:
"Comparing Quota and SpikeArrest policies | Apigee Edge | Apigee Docs").

### MED-33 Rate of 5 per minute, but the third call in ten seconds is rejected
- Verdict: DEFECT
- Defect: Stale index citation only. `policies.ratelimit.SpikeArrestViolation` is cited as
  "`error-codes.md` line 43" (twice, in Initial evidence and in the ledger); it is on line **47**.
- Severity: low
- Evidence: `.agents/skills/apigee-support-core/references/error-codes.md` line 47:
  `| \`policies.ratelimit.SpikeArrestViolation\` | 429 | The rate limit is exceeded. | [spike-arrest-policy](...) |`

Substance verified: 60/5 = 12 seconds (spike-arrest-policy.txt line 607 "Per-minute rates get
smoothed into full requests allowed in intervals of seconds"); "one request allowed every 200
*milliseconds* (1000/5)" is line 525; the "not coordinated across Message Processors" statement is
quoted from the comparing page, which this scenario also references, so the attribution is
acceptable here; the 10pm/weight-2 → five-messages example is line 395; the `failed` warning is
line 641; SpikeArrest-before-Quota is comparing page line 21.

### MED-34 A key value map read returns nothing, and the policy reports no error
- Verdict: DEFECT
- Defect: **The ground truth contradicts the diagnostic evidence the scenario itself supplies.**
  "Diagnostic evidence" states: *"The trace shows `apigee.countryCode` resolving to a value, for
  example `IN`, while the map contains keys named `IN` only in the API-scoped map"*. If the
  variable resolves to `IN` and the map contains a key `IN`, then
  `<Parameter ref="apigee.countryCode">` produces exactly the right key name — the `ref` is
  working. The ground truth nevertheless declares two defects: "Two defects, reported as one...
  Separately, the `<Parameter>` element uses `ref` ... so even with the scope corrected the key
  name being searched for is the *value* of `apigee.countryCode`, not the string `Development` or
  `IN`." It is *precisely* the string `IN`. There is one defect in the supplied evidence (scope
  mismatch), not two. The "two defects" reading belongs to the second Stack Overflow report,
  where the reporter wrote `ref="entry.Development"` — a variable that does not exist.
- Severity: medium
- Evidence: research/pages/api-platform_reference_policies_key-value-map-operations-policy.txt
  line 695: "| ref | Specifies the name of a variable whose value contains the exact name of the
  key you want to create, get, or delete. | N/A | Required if no literal value is given between
  the opening and closing tags. |" — i.e. `ref` is the *documented, intended* form when the key
  name is dynamic. research/so/q_21897932.json shows the reporter's policy already used
  `<Parameter ref="apigee.countryCode">` and the accepted fix was only `<Scope>apiproxy</Scope>`.

Secondary: `InvalidIndex` is cited as `error-codes.md` line 219; it is on line **224**.

Other content verified: `index` is 1-based (line 453) and zero/negative is a deployment failure
(line 873); `ratelimit` is reserved in two places (lines 601 and 939); the second SO report and
its accepted answer (`<Parameter ref="k1">` vs `<Parameter>k1</Parameter>`) are real and match
research/so/a_27850597.json.

### MED-35 502 Bad Gateway at exactly two minutes, with the backend reporting success four minutes later
- Verdict: DEFECT
- Defect: Misstatement of the source it depends on. "Expected investigation": *"Then work the
  documented causes for this exact fault code, and be willing to find they do not fit. The
  official playbook gives **two**."* The playbook gives **four**. Two documented causes are
  silently dropped, including "Backend closes connection abruptly", which is the cause whose own
  documented resolution ("the customer needs to engage their network operations team and backend
  server team", "collect the packet capture on the first hop right after Apigee") the scenario
  effectively reproduces in its own ticket.
- Severity: medium
- Evidence: research/pages/api-platform_troubleshoot_playbooks_runtime_unexpected-eof-at-target.txt
  line 3831: "A typical cause for a 502 Bad Gateway error is the Unexpected EOF error which can
  have the following reasons:" — followed by four table rows at lines 3842 ("Incorrectly
  configured target server"), 3846 ("Backend closes connection abruptly"), 3850 ("Incorrectly
  configured keep alive timeout") and 3854 ("NAT usage with AWS NLB target with cross-zone load
  balancing and IP preservation").

Secondary, low:
- Product label says "Apigee (and Apigee hybrid)" but the NLB cause is scoped `(Apigee X only)`
  (playbook line 3855). The scenario applies that cause without flagging the restriction.
- "The current defaults are `connect.timeout.millis` 3000 ms and `io.timeout.millis` 55000 ms,
  **capped at 300 seconds**" — the 300-second figure is not in the endpoint-properties reference
  at all; it comes from the 504 playbook ("Note that 300 seconds is the maximum limit"). The
  endpoint-properties reference only says the Ingress timeout "defaults to 300 seconds and is not
  configurable" (line 260) and that `api.timeout` "must be shorter than the standard Message
  Processor timeout of 300 seconds" (line 252).

Substance otherwise verified: 503 for connect timeout / 504 for `io.timeout.millis` / 408 for
ingress read (endpoint-properties-reference.txt lines 68, 84-85); defaults 3000 and 55000
(lines 66, 80); `keepalive.timeout.millis` default 60000 (line 60); `api.timeout` "cannot be set
with a variable" (line 252); `messaging.adaptors.http.flow.UnexpectedEOFAtTarget` at
`mon_fault-codes.txt` line 81 and `GatewayTimeout` at line 78, with
`grep -c "messaging.adaptors" .agents/.../error-codes.md` returning 0; `useCount=7` /
`bytesRead=0` / `bytesWritten=1303` at playbook line 4116; NLB resolution "Cloud NAT behaves
correctly here, and this is an issue with NLB architecture. No changes can be made at Apigee"; the
honesty about the undocumented 120-second wall is a genuine strength.

### MED-36 A JavaScript policy times out intermittently, and raising the limit is the wrong fix
- Verdict: DEFECT
- Defect: Stale index citation only. `steps.javascript.ScriptExecutionFailed` is cited as
  "`error-codes.md` line 61"; it is on line **66**. (HTTP 500 is correct.)
- Severity: low
- Evidence: `.agents/skills/apigee-support-core/references/error-codes.md` line 66;
  research/pages/api-platform_reference_policies_javascript-policy.txt line 404 also shows
  `| \`steps.javascript.ScriptExecutionFailed\` | \`500\` |`.

Also, low: title leakage — "**and raising the limit is the wrong fix**" states the ground truth
("`Raise timeLimit to 1000`" is the accepted answer the scenario wants rejected).

Substance verified: the free-trial note is quoted exactly from javascript-policy.txt line 192 —
"Specifies the maximum time (in milliseconds) a script can execute... Note: For free trial
accounts, execution time is limited to 200 ms." with "Required"; the proxy-within-proxy quotes
are verbatim from api-platform_antipatterns_proxy-within-proxy.txt lines 3734, 3769-3770; the
`LocalTargetConnection`/`APIProxy`/`ProxyEndpoint` sample matches line 3785-3791; and
research/so/a_22995892.json confirms the accepted answer is "The `timeLimit` attribute can be
updated to raise the execution limit."

### MED-37 One quota policy referenced from three flows exhausts faster than expected
- Verdict: DEFECT
- Defect: **Wrong flow-variable name in the diagnostic evidence.** The scenario instructs the
  agent to read `quota.<policy>.used.count` in a debug trace. No such variable exists. The
  documented Quota flow variable is `ratelimit.{policy_name}.used.count`. An agent following the
  scenario will look for a variable that is never populated.
- Severity: medium
- Defect (secondary): `policies.ratelimit.QuotaViolation` cited as "`error-codes.md` line 42"; it
  is on line **46**.
- Evidence: research/pages/api-platform_reference_policies_quota-policy.txt line 1168:
  `| ratelimit.{policy_name}.used.count | Long | Read-Only | Returns the current quota used
  within a quota interval. |` (and line 279, "ratelimit.QuotaPolicy.used.count: Current counter
  value"). Nothing in the page uses a `quota.` prefix for counter values.

Substance otherwise verified, and unusually well sourced:
- Line 118: "If there is no API product associated with an API proxy, a quota policy maintains a
  single counter, regardless of how many times you reference it in an API proxy. **The name of
  the quota counter is based on the `name` attribute of the policy.**"
- Lines 120-126 reproduce the Flow A/B/C worked example with exactly the letters and the
  1,2,3,4,5 sequence the scenario quotes.
- Line 86: "By default, Apigee maintains a separate quota counter for each operation defined in
  an API product"; line 100 documents `quotaCounterScope` as `PRODUCT` or `PROXY`.
- Line 130: "Using the same Quota policy in more than one place in an API proxy flow, which can
  unintentionally cause Quota to run out faster than you expected, is an anti-pattern."
- Line 14: "Quotas apply to individual API proxies and are not distributed among API proxies."

### MED-38 OAuth rejects a valid-looking token because no API product matched
- Verdict: DEFECT
- Defect: (a) Internal contradiction in the ticket. "Initial evidence" instructs the agent:
  *"Note a discrepancy worth surfacing to the agent: **the customer quotes a
  `keymanagement.service.`-prefixed variant**, which is the Apigee Edge-era string. The current
  index carries the `steps.oauth.v2.`-prefixed form."* But the scenario's own Initial support
  ticket, four lines above, quotes
  `"errorcode":"steps.oauth.v2.InvalidAPICallAsNoApiProductMatchFound"`. The customer as written
  quotes nothing of the sort. (The `keymanagement.service.` string is in the *source* SO question,
  research/so/q_24035609.json, not in this scenario's ticket.)
  (b) Stale citation and incomplete attribution: `steps.oauth.v2.InvalidAPICallAsNoApiProductMatchFound`
  is cited as "`error-codes.md` line 132, sourced to the delete-oauth-v2-info policy page"; it is
  on line **137**, and that row lists **three** source pages (delete-oauth-v2-info,
  get-oauth-v2-info-policy, set-oauth-v2-info-policy), not one.
- Severity: medium (a), low (b)
- Evidence: `.agents/skills/apigee-support-core/references/error-codes.md` line 137 lists all
  three policies; research/so/q_24035609.json body contains
  `"errorcode":"keymanagement.service.InvalidAPICallAsNoApiProductMatchFound"`.

Note the HTTP status itself is **not** affected by the known dedupe defect: all three policy pages
document 401 (delete-oauth-v2-info.txt line 161; get-oauth-v2-info-policy.txt line 457), so the
scenario's 401 is right. Also, title leakage: "**because no API product matched**" is the ground
truth.

The four-link enumeration is accurate against research/so/a_24035609.json (accepted answer score 3
"ensure that your API bundle is associated with at least 1 API Product"; equal-scored runner-up
score 3 "check that the product ... is listed in the products list"; third answer "manual"
approval; fourth answer about paths).

### MED-39 Every client call times out, and the Kubernetes object at fault is in another namespace
- Verdict: DEFECT
- Defect: Origin label. "Origin: **reported real-world case**, sourced from official documentation
  retrieved live this session (`.../playbooks/ingressgateway/api-calls-fail-timeout-errors`),
  page last updated 2026-10-09." This is a Google-authored troubleshooting playbook describing
  documented behaviour. There is no public incident report behind it. Labelling it "reported
  real-world case" inflates the evidence provenance and, in this scenario, the only "case" content
  (the error strings, the pending Service, the `istio-operator.yaml` range) is lifted verbatim from
  the playbook — so the scenario is effectively documented behaviour wearing a real-world label.
- Severity: medium
- Evidence: research/pages/api-platform_troubleshoot_playbooks_api-calls-fail-timeout-errors.txt
  — "Last updated 2026-10-09 UTC"; the page body begins "Possible causes ... The possible causes
  for the istio-ingressgateway service to be in a pending state are as follows". It is a
  documentation page, not a report. (The page's own Symptom section does reproduce the same error
  strings and the pending-Service table the scenario quotes, so the *content* is accurate.)

Substance otherwise verified verbatim:
- "Jobs in erroneous/pending state in istio-system namespace" and "Incorrect IP address range
  assigned to external load balancer" as configured in `istio-operator.yaml` — page lines 3834-3845.
- `kubectl get services -n istio-system` with `EXTERNAL-IP <pending>` — page lines 3809-3815.
- `kubectl -n istio-system delete job <JOB_NAME_FROM_STEP_1>` — page line 3876.

Title leakage: "**and the Kubernetes object at fault is in another namespace**" is the ground
truth.

### MED-40 Two green deploys, one invisible conflict
- Verdict: DEFECT
- Defect: The ground truth asserts a platform mechanism the cited register does not contain.
  "Ground-truth resolution" states: *"the platform has recorded an ambiguity it will later resolve
  by **choosing one winner**. **The loser 404s.**"* The register documents only that no error is
  returned and the deployments appear to succeed. It says nothing about a winner being chosen, and
  nothing about a 404. The scenario half-concedes this later ("Not a critical failure: not being
  able to say which proxy 404s. That is exactly the customer problem, and **the register gives no
  way to determine it**"), which contradicts its own ground-truth paragraph.
  Separately, the scenario omits the one page in `research/pages/` that *does* state the routing
  rule directly — the environment groups page, line 249: "Base paths must be unique within a host
  (no two proxies can have the same base path within a host)".
- Severity: low
- Evidence: research/pages/apigee-known-issues.txt line 2196 (entry 300660653): "Deploying proxies
  with the same path to multiple environments that are attached to the same instance and
  environment group is not allowed and should return a warning message about a base path
  conflict. **Instead, no error is shown and the deployments appear to succeed.**" — no mention of
  winner selection or of 404.
  research/pages/api-platform_fundamentals_environmentgroups-working-with.txt line 249: "- Base
  paths must be unique within a host (no two proxies can have the same base path within a host)".

The documented core of the diagnosis is correct: the entry exists, is Apigee, and is FIXED.

### MED-41 "Operation group limit of 51 exceeded in Operation Config"
- Verdict: DEFECT
- Defect: Reference deep link is dead. The scenario cites
  `https://cloud.google.com/apigee/docs/api-platform/publish/create-api-products#behavior-resource-path`.
  The cached page has no element with that id; the relevant section is "Default behavior of
  resource paths", whose anchor is `#default-behavior-of-resource-paths`. (The stale anchor comes
  from the known-issues register's own link.)
- Severity: low
- Evidence: research/pages/api-platform_publish_create-api-products.txt line 208: `### Default
  behavior of resource paths`; `grep -n "behavior-resource-path"` on that file returns nothing.
  The wildcard rules the scenario relies on are at lines 197-206 ("### Using wildcards in resource
  paths").

Substance verified: research/pages/apigee-known-issues.txt line 1278 — "APIproducts are limited to
50 paths. If you add additional paths, an error message is displayed: `Operation group limit of 51
exceeded in Operation Config`", status OPEN at line 1276. Both workarounds quoted at lines 1280 and
1282, including "The App that is associated with your API Products would need to be updated to
include the new one, but credentials and client-side request details have been proven to not need
changing."

### MED-42 The proxy limit that depends on how long your base paths are
- Verdict: OK
- Defect: n/a
- Severity: n/a
- Evidence: research/pages/apigee-known-issues.txt line 2218 (entry 301845257, FIXED at line 2216):
  "Attempting to deploy more than 800 proxies to an environment group fails with an error. **The
  limit on which an error is returned is lower than 800 when the basepaths are longer than 15
  characters.**" Line 1562 (entry 329304975, FIXED at line 1558): "Apigee is enforcing a temporary
  limit of 1000 basepaths per environment **to avoid potential failures when deploying API proxy
  revisions**." Line 1564: "If your API proxies or revisions contain more than one basepath, the
  total number of basepaths per environment must not exceed 1000." Every quoted phrase, both entry
  IDs and both FIXED states match.

Minor, not scored: title leakage — "**that depends on how long your base paths are**" hands over
the 15-character second factor that the scenario's rubric treats as the key diagnostic step.

### MED-43 The 404 that a version bump does not fix
- Verdict: OK
- Defect: n/a
- Severity: n/a
- Evidence: research/pages/apigee-known-issues.txt entry 378686709 (line 795) reproduces the
  scenario's example exactly: "Proxy-1: /a/v1/b / Proxy-2: /a/*/c ... calls to the `Proxy-2` may
  return a `404`, if the wildcard path is evaluated as `/a/v1/c`", with status line 800-801
  "FIXED in Apigee (support call required) / FIXED in hybrid 1.14.3 and hybrid 1.15.1 (procedure
  required)", and the text at line 809: "This issue is fixed in Apigee and in hybrid 1.14.3 and
  later. **However, the fix is not enabled by default.**" The opt-in asymmetry the whole scenario
  turns on is genuinely in the source.

Minor, not scored: "Skills expected: apigee-support-core, apigee-opdk-upgrader" — the OPDK
upgrader skill covers Edge for Private Cloud upgrades, but this scenario is Apigee (SaaS) and
hybrid, so the second skill does not apply.

### MED-44 Headers that were removed, then put back, and are still pinned
- Verdict: OK
- Defect: n/a
- Severity: n/a
- Evidence: research/pages/apigee-known-issues.txt entry 422757662 (line 1959), affected
  "Apigee 1-15-0-apigee-5 / hybrid 1.15.0", "FIXED in Apigee 1-15-0-apigee-7 and Apigee
  1-15-0-apigee-8": "Apigee stopped sending `x-b3` headers to target endpoints when Distributed
  Trace is disabled... Therefore this change has been reverted starting in Apigee
  1-15-0-apigee-7." The per-org opt-in note ("please reach out to Apigee to revert this change for
  now in your Apigee Org") and the caution ("Apigee does not recommend using `x-b3` headers when
  Distributed Trace is disabled") are both present verbatim.

Minor, not scored: title leakage — "**Headers that were removed, then put back, and are still
pinned**" states the non-monotonic behaviour and the per-org pin, which are precisely the two
conclusions the rubric asks the agent to reach.

### MED-45 `The URI contain illegal characters` after a version bump
- Verdict: OK
- Defect: n/a
- Severity: n/a
- Evidence: research/pages/apigee-known-issues.txt entry 480997525 (line 349), affected "Apigee
  1-17-0-apigee-1", "FIXED in Apigee 1-17-0-apigee-2": "In Apigee version 1-17-0-apigee-1, a Netty
  upgrade to 4.1.129.Final introduced a regression. This can cause API proxy calls to fail with a
  `400` status code and the error message `The URI contain illegal characters`. This issue is
  tracked externally in netty/netty#16020." The scenario's insistence on quoting the string without
  the trailing "s" matches the register character for character, and the upstream issue link is
  the register's own.

### MED-46 The 502 that means your certificate is bad
- Verdict: DEFECT
- Defect: Reference does not support the remediation. The ground truth is documented correctly, but
  "Correct remediation" — *"Fix the target's certificate chain, or add the issuing authority to the
  appropriate truststore"* — is attached to the ingress-gateway TLS playbook, which is about
  **ingress** one-way TLS (cert/key pairs, Kubernetes secrets) and contains **zero** occurrences
  of "truststore", "trust store" or "Enforce". The page that does document `<TrustStore>` and
  `<Enforce>` for a target `<SSLInfo>` block (`options-configuring-tls`) is not cited.
- Severity: low
- Evidence: `grep -c -i "truststore|trust store|Enforce" research/pages/api-platform_troubleshoot_playbooks_ingressgateway_api-calls-failing-tls-errors.txt`
  returns **0**. The supporting material is at
  research/pages/api-platform_system-administration_options-configuring-tls.txt line 45 (`<Enforce>`
  — "Enforces strict SSL ... A failure code of 4xx or 5xx is returned") and line 49 (`<TrustStore>`
  — "A keystore containing trusted server certificates").

Also low: title leakage — "**The 502 that means your certificate is bad**" is the ground truth
verbatim, and the scenario's own rubric scores "States 502 here means target certificate
validation failed".

Substance otherwise verified: research/pages/apigee-known-issues.txt line 1582 (entry 310384001,
hybrid 1.11.0, OPEN at line 1580) — "Cert validation failures may return a 502 instead of a 503
error response when users add the tag `<Enforce>true</Enforce>` in the target `<SSLInfo>` block for
default validation of TLS target endpoint certificates." Line 1605 (entry 205666368) — "Apigee
hybrid does not validate the target certificate by default." Both quoted correctly, and the Product
label (Apigee hybrid) matches the register.

---

## Summary

- **OK: 7** — MED-24, MED-27, MED-30, MED-42, MED-43, MED-44, MED-45
- **DEFECT: 16** — MED-23, MED-25, MED-26, MED-28, MED-29, MED-32, MED-33, MED-34, MED-35,
  MED-36, MED-37, MED-38, MED-39, MED-40, MED-41, MED-46
- MED-31 does not exist in the file.

By severity: critical 1 (MED-26), high 1 (MED-29), medium 9, low 5 (+ title-leakage observations
on 8 further scenarios, not scored separately).

Cross-cutting: all five `error-codes.md` line citations (MED-25, MED-33, MED-34, MED-36, MED-37,
MED-38) are stale by 4-5 lines because the index header grew after the scenarios were written.
The `error-codes.md` dedupe defect the brief warned about was checked and does **not** affect any
of these codes: `steps.oauth.v2.InvalidAPICallAsNoApiProductMatchFound` is 401 on all three pages
that document it, and `QuotaViolation` / `SpikeArrestViolation` / `ScriptExecutionFailed` are each
owned by a single policy page.

| ID | Severity | One-line description | Source that contradicts it |
| --- | --- | --- | --- |
| MED-26 | critical | Ground truth and "incorrect answers" both assert `JavaCalloutInstantiationFailed` means the class WAS found; the policy page documents its cause as "The class file specified in the `<ClassName>` element is not in the jar", and shows no `steps.javacallout.JavaCalloutInstantiationFailed` code exists | research/pages/api-platform_reference_policies_java-callout-policy.txt line 231 (also 222, 230) |
| MED-29 | high | Ground truth invents a hostname-identity diagnosis and a working "add the corporate root CA" remedy; the cited thread's error is a chain failure, the reporter's conclusion is that no fix exists, and `-k`/`rejectUnauthorized:false` disables identity checking too | research/issues/apigee_apigeetool-node-33.txt (body + 2016-01-06 comment) |
| MED-29 | medium | Reference captioned "Protecting credentials with TLS…" points at the hybrid scale-and-autoscale page, which has zero TLS mentions | research/pages/hybrid_v1.17_scale-and-autoscale.txt |
| MED-28 | medium | Reference captioned "Provisioning a tenant with Edge for Private Cloud" points at the hybrid upgrade page, which has zero occurrences of "provision" | research/pages/hybrid_latest_upgrade.txt; MANIFEST.tsv |
| MED-23 | medium | "Common incorrect answers" attributes to the maintainers a statement about `Global` scope counting/behaviour that does not exist in apigeelint#480 | research/issues/apigee_apigeelint-480.txt (DinoChiesa 2026-04-12, mldelaney94 2026-03-24) |
| MED-32 | medium | Attributes "Smoothing is not coordinated across Message Processors." to the SpikeArrest policy page; the string exists only on the comparing page | research/pages/api-platform_develop_comparing-quota-and-spike-arrest-policies.txt line 23; spike-arrest-policy.txt has 0 hits for "coordinat" |
| MED-34 | medium | Ground truth declares a second `ref`-vs-literal defect, but the scenario's own evidence shows `apigee.countryCode` resolving to `IN` against a map containing key `IN`, i.e. `ref` is correct | research/pages/api-platform_reference_policies_key-value-map-operations-policy.txt line 695; research/so/q_21897932.json |
| MED-35 | medium | "The official playbook gives two [causes]" — the playbook lists four; two documented causes are dropped | research/pages/api-platform_troubleshoot_playbooks_runtime_unexpected-eof-at-target.txt lines 3831, 3842, 3846, 3850, 3854 |
| MED-37 | medium | Diagnostic evidence tells the agent to read `quota.<policy>.used.count`; the documented variable is `ratelimit.{policy_name}.used.count` | research/pages/api-platform_reference_policies_quota-policy.txt line 1168 (also 279) |
| MED-38 | medium | "Initial evidence" says the customer quoted a `keymanagement.service.`-prefixed variant; the scenario's own ticket four lines above quotes `steps.oauth.v2.` | scenarios/medium.md line 5308 vs 5323-5325; research/so/q_24035609.json |
| MED-39 | medium | Origin labelled "reported real-world case" but the source is a Google-authored troubleshooting playbook (documented behaviour), with no public incident report behind it | research/pages/api-platform_troubleshoot_playbooks_api-calls-fail-timeout-errors.txt ("Last updated 2026-10-09 UTC") |
| MED-35 | low | "capped at 300 seconds" is not stated in the endpoint-properties reference; it comes from the 504 playbook | research/pages/api-platform_reference_endpoint-properties-reference.txt (300 s appears only at lines 252, 260, as Ingress/MP timeout) |
| MED-25 / MED-33 / MED-34 / MED-36 / MED-37 / MED-38 | low | Six `error-codes.md` line citations are stale by 4-5 lines | .agents/skills/apigee-support-core/references/error-codes.md lines 46, 47, 66, 137, 224 |
| MED-38 | low | Cites line 132 (actually 137) and says "sourced to the delete-oauth-v2-info policy page" when the row lists three pages | .agents/skills/apigee-support-core/references/error-codes.md line 137 |
| MED-40 | low | Ground truth asserts the platform "will later resolve by choosing one winner. The loser 404s."; the register documents neither, and the scenario later concedes "the register gives no way to determine it" | research/pages/apigee-known-issues.txt line 2196 |
| MED-41 | low | Reference anchor `#behavior-resource-path` does not exist on the cited page | research/pages/api-platform_publish_create-api-products.txt line 208 |
| MED-46 | low | Remediation ("add the issuing authority to the appropriate truststore") attached to an ingress TLS playbook with zero truststore/`Enforce` mentions | research/pages/api-platform_troubleshoot_playbooks_ingressgateway_api-calls-failing-tls-errors.txt; cf. options-configuring-tls.txt lines 45, 49 |
| MED-29 | low | Origin says apigeetool-node#6 was "merged"; the issue is `STATE: open` and the fix landed via #7 | research/issues/apigee_apigeetool-node-6.txt header |

Title-leakage observations (low, not separately scored): MED-23, MED-25, MED-26, MED-30, MED-36,
MED-38, MED-39, MED-42, MED-44 and MED-46 each state the ground-truth conclusion in the heading.
MED-36 ("raising the limit is the wrong fix"), MED-38 ("because no API product matched"), MED-46
("The 502 that means your certificate is bad") and MED-26 ("the build tool corrupted the artifact")
are the clearest cases — the answer is readable from the title line alone.