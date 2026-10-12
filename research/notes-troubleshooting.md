# Apigee fault handling, policy errors, and debugging — research notes

Every URL below was checked with `research/fetch.sh` or an equivalent `curl -w "%{http_code}"`
during this session. Anything not listed in "VERIFIED PAGES" was not verified and must not be
cited from this file.

**Read this first: cloud.google.com serves HTTP 200 for paths that do not exist.**
A nonexistent doc path returns `200` with a body reading
`The equivalent page does not exist in Apigee.` A 200 status alone is NOT proof a page exists.
The check that actually works is grepping the response body for that string.
This affects three of the four pages the task brief asked for by name.

---

## 1. VERIFIED PAGES

### Core fault-handling and policy-error pages

| Title | URL | HTTP | bytes |
| --- | --- | --- | --- |
| Handling faults | https://cloud.google.com/apigee/docs/api-platform/fundamentals/fault-handling | 200 | 63471 |
| What you need to know about policy errors | https://cloud.google.com/apigee/docs/api-platform/fundamentals/what-you-need-know-about-policy-errors | 200 | 8728 |
| What are flows | https://cloud.google.com/apigee/docs/api-platform/fundamentals/what-are-flows | 200 | 13581 |
| Flow variables and conditions | https://cloud.google.com/apigee/docs/api-platform/fundamentals/flow-variables-and-conditions | 200 | 41594 |
| Policy error reference | https://cloud.google.com/apigee/docs/api-platform/reference/policies/error-code-reference | 200 | 2312 |
| Policy reference overview | https://cloud.google.com/apigee/docs/api-platform/reference/policies/reference-overview-policy | 200 | 3453 |

### Policy runtime error playbooks (`api-platform/troubleshoot/policies/runtime/*`)

All are HTTP 200 with real content. Bytes as extracted by `fetch.sh`.

| Title | URL | HTTP | bytes |
| --- | --- | --- | --- |
| AssignMessage runtime errors | .../troubleshoot/policies/runtime/assign-message-runtime-errors | 200 | 9368 |
| BasicAuthentication runtime errors | .../runtime/basic-authentication-runtime-errors | 200 | 14616 |
| DecodeJWT runtime errors | .../runtime/decode-JWT-runtime-errors | 200 | 6937 |
| ExtractVariables runtime errors | .../runtime/extract-variables-runtime-errors | 200 | 27456 |
| FlowCallout runtime errors | .../runtime/flowcallout-runtime-errors | 200 | 6961 |
| JavaCallout runtime errors | .../runtime/java-callout-runtime-errors | 200 | 3628 |
| JavaScript runtime errors | .../runtime/javascript-runtime-errors | 200 | 25708 |
| JSONThreatProtection errors | .../runtime/jsonthreatprotection-errors | 200 | 35703 |
| JSONtoXML runtime errors | .../runtime/jsontoxml-runtime-errors | 200 | 33010 |
| KeyValueMap runtime errors | .../runtime/key-value-map-runtime-errors | 200 | 7235 |
| PythonScript runtime errors | .../runtime/python-script-runtime-errors | 200 | 6278 |
| Quota runtime errors | .../runtime/quota-runtime-errors | 200 | 9988 |
| ResetQuota runtime errors | .../runtime/reset-quota-runtime-errors | 200 | 13235 |
| ServiceCallout runtime errors | .../runtime/service-callout-runtime-errors | 200 | 17067 |
| SOAPMessageValidation runtime errors | .../runtime/soap-message-validation-runtime-errors | 200 | 23121 |
| SpikeArrest runtime errors | .../runtime/spike-arrest-runtime-errors | 200 | 9030 |
| XMLThreatProtection runtime errors | .../runtime/xmlthreatprotection-runtime-errors | 200 | 100399 |
| XMLtoJSON runtime errors | .../runtime/xmltoxml-runtime-errors | 200 | 28462 |
| XSLTransform runtime errors | .../runtime/xsl-transform-runtime-errors | 200 | 17254 |

Note the naming inconsistency, which is real and not a typo of mine:
the JSONThreatProtection page is `jsonthreatprotection-errors`, **not**
`jsonthreatprotection-runtime-errors`. The latter is a 200 stub. See section 5.

### Policy deployment error playbooks (`api-platform/troubleshoot/policies/deployment/*`)

All HTTP 200, all real content (23 checked, no stubs).

| Title | URL | HTTP |
| --- | --- | --- |
| AssignMessage | .../deployment/assign-message-deployment-errors | 200 |
| BasicAuthentication | .../deployment/basic-authentication-deployment-errors | 200 |
| DecodeJWT | .../deployment/decode-JWT-deployment-errors | 200 |
| ExtractVariables | .../deployment/extract-variables-deployment-errors | 200 |
| GenerateJWT | .../deployment/generate-JWT-deployment-errors | 200 |
| InvalidateCache | .../deployment/invalidate-cache-deployment-errors | 200 |
| JavaCallout | .../deployment/java-callout-deployment-errors | 200 |
| JavaScript | .../deployment/javascript-deployment-errors | 200 |
| KeyValueMap | .../deployment/key-value-map-deployment-errors | 200 |
| LookupCache | .../deployment/lookup-cache-deployment-errors | 200 |
| MessageLogging | .../deployment/message-logging-deployment-errors | 200 |
| PopulateCache | .../deployment/populate-cache-deployment-errors | 200 |
| PythonScript | .../deployment/python-script-deployment-errors | 200 |
| Quota | .../deployment/quota-deployment-errors | 200 |
| RegularExpressionProtection | .../deployment/regular-expression-protection-deployment-errors | 200 |
| ResetQuota | .../deployment/reset-quota-deployment-errors | 200 |
| ResponseCache | .../deployment/responsecache-deployment-errors | 200 |
| SAMLAssertion | .../deployment/samlassertion-deployment-errors | 200 |
| ServiceCallout | .../deployment/service-callout-deployment-errors | 200 |
| SOAPMessageValidation | .../deployment/soap-message-validation-deployment-errors | 200 |
| SpikeArrest | .../deployment/spike-arrest-deployment-errors | 200 |
| VerifyJWT | .../deployment/verify-JWT-deployment-errors | 200 |
| XMLtoJSON | .../deployment/xmltojson-deployment-errors | 200 |
| XSLTransform | .../deployment/xsl-transform-deployment-errors | 200 |

