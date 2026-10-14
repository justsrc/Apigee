# Final blind correctness pass: easy.md and medium.md

Adversarial review, 37 scenarios. Verified against `research/pages/` (285 cached files)
and `research/issues/`. No network used.

Before the per-scenario verdicts, two findings that apply across whole files, because they
change how a grader reads the answer keys.

## Cross-cutting finding A (MATERIAL): all 22 MED answer keys silently drop their critical-failure list

`tests/make_packets.py` extracts a scenario's critical failures only when the text sits
*inside* the `Evaluation rubric` section. In `easy.md` the line is bold body text under that
heading (`**Critical failures:** ...`), so it is captured. In `medium.md` it is a sibling
heading of the same level (`#### Critical failures: ...`, e.g. `scenarios/medium.md:99`),
so the extractor stops at the rubric heading and never emits it.

Verified mechanically:

```text
EASY-01..15 : cf_inside_rubric=True   cf_own_section=False
MED-01..22  : cf_inside_rubric=False  cf_own_section=True
```

Consequence: `grep -l "Critical failures" evaluation/packets/MED-*.key.md` returns **0 of
22**, against **15 of 15** for EASY. `hard.md` uses the easy.md style and keeps all 15, so
this is specific to medium.md's heading level, not a general tool limitation.

`evaluation/rubric.md` says "Scenario rubrics list critical failures specific to that case.
Use those." A grader working from the MED packets has the rubric *table* but not the
fail-the-scenario conditions. A MED answer that trips a listed critical failure can be
scored as a pass. This is the single most consequential defect found and it is invisible
unless you diff the scenario file against its packet.

Fix is a one-line style change in `medium.md`: demote `#### Critical failures:` to
`**Critical failures:**` so it joins the rubric section, matching easy.md and hard.md.

## Cross-cutting finding B (MINOR): MED-16's fault code is outside the required index

`medium.md` opens with "Fault codes are real and live in `error-codes.md`. Do not add codes
that are not in that file." `steps.oauth.v2.InvalidRequest` (medium.md:1640) is not in that
index. The code is real and correctly attributed: `api-platform_reference_policies_oauthv2-policy.txt:2250`
gives `steps.oauth.v2.InvalidRequest` with HTTP 400 and the "multiple different kinds of
errors" cause text the scenario quotes. The index is the incomplete artifact, not the
scenario. `build_error_index.py` returns 0 rows for that page's error reference because the
page renders its tables as HTML `<tr>` rather than markdown pipes. Same root cause puts
`messaging.adaptors.http.flow.SslHandshakeFailed` outside the index, but EASY-14 explicitly
declares that exception and attributes the code to the API Monitoring page, which is
allowed. MED-16 does not make that attribution, so it silently breaks its own file-level rule.

---

## EASY-01 Quota policy rejects the revision over a fractional interval

**Verdict**: MINOR
**Issues**:

1. The remediation block recommends `<TimeUnit>second</TimeUnit>` and then says "Confirm
   `second` is a supported `<TimeUnit>` value before recommending it." That hedge is
   correct but understates the constraint. `quota-policy.txt:1030` states `second` is
   "only supported for non-distributed counters (when `<Distributed>` is set to `false`)"
   and that Google recommends SpikeArrest instead. The shown XML omits `<Distributed>`,
   and the default is `false` (`quota-policy.txt` `<Distributed>` table), so the snippet
   happens to work, but only by accident of a default the scenario never states. An agent
   that copies the snippet into a policy that sets `<Distributed>true</Distributed>` gets a
   deployment rejection. Recommend naming the constraint explicitly.
   Everything else verified: `InvalidQuotaInterval` is a Quota deployment error
   (`quota-policy.txt:1876`), `QuotaViolation` is 500 (`quota-policy.txt:1868`), the
   "no HTTP status" framing for deployment errors matches the index's own preamble.

## EASY-02 Missing Interval produces a runtime 500

**Verdict**: CORRECT
**Issues**: none. `policies.ratelimit.FailedToResolveQuotaIntervalReference` at 500 with
"`<Interval>` element is not defined... This element is mandatory" is verbatim at
`quota-policy.txt:1865`. The 3% / conditional-flow reasoning is sound and the sibling code
is not conflated.

## EASY-03 FlowCallout cannot find the shared flow

