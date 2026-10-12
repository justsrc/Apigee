# Fix pass: scenarios/medium.md

Single file touched: `scenarios/medium.md`. No network used; every fact was verified with
`grep` against `research/pages/` (408 files) and `research/issues/`.

Verification baseline before editing: 22 scenarios, IDs MED-01..MED-22, 12 `####` sections
each. After editing: same 22 IDs, same section count on every one.

---

## FIX 1: MED-03 load balancing (invalid XML, one overstated claim)

Rewrote both XML blocks to the real schema from
`api-platform_deploy_load-balancing-across-backend-servers.txt`.

| Was | Now | Source line |
| --- | --- | --- |
| `<LoadBalancing>` | `<LoadBalancer>` | L212, L250, L299 |
| `<TargetServer>orders-1</TargetServer>` | `<Server name="orders-1" />` | L213-214 |
| `<Algorithm>ROUND_ROBIN</Algorithm>` | `<Algorithm>RoundRobin</Algorithm>` | L237, L251 |
| `<MaxFailures>` on `HTTPTargetConnection` | `<MaxFailures>` inside `<LoadBalancer>` | L329 |
| `<MinTimeBetweenFailures>` | removed; appears in zero cached pages | grep over all 408 |
| `<ServerUnhealthyResponse>` outside `LB` | inside `<LoadBalancer>` | L330-335 |

Added the `<TargetEndpoint>` wrapper and `<Path>`, both shown in the doc's examples.

Verified the two claims the scenario rests on:

- **MaxFailures default 0 disables failover — PARTLY TRUE, corrected.** L342: "The MaxFailures
  default is 0. This means that Apigee always tries to connect to the target for each request and
  never removes the target server from the rotation." The scenario previously said MaxFailures 0
  means "no failover occurs". That is too strong: `<RetryEnabled>` defaults to `true` (L358) and
  retries are triggered by I/O exceptions and HTTP timeouts (L227), so a single failing request
  can still be redirected. What 0 actually prevents is *removal from rotation*. The ground truth
  and the ticket were rewritten around that distinction.
- **HTTP 500 resets the failure counter unless classified — TRUE.** L314 says so almost verbatim.
  Kept, now with the quoted wording.

The ticket previously said "every request still fails", which contradicts both the doc and its own
evidence line ("requests return 503 when a node is stopped"). Rewritten to describe the real
symptom: latency on every other request, then success via the other node.

Added a `<HealthMonitor>` to the remediation (documented, and required to be paired with
MaxFailures > 0, L539/L587) and the note that failover is invisible in Trace sessions (L352).

Also added an explicit wrong-answer entry naming `weightedRoundRobin` and
`leastConnectionsWithHealthCheck` as nonexistent, since both were recorded fabrications.

## FIX 2: MED-15 Java callout (was unsatisfiable)

`api-platform_reference_policies_java-callout-policy.txt` splits its error reference into two
tables:

- Runtime errors (L220-222): one row, `steps.javacallout.ExecutionError`, HTTP 500, "Occurs when
  Java code throws an exception or returns null".
- Deployment errors (L226-236): `JavaClassNotFoundInJavaResource`, `JavaCalloutInstantiationFailed`,
  `JavaClassDefinitionNotFound`, `NoAppropriateConstructor`, `ResourceDoesNotExist`,
  `NoResourceForURL`, `IncompatibleJavaVersion`. All have HTTP status N/A.

The scenario asserted `JavaClassNotFoundInJavaResource` at request time while stating deployment
succeeded. Now uses `javacallout.ExecutionError` in the documented payload shape, and makes the
runtime-versus-deployment table split the actual evaluation target. Difficulty preserved: the
agent still has to rule out the deployment table on deployment evidence, read the callout's
per-request state assumptions, and refuse to name an exception the fault code does not carry.

## FIX 3: MED-05 key-value maps (claim was attributed to the wrong page)

The single-node refresh claim is **documented, but not on the page it was cited to.**
`api-platform_cache_key-value-maps.txt` has two `cache` hits, neither about node-level refresh.