Index pages: `.../troubleshoot/policies/introduction` (200, 4998 bytes) lists the canonical
playbook set. `.../troubleshoot/playbooks/introduction` (200, 29162 bytes) is the hybrid
infrastructure playbook index, a different thing.

### Debug, trace, and monitoring

| Title | URL | HTTP | bytes |
| --- | --- | --- | --- |
| Debug tool overview | https://cloud.google.com/apigee/docs/api-platform/debug/trace-overview | 200 | 5753 |
| Trace tool | https://cloud.google.com/apigee/docs/api-platform/debug/trace | 200 | 25079 |
| Offline trace | https://cloud.google.com/apigee/docs/api-platform/debug/offline-trace | 200 | 3609 |
| Health check | https://cloud.google.com/apigee/docs/api-platform/debug/health-check | 200 | 11611 |
| Audit logging | https://cloud.google.com/apigee/docs/api-observation/audit-logging | 200 | 13878 |
| **API Monitoring fault codes** | https://cloud.google.com/apigee/docs/api-monitoring/fault-codes | 200 | 19954 |
| Investigate (API Monitoring) | https://cloud.google.com/apigee/docs/api-monitoring/investigate | 200 | 6471 |

### Reference pages

| Title | URL | HTTP | bytes |
| --- | --- | --- | --- |
| Flow variables reference | .../api-platform/reference/variables-reference | 200 | 116345 |
| Conditions reference | .../api-platform/reference/conditions-reference | 200 | 11882 |
| API proxy configuration reference | .../api-platform/reference/api-proxy-configuration-reference | 200 | 69358 |
| Endpoint properties reference | .../api-platform/reference/endpoint-properties-reference | 200 | 19899 |
| Flow configuration reference | .../api-platform/reference/flow-configuration-reference | 200 | 51894 |

### Policy reference pages fetched for error tables (all HTTP 200)

quota-policy (84064), verify-api-key-policy (34333), raise-fault-policy (23597),
spike-arrest-policy (29560), basic-authentication-policy (18891), service-callout-policy,
extract-variables-policy, assign-message-policy, access-control-policy, oauthv2-policy,
javascript-policy, message-logging-policy, invalidate-cache-policy, lookup-cache-policy,
populate-cache-policy, reset-quota-policy, generate-jwt-policy, decode-jwt-policy,
verify-jwt-policy. All under `.../api-platform/reference/policies/`.

---

## 2. CONFIRMED TECHNICAL FACTS

All **documented**. URLs shortened to `.../apigee/docs/`.

### The default fault response shape

> "When a policy throws an error, Apigee immediately enters the error flow and generates an
> error message. This system-generated message is a JSON object that includes two bits of
> information: an `errorcode` and a `faultstring`."

— `.../api-platform/fundamentals/what-you-need-know-about-policy-errors`

Default body example from that page:

```json
{
   "fault":{
      "detail":{
         "errorcode":"steps.extractvariables.SourceMessageNotAvailable"
      },
      "faultstring":"mymessage message is not available for ExtractVariable: ParseJsonResponse"
   }
}
```

### errorcode structure: `[prefix].[error_name]`

> "The `errorcode` consists of a `prefix` and an `error name`, as follows: `[prefix].[error_name]`.
> In the above example `steps.extractvariables` is the prefix and `SourceMessageNotAvailable`
> is the error name."

— `.../fundamentals/what-you-need-know-about-policy-errors`

`fault.name` holds the **error_name only**, not the full errorcode:

> "The variable `fault.name` is the value of the `errorcode` attribute and `error.message` is
> the value of the `faultstring` attribute."
> "When a policy throws an error, the `fault.name` variable is always set to the error name."

— `.../fundamentals/what-you-need-know-about-policy-errors`

### The single most repeated instruction in this doc set

> "**Note:** For error handling, the best practice is to trap the `errorcode` part of the error
> response. Do not rely on the text in the `faultstring`, because it could change."

— present in every policy Error reference section checked. Confirmed in at least 21 policy pages
including quota-policy, verify-api-key-policy, raise-fault-policy, spike-arrest-policy,
basic-authentication-policy, oauthv2-policy, javascript-policy, message-logging-policy,
access-control-policy, extract-variables-policy, assign-message-policy, service-callout-policy,
generate-jwt-policy, decode-jwt-policy, verify-jwt-policy, hmac-policy, decode-jws-policy,
verify-jws-policy, generate-jws-policy, invalidate-cache-policy.