**Verdict**: CORRECT
**Issues**: none. `flow.SharedFlowNotFound`, 500, "Either the shared flow does not exist, or
the shared flow exists but is not deployed" — `flow-callout-policy.txt:412`. The scenario's
insistence on separating the two causes is exactly right, and the "cannot prove absence
from the code" discipline is correct.

## EASY-04 AccessControl blocks a corporate IP range

**Verdict**: CORRECT
**Issues**: none. `accesscontrol.IPDeniedAccess` at 403 caused by a client IP matching
`SourceAddress` is in the index and matches `access-control-policy.txt`. `IPRules`,
`MatchRule`, `SourceAddress`, `noRuleMatchAction` all confirmed
(`access-control-policy.txt:32-36`). The TEST-NET-3 observation is accurate.

## EASY-05 JavaScript policy blocked by a security violation

**Verdict**: MINOR
**Issues**:

1. "Also worth removing the now-unused callout if nothing else uses it" (easy.md:597) is
   orphaned. There is no callout anywhere in EASY-05. It reads as a leftover from another
   scenario and instructs the agent to remove something that does not exist. Appears in the
   Verification section, so it ships in the key.
2. `loadCredential` is genuinely absent from all 285 cached pages, and
   `steps.javascript.ScriptSecurityError` is real at 500
   (`javascript-policy.txt:492`). The framing is honest: the scenario does not claim the
   doc names the blocked call, it says the fault string does. Correct handling.

## EASY-06 BasicAuthentication cannot resolve its source variable

**Verdict**: CORRECT
**Issues**: none. The earlier header-casing error is gone; the cause is now step ordering,
which the runtime-errors page supports exactly:
"Out of scope (not available in the specific flow where the policy is being executed) /
Can't be resolved (is not defined)" and "can only occur if `IgnoreUnresolvedVariables`
element is set to `false`"
(`troubleshoot/policies/runtime/basic-authentication-runtime-errors.txt`). The
`request.header.Authorization` example matches the policy page's own decode sample (line
115). Good.

## EASY-07 JWS algorithm mismatch

**Verdict**: CORRECT
**Issues**: none. `steps.jws.AlgorithmMismatch`, 401, "The algorithm specified in the header
by the `Generate` policy did not match the one expected in the `Verify` policy" — matches
the index and `verify-jws-policy.txt`. PS256 is in the supported list
(`decode-jws-policy.txt` `InvalidAlgorithm` row), so the "supported in general, wrong for
this config" distinction holds.

## EASY-08 InvalidMessageWeight does not identify the policy

**Verdict**: CORRECT
**Issues**: none. Verified the shared-code claim in both directions: `quota-policy.txt:1867`
and `spike-arrest-policy.txt:727` both carry `policies.ratelimit.InvalidMessageWeight`. The
"the trace step name is the discriminator" conclusion follows. The JS remediation uses
`context.getVariable` / `context.setVariable` correctly.

## EASY-09 JSONToXML cannot resolve its source variable

**Verdict**: MINOR
**Issues**:

1. The ground truth says `request.body.payload` "is not a variable that exists. Apigee
   exposes the request payload as `request.content`." True, but the scenario does not
   acknowledge that a *nonexistent* variable is the textbook trigger for the sibling code
   it explicitly tells the agent to distinguish. `SourceUnavailable` fires when the source
   "is either: Out of scope... or Can't be resolved (is not defined)"
   (`json-xml-policy.txt:605`) — which describes `request.body.payload` exactly.
   `InvalidSourceType` fires on a *type* problem in a variable that does resolve
   (line 603). So the evidence points more naturally at `SourceUnavailable` than at the code
   the scenario hands over. The scenario gets out of this by fixing the code in turn 1 and
   telling the agent to work backwards from it, but a technically correct respondent who
   says "this code does not match this evidence; I would expect SourceUnavailable" is being
   marked down. The `<OutputVariable>`-mandatory-when-string rule is correct (line 604).

## EASY-10 HMAC policy missing a required element

**Verdict**: CORRECT
**Issues**: none. `steps.hmac.MissingConfigurationElement` is real and is listed under
**Deployment errors** on the HMAC page (`hmac-policy.txt:357`), so the 400-at-save framing
is right. `<SecretKey>` is Required with no default and a required `ref`
(`hmac-policy.txt:209-225`); `<VerificationValue>` is documented Optional and gates the
check (line 78-81). `InvalidSecretInConfig` and `InvalidVariableName` causes match lines
358-359. No invented elements.

## EASY-11 Unsupported TimeUnit

