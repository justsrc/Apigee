# Technical audit — scenarios/medium.md, MED-01..MED-22

Companion to `audit-medium-B.md`, which covers MED-23..MED-46. Together the two files
give every scenario in `medium.md` a recorded technical review, which is what release-gate
criterion D3 requires. 22 scenarios audited, in six independent read-only passes of three
or four scenarios each.

Source of truth is the cached corpus only: `research/pages/` (295 files),
`research/issues/` (39 threads), `research/notes-*.md`, and
`.agents/skills/apigee-support-core/references/`. No network was used and no scenario file
was edited during the audit itself.

## Result

Ten scenarios were sound as written. Twelve carried defects: five high, four medium, three
low. The five high-severity defects each inverted a piece of the diagnostic logic rather
than merely misquoting it:

- **MED-02** borrowed MED-01's environment-group verdict to explain a 404, which
  contradicts MED-02's own evidence that the `prod` hostname resolves and serves traffic.
  An environment in no group has no hostname at all.
- **MED-07** asserted `setSyncAuthorization` was never configured "for this environment".
  The API is `organizations/{org}:setSyncAuthorization`, so an org-scoped grant cannot be
  absent for one environment and present for its siblings. The premise was unsatisfiable.
- **MED-18** inverted a conjunction. The register documents WIF **and** a forward proxy
  together, so a single negative check excludes the issue. The scenario, and the reference
  file it was inherited from, both taught the opposite.
- **MED-10** asserted a trace in which `VerifyAccessToken` succeeded on an expired token,
  which that policy cannot do, while its own ground truth said the token was expired. The
  premise was unsatisfiable as written.

## Where two reviewers disagreed

MED-09 and MED-10 were audited twice, independently, and the passes disagreed.