### Exact fault codes WITH their exact HTTP status

From `.../reference/policies/quota-policy`, "### Runtime errors" table:

| Fault code | HTTP status |
| --- | --- |
| `policies.ratelimit.FailedToResolveQuotaIntervalReference` | `500` |
| `policies.ratelimit.FailedToResolveQuotaIntervalTimeUnitReference` | `500` |
| `policies.ratelimit.InvalidMessageWeight` | `500` |
| `policies.ratelimit.QuotaViolation` | `500` |

From `.../reference/policies/spike-arrest-policy`, "### Runtime errors":

| Fault code | HTTP status |
| --- | --- |
| `policies.ratelimit.FailedToResolveSpikeArrestRate` | `500` |
| `policies.ratelimit.InvalidMessageWeight` | `500` |
| `policies.ratelimit.SpikeArrestViolation` | `429` |

Note the asymmetry: a Quota violation is documented as `500` while the equivalent
SpikeArrest violation is `429`. Quota's table says "N/A" in the Fix column for
`policies.ratelimit.QuotaViolation`, i.e. no playbook exists for it.

From `.../reference/policies/verify-api-key-policy`, "### Runtime errors":

| Fault code | HTTP status |
| --- | --- |
| `keymanagement.service.consumer_key_missing_api_product_association` | `400` |
| `keymanagement.service.DeveloperStatusNotActive` | `401` |
| `keymanagement.service.invalid_client-app_not_approved` | `401` |
| `oauth.v2.FailedToResolveAPIKey` | `401` |
| `oauth.v2.InvalidApiKey` | `401` |
| `oauth.v2.InvalidApiKeyForGivenResource` | `401` |

From `.../reference/policies/basic-authentication-policy`:

| Fault code | HTTP status |
| --- | --- |
| `steps.basicauthentication.InvalidBasicAuthenticationSource` | `500` |
| `steps.basicauthentication.UnresolvedVariable` | `500` |

From `.../reference/policies/raise-fault-policy`:

| Fault code | HTTP status |
| --- | --- |
| `steps.raisefault.RaiseFault` | `500` |

RaiseFault's Deployment errors section reads, verbatim: **"None."**

### VerifyAPIKey documented defect

> "Currently, Apigee does not report the `ApiKeyNotApproved` error accurately. Instead, if a key
> is not approved (its status is set to `revoked` or `pending`), you will get the
> `FailedToResolveAPIKey` error instead."

— `.../reference/policies/verify-api-key-policy`

Practical consequence: a revoked key and a missing key are indistinguishable by errorcode.

### An internal inconsistency in the errorcode prefix — worth knowing before you match on it

The fault-handling page shows the default error for a missing API key as:

```json
{"fault":{"faultstring":"Failed to resolve API Key variable request.queryparam.apikey",
"detail":{"errorcode":"steps.oauth.v2.FailedToResolveAPIKey"}}}
```

— `.../fundamentals/fault-handling`

But the VerifyAPIKey policy reference table lists the fault code as `oauth.v2.FailedToResolveAPIKey`
with **no `steps.` prefix**. The same page's own example then matches on
`fault.name = "FailedToResolveAPIKey"`, which is prefix-independent and therefore unaffected.

**Hypothesis (not documented):** the runtime may emit a `steps.`-prefixed form that the
reference table omits. I did not observe this at runtime, so treat the discrepancy as a real
documentation inconsistency and prefer matching `fault.name` or the exact errorcode confirmed
on the failing system, not a prefix guessed from either page.

### Fault variables available in the error flow

From `.../reference/variables-reference`, section `## error`:

| Variable | Type | R/W |
| --- | --- | --- |
| `error` | message | Read/Write |
| `error.content` | String | Read/Write |
| `error.message` | String | Read only — "value is available only before the error Flow is executed" |
| `error.status.code` | Integer | Read only — "The HTTP status code associated with the error. For example, `400`." |
| `error.transport.message` | TransportMessage | Read only |
| `error.state` | Integer | Read only — "State in the Flow where an error occurred." |
| `error.header.<header_name>` | String | Read/Write |

From the same page, section `## fault`:

| Variable | Type | R/W | Note |
| --- | --- | --- | --- |
| `fault.name` | String | Read only | fault name from the policy's Runtime errors table |
| `fault.reason` | String | Read only | reason for the fault |
| `fault.category` | String | Read only | e.g. "Step" |
| `fault.subcategory` | String | Read only | e.g. "OASValidationFailure" |

`fault.category` / `fault.subcategory` map to the Category / Sub-category columns of the
API Monitoring fault codes table, which is how alerts get grouped.

### Proxy exit semantics

> "When an API proxy encounters an error, regardless of how it occurs, it exits the normal flow
> pipeline, enters an error state, and returns an error message to the client app. Once the API
> proxy enters the error state, it cannot return processing back to the normal flow pipeline."

— `.../fundamentals/fault-handling`

FaultRules are evaluated **only** when the proxy is in an error state. `<FaultRules>` is checked
first, then `<DefaultFaultRule>`. The DefaultFaultRule fires when no FaultRules are defined,
when none are executed, or when `<AlwaysEnforce>` is true.

### continueOnError suppresses fault handling entirely

> "if `continueOnError="true"` ... the proxy will *not* go into an error state if that policy
> fails, and the proxy won't look at your FaultRules."

— `.../fundamentals/fault-handling`