**Verdict**: CORRECT
**Issues**: none. The deployment-error row lists exactly `minute`, `hour`, `day`, `week`,
`month` (`quota-policy.txt:1877`), matching the scenario's list and the rubric's
"names the full documented list" anchor. Note the `<TimeUnit>` element reference separately
mentions `year` (line 766) and `second` (line 1030); the scenario correctly scopes its list
to the deployment-error reference, which is the source the error name points at.

## EASY-12 RevokeOAuthV2 timestamp bound

**Verdict**: CORRECT
**Issues**: none. `revoke-oauth-v2-policy.txt:315` gives
`steps.oauth.v2.InvalidEarlyTimestamp` / 500 / "Timestamp cannot be earlier than January 1,
2014". Line 298 gives both halves of the bound. The three sibling codes and their 500
statuses (lines 314-316) are correct. The "element is optional, defaults to the time the
policy executes" claim matches line 295. The seconds-vs-millis variant is labelled as a
second hypothesis rather than the confirmed cause, which is the honest framing.

## EASY-13 JWKS verification fails without kid

**Verdict**: CORRECT
**Issues**: none. `steps.jwt.KeyIdMissing` / 401 / "the signed JWT does not include a `kid`
property in the header" — `verify-jwt-policy.txt:1202`. The faultstring names the variable
via `fault.name` per the documented model. The explicit-key fallback is presented with its
cost (loss of rotation), and the scenario does not fabricate a manual `kid` injection path.

## EASY-14 Target handshake fails against legacy TLS