The real source is `api-platform_reference_policies_key-value-map-operations-policy.txt` L411:
"using `PUT` will only refresh the cache in the single runtime node that services the request.
To refresh the cache in each distributed runtime node, use the `<ExpiryTimeInSecs>` element".

That is a correction, not just a citation move. The same page L425 says "Updating a KVM with the
Apigee UI or API does not reset the KVM cache", so the documented behaviour belongs to the
**policy's** `PUT`, not to a Management API write. The old initial evidence said "The map is
updated through the Management API", which is precisely the case the claim does not cover.

Fixed by changing the write path to a policy `PUT` and adding the scoping as a scored element.
Also added three documented facts that were missing: there is no cross-node flush mechanism
(L423), the placeholder-`PUT` trick overwrites the value permanently (L424), and `private.`
prefixes what is exposed in Debug sessions rather than what is encrypted at rest (L473). The old
text said "verify they are in a secured map", which misdescribes the mechanism.

## FIX 4: MED-16..MED-22 audit

All seven origin IDs confirmed present in `research/issues/` and their claims checked against
source. All References URLs resolve (32 unique cloud.google.com URLs, each present in
`research/pages/`; the six missing MANIFEST rows were confirmed as real cached files).

- **MED-16** (api-platform-samples#7). Core diagnosis verified against the thread: Baskaran-md
  states the token request "is wrongly getting classified as authorization code request" and
  "Checked the deployments. It was not deployed properly", then names deployment base path vs
  proxy base path, not settable in the UI, defaulting to `/`. Two errors: (a) the scenario listed
  three parameter error strings as "documented in the OAuthV2 policy reference"; only
  `Required param : grant_type` (L2506) is. The documented code is `steps.oauth.v2.InvalidRequest`,
  HTTP 400, "used for multiple different kinds of errors, typically for missing or incorrect
  parameters" (L2249). Relabelled as a symptom, not a contract. (b) Initial evidence claimed "a
  second client on the same environment succeeds with a different `redirect_uri`", which contradicts
  a proxy-level base path fault. Replaced with "the authorize leg works", which is both consistent
  and is the strongest possible lure toward client-parameter fixes. Origin now marked closed-as-fixed.
- **MED-17** (apigee-deploy-maven-plugin#213). Message string, `Waiting to assert bundle
  activation.....`, `Deployment failed to activate`, and the hardcoded `Thread.sleep(10L)` all match
  the thread verbatim. Correction: the thread closes "Closing due to inactivity", not as fixed.
  Origin line and ground truth updated. Also sharpened the delay dispute: the maintainer's actual
  position was that the sleep is for reading deployment details, and he asked the reporter to lower
  the delay from 30 to 10 and find out why deployments were slow. The old text implied the reporter
  was simply wrong about the delay.
- **MED-18** (known issue 479872706). Fix (`ao.image.tag` / `mart.image.tag` =
  `1.16.0-hotfix.1`) and the MART credential-casting regression both verified (L257-270). Added the
  EKS scope from the register's "Affects" column, which the scenario omitted, and the full YAML
  from the register instead of a paraphrase. Second defect 479040521's missing
  `.Values.gcp.federatedWorkloadIdentity.enabled` check verified (L217-235).
- **MED-19** (known issue 543171828). `kubectl get daemonset apigee-logger -n apigee`, desired
  count 0, the `apigee.cloud.google.com/apigee-logger-enabled: "true"` default, the overrides.yaml
  clear-selector block, the label command, the 1.16.9 fix, and the GKE/GKE-on-prem on / AKS off
  platform defaults are all quoted correctly. No changes beyond the Origin line. This one was clean.
- **MED-20** (known issues 471125841 + 246774745). Verified. Three fixes: added the version scope
  (1.14.x, 1.15.x; fixed in 1.16.x) to the ticket and ground truth, since "restart the pods" is
  only correct pre-1.16; added upgrade as the primary remediation with the rolling restart as the
  documented workaround for affected versions; fixed a **malformed rubric** where "Diagnostic method"
  appeared twice as a row label, now "Evidence use". Origin marked both FIXED.
- **MED-21** (apigeelint#526). TD012 and TD006 messages match the thread verbatim. Two fixes:
  the thread's resolution was **three** changes (demote TD006, narrow TD012, change TD015), not two;
  and the MaxFailures antipattern was a real, documented member of the same thread, not an aside,
  so it is now a scored element with its own wrong answer. Added TD015 to the initial evidence so
  the three-way warning set is visible.
- **MED-22** (known issue 465834046). cert-manager 1.18 `Never`->`Always`, the upgraded-clusters-only
  scope, the "will cause an outage" quote, the patch command, and the 1.17.x ceiling all verified.
  One substantive correction: the old ground truth asserted the current intermittent failures and
  the future outage "share a cause". The register documents a *future* rotation-triggered outage
  and says nothing about a present fault. Rewritten so the agent must say the register does not
  explain the present symptom. Cassandra sentence sharpened to the doc's wording (mixed hybrid
  versions).

## FIX 5: file-wide

- `context.request.getValue("items")` does not exist. No such method appears in any of the 408
  cached pages; the JavaScript object model documents `context.getVariable(...)`, including the
  `request.queryparam.*` form at L1142. Replaced with `context.getVariable("request.queryparam.items")`.
- `AM-Target-Endpoint` (MED-06) and `AM-` style names are not documented trace step names.
  `AM-` appears in the cache only as a user-chosen policy naming prefix in fault-handling examples.
  Genericised to "the target endpoint step", with a note that step names are customer-defined.
- `SC-Enrich` (MED-12) is a customer policy name, not a claim about Apigee. Labelled as theirs
  rather than deleted, and paired with the documented `<Timeout>` element and its 500 behaviour (L519).

## Also fixed

- Header said "Fifteen cases"; there are 22. Corrected, with a line distinguishing the documented
  and synthetic scenarios from the seven imported ones.
- MED-02 asserted a deployment state value `DEPLOYING`. Only `READY` and the per-pod
  `deploymentStatus: deployed` are documented (L106-111, L154). Rewritten to those.
- MED-07 used `**Critical failures:**` as bold text where all 21 others use a `####` heading.
  Normalised, which also brings it to 12 sections like every other scenario.

## Not changed, flagged

- MED-07 and MED-22 cite `setSyncAuthorization` and the Apigee Synchronizer Manager role.
  **RETRACTED, this caveat was wrong.** A later review found `setSyncAuthorization` in
  `hybrid_v1.17_synchronizer-access.txt` at lines 94, 111, 129, 146, 165 and 171, and the
  `Switched to newer version N from version M` contract marker documented in
  `hybrid_v1.17_runtime-logs.txt` at lines 74 and 77. MED-07 needs no change and is correct as
  written. Recorded here because a wrong caveat in a fix report invites a later pass to
  "correct" working content.
- MED-21 cites "Advanced API Security" issuing the competing TLS warning. That comes from the
  issue thread, not from Google documentation, so it has no reference. Left as-is and attributed to
  the discussion context by its position in the scenario.
## MED-04: invented element, self-contradiction, and a real two-page conflict

### `<Key>` does not exist in ResponseCache

Verified element set, from
`research/pages/api-platform_reference_policies_response-cache-policy.txt`:

```
$ grep -oE '^## \\<[A-Za-z/]+[a-z]\\?> element' pages/api-platform_reference_policies_response-cache-policy.txt
## \<DisplayName\> element   ## \<CacheKey\> element     ## \<CacheLookupTimeoutInSeconds\> element
## \<CacheResource\> element ## \<ExcludeErrorResponse\> element  ## \<ExpirySettings\> element
## \<Scope\> element         ## \<SkipCacheLookup\> element  ## \<SkipCachePopulation\> element
## \<UseAcceptHeader\> element  ## \<UseResponseCacheHeaders\> element
```

`grep -c '<Key>'` returns 0 on both the ResponseCache page and the working-cachekeys
page. The name is real, but only in the JWT policies: `GenerateJWT` and `VerifyJWT` both
document `<Key>` as a required child of `<Algorithms>`, where it names the key
algorithm. Note this is `<Algorithms>`, not `<Encryption>` as the task brief described.
The task brief's conclusion is right, its parent element is wrong; the fix text cites
`<Algorithms>` because that is what the cache says.

Fixed: the scenario's Diagnostic evidence now shows a real policy using `<CacheKey>` and
`<KeyFragment>`, and states plainly that `<Key>` is not a ResponseCache element.

### Second invented element found while fixing the first

The same section also used `expiryInSeconds`, which appears nowhere on the ResponseCache
page. The real element is `<TimeoutInSeconds>` inside `<ExpirySettings>`, where
`<TimeoutInSeconds>` overrides both `<TimeOfDay>` and `<ExpiryDate>`. Fixed in Initial
evidence and in Common incorrect answers. This was not in the brief but sat inside the
same defect class in the same scenario, so leaving it would have half-fixed the problem.

### The self-contradiction

The remediation told the agent to "use documented guidance rather than inventing an
expression" while the Diagnostic evidence above it supplied an invented one. The
remediation now shows the corrected `<CacheKey>` with added fragments, so the advice and
the example agree.

### The two pages genuinely conflict on `<Scope>Exclusive`, and the scenario now says so

Both pages agree `Exclusive` is the default `<Scope>` value. They disagree on what the
prefix contains:

- ResponseCache policy reference: `orgName__envName__apiProxyName__proxy|TargetName__[serializedCacheKey]`,
  example `apifactory__test__weatherapi__default__apiAccessToken`. No revision number.
- Working with cache keys: `orgName__envName__apiProxyName__deployedRevisionNumber__nameof(proxyEndpoint|targetEndpoint)__[serializedCacheKey]`,
  example `mycompany__prod__weatherapi__16__default__hello__world`. Carries revision 16.

Both agree that a `<Prefix>` inside `<CacheKey>` supersedes the scope value.

The scenario states the conflict explicitly with both forms, both examples, and the note
that which form is implemented decides whether a new revision starts from an empty cache
or inherits the previous revision's entries. That consequence is labelled an inference in
the text, because it follows from comparing the two documented forms and neither page
states it. No page was picked silently, and a bare "the key looks like X" claim was added
to Common incorrect answers.

The remediation also directs the agent at the read-only
`responsecache.{policy_name}.cachekey` variable to read the real key instead of reasoning
about it, and warns that changing the key orphans existing entries rather than
invalidating them.

## MED-15: missing `steps.` prefix on the fault code

```
$ grep -oE '`steps\.javacallout\.[A-Za-z]+`|`[a-z]+\.javacallout\.[A-Za-z]+`' pages/*java-callout*.txt | sort -u
pages/api-platform_reference_policies_java-callout-policy.txt:`steps.javacallout.ExecutionError`
```

Exactly one code, with the prefix. HTTP 500, cause "Occurs when Java code throws an
exception or returns null during the execution of a `JavaCallout policy`". The
`error-codes.md` reference agrees: `steps.javacallout.ExecutionError`, 500.

Fixed in all three places the bare form appeared: the JSON payload, the Diagnostic
evidence, and the Ground-truth resolution.

Worth recording, because it is the likely origin of the defect and a later reviewer may
"correct" the fix back. The same java-callout-policy page carries an "Example error
response" block further down whose body reads `"errorcode":"javacallout.ExecutionError"`
with no prefix. The page contradicts itself: the runtime errors table and the dedicated
runtime errors page both carry `steps.`, the example block does not. Since this scenario's
entire evaluation target is exact-code discipline, the text now names the discrepancy
explicitly and says which of the two is authoritative, instead of leaving a reader to
copy the example block.

## Verification

All 22 scenario IDs unchanged and in order, `grep -c '^### MED-'` = 22, both touched
sections keep the full section structure, code fences balanced at 26 (even), and the
payload keeps the required nested shape `{"fault":{"detail":{"errorcode":"..."}}}`.
Remaining `<Key>` mentions are the deliberate negations, and the one remaining bare
`javacallout.ExecutionError` is the intentional contrast in the Ground-truth resolution.