### FaultRule evaluation order differs by endpoint

> - **ProxyEndpoint**: Bottom up, last FaultRule in the XML configuration first.
> - **TargetEndpoint**: Top down, first FaultRule in the XML configuration first.

— `.../fundamentals/fault-handling`

FaultRules must be defined in the endpoint where the error occurs; a TargetEndpoint error is not
handled by ProxyEndpoint FaultRules.

### Policy namespaces for the `.failed` flag (do not guess these)

> - RaiseFault policy: `raisefault.failed` (same for all RaiseFault policies)
> - VerifyAPIKey policy: `oauthV2.{policy_name}.failed`
> - Quota policy and SpikeArrest policy: `ratelimit.{policy_name}.failed`

— `.../fundamentals/fault-handling`

And from the policy Error reference sections:

| Policy | `.failed` variable |
| --- | --- |
| Quota | `ratelimit.<policy_name>.failed` |
| SpikeArrest | `ratelimit.<policy_name>.failed` |
| VerifyAPIKey | `oauthV2.<policy_name>.failed` |
| RaiseFault | `raisefault.<policy_name>.failed` |
| BasicAuthentication | `BasicAuthentication.<policy_name>.failed` |

The docs warn the prefix cannot be inferred:

> "How do you know what the fault variable's prefix is? You can't necessarily guess it from the
> contents of the fault string or error code. You have to look it up in the Policy error
> reference or you can use trace to inspect the flow variables that are created when an error
> occurs. For example, for the Extract Variables policy, the `[prefix].[policy_name].failed`
> prefix is `extractvariables` ... But for the Access Control policy, the prefix is `acl`."

— `.../fundamentals/what-you-need-know-about-policy-errors`

### Fault code prefixes are NOT uniform

Confirmed distinct prefixes for the same-shaped concept:

- `policies.` — quota and spike arrest (`policies.ratelimit.*`)
- `steps.` — most mediation/extension policies (`steps.extractvariables.*`, `steps.script.*`, `steps.servicecallout.*`)
- `oauth.` / `keymanagement.service.` — VerifyAPIKey (`oauth.v2.*`, `keymanagement.service.*`)
- `flow.` / `messaging.adaptors.http.flow.` / `messaging.runtime.` / `messaging.config.beans.` — gateway
  (note `flow.execution.ExecutionReturnedFailure` breaks the convention below)
- `protocol.http.` — HTTP protocol violations
- `security.util.` — `security.util.KeyAliasNotFound`
- `scripts.node.` — `scripts.node.ScriptExecutionError`
- `mintstep.` — monetization, `mintstep.undefinedProduct`
- `policies.concurrentratelimit.` — `policies.concurrentratelimit.ConcurrentRatelimitViolation`

**Do not write a matcher that assumes a single prefix shape.**

### Gateway / transport fault codes (API Monitoring table)

From `.../api-monitoring/fault-codes`. Category → Sub-category → Fault Code:

| Category / Sub-category | Name | Fault code |
| --- | --- | --- |
| Gateway / Proxy | APITimedOut | `flow.APITimedOut` |
| Gateway / Proxy | ApplicationNotFound | `messaging.adaptors.http.flow.ApplicationNotFound` |
| Gateway / Proxy | DecompressionFailureAtRequest | `messaging.adaptors.http.flow.DecompressionFailureAtRequest` |
| Gateway / Proxy | DecompressionFailureAtResponse | `messaging.adaptors.http.flow.DecompressionFailureAtResponse` |
| Gateway / Proxy | KeyAliasNotFound | `security.util.KeyAliasNotFound` |
| Gateway / Proxy | RouteToTargetFailed | `messaging.runtime.RouteFailed` |
| Gateway / Proxy | SharedFlowNotFound | `flow.SharedFlowNotFound` |
| Gateway / Proxy | TargetIsMissing | `messaging.runtime.TargetMissing` |
| Gateway / Target | FailedHandshakeWithTargetEndpoint | `messaging.adaptors.http.flow.SslHandshakeFailed` |
| Gateway / Target | TimeoutWithTargetOrCallout | `messaging.adaptors.http.flow.GatewayTimeout` |
| Gateway / Target | TargetOrCalloutEndpointsNotAvailable | `messaging.adaptors.http.flow.ServiceUnavailable` |
| Gateway / Target | TargetServerConfiguredInLoadBalancerIsDown | `messaging.adaptors.http.flow.NoActiveTargets` |
| Gateway / Target | UnexpectedEOFAtTarget | `messaging.adaptors.http.flow.UnexpectedEOFAtTarget` |
| Gateway / Virtual Host | InvalidKeystoreOrTrustStore | `messaging.runtime.SecurityStoreNotConfigured` |
| Gateway / Other | HTTPErrorResponseCode | `messaging.adaptors.http.flow.ErrorResponseCode` |
| Extension / MessageLogging | StepDefinitionExecutionFailed | `steps.messagelogging.StepDefinitionExecutionFailed` |
| Extension / Script | EvaluationFailed | `steps.script.ScriptEvaluationFailed` |
| Extension / Node Script | ExecutionError | `scripts.node.ScriptExecutionError` |
| Mediation / RaiseFault | RaiseFaultException | `steps.raisefault.RaiseFault` |
| Monetization | UndefinedProduct | `mintstep.undefinedProduct` |
| Security / SAMLAssertion | InvalidKeyStore | `steps.saml.generate.InvalidKeyStore` |
| Security / SAMLAssertion | InvalidMediaType | `steps.saml.generate.InvalidMediaTpe` |
| Security / SAMLAssertion | InvalidTrustStore | `steps.saml.validate.InvalidTrustStore` |
| Security / SAMLAssertion | SAMLAssertionForNotBeforeConditionViolated | `steps.saml.validate.NotBeforeConditionViolated` |
| Security / SAMLAssertion | SignatureValidationFailed | `steps.saml.validate.SignatureValidationFailed` |
| Security / SAMLAssertion | XPathResolutionFailed | `steps.saml.validate.XPathResolutionFailed` |
| Sense | RaiseFault | `messaging.runtime.SenseRaiseFault` |
| Traffic Mgmt / Caching | InvalidExpiryDatForCacheEntry | `messaging.config.beans.InvalidExpiryDateForCacheEntry` |
| Traffic Mgmt / ConcurrentRateLimit | ConcurrentRateLimitViolation | `policies.concurrentratelimit.ConcurrentRatelimitViolation` |

