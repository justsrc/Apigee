# Hostile review: scenarios/easy.md and scenarios/medium.md

Reviewed 2026-10-11. Every fault code, status, element and attribute below was checked
against a fetched page, not against the scenario's own prose. Page sources are in
`research/pages/`; `research/pages/MANIFEST.tsv` records the real URL and byte count for
each fetch.

## Suite-level findings (read these first)

**S1. The fault response bodies in both files are not the documented Apigee shape.**
Scenarios present bodies like:

```json
{ "errorcode": "...", "faultstring": "...", "faultname": "...", "status": "500" }
```

The documented payload has no top-level `errorcode`, `faultname` or `status` key:

```json
{ "fault": { "detail": { "errorcode": "..." }, "faultstring": "..." } }
```

Source: <https://cloud.google.com/apigee/docs/api-platform/fundamentals/what-you-need-know-about-policy-errors>
(cached: `api-platform_fundamentals_what-you-need-know-about-policy-errors.txt`, line 24)
and <https://cloud.google.com/apigee/docs/api-platform/fundamentals/fault-handling>
(cached: `api-platform_fundamentals_fault-handling.txt`, line 125).

`faultname` does not exist as a field; the fault *name* is the tail of `errorcode` and is
exposed as the `fault.name` flow variable. This does not break any individual scenario's
ground truth, but an agent that pattern-matches on this body shape is being trained on a
fiction. Fix once, globally.

**S2. `context.request.getValue(...)` is not a documented JavaScript API.**
The documented `context` methods are `getVariable()`, `setVariable()`, `removeVariable()`,
and the `context.*Request` objects expose *properties* (`headers`, `queryParams`, `method`,
`body`, `url`) — no `getValue`. Source:
<https://cloud.google.com/apigee/docs/api-platform/reference/javascript-object-model>
(cached: `api-platform_reference_javascript-object-model.txt`, lines 881–950 and
1042–1063). Affects **EASY-05** (where it is load-bearing) and **MED-13** (where it
appears in the remediation code).

**S3. Trace step names used across both files are undocumented.** `AM-Target-Endpoint`
(MED-06), `OAuthV2/VerifyAccessToken` (MED-10), `SA-Protect` / `AM-Count-Tokens` (EASY-08),
`SC-Enrich` (MED-12). None appear in
<https://cloud.google.com/apigee/docs/api-platform/debug/trace-overview> or
<https://cloud.google.com/apigee/docs/api-platform/fundamentals/fault-handling>. They are
plausible; they are not sourced. Low severity, but an agent asked to "cite the doc" cannot.

**S4. EASY-14 uses a fault code that the suite's own provenance rule forbids.**
Both files state: *"Do not add a code here that is not in
`.agents/skills/apigee-support-core/references/error-codes.md`."*
`messaging.adaptors.http.flow.SslHandshakeFailed` appears **zero** times in that file. The
code itself is real (see EASY-14 below); the rule is what is broken.

---

## EASY-01 Quota policy rejects the revision over a fractional interval

**Verdict**: MINOR ISSUES

**Fault codes checked**:

- `InvalidQuotaInterval` -> confirmed as a **deployment** error at
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
  (Deployment errors table, cached `api-platform_reference_policies_quota-policy.txt:1205`)
- `InvalidQuotaInterval` full cause text confirmed at
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/deployment/quota-deployment-errors>
  (cached `api-platform_troubleshoot_policies_deployment_quota-deployment-errors.txt`)
- `policies.ratelimit.QuotaViolation` / `500` -> confirmed, same quota-policy page line 1197

**Issues found**:

1. The "error message in full" the user supplies is invented:

   ```text
   Error Saving Revision 4
   InvalidQuotaInterval: The quota interval is not a valid integer.
   ```

   The documented message is:

   ```text
   Error Saving Revision [revision_number]
   Invalid quota interval [interval] in quota policy [policy_name].
   ```

   (quota-deployment-errors page, "Error message" section). A learner comparing the scenario
   string to the doc sees an immediate mismatch and learns to distrust the scenario.

2. "The save call returns HTTP 400" is not documented anywhere on the cited pages. Deployment
   errors on the quota page carry no HTTP status at all. Standard REST behaviour, but it is
   stated as fact without a source. Flagged as undocumented, not as wrong.

3. The remediation `<TimeUnit>second</TimeUnit>` is conditionally supported and the scenario
   omits the condition. The quota page states: *"The Quota policy also supports `second` as
   the time unit. However, `second` is only supported for non-distributed counters (when
   `<Distributed>` is set to `false`)."* (`api-platform_reference_policies_quota-policy.txt:768`).
   `<Distributed>` defaults to `false`, so the given XML happens to work — but the scenario
   frames the check as "confirm `second` is supported", which is the wrong question. Ask about
   `<Distributed>`, not support.

Everything else checks out: `type="rollingwindow"` is a valid quota type (same page,
`InvalidQuotaType` row), `<Interval>` must be an Integer (same page, `<Interval>` element
table), the deployment-vs-runtime split is correct, and the "0.5 worked six weeks ago"
narrative is coherent given the documented cause.

---

## EASY-02 Missing Interval produces a runtime 500, not a deploy failure

**Verdict**: CORRECT

**Fault codes checked**:

- `policies.ratelimit.FailedToResolveQuotaIntervalReference` / `500` -> confirmed at
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
  (cached `api-platform_reference_policies_quota-policy.txt:1194`). Cause text confirmed
  verbatim in substance at
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/runtime/quota-runtime-errors>
- `FailedToResolveQuotaIntervalReference` also confirmed at
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/deployment/quota-deployment-errors>
  cross-link, consistent with runtime classification.

No issues. `<Interval>` is documented Required, `<Quota>`, `<TimeUnit>`, `<Flow>`, `<Condition>`
are all real and correctly spelled. The runtime-vs-deployment distinction the scenario is
built on is exactly what the docs encode: the quota page lists
`FailedToResolveQuotaIntervalReference` under **Runtime errors** and `InvalidQuotaInterval`
under **Deployment errors**. The conditional-flow explanation for the 3% figure is sound
reasoning on top of the evidence, not an invented fault code. "`<Interval>1.0</Interval>` is
still a deployment error" is correct.

---

## EASY-03 FlowCallout cannot find the shared flow

**Verdict**: MINOR ISSUES

**Fault codes checked**:

- `flow.SharedFlowNotFound` / `500`, cause *"Either the shared flow does not exist, or the
  shared flow exists but is not deployed."* -> confirmed at
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/flow-callout-policy>
  (cached `api-platform_reference_policies_flow-callout-policy.txt:412`). The scenario's
  two-cause framing is a direct quote of the doc.
- Also listed as `Gateway SharedFlowNotFound` at
  <https://cloud.google.com/apigee/docs/api-monitoring/fault-codes> (cached `mon_fault-codes.txt:75`).

**Issues found**:

1. The diagnostic claim *"the shared flow reference is resolved at request time, not at
   upload"* is an inference presented as fact, and it points the **opposite** way from the
   shared-flows doc:
   <https://cloud.google.com/apigee/docs/api-platform/fundamentals/shared-flows>
   (cached `api-platform_fundamentals_shared-flows.txt:95`): *"Deploying the shared flow
   before the proxies makes it possible to resolve the proxy's dependency on the shared flow
   **at deploy time**."*
   That page applies to **both** Apigee and Apigee hybrid. Nothing on it or on the FlowCallout
   page states a request-time-vs-upload-time resolution rule for Apigee specifically. See also
   **MED-07**, where the same library asserts the opposite framing and claims a documented
   product difference. These two scenarios cannot both be grounded in this doc set.