On **MED-09** one pass called it clean; the other found that its diagnostic evidence
claimed a retry inside the same window succeeds, against `quota-policy.txt:591` ("If the
counter for the policy reaches this limit value, subsequent calls are rejected until the
counter resets") and the same statement at line 421. The second reading is the correct one
and the defect was fixed. The later pass then re-read the corrected text and found it
sound, which is the outcome the fix was aiming for.

On **MED-10** both passes found a defect and disagreed only on severity, medium against
high. The higher rating is recorded here, because the premise was unsatisfiable and an
answer that reasoned correctly could not have satisfied it.

## One suite-level defect, found here and fixed in the generator

The audit surfaced `steps.oauth.v2.InvalidRequest` as documented on the OAuthV2 page but
absent from the generated `error-codes.md`, which `medium.md` instructs agents to treat as
authoritative. The cause was in `research/build_error_index.py`: it matched the section
heading with `^## Error reference$`, and two policy pages publish that heading as
`## <span id="errorcodes"></span>Error reference`. Both pages were dropped wholesale —
every runtime code, deployment error, and fault variable on each. The index gained 22
runtime codes, 9 deployment errors and 5 fault variables once the match tolerated leading
inline markup. `tests/fault_probe.py` carries a probe that reverts the fix and confirms the
checker catches it.

The project's own note applies here and is the reason it was worth fixing properly: a
generated reference that is quietly incomplete is worse than none, because it is trusted.

## Note on titles

Titles are not a grading defect anywhere in this suite. `tests/make_packets.py` writes
`# Support case <ID>` into the prompt and deliberately omits the scenario title, so a title
phrased as a conclusion cannot hand the agent the criterion. Titles remain in the answer key
for the grader. Findings that treat a leaky title as a defect have been marked
non-actionable rather than silently dropped.

---

### MED-01. Deployed successfully, every request returns 404

- Verdict: OK
- Defect: n/a for every load-bearing claim. One low-severity *precision* item that I am
  explicitly unsure rises to a defect: medium.md:27 and medium.md:50-51 assert "environment
  groups do not exist on Edge" flatly, while the project's own reference says to hedge
  ("strongly supported, not documented, so say so rather than asserting it flatly",
  products.md:48-52). Second reading: the sentence is agent-facing guidance about *why* to
  establish the product, not a claim to be verified, and no listed critical failure or
  rubric cell penalises an unhedged statement, so it cannot score a correct answer wrong.
- Severity: n/a (borderline low, non-load-bearing)
- Evidence:
  - Core rule, verbatim: `research/pages/api-platform_fundamentals_environments-overview.txt:16`
    "An environment must be a member of at least one environment group before you can
    access proxies deployed within it. In other words, you must assign an environment to a
    group before you can use it." Restated at `:142` ("Environments | Must be in at least one
    environment group"). This is exactly the claim at medium.md:56-57.
  - Mechanism behind the 404, verbatim:
    `research/pages/api-platform_fundamentals_environmentgroups-working-with.txt:95` "Environments
    that are not in a group cannot be accessed because there is no host name associated with
    them. Host names are defined on the environment group, not on the environment." This
    supports medium.md:61-62 ("the proxy hostname resolves to nothing that serves this
    environment"). Note the docs never print the string "404" for this case; the 404 status
    in medium.md:43 is a correct inference, not a documented quote, and the scenario does
    not claim otherwise.
  - Remediation is real and documented as both API and console:
    `api-platform_fundamentals_environmentgroups-working-with.txt:129` "To add a new
    environment to an environment group using the Apigee API, send a `POST` request to the
    Environment group attachment API", curl at `:136-139`, and `:97` "you have an option to
    add an unassigned environment to an environment group using the Apigee UI or the Apigee
    API". Matches medium.md:69-71.
  - Remediation/verification pairing holds: medium.md:78-80 asks to re-check other
    environments in the same group; `api-platform_fundamentals_environments-overview.txt:160`
    "You can use the hostname to route requests to a proxy deployed in any of the
    environments" and `:294` "Every deployment to an environment has the potential to affect
    the routing of traffic for every environment group to which that environment is
    attached" show a misconfigured group can reach further than the environment being fixed.
  - Incorrect-answer entry is not fabricated: "Error Saving Revision" is a real deployment
    error string, `api-platform_troubleshoot_policies_deployment_assign-message-deployment-errors.txt:148`.
  - Edge claim provenance: products.md:48-52 and research/notes-product-differences.md:238
    ("Label: documented for X+hybrid; strongly supported (documentation-level) for Edge").
    MED-01's second reference, `get-started/compare-apigee-products`
    (medium.md:107-108), cannot carry that weight: the cached page is X-vs-hybrid only —
    `api-platform_get-started_compare-apigee-products.txt:7` "compares the features and
    functionality between Apigee and Apigee hybrid" — and products.md:29-40 warns that this
    page "used to carry that list" and "has been rewritten". Citing it is not a false quote
    (the scenario makes no quotation from it), but it is a weak pointer for the Edge claim.
  - Title, difficulty, critical failures: the title states a symptom, not the answer;
  - `medium` is right (two hypotheses, one must be rejected on sight); the two critical
    failures (redeploy; assert deploy failed) cannot be tripped by a correct answer, since
    the ground truth (medium.md:61-65) explicitly denies both.

---

### MED-02. Works for some users, 404s for others, same deployment

- Verdict: DEFECT
- Defect: the ground truth requires the agent to accept a second cause that the scenario's
  own evidence contradicts, and it attributes that 404 to the MED-01 environment-group
  failure in a form the documentation forbids. MED-02 asserts (medium.md:159) "the 404 is
  the environment group issue from MED-01 affecting one hostname", and MED-01's issue is
  specifically that the environment is **not a member of any group**
  (medium.md:55-57, 61-62). But `research/pages/api-platform_fundamentals_environmentgroups-working-with.txt:95`
  states an environment not in a group has **no host name associated with it and cannot be
  accessed**, and `api-platform_fundamentals_environments-overview.txt:16` repeats the
  membership requirement. MED-02's own evidence then requires that prod *is* reachable:
  "The colleague and the customer both use the `prod` environment hostname" (medium.md:148)
  and "Analytics shows traffic in both" (medium.md:136). Those cannot both hold — if prod
  is in no group it has no hostname, so no colleague request and no prod analytics record
  can exist. Compounding this, the propagation half of the answer rests on an observation the
  evidence block deletes: the ticket says the colleague "still gets the old behavior"
  (medium.md:130) but the Initial evidence replaces it with "Requests from another region
  return 404" (medium.md:136), so the agent is never shown the old-revision signal that is
  the only evidence for propagation. Both the remediation (medium.md:164-165, "separately
  resolve the environment group membership that is causing the 404") and the Verification
  (medium.md:172-174) then inherit the contradiction.
- Severity: high
- Evidence:
  - Documented semantics that break the premise:
    - `api-platform_fundamentals_environmentgroups-working-with.txt:95` — "Environments that
      are not in a group cannot be accessed because there is no host name associated with
      them."
    - `api-platform_fundamentals_environments-overview.txt:16` — membership is a precondition
      for accessing proxies; `:14` "You define hostnames on your environment groups (not on
      individual environments)".
  - What is correct and citable in MED-02:
    - "eventually consistent across Message Processors" (medium.md:142) —
      `api-platform_deploy_ui-deploy-overview.txt:19` "In Apigee, MPs act independently of
      one another and any given MP can be in a different state than the other MPs ... This is
      known as an *eventually consistent* deployment model for API proxies."
    - Deployment state as a separate check (medium.md:146-148) —
      `api-platform_deploy_ui-deploy-overview.txt:97-112` shows `"state": "READY"` and
      `pods[].deploymentStatus: "deployed"`; `:154` same in the gcloud form;
      `api-platform_fundamentals_configure-proxy-with-yaml-example.txt:395` "The deploy
      request returns immediately; deployment is asynchronous. Poll the revision's deployment
      status, which reports `PROGRESSING` until it becomes `READY`".
    - "The deployment API call returning success means the deployment was accepted, not
      that every runtime has finished loading it" —
      `api-platform_get-started_compare-apigee-products.txt:39-40` "Asynchronous deployments /
      Retrieving deployment status is based on the last time the runtime plane 'checked-in'
      with the management plane".
    - The deployments API returns "actual state reported by runtime pods" —
      `research/pages/INV-reference_apis_apigee_rest_v1_organizations.environments.apis.revisions.deployments.txt`
      (`get` method description), which supports checking per-pod status as a distinct step.
  - Contrast with the alternative 404 cause the scenario never considers:
    `api-platform_deploy_ui-deploy-overview.txt:67` documents a yellow-triangle state meaning
    "some routing did not update due to base path conflicts" — a documented 404-shaped
    routing outcome on a not-fully-propagated deployment that fits "404 on one hostname"
    better than "prod is in no group".
  - Title leakage / difficulty / critical failures: the title is a symptom, not the answer,
    and the single critical failure (medium.md:194) is properly qualified "without evidence",
    so a correct answer is not scored wrong by that line. The defect is in the ground truth,
    not in the grading hooks.
  - Minimal repair that would clear the defect: either drop the env-group second cause
    entirely, or make the evidence consistent with it (e.g. state that the customer's
    hostname is not attached to the group while the colleague's is, and put that finding in
    the Diagnostic evidence), and restore the colleague's "old behavior" observation to the
    Initial evidence block.

---

### MED-03. Load balancing does not fail over to a healthy backend

- Verdict: OK
- Defect: n/a
- Severity: n/a
- Evidence (every XML element and every quoted string checked against the schema docs):
  - `<MaxFailures>` default and its exact quoted sentence (medium.md:258-260) —
    `research/pages/api-platform_deploy_load-balancing-across-backend-servers.txt:342` "**The
    MaxFailures default is 0.** This means that Apigee always tries to connect to the target
    for each request and never removes the target server from the rotation." Same statement
    at `research/pages/api-platform_antipatterns_load-balancing-maxfailures.txt:146`. The
    element is a real child of `<LoadBalancer>` (`:329`).
  - HTTP errors do not count as failures, verbatim (medium.md:266-270) —
    `api-platform_deploy_load-balancing-across-backend-servers.txt:314` "when Apigee does
    receive a response from a target, even if the response is an HTTP error (such as `404`
    or `500`), that counts as a response from the target server, and the failure counter is
    reset. To ensure that bad HTTP responses (such as `500`) also increment the failure
    counter ... you can add the `<ServerUnhealthyResponse>` element with `<ResponseCode>`
    child elements." Confirms "Only codes listed under `<ServerUnhealthyResponse>` increment
    the counter."
  - Retry semantics and default (medium.md:261-264) — `:227` "**Retries are triggered by
    I/O exceptions and HTTP time outs. Retries are not triggered by HTTP error codes (`4xx`,
    `5xx`).**"; `:360` "By default `<RetryEnabled>` is set to `true`"; `:370` "There must be
    a minimum of two target servers defined in the target endpoint configuration for retry
    to work." The scenario's two-server example satisfies that, so "every other request
    gets noticeably slower before it succeeds" (medium.md:222-223) is satisfiable.
  - Remediation XML is schema-correct and near-identical to the documented samples:
    `<Algorithm>RoundRobin</Algorithm>` `:326`; `<MaxFailures>5</MaxFailures>` `:329`;
    `<ServerUnhealthyResponse><ResponseCode>…` `:330-335`; `<HealthMonitor>` as a child of
    `<HTTPTargetConnection>` `:571`, `:600`, sample `:616-625`; `<IsEnabled>`,
    `<IntervalInSec>`, `<TCPMonitor>` `:583-585`; `<ConnectTimeoutInSec>` `:634`. The
    MaxFailures+HealthMonitor pairing in the scenario's block is character-for-character the
    antipattern page's best-practice sample,
    `api-platform_antipatterns_load-balancing-maxfailures.txt:124-141`.
  - "Enabling a health monitor requires `<MaxFailures>` greater than 0, and the documentation
    recommends both together" (medium.md:308-309) —
    `api-platform_deploy_load-balancing-across-backend-servers.txt:539` "You must set
    `<MaxFailures>` greater than 0 when using a health monitor.", `:344` "It is best to use
    MaxFailures \> 0 with a health monitor", `:589`, and
    `api-platform_antipatterns_load-balancing-maxfailures.txt:113` "**Always define a Health
    Monitor** when `MaxFailures` is set to a non-zero value".
  - Remediation reaches its own Verification (medium.md:314-317): removal at threshold —
    `:567` "If the number of failures for that server meets or exceeds a predefined threshold
    (`<MaxFailures>`), Apigee stops sending requests to that server"; return to rotation —
    `:344` "When a health monitor is in place, Apigee automatically puts the target server
    back in rotation after the target is up and running again", `:537` "No proxy re-deployments
    are required". Both failure modes are exercised by different settings, as the scenario
    states.
  - Trace/Cloud Logging note (medium.md:319-320) — `:352-354` "the individual server failures
    that initiated the failover are not explicitly displayed within Trace sessions ... consult
    your Google Cloud logs." Quoted accurately.
  - Algorithm values (medium.md:333-335) — `:223` "three load balancing algorithms,
    `RoundRobin`, `Weighted`, and `LeastConnections`. Round Robin is the default algorithm";
    `:237` repeats the enumeration. `weightedRoundRobin` / `leastConnectionsWithHealthCheck`
    appear nowhere in the corpus; the scenario correctly calls them out as nonexistent.
  - No fault code is named, so error-codes.md is not exercised here.
  - Non-defect observations, recorded for completeness: (a) the title asserts the surface
    finding ("does not fail over") but withholds the harder half (a 500 never counts as a
    failure at any MaxFailures value), so it is symptom-level, not answer-level; (b) the
    remediation pairs a TCP monitor with 500 classification, and `:598` says a successful TCP
    check "resets the failure count to 0" while `:346` says monitor calls count toward
    MaxFailures — so a 500-returning node may flap. The scenario's verification only demands
    that it "leaves rotation once the threshold is reached" (`:567`), which the fix does
    achieve, so this is a nuance, not a defect. `medium` is the right classification.

---

### MED-04. Cached responses are stale and nobody can reproduce it

- Verdict: OK
- Defect: n/a. One uncertain, non-load-bearing wording item I flag rather than call a
  defect: medium.md:417-418 says "The documented ResponseCache elements are `<DisplayName>`,
  `<CacheKey>` with its `<Prefix>` and `<KeyFragment>` children, and `<Scope>`." Read
  strictly, that is an incomplete enumeration — the same page's element reference also lists
  `<ExpirySettings>`, `<CacheResource>`, `<CacheLookupTimeoutInSeconds>`,
  `<ExcludeErrorResponse>`, `<SkipCacheLookup>`, `<SkipCachePopulation>`,
  `<UseAcceptHeader>`, `<UseResponseCacheHeaders>`, `<Properties>`
  (`api-platform_reference_policies_response-cache-policy.txt:129-152`), and MED-04's own
  sample policy at medium.md:399-409 uses three of them. Reading A: it is shorthand scoped to
  the cache-key paragraph and no scoring cell depends on it. Reading B: an agent could
  wrongly conclude ResponseCache has only four elements. Nothing in the ground truth,
  remediation, or critical failures depends on the enumeration, so I do not score it as a
  defect.
- Severity: n/a (borderline low, non-load-bearing)
- Evidence:
  - The central doc-disagreement claim is exactly right (medium.md:420-429):
    - ResponseCache reference form, no revision —
      `api-platform_reference_policies_response-cache-policy.txt:493` "a cache key would take
      the following form when scope is set to `Exclusive` : *orgName\_\_envName\_\_apiProxyName\_\_proxy\|TargetName\_\_* [ *serializedCacheKey* ]",
      and the example at `:507` "apifactory__test__weatherapi__default__apiAccessToken".
    - Working-with-cache-keys form, revision present —
      `api-platform_reference_policies_working-cachekeys.txt:138` "orgName__envName__apiProxyName__deployedRevisionNumber__nameof(proxyEndpoint|targetEndpoint)__[serializedCacheKey]",
      and the example at `:146` "mycompany__prod__weatherapi__16__default__hello__world"
      (revision 16 spelled out in the surrounding text at `:141`).
    - Both pages agree Exclusive is the default and Prefix supersedes Scope —
      response-cache-policy.txt:489 (Default "Exclusive"), `:495` "If a `<Prefix>` element is
      present in `<CacheKey>`, it supersedes a `<Scope>` element value", `:326` "A `<Prefix>`
      element value overrides a `<Scope>` element value"; working-cachekeys.txt:119 and the
      worked example at `:147` `<Prefix>system1</Prefix>` → "system1__hello__world". That last
      example is what supports medium.md:472-474 ("it would remove the org, environment, and
      proxy names from the prefix").
  - The scenario is right that this is an inference and not a documented guarantee
    (medium.md:431-437): neither page states deploy-clears-cache behaviour. I found no such
    statement in either file — the claim of restraint is accurate.
  - `<CacheKey>` / `<KeyFragment>` / `<Prefix>` are real elements —
    response-cache-policy.txt:202-208 (`<CacheKey>` skeleton), `:270-306` (`<KeyFragment>`,
    `ref` attribute), `:308-328` (`<Prefix>`); working-cachekeys.txt:8, 21, 29 ("Apigee
    composes the cache key of two parts, the prefix part and the composite fragment part,
    separated by a double-underscore"). Remediation's "documented composition rules are in
    Working with cache keys" (medium.md:461-462) is fair.
  - Diagnostic-evidence policy XML is schema-valid and matches the documented element
    reference verbatim in structure (medium.md:399-409 vs
    `api-platform_reference_policies_response-cache-policy.txt:131-151`): `async`,
    `continueOnError`, `enabled`, `name`, `<DisplayName>`, `<CacheKey><KeyFragment
    ref="request.uri"/>`, `<Scope>Exclusive</Scope>`, `<ExpirySettings><TimeoutInSeconds>`,
    `<CacheResource>`. `request.uri` as a KeyFragment ref is the documented example at `:136`.
    `TimeoutInSeconds` inside `ExpirySettings` is documented at `:447-459`.
  - `<Key>` belongs to the JWT policies, not ResponseCache (medium.md:414-418, 499-500) —
    `api-platform_reference_policies_generate-jwt-policy.txt:411-414` `<Algorithms><Key>key-algorithm</Key><Content>…`
    and `:433` "`<Key>` | Required | Specifies the encryption algorithm for the key.";
    `api-platform_reference_policies_verify-jwt-policy.txt:378`, `:399`. Grep for `<Key>` in
    `api-platform_reference_policies_response-cache-policy.txt` returns nothing.
  - Header-variable refs are valid — response-cache-policy.txt:72 "Any HTTP header is
    available as `request.header.{header_name}`, for example `request.header.user-agent`",
    so the `request.header.x-tenant-id` / `x-pricing-version` fragments in the remediation
    are legal syntax.
  - Read-only cache-key variable (medium.md:480-482) —
    `api-platform_reference_policies_response-cache-policy.txt:657` "`responsecache.{policy_name}.cachekey`
    | String | Read-Only | Returns the key used".
  - "Changing the key … entries written under the old key become unreachable rather than
    being invalidated" (medium.md:476-478) is a sound inference from the composition rules and
    is not contradicted anywhere in the corpus.
  - Arithmetically consistent: Apigee TTL 300 s, upstream TTL 5 min, observed window "a few
    minutes", "Turning off the Apigee cache would not reduce it below five minutes"
    (medium.md:445-448) — all mutually consistent; the upstream 5-minute figure is supplied as
    scenario evidence (medium.md:439) and is labelled synthetic at medium.md:366, which is
    the honest labelling.
  - No correct answer is trapped: the two critical failures (medium.md:516-517) are mirrored by
    two explicit incorrect-answer entries (medium.md:493-494, 499-500), and the tenant-separation
    check demanded by Verification (medium.md:488-489) is achievable only after the key change
    the remediation prescribes — remediation does reach its own verification.
  - Title states a symptom, not an answer ("nobody can reproduce it" is the customer's
    framing); `medium` is defensible, though the required doc-conflict handling is the
    hardest reasoning in this file and could justify `hard`.

---

## Cross-cutting findings (MED-01–MED-04)

1. **Environment-group absence is asserted as a global fact in MED-01 and then relied on in
   MED-02 with opposite consequences.** The same corpus line
   (`research/pages/api-platform_fundamentals_environmentgroups-working-with.txt:95`,
   "Environments that are not in a group cannot be accessed because there is no host name
   associated with them") is correct in MED-01 (no hostname → 404) and fatal in MED-02 (no
   hostname → the colleague and the analytics record cannot exist). Any MED-0x that borrows
   MED-01's resolution must re-derive it from the evidence rather than importing the verdict.
2. **One cross-scenario reference, one citation standard.** MED-01's second reference
   (`get-started/compare-apigee-products`, medium.md:107-108) is a page the project has
   already recorded as rewritten and no longer carrying unsupported-feature lists
   (`.agents/skills/apigee-support-core/references/products.md:29-40`), so it cannot support
   the Edge claim MED-01 makes at medium.md:27 and medium.md:50. MED-02, by contrast, has no
   reference at all for the env-group cause its ground truth requires. The References blocks
   and the "hedged vs. flat" rule for the Edge claim are inconsistently applied across these
   four scenarios.
3. **Two different 404 mechanisms are available in the corpus and are not distinguished in
   MED-02.** Beyond environment groups,
   `research/pages/api-platform_deploy_load-balancing-across-backend-servers.txt` is silent,
   but `api-platform_deploy_ui-deploy-overview.txt:67` documents routing that "did not update
   due to base path conflicts", and
   `api-platform_fundamentals_environments-overview.txt:294` documents environment
   attachment changing routing group-wide. A scenario that pairs a 404 with an incomplete
   deployment should say which mechanism it means.
4. **Scenario XML blocks are, in general, schema-faithful.** Every element and attribute in
   MED-03 (`<MaxFailures>`, `<ServerUnhealthyResponse>/<ResponseCode>`,
   `<HealthMonitor>/<TCPMonitor>/<ConnectTimeoutInSec>`, `<RetryEnabled>`) and MED-04
   (`<CacheKey>/<KeyFragment>/<Prefix>`, `<Scope>`, `<ExpirySettings>/<TimeoutInSeconds>`,
   `<CacheResource>`) matched the documented schema exactly, including capitalization. The
   element-fabrication defect class did not recur in this block; the defects found here are
   evidence/ground-truth consistency (MED-02) and enumeration precision (MED-04).

---

### MED-05. Key value map updates are not visible everywhere

- Verdict: OK
- Defect: n/a for every load-bearing claim. One low-severity precision item I am
  explicitly unsure rises to a defect: medium.md:596 asserts "Staging with two keys is
  the supported pattern." I could find no documented two-key/blue-green KVM rotation
  pattern anywhere in the corpus — the only "alongside the existing" language is about
  `<InitialEntries>` adding new pairs, which is a different mechanism
  (`api-platform_reference_policies_key-value-map-operations-policy.txt:558`,
  `api-platform_cache_key-value-maps.txt:124`). Second reading: it is presented as
  remediation advice derived from the documented propagation delay, not as a quotation,
  and no critical failure or rubric cell requires an agent to call it documented, so it
  cannot score a correct answer wrong. The advice itself is technically sound.
- Severity: n/a (borderline low, non-load-bearing)
- Evidence:
  - Primary quoted fact, verbatim and exact:
    `research/pages/api-platform_reference_policies_key-value-map-operations-policy.txt:411`
    "`PUT` … using `PUT` will only refresh the cache in the single runtime node that
    services the request. To refresh the cache in each distributed runtime node, use the
    `<ExpiryTimeInSecs>` element to specify refresh intervals for each node." This is
    character-for-character what medium.md:570-573 quotes.
  - The Management API scoping caveat, verbatim:
    same file `:425` "Updating a KVM with the Apigee UI or API does not reset the KVM
    cache." medium.md:578 quotes this correctly and draws the right conclusion (a
    Management API write has no single-node refresh to explain), matching medium.md:576-580.
  - No-flush / placeholder claims, verbatim: same file `:423` "There is no policy-level
    mechanism to manually flush the KVM cache, and there is no way to invalidate a
    cached entry across all runtime nodes from a single policy execution." and `:424`
    "Do not attempt to 'expire' a KVM value by issuing a `PUT` of a placeholder with a
    short `<ExpiryTimeInSecs>`. The placeholder value is written to the KVM permanently
    (KVM values have no server-side TTL)". Both match medium.md:592-595.
  - `private.` prefix claims, verbatim and twice-sourced: same file `:194` "If the
    `private.` attribute is not used, the KVM is still encrypted; however, the KVM
    information will appear decrypted in the Debug session and no exception will be
    thrown." and `:473` "If you do not use the `private.` prefix, the data retrieved from
    the KVM will appear in cleartext, in any Debug session you create." This supports
    medium.md:598-601 and the "Common incorrect answers" entry at medium.md:613-614, so
    the critical failure at medium.md:629 ("recommending debug output of a KVM value
    without flagging the `private.` prefix") cannot be tripped by a correct answer.
  - XML is real and correctly cased: `<ExpiryTimeInSecs>` is a direct child of
    `<KeyValueMapOperations>`, sibling to `<Scope>` and parent to `<Put>`
    (`…key-value-map-operations-policy.txt:32-43`, and again at `:235`). Default `300`,
    presence Optional, type Integer (`:395-399`). `<Put>`/`<Key>`/`<Parameter>`/`<Value>`
    all real (`:36-42`).
  - Default-expiry nuance the scenario gets right implicitly: "A value of 0 or -1, or
    excluding this element, means the default value of 300 seconds is used" (`:385`), which
    is why the verification at medium.md:605-607 asks to compare convergence against the
    *configured* value rather than a fixed 60.
  - Remediation/verification pairing holds: shortening `<ExpiryTimeInSecs>` narrows the
    per-node TTL that `:411` and `:407` describe, and polling every node for convergence
    time is the direct measurement of the behavior `:411` predicts. No gap.
  - No fault code is asserted anywhere in MED-05, so defect class 2 does not apply.
    Title "Key value map updates are not visible everywhere" describes the symptom, not
    the cause (the ticket at medium.md:547-549 still asks "Is the key-value map corrupt?",
    which is the actual discriminator). Difficulty "medium" is apt: the mechanism is
    one documented sentence plus a scoping trap.

---

### MED-06. Latency jumped and nobody knows which layer moved

- Verdict: DEFECT
- Defect: garbled sentence at medium.md:706-707. The "Common incorrect answers" entry
  reads "The absence of a deploy is not evidence of applause; it is the absence of one
  class of cause." "applause" is not a word that fits and appears nowhere else in the
  corpus (`rg -n applause scenarios/ research/ .agents/` returns exactly this one hit,
  medium.md:707). Almost certainly a corrupted word ("evidence" / "innocence" /
  "guilt"). It sits in the negative-example block, so it does not misstate the correct
  answer — it is a prose corruption, not a technical error — but it will read as noise to
  a grader and is trivially fixable.
- Severity: low
- Evidence:
  - The defect itself: scenarios/medium.md:706-707, quoted above. Sole occurrence in the
    repository; no source page contains the word.
  - The substantive claims all check out, which is why this is low and not higher:
  - `target.duration` is a real, documented flow variable with exactly the semantics
    MED-06 relies on: `research/pages/dbg_trace.txt:26` "`target.duration` is the target
    latency, or the amount of time, in milliseconds, that a request takes to be sent to
    and received from the target (calculated as the difference between
    `target.received.end.timestamp` and `target.sent.start.timestamp`)". The built-in
    filter example on the same line is `target.duration > 420 && client.duration > 1000`,
    i.e. the product already ships the exact separation-of-layers move the rubric demands
    ("Requires trace plus external measurement", medium.md:714).
  - "Apigee's own processing in the trace is small" is measurable from the same two
    variables (`client.duration` is client latency; the residual is gateway processing), so
    medium.md:679-680 is supportable rather than hand-waved.
  - Timeout faults referenced in Verification (medium.md:696-697, "no new timeout faults
    appear in API Monitoring") exist in the cited index:
    `research/pages/mon_fault-codes.txt:69` "Gateway APITimedOut | flow.APITimedOut" and
    `:78` "Gateway TimeoutWithTargetOrCallout | messaging.adaptors.http.flow.GatewayTimeout".
  - The claim that timeouts "configured against the old latency may now fire
    intermittently" (medium.md:690-691) is consistent with the above 504-family codes and
    with `research/pages/api-platform_troubleshoot_playbooks_504-target-read-timeout.txt:3751`
    "The `TARGET_READ_TIMEOUT` reason indicates that Apigee runtime did not receive a
    timely response from the target".
  - Unsupported-attribution check: MED-06 is marked `Origin: synthetic` (medium.md:649)
    and asserts no maintainer, issue, or doc says anything it does not. It does not quote
    a source for the step-naming remark at medium.md:674-675 ("Step names are
    customer-defined and differ between proxies") — I could not find a documented
    statement of trace step naming in `dbg_trace.txt`,
    `api-platform_debug_trace-overview.txt`, or the references. That is an unsourced
    assertion presented as background, but it is operationally harmless and, if anything,
    correct: trace steps are labeled by policy `name`, which is customer-chosen (the
    policy root attribute `name` is visible throughout
    `api-platform_reference_policies_key-value-map-operations-policy.txt:32`,
    `:230-231`). I am explicitly unsure whether this counts as a defect; I lean no,
    because it is advice about how to read a trace, not a claim about Apigee behavior.
  - Difficulty "medium" is right, arguably even generous: the discriminating measurement
    (external baseline) is the whole scenario, and the rubric's 0/2/4 ladder
    (medium.md:713-716) maps cleanly onto it. Title does not leak — it names the symptom
    and the ambiguity, not the layer.
  - Critical failures (medium.md:718-719, "recommending a timeout increase as the primary
    remedy; attributing cause without measurement") cannot be tripped by a correct answer;
    the resolution explicitly refuses both.

---

### MED-07. Deployment succeeds on hybrid but the runtime never applies it

- Verdict: DEFECT
- Defect: two problems, one substantive.

  (a) UNSATISFIABLE / CONTRADICTORY PREMISE — MED-07 makes sync authorization
  environment-scoped, and the API is organization-scoped. medium.md:769-771 says
  "Checking the org's sync authorization shows it was never configured **for this
  environment**", and medium.md:776 says the Synchronizer "has no permission to pull
  artifacts **for this environment**". But `setSyncAuthorization` is an organization-level
  call with no environment parameter:
  `research/scratch-pages/vfy-9376b7cea773043fea4e698066142e9d.txt:147` "`setSyncAuthorization`
  | POST /v1/{name=organizations/*}:setSyncAuthorization"; the `v1.organizations.environments`
  method table (`:743-759`) contains no sync-authorization method at all. A brand-new
  environment in an organization whose other environments work cannot be missing an
  authorization that is never per-environment. The ticket at medium.md:748-750 explicitly
  says "The other environments on the same cluster are fine" — so if the cause really were
  "sync auth was never set", nothing anywhere in that org would ever have synced and the
  existing environments would be equally dead. The premise as written cannot produce the
  stated 404-with-healthy-neighbours signature.

  (b) The scenario also stacks a second, independent cause it does not resolve: "the
  service account the Synchronizer runs as does not hold the Apigee Synchronizer Manager
  role" (medium.md:770-771). The role requirement is real and per-environment
  configurable — `research/pages/hybrid_latest_config-prop-ref.txt:1519`
  "`envs[].serviceAccountPaths.synchronizer` … Path to file on local system to a Google
  Service Account key with the Apigee Synchronizer Manager role." So a *new* environment
  wired to a *new/different* Synchronizer SA that lacks the role is a perfectly coherent
  environment-scoped cause. The scenario mixes that with the org-scoped
  `setSyncAuthorization` omission and labels the composite as environment-scoped. The
  remediation (medium.md:787-789, "Call `setSyncAuthorization` for the organization")
  only addresses half of the stated evidence.

- Severity: high
- Evidence:
  - Org scope, quoted above: `research/scratch-pages/vfy-9376b7cea773043fea4e698066142e9d.txt:147`
    and the absence of any sync method at `:743-759`. Same org scoping in the setup doc:
    `research/pages/hybrid_v1.17_synchronizer-access.txt:111`
    `"https://apigee.googleapis.com/v1/organizations/YOUR_ORG_NAME:setSyncAuthorization"`,
    and the companion `getSyncAuthorization` at `:186` is likewise
    `organizations/your_org_name:getSyncAuthorization`.
  - The contradiction, stated in the scenario itself: medium.md:748-750 "The other
    environments on the same cluster are fine." vs medium.md:769-770 "never configured for
    this environment". If `setSyncAuthorization` was never called for the org, the
    Synchronizer pulls nothing for *any* environment. The scenario's own remediation
    acknowledges this scope at medium.md:791-792 ("it affects the whole organization") and
    medium.md:800-801 ("confirm the pre-existing environments still serve, since the
    change is organization-wide") — which directly contradicts the "for this environment"
    framing in the evidence and resolution. The rewrite traded one inconsistency for
    another: the remediation is org-scoped and correct, the premise is env-scoped and
    cannot hold.
  - The role requirement IS documented, verbatim:
    `research/pages/hybrid_v1.17_synchronizer-access.txt:98` "**IMPORTANT:** Be sure that
    the service account name that you add to this API has the **Apigee Synchronizer
    Manager** role." Repeated at `:118` and `:154`, and independently required per
    environment at `hybrid_latest_config-prop-ref.txt:1519`. So the "Apigee Synchronizer
    Manager role" string in medium.md:771/780/788 is real.
  - The log-line marker IS documented, verbatim:
    `research/pages/hybrid_latest_runtime-logs.txt:74` "`hybrid-runtime Apigee-Timer-9 INFO
    RUNTIME-SYNC-SERVICE - RuntimeSyncServiceImpl.updateToVersion() : Switched to newer
    version 750 from version null` | The MP changed to a newer version of the configuration
    contract." and `:77` the 751-from-750 variant. medium.md:767-768 renders the pattern
    as "`Switched to newer version N from version M`", which matches the documented shape.
    So the diagnostic evidence at medium.md:767-769 is sound and the Verification at
    medium.md:796-798 ("the contract version line appearing in the runtime pod log, not
    the Management API response") is the right check.
  - The four-step decomposition is real but is NOT in the two pages MED-07 cites. Its
    source is `research/notes-round2.md:1193-1197` and
    `.agents/skills/apigee-support-core/references/hybrid.md:15-19` ("1. The revision was
    saved. 2. The Synchronizer pulled the contract. 3. The Message Processor applied it.
    4. The Watcher reported status."). The Watcher step is sourced at
    `research/notes-round2.md:815` "Watcher periodically executes task in the runtime
    cluster such as reconfiguring Ingress routes, checking ingress status for new proxy
    deployments, fetching deployment status from Message Processors and Ingress in order
    to report status to Management Plane."
  - CITATION DEFECT (in reply to the brief's specific question): the two References at
    medium.md:827-830 are `hybrid/latest/what-is-hybrid` and
    `api-platform/get-started/compare-apigee-products`. I grepped both cached pages for
    every load-bearing term — `setSyncAuthorization`, `Synchronizer Manager`,
    `Switched to newer version`, `Watcher` — and got **zero hits in both**. Those pages
    support only the weak framing ("the control plane and runtime plane are separate",
    `hybrid-what-is-hybrid.txt:40` "The Synchronizer fetches configuration data about an
    API environment from the management plane… This downloaded data is also called the
    *contract*"). So the earlier review's criticism of citation quality still stands in
    substance even though the *content* of MED-07 was rewritten correctly: the new
    Synchronizer/role thesis is factually right, but neither cited page contains the
    Synchronizer Manager role, the pod-log marker, or `setSyncAuthorization`. The correct
    citations are `hybrid/v1.17/synchronizer-access` and `hybrid/latest/runtime-logs`.
    The previous defect (an invented hybrid-vs-X shared-flow validation difference
    contradicting EASY-03) is genuinely gone — I confirmed MED-07 no longer mentions
    shared flows at all, and EASY-03 (`scenarios/easy.md:296-340`) is untouched and
    internally consistent on its own terms.
  - Critical-failure check (medium.md:822-823, "recommending a redeploy as the fix;
    treating a successful Management API call as proof the runtime applied the change"):
    these are safe — the premise defect above does not cause a correct answer to trip
    them, and the remediation is neither a redeploy nor a Management-API-only check.
  - Difficulty "medium" is defensible for the intended concept; the scenario becomes
    wrong rather than hard, which is why this is a high-severity correctness defect and
    not a difficulty problem.

---

### MED-08. Mutual TLS broke after a certificate authority renewal

- Verdict: OK
- Defect: n/a. I checked every element of the nine defect classes and found nothing that
  rises above a wording quibble.
- Severity: n/a
- Evidence:
  - The core claim is verbatim documented, and in both directions exactly as stated:
    `research/pages/api-platform_reference_api-proxy-configuration-reference.txt:458`
    "Apigee requires the `clientAuth` EKU to be present in client certificates for mTLS
    handshakes. Without this EKU, mTLS connections will fail for both northbound (client
    to Apigee) and southbound (Apigee to backend) traffic." That is precisely
    medium.md:872-874, including the two-directional failure that the ticket at
    medium.md:851-852 and the evidence at medium.md:856-857 rely on.
  - The CA-continuation premise is sourced too: same file `:456` "Public Certificate
    Authorities (CAs) are discontinuing the inclusion of the `clientAuth` Extended Key
    Usage (EKU) in latest publicly-trusted SSL/TLS certificates. This industry-wide
    change affects Apigee mutual TLS (mTLS) configurations". medium.md:845-846 and
    medium.md:868 track this faithfully. (Note the doc scopes the discontinuation to
    *publicly-trusted* certs; the ticket says "Our CA", implying a private CA. That is a
    scenario-side choice, and the diagnostic evidence at medium.md:867-868 supplies the
    fact that this CA dropped the EKU, so the premise stays satisfiable.)
  - `<SSLInfo>` / `ClientAuthEnabled` / `IgnoreValidationErrors` are all real and correctly
    cased: `api-platform_reference_api-proxy-configuration-reference.txt:468-471` defines
    `ClientAuthEnabled`, `KeyStore`, `KeyAlias`, `Enforce`, `IgnoreValidationErrors` under
    the TLS section; sample XML with `<ClientAuthEnabled>true</ClientAuthEnabled>` at
    `:544`. `api-platform_system-administration_options-configuring-tls.txt:25` and the
    table at `:46`/`:50` match. The scenario's only XML-ish references are element names
    and they all exist.
  - "Common incorrect answers" are all genuinely wrong answers, none state the correct
    one: re-uploading (medium.md:894-895) — the keystore already holds it;
    `IgnoreValidationErrors` (medium.md:897) — per
    `api-platform_reference_api-proxy-configuration-reference.txt:471` it "Indicates
    whether validation errors are ignored", i.e. chain/hostname validation, and it cannot
    conjure an absent EKU (also `options-configuring-tls.txt:50`: "If the backend system
    uses SNI and returns a cert with a subject Distinguished Name (DN) that does not
    match the hostname, there is no way to ignore the error"); truststore-for-the-CA
    (medium.md:899-900) — same CA, chain intact, so the truststore is already correct.
  - Remediation achieves Verification: reissue with `clientAuth` (medium.md:881) is
    exactly what makes "Confirm the EKU on the new certificate before deploying it
    anywhere. Then test northbound and southbound independently" (medium.md:889-890)
    possible, and testing both sides separately is warranted precisely because the
    documented failure is two-sided.
  - Unsupported-attribution check: MED-08 claims no maintainer or issue said anything it
    does not. The one external artifact it leans on is the blog post linked at
    `…api-proxy-configuration-reference.txt:458`
    ("Navigating the industry shift in client authentication for Apigee mTLS"); the
    scenario does not quote it, so there is no misquote risk.
  - Critical failure (medium.md:911, "recommending `IgnoreValidationErrors` as the fix")
  cannot be tripped by a correct answer, and it is reinforced rather than contradicted by
  the incorrect-answers list. No fault code is asserted, so defect class 2 is n/a.
  - Title leakage: "Mutual TLS broke after a certificate authority renewal" gives the
    trigger but not the EKU — the discriminator still has to be found. Difficulty
    "medium" is right: the evidence at medium.md:867-868 is decisive, but the agent must
    know to check EKU before chains or keystore state, and the rubric's
    "Checks truststore / Inspects certificate / Inspects the EKU extension specifically"
    ladder (medium.md:907) rewards exactly that ordering.

---

## Cross-cutting findings (MED-05–MED-08)

1. **Citation drift between scenario bodies and their own References lists (MED-07;
   latent in MED-05 and MED-08).** MED-07 is the confirmed instance: its two References
   (`hybrid/latest/what-is-hybrid`, `api-platform/get-started/compare-apigee-products`)
   contain **none** of the four load-bearing facts — `setSyncAuthorization`, "Apigee
   Synchronizer Manager", "Switched to newer version", "Watcher" — verified by zero grep
   hits in `research/pages/hybrid-what-is-hybrid.txt`,
   `research/pages/hybrid_what-is-hybrid.txt`, and
   `research/pages/api-platform_get-started_compare-apigee-products.txt`. The correct
   sources exist in the corpus and are uncited:
   `research/pages/hybrid_v1.17_synchronizer-access.txt:94-118` and
   `research/pages/hybrid_latest_runtime-logs.txt:74-77`. This is the same failure mode
   the earlier review flagged for MED-07 (content present in neither cited page), so the
   rewrite fixed the prose but not the sourcing. MED-05 and MED-08, by contrast, cite pages
   that do contain their quotes (`…key-value-map-operations-policy.txt:411/423/424/425`,
   `…api-proxy-configuration-reference.txt:458`) — I verified both — so MED-07 is the
   outlier, not a systemic pattern. Recommend a lint: for each scenario, grep its
   Reference URLs' cached pages for its distinctive identifiers.

2. **Scope drift on control-plane APIs (MED-07, and MED-05 by contrast).** MED-07 treats
   an organization-scoped API as environment-scoped. MED-05 gets the analogous scoping
   question exactly right — it insists on distinguishing the KeyValueMapOperations policy
   from the Management API path and cites
   `api-platform_reference_policies_key-value-map-operations-policy.txt:425` to do it
   (medium.md:576-580). The two scenarios therefore teach opposite habits about
   authorization scope. Worth an explicit note in MED-07's evaluation objectives, since the
   skill reference itself is careful about it (`hybrid.md:36` "If `setSyncAuthorization`
   was never called for an organization…").

3. **Prose corruption in a graded negative-example block (MED-06).** medium.md:707
   "not evidence of applause" is a single-token corruption with no corpus support. Not
   cross-scenario in my sample (one hit across `scenarios/`, `research/`, `.agents/`), but
   it sits inside a block a grader reads as authoritative, so a whole-file spell/word check
   over the "Common incorrect answers" sections is cheap insurance.

No defect is shared between MED-05, MED-06, and MED-08; items 1-3 above each involve
MED-07 or MED-06 alone, with item 1 generalizing as a process recommendation.

---

### MED-09 Bursts are rejected by a Quota policy that is enforcing correctly

- Verdict: DEFECT
- Defect: `medium.md:992-993` (turn-2 released evidence) states "Clients that retry
  **within the same window succeed**, because the counter resets on the window boundary
  rather than on the retry." Within the same window the counter is still at the limit, so
  the retry is rejected; only retries that land *after* the reset get through. This
  contradicts the scenario's own Ground-truth resolution at `medium.md:1002-1003`
  ("Retries landing after a counter reset is normal window behavior") and the Quota
  policy reference: `research/pages/api-platform_reference_policies_quota-policy.txt:10`
  — "Apigee rejects subsequent API calls and returns an error message **until the Quota
  counter automatically resets at the end of the specified time interval**". The clause
  as written describes under-counting, i.e. the opposite of the intended finding ("the
  quota is enforced accurately", `medium.md:991`).
- Severity: low (not medium: ground truth, remediation, verification and rubric are all
  consistent and unaffected, and the same paragraph opens with "the quota is enforced
  accurately", so the intended finding survives. The residual risk is that an agent
  repeats the evidence sentence and re-opens the miscounting hypothesis.)
- Evidence (everything else in MED-09 checks out):
  - `QuotaViolation` = HTTP 500:
    `research/pages/api-platform_reference_policies_quota-policy.txt:1197`
    ("`policies.ratelimit.QuotaViolation` | `500` | The quota limit was exceeded.");
    `.agents/skills/apigee-support-core/references/error-codes.md:46`.
  - `SpikeArrestViolation` = HTTP 429:
    `research/pages/api-platform_reference_policies_spike-arrest-policy.txt:679-683`;
    `references/error-codes.md:47`.
  - The 500-vs-429 duality MED-09 calls out is real, not conflated: the closing note on
    the Quota page says the system returns `429` —
    `...quota-policy.txt:1260` "When the rate of incoming requests exceeds the thresholds
    set by Quota or SpikeArrest policy, the system returns an HTTP status code `429 Too
    Many Requests`" — and the comparison table lists 429 for Quota —
    `api-platform_develop_comparing-quota-and-spike-arrest-policies.txt:22`. The
    "Not a critical failure" carve-out at `medium.md:1085-1086` is therefore accurate.
  - "Don't use the Quota policy to shield against overall traffic spikes ... use the
    SpikeArrest policy": `...quota-policy.txt:31`. Also `:66`.
  - SpikeArrest child elements `<DisplayName> <Identifier> <MessageWeight> <Rate>
    <UseEffectiveCount>`: `...spike-arrest-policy.txt:52` and syntax block `:72-77`.
    No `rateLimit` or `timeWindow` element exists anywhere on the page — the "Common
    incorrect answers" entry at `medium.md:1064-1065` is correct.
  - `<Rate>` format `int``ps` / `int``pm`, int must be a positive non-zero integer:
    `...spike-arrest-policy.txt:499-504`. `<Rate>` Required, Default n/a: `:466-469`
    (so "do not quote a documented default for `<Rate>`", `medium.md:1037-1038`, is right).
  - `<UseEffectiveCount>` default False, smoothing not supported for Apigee orgs, set to
    `true`: `...spike-arrest-policy.txt:597-601`, table `:625`. `true` = counts
    synchronized across MPs in a region + sliding window: `:578`.
  - Ordering SpikeArrest before Quota in the ProxyEndpoint Request PreFlow:
    `...comparing-quota-and-spike-arrest-policies.txt:21` ("If you use both SpikeArrest
    and Quota policies in the same proxy, SpikeArrest should always be attached before
    the Quota policy in the ProxyEndpoint Request PreFlow").
  - Shared-flow / multi-flow counting: nothing in MED-09 depends on it, and nothing in it
    is wrong about it. For the record, `...quota-policy.txt:118-130` documents that one
    policy used in several flows (or a shared flow) keeps a **single** counter updated by
    all instances, and calls that an anti-pattern (`:130`) — it multiplies *counting*
    toward the limit but does not change the fault code or status.
  - Difficulty "medium" is appropriate: the diagnosis requires holding two documented
    statuses apart and resisting a "Quota miscounts" reading.

---

### MED-10 Token works against one API and fails against another

- Verdict: DEFECT
- Defect: `medium.md:1137-1138` (turn-2 released evidence) — "A trace of the failing
  proxy shows `OAuthV2/VerifyAccessToken` **succeeded** at the validate step and the
  failure occurs at a later `SetOAuthV2Info` step." This contradicts both the documented
  behaviour and the scenario's own Ground-truth resolution at `medium.md:1142-1144`
  ("The token is expired, which is a single condition ... `VerifyAccessToken` surfaces
  401, while `GetOAuthV2Info` and `SetOAuthV2Info` surface 500 for an expired token").
  `research/pages/api-platform_reference_policies_oauthv2-policy.txt:1330` maps
  `steps.oauth.v2.access_token_expired` to `401`, "Thrown by operations:
  **VerifyAccessToken** InvalidateToken". There is no documented knob that lets an
  expired token pass `VerifyAccessToken` — `rg -i "IgnoreExpiry"` over the whole
  `research/` corpus returns nothing. So a 500 at `SetOAuthV2Info` caused by an expired
  token requires the request to have already passed `VerifyAccessToken`, which the same
  table says cannot happen for an expired token. Read literally the evidence makes the
  premise unsatisfiable; read charitably ("the fault is not at the VerifyAccessToken
  step") it makes the ground truth unreachable as written.
- Severity: medium
- Evidence (everything else in MED-10 checks out):
  - 401 for expired token via VerifyAccessToken: `...oauthv2-policy.txt:1330`;
    `references/error-codes.md:154` (which correctly flags the 500/401 **CONFLICT**
    across the three pages).
  - 500 for expired token via GetOAuthV2Info:
    `research/pages/api-platform_reference_policies_get-oauth-v2-info-policy.txt:451`
    ("`steps.oauth.v2.access_token_expired` | `500`").
  - 500 for expired token via SetOAuthV2Info:
    `research/pages/api-platform_reference_policies_set-oauth-v2-info-policy.txt:193`.
  - `invalid_client` (401) vs `InvalidClientIdentifier` (500) split on `<GenerateResponse>`
    for the same condition, with the doc's own advice to catch both in fault rules —
    exactly what `medium.md:1155-1156` claims:
    `...oauthv2-policy.txt:1339` ("`<GenerateResponse>` ... set to **true**"), `:1343`
    ("set to **false**"), both carrying "It is recommended that you change existing fault
    rule conditions to catch both the invalid_client and InvalidClientIdentifier names",
    and the documented condition at `:1461`.
  - "Key on `errorcode` rather than status" is the documented best practice:
    `...oauthv2-policy.txt:1421`.
  - Reference "OAuth HTTP status codes, deprecated but informative" is accurate:
    `research/pages/api-platform_reference_policies_oauth-http-status-code-reference.txt:6`
    ("**This topic is deprecated.**").
  - No critical-failure risk from the wording above: an agent that correctly names which
    policy produced which status cannot trip
    `medium.md:1182-1183` ("recommending escalation as a platform bug without checking
    which policy produced the status"). An agent that instead flags the
    VerifyAccessToken/expired-token contradiction is answering the evidence correctly and
    would most likely be docked on "Technical correctness" — the defect mis-scores, it
    does not mis-gate.
  - Difficulty "medium" is right for the concept; the evidence defect is what needs fixing.

---

### MED-11 Everything works in test and fails in production

- Verdict: OK
- Defect: n/a
- Severity: n/a
- Evidence:
  - Every element and attribute in the diagnostic-evidence policy is real, with exact
    capitalization: `research/pages/api-platform_reference_policies_key-value-map-operations-policy.txt:32-38`
    (`<KeyValueMapOperations ... name="FooKVM" mapIdentifier="FooKVM">` with
    `<Scope>environment</Scope>`, `<Get assignTo="foo_variable" index="2">` and
    `<Key><Parameter>FooKey_1</Parameter></Key>`); `mapIdentifier` attribute documented at
    `:287` and `:283`; `<Get>` attributes `assignTo` (Required) and `index` (Optional,
    1-based) at `:452-453`; `private.` prefix on `assignTo` is the documented convention
    for KVM values (`:473`) and is required for encrypted KVMs
    (`research/pages/api-platform_troubleshoot_policies_runtime_key-value-map-runtime-errors.txt:141`).
  - "`prod` has no `orders.timeout` key at all ... that variable is never assigned" is a
    fair inference from the element's own description —
    `...key-value-map-operations-policy.txt:430` "Retrieves the value for the key
    specified" and `:432` "Apigee decrypts the stored data and assigns it to a variable in
    the message context". Caveat, not a defect: the corpus documents **no** error for a
    missing key in `<Get>` — the KVM runtime-error page lists only
    `steps.keyvaluemapoperations.UnsupportedOperationException` (empty `mapIdentifier`) and
    `SetVariableFailed` — so "missing key ⇒ no assignment, no fault" is silent-by-default
    behaviour rather than a documented guarantee. The scenario's own reasoning is stated
    accurately and does not over-claim a fault code.
  - Environment scoping claim is documented:
    `research/pages/api-platform_cache_key-value-maps.txt:39` (Environment scope: "you may
    want API proxies deployed in the `prod` environment to not have access to KVMs in the
    `test` environment. If you want the same KVM keys to be available in production,
    create a parallel KVM scoped to the `prod` environment"), and `:40` (Organization
    scope is the only cross-environment one). The second reference URL
    (`.../fundamentals/environments-overview`) is a real cached page
    (`research/pages/api-platform_fundamentals_environments-overview.txt`).
  - Direction ("the failing environment is the one missing the key") is consistent
    throughout: `medium.md:1232-1234`, `:1257-1262`, `:1298-1300`, and the critical-failure
    list at `:1318-1319` correctly forbids blaming the well-formed `30`.
  - Remediation achieves Verification: both offered fixes (populate the entry through a
    managed path, or give the policy a default) make "the same request behaves identically
    in both environments", `medium.md:1286-1290`.
  - No self-contradiction, no invented element, no misattributed code, and no critical
    failure a correct answer could trip (`medium.md:1318-1319`, `:1321-1324`).

---

### MED-12 Service callout times out and takes the request with it

- Verdict: DEFECT
- Defect: `medium.md:1346-1347` (Scenario metadata → Evaluation objectives) —
  "distinguish the callout's own timeout from the request target's timeout; **both
  present as a 500** with different fixes". The request-target timeout does not present
  as a 500:
  `research/pages/api-platform_reference_endpoint-properties-reference.txt:85` — "If a
  timeout happens while writing the HTTP request or reading the HTTP response, `504
  Gateway Timeout` is returned" (and `:276` for the same condition under
  `io.timeout.millis`); `research/pages/api-platform_troubleshoot_playbooks_504-target-read-timeout.txt:3746`
  — "This issue appears as a Gateway Timeout error with HTTP status `504`", with body
  `"errorcode":"messaging.adaptors.http.flow.GatewayTimeout","reason":"TARGET_READ_TIMEOUT"`
  (`:3762`). A target *connect* timeout is 503
  (`...endpoint-properties-reference.txt:68`). The contrast the scenario is actually
  drawing (callout `<Timeout>` → 500, target timeout → 504) is the useful one and is
  stated correctly in the body; the "both 500" phrasing is simply wrong.
- Severity: medium
- Evidence (the scenario body checks out):
  - ServiceCallout `<Timeout>` expiry → HTTP 500, policy fails, proxy enters error
    state, verbatim from `research/pages/api-platform_reference_policies_service-callout-policy.txt:416`:
    "If the ServiceCallout hits a timeout, an HTTP 500 is returned, the policy fails, and
    the API proxy goes into an error state, as described in Handling faults." Corroborated
    by `research/pages/api-platform_fundamentals_fault-handling.txt:83` ("enters an error
    state, and returns an error message to the client app") and `:435` (`continueOnError`
    is what stops the request dying). The title's "takes the request with it" is therefore
    correct for the default `continueOnError="false"`.
  - No 504 misattribution inside the scenario: MED-12 nowhere claims a callout timeout
    returns 504, and it never names `io.timeout.millis` / `api.timeout` incorrectly.
  - Documented default for `<Timeout>` is 55000 ms (55 s): `...service-callout-policy.txt:428`.
    MED-12 makes **no** default claim (it says only "a configured timeout", and 200 ms in
    the trace, `medium.md:1357`, `:1367`), so there is nothing to fault here — but note the
    scenario correctly avoids quoting a default.
  - `<Timeout>` "cannot be set dynamically at runtime": `...service-callout-policy.txt:416`.
    MED-12 does not contradict this.
  - Remediation is achievable: a non-blocking callout is documented — omit `<Response>`
    and "the API proxy does not wait for a response"
    (`...service-callout-policy.txt:398`); a fault rule degrades gracefully
    (`...service-callout-policy.txt:1260-1273`; `...fault-handling.txt:132`).
  - "Raising the callout timeout without a fault rule" as a wrong answer
    (`medium.md:1399-1400`) is consistent with the remediation, which also lists raising
    the timeout within a latency budget but pairs it with fault handling
    (`medium.md:1384-1389`) — so a correct answer that raises the timeout *and* adds fault
    handling does not trip `medium.md:1416-1417`. No critical-failure risk.
  - Severity is medium, not high, because the wrong claim lives in `Scenario metadata`,
    which `tests/make_packets.py:45-48` releases to neither the agent nor the grader; the
    body of the scenario and the rubric are unaffected.
  - Noted ambiguity, not scored as a defect: the ticket says "We raised **its** timeout and
    it did not help" (`medium.md:1352-1353`) and the resolution reads that as the
    *enrichment service's* timeout, not the callout's (`medium.md:1379-1380`). Both
    readings are grammatically available; the resolution explicitly picks one and the
    trace (`<Timeout>` of 200 ms still configured, `medium.md:1367`) is consistent with it.
    An agent that reads "its" as the callout's timeout and says so is not marked wrong by
    any rubric row or critical failure.
  - Difficulty "medium" is appropriate.

---

## Cross-cutting findings (MED-09–MED-12)

1. Turn-2 "Diagnostic evidence" contradicts the "Ground-truth resolution" in two of the
   four scenarios, and in both cases the contradiction is the kind the corpus settles
   against the evidence. MED-09 (`medium.md:992-993`) asserts that a retry *within the same
   quota window* succeeds, which `...quota-policy.txt:10` and the scenario's own
   `medium.md:1002-1003` deny. MED-10 (`medium.md:1137-1138`) asserts that `VerifyAccessToken`
   *succeeded* on an expired token, which `...oauthv2-policy.txt:1330` denies. Because
   `tests/make_packets.py:46` releases this section verbatim at turn 2, both are
   agent-visible and can steer a correct answer toward a wrong diagnosis. The two other
   scenarios in this block do not have the problem, so this is not a systematic generator
   bug — but it is the most common defect class in this range and worth a check on the
   other MED entries.

2. Both MED-09 and MED-10 are graded on a two-status distinction where the corpus itself is
   internally inconsistent, and both scenarios handle it correctly by splitting the
   difference explicitly (MED-09 `medium.md:1085-1090`, MED-10 `references/error-codes.md:154`
   CONFLICT rows). No defect; flagged so the pattern is not "fixed" away. The MED-09
   carve-out ("not a critical failure: raising the 500 versus 429 question") is verified
   accurate against `...quota-policy.txt:1197` and `:1260`.

3. MED-12's only defect is in non-released `Scenario metadata`. MED-11 has none. So the
   four-scenario block is 2 DEFECT / 2 OK, with no defect that crosses scenario boundaries
   other than the evidence-contradiction pattern in (1).

---

### MED-13. Two conditions produce the same error code

- Verdict: DEFECT
- Defect: The title and the metadata promise a two-cause / trace-step discriminator exercise that
  the scenario body never supplies. `scenarios/medium.md:1407` titles it "Two conditions produce
  the same error code", and `scenarios/medium.md:1418-1419` states the objective as "one error
  code, several causes; **the trace step is the discriminator**, not the code". But the body
  contains exactly **one** condition (a missing `items` query parameter, `medium.md:1448-1449`,
  resolved at `medium.md:1453-1455`) and contains **no trace step at all**. The discriminator the
  body actually uses is the fault string (`medium.md:1434-1438`: "the fault string is where the
  detail lives. The agent should ask for the fault string"), which directly contradicts the
  metadata line. The rubric (`medium.md:1491-1492`) is keyed to the body ("Asks for fault string",
  "Identifies the null dereference"), so it contradicts the title instead.
  Secondary, lower-severity fidelity issue: `medium.md:1442-1446` presents
  `TypeError: Cannot read property 'length' of undefined` as "The full fault string". The only
  documented fault string shape for this code is the wrapped form, and the only documented
  example uses different inner wording — `research/pages/api-platform_troubleshoot_policies_runtime_javascript-runtime-errors.txt:537`:
  `"Execution of ParseJSONResponse failed with error: Javascript runtime error: \"TypeError: Cannot read property \"length\" **from** undefined. (ParseJSONResponse.js:7)\""`
  (repeated at lines 547, 554, 611). The scenario drops the wrapper (which is where the policy
  name and the `file:line` live, `…javascript-runtime-errors.txt:547`: "You can find all this
  information in the `faultstring` element") and uses "of undefined" rather than the documented
  "from undefined". Both readings are possible: Rhino's message text does vary by engine version,
  so the inner text is defensible, but calling the bare `TypeError` the "full" fault string
  understates what the scenario is simultaneously training the agent to ask for.
- Severity: medium
- Evidence:
  - `steps.javascript.ScriptExecutionFailed` is real and HTTP 500 —
    `research/pages/api-platform_reference_policies_javascript-policy.txt:404` ("The `JavaScript`
    policy can throw many different types of `ScriptExecutionFailed` errors…", status `500`);
    mirrored in `.agents/skills/apigee-support-core/references/error-codes.md:66` (HTTP `500`).
    The scenario's "family of errors" framing is correct.
  - "check the fault string for details" is documented —
    `…javascript-policy.txt:405` and `:406` ("See the fault string for details.");
    `…javascript-policy.txt:433` ("Do not rely on the text in the `faultstring`, because it could
    change") supports both the remediation line `medium.md:1470-1471` and the critical failure at
    `medium.md:1496`. No critical-failure trap here: the documented fault rule example at
    `…javascript-policy.txt:460` matches on `fault.name`, not `faultstring`, so a correct answer
    cannot trip it.
  - The remediation snippet is valid: `context.getVariable("request.queryparam.items")` uses
    documented API and variable form — `research/pages/api-platform_reference_javascript-object-model.txt:883-894`
    (`context.getVariable()`) and `:1142` (`context.getVariable("request.queryparam.user")`).
  - The "JavaScript timeout" incorrect answer is harmless: the JavaScript policy element
    reference has no timeout element at all (`…javascript-policy.txt` element headings at lines
    203, 220, 242, 272, 294, 332 — DisplayName, IncludeURL, Property, ResourceURL, Source,
    SSLInfo), so it is wrong twice over, which is fine for a distractor.
  - No fault code is misattributed and no HTTP status is stated wrongly. References cited at
    `medium.md:1500-1503` both exist in the corpus
    (`api-platform_reference_policies_javascript-policy.txt`,
    `api-platform_fundamentals_fault-handling.txt`).
  - Defect class 7 (unsatisfiable premise) is **not** raised: the stated evidence can produce the
    stated fault, and the ground truth does not contradict the diagnostic evidence. The defect is
    confined to title/metadata vs body/rubric, plus the fault-string rendering.

---

### MED-14. A revoked token still works for a few minutes

- Verdict: DEFECT
- Defect: The "Correct remediation" is unsupported by the corpus, contradicts the scenario's own
  premise, and does not achieve the stated goal ("For immediate lockout",
  `scenarios/medium.md:1554-1555`: "revoke at the identity provider as well if one is in the path,
  so the credential is rejected upstream rather than relying on the cache expiring"). Three
  problems:
  (a) **It cannot work for this ticket.** The premise is a token "invalidated through the OAuthV2
  `InvalidateToken` operation" (`medium.md:1530`). Per
  `research/pages/api-platform_security_oauth_validating-and-invalidating-access-tokens.txt:18`,
  "You can revoke only opaque OAuth tokens … that have been **generated by the OAuthV2 policy**",
  and `:22` attributes revocation to the OAuthV2 `InvalidateToken` operation. Apigee is the token
  store, so there is no upstream IdP holding this credential.
  (b) **Even if one existed, it would not shorten the window.** The documented behaviour is that
  `OAuthV2/VerifyAccessToken` serves the cached lookup result —
  `research/pages/api-platform_reference_policies_oauthv2-policy.txt:440`: "Subsequent invocations
  of `OAuthV2/VerifyAccessToken` until the TTL elapses will read the in-memory cached result".
  Revoking anything upstream does not evict that entry.
  (c) **The documented lever is omitted, and the rubric penalises it.** The corpus documents
  exactly the control for this case —
  `research/pages/api-platform_reference_policies_oauthv2-policy.txt:442`: "The default TTL for
  the access token cache is 180 seconds. This element allows you to reduce that TTL … One scenario
  in which this would make sense is if you sometimes revoke tokens, and you want to reduce the
  time window during which Apigee will continue to treat revoked tokens as valid." Supported range
  1–180 seconds (`:444`), `VerifyAccessToken` only (`:440`). The scenario never mentions
  `<CacheExpiryInSeconds>`, yet the rubric anchors the top score on the unsupported action —
  `medium.md:1581`: "Quality of next step | Cache flush | Document window | **Offers upstream
  revocation for immediate lockout**". A technically correct answer recommending the documented
  1–180 s TTL reduction matches none of the three anchors and can be scored at or near the 0
  anchor ("Cache flush"), which is defect class 9 (a correct answer tripping a listed penalty) as
  well as class 4.
  Secondary issue: the Verification step `medium.md:1562-1563` — "Repeat to confirm the window is
  consistently three minutes rather than occasionally longer" — is in tension with
  `research/pages/api-platform_reference_policies_oauthv2-policy.txt:518`: "Apigee keeps the
  following entities in cache for a **minimum** of 180 seconds **after the entities are
  accessed**", i.e. sustained polling refreshes the clock. The headline warning is an upper bound
  ("may still succeed for up to three minutes",
  `…validating-and-invalidating-access-tokens.txt:10`), so "rather than occasionally longer" is
  not guaranteed by the sources.
- Severity: high
- Evidence:
  - The three-minute / 180-second revocation window is documented, verbatim, three times:
    `research/pages/api-platform_reference_policies_oauthv2-policy.txt:710` (on the
    `InvalidateToken` row: "OAuth tokens are cached for three minutes (180 seconds); therefore, a
    revoked token may still succeed for up to three minutes, until its cache limit expires");
    `research/pages/api-platform_reference_policies_revoke-oauth-v2-policy.txt:14`;
    `research/pages/api-platform_security_oauth_validating-and-invalidating-access-tokens.txt:10`
    and `:29`. Restated in
    `.agents/skills/apigee-support-core/references/security.md:28-30` and sourced in
    `research/notes-security.md:108`. The scenario's core number is real.
  - `InvalidateToken` is a real operation —
    `research/pages/api-platform_reference_policies_oauthv2-policy.txt:710`;
    `…validating-and-invalidating-access-tokens.txt:22-23`.
  - The scenario cites **no fault code at all** (`medium.md:1507-1591`), so defect class 2 cannot
  arise. The HTTP/trace wording is clean.
  - The "Common incorrect answer" "There is no documented supported way to force-flush token
  caches across runtimes" (`medium.md:1572-1573`) is **correct**: the Caches API and
  `InvalidateCache` are scoped to policy caches —
    `research/pages/api-platform_cache_cache-internals.txt:6` (PopulateCache/LookupCache/
    InvalidateCache/ResponseCache) and `:12` ("List and delete are the only cache API operations
    available"); `research/pages/api-platform_reference_policies_invalidate-cache-policy.txt:10-16`.
    No page in the corpus documents flushing the OAuth token cache.
  - The single documented reference at `medium.md:1589-1590` does carry the three-minute warning,
    so the citation is honest — the defect is the remediation, not the sourcing.
  - Difficulty: defensible as medium, but the answer is a verbatim warning adjacent to
    `InvalidateToken` on the cited page, so it sits closer to easy. Low-severity observation.

---

### MED-15. A Java callout fails only on some requests

- Verdict: OK
- Defect: n/a
- Severity: n/a
- Evidence (each load-bearing claim, cited):
  - **The previously recorded critical defect is fixed.** The earlier review flagged MED-15 as
    "unsatisfiable as written" because it fired a deployment-only error at request time while its
    own evidence said the deployment succeeded. The current text no longer does this. Initial
    evidence `scenarios/medium.md:1618-1622` now shows `"errorcode":"steps.javacallout.ExecutionError"`
    — the **runtime** code, not a deployment name — alongside "Deployment succeeded", and the
    Expected investigation `medium.md:1629-1630` uses that success to rule the deployment table
    out. Deployment-only names now appear only in the resolution (`medium.md:1651-1655`) and in
    the "Common incorrect answers" (`medium.md:1686-1687`), correctly labelled as deployment
    errors.
  - Runtime table is exactly one row, with the stated code, status and cause —
    `research/pages/api-platform_reference_policies_java-callout-policy.txt:216-222`:
    "| `steps.javacallout.ExecutionError` | `500` | Occurs when Java code throws an exception or
    returns null during the execution of a `JavaCallout policy`. |". The scenario's ground truth
    `medium.md:1643-1645` quotes this accurately, and "That is the whole runtime error table"
    (`medium.md:1645`) is correct.
  - The prefix discrepancy the scenario flags is real and precisely located —
    `research/pages/api-platform_reference_policies_java-callout-policy.txt:248-263` (Example error
    response) carries `"errorcode":"javacallout.ExecutionError"` without the `steps.` prefix, at
    line 259, while line 222 and
    `.agents/skills/apigee-support-core/references/error-codes.md:65` both carry
    `steps.javacallout.ExecutionError`. The scenario states this correctly at `medium.md:1646-1649`.
    (Third variant not mentioned, but its omission is not a false claim:
    `research/pages/java-callout-runtime-errors.txt:26-33` shows a response body with
    `flow.execution.ExecutionReturnedFailure`, and `research/notes-troubleshooting.md:487-513`
    documents that mismatch.)
  - Every deployment error name cited exists, in the deployment table, with no HTTP status —
    `…java-callout-policy.txt:224-236` ("These errors can occur when the proxy containing the policy
    is deployed.", HTTP status `N/A` for all rows): `ResourceDoesNotExist` (:230),
    `JavaCalloutInstantiationFailed` (:231), `JavaClassNotFoundInJavaResource` (:233),
    `JavaClassDefinitionNotFound` (:234), `NoAppropriateConstructor` (:235), `NoResourceForURL`
    (:236). The scenario lists six of the seven (it omits `IncompatibleJavaVersion`, :232) but
    only claims those six "are all in the deployment error table", which is true; the critical
    failure at `medium.md:1703-1705` is phrased generically so the omission creates no trap.
  - The fault string is quoted from the same documented example —
    `…java-callout-policy.txt:257`: `"faultstring":"Failed to execute JavaCallout. [policy_name]"`,
    matching `medium.md:1624-1625`.
  - "The fault code and the generic faultstring do not carry the exception" is documented —
    `research/pages/java-callout-runtime-errors.txt:59` ("Capture and store the Java exception in a
    flow variable") and `:69` ("a stack trace is available in the `JAVA_STACKTRACE` variable. The
    stack trace lists the actual exception and the Java source file and line number"), supporting
    the remediation `medium.md:1666-1667`.
  - Packaging/duplicate-JAR remediation is quoted almost verbatim —
    `…java-callout-policy.txt:302` ("Place the JAR in an API proxy under `/resources/java`") and
    `:318-323` ("Having multiple copies of same JAR deployed can cause non-deterministic behavior
    at runtime because of potential ClassLoader conflicts"), matching `medium.md:1673-1675`.
  - Product applicability is correct — `…java-callout-policy.txt:3`: "This page applies to
    **Apigee** and **Apigee hybrid**", matching `medium.md:1602`.
  - Critical failures (`medium.md:1703-1705`) are sound and not trip-able by a correct answer: the
    documented duplicate-JAR/ClassLoader guidance the scenario itself endorses
    (`medium.md:1673-1675`) names no deployment error name, so it does not trigger "naming a
    deployment error name as the runtime cause".
  - Non-blocking observations (not defects, recorded for transparency):
    (i) `medium.md:1672` frames the duplicate-JAR guidance as belonging "to the deployment table",
    but that sentence actually comes from "Usage notes and best practices"
    (`…java-callout-policy.txt:314-323`) and describes *runtime* non-determinism — a minor
    attribution slip that does not change any answer.
    (ii) The narrative mechanism at `medium.md:1636-1639` (a thread-local initialised by the first
    call) explains first-succeeds/rest-fail but not the hourly periodicity asserted at
    `medium.md:1613-1614`. This is scenario fiction about customer code, not a corpus claim, and
    no cached page documents callout statefulness, so it is not a documented-accuracy defect.
    (iii) Difficulty: the fault code is handed to the agent in the evidence
    (`medium.md:1620-1622`), leaving a documentation lookup plus a deploy-vs-runtime
    classification. Reasonable for medium, arguably easy.

---

## Cross-cutting findings (MED-13–MED-15)

- **No XML anywhere in this batch.** MED-13, MED-14 and MED-15 contain no policy configuration
  snippets, so the largest defect class in this audit family is untestable here. MED-15's
  remediation names only documented path facts (`/resources/java`, single JAR copy), verified at
  `research/pages/api-platform_reference_policies_java-callout-policy.txt:302` and `:318-323`.
- **The previously flagged MED-15 deploy-vs-runtime conflation is resolved.** MED-15 is now the
  cleanest of the three: its runtime code, HTTP status, cause wording, fault string and packaging
  guidance all trace to `research/pages/api-platform_reference_policies_java-callout-policy.txt`.
  The MED-15 critical failure list is precise enough that no correct answer trips it.
- **Shared pattern across MED-13 and MED-14: the documented lever is missing from the remediation
  while the rubric rewards something else.** MED-14 omits the documented `<CacheExpiryInSeconds>`
  window-reducer (`research/pages/api-platform_reference_policies_oauthv2-policy.txt:442`) and
  anchors its top rubric score on an unsupported upstream action (`scenarios/medium.md:1581`).
  MED-13 omits the documented fault-string shape that carries the policy name and `file:line`
  (`research/pages/api-platform_troubleshoot_policies_runtime_javascript-runtime-errors.txt:547`)
  while training the agent to request the fault string. In both cases the scenario is
  technically defensible line-by-line but mis-scores the answer a documentation-first agent would
  give.
- **MED-13 and MED-14 both have headline/metadata statements their bodies do not deliver**
  (`medium.md:1407` / `:1418-1419` versus the single-cause body; `medium.md:1562-1563` demanding a
  stable three-minute window against a documented 180 s *minimum* per access at
  `research/pages/api-platform_reference_policies_oauthv2-policy.txt:518`). MED-15 does not share
  this problem.

---

### MED-16 The OAuth error names a missing parameter, but the token request never reached the token endpoint

- Verdict: DEFECT
- Defect: Two findings.
  1. **Title leakage (medium.md:1716).** The title states the ground-truth mechanism verbatim. The scenario's "Ground-truth resolution" (medium.md:1769-1772) reads "The token request is being served by the authorization-code flow because of how the proxy was deployed." The title already tells the agent the token request "never reached the token endpoint", which is the single inference the scenario is built around. The remaining work (deployment vs proxy base path, the redeploy) is procedural, not diagnostic.
  2. **Fault code not in the generated index (low; per instruction, reported separately).** `steps.oauth.v2.InvalidRequest` is genuinely documented but absent from `references/error-codes.md`, so medium.md:1754 violates the file-level rule at medium.md:13-15 ("Do not add codes that are not in that file"). Unlike the precedent at medium.md:4794-4798, MED-16 does not disclose the absence.
- Severity: medium (driven by finding 1; finding 2 is low on its own)
- Evidence:

  **Fault code `steps.oauth.v2.InvalidRequest`**
  - Documented in `research/pages`: **YES** — `research/pages/api-platform_reference_policies_oauthv2-policy.txt:1340`:
    `| steps.oauth.v2.InvalidRequest | 400 | This error name is used for multiple different kinds of errors, typically for missing or incorrect parameters sent in the request. If <GenerateResponse> is set to false , use fault variables (described below) to retrieve details about the error, such as the fault name and cause. | GenerateAccessToken GenerateAuthorizationCode GenerateAccessTokenImplicitGrant RefreshAccessToken |`
  - Present in `references/error-codes.md`: **NO**. The file contains exactly 14 `steps.oauth.v2.` rows (error-codes.md:136-147); a case-insensitive search for `invalidrequest` across all of `references/*.md` returns nothing. The index omission is a parser artifact: the OAuthV2 page's error tables are unbackticked pipe tables (oauthv2-policy.txt:1328-1347) that `build_error_index.py` evidently does not ingest, the same way MED-15's `steps.javacallout.ExecutionError` is indexed.
  - HTTP status 400: **correct** (line 1340). Runtime vs deployment: **correct** — it sits under `### Runtime errors` at oauthv2-policy.txt:1324, not the deployment table.
  - MED-16's quote is accurate. medium.md:1755-1756 quotes "used for multiple different kinds of errors, typically for missing or incorrect parameters sent in the request"; the source line 1340 reads "This error name is used for multiple different kinds of errors, typically for missing or incorrect parameters sent in the request."
  - MED-16's "The individual messages are not enumerated in the policy reference" (medium.md:1756-1757) is **correct**: the string `missing a required parameter` appears nowhere in `research/pages/`. The table enumerates only fault-level causes.
  - MED-16 does not confuse it with the neighbouring `steps.oauth.v2.MissingParameter` (oauthv2-policy.txt:1346, HTTP 500, "The response type is token, but no grant types are specified"). Using the wrong one would have been a real defect; it is not used.

  **Flow conditions (no invented XML)**
  - `<Condition>proxy.pathsuffix == "/oauth/authorizationcode"</Condition>` — `research/pages/api-platform_security_oauth_oauth-v2-policy-authorization-code-grant-type.txt:135`.
  - `<Condition>proxy.pathsuffix == "/oauth/accesstoken"</Condition>` — same file, line 145.
  - `<Condition>proxy.pathsuffix == "/oauth/authorize"</Condition>` — same file, line 124.
  - `proxy.pathsuffix` is a documented flow variable: `research/pages/vr2.txt:376`. MED-16 uses exact element name, exact capitalization, exact pathsuffix values. No XML defect.

  **Attribution to api-platform-samples#7 — every attributed element is in the thread**
  - Error text: `research/issues/apigee_api-platform-samples-7.txt:31` and `:89` — `{ErrorCode : "invalid_request", Error :"The request is missing a required parameter : response_type"}`. Matches medium.md:1736-1737 exactly.
  - Cascade: issue:164-168 — "After adding response_type, got: ... missing a required parameter : client_id / After adding client_id, got: ... Invalid redirection uri". Matches medium.md:1750-1752 precisely, including the ordering.
  - Wrong-flow classification: issue:272 (baskaran-md) — "your request to accesstoken ... is wrongly getting classified as authorization code request, that is when you will see the error message you have specified". This is the ground truth at medium.md:1769-1770.
  - Deployment, not bundle: issue:276 — "Checked the deployments. It was not deployed properly. Fixed it."
  - Deployment base path, UI, and `/` default: issue:284 — "There is a notion of deployment basepath apart from the proxy basepath which is provided in the proxy. You cannot set that deployment basepath from the UI. However, if its not set, it defaults to '/'." This matches medium.md:1781-1782 verbatim, and the undeploy/redeploy fix at issue:284 matches medium.md:1779.
  - "closed as fixed" (medium.md:1725): issue:3 `STATE: closed state_reason: completed`; issue:276/279 maintainer "Fixed it" / reporter "It works for me now." Supported.
  - Note (not a defect): the deployment-base-path facts are sourced **only** from a CONTRIBUTOR comment in the 2013 thread. They are not in any `research/pages` doc — `api-platform_deploy_ui-deploy-overview.txt:67` mentions only a "base path conflicts" yellow-triangle icon. MED-16 presents them as platform facts without attribution. Given the stated origin, acceptable, but the docs do not corroborate.

  **Other defect classes checked, no finding**
  - Self-contradiction: none. The "Common incorrect answers" entry "Adding `response_type=code` to the token request" (medium.md:1795) is genuinely incorrect per the ground truth, even though a *maintainer* recommended exactly that at issue:95-97. MED-16 correctly refuses to treat the maintainer's guess as the answer.
  - Remediation vs verification: medium.md:1779 (match deployment base path to proxy base path) does produce what medium.md:1789-1791 demands (token returns a token, authorize still returns a code).
  - Unsatisfiable premise: none. The cascade plus a trace showing entry into the `/oauth/authorizationcode` flow fully produces the stated fault.
  - Critical failures: "recommending adding `response_type` or `client_id` to the token request; asserting the OAuth policy is misconfigured" (medium.md:1814-1815) cannot be tripped by a technically correct answer. Sound.
  - Difficulty: low-to-medium as written, partly because of the title leak. Note for calibration.

---

### MED-17 The deploy tool says "Deployment failed" and the Management API says the deployment worked

- Verdict: OK
- Defect: n/a
- Severity: n/a
- Evidence:

  **Fault codes named: none.** MED-17 names no Apigee fault code. The only quoted strings are the Maven plugin's own `MojoExecutionException` message and two log lines. Nothing to check against `research/pages` or `error-codes.md`.

  **The message is tool-authored, not Apigee-authored (medium.md:1858-1861)**
  - `research/issues/apigee_apigee-deploy-maven-plugin-213.txt:27` — `throw new MojoExecutionException("Deployment failed: Bundle did not activate within expected time. Please check deployment status manually before trying again");` inside `RestClient.java`. Verbatim match with medium.md:1846-1847 and medium.md:1859-1860.

  **"waits a fixed interval, then makes a follow-up call ... treats a not-yet-set deployed revision as a failure" (medium.md:1875-1876)**
  - Source code quoted in-thread at issue:15-34: `Thread.sleep(10L)` then `final Long deployedRevision = this.getDeployedRevision(bundle);` then `if (!bundle.getRevision().equals(deployedRevision)) ... throw new MojoExecutionException(...)`.
  - Maintainer's own description, issue:134 — "That Thread.sleep(10) is only when the state in the deployment response is not equal to 'deployed', then the plugin makes another call to get the deployment details. And in that call, if the deployed revision is not set, then it fails with that error". Exact match to medium.md:1875-1876.

  **Maintainer's quoted position (medium.md:1878-1880)**
  - issue:39 — "you can ignore that hardcoded value. Thats just used to get the deployment details and see if the deployment is completed and stable". MED-16's counterpart MED-17 quotes it as "...see if the deployment is completed", dropping the trailing "and stable". Truncation only; not a misquotation.
  - "`apigee.override.delay` applies to the deployment call, not to the activation check" (medium.md:1880): issue:131 "`apigee.override.delay` is used for the seamless deployment"; issue:160 "Yes, the delay is included only to upload the bundle but not for checking the deployment." Supported.

  **Maintainer asked to lower 30 to 10 and to explain the 30 seconds (medium.md:1881-1882)**
  - issue:107 — "can you remove the delay from the pom profile and try? Have you always had that set to 30?"
  - issue:146 — "please change the value from 30 to something like 10 and see if that halps?"
  - issue:148 — "If you still continue to see errors, then pls check your Apigee logs to see why they take so long?"
  - issue:144 — "Usually you dont have to set the override delay to 30 ... Usually its less than 5-10 seconds."

  **`apigee.override.delay` is 30 in the POM (medium.md:1852)**: issue:107, 144, 146 all presuppose the 30 value. Supported.

  **Management API direct deploy succeeds in ~30 s (medium.md:1868-1869)**
  - issue:101 — "Yes Management API works well directly but it took around 30 secs to deploy where as deployment through plugin is failing with activation issue."

  **Plugin log strings (medium.md:1869-1871)**
  - issue:136-140 (maintainer asks to confirm seeing exactly): "Waiting to assert bundle activation....." / "Deployment failed to activate". Both appear verbatim in the quoted code at issue:19 and issue:26. Verbatim match.

  **Common incorrect answer: raising the delay was raised in-thread and was told it would not help (medium.md:1904-1905)**
  - issue:156 (reporter) — "Seems plugin doesn't depend on delay since delay with 50sec deployment worked for me."
  - issue:160 (maintainer) — "Yes, the delay is included only to upload the bundle but not for checking the deployment."

  **Closure (medium.md:1835-1836, 1886)**
  - issue:176-180 — "If the issue is not related to the plugin, can we close this?" / "Closing due to inactivity". The scenario's "closed for inactivity, not fixed" is supported by the closing comment.
  - Minor nuance, not scored as a defect: the GitHub metadata field is `STATE: closed state_reason: completed` (issue:3), not `not_planned`. MED-17's characterization rests on the closing comment text rather than the metadata field. Both readings are defensible; the comment is unambiguous.

  **Other defect classes checked, no finding**
  - No XML, no policies, no fault codes.
  - Self-contradiction: none. medium.md:1876 correctly distinguishes two different delays, and the "Common incorrect answers" entry does not state the correct answer.
  - Remediation vs verification: medium.md:1890 (make the check poll rather than sample) directly produces medium.md:1899-1900 (revisions serving, previously-passing builds still pass). Sound.
  - Unsatisfiable premise: none.
  - Critical failures (medium.md:1920-1921): "asserting the delay setting is the root cause" cannot be tripped by a correct answer; "opening a platform defect" also cannot.
  - Title: partial leak, below the MED-16 threshold but worth noting. "the Management API says the deployment worked" pre-establishes that the deployment succeeded, which is the scenario's core conclusion. It does not give the mechanism (fixed `Thread.sleep` + single-shot `getDeployedRevision`) or the genuine unknown (why 30 s), so I read this as acceptable framing rather than a defect. Flagging as a judgment call.
  - Minor vagueness, not scored: medium.md:1890 "or work around the fixed interval" gives no mechanism, and the thread shows the make-it-configurable request was never implemented (issue:169, unanswered). A reader could find this unsatisfying but it contradicts nothing.

---

### MED-18 Every API product, app and developer fails to load after a hybrid upgrade

- Verdict: DEFECT
- Defect: **Logically invalid inference embedded in the ground truth, the common-incorrect-answer list, and the critical-failure list.** medium.md:1975-1977 correctly states "affecting environments that use Workload Identity Federation together with an HTTP forward proxy. Both conditions are required." medium.md:1980-1982 then asserts the opposite: "An agent that checks only 'are you using WIF?' or only 'do you have a forward proxy?' will correctly observe one is absent and wrongly close the case." Under a documented conjunction, correctly observing one condition **absent** *does* correctly rule the issue out. The sentence is self-contradictory as written ("correctly observe ... wrongly close"). The same error is repeated at medium.md:2016-2018 ("Either alone rules the issue out incorrectly") and is escalated into a critical failure at medium.md:2029-2030 ("ruling the issue out by checking only one of the two gating features"). Source of truth: `research/pages/apigee-known-issues.txt:265` — "environments using Workload Identity Federation (WIF) **in conjunction with** an HTTP Forward Proxy **may fail**", i.e. an AND. Also `research/pages/hybrid_release-notes.txt:2184`. Note the same flawed phrasing originates in `references/hybrid.md:96-98` ("Checking either one alone rules it out wrongly"); MED-18 inherited it rather than inventing it.
- Severity: high
- Evidence:

  **Why this can penalise a technically correct answer (defect class 9)**
  - MED-18's own "Initial evidence" (medium.md:1959) gives only "The installation is on EKS". It does not tell the agent how WIF is configured.
  - On EKS, WIF is `gcp.federatedWorkloadIdentity.enabled` (`research/pages/hybrid_latest_config-prop-ref.txt:1534` — "Enables Workload Identity Federation on non-GKE platforms"). The GKE property `gcp.workloadIdentity.enabled` is documented as GKE-specific (config-prop-ref.txt:1545 — "Enables using Workload Identity Federation for GKE"), and the two are mutually exclusive ("Must not be set true if `gcp.federatedWorkloadIdentity.enabled` is set to true").
  - An agent that checks `gcp.workloadIdentity.enabled`, reads the documented-correct value `false` for an EKS cluster, and concludes "WIF is not in use, so 479872706 cannot apply" has followed the documentation exactly. Under MED-18's stated critical failure that answer is marked wrong. The scenario never distinguishes the two WIF properties, so it cannot distinguish the defensible answer from the wrong one.

  **Both readings, stated**
  - Reading A (the scenario's literal text): false. Given the AND, a single definitive negative check rules out.
  - Reading B (charitable, from `references/hybrid.md:97`): "a trap when the two configurations arrived at different times" — i.e. the trap is a *stale or partial inventory* (the forward proxy was added after the WIF check was run). Under this reading the advice ("check both") is right but the stated justification is still wrong, because MED-18 drops the temporal qualifier entirely and writes "Checking either one alone rules the issue out incorrectly."
  - Practical guidance ("check both features") is sound; the logical claim and the critical failure derived from it are not.

  **Issue ID, product, version, and fix — all correct**
  - `research/pages/apigee-known-issues.txt:257` `479872706`; `:259` `hybrid 1.16.0 (EKS with WIF and forward proxy)`; `:261` `FIXED in hybrid 1.16.0-hotfix.1`. Matches medium.md:1941-1942, 1969-1970, 1978.
  - `:263` headline — "Unable to load API Products, Apps, and Developers after migrating data to Apigee Hybrid 1.16." Matches medium.md:1951-1952.
  - `:265` — "environments using Workload Identity Federation (WIF) in conjunction with an HTTP Forward Proxy may fail to load management entities (API Products, Apps, Developers) **due to a credential casting regression in MART**". Matches medium.md:1975-1976 verbatim on cause and component.
  - `:259` supports "The register scopes the issue to EKS" (medium.md:1977). Correct — the *Affects* column scopes it, not the body prose; MED-18 correctly attributes the scoping to the register.
  - `research/pages/hybrid_release-notes.txt:2184` corroborates: "Resolved an issue that prevented loading API products, apps, and developers after migrating data to Apigee hybrid 1.16.0 in configurations using Workload Identity Federation (WIF) with an HTTP Forward Proxy."

  **The remediation YAML is the documented workaround, character for character**
  - medium.md:1989-1998 vs `research/pages/apigee-known-issues.txt:273-283`:

    ```text
    ao:
      image:
        url: "gcr.io/apigee-release/hybrid/apigee-operators"
        tag: "1.16.0-hotfix.1"
    mart:
      image:
        url: "gcr.io/apigee-release/hybrid/apigee-mart-server"
        tag: "1.16.0-hotfix.1"
    ```

  - All four property paths exist: `ao.image.url` config-prop-ref.txt:137, `ao.image.tag` :136, `mart.image.url` :2190, `mart.image.tag` :2189. No invented keys, correct casing. **No XML/YAML defect.**

  **Neighbouring defect 479040521 — correctly described**
  - `research/pages/apigee-known-issues.txt:217` `479040521`; `:219` `hybrid 1.16.0`; `:221` `FIXED in hybrid 1.16.0-hotfix.1`; `:223` "`apigee-operator-guardrails-sa` not created on AKS/EKS with Federated Workload Identity." Matches medium.md:2000-2001.
  - medium.md:2002-2003 "the chart template's initial `if` condition omits `.Values.gcp.federatedWorkloadIdentity.enabled`" matches `:231` + `:239` / `:252` — `{{ - if or (.Values.serviceAccountSecretProviderClass) (.Values.gcp.workloadIdentity.enabled) (.Values.gcp.federatedWorkloadIdentity.enabled) } }`. Correct, including the exact dotted key.
  - `research/pages/hybrid_release-notes.txt:2185` corroborates.
  - Completeness caveat (low, not separately scored): the register's workaround edits **two** templates — `apigee-operator-guardrails-sa.yaml` **and** `apigee-operator-guardrails.yaml` (known-issues.txt:229 and :242, with the note "Note: This is the `apigee-operator-guardrails.yaml` template file, not the `apigee-operator-guardrails-sa` file") — then applies the chart (:255). MED-16... MED-18 says "the chart template's initial `if` condition" (singular) and gives no steps. Since MED-18 frames this as a "check", not a remediation, it is incomplete rather than wrong.

  **MART scoping (medium.md:1964-1965, 1975)**
  - `research/pages/hybrid_v1.17_service-config.txt:71` — "Management API for Runtime data (MART) | Exposes an endpoint to administer data entities on the runtime plane, such as KMS (API keys and OAuth tokens), quotas, KVMs, and **API products**."
  - `research/pages/api-platform_get-started_compare-apigee-products.txt:253` — "**MART interacts with the local Cassandra datastore** and serves as an API provider for the Apigee APIs to access and manage runtime data entities." (same at `hybrid...`? no — at `api-platform_get-started_apigee-feature-summary.txt:253` and `fsum2.txt:253`).
  - Supports MED-18's "Everything works except the components that reach the runtime datastore" and, in general terms, "They are in Cassandra" (medium.md:2014). **Caveat, low:** the corpus never enumerates developers or developer apps as Cassandra-resident. `hybrid_v1.17_service-config.txt:68` scopes Cassandra to "KMS, OAuth, KVMs, and caching for the runtime plane", and MART's own entity list at :71 stops at "API products". The general MART→Cassandra relationship is documented; the specific claim that *developers and developer apps* live in Cassandra is an inference. The conclusion it supports (do not re-import; no data loss) is fully supported by known-issues.txt:265, so the inference is harmless.

  **Other defect classes checked, no finding**
  - Self-contradiction beyond the conjunction error: none. "Ground-truth resolution" and "Diagnostic evidence" agree on MART version, both gating features, and EKS.
  - Remediation vs verification: medium.md:1986-1998 changes both `ao` and `mart` images, and medium.md:2007-2008 demands "confirm proxy deployment still works, because the fix changes the operator image, not just MART". Consistent and achievable.
  - Unsatisfiable premise: none.
  - Critical failures: "telling a customer their data is lost" cannot be tripped by a correct answer. "Ruling the issue out by checking only one of the two gating features" **can** — see above.
  - Title: "Every API product, app and developer fails to load after a hybrid upgrade" is symptom-only. No leak.
  - Difficulty (low severity, judgment call): the ticket names the exact affected version (medium.md:1951, "upgraded our hybrid install to 1.16.0") and the symptom string is a near-verbatim match to the register headline (known-issues.txt:263). "Expected investigation" hands over MART (medium.md:1964). One register lookup resolves it. This reads closer to **low** than medium.

---

### MED-19 Runtime logs stopped after a successful upgrade

- Verdict: OK
- Defect: n/a
- Severity: n/a
- Evidence:

  **Fault codes named: none.** MED-19 names no Apigee fault code. Nothing to check against `research/pages` or `error-codes.md`.

  **The discriminating command (medium.md:2071-2073, 2080)**
  - `research/pages/apigee-known-issues.txt:28` — "`kubectl get daemonset apigee-logger -n apigee` reports a desired count of `0` and no logger pods are created." Verbatim match to the command and to the desired-count reading.
  - DaemonSet resource name `apigee-logger` and namespace `apigee` both match. No invented resource.

  **Default node selector, and the bug-fix-turned-regression (medium.md:2081-2090)**
  - `research/pages/apigee-known-issues.txt:30` — "The `apigee-telemetry` chart has always shipped a default `logger.nodeSelector` of `apigee.cloud.google.com/apigee-logger-enabled: \"true\"`, which requires you to label the nodes that should run the logger. Releases before the affected versions ignored component-level node selectors, so the logger was scheduled on the Apigee node pools even though the nodes were not labeled. The affected releases apply component-level node selectors correctly, so the default now takes effect and the DaemonSet matches no nodes."
  - This single line supports medium.md:2081-2083 (default selector, chart name, no nodes labelled), medium.md:2087-2090 (earlier releases ignored them; affected release honours them; DaemonSet matches no nodes) and the "counter-intuitive" framing at medium.md:2092-2093. All accurate.

  **Property names and defaults — exact, from the configuration reference**
  - `research/pages/hybrid_latest_config-prop-ref.txt:1744` `logger.enabled`; `:1750` "**Default value:** `false`"; `:1752` "**Chart:** `apigee-telemetry`".
  - `:1957` `logger.nodeSelector.key`; `:1963` "**Default value:** `apigee.cloud.google.com/apigee-logger-enabled`".
  - `:1973` `logger.nodeSelector.value`; `:1979` "**Default value:** `true`".
  - The MED-19 selector string `apigee.cloud.google.com/apigee-logger-enabled: "true"` (medium.md:2082) is the key and value the reference documents, joined. **No invented YAML keys.**
  - `research/pages/apigee-known-issues.txt:32` — "Only deployments that set `logger.enabled: true` are affected." Consistent with medium.md:2081 and with medium.md:2127-2128 ("The flag being true is the precondition, not the cause").

  **Both remediation branches are the documented workaround, character for character**
  - medium.md:2099-2105 vs known-issues.txt:44-49:

    ```text
    logger:
      enabled: true
      nodeSelector:
        key: ""
        value: ""
    ```

  - medium.md:2110 vs known-issues.txt:59 — `kubectl label nodes NODE_NAME apigee.cloud.google.com/apigee-logger-enabled=true`. Exact.
  - known-issues.txt:36 ("To run the logger on every node, which matches the behavior of earlier releases, clear the default node selector") and :51 ("keep the default node selector and label each of those nodes") match medium.md:2097 and 2107 exactly, including the framing of the two options.
  - "Then upgrade the `apigee-telemetry` chart" (medium.md:2113) matches known-issues.txt:34 — "**Workaround:** Choose one of the following, then upgrade the `apigee-telemetry` chart." The upgrade step is documented, not invented.

  **Affected and fixed versions (medium.md:2050, 2059, 2113)**
  - known-issues.txt:20 `543171828`; :22 `hybrid 1.14.7, hybrid 1.15.7, and hybrid 1.16.8`; :24 `FIXED in hybrid 1.16.9`. Ticket's "upgraded hybrid to 1.16.8" is an affected version. Exact.
  - `research/pages/hybrid_release-notes.txt:857` corroborates — "Fixed an issue where the `apigee-logger` DaemonSet failed to schedule on cluster nodes without custom node labels due to a default `logger.nodeSelector` in the Helm chart."

  **Platform dependency (medium.md:2128-2129)**
  - `research/pages/hybrid_v1.17_logging-view.txt:57` — "Logging is provided by default on GKE and GKE on-prem. ... On AKS, you must explicitly enable logging by setting `logger.enabled` to `true` in your overrides file." Exact match.
  - Independently corroborated at `references/hybrid.md:73-74`.
  - Minor tension inside the docs themselves, not a scenario defect: logging-view.txt:57 also says "On these platforms, be sure that you have **disabled** logging ... by setting `logger.enabled` to `false`", and config-prop-ref.txt:1750 lists the global default as `false`. MED-19 follows the doc's leading clause and the skill reference; it is not misattributed.

  **Logs Explorer resource type (medium.md:2118)**
  - `research/pages/hybrid_v1.17_logging-view.txt:67` — "In the **Resource type** drop-down list, select **Kubernetes Container**, the name of your cluster, and your namespace ID." Exact. Both cited references (hybrid/v1.17/logging, hybrid/v1.17/logging-view) exist in the corpus.

  **"Runtime is healthy, logger is simply not scheduled" (medium.md:2075-2076, 2085-2086, 2122)**
  - Independently corroborated at `references/hybrid.md:80-83` — "a bug fix that began honouring component-level node selectors activated a latent default `logger.nodeSelector`, leaving the runtime healthy but the log daemonset scaled to zero. `kubectl get daemonset apigee-logger` showing a desired count of 0 with healthy runtime pods is that signature."
  - Consistent with MED-19's initial evidence (medium.md:2064, traffic normal, proxies serve).

  **Other defect classes checked, no finding**
  - No XML. All YAML keys, Helm values, Kubernetes labels and kubectl invocations verified against `research/pages`.
  - Self-contradiction: none. The ground truth agrees with the diagnostic evidence; the "Common incorrect answers" entry "Checking only whether `logger.enabled` is set" (medium.md:2127) is genuinely incorrect, and the appended platform note is correct rather than the answer itself.
  - Remediation vs verification: both branches (clear selector → DaemonSet matches every node; label nodes → DaemonSet matches exactly the labelled nodes) produce logger pods and therefore Logs Explorer lines. Achieves medium.md:2117-2118.
  - Unsatisfiable premise: none.
  - Critical failures (medium.md:2140-2141): "escalating as a runtime outage", "recreating the DaemonSet", "recommending a runtime restart" — none can be tripped by a technically correct answer. The DaemonSet-recreation entry is well reasoned: recreating it re-renders the default selector and it matches no nodes again (known-issues.txt:30).
  - Title: "Runtime logs stopped after a successful upgrade" is symptom-only. No leak.
  - Two low-severity notes, neither a defect:
    1. Verification wording (medium.md:2117) — "the desired count matches the labelled node count" describes only the label-nodes branch. On the clear-the-selector branch the correct expectation is "matches the total node count". Imprecise, not wrong.
    2. Difficulty (judgment call): the ticket names `1.16.8` (medium.md:2059), which is one of three affected versions, and the symptom "no Apigee runtime logs at all" matches the register headline closely (known-issues.txt:26). One register lookup resolves it, so this reads closer to **low** than medium. The counter-intuitive "a fix caused this" step is real work, but only after the lookup.

---

## Cross-cutting findings (MED-16–MED-19)

**1. The conjunction trap in MED-18 is inherited from the skill reference, not invented by the scenario.**
`references/hybrid.md:96-98` states: "**MART credential regression** is gated on workload identity federation **and** a forward proxy **together**. Checking either one alone rules it out wrongly, which is a trap when the two configurations arrived at different times." MED-18 (medium.md:1980-1982, 2016-2018, 2029-2030) drops the temporal qualifier ("arrived at different times") and converts it into an unconditional logical error. The source register, `research/pages/apigee-known-issues.txt:265`, documents an AND ("in conjunction with"), under which a single definitive negative check correctly rules the issue out.
Fixing MED-18 alone would leave `hybrid.md` teaching the same false rule to every agent that loads the reference. Both should change. `hybrid.md:97` already contains the charitable reading ("when the two configurations arrived at different times") that would make the claim correct — promoting that qualifier into MED-18 is the minimal fix.

**2. `error-codes.md` has a systematic hole for the OAuthV2 policy page, and MED-16 sits in it.**
`references/error-codes.md:136-147` contains 14 `steps.oauth.v2.` rows, all sourced from `revoke-oauth-v2-policy`, `get/set/delete-oauth-v2-info-policy`. **None** of the 18 codes on the OAuthV2 policy page's own runtime error table (`research/pages/api-platform_reference_policies_oauthv2-policy.txt:1330-1347`) is present — not `InvalidRequest`, not `MissingParameter`, not `InvalidClientIdentifier`, not `UnSupportedGrantType`. The cause is visible in the data: the OAuthV2 page's table is unbackticked and its fault-code column is bare text (line 1340: `| steps.oauth.v2.InvalidRequest | 400 | ...`), while the indexed pages emit backticked codes (e.g. `api-platform_reference_policies_set-oauth-v2-info-policy.txt:193`: `` | `steps.oauth.v2.access_token_expired` | `500` | ``). `build_error_index.py` almost certainly keys on the backticked form. Note that `references/security.md:21-22` cites `steps.oauth.v2.InvalidClient` as its worked example of the prefix — and that code is *also* absent from the index, so the reference file's own example is unresolvable.
This matters beyond MED-16: any future scenario citing an OAuthV2-page code will violate the medium.md:13-15 rule. Two fixes are available — teach the parser the unbackticked form, or add an explicit "documented but not indexed" disclosure. The file already has a precedent for the disclosure style at `scenarios/medium.md:4794-4798`.
Also worth noting for the index build: `api-platform_reference_policies_oauthv2-policy.txt:1340` documents `InvalidRequest` at **400**, while the similarly-named `invalid_request-authorization_code_invalid` in `error-codes.md:146` is marked **"401, 500 CONFLICT"**. An agent that pattern-matches on the prefix will pick up the wrong row and the wrong status.

**3. MED-18 and MED-19 both sit closer to "low" than "medium".**
In both, the ticket names the exact affected hybrid version (medium.md:1951 `1.16.0`; medium.md:2059 `1.16.8`) and the symptom is a near-verbatim match to the known-issues register headline (`apigee-known-issues.txt:263` and `:26`). The MED-18 "Expected investigation" additionally hands over the affected component (MART, medium.md:1964), and MED-19's "Expected investigation" hands over the exact discriminating command and the exact decision rule (medium.md:2071-2076). Once the register is consulted — which is the skill's documented method — both resolve in one step. MED-16 is different: there the work is genuinely diagnostic, but the title gives it away. If the medium tier is meant to hold "more than one hypothesis tested" (`medium.md:3-5`), these three are candidates for a light re-tier or a tightened ticket.

**4. What held up under scrutiny.** No invented XML, YAML, Helm values, Kubernetes resource names or labels were found in any of the four scenarios. Every `overrides.yaml` block, `kubectl` invocation, flow `<Condition>` and Helm chart path cited in MED-16 through MED-19 matches the cached corpus character for character, and every claim attributed to `api-platform-samples#7`, `apigee-deploy-maven-plugin#213`, known issue `479872706`, `479040521` or `543171828` is present in the cited source text. The single high-severity defect (MED-18's conjunction inference) is a logic error, not a fabrication — and it is traceable to an upstream reference file rather than to the scenario.

---

### MED-20 A deployed timeout change is not taking effect on some requests only

- Verdict: DEFECT
- Defect: Known issue **246774745 is mis-scoped to hybrid**. The register's Affects column for
  246774745 is `Apigee` (SaaS), not hybrid — `research/pages/known-issues-v.txt:2168-2176` and
  `research/ki-entries.json` (`"id": "246774745", "product": "Apigee", "affects": "Apigee"`). The
  scenario declares `- Product: hybrid` (scenarios/medium.md:2162), the ticket says "We are on
  hybrid 1.15.5" (medium.md:2175), and the Initial evidence says "The TargetEndpoint uses a
  `<LoadBalancer>` with more than one target server" (medium.md:2179). Yet the Ground-truth
  resolution asserts "A second documented defect, 246774745, **compounds it**" (medium.md:2203-2205),
  and that mis-scoped entry is then made load-bearing in the Correct remediation ("Separately, if
  several flows set different timeouts against the same target host, consolidate them", medium.md:
  2215-2216) and in the Verification ("Then exercise every flow that sets a timeout for that target
  host", medium.md:2220-2221). Contrast the sibling entry, which is correctly hybrid-scoped:
  known-issues-v.txt:337-341 gives 471125841 Affects = `hybrid 1.14.x,hybrid 1.15.x`, and hybrid
  entries are always labelled "hybrid ..." in this column (e.g. 543171828 at
  `research/pages/ki-live-20261012.txt:17` = `hybrid 1.14.7, hybrid 1.15.7, and hybrid 1.16.8`;
  entries that cover both say `Apigee, Apigee hybrid`). So `Apigee` alone means SaaS and excludes
  hybrid.
  Both readings, since the point is arguable: (a) strict — the register does not scope 246774745 to
  hybrid, so citing it as compounding a hybrid incident is wrong; (b) lenient — the entry is
  presented as a bonus caveat, and the register's Affects column is a coarse product filter that
  the page header renders as the "Apigee" facet (`research/pages/ki-live-20261012.txt:9` lists
  "Apigee ... hybrid 1.16 hybrid 1.15 ..."). I score (a): the entry is repeated in three sections
  including a Verification requirement, so the scope error is not cosmetic.
  Everything else in the scenario checks out, including the primary resolution — see Evidence.
- Severity: low
- Evidence:
  - `io.timeout.millis` is real and lives on `<HTTPTargetConnection>`:
    `.agents/skills/apigee-support-core/references/policy-mechanics.md:132`
    "`io.timeout.millis` | 55000 | `<HTTPTargetConnection>` | `504` on write to target or read from
    target"; `research/pages/api-platform_reference_endpoint-properties-reference.txt:78,272`.
  - No timeout-mechanism conflation and no fault code at all. MED-20 names only `io.timeout.millis`
    across lines 2154-2244; it never says 504, never mentions ServiceCallout, never mentions
    `api.timeout`, `connect.timeout.millis`, `<Timeout>`, or the Message Processor pool timeout. So
    the "callout timeout is a 500, not a 504" defect class does not apply.
  - 471125841: `research/pages/known-issues-v.txt:337-345` — Affects `hybrid 1.14.x,hybrid 1.15.x`
    (line 339), "FIXED in hybrid 1.16.x" (line 341), "When a new API proxy revision is created and
    deployed with an updated `io.timeout.millis` value, the new value might not be consistently
    honored." (line 343), "This happens when multiple servers are used under \<LoadBalancer\> in the
    TargetEndpoint." (line 345). Matches medium.md:2197-2201 verbatim, including the scope
    (1.14.x/1.15.x) and the FIXED version.
  - **The partial-effect ("some requests only") explanation is the mechanism the ground truth
    names**, which is the specific thing to confirm: the register says the new value "might not be
    **consistently** honored" and is "**intermittently** not honored" (known-issues-v.txt:343,345) —
    i.e. partial application is the documented symptom, and the documented precondition (multiple
    servers under `<LoadBalancer>`) is exactly the structural signal the scenario says the symptom
    does not reveal (medium.md:2201). Premise is satisfiable: hybrid 1.15.5 is in the affected range
    and the Initial evidence supplies the LoadBalancer precondition.
  - Remediation matches the documented workaround: known-issues-v.txt:345 "**Workaround:** After
    API proxy deployment, restart the apigee-runtime pods one by one so that the change is
    propagated correctly." → medium.md:2211-2213, including "rather than all at once, to keep
    serving traffic". The "Common incorrect answers" entry at medium.md:2229 ("Rolling every runtime
    pod at once. That turns a partial problem into a full outage.") does **not** state the correct
    answer, so no class-3 self-contradiction.
  - "Contract version lines" in the hybrid pod log are real:
    `research/pages/hybrid_latest_runtime-logs.txt:67-77`, section "Contract version information",
    e.g. line 71 "`RuntimeSyncServiceImpl.updateToVersion() : Switched to newer version 750 from
    version null` — The MP changed to a newer version of the configuration contract." Supports
    medium.md:2187.
  - 246774745's body text is quoted accurately even though its scope is wrong:
    known-issues-v.txt:2174-2176 "If a proxy sets two or more `io.timeout.millis` values in two or
    more flows using the same target host, only one `io.timeout.millis` value is honored." =
    medium.md:2204-2205. Both entries are FIXED, as medium.md:2163-2164 claims.
  - Remediation ↔ Verification are consistent: consolidation (medium.md:2215-2216) is checked by
    exercising every flow (medium.md:2220-2221). No class-4 failure.
  - Minor, not scored: the critical failure "recommending a redeploy as the fix" (medium.md:2243) is
    mildly loose, because a correct answer that upgrades to 1.16.x and then deploys the new
    revision has recommended a redeploy as part of the fix. The failure is scoped to redeploy *as
    the fix*, so a complete answer does not trip it.
  - Difficulty "medium" is right: the agent must reject both the redeploy and backend hypotheses and
    then reach a version-scoped register entry, plus a second one. Not class-8.

---

### MED-21 The linter and the security team want opposite things

- Verdict: OK
- Defect: n/a
- Severity: n/a
- Evidence:
  - Both linter rules are real and the messages are quoted verbatim from the issue thread:
    `research/issues/apigee_apigeelint-526.txt:2` (issue TITLE: "TD012 & TD015 - TargetEndpoint
    HTTPTargetConnection should have exactly one SSLInfo & Missing MaxFailures element within
    LoadBalancer"); TD012 text at line 86 and line 162 ("TargetEndpoint HTTPTargetConnection should
    have exactly one SSLInfo"); TD006 text at line 102 and line 154 ("When using a LoadBalancer, the
    SSLInfo should be configured in the TargetServer, not under HTTPTargetConnection"); TD015 at
    line 112 and line 166 ("Missing MaxFailures element within LoadBalancer"). All three match
    medium.md:2280-2283 exactly, including the rule IDs.
  - The security control the scenario collides with is real: `research/issues/apigee_apigeelint-526.txt:121`,
    reporter PratMoha, "For TD012, this also gets flagged in Advanced API Security to add a SSLInfo
    section to the target httpconnection, even when the same is defined in the target server."
  - The scenario attributes **nothing to the maintainers that they did not say**. DinoChiesa
    (COLLABORATOR) at issue line 170-176 writes, verbatim: "So this is what I propose for changes: 1.
    Demote TD006 to an External Plugin. 2. Modify TD012 to fire if and only if there is no
    LoadBalancer 3. Modify TD015 so that it does not complain about a missing MaxFailures if there is
    a single server." That is character-for-character the three changes in medium.md:2309-2311.
    ssvaidyanathan (COLLABORATOR) concurs on 2 and 3 at line 187 ("lets do what you proposed which
    checks only if there is a URL configured (https)") and line 191 ("Yes - lets warn only if there
    are more than one server").
  - v2.67.0 is confirmed by a maintainer, not invented: issue line 195-196, ssvaidyanathan at
    2025-06-04T00:43:12Z, "Fixed in v2.67.0"; issue line 3 `STATE: closed state_reason: completed`.
    Matches medium.md:2264 and medium.md:2309.
  - "The linter cannot see the TargetServer" is the maintainer's own reasoning: issue line 154 "And it
    has no way to check the referred TargetServer - in other words it has no way to check that SSLInfo
    is configured in the TargetServer, per the recommendation. The design of the plugin is sort of
    broken"; line 162 "Apigeelint cannot check case (b), because TargetServers are not present in the
    proxy definition." Matches medium.md:2289-2290 and 2304-2305. The report was accepted as a
    defect: issue line 110, DinoChiesa, "ok that's for sure wrong. I'll have a look."
  - "TLS belongs on the target server when using a `<LoadBalancer>`" is backed by Apigee docs, not just
    the issue: `research/pages/api-platform_deploy_load-balancing-across-backend-servers.txt:424`
    "If you are using a target server to define the backend service, and the backend service requires
    the connection to use the HTTPS protocol, then you must enable TLS/SSL in the target server
    definition."
  - MaxFailures antipattern, every clause, from
    `research/pages/api-platform_antipatterns_load-balancing-maxfailures.txt` (page scope line 1:
    "*This page applies to **Apigee** and **Apigee hybrid**.*", which supports medium.md:2263
    "Product: Apigee or hybrid"):
    - line 77 "Having single TargetServer in a `LoadBalancer` configuration of the TargetEndpoint or
      Service Callout policy with `MaxFailures` set to a non-zero value is not recommended as it can
      have adverse implications." → medium.md:2313-2314.
    - line 98 "Apigee does not automatically put the TargetServer back in rotation even after the
      target is up and running again. To address this issue, ***the API Proxy must be redeployed***
      for Apigee to put the TargetServer back into rotation." → medium.md:2315-2316 quotes "the API
      Proxy must be redeployed" exactly.
    - line 100 "If the same configuration is used in the Service Callout policy, then the API requests
      will get 500 Error after the requests to the TargetServer \"target1\" fails 5 times." →
      medium.md:2316 "The same configuration in a ServiceCallout produces 500s instead." Status code
      correct (500, not 504).
    - line 146 "**The default value of MaxFailures is 0.** This means that Apigee always tries to
      connect to the target for each request and never removes the target server from the rotation."
      → medium.md:2323-2324 "leave it at the documented default of 0".
    - line 113 "Having a HealthMonitor ensures that the TargetServer is put back into rotation as
      soon as the target server becomes available again, ***meaning there is no need to redeploy the
      proxy***" → medium.md:2324-2325 "the documented way to get a removed server back into rotation
      without a redeploy". Line 144 is best practice 3, the complement.
  - No invented XML. `<LoadBalancer>`, `<Server name="..."/>`, `<SSLInfo>`, `<MaxFailures>`,
    `<HealthMonitor>` all appear in the antipattern page's samples (lines 41-48, 86-94, 124-142) and
    in the issue's own config at issue lines 41-49 and 75-84, which is exactly the shape MED-21's
    Diagnostic evidence describes (medium.md:2298-2300). No `ClientCertStore`/`ClientCertAlias`
    anywhere (those are correctly identified as non-existent in
    `.agents/skills/apigee-support-core/references/policy-mechanics.md:120-121`).
  - Remediation ↔ Verification are consistent: suppression on a pre-v2.67.0 linter is documented
    (issue line 67, ssvaidyanathan: "If you do not want that to show up, you can include that rule
    to the exclude set"; issue line 158, DinoChiesa option 1: "they can do so with the command-line
    switch (`-e TD006`), or a directive in the XML (`<!-- apigeelint disable=TD006 -->`), or in the
    `.apigeelintrc` file"), and Verification then lints on v2.67.0+ (medium.md:2329). No class-4
    failure.
  - No class-3 self-contradiction: none of the four "Common incorrect answers" entries
    (medium.md:2333-2345) states the resolution; entry 4 in particular correctly says both
    authorities describe a real conflict.
  - Difficulty "medium" is right — two mutually exclusive rules plus a tool-reach explanation plus a
    second antipattern. Not class-8.
  - Minor imprecisions, explicitly **not** scored as defects, with both readings:
    (i) medium.md:2314 says "the server is taken out of rotation on the **first** failure", but the
        doc's example uses `MaxFailures` 5 and says removal happens after "five consecutive requests
        failed" / "fails five times" (antipattern page lines 73, 96). Strictly the count is
        `MaxFailures`, not 1. A reader could also read "first failure" as shorthand for "first
        failure past the threshold". The load-bearing claim (never returns without a redeploy) is
        exact.
    (ii) medium.md:2342 "takes the only server out of rotation **permanently**" mildly contradicts
        the same scenario's own line 2316, which says a redeploy is required for it to return. The
        doc agrees with 2316 (line 98), so 2342 is the imprecise one; it is inside a
        "Common incorrect answers" rationale, not a graded claim.
    (iii) The critical failure "telling the customer one of the two authorities is simply wrong"
        (medium.md:2358) has some friction with the maintainers' own position: DinoChiesa at issue
        line 164 says of the security scanner "That seems like a bug in Adv API Sec. We don't have
        control over that. I suggest you connect with Google support and file a bug." An agent that
        relays that advice is quoting the maintainer, yet the wording of the failure could be read as
        catching it. Reading it as narrowly "dismissing an authority outright", no correct answer
        trips it; reading it broadly, there is a class-9 ambiguity. I lean narrow and do not score
        it, but flagging it.
    (iv) The Verification "confirm none of TD006 ... fire" is trivially true on v2.67.0+ because
        TD006 was demoted to a disabled-by-default External Plugin (issue line 160), so the check
        proves less than it appears to. Harmless, since TD012 and TD015 are the substantive checks.

---

### MED-22 A routine cert-manager upgrade plants a future outage

- Verdict: DEFECT
- Defect: **Spurious, wrongly-scoped Verification step.** Medium.md:2454-2455 requires "Separately,
  verify Cassandra backup and restore across the clusters, because Cassandra backup and restore
  cannot work with mixed hybrid versions." The cited constraint is real
  (`research/pages/hybrid_v1.17_upgrade.txt:82`: "until all remaining clusters are upgraded Cassandra
  backup and restore cannot work with mixed versions. For example, a backup from Hybrid 1.16 cannot
  be used to restore a Hybrid 1.17 instance.") but it is lifted out of its context and its premise is
  false in this scenario. Its source context is the section heading "Before you upgrade to 1.17.1 -
  limitations and important notes" (hybrid_v1.17_upgrade.txt:76) and it governs a *hybrid version*
  upgrade rolled out cluster-by-cluster. MED-22 states twice that no hybrid upgrade is in progress and
  that the clusters are on the same hybrid version — medium.md:2393 "Both are the same hybrid
  version" and medium.md:2397 "Two hybrid clusters, same hybrid version, same changes". So "mixed
  hybrid versions" is false on the facts given, and nothing in the Correct remediation
  (medium.md:2433-2448, which only patches `rotationPolicy`) has any bearing on Cassandra backup or
  restore. An agent that correctly solves the cert-manager question cannot justify this step from any
  evidence in the packet, and a grader applying it literally would penalise a correct answer. That is
  defect class 4 (remediation does not achieve verification) plus an out-of-context misattribution
  (class 5). Both readings: (a) the step is a lifted-from-context non-sequitur and should be deleted;
  (b) a charitable reading is "a DR hygiene note for later" — but then the stated reason is wrong and
  the step still does not follow from the scenario. I score (a).
  Secondary, lower-severity, same scenario: the turn-2 Diagnostic Evidence asserts a state the stated
  mechanism does not produce — see Evidence item 5.
- Severity: medium
- Evidence:
  - cert-manager 1.18 default flip is real: `research/pages/hybrid-release-notes.txt:2586`
    "**Note:** cert-manager release 1.18 introduces a change to the default certificate
    `Spec.PrivateKey.RotationPolicy` value that can impact traffic on upgraded Apigee hybrid
    installations. This does not affect new installations of Apigee Hybrid. See [Known issue
    465834046]". And `research/pages/known-issues-v.txt:363` "cert-manager versions 1.18+ changed the
    default for the private key rotation policy from `Never` to `Always`."
  - The fresh-vs-upgraded split is quoted exactly: known-issues-v.txt:365-366 "**Note:** This only
    applies to upgraded Apigee hybrid clusters. The certificates in fresh installs of the hybrid
    versions 1.14.3+, 1.15.1+, and 1.16.0. already have the rotation policy set to `Never`." MED-22
    quotes "only applies to upgraded Apigee hybrid clusters" at medium.md:2420. The version/status
    scoping in the metadata is exact: known-issues-v.txt:361-363, Affects "hybrid 1.14.3, hybrid
    1.15.1, and hybrid 1.16.0 and later for upgrades", Status "FIXED in hybrid 1.14.3, hybrid 1.15.1,
    and hybrid 1.16.0 for fresh installs" — i.e. medium.md:2381-2382's "FIXED for fresh installs ...
    upgraded clusters are not covered" is a fair reading.
  - The future outage really follows from the stated facts: known-issues-v.txt:367-368 "Newer versions
    of cert-manager (v1.18+) now automatically rotate the private keys. When this key is rotated for
    the apigee-ca certificate, it will cause an outage." MED-22 quotes "When this key is rotated for
    the `apigee-ca` certificate, it will cause an outage." at medium.md:2423-2424, verbatim. So the
    "plants a future outage" framing is documented, not inferred.
  - Remediation is the documented workaround, command reproduced correctly:
    known-issues-v.txt:372 "Edit the `apigee-ca` certificate in the `cert-manager` namespace and set
    `spec.privateKey.rotationPolicy` to `Never`"; the patch command at known-issues-v.txt:440-444 is
    `kubectl patch Certificate -n cert-manager --type=json -p='[{"op": "replace", "path":
    "/spec/privateKey/rotationPolicy", "value": "Never"}]' -o=yaml apigee-ca`, matching
    medium.md:2438-2442. The "Alternative ... do not upgrade cert-manager above 1.17.x" is verbatim
    from known-issues-v.txt:373 "Do not upgrade cert-manager to a version higher than 1.17.x." The
    ordering warning is verbatim from known-issues-v.txt:375 "**Warning:** Performe these steps
    *before* upgrading cert-manager. Otherwise, you may trigger a certificate rotation." → medium.md:
    2447-2448. Verification step 1 matches doc step 3 at known-issues-v.txt:448 and the expected
    output at line 477 `rotationPolicy: Never`.
  - The Diagnostic Evidence command is the documented one: known-issues-v.txt:379
    `kubectl get certificate apigee-ca -n cert-manager -o yaml`, identical to medium.md:2409 and
    2453. `spec.privateKey.rotationPolicy` is the real field path (known-issues-v.txt:475-477,
    shown nested under `privateKey:`). No invented XML/field.
  - Secondary finding, low severity, both readings: the turn-2 evidence is internally strained.
    medium.md:2412-2413 asserts "On the failing cluster, `spec.privateKey.rotationPolicy` is unset or
    set to `Always`. On the healthy cluster it is `Never`. **Both clusters run cert-manager at or
    above 1.18**", while medium.md:2397-2398 says both were upgraded, not installed fresh. Under the
    documented mechanism, an upgraded cluster on cert-manager ≥1.18 that has never been patched should
    be unset/`Always`, so both should look alike; the doc only guarantees `Never` for *fresh* installs
    of 1.14.3+/1.15.1+/1.16.0+ (known-issues-v.txt:365-366), not for upgraded ones. Reading (a): the
    scenario quietly relies on an unstated difference (one cluster patched previously, or a hybrid
    upgrade path that re-renders the Certificate), which a careful agent may challenge instead of
    accepting. Reading (b): the evidence is given to the agent as observed fact and does not have to
    be derivable; the doc does not say an upgraded cluster *cannot* have `Never`. I lean (a) as a
    documentation gap in the scenario, but it does not make the premise unsatisfiable, so I am not
    scoring it as a separate defect.
  - Minor, not scored: metadata line 2384-2385 claims "nothing in the symptom points at cert-manager",
    but the ticket's own first sentence is "We upgraded cert-manager on our hybrid clusters last week"
    (medium.md:2391, and `evaluation/packets/MED-22.prompt.md:16`). cert-manager is named in the
    visible evidence, so the metadata overstates the difficulty. It is metadata, not agent-visible,
    and it does not harm the exercise.
  - Minor, not scored: the prescribed patch uses JSON-patch `op: "replace"` on
    `/spec/privateKey/rotationPolicy`, and RFC 6902 `replace` fails when the target path is absent —
    i.e. in exactly the "is unset" case the Diagnostic Evidence includes (medium.md:2412). This is
    inherited verbatim from Google: known-issues-v.txt:418 and 423-427 give the same `op: "replace"`
    under a precondition of "If `rotationPolicy` is not set or if it is set to `Always`". Faithful to
    the source, so not a scenario defect, but worth recording since the doc workaround itself is
    fragile.
  - No class-6 title leakage (see header note). No class-1 invented elements. No fault codes named.
    Difficulty "medium" is right: the agent must compare clusters rather than versions, and must
    resist claiming the entry explains the present symptom — which medium.md:2426-2431 handles well
    and in line with the packet preamble's "If you cannot establish a root cause, say that plainly"
    (`evaluation/packets/MED-22.prompt.md:7-8`). No class-2 fault codes, no class-8 difficulty
    problem. Critical failures (medium.md:2477-2478) are sound: a correct answer cannot plausibly
    recommend a CA rebuild, and the version-comparison failure is the intended discriminator.

---

## Cross-cutting findings (MED-20–MED-22)

1. **Register product-scope drift (MED-20).** MED-20 imports 246774745, whose Affects column is
   `Apigee`, into a scenario declared `Product: hybrid` and with a hybrid version in the ticket. The
   pattern to watch across the suite: the known-issues Affects column distinguishes
   `hybrid <versions>`, `Apigee`, and `Apigee, Apigee hybrid`
   (`research/pages/ki-live-20261012.txt:9,17`; `research/ki-entries.json` `"product"` field), and
   any scenario that pairs a SaaS-only entry with a hybrid case inherits this error.

2. **Verbatim-quote fidelity is high across all three; context fidelity is not (MED-20 and MED-22).**
   Every direct quotation I checked is exact (MED-20's two register quotes, MED-21's three linter
   strings and the "the API Proxy must be redeployed" phrase, MED-22's "only applies to upgraded
   Apigee hybrid clusters" and "it will cause an outage"). The two defects are both cases where an
   exact quote was moved to a scope the quote does not cover — a SaaS entry imported into a hybrid
   case (MED-20) and a mixed-hybrid-version upgrade constraint imported into a same-version case
   (MED-22). Neither error is detectable by quote-matching alone; both require reading the Affects
   column / the surrounding section.

3. **Not defects, recorded so they are not re-raised.** (a) Title leakage is not live for these three:
   `tests/make_packets.py:203-216` strips titles and writes `# Support case <ID>`
   (`evaluation/packets/MED-20.prompt.md:13`, `MED-21.prompt.md:13`, `MED-22.prompt.md:13`), which
   supersedes the stale method note at `evaluation/audit-hard-reg.md:15-17`. (b) No timeout-mechanism
   conflation appears in MED-20: it names only `io.timeout.millis`, and asserts no fault code at all,
   so there is nothing to mis-attribute. (c) No maintainer-attribution error in MED-21: the three
   changes at medium.md:2309-2311 are DinoChiesa's verbatim list at
   `research/issues/apigee_apigeelint-526.txt:170-176`, and v2.67.0 is ssvaidyanathan's own closing
   comment at line 196.