Note the spelling discrepancies **in the docs themselves**: `InvalidMediaTpe` (sic) for
InvalidMediaType, and `InvalidExpiryDatForCacheEntry` as the display name against a fault code
spelled `...InvalidExpiryDateForCacheEntry`. Match the fault code, not the display name.

Other notable entries on that page: `protocol.http.TooBigBody`, `protocol.http.TooBigHeaders`,
`protocol.http.BadPath`, `protocol.http.InvalidPath`, `protocol.http.Response306Reserved`,
`protocol.http.EmptyPath`, `protocol.http.Response405WithoutAllowHeader`,
`protocol.http.ResponseWithBody`, `protocol.http.ProxyTunnelCreationFailed`,
`protocol.http.UnsupportedEncoding`, `protocol.http.DuplicateHeader`,
`protocol.http.EmptyHeaderName`, `protocol.http.HeaderNameWithNonAsciiChar`,
`protocol.http.HeaderWithInvalidChar`, `messaging.adaptors.http.flow.LengthRequired`.

That page also states:

> "When setting up alerts, fault codes are organized by category and subcategory, and display the
> human-readable name. When using the Investigate dashboard, the raw fault codes are displayed."

### Fault taxonomy (four top-level categories)

From `.../fundamentals/fault-handling`, section "Fault taxonomy":

- **Messaging** — Custom faults `{fault_name}`; Response codes `InternalServerError`, `NotFound`; Routing failures `NoRoutesMatched`; Classification failures `NotFound`
- **Transport** — Connectivity `ConnectionRefused`, `ConnectionReset`, `ConnectionTimeout`; Request/Response validations `ContentLengthMissing`, `HostHeaderMissing`; IO errors `SSLHandshakeError`, `ReadTimeout`, `ReadError`, `WriteTimeout`, `WriteError`, `ChunkError`
- **System** — Memory `OutOfMemory`, `GCOverLimit`; Thread `RogueTaskTerminated`
- **Policy** — "Faults for each policy type are defined in the Policy reference."

### 504 and timeout mechanics

From `.../reference/endpoint-properties-reference`, "Setting io.timeout.millis and api.timeout":

> 1. The Ingress (aka Internal Load Balancer) sends its timeout value to the Message Processor.
>    This timeout value defaults to 300 seconds and is **not configurable**.
> 2. ... If `api.timeout` is **not** set at the proxy level, use the timeout set by the Ingress.
>    If set, use the **lesser** of the Ingress timeout or the value of `api.timeout`.
> 3. `api.timeout` specifies the maximum time an API proxy has to execute from request to response.
>    ... If the value is less than zero ... the Message Processor returns a `504 Gateway Timeout`.
> 4. `io.timeout.millis` specifies the maximum time the target endpoint has to respond.
>    Before connecting, the Message Processor determines the lesser of
>    (`api.timeout` - elapsed) and `io.timeout.millis`.

So a `504` can be produced by the proxy-level budget, not only by the target. Both
`connect.timeout.millis` and `io.timeout.millis` are real TargetEndpoint transport property
names. Separately, the spike-arrest deployment playbook notes that when `<LoadBalancer>` is
configured and `<RetryEnabled>` is true, Apigee retries the connection up to three times,
which extends total latency.

### Condition operators (exact names)

From `.../reference/conditions-reference`, the `## Operators` table maps symbols to names:

| Symbol | Name | Notes |
| --- | --- | --- |
| `!=` | `NotEquals`, `IsNot` | not equals, case sensitive |
| `>` | `GreaterThan` | |
| `>=` | `GreaterThanOrEquals` | |
| `<` | `LesserThan` | "The Apigee UI does not support the literal `<`" |
| `<=` | `LesserThanOrEquals` | same UI limitation |
| `~~` | `JavaRegex` | `javax.util.regex`, case sensitive |
| `~` | `Matches`, `Like` | glob-style `*` wildcard, case sensitive |
| `~/` | `MatchesPath`, `LikePath` | path expression |
| `=\|` | `StartsWith` | |

Also documented in fault-handling: if you use `<` or `>` and get "bad XML" validation
failures, use the word forms `LesserThan` / `GreaterThan`. `MatchesPath` appears in the
conditions page's own examples, e.g. `<Condition>request.path MatchesPath "/statuses/**"</Condition>`.

### Runtime fault codes observed across the playbook set