2. `apigee:sharedFlow` metadata (in "Common incorrect answers") appears **nowhere** in any
   fetched page. It reads like a Maven-plugin construct that has leaked into a
   cloud.google.com-sourced scenario. Harmless as a wrong answer to reject, but unsourced.

Ground truth (shared flow not deployed to this environment) is a legitimate reading of the
documented two-cause statement plus the deployment evidence, and the difficulty label is right.

---

## EASY-04 AccessControl blocks a corporate IP range

**Verdict**: MATERIAL ERROR

**Fault codes checked**:

- `accesscontrol.IPDeniedAccess` / `403` -> confirmed at
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/access-control-policy>
  (cached `api-platform_reference_policies_access-control-policy.txt:558`). Cause text
  matches the scenario's ground truth.

**Issues found**:

1. **The XML in the diagnostic evidence uses elements that do not exist.** The scenario shows:

   ```xml
   <SourceAddress mask="32">
     <Address>203.0.113.0</Address>
     <Address>198.51.100.0</Address>
   </SourceAddress>
   ```

   `<SourceAddress>` is a leaf element whose **text content** is the address. It has no
   `<Address>` child. The doc's examples (same page, lines 34, 82, 106):

   ```xml
   <SourceAddress mask="32">198.51.100.1</SourceAddress>
   ```

   There is no `<Address>` element anywhere in the AccessControl schema.

2. **The mask semantics contradict the ground truth.** With `mask="32"` only the exact address
   `203.0.113.0` is denied. The scenario asserts *"The office egress address is 203.0.113.47,
   inside the blocked range."* It is not. Per the doc, blocking `198.51.100.*` requires
   `mask="24"` or `mask="16"`. As written, the policy would **not** block 203.0.113.47 and the
   scenario's own premise collapses.

3. Secondary: `<SourceAddress>` is shown bare, outside `<IPRules><MatchRule action="DENY">`,
   which the doc requires for a DENY rule (same page, lines 31–37). An agent being graded on
   "correlates policy range with the client IP" will be handed a config that cannot produce the
   reported fault.

The `403` status and the "policy decision, not credential failure" reasoning are correct.

---

## EASY-05 JavaScript policy blocked by a security violation

**Verdict**: MATERIAL ERROR

**Fault codes checked**:

- `steps.javascript.ScriptSecurityError` / `500`, cause *"A security error occurred when the
  `JavaScript` executed. See the fault string for details."* -> confirmed at
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/javascript-policy>
  (cached `api-platform_reference_policies_javascript-policy.txt:406`)
- `steps.javascript.ScriptExecutionFailed` / `500`, listed as a family of errors
  (RangeError, ReferenceError, SyntaxError, TypeError, URIError) -> confirmed, same line 404.
  The distinction the scenario asks for is real.

**Issues found**:

1. **The triggering call is not a restricted call.** The scenario's ground truth is: *"`context.request.getValue("computeToken")` invokes a Java method that the JavaScript sandbox blocks."* `getValue` does not exist on the request object. The documented `context.*Request` properties are `url`, `headers`, `queryParams`, `method`, `body`; the documented `context` methods are `getVariable`, `setVariable`, `removeVariable`. Source:
   <https://cloud.google.com/apigee/docs/api-platform/reference/javascript-object-model>
   (cached `api-platform_reference_javascript-object-model.txt:881–950, 1042–1063`). Calling an
   undefined method would produce `TypeError` / `ScriptExecutionFailed`, i.e. the *other* code
   the scenario is trying to distinguish. The stated cause is not supported by any page.

2. **The "diagnostic evidence" is not valid JavaScript.** `var fn = JavaScript.fromCharCode(0);`
   — `JavaScript` is not a global object in the Apigee sandbox and `fromCharCode` belongs to
   `String`. The scenario presents this as the experiment that "confirms the original call was
   blocked by the sandbox rather than failing". It confirms nothing. (`fromCharCode` and
   `computeToken` appear zero times in the entire `research/pages/` cache.)

3. `context.variable("token", fn)` is also not a documented method (see S2).

The framing — that a ScriptSecurityError is the sandbox and not a code bug, and that
`ScriptSecurityFailed`/`ScriptExecutionFailed` are different animals — is sound and matches the
doc. But the mechanism, the script, and the confirming experiment are all fabrications, and
the scenario's "critical failure" clause ("do not propose a method name not verified against
the JavaScript object model") is being enforced against a script that itself uses two
unverified method names.

---

## EASY-06 BasicAuthentication cannot resolve its source variable

**Verdict**: MATERIAL ERROR

**Fault codes checked**:

- `steps.basicauthentication.UnresolvedVariable` / `500` -> confirmed at
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/basic-authentication-policy>
  (cached `api-platform_reference_policies_basic-authentication-policy.txt:333`)

**Issues found**:

1. **The scenario states the opposite of the documented cause.** The doc says:
   > `steps.basicauthentication.UnresolvedVariable` | `500` | The required source variables for
   > the decode or encode are not present. **This error can only occur if
   > `IgnoreUnresolvedVariables` is false.**

   The scenario says: *"it can only occur when `IgnoreUnresolvedVariables` is **set**"*, puts
   `<IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>` in the config, and grounds the
   whole case on *"`IgnoreUnresolvedVariables` being set is what turned a missing variable into
   an error instead of silently continuing."* The same page's element reference is equally
   explicit: *"When set to `true`, the policy will not throw an error if a variable cannot be
   resolved... Default: true"* (line 202, 214). The documented config that produces this fault
   is `false`. This is a direct contradiction of the ground truth, and it is the exact error
   class the evaluation is supposed to catch.

2. **`<SourceVariable>` does not exist in the BasicAuthentication policy.** The scenario's
   policy config is:

   ```xml
   <BasicAuthentication name="DecodeBasicAuth">
     <SourceVariable request.header.Authorization</SourceVariable>
   ```

   The real element is `<Source>` (and `<User>`/`<Password>` are required for Decode). Same
   page, lines 109–116 and the `<Source>` element reference.

3. **The premise that flow-variable names are case-sensitive for headers is undocumented and
   probably wrong.** The entire scenario is *"HTTP header names are case-insensitive on the
   wire, but Apigee flow variable names are case-sensitive, so `request.header.Authorization`
   and `request.header.authorization` are different variables."* No such statement exists on
   <https://cloud.google.com/apigee/docs/api-platform/reference/variables-reference> — the page
   consistently renders header variables in **lowercase** (`request.header.cache-control`,
   `request.header.host`, cached `api-platform_reference_variables-reference.txt:445, 373`) and
   never discusses case sensitivity of header variable lookup. The only case-related material on
   the site is about **condition operators** (`=` is case sensitive, `:=` is case insensitive),
   <https://cloud.google.com/apigee/docs/api-platform/reference/conditions-reference>. This is
   the most plausible-but-undocumented claim in the file, and it is load-bearing.

4. The remediation's `<AssignMessage>` with `<Set><Header .../></Set>` and
   `<IgnoreUnresolvedVariables>` are all real elements
   (<https://cloud.google.com/apigee/docs/api-platform/reference/policies/assign-message-policy>,
   child element list line 40). That part is fine.

---

## EASY-07 JWS algorithm does not match between generate and verify

**Verdict**: CORRECT

**Fault codes checked**:

- `steps.jws.AlgorithmMismatch` / `401`, cause *"The algorithm specified in the header by the
  `Generate` policy did not match the one expected in the `Verify` policy. The algorithms
  specified must match."* -> confirmed at
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jws-policy>
  (cached `api-platform_reference_policies_verify-jws-policy.txt:518`)