**Verdict**: CORRECT
**Issues**: none, and the caveat section is doing exactly the right work.
`options-configuring-tls.txt:8` names the code and the TLS 1.0/1.1 restriction directly;
`mon_fault-codes.txt:77` maps it under Target to `FailedHandshakeWithTargetEndpoint`. Both
attributions in the caveat check out. `<Protocols>` semantics confirmed
(`api-proxy-configuration-reference.txt:836`: "If no protocols are specified, then all
protocols available for the JVM will be permitted"), so "narrower, never wider" is right.

## EASY-15 Quota counter behaves differently than expected

**Verdict**: CORRECT
**Issues**: none. `quota-policy.txt:14` is almost a verbatim source for the ground truth:
"Quotas apply to individual API proxies and are not distributed among API proxies. For
example, if you have three API proxies in an API product, a single quota is not shared
across all three even if all three use the same quota policy configuration." 3 × 10,000 =
30,000 follows.

---

## MED-01 Deployed successfully, every request returns 404

**Verdict**: CORRECT
**Issues**: none. `environments-overview.txt:16`: "An environment must be a member of at
least one environment group before you can access proxies deployed within it." The
Edge-vs-hybrid product split is right: `compare-apigee-products.txt` lists "Support for
environment groups" only under Apigee, and hybrid docs treat envgroups as first-class
(`hybrid_latest_environments-about.txt:129`).

## MED-02 Works for some users, 404s for others

**Verdict**: CORRECT
**Issues**: none. `READY` state and per-pod `deploymentStatus: deployed` are the real
fields (`ui-deploy-overview.txt:111,148`). The rubric correctly forbids asserting a
regional deployment model, which no evidence supports.

## MED-03 Load balancing does not fail over

**Verdict**: CORRECT
**Issues**: none, and this one is unusually well-anchored. `<MaxFailures>` default 0 with
"Apigee always tries to connect to the target for each request and never removes the target
server from the rotation" is verbatim (`load-balancing-across-backend-servers.txt:342`).
The 500-does-not-count quote is verbatim (line 314): "even if the response is an HTTP error
(such as `404` or `500`), that counts as a response from the target server, and the failure
counter is reset." `<RetryEnabled>` default true and its I/O-or-timeout trigger are correct
(line 358-360). Algorithm values are exactly RoundRobin/Weighted/LeastConnections (line 237).
`<HealthMonitor>` requiring `MaxFailures > 0` is correct (line 539). Trace caveat (line 352)
is accurate. The critical failure — changing only MaxFailures — is the right trap.

## MED-04 Cached responses are stale

**Verdict**: CORRECT
**Issues**: none. The scenario's central claim, that the two official pages disagree about
the `Exclusive` prefix, is real and I confirmed both forms:
`response-cache-policy.txt:598,640-643` gives
`orgName__envName__apiProxyName__proxyNameITargetName` with example
`apifactory__test__weatherapi__default__apiAccessToken`; `working-cachekeys.txt:138,146`
gives `...__deployedRevisionNumber__nameof(proxyEndpoint|targetEndpoint)__[...]` with
example `mycompany__prod__weatherapi__16__default__hello__world`. Revision 16 is present in
one and absent in the other. Both pages agree `Exclusive` is the default and that `<Prefix>`
supersedes `<Scope>` (line 600). ResponseCache has no `<Key>` element — confirmed by the
child-element tables; `<CacheKey>`/`<KeyFragment>`/`<Prefix>` are correct. The
`responsecache.{policy_name}.cachekey` read-only variable is real
(`response-cache-policy.txt:798`). This scenario handles the ambiguity the way it should:
it refuses to force a conclusion and says the question has to be tested.

## MED-05 Key value map updates not visible everywhere

**Verdict**: CORRECT
**Issues**: none. The single-node quote is verbatim
(`key-value-map-operations-policy.txt:411`). The scoping is the valuable part and it is
accurate: line 425 "Updating a KVM with the Apigee UI or API does not reset the KVM cache",
line 423 on no cross-node invalidation mechanism, line 424 on the placeholder-`PUT` trap.
The `private.` prefix behaviour is confirmed (`cache/key-value-maps.txt:130,258`). Critical
failure correctly separates the policy `PUT` path from the Management API path.

## MED-06 Latency jumped, unknown layer

**Verdict**: MINOR
**Issues**:

1. "The absence of a deploy is not evidence of applause; it is the absence of one class of
   cause" (medium.md:705) is a rhetorical flourish that does not parse as a technical
   claim. It reads as a joke dropped into an answer key. Harmless to correctness, but it is
   the kind of line that erodes trust in the rest of the document.
2. Substance is sound: the scenario correctly refuses to attribute without the trace plus an
   external measurement, and correctly flags that p95 is not the whole story. No fault
   codes or elements asserted.

## MED-07 Hybrid deployment succeeds, runtime never applies it

**Verdict**: MINOR
**Issues**:

1. "the Synchronizer pulls the contract, the Message Processor applies it, and the Watcher
   reports status" (medium.md:761) lists four steps including a Watcher. The Watcher
   component exists in hybrid (`watcher.image.url` in `hybrid_latest_config-prop-ref.txt`)
   but I could not find documentation describing it as the fourth step of this specific
   sequence. The load-bearing parts — the `Switched to newer version N from version M`
   marker (`hybrid_v1.17_runtime-logs.txt:74`) and the `setSyncAuthorization` plus
   Apigee Synchronizer Manager requirement (`hybrid_v1.17_synchronizer-access.txt:94,98`) —
   are both verified. Treat the four-step framing as a reasonable synthesis rather than a
   quotable one.
2. Otherwise correct, including the "nothing is wrong with the proxy, the revision, or the
   runtime" conclusion and the honest note that the API will accept an identity that lacks
   the role.

## MED-08 Mutual TLS broke after CA renewal

**Verdict**: CORRECT
**Issues**: none. `api-proxy-configuration-reference.txt:458` is nearly verbatim:
"Apigee requires the `clientAuth` EKU to be present in client certificates for mTLS
handshakes. Without this EKU, mTLS connections will fail for both northbound (client to
Apigee) and southbound (Apigee to backend) traffic." The two-sided failure in the ticket is
therefore exactly the documented signature, and the "check EKU before chains or protocols"
ordering is right.

## MED-09 Intermittent 429 under bursty client traffic

**Verdict**: MATERIAL
**Issues**:

1. **Fabricated configuration elements in the answer key.** The remediation says "add
   SpikeArrest with a low `rateLimit` and a short `timeWindow`" (medium.md:971, and
   `evaluation/packets/MED-09.key.md`). Neither element exists. The documented SpikeArrest
   children are `<DisplayName>`, `<Identifier>`, `<MessageWeight>`, `<Rate>`, and
   `<UseEffectiveCount>` (`spike-arrest-policy.txt:70-72,291-687`), and the rate is a single
   `<Rate>` element whose body is a suffixed integer such as `5ps` or `12pm`
   (lines 484-537). `grep -rn -i "timeWindow"` across all 285 cached pages returns nothing;
   `rateLimit` appears only as part of the `ratelimit.<policy>.count` flow-variable
   namespace, never as an element. The project rule is explicit that invented configuration
   elements are penalised at the *top* of the scale, and this one is in the key a grader
   reads as correct. Must be rewritten to `<Rate>` with an `Nps`/`Npm` value.