Collected from the `"errorcode"` fields in the fetched runtime playbooks. These are the codes
the playbooks actually diagnose:

```
policies.ratelimit.FailedToResolveQuotaIntervalReference
policies.ratelimit.FailedToResolveQuotaIntervalTimeUnitReference
policies.ratelimit.FailedToResolveSpikeArrestRate
policies.ratelimit.InvalidMessageWeight
steps.assignmessage.UnresolvedVariable
steps.assignmessage.VariableOfNonMsgType
steps.basicauthentication.InvalidBasicAuthenticationSource
steps.basicauthentication.UnresolvedVariable
steps.extractvariables.ExecutionFailed
steps.extractvariables.InvalidJSONPath
steps.extractvariables.JsonPathParsingFailure
steps.extractvariables.SetVariableFailed
steps.extractvariables.SourceMessageNotAvailable
steps.extractvariables.UnableToCast
steps.javascript.ScriptExecutionFailed
steps.jwt.FailedToDecode
steps.jwt.InvalidToken
steps.script.ScriptEvaluationFailed
steps.servicecallout.ExecutionFailed
steps.servicecallout.RequestVariableNotMessageType
steps.servicecallout.RequestVariableNotRequestMessageType
flow.execution.ExecutionReturnedFailure   (JavaCallout playbook — see mismatch note below)
```

### A second documentation mismatch: JavaCallout's own code disagrees with itself

The JavaCallout runtime playbook heads its section `ExecutionError` and declares the error code as
`steps.javacallout.ExecutionError`, then shows the response body carrying a completely different
errorcode:

```json
{
  "fault": {
    "faultstring": "Execution returned an error result",
    "detail": {
      "errorcode": "flow.execution.ExecutionReturnedFailure"
    }
  }
}
```

— `.../troubleshoot/policies/runtime/java-callout-runtime-errors`

Cause per that page: "This error occurs if Java code throws an exception or returns *null* during
the execution of a JavaCallout policy."

If you are writing a matcher, the JSON body is what the runtime actually sends; the heading is a
label. Confirm against the JavaCallout policy's own Runtime errors table before committing to
either string.

### Two policy pages in this project disagree about one same-named error