No issues found. `<Algorithm>` is a real VerifyJWS element (line 164: valid values
`HS256, HS384, HS512, RS256, RS384, RS512, ES256, ES384, ES512, PS256, PS384, PS512`), so the
scenario's claim that PS256 is supported platform-wide and the mismatch is a local
configuration constraint is correct. The "VerifyJWS does not document a wildcard" claim holds —
the doc only documents comma-separated multiple values, with the constraint that HS*cannot be
combined with others and ES* cannot be combined with others, while RS***and** PS* can be
combined (line 157). The remediation of `RS256, PS256` is therefore legal, and the "no
wildcard" warning is correct. The 401 is correct. Difficulty label is right.

---

## EASY-08 InvalidMessageWeight does not tell you which policy failed

**Verdict**: CORRECT

**Fault codes checked**:

- `policies.ratelimit.InvalidMessageWeight` / `500`, *"the value of the `<MessageWeight>` element
  specified through a flow variable is invalid (a non-integer value)"* -> confirmed on the
  Quota page, <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
  line 1196
- The identical code, status and cause -> confirmed on the SpikeArrest page,
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy>
  (cached `api-platform_reference_policies_spike-arrest-policy.txt`, runtime errors table)

No issues. The central pedagogical claim — one code, two policies, trace step name is the
discriminator — is exactly what the two pages show. `<MessageWeight>`, `<Identifier>`,
`<Rate>`, `<UseEffectiveCount>` are all real SpikeArrest children. The "raising the weight to 0
changes what the limit means" critique of the `ratelimit.<policy>.exceed.count` / weight
semantics is sound. The `parseInt(..., 10)` fallback is a legitimate fix. This is one of the
cleanest scenarios in the file.

---

## EASY-09 JSONToXML receives a non-JSON source

**Verdict**: MATERIAL ERROR

**Fault codes checked**:

- `steps.jsontoxml.InvalidSourceType` / `500`, cause *"This error occurs if the type of the
  variable used to define the `<Source>` element is invalid. The valid types of variable are
  `message` and `string`."* -> confirmed at
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/json-xml-policy>
  (cached `api-platform_reference_policies_json-xml-policy.txt:603`)

**Issues found**:

1. **The stated cause contradicts the documented cause.** The scenario's ground truth is:
   *"The client is sending JSON in the body while declaring the content type as `text/plain`.
   The JSONToXML policy expects a JSON source and rejects the type."*
   `InvalidSourceType` is about the **type of the flow variable named in `<Source>`** — i.e. the
   variable resolved to something that is neither `message` nor `string`. It has nothing to do
   with the HTTP `Content-Type` header or the shape of the payload.

   A client posting `Content-Type: text/plain` with a JSON body would, if anything, hit
   `steps.jsontoxml.ExecutionFailed` ("The input payload (JSON) is empty or the input (JSON)
   passed to JSON to XML policy is invalid or malformed", same page line 601) — or succeed
   entirely, since the policy does not read the declared content type. The scenario attributes
   a fault to a condition the doc does not describe, and the remediation ("On the client side,
   send `Content-Type: application/json`") would not change the fault at all.

2. Consequential: the "Common incorrect answers" entry — *"Blaming the Apigee runtime. The
   documented cause is a client-supplied source type"* — is the documented cause stated
   correctly. The scenario's own "Common incorrect answers" section contradicts its ground
   truth section.

The `500` status is correct, `<Source>` and `<OutputVariable>` are real elements, and the
"don't blanket-rewrite content types" safety reasoning is good. The fault-code-to-cause mapping
is wrong.

---

## EASY-10 HMAC policy missing a required element

**Verdict**: MATERIAL ERROR

**Fault codes checked**:

- `steps.hmac.MissingConfigurationElement`, listed under **Deployment errors** -> confirmed at
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/hmac-policy>
  (cached `api-platform_reference_policies_hmac-policy.txt:356`)

**Issues found**:

1. **Two non-existent elements.** The diagnostic evidence names
   `<SecretVariable>` and `<VerificationOutput VariableToVerify>`. Neither exists. The HMAC
   policy's real children are `<Algorithm>`, `<DisplayName>`, `<Message>`, `<Output>`,
   `<SecretKey>`, `<VerificationValue>`, `<IgnoreUnresolvedVariables>`
   (`api-platform_reference_policies_hmac-policy.txt`, element reference headings).
   `<VerificationOutput>` additionally has no `VariableToVerify` attribute because it does not
   exist at all.

2. **`<Algorithm>HS256</Algorithm>` is invalid for the HMAC policy.** The deployment-error table
   (same page, line 357) states `steps.hmac.InvalidValueForElement` fires when the `<Algorithm>`
   value *"is not one of the following values: `SHA-1`, `SHA-224`, `SHA-256`, `SHA-512`, or
   `MD-5`."* A policy configured with `HS256` would be rejected with
   `InvalidValueForElement`, not `MissingConfigurationElement`. The scenario's stated trigger —
   a broken template removing the secret element — is undermined by the fact that the policy
   is already broken in a second, earlier way.

3. **HTTP status mismatch.** The scenario asserts "The save returns HTTP 400." The page it
   cites assigns **401** to `steps.hmac.MissingConfigurationElement`, even in the deployment
   errors table. The 400 is plausible for a Management API save rejection, but it contradicts
   the cited page and is not sourced. Flagged.

The classification of this error name as a deployment-stage failure is **correct** and is the
scenario's actual teaching point. Its "critical failures" and the old-revision explanation are
sound. Only the XML and the status are wrong.

---

## EASY-11 Unsupported TimeUnit blocks the revision

**Verdict**: MINOR ISSUES

**Fault codes checked**:

- `InvalidQuotaTimeUnit`, *"If the time unit specified in the `<TimeUnit>` element is
  unsupported, then the deployment of the API proxy fails. The supported time units are
  `minute`, `hour`, `day`, `week`, and `month`."* -> confirmed at
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
  (cached `api-platform_reference_policies_quota-policy.txt:1206`) and expanded at
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/deployment/quota-deployment-errors>

**Issues found**:

1. **The "documented list" is narrower than the same page's element reference.** The scenario
   states twice that *"The supported values are `minute`, `hour`, `day`, `week` and `month`"*,
   and the rubric awards full marks for naming "the full documented list". The `<TimeUnit>`
   element section on that same page (line 763) says: *"Select from `minute`, `hour`, `day`,
   `week`, `month`, **or `year`**"*, and the following note (line 768) adds `second` under the
   `<Distributed>false</Distributed>` condition. So the page documents at least seven usable
   values, not five. A grader following the rubric literally would mark a correct answer wrong.
   The five-value list is correct only as a verbatim reading of the `InvalidQuotaTimeUnit` row —
   the scenario should say so rather than calling it the documented list.

2. The scenario calls its citation "Quota policy deployment errors" while pointing at the
   Quota *policy reference*. The policy page does carry a Deployment errors section, so this
   is a labelling quibble, not a bad link. The playbook at
   `troubleshoot/policies/deployment/quota-deployment-errors` would be the tighter citation.

The singular/plural insight, the "1 minutes is doubly wrong" observation, and the
`day` remediation are all correct.

---

## EASY-12 Rejected token looks like a clock skew problem

**Verdict**: MATERIAL ERROR

**Fault codes checked**:

- `steps.oauth.v2.InvalidEarlyTimestamp` -> **NOT FOUND** on the page the scenario cites.
  It appears on
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/revoke-oauth-v2-policy>
  (cached `api-platform_reference_policies_revoke-oauth-v2-policy.txt:315`), documented as:
  `steps.oauth.v2.InvalidEarlyTimestamp` | **500** | **"Timestamp cannot be earlier than
  January 1, 2014."**
  The cited page, <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>,
  contains no timestamp fault codes at all (its runtime table runs
  `access_token_expired`, `access_token_not_approved`, `FailedToResolve*`, `InvalidRequest`,
  `InvalidAccessToken`, `InvalidClientIdentifier`, `InsufficientScope`, etc.).
  The repository's own `error-codes.md` line 124 agrees: the code is attributed to
  `revoke-oauth-v2-policy` with status **500**.

**Issues found**:

1. **Wrong status.** The scenario says `401`. The doc says `500`.

2. **Wrong cause.** The scenario builds its whole ground truth on `nbf` clock skew: *"`nbf`
   (not before) is a claim about when a token becomes valid. An early timestamp fault means the
   presented token is not valid yet, according to the runtime's clock."* The documented cause is
   a **lower-bound validation of a timestamp supplied to the RevokeOAuthV2 policy** — it must
   not be earlier than 1 January 2014. That is not an `nbf` claim, not a clock-skew check, and
   it has nothing to do with client devices.

3. **Wrong policy.** The code belongs to `revoke-oauth-v2-policy`, not `oauthv2-policy`. The
   scenario's ticket ("401 from the token endpoint", "devices whose clocks drift") describes a
   verification flow; the code the scenario quotes is thrown by a revocation flow.

4. **The three-code relationship is misdescribed.** The scenario says `InvalidEarlyTimestamp`
   "is distinct from `InvalidFutureTimestamp` and `InvalidTimestamp`, which point at different
   clock problems". On the revoke page all three are timestamp-*input* validations
   ("cannot be earlier than January 1, 2014" / "cannot be in the future" / "is invalid") — three
   shapes of one bad-input condition, not three clock problems. Note that the *sibling* family
   does exist with the statuses the scenario describes, but on the JWS/DecodeJWS pages
   (`steps.jws.InvalidClaim`, `steps.jwt.InvalidClaim` / `steps.jws.MissingPayload`), which the
   scenario does not cite.

This scenario would teach an agent to confidently attach a real fault code to a cause the
documentation does not state. That is the worst failure mode in the suite.

---

## EASY-13 JWKS verification fails because the token has no key id

**Verdict**: CORRECT

**Fault codes checked**: none quoted — the scenario deliberately names no code.

- The behaviour is quoted near-verbatim from
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/jwt-policies-overview>
  (cached `api-platform_reference_policies_jwt-policies-overview.txt:357`, JWKS resolution
  step 3): *"Examine the JWS/JWT header to find the Key ID (kid). If the inbound JWT does not
  include a key ID (kid) in the header, then the mapping of kid to verification-key is not
  possible, and Apigee will throw a fault."*
- For reference, the specific code the doc implies is
  `steps.jws.KeyIdMissing` / `401`, *"The `Verify` policy uses a JWKS as a source for public
  keys, but the signed JWS does not include a `kid` property in the header"* —
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jws-policy>
  line 533.

No issues. The step ordering claim ("the resolution step fails before verification happens")
matches the doc's numbered sequence, which places `kid` resolution at step 3 and signature
verification at step 6. Not naming a code is a defensible choice given the scenario's stated
evaluation objective, and it is honestly scoped rather than underdetermined. The fallback
advice (explicit key instead of JWKS, with the rotation cost named) is correct and correctly
weighted.

---

## EASY-14 Target handshake fails against a legacy TLS backend

**Verdict**: MINOR ISSUES

**Fault codes checked**:

- `messaging.adaptors.http.flow.SslHandshakeFailed` -> confirmed at
  <https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls>
  (cached `api-platform_system-administration_options-configuring-tls.txt:8`, fetched and
  re-verified live): *"Apigee does not support the use of TLS 1.0 or TLS1.1. If you use these
  protocols in your target endpoint configuration, the Apigee target endpoint throws the error
  `messaging.adaptors.http.flow.SslHandshakeFailed`."*
- Also catalogued at <https://cloud.google.com/apigee/docs/api-monitoring/fault-codes>
  (cached `mon_fault-codes.txt:77`, category "Target").

**Issues found**:

1. **Provenance rule violation (see S4).** The code does not appear in
   `.agents/skills/apigee-support-core/references/error-codes.md`, which both files declare to
   be the authoritative list. Either add it to the index or drop the code.

2. **The 502 is not documented on the cited pages.** `options-configuring-tls` gives no HTTP
   status for the handshake failure, and neither does the API Monitoring fault-code table.
   502 is what Apigee returns for target-side failures in practice, but the scenario asserts it
   without a source.

Everything else is strong. `<SSLInfo>` / `<Enabled>` are real
(<https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls>
lines 22–23). The `IgnoreValidationErrors`-does-not-help reasoning is correct and matches the
doc's own distinction between validation (`<IgnoreValidationErrors>`) and protocol negotiation
(`<Protocols>`), and refusing to invent an Apigee-side workaround is the right call.

---

## EASY-15 Quota counter behaves differently than the team expects

**Verdict**: CORRECT

**Fault codes checked**: none quoted.

No issues. The scope rule is quoted near-verbatim from
<https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
(cached `api-platform_reference_policies_quota-policy.txt:14`): *"Quotas apply to individual API
proxies and are not distributed among API proxies. For example, if you have three API proxies
in an API product, a single quota is not shared across all three even if all three use the same
quota policy configuration."* That is almost exactly the scenario's ground truth, including the
three-proxy example. `<Interval>1</Interval>` / `<TimeUnit>month</TimeUnit>` is valid. The
remediation options (accept and document; move to a shared point; consolidate) are all real
architectures, and the warning against bumping to 30,000 is correct reasoning about config
coupling. Correctly framed as an expectation mismatch rather than a defect.

---

## MED-01 Deployed successfully, every request returns 404

**Verdict**: MINOR ISSUES

**Fault codes checked**: none quoted.

**Issues found**:

1. **Citation does not support the product claim.** The scenario's parenthetical *"Product:
   Apigee (environment groups do not exist on Edge)"* and its "establish the product first"
   objective are supported by the **Edge-to-X** comparison,
   <https://docs.apigee.com/migration-to-x/compare-apigee-edge-to-apigee-x>
   (cached `edge-vs-x.txt:62–68`, where "Environments → Support for environment groups" appears
   in the "Support in Apigee X and hybrid" column). The scenario instead cites
   <https://cloud.google.com/apigee/docs/api-platform/get-started/compare-apigee-products>,
   which compares Apigee X against **hybrid** and says nothing about Edge at all. The conclusion
   is right; the citation will not support it.

2. The central documented requirement is confirmed and quoted correctly: *"An environment must
   be a member of at least one environment group before you can access proxies deployed within
   it."* — <https://cloud.google.com/apigee/docs/api-platform/fundamentals/environments-overview>
   (cached `api-platform_fundamentals_environments-overview.txt:16`, repeated in the "Key
   points" table at line 142). Also confirmed: an environment group is where hostnames live,
   not the environment (line 14), which is the causal step the scenario relies on.

The scenario is sound, correctly labelled medium, and the "resist the redeploy" discipline is
the right lesson. Only the reference list is off by one hop.

---

## MED-02 Works for some users, 404s for others, same deployment

**Verdict**: MINOR ISSUES

**Fault codes checked**: none quoted.

**Issues found**:

1. **`DEPLOYING` is not a documented deployment state.** The docs show only `"state": "READY"`:
   <https://cloud.google.com/apigee/docs/api-platform/deploy/ui-deploy-overview>
   (cached `api-platform_deploy_ui-deploy-overview.txt`, "Viewing deployment status" API
   example). I fetched the deployments API reference
   (<https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.environments.apis.revisions.deployments>,
   HTTP 200) and it does not enumerate state values either. `DEPLOYING` is a real API enum value
   in practice, but it is unsourced here. `READY` is fine.

2. **The evidence imports MED-01's finding into MED-02.** The diagnostic evidence folds in
   "the 404 is the environment group issue from MED-01", making this scenario depend on a
   cross-reference rather than being self-contained. The scenario then concedes it is "two
   problems that happen to present together", which undercuts its own "medium" premise — an
   agent is really being asked to solve a two-part question where one part is handed to it.

The underlying model is confirmed and correctly used: *"In Apigee, MPs act independently of one
another and any given MP can be in a different state than the other MPs... This is known as an
eventually consistent deployment model"* and *"Deploying an API proxy on Apigee does not make it
immediately available"* (same page, lines 19 and 49). The "deployments are not regional by
design" trap and the "do not redeploy to force propagation" answer are both correct. Only the
state enum and the self-containment are problems.

---

## MED-03 Load balancing does not fail over to a healthy backend

**Verdict**: MATERIAL ERROR

**Fault codes checked**: none quoted.

**Issues found**:

1. **Four element/attribute names in both config blocks do not match the documentation.** The
   documentation at
   <https://cloud.google.com/apigee/docs/api-platform/deploy/load-balancing-across-backend-servers>
   (cached `api-platform_deploy_load-balancing-across-backend-servers.txt:322–340, 247–258`)
   uses:

   ```xml
   <LoadBalancer>
     <Algorithm>RoundRobin</Algorithm>
     <Server name="target1" />
     <Server name="target2" />
     <MaxFailures>5</MaxFailures>
     <ServerUnhealthyResponse>...</ServerUnhealthyResponse>
   </LoadBalancer>
   ```

   The scenario uses `<LoadBalancing>` (wrong element name), `<TargetServer>orders-1</TargetServer>`
   (wrong — it is `<Server name="..."/>`), and `<Algorithm>ROUND_ROBIN</Algorithm>` (wrong value
   — *"The available algorithms are `RoundRobin`, `Weighted`, and `LeastConnections`"*, line 237;
   the default is `RoundRobin`).

2. **`<MinTimeBetweenFailures>` does not exist in the current docs.** It appears nowhere in
   `load-balancing-across-backend-servers`, nowhere in
   <https://cloud.google.com/apigee/docs/api-platform/reference/endpoint-properties-reference>,
   and nowhere in <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>
   (I re-fetched this page live: 200, 69,358 bytes, zero hits). It is in the remediation block,
   so an agent copying the answer ships a config that either errors on validation or is silently
   ignored.

3. **Wrong citation.** The scenario's References list
   `api-platform/reference/api-proxy-configuration-reference` for `<MaxFailures>` and
   `<ServerUnhealthyResponse>`. Neither string appears on that page. The supporting page is
   `api-platform/deploy/load-balancing-across-backend-servers`.

The **reasoning is correct and is the scenario's actual value**:

- *"**The MaxFailures default is 0.** This means that Apigee always tries to connect to the target
  for each request and never removes the target server from the rotation."* (line 342) — the
  scenario's headline claim is verbatim correct.
- *"when Apigee does receive a response from a target, even if the response is an HTTP error
  (such as `404` or `500`), that counts as a response from the target server, and the failure
  counter is reset. To ensure that bad HTTP responses (such as `500`) also increment the failure
  counter... you can add the `<ServerUnhealthyResponse>` element"* (line 314) — the scenario's
  second claim is verbatim correct.
- `RetryEnabled` defaults to `true` and requires two target servers (lines 360–370); the
  scenario's dismissal of "add a Retry policy to the proxy" as the wrong layer is right.

So the diagnosis is documented; every line of XML in the scenario is wrong.

---

## MED-04 Cached responses are stale and nobody can reproduce it

**Verdict**: MATERIAL ERROR

**Fault codes checked**: none quoted.

**Issues found**:

1. **`<Key>` does not exist in the ResponseCache policy.** The scenario's diagnostic evidence —
   *"The ResponseCache policy has a `<Key>` expression that includes the request URL"* — names
   a non-existent element. The real structure, per
   <https://cloud.google.com/apigee/docs/api-platform/reference/policies/response-cache-policy>
   (cached `api-platform_reference_policies_response-cache-policy.txt:51–59, 190–232`):

   ```xml
   <ResponseCache name="ResponseCache">
     <CacheKey>
       <KeyFragment ref="request.queryparam.w" />
     </CacheKey>
     <ExpirySettings>
       <TimeoutInSeconds>600</TimeoutInSeconds>
     </ExpirySettings>
   </ResponseCache>
   ```

   Confirmed by <https://cloud.google.com/apigee/docs/api-platform/reference/policies/working-cachekeys>
   (cached `api-platform_reference_policies_working-cachekeys.txt`): *"Apigee uses the values of
   configuration elements -- `<Scope>`, `<CacheKey>`/`<Prefix>`, and `<CacheKey>`/`<KeyFragment>`
   -- to compose a value for the cache key."* Since the `<Key>` expression is the artifact the
   agent is supposed to go read, an agent following the scenario literally will find nothing to
   read.

2. **`expiryInSeconds` is not an element.** The scenario says *"a ResponseCache policy on the
   response path with a short `expiryInSeconds`"*, and later *"Setting `expiryInSeconds` to 0"*.
   The real elements are `<ExpirySettings>` with `<TimeoutInSeconds>`, `<ExpiryDate>` and
   `<TimeOfDay>` children (same page, lines 354–426). There is no `expiryInSeconds`.

The analytical structure is good and the two-layer attribution (Apigee cache vs. upstream
five-minute TTL) is exactly the right lesson, and the cross-tenant cache-key defect is a real
and serious finding. But the config vocabulary is invented.

---

## MED-05 Key value map updates are not visible everywhere

**Verdict**: MATERIAL ERROR

**Fault codes checked**: none quoted.

**Issues found**:

1. **The central claim is presented as documented and I could not find it documented anywhere.**
   The scenario's origin is "documented", its evaluation objective is "recognize documented
   single-node cache refresh", and its ground truth is *"A `PUT` refreshes the cache on one node
   only, so other nodes pick up the new value after their cache refresh."*

   I checked <https://cloud.google.com/apigee/docs/api-platform/cache/key-value-maps>
   (re-fetched live: HTTP 200, 28,928 bytes) for `propagat`, `eventual`, `refresh`,
   `consistent`, `one node`, `single node`, `immediate` — **zero** substantive hits; the only
   matches are the word "cache" used in the sense of "values don't expire like a cache might"
   (line 28). I also checked
   <https://cloud.google.com/apigee/docs/api-platform/cache/cache-internals>,
   <https://cloud.google.com/apigee/docs/api-platform/reference/policies/key-value-map-operations-policy>
   and the KVM runtime/deployment playbook pages — no propagation statement in any of them. The
   repository's own `research/official-documentation-index.md` has no source for it either.

   The behaviour is plausible; the label "documented" is not. An agent that follows this
   scenario's instruction to "look for documented propagation behavior" and then reports
   "the docs say X" will be fabricating a citation. Re-label as synthetic, or find the source.

2. **The `private.` framing is slightly off.** The scenario says *"verify they are in a secured
   map... A forgotten `private.` prefix means the value is visible in debug output in
   cleartext."* The doc is about the **variable name** used when retrieving a value through the
   KeyValueMapOperations policy, not about map classification: *"Because all KVM values are
   encrypted, you need to add the `private.` prefix to the variable name, which prevents the KVM
   key/value pairs from appearing in Debug sessions."*
   (<https://cloud.google.com/apigee/docs/api-platform/cache/key-value-maps>, lines 130 and 258;
   same wording in the KeyValueMapOperations `<Get>` docs). "Secured map" is not a KVM concept in
   this doc set.

The staged-cutover remediation and the "don't print the value in debug" safety point are sound
operational advice; they just are not sourced.

---

## MED-06 Latency jumped and nobody knows which layer moved

**Verdict**: MINOR ISSUES

**Fault codes checked**: none quoted.

**Issues found**:

1. The trace step name `AM-Target-Endpoint` is not documented (see S3).

Nothing else. The scenario is honestly marked synthetic, requires measurement before
attribution ("an independent measurement of the target reproduces the delay without Apigee in
the path"), and the three listed failure modes — blaming Apigee, raising the timeout, adding a
cache — are the right ones. The line "the absence of a deploy is not evidence of applause; it is
the absence of one class of cause" is a good calibration lesson. The timeout side-effect
warning is a real risk. Difficulty label is appropriate.

---

## MED-07 Shared flow deploys on one product and fails on another

**Verdict**: MATERIAL ERROR

**Fault codes checked**: none quoted.

**Issues found**:

1. **The claimed documented product difference does not exist in the doc set.** The scenario's
   origin is "documented" and its stated ground truth is *"Hybrid validates shared-flow
   dependencies at deployment time. Apigee resolves the reference when the request runs."*
   Neither cited page supports a product split:
   - <https://cloud.google.com/apigee/docs/api-platform/fundamentals/shared-flows> carries the
     banner *"This page applies to **Apigee** and **Apigee hybrid**"* (cached
     `api-platform_fundamentals_shared-flows.txt:1`) and states, for **both** products:
     *"Deploying the shared flow before the proxies makes it possible to resolve the proxy's
     dependency on the shared flow at deploy time."* (line 95) and *"The consuming API proxy
     must be deployed **after** the shared flow and to the same environment"* (line 115).
   - <https://cloud.google.com/apigee/docs/api-platform/get-started/compare-apigee-products>
     compares Apigee X with hybrid and says nothing about shared-flow deployment validation.
   - <https://cloud.google.com/apigee/docs/api-platform/get-started/apigee-feature-summary>
     (fetched live, 200) — no shared-flow entry.

   The doc statement leans the *opposite* way from the scenario's "Apigee resolves at request
   time" half. The FlowCallout page does document `flow.SharedFlowNotFound` as a **500 runtime**
   fault, which is consistent with request-time resolution, but no page states that Apigee and
   hybrid behave differently here.

2. **It directly contradicts EASY-03.** EASY-03's diagnostic evidence states *"The proxy
   deployment succeeded because the shared flow reference is resolved at request time, not at
   upload"* on **Apigee**. MED-07 states the identical bundle is **rejected at deploy time** on
   hybrid and that this is the documented difference. Both are marked "documented"; the two
   scenarios cannot both be right, and neither is sourced.

3. **The verification step is incoherent.** *"Confirm requests fail with a shared-flow-not-found
   style fault rather than a deployment error, which confirms the deployment-time dependency is
   satisfied."* A `SharedFlowNotFound` fault is the failure you are fixing; asserting it as the
   success signal means the check can never pass as written.

Note the irony: the release notes contain *"FlowCallout succeeded, although SharedFlow had
   errors in deployment. (Fixed in Apigee hybrid v1.6.1)"*
   (cached `hybrid_release-notes.txt:9543`) — i.e. a historical hybrid behaviour where the
   dependency was *not* enforced, which is the opposite direction and a different bug. That is
   not what the scenario is about, and it is not the claim the scenario makes.

---

## MED-08 Mutual TLS broke after a certificate authority renewal

**Verdict**: CORRECT

**Fault codes checked**: none quoted.

No issues. The ground truth is quoted almost verbatim from
<https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>
(cached `api-platform_reference_api-proxy-configuration-reference.txt:745–747`, re-verified on
a live fetch):
> *"Public Certificate Authorities (CAs) are discontinuing the inclusion of the `clientAuth`
> Extended Key Usage (EKU) in latest publicly-trusted SSL/TLS certificates. This industry-wide
> change affects Apigee mutual TLS (mTLS) configurations... **Apigee requires the `clientAuth` EKU
> to be present in client certificates for mTLS handshakes. Without this EKU, mTLS connections
> will fail for both northbound (client to Apigee) and southbound (Apigee to backend) traffic.**"*

That covers the two-sided failure, the renewal trigger, the direction of the diagnosis ("inspect
the EKU before looking at chains, protocols or keystore state"), and the remediation being a CA
reissue rather than an Apigee change. The dismissal of `IgnoreValidationErrors` as the fix is
correct — that element affects certificate validation, not key-usage extension checking, as the
TLS page's own element descriptions distinguish. The "a northbound pass does not imply a
southbound pass" verification discipline is right and is the reason this scenario earns its
"medium" label. Best-documented scenario in the set.

---

## MED-09 Intermittent 429 under bursty client traffic

**Verdict**: MATERIAL ERROR

**Fault codes checked**:

- `policies.ratelimit.QuotaViolation` / `500` -> confirmed at
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
  line 1197 ("The quota limit was exceeded.")

**Issues found**:

1. **Two non-existent SpikeArrest elements in the remediation.** The scenario says: *"add
   SpikeArrest with a low `rateLimit` and a short `timeWindow` for burst protection."*
   <https://cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy>
   (cached `api-platform_reference_policies_spike-arrest-policy.txt`) documents the child
   elements as **`<Identifier> <MessageWeight> <Rate> (Required) <UseEffectiveCount>`**
   (line 52). A grep for `TimeWindow` and for `rateLimit` across the whole page returns **0
   hits**. The policy has no `<TimeWindow>` element and no `rateLimit` element. The correct
   configuration is `<Rate>intps</Rate>` / `<Rate>intpm</Rate>` only.

2. **The scenario's title contradicts its own evidence and its own citation.** The title says
   "Intermittent **429**". The evidence says *"clients receive `policies.ratelimit.QuotaViolation`
   with HTTP **500**."* The Quota policy page says 500. The 429 comes from
   `policies.ratelimit.SpikeArrestViolation` (SpikeArrest page), which the scenario has not
   deployed yet. The scenario therefore teaches the wrong status for the policy the reporter
   actually has.

3. **The doc set is itself contradictory here, and the scenario does not say so.** The
   comparison page <https://cloud.google.com/apigee/docs/api-platform/develop/comparing-quota-and-spike-arrest-policies>
   (cached `api-platform_develop_comparing-quota-and-spike-arrest-policies.txt:22`) states in
   its chart: *"HTTP status code when limit has been reached: 429 (Too Many Requests)"* for
   **Quota** as well as SpikeArrest — contradicting the Quota policy page's 500. This is a real
   inconsistency in the documentation. A good scenario would surface it as part of the
   diagnostic work ("the two pages disagree; the policy reference is authoritative"). This one
   silently picks a side in the title and a different side in the body.

The policy-choice argument itself is **correct and well cited**: *"Don't use it [Quota] to:
Protect your API proxy's target backend against traffic spikes. Use SpikeArrest or PromptTokenLimit
for that"* (same comparison page, line 19), and *"If you use both SpikeArrest and Quota policies
in the same proxy, SpikeArrest should always be attached before the Quota policy"*
(line 21). The "the quota is enforcing correctly, the policy choice is wrong" conclusion is
sound. The SpikeArrest configuration the scenario hands the agent is not.

---

## MED-10 Token works against one API and fails against another

**Verdict**: MINOR ISSUES

**Fault codes checked**:

- `steps.oauth.v2.access_token_expired` / **401** "The access token is expired." ->
  confirmed at <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>
  (cached `api-platform_reference_policies_oauthv2-policy.txt:1328`, Thrown by operations:
  `VerifyAccessToken InvalidateToken`)
- `steps.oauth.v2.access_token_expired` / **500** "The access token sent to the policy is
  expired." -> confirmed at
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/get-oauth-v2-info-policy>
  and <https://cloud.google.com/apigee/docs/api-platform/reference/policies/set-oauth-v2-info-policy>
- `invalid_client` / 401 when `<GenerateResponse>` is true and `InvalidClientIdentifier` / 500
  when it is false -> confirmed, oauthv2-policy runtime table. The scenario's "splits on
  `<GenerateResponse>`" is exact.

**Issues found**:

1. **The diagnostic evidence contradicts the ground truth.** The scenario's evidence says: *"A
   trace of the failing proxy shows `OAuthV2/VerifyAccessToken` **succeeded** at the validate
   step and the failure occurs at a later `SetOAuthV2Info` step."* But the ground truth is
   *"The token is expired... `VerifyAccessToken` surfaces 401."* Per the OAuthV2 page,
   `access_token_expired` is thrown **by** `VerifyAccessToken`; it cannot succeed with an expired
   token. Either the trace line or the ground truth is wrong, and an agent reasoning from the
   trace would conclude the first proxy is fine, which is the opposite of the scenario's
   premise.

2. The `oauth-http-status-code-reference` citation is explicitly deprecated (the page's own
   banner). The scenario labels it "deprecated but informative", which is honest, and the
   primary citation (the three live policy pages) is the right one.

The core teaching point — same condition, different status, because the status is
policy-specific — is exactly right and precisely documented. One contradictory evidence line.

---

## MED-11 Everything works in test and fails in production

**Verdict**: MINOR ISSUES

**Fault codes checked**: none quoted.

**Issues found**:

1. **The evidence does not establish why `test` succeeds.** The diagnostic evidence says
   `prod` has `orders.timeout` = `30` and *"`test` has no such key"*, and that the JavaScript
   policy *"produces a malformed value in production only."* A missing key in `test` is itself a
   difference that the same script has to survive; the scenario never states that the policy
   defaults when the variable is absent, so an agent cannot derive "malformed in prod only"
   from the evidence given. It has to assume the missing-value case is handled. That is the
   one step that separates the scenario from being fully solvable, and it is the step the
   scenario asserts rather than supplies.

Everything else is sound: the general shape (identical bundle, environment-scoped
configuration differs) is a real and common failure class; the KVM page correctly supports the
claim that maps live outside the proxy bundle
(<https://cloud.google.com/apigee/docs/api-platform/cache/key-value-maps>); the
"redeploying is not the fix" and "don't hand-copy maps" answers are right; and the scenario is
honestly marked synthetic. The `private.`-prefix advice in MED-05 is echoed correctly here.

---

## MED-12 Service callout times out and takes the request with it

**Verdict**: CORRECT

**Fault codes checked**: none quoted directly, but the behaviour is documented:

- `<Timeout>` element, milliseconds, **default 55000**:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/service-callout-policy>
  (cached `api-platform_reference_policies_service-callout-policy.txt:414–430`)
- *"If the ServiceCallout hits a timeout, an HTTP 500 is returned, the policy fails, and the API
  proxy goes into an error state, as described in Handling faults."* (line 416) — the 500 in
  the ticket is documented.
- `InvalidTimeoutValue` deployment error for a zero or negative `<Timeout>` (deployment errors
  table) — consistent.

No issues. The `<Timeout>` element name is real, the configured-timeout-vs-upstream-timeout
distinction is the correct reading of "You cannot set this value dynamically at runtime", the
"p95 hides the tail" reasoning is sound (and is the reason the doc's own advice to check
`ratelimit.<policy>.available.count` matters), and the remediation set — raise within a latency
budget, or degrade via a fault rule, or cache — is all legitimate. "Handle it in a fault flow
rather than letting the callout fault surface as a 500" is directly supported by the
`goes into an error state` wording. The `service-callout` + `fault-handling` citation pair is
appropriate.

---

## MED-13 Two conditions produce the same error code

**Verdict**: MINOR ISSUES

**Fault codes checked**:

- `steps.javascript.ScriptExecutionFailed` / `500`, *"The `JavaScript` policy can throw many
  different types of `ScriptExecutionFailed` errors. Commonly seen types of errors include
  RangeError, ReferenceError, SyntaxError, TypeError, and URIError."* -> confirmed at
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/javascript-policy>
  (cached `api-platform_reference_policies_javascript-policy.txt:404`)
- `steps.javascript.ScriptExecutionFailedLineNumber` / `500`, *"An error occurred in the
  `JavaScript` code. See the fault string for details."* (line 405) — the "check the fault
  string" guidance is documented twice.

**Issues found**:

1. **The remediation uses an undocumented JavaScript API** (see S2):

   ```javascript
   var raw = context.request.getValue("items");
   ```

   The documented way to read a flow variable from JavaScript is
   `context.getVariable("request.queryparam.items")`
   (<https://cloud.google.com/apigee/docs/api-platform/reference/javascript-object-model>,
   lines 881–900). As written the guard does not work, which is the opposite of the
   scenario's intent.

Everything else is correct: the null-dereference diagnosis, the fault-string-as-diagnostic /
not-as-error-handling distinction (which the scenario states carefully and correctly), the
hourly/peak correlation explanation, and the "raising the JavaScript timeout does not apply"
trap. The difficulty label is right — the work is asking for the fault string and reading it.

---

## MED-14 A revoked token still works for a few minutes

**Verdict**: MINOR ISSUES

**Fault codes checked**: none quoted directly; the behaviour is documented verbatim:
> *"**Warning:** OAuth tokens are cached for three minutes (180 seconds); therefore, a revoked
> token may still succeed for up to three minutes, until its cache limit expires."*

Confirmed at:

- <https://cloud.google.com/apigee/docs/api-platform/security/oauth/validating-and-invalidating-access-tokens>
  (three occurrences, lines 10, 29 and in context; fetched live, HTTP 200, 9,224 bytes)
- <https://cloud.google.com/apigee/docs/api-platform/security/oauth/enable-retrieval-and-revocation-oauth-20-access-tokens-end-user-id-app-id-or-both>
  (line 8; fetched live, HTTP 200, 5,761 bytes)

**Issues found**:

1. **The citation does not contain the claim.** The scenario's sole reference is
   <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>. I
   checked that page for a three-minute caching statement; there is none. The claim lives on
   the two `security/oauth/*` pages above. An agent told to "stop at the documented cache
   window" and pointed at the OAuthV2 policy page will not find it — which is the exact skill
   the scenario claims to test.

Otherwise the scenario is strong: the correct conclusion (revocation works, the window is
documented), the correct escalation to a real security consequence (revocation alone is not
sufficient for immediate lockout, use the identity provider), and a genuinely good
"common incorrect answer" — advising the security team to accept the window during a credential
compromise. The "no documented supported way to force-flush token caches" claim checks out: no
such mechanism appears in the OAuthV2, OAuth security, or cache-internals pages. `InvalidateToken`
is a real `<Operation>` value.

---

## MED-15 A Java callout fails only on some requests

**Verdict**: MATERIAL ERROR

**Fault codes checked**:

- `JavaClassNotFoundInJavaResource`, fault string `Failed to find the ClassName in java resource
  [jar_name] - [class_name]`, HTTP status `N/A`, listed under **Deployment errors** ->
  confirmed at <https://cloud.google.com/apigee/docs/api-platform/reference/policies/java-callout-policy>
  (cached `api-platform_reference_policies_java-callout-policy.txt:226–233`, under the heading
  *"These errors can occur when the proxy containing the policy is deployed."*)
- `steps.javacallout.ExecutionError` / `500` is the **only** runtime error the page documents
  (same page, runtime errors table, one row).

**Issues found**:

1. **The scenario asserts a deployment-only error code at runtime, against the page it cites.**
   The diagnostic evidence states: *"The first request in each hour succeeds and subsequent
   ones fail with `JavaClassNotFoundInJavaResource`."* Per the Java callout page, that code is
   emitted when the proxy is **deployed**, and the scenario's own evidence three lines earlier
   says *"Deployment succeeded, so the class was found at deploy time."*

2. **The scenario is internally self-contradictory.** Its "Expected investigation" says *"classpath
   and class-definition errors are unlikely, because those are deployment errors"*; its "Ground
   truth resolution" says *"The documented class-not-found errors surface as deployment
   failures, which is the distinguishing signal: deployment succeeded, so this is not a
   classpath problem at deploy time."* Then the evidence reports that class-not-found code from
   the request path. An agent cannot satisfy both the stated ground truth and the stated
   evidence. Either answer is marked wrong by half the scenario.

3. **The remediation inherits the contradiction.** *"If the class genuinely cannot be resolved at
   runtime for some requests..."* — the doc does not describe a request-scoped class-resolution
   failure for this policy.

The one genuinely good instinct here is well handled: refusing to name a specific Java
exception from a fault code alone, and asking for the full stack trace, since the page's fault
strings carry the detail. That should be a different scenario. As written this one asks the
agent to accept a documented deployment error occurring at runtime.

---

## Summary table of MATERIAL ERRORs

| Scenario | Material error | Contradicting source |
| --- | --- | --- |
| **EASY-04** | `<SourceAddress>` shown with non-existent `<Address>` children and outside `<IPRules>/<MatchRule>`; `mask="32"` cannot produce the stated block of `203.0.113.47` | [access-control-policy](https://cloud.google.com/apigee/docs/api-platform/reference/policies/access-control-policy) |
| **EASY-05** | Ground truth blames `context.request.getValue` (not a documented API); "confirming" experiment `JavaScript.fromCharCode(0)` is not valid JS; `context.variable()` is not documented | [javascript-object-model](https://cloud.google.com/apigee/docs/api-platform/reference/javascript-object-model) |
| **EASY-06** | Says `UnresolvedVariable` occurs only when `IgnoreUnresolvedVariables` is **set**; doc says it can only occur when it is **false**. Uses non-existent `<SourceVariable>` (real name `<Source>`). Case-sensitivity premise for `request.header.*` is undocumented | [basic-authentication-policy](https://cloud.google.com/apigee/docs/api-platform/reference/policies/basic-authentication-policy), [variables-reference](https://cloud.google.com/apigee/docs/api-platform/reference/variables-reference) |
| **EASY-09** | Attributes `steps.jsontoxml.InvalidSourceType` to the client's declared `Content-Type`; doc attributes it to the **type of the `<Source>` flow variable** | [json-xml-policy](https://cloud.google.com/apigee/docs/api-platform/reference/policies/json-xml-policy) |
| **EASY-10** | Uses non-existent `<SecretVariable>` and `<VerificationOutput VariableToVerify>` (real: `<SecretKey>`, `<VerificationValue>`); `<Algorithm>HS256</Algorithm>` is invalid for HMAC and would raise `InvalidValueForElement`; asserts 400 where the page says 401 | [hmac-policy](https://cloud.google.com/apigee/docs/api-platform/reference/policies/hmac-policy) |
| **EASY-12** | `steps.oauth.v2.InvalidEarlyTimestamp` is on **revoke-oauth-v2-policy**, not oauthv2-policy; status is **500**, not 401; cause is "Timestamp cannot be earlier than January 1, 2014", not `nbf` clock skew | [revoke-oauth-v2-policy](https://cloud.google.com/apigee/docs/api-platform/reference/policies/revoke-oauth-v2-policy), [oauthv2-policy](https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy) |
| **MED-03** | `<LoadBalancing>`, `<TargetServer>`, `<Algorithm>ROUND_ROBIN</Algorithm>` and `<MinTimeBetweenFailures>` are all wrong or absent from the docs; cites a page containing neither element it names | [load-balancing-across-backend-servers](https://cloud.google.com/apigee/docs/api-platform/deploy/load-balancing-across-backend-servers) |
| **MED-04** | ResponseCache has no `<Key>` element (it is `<CacheKey>/<KeyFragment>`) and no `expiryInSeconds` (it is `<ExpirySettings>/<TimeoutInSeconds>`); both are the evidence the agent is sent to read | [response-cache-policy](https://cloud.google.com/apigee/docs/api-platform/reference/policies/response-cache-policy), [working-cachekeys](https://cloud.google.com/apigee/docs/api-platform/reference/policies/working-cachekeys) |
| **MED-05** | "Documented single-node cache refresh" is not in the KVM page or any other page checked; origin and evaluation objective both assert it is documented. "Secured map" is not a KVM concept here | [key-value-maps](https://cloud.google.com/apigee/docs/api-platform/cache/key-value-maps) |
| **MED-07** | The claimed documented hybrid-vs-Apigee difference in shared-flow deploy-time validation does not exist in either cited page; the shared-flows page applies to both and states the opposite-leaning rule; contradicts EASY-03 | [shared-flows](https://cloud.google.com/apigee/docs/api-platform/fundamentals/shared-flows), [compare-apigee-products](https://cloud.google.com/apigee/docs/api-platform/get-started/compare-apigee-products) |
| **MED-09** | SpikeArrest has no `rateLimit` or `timeWindow` element (children are `<Identifier> <MessageWeight> <Rate> <UseEffectiveCount>`); title says 429 while the body and the Quota page say `QuotaViolation` = 500 | [spike-arrest-policy](https://cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy), [quota-policy](https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy) |
| **MED-15** | Asserts the **deployment-only** error `JavaClassNotFoundInJavaResource` occurring on the request path, while its own ground truth says deployment succeeded and that code is a deployment error; the scenario is unsatisfiable as written | [java-callout-policy](https://cloud.google.com/apigee/docs/api-platform/reference/policies/java-callout-policy) |

**Twelve material errors.** Five of them (EASY-06, EASY-09, EASY-12, MED-07, MED-15) are the
serious class: a stated ground truth that the documentation contradicts, or a scenario whose
ground truth and evidence contradict each other. Three more (EASY-04, EASY-10, MED-03) supply
XML that cannot produce the fault they describe. The remaining four (EASY-05, MED-04, MED-05,
MED-09) invent API surfaces or mislabel unsourced claims as documented.

### Scenarios I could not fault

**EASY-02, EASY-07, EASY-08, EASY-13, EASY-15, MED-08, MED-12** are correct as written. MED-08
is the strongest: its ground truth is a near-verbatim quote of the EKU paragraph on the page it
cites. EASY-08's "one code, two policies" premise is exactly what the Quota and SpikeArrest
pages show.

### Aggregate fix list

1. Rewrite the fault payload shape in all 30 scenarios to `{"fault":{"detail":{"errorcode":...},"faultstring":...}}` (S1).
2. Replace `context.request.getValue(x)` with `context.getVariable(x)` and `context.variable(k,v)` with `context.setVariable(k,v)` in EASY-05 and MED-13 (S2).
3. Source or drop `AM-Target-Endpoint`, `OAuthV2/VerifyAccessToken`, `SA-Protect`, `SC-Enrich` (S3).
4. Add `messaging.adaptors.http.flow.SslHandshakeFailed` to `.agents/skills/apigee-support-core/references/error-codes.md`, or EASY-14 violates the suite's own stated rule (S4).
5. Reconcile EASY-03 against MED-07 on shared-flow resolution timing; at most one can be "documented", and I could not find documentation for either.
6. Add a documentation-contradiction check to the build scripts. Seven of the twelve material errors here (EASY-06, EASY-09, EASY-12, MED-03, MED-09, MED-15, plus MED-04) would have been caught by grepping each scenario's quoted fault code, status and element names against `research/pages/` — the tooling in this repo already supports it.