2. Secondary: the ticket title and body say "429", but the initial evidence states
   `policies.ratelimit.QuotaViolation` with **HTTP 500**, which is what
   `quota-policy.txt:1868` documents. Both are defensible readings of Apigee's real
   behaviour (the comparison page lists 429 as the limit-reached status), but the scenario
   never reconciles them, and a respondent who trusts the title over the payload will
   argue about a status code that is not the point. Worth a sentence.

## MED-10 Token works against one API, fails against another

**Verdict**: CORRECT
**Issues**: none. The policy-specific status split is real: `steps.oauth.v2.access_token_expired`
is 500 on GetOAuthV2Info (`get-oauth-v2-info-policy.txt:451`) and SetOAuthV2Info
(`set-oauth-v2-info-policy.txt:193`), while the OAuthV2 page's own VerifyAccessToken row is
401 (`oauthv2-policy.txt:2183-2185`). The `invalid_client` / `InvalidClientIdentifier`
`GenerateResponse` split is documented verbatim at `oauthv2-policy.txt:2241-2244,2273-2276`.
The trace-based discriminator is sound. Attributing the 500 to a later `SetOAuthV2Info`
step while VerifyAccessToken succeeded at the validate step is coherent.

## MED-11 Works in test, fails in production

**Verdict**: MINOR
**Issues**:

1. "A JavaScript policy reads that variable and passes it as a timeout, producing a
   malformed value in production only" (medium.md:1145-1146) is thin. `prod` has
   `orders.timeout` set to `30` and `test` has no such key, so in production the variable
   *resolves to a well-formed value* and in test it is absent. The stated mechanism points
   the wrong way: on these facts the malformed/unresolved case is the one with no key. The
   shape of the lesson (environment-scoped config differs, diff rather than redeploy) is
   right and matches the general rule, but the specific instance as written is not
   self-consistent. Either flip the evidence (a key present in `test` with a bad value, or
   a `prod` key holding a non-numeric string) or drop the mechanism and keep the
   difference-as-such point.
2. Otherwise sound: the "the bundle is not the variable" conclusion is correct and the
   critical failure against repeated manual map edits is the right one.

## MED-12 Service callout times out

**Verdict**: CORRECT
**Issues**: none. `service-callout-policy.txt:519` is verbatim: "If the ServiceCallout hits
a timeout, an HTTP 500 is returned, the policy fails, and the API proxy goes into an error
state." The p95-hides-the-tail reasoning and the "which timeout is firing" discriminator are
both correct, and the fault rule recommendation is sound.

## MED-13 Two conditions produce the same error code

**Verdict**: CORRECT
**Issues**: none. `javascript-policy.txt:490` confirms ScriptExecutionFailed is a family
(RangeError, ReferenceError, SyntaxError, TypeError, URIError) and that the fault string
carries detail. The critical failure against matching on `faultstring` for *error handling*
while allowing it as a *diagnostic aid* is precisely the distinction the docs draw
(`javascript-policy.txt:519`: "Do not rely on the text in the `faultstring`").

## MED-14 Revoked token still works for a few minutes

**Verdict**: CORRECT
**Issues**: none. `oauthv2-policy.txt:1108` is verbatim: "OAuth tokens are cached for three
minutes (180 seconds); therefore, a revoked token may still succeed for up to three
minutes, until its cache limit expires." The scenario's refusal to let the urgency framing
override the documented behaviour, while still surfacing the operational consequence, is
handled well.

## MED-15 Java callout fails on some requests

**Verdict**: CORRECT
**Issues**: none, and this scenario is now exactly right. `java-callout-policy.txt:222`
gives the single runtime error `steps.javacallout.ExecutionError`, 500, "Occurs when Java
code throws an exception or returns null". The bare `javacallout.ExecutionError` form
appears only in the example error response at line 259, and the six deployment names
(`JavaClassNotFoundInJavaResource`, `JavaCalloutInstantiationFailed`,
`JavaClassDefinitionNotFound`, `NoAppropriateConstructor`, `ResourceDoesNotExist`,
`NoResourceForURL`) are all in the deployment table with HTTP status N/A (lines 230-236).
The critical failure against naming a deployment error at request time is correct and the
"stop short of naming the Java line" instruction is the honest calibration.

## MED-16 OAuth error names a missing parameter

