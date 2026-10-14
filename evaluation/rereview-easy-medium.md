# Blind re-review: scenarios/easy.md and scenarios/medium.md

Scope: 15 EASY scenarios, 22 MED scenarios. All verification against the 408 cached pages in
`research/pages/`, `research/issues/`, and
`.agents/skills/apigee-support-core/references/error-codes.md`. No network used.

The previous fix pass fixed most of what it claimed to. The remaining defects cluster in two
places: EASY-06 (ground truth asserts behaviour the docs contradict) and the two scenarios with
invented XML elements (EASY-10, MED-04). The `context.variable(...)` error class survived the
`context.request.getValue` fix in a new location.

---

## EASY-01 Quota policy rejects the revision over a fractional interval

**Verdict**: CORRECT

**Issues**: none.

Verified: `InvalidQuotaInterval` is a deployment error on the Quota page
(`api-platform_reference_policies_quota-policy.txt` L1876; deploy-errors page L40 "If the quota
interval specified in the `<Interval>` element of the Quota Policy is not an integer, then the
deployment of the API proxy fails"). `QuotaViolation` is HTTP 500 in the runtime errors table
(L1868). The `<TimeUnit>second</TimeUnit>` remediation is documented (L1030) and legal here
because `<Distributed>` defaults to `false` (L1101-1110), which the scenario correctly conditions
on with "Confirm `second` is a supported `<TimeUnit>` value before recommending it."

---

## EASY-02 Missing Interval produces a runtime 500, not a deploy failure

**Verdict**: CORRECT

**Issues**: none.

Verified: `policies.ratelimit.FailedToResolveQuotaIntervalReference` HTTP 500, cause "Occurs if
the `<Interval>` element is not defined within the `<Quota>` policy. This element is mandatory"
(quota-policy L1865). The conditional-flow mechanism in the diagnostic evidence is sound and the
ground truth correctly separates it from the deployment error in EASY-01.

---

## EASY-03 FlowCallout cannot find the shared flow

**Verdict**: CORRECT

**Issues**: none.

Verified: `flow.SharedFlowNotFound` HTTP 500, cause "Either the shared flow does not exist, or the
shared flow exists but is not deployed"
(`api-platform_reference_policies_flow-callout-policy.txt` L412). The two-cause framing and the
"resolved at request time, not at upload" reasoning follow from the documented cause.

---

## EASY-04 AccessControl blocks a corporate IP range

**Verdict**: CORRECT

**Issues**: none.

The fix from the previous pass is good. Verified the XML against
`api-platform_reference_policies_access-control-policy.txt` L32-36: `IPRules noRuleMatchAction`,
`MatchRule action="DENY"`, `SourceAddress mask="24"` all real and correctly nested. `SourceAddress`
is the element named in the documented cause for `accesscontrol.IPDeniedAccess`, HTTP 403 (fault
table, AccessControl page). The TEST-NET-3 aside is a correct observation, not a doc claim.

---

## EASY-05 JavaScript policy blocked by a security violation

**Verdict**: MINOR

**Issues**:

1. **`context.variable(...)` is not a documented API.** easy.md lines 546 and 561:
   `context.variable("token", loadCredential(token));` and `context.variable("token", token);`.
   The JavaScript object model documents `context.getVariable()` and `context.setVariable()`
   (`api-platform_reference_javascript-object-model.txt` L909-920: "**context.setVariable()** Sets
   the value for a custom variable"; L34, L112, L538 and every other example uses `setVariable`).
   `grep -rn "context.variable" research/pages/` returns **zero** hits for the two-argument method
   form. This is the identical error class the previous fix pass was chartered to remove
   (`fix-easy.md` FIX 4 removed `context.request.getValue`); the replacement code introduced a
   second undocumented call in the same lines. Impact is bounded because the scenario is about
   `ScriptSecurityError`, not about the setter, and the fault code and 500 status are correct —
   hence MINOR rather than MATERIAL.

2. Scenario correctly avoids the previously-reported `getValue` form. The `ScriptSecurityError`
   row is real: HTTP 500, "A security error occurred when the `JavaScript` executed. See the fault
   string for details" (javascript-policy page, runtime errors table). The fix-column reading is
   accurate.

---

## EASY-06 BasicAuthentication cannot resolve its source variable

**Verdict**: MATERIAL

**Issues**:

1. **The ground truth states platform behaviour that the cited documentation contradicts.**
   easy.md lines 695-700 assert: "HTTP header names are case-insensitive on the wire, but Apigee
   flow variable names are case-sensitive, so `request.header.Authorization` and
   `request.header.authorization` are different variables. This surprises people regularly."

   No cached page documents this, and the docs cut the other way. `verify-jws-policy.txt` L444:
   "By default, the JWS is retrieved from the variable **request.header.authorization**. In this
   case, Apigee looks for the JWS in the request Authorization header." Same for
   `decode-jws-policy.txt` L116 and `decode-jwt-policy.txt` L84 — the *lowercase* variable name is
   the documented default for the `Authorization` header. Meanwhile `basic-authentication-policy.txt`
   L115/L298/L305 uses `request.header.Authorization` for that same header. Both spellings are
   documented defaults for the same wire header, which is only coherent if header-variable lookup
   is not case-distinguishing in the way the scenario claims. Further, `variables-reference.txt`
   L1597 pairs the header `Cache-control` with the variable `request.header.cache-control` — a
   mixed-case header read through a lowercase variable, again inconsistent with a strict
   case-sensitivity rule.

   This is not a documentation gap that a careful agent could resolve; it is an assertion presented
   as settled fact, and the wrong side of it, resting the entire ground truth. Under review rule 9
   ("any claim that is plausible but NOT documented is labelled as such") this must either be
   sourced or relabelled as a hypothesis.

2. **The remediation does not work under either reading.** The AssignMessage block (lines
   713-718) copies `{request.header.authorization}` into `<Header name="Authorization">`. If the
   scenario's own case-sensitivity claim is true, then `<Source>request.header.Authorization</Source>`
   should have matched the incoming header and the fault cannot be occurring as described — the
   premise is self-defeating. If lookup is actually case-insensitive, the AssignMessage is a no-op
   and fixes nothing. The scenario hedges with "Confirm the header actually exists under the
   lowercase name before writing this", which papers over the contradiction rather than resolving
   it.

3. Consequence for scoring: the rubric's 4-point band is "Explains wire case-insensitivity versus
   variable case-sensitivity", and "Critical failures" lists three wrong answers that all depend on
   the same unverified claim. A correct answer would be scored as a critical failure. The fault
   code itself (`steps.basicauthentication.UnresolvedVariable`, HTTP 500, "This error can only
   occur if `IgnoreUnresolvedVariables` is false") is correct and well used, and that part of the
   scenario is sound.

---

## EASY-07 JWS algorithm does not match between generate and verify

**Verdict**: CORRECT

**Issues**: none.

Verified: `steps.jws.AlgorithmMismatch` HTTP 401, cause "The algorithm specified in the header by
the `Generate` policy did not match the one expected in the `Verify` policy"
(`api-platform_reference_policies_verify-jws-policy.txt`). PS256 is a real Apigee algorithm and the
scenario correctly distinguishes platform support from the single configured value.

---

## EASY-08 InvalidMessageWeight does not tell you which policy failed

**Verdict**: CORRECT

**Issues**: none.

Verified the shared-code claim on both pages: `policies.ratelimit.InvalidMessageWeight`, HTTP 500,
"the value ... specified through a flow variable is invalid (a non-integer value)" appears on the
Quota page L1867 and the SpikeArrest page L727. The trace-step discriminator is sound, and the
previous pass's replacement of invented step names with policy-type labels plus an explicit note is
the right call. The `parseInt`/`isNaN` remediation uses documented object-model calls.

---

## EASY-09 JSONToXML cannot resolve its source variable

**Verdict**: CORRECT

**Issues**: none.

Verified: `steps.jsontoxml.InvalidSourceType` HTTP 500, "the type of the variable used to define
the Source element is invalid. The valid types of variable are message and string", and the
sibling `steps.jsontoxml.SourceUnavailable` for out-of-scope/unresolvable
(`api-platform_reference_policies_json-xml-policy.txt`). The `<OutputVariable>` mandatory-when-
source-is-`string` rule is quoted correctly from the same table. `request.content` is the correct
variable.

---

## EASY-10 HMAC policy missing a required element

**Verdict**: MATERIAL

**Issues**:

1. **Two XML elements in the scenario do not exist.** Line 1169: "There is no `<SecretVariable>`,
   no secret reference, and no `<VerificationOutput VariableToVerify>`." The HMAC policy has no
   `<SecretVariable>` element and no `<VerificationOutputVariableToVerify>` element. The real
   elements are `<SecretKey>` (required, ref attribute) and `<VerificationValue>` (optional).
   Verified from the element reference of `api-platform_reference_policies_hmac-policy.txt`:
   sections are `<Algorithm>`, `<DisplayName>`, `<Message>`, `<Output>`, `<SecretKey>`,
   `<VerificationValue>`, `<IgnoreUnresolvedVariables>` — that is the complete list.
   `grep -rn "SecretVariable" research/pages/` and `grep -rn "VerificationOutputVariableToVerify"`
   both return zero hits across all 408 pages. Naming invented elements as the thing that is
   *absent* is worse than naming them as present, because the absent element is what the reader is
   supposed to go and add.

2. **The scenario's own diagnosis is not reachable from its evidence.** The ground truth says the
   trigger is a missing `<SecretVariable>`/secret reference. But the bundled policy also omits
   `<Message>`, which the same page marks **Presence: Required** (L156-190), and `<SecretKey>`,
   also **Required** (L209). Any of those absent elements produces
   `steps.hmac.MissingConfigurationElement`. The agent cannot distinguish which required element
   the template failed to render, and the rubric rewards naming the specific one. Minor relative to
   issue 1 but worth noting.

3. **Positive note on what was fixed.** The previous pass's central correction is right and should
   not be reverted: the documentation lists `steps.hmac.MissingConfigurationElement` under
   **Deployment errors** with HTTP status 401 (hmac-policy L350-356), not as a runtime fault. The
   scenario's framing — save-time rejection, 400, traffic on the old revision still served — is
   consistent with a deployment error, and its explicit "Despite the `steps.` prefix" note is the
   right teaching point. The fault code is real and in `error-codes.md`. The "missing element vs
   wrong value vs unresolved variable are three different failures with three different codes"
   distinction is accurate per the table.

---

## EASY-11 Unsupported TimeUnit blocks the revision

**Verdict**: CORRECT

**Issues**: none.

Verified against the Quota deployment-errors page L142 and the Quota policy page L1877: "The
supported time units are `minute`, `hour`, `day`, `week`, and `month`." The `InvalidQuotaTimeUnit`
name, the 400-on-save framing, and the plural-vs-singular point are all correct.

---

## EASY-12 RevokeOAuthV2 rejects a timestamp before 2014-01-01

**Verdict**: CORRECT

**Issues**: none. This is the cleanest rewrite in the file.

Verified against `api-platform_reference_policies_revoke-oauth-v2-policy.txt`:

- `steps.oauth.v2.InvalidEarlyTimestamp`, HTTP 500, "Timestamp cannot be earlier than January 1,
  2014." (L315) — matches the known facts and the scenario exactly.
- Siblings `InvalidFutureTimestamp` (500, "cannot be in the future") and `InvalidTimestamp` (500,
  "Timestamp is invalid") both real (L313-316); the scenario keeps them distinct rather than
  collapsing them.
- `<RevokeBeforeTimestamp>` type "64-bit (long) integer representing the number of milliseconds
  elapsed since midnight, on January 1, 1970 UTC" and "cannot be in the future and cannot be before
  January 1, 2014" (L297-298). Both halves of the two-trigger story (absent param resolving to 0,
  and seconds read as milliseconds) land on the documented bound.
- The note that the element is optional and defaults to execution time is consistent with the
  element reference.

---

## EASY-13 JWKS verification fails because the token has no key id

**Verdict**: CORRECT

**Issues**: none.

Verified: `api-platform_reference_policies_jwt-policies-overview.txt` L356 gives the resolution
step verbatim — "Examine the JWS/JWT header to find the Key ID (kid). If the inbound JWT does not
include a key ID (kid) in the header, then the mapping of kid to verification-key is not possible,
and Apigee will throw a fault." The scenario paraphrases this accurately and does not invent a
fault code. The corroborating code `steps.jwt.KeyIdMissing`, HTTP 401, is real
(`verify-jwt-policy.txt` L1202) though the scenario does not need to cite it.

---

## EASY-14 Target handshake fails against a legacy TLS backend

**Verdict**: CORRECT

**Issues**: none. The previous pass's reframing is sound and should be kept.

Verified: `api-platform_system-administration_options-configuring-tls.txt` L8 — "Apigee does not
support the use of TLS 1.0 or TLS1.1. If you use these protocols in your target endpoint
configuration, the Apigee target endpoint throws the error
`messaging.adaptors.http.flow.SslHandshakeFailed`." Independently,
`mon_fault-codes.txt` L77 maps `Target` / `FailedHandshakeWithTargetEndpoint` to the same
errorcode. The scenario's "Caveat on the fault code" subsection states both sources and says no
policy raises it — correct, and it satisfies the brief's stated exception. The `<Protocols>`
ground truth is quoted accurately from the Configuring TLS page L100-101: "If no protocols are
specified, then all protocols available for the JVM will be permitted", so `<Protocols>` can only
narrow, never widen. `<SSLInfo>`/`<Enabled>` are real.

---

## EASY-15 Quota counter behaves differently than the team expects

**Verdict**: CORRECT

**Issues**: none.

Verified near-verbatim: `api-platform_reference_policies_quota-policy.txt` L14 — "Quotas apply to
individual API proxies and are not distributed among API proxies. For example, if you have three
API proxies in an API product, a single quota is not shared across all three even if all three use
the same quota policy configuration." The scenario's ground truth matches this exactly, including
the three-proxy arithmetic.

---

## MED-01 Deployed successfully, every request returns 404

**Verdict**: CORRECT

**Issues**: none.

Verified: `api-platform_fundamentals_environments-overview.txt` L16 — "An environment must be a
member of at least one environment group before you can access proxies deployed within it. In other
words, you must assign an environment to a group before you can use it." Also L95 of
environmentgroups-working-with: "Environments that are not in a group cannot be accessed because
there is no host name associated with them. Host names are defined on the environment group, not
the environment." The Edge-scoping note is consistent with
`api-platform_get-started_compare-apigee-products.txt` L44 listing "Support for environment groups"
under Apigee features only.

---

## MED-02 Works for some users, 404s for others, same deployment

**Verdict**: CORRECT

**Issues**: none.

Verified: `api-platform_deploy_ui-deploy-overview.txt` L19 — "MPs act independently of one another
and any given MP can be in a different state than the other MPs (such as active or disabled). This
is known as an *eventually consistent* deployment model for API proxies." The `READY` state value
and the per-pod `deploymentStatus` values `deployed` / `error` / `pending` are real fields
(`rev-env-deployments-res.txt` PodStatus schema). The previous pass's correction of `DEPLOYING` to
`READY` is right. The deliberate cross-reference to MED-01's environment-group issue is labelled
as a second, independent problem rather than conflated — good handling.

---

## MED-03 Load balancing does not fail over to a healthy backend

**Verdict**: CORRECT

**Issues**: none. This is the most-improved scenario in the file.

Verified every element in both XML blocks against
`api-platform_deploy_load-balancing-across-backend-servers.txt`: `<LoadBalancer>` (not
`<LoadBalancing>`), `<Algorithm>RoundRobin</Algorithm>` (L251, one of exactly three documented
values — RoundRobin, Weighted, LeastConnections, L235-299), `<Server name="..."/>` (L213-214),
`<MaxFailures>` nested inside `<LoadBalancer>` (L329), `<ServerUnhealthyResponse>` with
`<ResponseCode>` children inside `<LoadBalancer>` (L330-335), `<HealthMonitor>` as a child of
`<HTTPTargetConnection>` with `<IsEnabled>`/`<IntervalInSec>`/`<TCPMonitor>`/`<ConnectTimeoutInSec>`
(L610-623). The remediation block is structurally identical to the documented sample.

Two substantive claims both check out:

- MaxFailures default 0, quoted from L342: "This means that Apigee always tries to connect to the
  target for each request and never removes the target server from the rotation."
- HTTP 500 does not count as a failure, quoted from L314: "even if the response is an HTTP error
  (such as `404` or `500`), that counts as a response from the target server, and the failure
  counter is reset."

The `<RetryEnabled>` default `true` and its I/O-error-and-timeout triggers are correct (L358), and
the past pass correctly softened the old over-broad "no failover occurs" claim. The Trace-session
invisibility note is quoted from L352. The explicit `weightedRoundRobin` /
`leastConnectionsWithHealthCheck` wrong-answer entry is a good guard against exactly the
fabrications flagged previously.

---

## MED-04 Cached responses are stale and nobody can reproduce it

**Verdict**: MATERIAL

**Issues**:

1. **`<Key>` is not a ResponseCache element.** medium.md line 389: "The ResponseCache policy has a
   `<Key>` expression that includes the request URL but not the caller's identity or any version
   header." The ResponseCache policy has no `<Key>` element. The real elements are `<CacheKey>`
   with `<Prefix>` and one or more `<KeyFragment>` children, plus `<Scope>`
   (`api-platform_reference_policies_response-cache-policy.txt` L248 `<CacheKey>`, L328
   `<CacheKey>`/`<KeyFragment>`, L366 `<CacheKey>`/`<Prefix>`, L580 `<Scope>`;
   `api-platform_reference_policies_working-cachekeys.txt` L8, L27, L29). `grep -c "^## \\<Key\\>"
   ` on the ResponseCache reference returns 0. A repo-wide grep finds `<Key>` only inside
   `<Encryption>` in the GenerateJWT / VerifyJWT / JWT-overview pages, where it is the key-encryption
   algorithm — an unrelated element in an unrelated policy.

   The remediation tells the agent to "widen the cache key ... There is documented guidance on
   constructing cache keys; use it rather than inventing an expression" — while the scenario itself
   supplies an invented element name. That is a self-undermining instruction and exactly the error
   class flagged in the prior review round.

2. Scenario is otherwise sound and worth keeping. The two-layer staleness reasoning, the
   cross-tenant key defect, and the "measure before disabling" remediation are all coherent and
   correctly labelled synthetic. The rubric's critical failure ("missing the cross-tenant cache key
   defect") is a good discriminator. Only the element name needs fixing — it should be
   `<CacheKey>` with `<KeyFragment>` children, e.g. the documented
   `<KeyFragment ref="request.uri" />` (ResponseCache page L136).

---

## MED-05 Key value map updates are not visible everywhere

**Verdict**: CORRECT

**Issues**: none. The previous pass's rewrite is accurate and the scoping is the strongest part of
it.

Verified against `api-platform_reference_policies_key-value-map-operations-policy.txt`:

- L411: "using `PUT` will only refresh the cache in the single runtime node that services the
  request. To refresh the cache in each distributed runtime node, use the `<ExpiryTimeInSecs>`
  element to specify refresh intervals for each node" — quoted verbatim in the ground truth.
- L425: "Updating a KVM with the Apigee UI or API does not reset the KVM cache" — the scenario uses
  this to scope the claim to the policy path, which is the correct and previously-missing nuance.
- L423-424: no cross-node flush mechanism, and the placeholder-`PUT` trap overwrites the stored
  value permanently. Both present and correct.
- `private.` prefix correctly described as what hides a value from Debug sessions, not what
  encrypts it at rest (`api-platform_cache_key-value-maps.txt` L130, L258). The previous pass
  fixed a real error here.

---

## MED-06 Latency jumped and nobody knows which layer moved

**Verdict**: CORRECT

**Issues**: none.

Labelled synthetic, appropriately hedged ("the measurement is" the proof, not the timing
correlation), and the trace-vs-external-measurement methodology is sound. Removing the invented
`AM-Target-Endpoint` step name and noting that step names are customer-defined is the right call.

---

## MED-07 Deployment succeeds on hybrid but the runtime never applies it

**Verdict**: MINOR

**Issues**:

1. **The `setSyncAuthorization` flag from the previous pass is a false alarm, and the pass was
   right to leave it in.** `fix-medium.md` L159-163 states the method name "appears in no cached
   page" and is "not locally verifiable". That is incorrect. `hybrid_v1.17_synchronizer-access.txt`
   L94, L111, L129, L146, L165, L171 documents the `setSyncAuthorization` API and its call form,
   including the control-plane-hostname variant. The claim is documented. No scenario change needed;
   the fix report's caveat should be retracted.

2. **The `Switched to newer version N from version M` marker is also documented**, contrary to the
   impression left by the fix report: `hybrid_v1.17_runtime-logs.txt` L74 and L77 give the exact
   line format and what it means ("The MP changed to a newer version of the configuration
   contract"). The scenario's use of it as the verification signal is sound.

3. **Reference gap.** MED-07's References list only "What is Apigee hybrid" and "Compare Apigee
   products". Neither supports the load-bearing claims (`setSyncAuthorization`, the Synchronizer
   Manager role, the pod-log contract-version marker). A reader cannot follow the citation to the
   page that does. Worth adding `hybrid/v1.17/synchronizer-access` and `hybrid/v1.17/runtime-logs`.
   This is a citation completeness issue, not a factual error, hence MINOR.

---

## MED-08 Mutual TLS broke after a certificate authority renewal

**Verdict**: CORRECT

**Issues**: none.

Well documented: `api-platform_reference_api-proxy-configuration-reference.txt` L745-747 — "Public
Certificate Authorities (CAs) are discontinuing the inclusion of the `clientAuth` Extended Key
Usage (EKU) in latest publicly-trusted SSL/TLS certificates... Apigee requires the `clientAuth`
EKU to be present in client certificates for mTLS handshakes. Without this EKU, mTLS connections
will fail for both northbound (client to Apigee) and southbound (Apigee to backend) traffic." The
scenario's two-sided failure and its instruction to inspect EKU before chains or keystores both
follow directly.

---

## MED-09 Intermittent 429 under bursty client traffic

**Verdict**: MINOR

**Issues**:

1. **Title/evidence contradiction.** The title (line 849) says "Intermittent **429**", but the
   scenario's Initial evidence (line 873) and its whole analysis are about
   `policies.ratelimit.QuotaViolation` with **HTTP 500**. In the documentation the Quota page's
   runtime error table gives `policies.ratelimit.QuotaViolation` = **500**
   (`api-platform_reference_policies_quota-policy.txt` L1868), while the SpikeArrest page gives
   `policies.ratelimit.SpikeArrestViolation` = **429** (L733) — and the Quota page carries a
   trailing note (L1931) that the system returns `429 Too Many Requests` when Quota or SpikeArrest
   thresholds are exceeded.

   So the source documentation is itself internally inconsistent on this point, but the scenario
   inherits only one half of it. It asserts 500 in the body while its own title tells the agent to
   expect 429, and it never flags the discrepancy. An agent that correctly answers "429, per the
   note on the Quota page" would appear to contradict the ticket. Either align the title to the
   evidence, or make the 500-vs-429 conflict part of the scenario. MINOR because the substantive
   teaching point — Quota enforces correctly, policy choice is wrong — is correct and matches the
   documented guidance in `comparing-quota-and-spike-arrest-policies.txt` ("Don't use it to:
   Protect your API proxy's target backend against traffic spikes. Use SpikeArrest ... for that.").

2. SpikeArrest default values referenced but not quoted; the remediation correctly says to "Check
   the documented defaults for both before choosing values" rather than inventing them. Fine.

---

## MED-10 Token works against one API and fails against another

**Verdict**: CORRECT

**Issues**: none.

Verified: `steps.oauth.v2.access_token_expired` is **500** on both
`api-platform_reference_policies_get-oauth-v2-info-policy.txt` L451 and
`api-platform_reference_policies_set-oauth-v2-info-policy.txt` L193, while
`InvalidAPICallAsNoApiProductMatchFound` is **401** on both — confirming statuses are
policy-specific rather than condition-specific. The remediation aside is also accurate: the OAuthV2
page L2244 and L2275 both carry the note "It is recommended that you change existing fault rule
conditions to catch both the `invalid_client` and `InvalidClientIdentifier` names", and those two
names are precisely the ones that split on `<GenerateResponse>` true vs false (L2244 vs L2275).
The rubric line "Verifies expired and valid on both" is well matched to the diagnostic work.

---

## MED-11 Everything works in test and fails in production

**Verdict**: CORRECT

**Issues**: none.

Labelled synthetic, appropriately generic, and the KVM-environment-scoping mechanism is real
(environment-scoped KVM maps are documented, and MED-05's verified per-node caching facts make
this consistent). No undocumented claims, no invented elements.

---

## MED-12 Service callout times out and takes the request with it

**Verdict**: CORRECT

**Issues**: none.

Verified: `<Timeout>` is a real ServiceCallout element
(`api-platform_reference_policies_service-callout-policy.txt` L517-526), and the scenario's stated
behaviour is quoted almost verbatim from the doc: "If the ServiceCallout hits a timeout, an HTTP
500 is returned, the policy fails, and the API proxy goes into an error state." The p95-vs-p99.9
reasoning is correct statistical hygiene, and the scenario explicitly says step names are the
customer's. `SC-Enrich` being labelled as the customer's own name rather than an Apigee convention
is the right treatment.

---

## MED-13 Two conditions produce the same error code

**Verdict**: CORRECT

**Issues**: none.

Verified: `steps.javascript.ScriptExecutionFailed` HTTP 500, "The JavaScript policy can throw many
different types of ScriptExecutionFailed errors"
(`api-platform_troubleshoot_policies_runtime_javascript-runtime-errors.txt` L39; also
`api-platform_reference_policies_javascript-policy.txt`). The scenario's "the fault string is where
the detail lives" is documented at L101 of the runtime-errors page ("You can find all this
information in the `faultstring` element of the error response"). The distinction it draws — fault
string useful for diagnosis, error code for handling — is the correct one and matches the
"what-you-need-know-about-policy-errors" guidance the file cites.

---

## MED-14 A revoked token still works for a few minutes

**Verdict**: CORRECT

**Issues**: none.

Verified verbatim: `api-platform_reference_policies_oauthv2-policy.txt` L1108 — "OAuth tokens are
cached for three minutes (180 seconds); therefore, a revoked token may still succeed for up to three
minutes, until its cache limit expires." The 09:15-to-09:18 window matches exactly. The
"no documented supported way to force-flush token caches" wrong answer is a correct negative, and
the security framing (revocation alone is insufficient for immediate lockout) is the right
instinct to reward.

---

## MED-15 A Java callout fails only on some requests

**Verdict**: MATERIAL

**Issues**:

1. **The fault code in the payload is missing its `steps.` prefix.** line 1436:
   `{"fault":{"detail":{"errorcode":"javacallout.ExecutionError"}}}`, repeated at lines 1452 and
   1457. The documented code is **`steps.javacallout.ExecutionError`**
   (`api-platform_reference_policies_java-callout-policy.txt` L220-222, and
   `error-codes.md` L14). The bare form appears in zero cached pages.

   This is not cosmetic here, because the scenario's entire evaluation target is exact-code
   discipline: the rubric's 4-point band is "Uses the runtime table and rules out the deployment
   table" and a critical failure is "naming a deployment error name as the runtime cause". Training
   on a payload with a malformed `errorcode` undercuts the exact behaviour being graded, and the
   brief's rule is explicit that fault codes must exist in `error-codes.md` — where this one is
   recorded only in the `steps.` form.

2. Everything else in this scenario is right and should be preserved. Verified: `javacallout.ExecutionError`
   is the policy's **only** runtime error, HTTP 500, "Occurs when Java code throws an exception or
   returns null during the execution of a `JavaCallout policy`". All six names the ground truth
   redirects away from — `JavaClassNotFoundInJavaResource`, `JavaCalloutInstantiationFailed`,
   `JavaClassDefinitionNotFound`, `NoAppropriateConstructor`, `ResourceDoesNotExist`,
   `NoResourceForURL` — are real, and all sit in the deployment-errors table with HTTP status N/A.
   The faultstring quote is exact (L257: `"faultstring":"Failed to execute JavaCallout. [policy_name]"`).
   The honesty constraint ("the fault code and the generic faultstring do not carry the exception")
   is a genuinely good evaluation design and the difficulty rating is right.

---

## MED-16 The OAuth error names a missing parameter

**Verdict**: MINOR

**Issues**:

1. **The file header's absolute claim does not hold for this scenario.** medium.md L11-13: "Fault
   codes are real and live in `.agents/skills/apigee-support-core/references/error-codes.md`. Do not
   add codes that are not in that file." `steps.oauth.v2.InvalidRequest` — used at line 1564 and
   named in two wrong answers — is documented on the OAuthV2 policy page L2250 with HTTP 400, but
   `grep "InvalidRequest" error-codes.md` returns **zero** hits. The code is real and the status is
   right, so this is an index-coverage gap rather than a factual error; but the header states the
   rule without the exception carve-out that easy.md provides for EASY-14. Either add the exception
   sentence or add the code to the index.

2. Everything else verifies. `steps.oauth.v2.InvalidRequest`, 400, "This error name is used for
   multiple different kinds of errors, typically for missing or incorrect parameters sent in the
   request" — the scenario's reading of it as a coarse, non-contractual signal is exactly right, and
   the error-codes.md top guidance ("Take the `errorcode` from the response body, not the
   `faultstring` prose") is what makes this the right lesson. The origin thread
   (`research/issues/apigee_api-platform-samples-7.txt`) supports the narrative: L272 "wrongly getting
   classified as authorization code request", L276 "Checked the deployments. It was not deployed
   properly", L284 on deployment basepath defaulting to `/` and not being settable in the UI. The
   previous pass's decision to drop the invented "second client succeeds" evidence in favour of
   "the authorize leg works" is a genuine improvement — it is consistent with a proxy-level routing
   fault and it is the stronger lure.

---

## MED-17 The deploy tool says "Deployment failed"

**Verdict**: CORRECT

**Issues**: none.

Verified line-by-line against `research/issues/apigee_apigee-deploy-maven-plugin-213.txt`:
`apigee.override.delay` (L41, L53), the message string "Deployment failed: Bundle did not activate
within expected time. Please check deployment status manually before trying again" (L27, L59, L126),
`Waiting to assert bundle activation.....` (L19, L138), `Deployment failed to activate` (L26, L139),
the hardcoded `Thread.sleep(10L)` (L20), "it took around 30 secs to deploy" (L101), the maintainer's
actual position that "That Thread.sleep(10) is only when the state in the deployment response is not
equal to 'deployed'" (L134) and the request to "change the value from 30 to something like 10"
(L146). The scenario's refusal to assert why deployments take 30 seconds, and its "closed for
inactivity, not fixed" origin line, both match the record. Honest handling of an unresolved dispute
is the right design here.

---

## MED-18 Every API product, app and developer fails to load after a hybrid upgrade

**Verdict**: CORRECT

**Issues**: none.

Verified against `research/pages/apigee-known-issues.txt` L257-270: entry 479872706, Affects "hybrid
1.16.0 (EKS with WIF and forward proxy)", FIXED in hybrid 1.16.0-hotfix.1, cause "environments using
Workload Identity Federation (WIF) in conjunction with an HTTP Forward Proxy may fail to load
management entities ... due to a credential casting regression in MART". The `overrides.yaml` YAML
block in the remediation matches the register's block exactly. The conjunction trap is correctly
identified as the evaluation target, and the neighbouring defect 479040521's missing
`.Values.gcp.federatedWorkloadIdentity.enabled` condition is real (known-issues L250-253). The
previous pass's addition of the EKS scope and the "re-import is not the problem" wrong answer are
both correct additions.

---

## MED-19 Runtime logs stopped after a successful upgrade

**Verdict**: CORRECT

**Issues**: none.

Verified against `apigee-known-issues.txt` L20-45: entry 543171828, Affects "hybrid 1.14.7, hybrid
1.15.7, and hybrid 1.16.8", FIXED in hybrid 1.16.9, `kubectl get daemonset apigee-logger -n apigee`
reporting desired count 0, the `apigee.cloud.google.com/apigee-logger-enabled: "true"` default
nodeSelector, the "releases before the affected versions ignored component-level node selectors"
explanation, and "Only deployments that set `logger.enabled: true` are affected". Every element of
the scenario — the one-command discriminator, the counter-intuitive "a bug fix caused this"
reading, both workarounds, and the platform note (logging on by default on GKE and GKE on-prem, off
by default on AKS) — traces to the register or the release notes. The past pass's judgement that
this one was clean was right.

---

## MED-20 A deployed timeout change is not taking effect on some requests only

**Verdict**: MINOR

**Issues**:

1. **246774745 is characterised as a live compounding defect.** The ground truth says "A second
   documented defect, 246774745, compounds it", and the remediation says "if several flows set
   different timeouts against the same target host, consolidate them, because the per-flow values
   will collapse to one regardless." The register (`apigee-known-issues.txt` L2168-2173) shows
   246774745 as **FIXED**, with no version scope, titled "Value of `io.timeout.millis` is not
   honored when used with multiple dynamic targets" — its body reads "If a proxy sets two or more
   `io.timeout.millis` values in two or more flows using the same target host, only one
   `io.timeout.millis` value is honored", which the scenario quotes accurately.

   The problem is the framing, not the quote. The scenario is otherwise scrupulous about version
   scoping — it makes "we are on hybrid 1.16.x or later rules it out" a scored wrong answer for
   471125841 — yet presents 246774745 as if it were an active hazard on the customer's 1.15.5. The
   register gives no affected-version list for it. An agent that correctly says "246774745 is marked
   fixed and carries no version scope, so I would not treat it as your live cause" is being
   steered away from the defensible answer. The same issue appears in the Verification section
   ("the collapse to a single value will only show up there"), which asserts an active behaviour
   the register attributes to a fixed defect.

   MINOR rather than MATERIAL: the primary defect, the version scope, the upgrade-first remediation,
   and the documented one-by-one `apigee-runtime` restart workaround (all verified at
   known-issues L337-348) are correct, and the scenario's structural insight — that the symptom
   does not reveal the `<LoadBalancer>` — is sound.

2. Positive: the previous pass's three fixes here all landed. The version scope is in the ticket
   and the ground truth, the upgrade is correctly the primary remediation with the restart as the
   pre-1.16 workaround, and the duplicated "Diagnostic method" rubric row is repaired.

---

## MED-21 The linter and the security team want opposite things

**Verdict**: CORRECT

**Issues**: none.

Verified against `research/issues/apigee_apigeelint-526.txt`. Both warning strings are verbatim:
"TargetEndpoint HTTPTargetConnection should have exactly one SSLInfo" (TD012) and "When using a
LoadBalancer, the SSLInfo should be configured in the TargetServer, not under HTTPTargetConnection"
(TD006), plus "Missing MaxFailures element within LoadBalancer" (TD015). The structural insight —
that the linter scans the proxy bundle, TargetServers are environment configuration and are not in
it, so it "has no way to check the referred TargetServer" — is the maintainer's own words at the
DinoChiesa comment. The three-part resolution (demote TD006 to an External Plugin; narrow TD012 to
fire iff there is no LoadBalancer; change TD015 to not complain on a single server) is quoted
correctly, and "Fixed in v2.67.0" is the thread's closing comment. The MaxFailures antipattern is
verified separately at `api-platform_antipatterns_load-balancing-maxfailures.txt`: single TargetServer
with non-zero MaxFailures → 503 (503 in TargetEndpoint, 500 in ServiceCallout), "Apigee does not
automatically put the TargetServer back into rotation... the API Proxy must be redeployed", and
HealthMonitor as the documented cure. The previous pass correctly upgraded this from a two-part fix
to three and promoted the antipattern to a scored element.

---

## MED-22 A routine cert-manager upgrade plants a future outage

**Verdict**: CORRECT

**Issues**: none.

Verified against `apigee-known-issues.txt` L359-390: entry 465834046, Affects "hybrid 1.14.3, hybrid
1.15.1, and hybrid 1.16.0 and later for upgrades", FIXED for fresh installs in those versions,
"cert-manager versions 1.18+ changed the default for the private key rotation policy from `Never` to
`Always`", "**Note:** This only applies to upgraded Apigee hybrid clusters", and "When this key is
rotated for the apigee-ca certificate, it will cause an outage". Both workarounds are correct — the
`kubectl patch` JSON-path command and the "do not upgrade above 1.17.x" ceiling — as is the
ordering warning ("Perform these steps *before* upgrading cert-manager. Otherwise, you may trigger a
certificate rotation").

The scenario's most valuable property is that it refuses to over-claim: the ground truth states
plainly that "the current intermittent connection failures are not themselves explained by this
register entry" and that the agent should treat it as the reason to act now rather than the
diagnosis of what is already happening. That is correct handling of a forward-looking register entry
presented as an active symptom, and it matches the previous pass's stated correction. The
Cassandra backup/restore verification note is consistent with the upgrade guidance on mixed hybrid
versions.

---

## MATERIAL ERROR COUNT: 4 of 37

| Scenario | Error |
| --- | --- |
| EASY-06 | Ground truth asserts Apigee header flow variables are case-sensitive and that `request.header.Authorization` != `request.header.authorization`; the cited docs use both spellings as defaults for the same `Authorization` header, and the scenario's own remediation is a no-op under either reading. Undocumented claim presented as fact; correct answers would be scored as critical failures. |
| EASY-10 | Cites two non-existent HMAC elements, `<SecretVariable>` and `<VerificationOutput VariableToVerify>`. The real elements are `<SecretKey>` (Required) and `<VerificationValue>`. Both names appear in zero of 408 cached pages. |
| MED-04 | Cites a non-existent ResponseCache element `<Key>`. The real elements are `<CacheKey>` with `<KeyFragment>`/`<Prefix>` children and `<Scope>`. Instructs the agent not to invent an expression while supplying one. |
| MED-15 | Fault code payload reads `javacallout.ExecutionError`; the documented and indexed code is `steps.javacallout.ExecutionError`. Undermines the scenario's own evaluation target of exact-code discipline. |

Three MINOR findings (EASY-05 `context.variable()`, MED-09 title/evidence 429-vs-500, MED-20
246774745 framed as live) and one fix-report correction (MED-07's `setSyncAuthorization` is
documented; the caveat should be retracted) are detailed above. Everything else in both files holds
up: fault codes are real and correctly sourced, quoted statuses match the docs, and the two error
classes that dominated the last round — invented XML elements and undocumented JavaScript APIs —
are down to the four items above.