`policies.ratelimit.InvalidMessageWeight` appears in both the Quota runtime playbook and the
SpikeArrest runtime playbook, with byte-identical wording ("Invalid message weight value
[invalid_value]") and identical cause text about a non-integer `<MessageWeight>`. The Quota
playbook diagnoses it via `<MessageWeight ref="message_weight"/>` in a `<Quota>` policy; the
SpikeArrest playbook diagnoses the same code in a `<SpikeArrest>` policy. Since the prefix is
`policies.ratelimit` for both, **the errorcode alone cannot tell you which policy raised it.**
Confirm from trace which policy step failed.

### Documentation defect found on the SpikeArrest runtime playbook

`.../runtime/spike-arrest-runtime-errors` renders its first code block as:

```json
{
    "fault": {jdoe
        "faultstring": "Invalid message weight value [invalid_value]",
```

There is a stray `{jdoe` after `"fault":`. It is in the served page, not in my extraction.
Do not copy that block verbatim into an example; the Quota playbook has the same block clean.

---

## 3. RUNTIME VS DEPLOYMENT ERROR DISTINCTION

### How the docs define each

The structural distinction is carried by the **column headers**, which are identical across every
policy Error reference section:

**Runtime errors** — the section header reads:

> "These errors can occur when the policy executes."

Table columns: `Fault code` | `HTTP status` | `Cause` | (`Fix`)

The presence of a **dotted fault code** and an **HTTP status** is the marker. A runtime error
reaches the client as an HTTP response body carrying `errorcode`.

**Deployment errors** — the section header reads:

> "These errors can occur when you deploy a proxy containing this policy."

Table columns: `Error name` | `Cause` | (`Fix`)

Note there is **no HTTP status column** and the values are **bare error names, not dotted fault
codes**. That is the structural tell: a deployment error is an `Error name`, a runtime error is
a `[prefix].[error_name]` fault code.

The troubleshooting playbooks then split the *symptom*:

- Runtime playbook sections are headed `### Error code` followed by `### Error response body`
  containing a JSON `{"fault": {...}}` object.
- Deployment playbook sections are headed `### Error message` followed by plain text of the form:

```
Error Saving Revision [revision_number]
Invalid spike arrest rate [invalid_rate].
```

— `.../troubleshoot/policies/deployment/spike-arrest-deployment-errors`

That "Error Saving Revision N" banner is the deployment-failure signature.

### Examples from five policies

**Quota.** Same element, two different failure modes, depending on where the bad value sits.
This is the cleanest illustration in the whole doc set.

Runtime (`policies.ratelimit.FailedToResolveQuotaIntervalReference`, HTTP `500`):
> "Occurs if the `<Interval>` element is not defined within the `Quota` policy."

Deployment (`InvalidQuotaInterval`):
> "If the quota interval specified in the `<Interval>` element is **not an integer**, then the
> deployment of the API proxy fails. For example, if the quota interval specified is 0.1..."

So a *missing* `<Interval>` is a 500 at runtime; a *non-integer* `<Interval>` is rejected at
deploy. Same policy, same element, different failure modes. The full deployment error names for
Quota are `InvalidQuotaInterval`, `InvalidQuotaTimeUnit`, `InvalidQuotaType`, `InvalidStartTime`,
`StartTimeNotSupported`, `InvalidSynchronizeIntervalForAsyncConfiguration`,
`InvalidAsynchronizeConfigurationForSynchronousQuota`.
— `.../reference/policies/quota-policy`

**SpikeArrest.** Runtime `policies.ratelimit.SpikeArrestViolation` = `429`; runtime
`policies.ratelimit.FailedToResolveSpikeArrestRate` = `500`. The single deployment error is
`InvalidAllowedRate`:
> "If the spike arrest rate specified in the `<Rate>` element ... is not an integer or if the rate
> does not have `ps` or `pm` as a suffix, then the deployment of the API proxy fails."

— `.../reference/policies/spike-arrest-policy` and `.../deployment/spike-arrest-deployment-errors`

**BasicAuthentication.** Runtime: `steps.basicauthentication.InvalidBasicAuthenticationSource`
(500) and `steps.basicauthentication.UnresolvedVariable` (500). Deployment: four bare error names
`UserNameRequired`, `PasswordRequired`, `AssignToRequired`, `SourceRequired`, each of the form
"The `<X>` element must be present for the named operation."
— `.../reference/policies/basic-authentication-policy`

**VerifyAPIKey.** Six runtime fault codes, four of which are `401`. Exactly **one** deployment
error: `SpecifyValueOrRefApiKey` — "The `<APIKey>` element does not have a value or key specified."
This is the clearest case of a policy with a substantial runtime error surface and a trivial
deploy-time error surface.
— `.../reference/policies/verify-api-key-policy`

**RaiseFault.** The degenerate case that proves the split:
> ### Deployment errors
> None.

Its only runtime error is `steps.raisefault.RaiseFault` = `500`.
— `.../reference/policies/raise-fault-policy`

### Operational consequences, stated plainly

- A deployment error means **the revision was rejected**. Per the fault taxonomy and the
  ordering of `<FaultRules>` evaluation, the previously deployed revision keeps serving. Nothing
  ever reached the runtime, so there is no trace and no `errorcode` to read.
- A runtime error means **the revision deployed and then failed while serving a request**. The
  evidence is the `errorcode` in the response body and the API Monitoring trace.
- The two never appear together for the same revision. If someone reports "requests are failing",
  it is a runtime error. If someone reports "I can't deploy", it is a deployment error.
- RaiseFault's "Deployment errors: None" also means a RaiseFault-based fault rule cannot be the
  cause of a failed deployment.

**Unverified:** the claim that a rejected deployment leaves the prior revision serving is
consistent with the docs' fault taxonomy and with standard Apigee behaviour, but I did not find
it stated in this exact sentence on a page I fetched. Treat the strong form of that claim as
**hypothesis**; the operational advice (check deployment errors vs `errorcode`) does not depend
on it.

---

## 4. FAULT VARIABLE PATTERNS

### The three documented patterns

From `.../fundamentals/what-you-need-know-about-policy-errors` and each policy's
`### Fault variables` table:

**1. `fault.name`** — the error name portion only.

| Variable | Where | Example |
| --- | --- | --- |
| `fault.name="<fault_name>"` | "`fault_name` is the name of the fault, as listed in the Runtime errors table above. The fault name is the last part of the fault code." | `fault.name Matches "QuotaViolation"` |

Always set when a policy throws an error. Prefix-independent, which makes it the safest thing to
match on despite the `steps.` inconsistency noted in section 2.

**2. `<policy_namespace>.<policy_name>.failed`** — a boolean per policy instance.

| Variable | Where | Example |
| --- | --- | --- |
| `ratelimit.<policy_name>.failed` | "`policy_name` is the user-specified name of the policy that threw the fault." | `ratelimit.QT-QuotaPolicy.failed = true` |

Confirmed namespaces: `ratelimit` (Quota, SpikeArrest), `oauthV2` (VerifyAPIKey),
`raisefault` (RaiseFault), `BasicAuthentication` (BasicAuthentication), `extractvariables`
(ExtractVariables), `acl` (AccessControl, per the fault-handling page's warning).

`policy_name` is the policy's `name` **attribute**, not the DisplayName:

> "The *name* of the policy you are checking. This is the value of the policy's name attribute,
> not the display name."

**3. `error.*`** — only in the error flow, contextual like `message`:

| Variable | Type | R/W |
| --- | --- | --- |
| `error` | message | Read/Write |
| `error.content` | String | Read/Write |
| `error.message` | String | Read only, **only before the error Flow executes** |
| `error.status.code` | Integer | Read only |
| `error.state` | Integer | Read only |
| `error.header.<header_name>` | String | Read/Write |

### Worked fault rule from the docs

```xml
<FaultRule name="invalid_key_rule">
    <Step>
        <Name>invalid-key-message</Name>
        <Condition>oauthV2.Verify-API-Key-1.failed = true</Condition>
    </Step>
    <Condition>fault.name = "FailedToResolveAPIKey"</Condition>
</FaultRule>
```
— `.../fundamentals/fault-handling`

The Step-level condition uses the `.failed` flag; the outer rule condition uses `fault.name`.
Combining them is the documented idiom for scoping a rule to one specific policy instance.

### Constraint on what is readable in an error state

> "When an API proxy goes into an error state, the only available variables for use in conditions
> are: The variables of the policy that failed. The HTTP message variables that exist at the point
> of failure."

— `.../fundamentals/fault-handling`

Named example: on a Quota failure you can read `ratelimit.<quota_policy_name>.exceed.count`.

### RaiseFault's `<Name>` writes into these variables

The RaiseFault reference shows that when you omit an element, the policy's `name` attribute
supplies the value, and gives example output:

```json
{"fault":{"faultstring":"Raising fault. Fault name : Raise-Fault-1","detail":{"errorcode":"errorCode"}}}
```

— `.../reference/policies/raise-fault-policy`

Note this example's `errorcode` is the literal placeholder `errorCode`, illustrating that
RaiseFault lets you supply your own errorcode. **Hypothesis:** a RaiseFault-derived `fault.name`
equals the `<Name>` element's value. The page's own note says `fault.name = "RaiseFault"` in its
Fault variables example, which contradicts that reading. I did not verify RaiseFault's `fault.name`
behaviour at runtime; do not rely on it without checking trace.

### RaiseFault vs FaultRule precedence

- FaultRule response data wins; RaiseFault data is used only for fields the FaultRule did not set.
- Headers from both are included; duplicate header names produce a multi-valued header.
- If `<DefaultFaultRule>` has `<AlwaysEnforce>true</AlwaysEnforce>`, it runs even when another
  FaultRule already ran, and because it is last its payload wins.

— `.../fundamentals/fault-handling`

---

## 5. 404 / NOT FOUND

### Hard 404s

| URL under `https://cloud.google.com/apigee/docs/` | Status |
| --- | --- |
| `api-platform/debug/debug-runtime-errors` | 404 |
| `api-platform/debug/api-proxy-debugging` | 404 |
| `api-platform/debug/trace-faq` | 404 |
| `api-platform/debug/install-create-overrides` | 404 |
| `api-platform/monitoring/fault-codes` | 404 |
| `api-monitoring/debug` | 404 |
| `api-platform/reference/policies/reference-overview` | 404 (real page is `reference-overview-policy`) |
| `api-platform/reference/policies/endpoint-properties-reference` | 404 (real page is `api-platform/reference/endpoint-properties-reference`) |
| `api-platform/troubleshoot/policies/deployment/stats-collector-deployment-errors` | `404(soft)` — HTTP 200 but a stub body. **Listed in the official intro index at `.../troubleshoot/policies/introduction` but the page does not exist.** Broken link in Google's own docs. |
| `api-platform/monitoring` | 404 — the whole section is absent, confirming `api-monitoring/*` is the real location |

### The dangerous category: HTTP 200 with no content

These return **200** and serve only "The equivalent page does not exist in Apigee."
Treating a 200 as proof of existence would put all of these into a citation.

| URL | Why you would guess it |
| --- | --- |
| `api-platform/troubleshoot/runtime-errors` | named in the task brief as a required page |
| `api-platform/troubleshoot/troubleshooting-landing` | named in the task brief as a required page |
| `api-platform/troubleshoot/support-d` | the canonical URL that `troubleshooting-landing` actually redirects to |
| `api-platform/troubleshoot/policies/runtime/raise-fault-runtime-errors` | pattern-completed from the existing runtime pages |
| `api-platform/troubleshoot/policies/runtime/verify-api-key-runtime-errors` | same |
| `api-platform/troubleshoot/policies/runtime/oauth-v2-runtime-errors` | same |
| `api-platform/troubleshoot/policies/runtime/message-logging-runtime-errors` | same |
| `api-platform/troubleshoot/policies/deployment/raise-fault-deployment-errors` | same |
| `api-platform/troubleshoot/policies/runtime/jsonthreatprotection-runtime-errors` | same; the real page drops `-runtime` entirely |
| `api-platform/troubleshoot/policies/deployment/stats-collector-deployment-errors` | copied from the intro index link; the link itself is broken upstream |

The `jsonthreatprotection` case is the instructive one: the pattern
`.../runtime/<policy>-runtime-errors` holds for 17 of 20 runtime pages and fails for the
others. Never infer a sibling URL by string substitution.

### Two defects in this project's own tooling, found while working

1. **`fetch.sh` stub detection did not match.** The guard grepped the raw HTML for
   `The equivalent page does not exist in the selected`; the site actually serves
   `The equivalent page does not exist in Apigee.` Every stub above passed through as if it were
   real content. The current version of the script reports `404(soft)` and gets this right, but
   any page fetched before that fix should be re-verified by grepping the body.
2. **`fetch.sh` was edited by another agent mid-run** and changed both its stub handling and its
   HTML extraction (pandoc 3.8 was silently truncating large pages after the first table; the
   fix trims to `<div class="devsite-article-body">` before converting). My first-pass byte
   counts for large pages were taken with the old extractor and are unreliable. I re-fetched the
   core pages after the change; the byte counts in section 1 are post-fix.
3. Transient: two fetches returned 200 with a 0-byte extraction before the script was replaced.
   Both succeeded on retry. Treat a 0-byte result as retry, not as a nonexistent page.

### Unverified / not attempted

- I did not find and could not verify any page under `api-platform/monitoring/*`. That section
  appears not to exist as such; monitoring lives at `api-monitoring/*` and
  `api-observation/*`. Do not cite `api-platform/monitoring/`.
- The API Monitoring fault codes table has no HTTP status column. Fault code to HTTP status for
  gateway categories is **not documented in this doc set** — it must come from the policy tables
  or from observation.
- I did not verify the Edges/Deployments management-API pages for deployment error response
  shapes.