**Verdict**: MINOR (scenario content correct; see cross-cutting finding B for the index issue)
**Issues**:

1. `steps.oauth.v2.InvalidRequest` is absent from `error-codes.md`, which medium.md's own
   preamble forbids. Code and 400 status are real (`oauthv2-policy.txt:2250-2256`) and the
   quoted cause matches. The fix belongs in `build_error_index.py` (the OAuthV2 page's
   error tables are HTML, and `rows_of` returns 0), not in the scenario.
2. Substantively the scenario is strong. The source issue confirms the routing diagnosis:
   the reporter observed the token request "wrongly getting classified as authorization code
   request" and the maintainer replied that deployment basepath "cannot be set from the UI...
   defaults to '/'... un-deploying your proxy and deploying again through API made it work"
   (`research/issues/apigee_api-platform-samples-7.txt:272,284`). The cascade reasoning is
   correct and the "error text is a symptom, not a contract" framing is the right lesson.

## MED-17 Deploy tool says failed, Management API says worked

**Verdict**: CORRECT
**Issues**: none. Every disputed detail is sourced. The maintainer: "you can ignore that
hardcoded value. Thats just used to get the deployment details and see if the deployment is
completed and stable" and "That Thread.sleep(10) is only when the state in the deployment
response is not equal to 'deployed'... if the deployed revision is not set, then it fails
with that error" (`issues/apigee_apigee-deploy-maven-plugin-213.txt:39,134`). The log
strings `Waiting to assert bundle activation.....` and `Deployment failed to activate` are
verbatim (lines 138-139). The maintainer's advice to drop the delay from 30 to 10 is
recorded. Closure for inactivity is at line 180. The scenario's refusal to declare the
30-second deployment time explained is exactly the honest move, and the rubric's
"States that the 30-second deployment time is unexplained" anchor rewards it.

## MED-18 MART entities fail to load after hybrid upgrade

**Verdict**: CORRECT
**Issues**: none. `apigee-known-issues.txt:257-282` gives issue 479872706, "hybrid 1.16.0
(EKS with WIF and forward proxy)", FIXED in 1.16.0-hotfix.1, with the credential-casting
regression and the conjunction of WIF **and** HTTP forward proxy. The neighbouring defect
479040521 (`apigee-operator-guardrails-sa` not created on AKS/EKS with Federated Workload
Identity, because the template's initial `if` omits
`.Values.gcp.federatedWorkloadIdentity.enabled`) is at lines 217-239. The overrides.yaml
snippet matches the documented workaround exactly. The trap being taught — that checking
either gating feature alone rules the issue out incorrectly — is the real content and it is
correct.

## MED-19 Runtime logs stopped after upgrade

**Verdict**: CORRECT
**Issues**: none. `apigee-known-issues.txt:20-59` confirms 543171828, affected versions
1.14.7/1.15.7/1.16.8, FIXED in 1.16.9, the `apigee-logger` DaemonSet desired count of 0,
the default `logger.nodeSelector` of `apigee.cloud.google.com/apigee-logger-enabled:
"true"`, and that earlier releases ignored component-level node selectors. Both remedies
(clear the selector, or label the nodes) match the documented workarounds verbatim. The
platform note is also right: "Logging is provided by default on GKE and GKE on-prem... On
AKS, you must explicitly enable logging" (`hybrid_v1.17_logging-view.txt:57`).

## MED-20 Deployed timeout change not taking effect

**Verdict**: CORRECT
**Issues**: none. `apigee-known-issues.txt:337-347` gives 471125841, hybrid 1.14.x and
1.15.x, FIXED in 1.16.x, "The updated value of `io.timeout.millis` is intermittently not
honored... when multiple servers are used under `<LoadBalancer>` in the TargetEndpoint",
with the one-by-one `apigee-runtime` pod restart workaround. 246774745 (line 2168-2176)
gives the "two or more `io.timeout.millis` values in two or more flows using the same target
host, only one is honored" compounding defect. The ticket's version (1.15.5) sits correctly
inside the affected range, and the scenario is right that "we are on 1.16.x or later" would
change the answer.

## MED-21 Linter and security team want opposite things

**Verdict**: CORRECT
**Issues**: none. `research/issues/apigee_apigeelint-526.txt` confirms all three rule strings
verbatim (`TargetEndpoint HTTPTargetConnection should have exactly one SSLInfo` TD012;
`When using a LoadBalancer, the SSLInfo should be configured in the TargetServer, not under
HTTPTargetConnection` TD006; `Missing MaxFailures element within LoadBalancer` TD015), the
maintainer's three-part fix plan, and "Fixed in v2.67.0". The diagnosis of *why* the rules
contradict each other is the maintainer's own words: TD006 "has no way to check the referred
TargetServer... The design of the plugin is sort of broken - it assumes that if there is an
SSLInfo under HTTPTargetConnection, then it is NOT present in the TargetServer. But that is
not a valid assumption." The MaxFailures antipattern is also real
(`antipatterns/load-balancing-maxfailures.txt:98`: "Apigee does not automatically put the
TargetServer back into rotation... the API Proxy must be redeployed"; line 100 on the
ServiceCallout 500 variant). Note the maintainer's actual resolution for TD006 was to
demote it to an external plugin and narrow TD012, which the scenario reports correctly.

## MED-22 cert-manager upgrade plants a future outage

**Verdict**: CORRECT
**Issues**: none. `apigee-known-issues.txt:359-447` gives 465834046, "hybrid 1.14.3, hybrid
1.15.1, and hybrid 1.16.0 and later for upgrades", FIXED for fresh installs in those
versions, cert-manager 1.18+ changing the rotation-policy default from `Never` to `Always`,
"this only applies to upgraded Apigee hybrid clusters", and "When this key is rotated for the
apigee-ca certificate, it will cause an outage." The `kubectl patch` command matches the
documented procedure including the warning to perform it *before* upgrading cert-manager.
The Cassandra mixed-version backup/restore caveat is real (`hybrid_v1.17_upgrade.txt:82`).
Most importantly, the scenario refuses to claim the register entry explains the *current*
intermittent failures, and says so explicitly — that is the correct handling of a future-risk
entry and it is rarer than it should be in this suite.

---

## Summary

MATERIAL ERROR COUNT: 2 of 37

Counted as material: cross-cutting finding A (all 22 MED answer keys drop their
critical-failure list) and MED-09 (fabricated SpikeArrest elements in the answer key).
Cross-cutting finding B is scoped as MINOR per-scenario because the fault code itself is
real and correctly attributed; the defect is in the generated index.

| # | Location | Error | Evidence | Severity |
| --- | --- | --- | --- | --- |
| 1 | `scenarios/medium.md` (all 22 `#### Critical failures:` headings, e.g. line 99); `evaluation/packets/MED-*.key.md` | Critical-failure conditions are omitted from every MED answer key because they are sibling headings rather than body text under the rubric. A grader using the packets cannot see the fail-the-scenario conditions. | `grep -l "Critical failures" evaluation/packets/MED-*.key.md` → 0/22; EASY → 15/15; hard.md → 15/15. `make_packets.py` `section()` stops at the next heading. | MATERIAL |
| 2 | `scenarios/medium.md:971`; `evaluation/packets/MED-09.key.md` | Answer key recommends SpikeArrest "with a low `rateLimit` and a short `timeWindow`". Neither element exists. | `spike-arrest-policy.txt` children are `<DisplayName>`, `<Identifier>`, `<MessageWeight>`, `<Rate>`, `<UseEffectiveCount>`; rate is `<Rate>5ps</Rate>` form (lines 484-537). `grep -rn -i timeWindow` over 285 pages → no matches; `rateLimit` appears only in the `ratelimit.*` flow-variable namespace. | MATERIAL |

MINOR findings worth fixing but not score-changing: EASY-01 (the `second` time unit needs
`<Distributed>false</Distributed>` stated, not left to a default), EASY-05 (orphan
"remove the now-unused callout" line, no callout exists), EASY-09 (`SourceUnavailable` is
the more natural code for a nonexistent source variable; the scenario should acknowledge
the tension), MED-06 (one joke line in an answer key), MED-07 (four-step sequence including
the Watcher is a synthesis, not a quotable doc line), MED-11 (the KVM mechanism points the
wrong way given which environment lacks the key), MED-09 secondary (429 in the title vs 500
in the payload), and MED-16's dependency on the incomplete `error-codes.md` index.

Everything else held up. The fault codes are real and correctly attributed; the nested
error payload shape is right throughout; the deliberately-hard cases (MED-04's
self-documented documentation conflict, MED-15's runtime-vs-deployment table split, MED-18's
conjunction trap, MED-22's refusal to over-claim) are the strongest material in the suite.
