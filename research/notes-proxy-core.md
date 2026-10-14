# notes-proxy-core.md

Research notes for the Apigee engineering support skill.
Scope: core proxy mechanics. Every URL below was fetched with `xfetch.sh` and
recorded a real HTTP status. Nothing here is cited from memory.

---

## TOOLING FINDING (read this before trusting any other research file)

**The original `fetch.sh` silently truncates pages.** Google doc HTML contains
unbalanced markup. Verified on `assign-message-policy`: in one region `<table>`
is opened twice and closed once, `<tbody>` opened twice and closed once.
`pandoc -f html` hits the malformed region and **drops everything after it,
with no error and no warning**. Observed result: HTTP 200, a plausible-looking
10,897-byte Markdown file, containing only the first ~30% of the page — no
element tables, no restrictions, no `## Error reference`.

Measured loss on one page: **10,897 bytes -> 170,439 bytes** after fixing the
extractor (15.6x).

A second, independent defect in my first extractor: dropping `<aside>` tags
silently deletes load-bearing content. On `assign-message-policy`, the
`<Path>` (child of `<Set>`) section has **no body text outside its `<aside>`**,
and that aside is the only place the docs explain rewriting the target URL.

Replacement scripts written for this task:

- `research/extract.py` — parses with lxml (auto-closes malformed tags per
  HTML5 rules), isolates `<div class="devsite-article-body">`, keeps `<aside>`,
  re-serialises well-formed HTML, then hands that to pandoc so element tables
  still become Markdown tables. Asserts heading count is preserved.
- `research/xfetch.sh` — fetch + extract, prints
  `STATUS / BYTES / HTML_HEADINGS / MD_HEADINGS / URL`, exits non-zero if
  headings were lost.
- `research/xbatch.sh` — parallel driver.

**Third caveat: HTTP 200 does not mean the page exists.**
`api-platform/troubleshoot/policies/runtime/responsecache-runtime-errors`
returns **HTTP 200** and its entire body is:

> ## The equivalent page does not exist in Apigee

So a status check alone is insufficient. Gate citations on extracted content,
not on status.

---

## 1. VERIFIED PAGES

Title | URL | HTTP | bytes
--- | --- | --- | ---
AssignMessage policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/assign-message-policy> | 200 | 170439
CORS policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/cors-policy> | 200 | 33613
ExtractVariables policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/extract-variables-policy> | 200 | 62289
FlowCallout policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/flow-callout-policy> | 200 | 17939
InvalidateCache policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/invalidate-cache-policy> | 200 | 19586
JavaScript policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/javascript-policy> | 200 | 27103
KeyValueMapOperations policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/key-value-map-operations-policy> | 200 | 45154
LookupCache policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/lookup-cache-policy> | 200 | 17590
MessageLogging policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/message-logging-policy> | 200 | 34905
PopulateCache policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/populate-cache-policy> | 200 | 21699
Quota policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy> | 200 | 84253
Policy reference overview | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/reference-overview-policy> | 200 | 13991
ResponseCache policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/response-cache-policy> | 200 | 34252
ServiceCallout policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/service-callout-policy> | 200 | 60542
SpikeArrest policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy> | 200 | 32895
Working with cache keys | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/working-cachekeys> | 200 | 10151
API proxy configuration reference | <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference> | 200 | 69564
Conditions reference | <https://cloud.google.com/apigee/docs/api-platform/reference/conditions-reference> | 200 | 13025
Endpoint properties reference | <https://cloud.google.com/apigee/docs/api-platform/reference/endpoint-properties-reference> | 200 | 25195
Flow configuration reference | <https://cloud.google.com/apigee/docs/api-platform/reference/flow-configuration-reference> | 200 | 52095
JavaScript object model | <https://cloud.google.com/apigee/docs/api-platform/reference/javascript-object-model> | 200 | 57837
Limits | <https://cloud.google.com/apigee/docs/api-platform/reference/limits> | 200 | 33738
Variables reference | <https://cloud.google.com/apigee/docs/api-platform/reference/variables-reference> | 200 | 116542
Policy error reference | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/error-code-reference> | 200 | 1759
RaiseFault policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/raise-fault-policy> | 200 | 23787
Cache internals | <https://cloud.google.com/apigee/docs/api-platform/cache/cache-internals> | 200 | 7705
HTTP response caching | <https://cloud.google.com/apigee/docs/api-platform/cache/http-response-caching> | 200 | 15790
Using key value maps | <https://cloud.google.com/apigee/docs/api-platform/cache/key-value-maps> | 200 | 15119
Load balancing across backend servers | <https://cloud.google.com/apigee/docs/api-platform/deploy/load-balancing-across-backend-servers> | 200 | 36319
Comparing rate-limiting policies | <https://cloud.google.com/apigee/docs/api-platform/develop/comparing-quota-and-spike-arrest-policies> | 200 | 9523
Resource files | <https://cloud.google.com/apigee/docs/api-platform/develop/resource-files> | 200 | 27685
Environments overview | <https://cloud.google.com/apigee/docs/api-platform/fundamentals/environments-overview> | 200 | 22674
Flow hooks | <https://cloud.google.com/apigee/docs/api-platform/fundamentals/flow-hooks> | 200 | 7107
Flow variables and conditions | <https://cloud.google.com/apigee/docs/api-platform/fundamentals/flow-variables-and-conditions> | 200 | 43383
Shared flows | <https://cloud.google.com/apigee/docs/api-platform/fundamentals/shared-flows> | 200 | 15428
What you need to know about policy errors | <https://cloud.google.com/apigee/docs/api-platform/fundamentals/what-you-need-know-about-policy-errors> | 200 | 8942
Handling faults | <https://cloud.google.com/apigee/docs/api-platform/fundamentals/fault-handling> | 200 | 63659
Controlling API proxies with flows | <https://cloud.google.com/apigee/docs/api-platform/fundamentals/what-are-flows> | 200 | 13788
Understanding APIs and API proxies | <https://cloud.google.com/apigee/docs/api-platform/fundamentals/understanding-apis-and-api-proxies> | 200 | 7914
Deploy error: AssignMessage | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/deployment/assign-message-deployment-errors> | 200 | 7891
Deploy error: KVM | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/deployment/key-value-map-deployment-errors> | 200 | 10710
Deploy error: Quota | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/deployment/quota-deployment-errors> | 200 | 23397
Deploy error: ResponseCache | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/deployment/responsecache-deployment-errors> | 200 | 19295
Deploy error: SpikeArrest | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/deployment/spike-arrest-deployment-errors> | 200 | (status only)
Runtime error: AssignMessage | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/runtime/assign-message-runtime-errors> | 200 | 9585
Runtime error: JavaScript | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/runtime/javascript-runtime-errors> | 200 | 25928
Runtime error: KVM | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/runtime/key-value-map-runtime-errors> | 200 | 7462
Runtime error: Quota | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/runtime/quota-runtime-errors> | 200 | 10196
Runtime error: ServiceCallout | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/runtime/service-callout-runtime-errors> | 200 | 17284
Runtime error: ResponseCache **(stub page — see tooling finding)** | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/runtime/responsecache-runtime-errors> | 200 | 1371

---

## 2. CONFIRMED TECHNICAL FACTS

### 2.1 Proxy structure, flows, the Condition element

S = <https://cloud.google.com/apigee/docs/api-platform/fundamentals/what-are-flows>
C = <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>
R = <https://cloud.google.com/apigee/docs/api-platform/reference/conditions-reference>

- A processing pipeline "consists of a request flow and a response flow. Each
  request flow and response flow is subdivided into a PreFlow, one or more
  optional *conditional* or *named* flows, and a PostFlow." (C)
- PreFlow "Always executes. Executes before any conditional Flows."
  PostFlow "Always executes. Executes after any conditional Flows." (C)
- Execution order, request pipeline (C):
  1\. Proxy Request PreFlow, 2. Proxy Request Conditional Flows (opt),
  3\. Proxy Request PostFlow, 4. Target Request PreFlow,
  5\. Target Request Conditional Flows (opt), 6. Target Request PostFlow.
- Execution order, response pipeline (C):
  1\. Target Response PreFlow, 2. Target Response Conditional Flows (opt),
  3\. Target Response PostFlow, 4. Proxy Response PreFlow,
  5\. Proxy Response Conditional Flows (opt), 6. Proxy Response PostFlow,
  7\. PostClientFlow Response (opt).
- Flow support differs by endpoint (S):
  ProxyEndpoint supports "PreFlow, conditional flows, PostFlow, PostClientFlow";
  TargetEndpoint supports "PreFlow, conditional flows, PostFlow".
- `PostClientFlow` runs after the response returns to the client. "**Only the
  MessageLogging policy can be attached to this flow.**" (C)
- "the ordering of PreFlow and PostFlow elements is not important — the API
  proxy will always execute each at the appropriate point in the pipeline,
  regardless of where they appear in the Endpoint configuration." (C)
- "Only one conditional flow is executed per segment — the first flow whose
  condition evaluates to true." (S) Applies separately to each of the four
  endpoint/direction segments.
- "Proxy endpoints and target endpoints support an unlimited number of
  conditional flows (also known as *named flows*)." (C)
- `<Flow>` child elements: `Name` (required), `Condition` (required for
  non-PreFlow/PostFlow), `Request`, `Response`. (C)
- A single flow **without** a `Condition` placed at the end of a flow sequence
  "will act as the 'Else' statement at the end of the sequence of flows." (C)
- `<Condition>` grammar: `<Condition>variable.name operator "value"</Condition>` (R)
- Conditions may be used for three things (R): policy execution (on `<Step>`),
  flow execution (on `<Flow>`), and **target endpoint route selection**
  (on `<RouteRule>`).
- Only *named* flows can be conditional: "Preflows and postflows (both request
  and response) on `ProxyEndpoints` and `TargetEndpoints` execute for every
  transaction." (R)
- Operators (R). Symbol and word forms are interchangeable:
  `!` (`Not`/`not`), `=` (`Equals`/`Is`), `!=` (`NotEquals`/`IsNot`),
  `:=` (`EqualsCaseInsensitive`), `>` (`GreaterThan`), `>=`
  (`GreaterThanOrEquals`), `<` (`LesserThan`), `<=` (`LesserThanOrEquals`),
  `&&` (`And`/`and`), `||` (`Or`), `()` group, `~~` (`JavaRegex`),
  `~` (`Matches`/`Like`), `~/` (`MatchesPath`/`LikePath`), `=|` (`StartsWith`).
- Operator restrictions (R): "Arithmetic operators (`+ * - / %`) are not
  supported." A space is required before and after an operator. Java operator
  precedence applies. Regular expressions follow `java.util.regex`.
- Literals: `null`, `true`, `false`. e.g. `flow.cachehit is true`. (R)
- Path expressions (R): `*` = one path element, `**` = multiple levels,
  `{name}` = one path element. "`%` is treated as an escape character. The
  pattern `%{user%}` matches `{user}` but not `user`."
- `Matches` does **not** do regex; use `~~`/`JavaRegex` for that.
  (flow-variables-and-conditions)
- JavaRegex tests the **entire** subject string, via
  `java.util.regex.Pattern.matches(str)` — not a partial match as in Perl or
  mod_rewrite. (flow-variables-and-conditions)
- `proxy.pathsuffix` "is a string that always starts with a slash (`/`)
  character". (flow-variables-and-conditions)
- Policy attachment: `<Step><Name>MyPolicy</Name></Step>`. "Policies are
  enforced in the order in which they are attached to a Flow." (C)
- Policy names are restricted to `A-Za-z0-9._\- $ %`. (C)
- Policy attributes (C): `name` (required), `enabled` (default `true`),
  `continueOnError` (default `false`), `async` (default `false`).
  `enabled="false"` turns the policy off even while attached.

### 2.2 Routing, proxy vs target endpoint, target servers, load balancing

C as above.
LB = <https://cloud.google.com/apigee/docs/api-platform/deploy/load-balancing-across-backend-servers>
EP = <https://cloud.google.com/apigee/docs/api-platform/reference/endpoint-properties-reference>

- A target endpoint is "the outbound equivalent of a proxy endpoint"; it acts
  as the client to the backend service. (C)
- `BasePath` (child of `HTTPProxyConnection`) default `/`; "BasePath must be
  unique within an environment." (C)
- A `RouteRule` has `Name` (required), optional `Condition`, and then either
  `TargetEndpoint` (named target under `/apiproxy/targets`) **or** `URL`
  (direct call, "bypassing any TargetEndpoint configurations"). (C)
- Null route: `<RouteRule name="GoNowhere"/>` — a RouteRule with neither
  `TargetEndpoint` nor `URL` does not forward to a target. (C)
- TargetEndpoint connects via exactly one of `HTTPTargetConnection` (HTTP/HTTPS)
  or `LocalTargetConnection` (local proxy chaining). "Configure only one of
  these in a target endpoint." (C)
- `HTTPTargetConnection` child elements: `URL`, `LoadBalancer`, `Properties`,
  `SSLInfo`, `Authentication`. (C)
- **TargetServer is referenced by name through `<Server name="...">` inside
  `<LoadBalancer>`.** I searched for a `<Target>` element across
  api-proxy-configuration-reference, load-balancing-across-backend-servers and
  endpoint-properties-reference: **zero occurrences.** `<Target>` is not a
  documented element in the current Apigee docs. (C, LB, EP)
- A named target server "consists of a name, a host, a protocol, and a port,
  with an additional element to indicate whether the target server is enabled or
  disabled", plus optional `<SSLInfo>`. (LB)
- Target servers are environment-scoped; managed at
  `organizations/{org}/environments/{env}/targetservers`. (LB)
- `<LoadBalancer>` algorithms: `RoundRobin` (default), `Weighted`,
  `LeastConnections`. (LB)
- `Weighted` "requires you to set a `weight` attribute for each target server";
  the element form shown is `<Server name="target1"><Weight>1</Weight></Server>`.
  (LB)
- `<Path>` inside `HTTPTargetConnection` "forms the basepath of the target
  endpoint URI for all target servers. It is only used when `<LoadBalancer>` is
  used. Otherwise, it is ignored." (LB)
- `<MaxFailures>`: "**The MaxFailures default is 0.** This means that Apigee
  always tries to connect to the target for each request and never removes the
  target server from the rotation." (LB)
- "A response failure means Apigee doesn't receive any response from a target
  server." An HTTP error response such as 404 or 500 **resets** the counter
  unless matched by `<ServerUnhealthyResponse><ResponseCode>`. (LB)
- `<RetryEnabled>` defaults to `true`. (LB)
- `<IsFallback>true</IsFallback>` — "One (and only one) target server can be
  set as the *fallback* server." It is not used until all others are out of
  rotation. (LB)
- "the running failure count for each target server is maintained on a
  **per-load-balancer basis**" — two target endpoints sharing the same target
  servers have independent counters. (LB)
- With `MaxFailures > 0` and no health monitor, Apigee removes the target on
  the first failure and re-checks health "every five minutes". (LB)
- Health monitor: `<HealthMonitor>` is a child of `HTTPTargetConnection`, with
  `IsEnabled` (default `false`), `IntervalInSec` (required), and exactly one of
  `HTTPMonitor` or `TCPMonitor`. `TCPMonitor` requires `ConnectTimeoutInSec`
  and optionally `Port`. "Health monitors cannot be created in the UI." (LB)
- `TCPMonitor` child `<UseTargetServerSSLInfo>` is needed for health monitors
  that must use the target server's keystore/truststore (mTLS). (LB)
- Endpoint transport properties with defaults (EP):
  `allow.post.without.content.length` = false,
  `allow.put.without.content.length` = false,
  `allow.tls.session.resumption` = true,
  `keepalive.timeout.millis` = 60000,
  `connect.timeout.millis` = 3000,
  `ignore.allow.header.for.405` = true,
  `io.timeout.millis` = 55000,
  `supports.http11` = true,
  `use.proxy` = true,
  `use.proxy.tunneling` = true,
  `use.proxy.host.header.with.target.uri` = true,
  `retain.queryparams`.
- Status codes implied by those properties (EP): a **connection** timeout gives
  `503` (or `504` when `LoadBalancer` is used); an **IO** timeout reading the
  inbound request gives `408`, while a timeout writing the target request or
  reading the target response gives `504`.
- `request.payload.parse.limit` (ProxyEndpoint `Properties`): min 10M,
  max 30M, default 10M. `response.payload.parse.limit` (TargetEndpoint
  `Properties`): same 10M/30M/10M. (C)

### 2.3 AssignMessage

AM = <https://cloud.google.com/apigee/docs/api-platform/reference/policies/assign-message-policy>

- Parent element `<AssignMessage>`, attributes `continueOnError`, `enabled`,
  `name`. Child elements: `<Add>`, `<AssignTo>`, `<AssignVariable>`,
  `<Copy>`, `<DisplayName>`, `<IgnoreUnresolvedVariables>`, `<Remove>`,
  `<Set>`. (AM)
- `<Add>` children: `<FormParams>` / `<FormParam name="...">`,
  `<Headers>` / `<Header name="...">`, `<QueryParams>` / `<QueryParam name="...">`. (AM)
- `<Set>` children: `<Authentication>`, `<FormParams>`, `<Headers>`,
  `<Payload>`, `<Path>`, `<QueryParams>`, `<StatusCode>`, `<Verb>`,
  `<Version>`. (AM)
- `<Set><Verb>` accepts `[GET|POST|PUT|PATCH|DELETE|{variable}]`.
  `<Set><StatusCode>` accepts `HTTP_STATUS_CODE` or `{variable}`.
  `<Set><Payload>` takes attributes `contentType`, `variablePrefix`,
  `variableSuffix`. (AM)
- **`<Set>` overwrites; `<Add>` appends.** "`Set` overwrites headers or query
  or form parameters that already exist in the original message or adds new if
  they don't. Headers and query and form parameters in an HTTP message might
  hold multiple values. To add additional values ... use the `<Add>` element
  instead." (AM)
- `<AssignTo createNew="[true|false]" transport="http" type="[request|response]">DESTINATION_VARIABLE_NAME</AssignTo>` (AM)
- If `<AssignTo>` is omitted or empty, the policy acts on request or response
  "based on where the policy executes". (AM)
- `createNew="true"` + a name creates a custom message, e.g.
  `<AssignTo createNew="true" type="request">MyRequestObject</AssignTo>`.
  (AM)
- **Setting the target URL**: the `<Path>` (child of `<Set>`) section documents
  — in an aside, not body text — that to rewrite the target URL you must
  "override the `target.url` variable by configuring an AssignMessage policy
  with the `<AssignVariable>` element, and attaching it to the `TargetEndpoint`.
  (You can't override `target.url` in a policy attached to the
  `ProxyEndpoint`, because Apigee initializes the variable in the
  `TargetEndpoint`.)" Example given:
  `<AssignVariable><Name>target.url</Name><Value>https://mocktarget.apigee.net/user?user=Dude</Value></AssignVariable>`.
  A JavaScript policy in the TargetEndpoint can also override `target.url`. (AM)
- `<Copy source="VARIABLE_NAME">` with `<FormParams>`, `<Headers>`,
  `<Path>`, `<Payload>`, `<QueryParams>`, `<StatusCode>`, `<Verb>`, `<Version>`,
  each `[false|true]`. Omitting `source` means source is the `request` message. (AM)
- `<IgnoreUnresolvedVariables>` default is `true` in the UI template. When
  `false`, a referenced variable that does not exist puts the API flow into the
  fault state. (AM)
- The policy "executes actions in the order in which they appear in the policy
  configuration" — `<Remove>` must precede `<Set>` if you want remove-then-set. (AM)

### 2.4 Response caching and cache keys

RC = <https://cloud.google.com/apigee/docs/api-platform/reference/policies/response-cache-policy>
CK = <https://cloud.google.com/apigee/docs/api-platform/reference/policies/working-cachekeys>
CI = <https://cloud.google.com/apigee/docs/api-platform/cache/cache-internals>
LC = <https://cloud.google.com/apigee/docs/api-platform/reference/policies/lookup-cache-policy>
PC = <https://cloud.google.com/apigee/docs/api-platform/reference/policies/populate-cache-policy>
IC = <https://cloud.google.com/apigee/docs/api-platform/reference/policies/invalidate-cache-policy>
LIM = <https://cloud.google.com/apigee/docs/api-platform/reference/limits>

- Full element set: `<ResponseCache>` with `<DisplayName>`, `<Properties>`,
  `<CacheKey>` (containing `<Prefix>` and one or more `<KeyFragment>`),
  `<Scope>`, `<ExpirySettings>` (`<ExpiryDate>`, `<TimeOfDay>`,
  `<TimeoutInSeconds>`), `<CacheResource>`, `<CacheLookupTimeoutInSeconds>`,
  `<ExcludeErrorResponse>`, `<SkipCacheLookup>`, `<SkipCachePopulation>`,
  `<UseAcceptHeader>`, `<UseResponseCacheHeaders>`. (RC)
- Cache key composition: "Apigee composes the cache key of two parts, the
  prefix part and the composite fragment part, separated by a
  double-underscore": `PREFIX_PART__FRAGMENT_PART`. (CK)
- `<Prefix>` "overrides a `<Scope>` element value". (RC, LC, PC, IC, CK)
- `<Scope>` valid values: `Global`, `Application`, `Proxy`, `Target`,
  `Exclusive`. Default is `"Exclusive"`. (RC, LC, PC, IC)
- Scope prefixes (RC): `Global` -> `orgName__envName__`;
  `Application` -> `orgName__envName__apiProxyName`;
  `Proxy` -> `orgName__envName__apiProxyName__proxyEndpointName`;
  `Target` -> `orgName__envName__apiProxyName__targetEndpointName`;
  `Exclusive` -> `ApiProxyName_ProxyEndpointName` (or
  `ApiProxyName_TargetName`).
  Worked example: `apifactory__test__weatherapi__default__apiAccessToken`.
- `<KeyFragment ref="variable_name"/>` takes an optional `ref` attribute;
  "Should not be used if this element contains a literal value." (RC)
- Worked cache-key example (CK):
  `<Prefix>system1</Prefix>` + `<KeyFragment>apiAccessToken</KeyFragment>` +
  `<KeyFragment ref="request.header.Content-Type"/>` +
  `<KeyFragment>bar</KeyFragment>` -> `system1__apiAccessToken__application/json__bar`.
- `request.querystring` inserts the whole query string literally, so parameter
  **order matters**: "`param1=value1&param2=value2` and
  `param2=value2&param1=value1` don't result in the same cache key value." (CK)
- **Documented size/time limits**: "Cache keys are limited to a size of 2 KB."
  (RC) "The maximum size for each cached object is 256 KB." (RC)
  Limits page (LIM): Cache key size 2 KB (enforced); Cache value size 256 KB
  (enforced); Cache expiration ">=1 second, <= 30 days" (enforced);
  Items in cache "10 million in each cache"; Caches at environment scope 100;
  Cache resource deletion rate 1 per minute.
- `<ExcludeErrorResponse>` default `true` — by default error responses are NOT
  cached. "This policy can cache HTTP responses with **any** status code" if you
  set it to `false`. (RC)
- `<ExpirySettings>` is required. `<TimeoutInSeconds>` overrides both
  `<TimeOfDay>` and `<ExpiryDate>`. (RC)
- PopulateCache documents the precedence explicitly: "If you specify multiple
  elements, the order of precedence is: `TimeoutInSeconds`, `ExpiryDate`,
  `TimeOfDay`." (PC)
- `<ExpiryDate>` form `mm-dd-yyyy`; `<TimeOfDay>` form `HH:mm:ss`. On
  PopulateCache, `<TimeOfDay>` is "in the UTC time zone"; on ResponseCache the
  docs say "the default locale and time zone will vary depending on where the
  code is running". (PC, RC)
- `<TimeoutInSec>` is deprecated in favour of `<TimeoutInSeconds>`. (RC, PC)
- `ExpiryDate` in the past -> "the policy will apply the maximum time-to-live
  to the cached entry. This maximum is **30 days**." (PC)
- `<CacheResource>` names the cache; omit it to use the included shared cache.
  (RC, LC, PC, IC)
- `<CacheLookupTimeoutInSeconds>` **default is 30 on ResponseCache (RC) and 12
  on LookupCache (LC).** This is an inconsistency between the two pages — see
  gotchas.
- `<UseAcceptHeader>` default `false`. When `true`, Apigee appends
  `Accept`, `Accept-Encoding`, `Accept-Language` and `Accept-Charset` to the
  cache key. Motivation given: without it, a client that cannot read gzip can
  be served a gzipped cached entry. (RC)
- `<UseResponseCacheHeaders>` default `false`. When `true`, Apigee considers
  `Cache-Control s-maxage`, `Cache-Control max-age` and `Expires`, and uses the
  **lowest** of those and `<ExpirySettings>`. Precedence: `s-maxage` beats
  `max-age`. Worked example: no s-maxage, max-age 300, Expires in 3 days,
  TimeoutInSeconds 600 -> max-age 300 wins. (RC)
- **What invalidates a cache entry**: the `InvalidateCache` policy. (IC)
  It can also be invalidated by expiry (TTL). (CI)
- Two-level cache (CI): L1 is a **1-second** in-memory cache per message
  processor; L2 is a shared persistent store (Cassandra) across all message
  processors. Write = both. Read = L1 then L2, then miss.
  Update/invalidate = delete from L1 and L2 on the receiving processor only.
- Because L1 expires in one second, "there is no delete/update event needed to
  remove the entry from L1" — so after invalidation other processors can still
  serve a stale L1 entry for up to one second. (CI)
- "As the memory limit is reached, Apigee removes cache entries from memory
  (although they are still kept in the L2 persistent cache) ... on a
  least-recently-used basis." (CI)
- "L2 cache content in L2 is encrypted with the AES-256 algorithm."
  (CI) "**Apigee and Apigee hybrid (version 1.4 and later):** Cache and KVM
  data are always encrypted." (RC, PC)
- ResponseCache miss behaviour: "Apigee returns the actual response from the
  target to the client and stores the entry in cache until it expires or is
  invalidated." LookupCache miss: "No value is retrieved from the cache." (CI)
- ResponseCache flow variables (RC):
  `responsecache.{policy_name}.cachename`, `.cachekey`, `.cachehit`,
  `.invalidentry`.
- LookupCache flow variables (LC): `lookupcache.{policy-name}.cachename`,
  `.cachekey`, `.cachehit`, `.assignto`.
- InvalidateCache adds `<CacheContext>` with `<APIProxyName>`, `<ProxyName>`,
  `<TargetName>`, and `<PurgeChildEntries>` (default `false`) which "purges
  cache entries that share the same `<Prefix>` value ... even if the
  PopulateCache policy instances that loaded those items also used various
  `<KeyFragment>` elements". (IC)
- `<CacheContext>` values "are mandatory when a CacheKey prefix (that is, a
  custom prefix) is not used to clear cache entries added by another API
  proxy." (IC)
- LookupCache `<AssignTo>`: "The variable must be writable. If the cache lookup
  doesn't retrieve a value, the variable will not be set." (LC)
- PopulateCache `<Source>` is required and names the variable written to
  cache. (PC)

### 2.5 Key-value maps

KVM = <https://cloud.google.com/apigee/docs/api-platform/cache/key-value-maps>
KVMO = <https://cloud.google.com/apigee/docs/api-platform/reference/policies/key-value-map-operations-policy>
LIM as above

- KVM scopes (KVM): **API proxy** ("Only the API proxy can access the KVM"),
  **Environment** ("All API proxies in a specific environment"), and
  **Organization** ("All API proxies in all environments").
- Access paths: Apigee UI, Apigee REST API, or the KeyValueMapOperations
  policy. "You will need to create a KVM with the API before accessing it with
  the KeyValueMapOperations policy." (KVM, KVMO)
- REST endpoints by scope (KVM):
  `organizations.apis.keyvaluemaps`,
  `organizations.environments.keyvaluemaps`,
  `organizations.keyvaluemaps`
  (plus `.entries` variants, and `/delete` sub-resources).
- Example proxy-scoped GET (KVM):
  `https://apigee.googleapis.com/v1/organizations/ORG/apis/API/keyvaluemaps/KVM`
- "A KVM is a custom collection of encrypted key/value String pairs." (KVM)
- Encryption (KVM): "In **Apigee**, all KVM entries for API proxy, organization
  and environment scopes are protected using the Cloud KMS key provided when an
  Apigee organization is provisioned (see the `runtimeDatabaseEncryptionKey`
  field in the Organization resource). Apigee uses AES256." "In **Apigee
  hybrid**, you can provide separate encryption keys ... cipher sizes of
  AES128, AES196 or AES256."
- Masking (KVM): `maskedValues` flag / **Mask values** UI setting. "Values are
  masked at the KVM level. You can't mask individual KVM entries; either all
  values within a KVM are masked, or none are." Masking is not auto-enabled for
  existing KVMs.
- KVM names "can contain only letters, numbers, and hyphens and cannot be
  longer than 255 characters. It cannot include spaces or other special
  characters." (KVM)
- Policy root element `<KeyValueMapOperations>` with attribute
  `mapIdentifier="urlMapper"`. (KVMO)
- `<Scope>` valid values: `organization`, `environment` (default), `apiproxy`,
  `policy` (API proxy revision). (KVMO)
- `<Get assignTo="VARIABLE_NAME" index="INDEX_NUMBER">`. `index` is
  **1-based**; "If no index value is specified, all the values of that entry
  are assigned to the variable as a `java.util.List`." (KVMO)
- `<Put override="BOOLEAN">`, `<Delete>`, `<InitialEntries>`,
  `<MapName>`, `<Key>` / `<Parameter>`, `<Value>`, `<ExpiryTimeInSecs>`,
  `<ExclusiveCache>` (deprecated — "Use the `<Scope>` element instead"). (KVMO)
- A key can be composite: `<Key><Parameter ref='userID'/><Parameter ref='role'/></Key>`. (KVMO)
- "The key size is limited to 2 KB." (KVMO)
- `<InitialEntries>`: "Keys and values populated by this element must be
  literals. For example, `<Parameter ref="request.queryparam.key">` isn't
  supported within this element." (KVMO)
- `<ExpiryTimeInSecs>` default `300` (5 minutes); a value of 0 or -1, or
  omitting the element, means 300. (KVMO)
- "This KVM Operations policy always reads from cache for `GET` operations."
  (KVMO)
- "using `PUT` will only refresh the cache in the single runtime node that
  services the request" — a PUT does not invalidate other runtime nodes.
  (KVMO)
- "You must specify the same scope value you used when the map was created."
  (KVMO)
- `private.` prefix: "use the `private.` prefix on the variable name specified
  in the `assignTo` attribute" to hide the value from Debug sessions; without
  it "the data retrieved from the KVM will appear in cleartext". (KVMO, KVM)
- KVM limits (LIM): KVMs at organization scope 100; at environment scope 900;
  at proxy scope 4,250 or 6,000; KVM key size 2 KB; KVM value size **10 KB**;
  items in KVMs across the organization 5 million. Note the "Currently
  enforced?" column: key size and value size are **"Planned"**, i.e. not
  automatically enforced.

### 2.6 JavaScript callouts and the JavaScript object model

JS = <https://cloud.google.com/apigee/docs/api-platform/reference/policies/javascript-policy>
OM = <https://cloud.google.com/apigee/docs/api-platform/reference/javascript-object-model>

- "Apigee supports JavaScript running on the **Rhino JavaScript engine 1.7.13**."
  "JavaScript source files must have a `.js` extension." (JS)
- Policy element is `<Javascript ... timeLimit="200" name="...">`. Children:
  `<DisplayName>`, `<Properties>`/`<Property name="propName">`,
  `<SSLInfo>` (`<Enabled>`, `<ClientAuthEnabled>`, `<KeyStore>`, `<KeyAlias>`,
  `<TrustStore>`), `<IncludeURL>`, `<ResourceURL>`, `<Source>`. (JS)
- `timeLimit` is **required**: "Specifies the maximum time (in milliseconds) a
  script can execute. For example, if a 200 ms limit is exceeded, the policy
  throws this error: `Javascript.{policy_name} failed with error: Javascript
  runtime exceeded limit of 200ms`." (JS)
- `languageVersion` optional, default `VERSION_DEFAULT`; values
  `VERSION_DEFAULT`, `VERSION_1_0` ... `VERSION_1_8`, `VERSION_ES6`. (JS)
- "Either `<ResourceURL>` or `<Source>` is required. If both `<ResourceURL>` and
  `<Source>` are present, the policy ignores `<ResourceURL>`." (JS)
- Resource URL pattern `jsc://filename.js`; files live in
  `apiproxy/resources/jsc` at API proxy scope, or at environment/organization
  scope. (JS)
- JS object model scope objects: `context`, `request`, `response`, `crypto`,
  `print`, `properties`. (OM)
- "The `context` object has global scope. It is available everywhere within the
  API proxy flow. It has four child objects: `proxyRequest`, `proxyResponse`,
  `targetRequest`, `targetResponse`." (OM)
- `request`/`response` are "**shorthand** references to the ambient request and
  response": in a proxy flow they are `context.proxyRequest` /
  `context.proxyResponse`; in a target flow they are `context.targetRequest` /
  `context.targetResponse`. (OM)
- `context` methods: `context.getVariable(name)`, `context.setVariable(name, value)`,
  `context.removeVariable(name)`. (OM)
- `context.flow` values: `PROXY_REQ_FLOW`, `PROXY_RESP_FLOW`,
  `TARGET_REQ_FLOW`, `TARGET_RESP_FLOW`. "Each Flow name encompasses the
  PreFlow, PostFlow, and any conditional Flows defined in the ProxyEndpoint(s)
  or TargetEndpoint(s)." (OM)
- `context.session` — "a map of name/value pairs that you can use to pass
  objects between two different steps executing in the same context". (OM)
- `properties.<name>` reads the `<Property name="...">` value. (JS, OM)
- `crypto` supports **SHA-1, SHA256, SHA512, MD5**; each object offers
  `update()`, `digest()` (hex) and `digest64()` (base64). (OM)
  **There is no standalone `Base64` object on this page.** The only base64
  functionality documented is `digest64()` on a hash object. I could not verify
  a general-purpose Base64 encoder/decoder in the JavaScript object model.
- `print()` writes to the Debug tool; visible under the `stepExecution-stdout`
  property. (JS, OM)
- `.asXML` notation: "the string includes all declarations as well as XML
  comments" for `*.content`; "cleaned of declarations and comments" for
  `*.content.asXML`. Only the `.asXML` form can traverse the XML hierarchy. (OM)
- `httpClient` exposes exactly two methods, `get()` and `send()`, for
  "multiple, parallel, asynchronous HTTP requests". `httpClient.get(url)` is
  "for simple HTTP `GET` requests, **with no support for HTTP headers**". (OM)
- Recommended target URL rewrite pattern (JS): in `TARGET_REQ_FLOW`,
  `context.setVariable("target.url", url)`.
- Apigee "does not recommend" JavaScript for logging (use MessageLogging),
  for replacing Apigee policies, or for system calls — "The security model does
  not permit system calls from the JavaScript policy... Although some calls
  might be functional, they are unsupported and subject to active disablement at
  any time." (JS)

### 2.7 Service callouts

SC = <https://cloud.google.com/apigee/docs/api-platform/reference/policies/service-callout-policy>

- Typical composition: AssignMessage builds the request, ServiceCallout sends
  it and names the response variable, ExtractVariables parses the response. (SC)
- `<ServiceCallout>` with `<Request clearPayload="true" variable="myRequest">`
  (containing `<IgnoreUnresolvedVariables>`, `<Remove>`, `<Copy>`, `<Add>`,
  `<Set>`), `<Response>calloutResponse</Response>`, `<Timeout>30000</Timeout>`,
  and one of `<HTTPTargetConnection>` (with `<URL>`, `<LoadBalancer>`,
  `<SSLInfo>`, `<Properties>`, `<Authentication>`) or `<LocalTargetConnection>`
  (`<APIProxy>`, `<ProxyEndpoint>`, `<Path>`). (SC)
- `<Timeout>`: "The time in milliseconds that the ServiceCallout policy will
  wait for a response from the target. **You cannot set this value dynamically
  at runtime.**" **Default 55000 milliseconds (55 seconds)**, "the default HTTP
  timeout setting for Apigee". "If the ServiceCallout hits a timeout, an HTTP
  500 is returned, the policy fails, and the API proxy goes into an error
  state." (SC)
- `<HTTPTargetConnection>` and `<LocalTargetConnection>`, each **Required** —
  one of the two must be present, enforced at deploy time as
  `ConnectionInfoMissing`. (SC)
- `<LocalTargetConnection>` "Specifies a local proxy — that is, a proxy in the
  same organization and environment". (SC)
- `<HTTPTargetConnection><LoadBalancer>` supports the same
  `<Algorithm>`/`<Server name="...">` form as a target endpoint, e.g.
  `<Server name="httpbin"/>`. (SC)
- `<HTTPTargetConnection><URL>` is required inside HTTPTargetConnection
  (deploy error `URLMissing` if missing or empty). (SC)
- `<Authentication>` children: `<HeaderName>`, plus either
  `<GoogleAccessToken>` (`<Scopes>`/`<Scope>`, `<LifetimeInSeconds>`) or
  `<GoogleIDToken>` (`<Audience useTargetUrl="BOOLEAN">`, `<IncludeEmail>`). (SC)

### 2.8 ExtractVariables

EV = <https://cloud.google.com/apigee/docs/api-platform/reference/policies/extract-variables-policy>

- `<ExtractVariables>` children: `<DisplayName>`, `<Source clearPayload="true|false">request</Source>`,
  `<VariablePrefix>`, `<IgnoreUnresolvedVariables>`, `<URIPath>`/`<Pattern ignoreCase="...">`,
  `<QueryParam name="...">`/`<Pattern>`, `<Header name="...">`/`<Pattern>`,
  `<FormParam name="...">`/`<Pattern>`, `<Variable name="...">`/`<Pattern>`,
  `<JSONPayload>`/`<Variable name="..." type="float">`/`<JSONPath>`,
  `<XMLPayload stopPayloadProcessing="false">`/`<Namespaces>`/
  `<Variable name="..." type="boolean">`/`<XPath>`. (EV)
- "Variables set with the ExtractVariables policy have *global* scope" — usable
  from any policy or code in any stage of the flow that executes *after* the
  ExtractVariables policy, including PreFlow, PostFlow, PostClientFlow and
  Error Flows. (EV)
- Multiple `<Pattern>` resolution (EV): "All patterns are tested for match. If
  none of the patterns match, the policy does nothing and the variable(s) is not
  created. If more than one pattern matches, the pattern with longest path
  segments is used for extraction. If two matched patterns has same longest path
  segments, then the pattern specified first in the policy is used."
- URI patterns match against `proxy.pathsuffix`. Example: base path
  `/basepath/v1`, request `/basepath/v1/a/b`, pattern `/a/{pathSeg}` ->
  `urirequest.pathSeg` = `b`. (EV)
- "If the pattern does not match, then the corresponding variable is not
  created. Therefore, if another policy references the variable, it can cause an
  error." Mitigation: `<IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>`
  in the *referencing* policy treats it as an empty string. (EV)
- "The policy executes sequentially from the first extraction pattern to the
  last. If the policy writes a value to the same variable from multiple places,
  the last write in the policy determines the value." (EV)
- JSONPath/XPATH: "All `<Variable>` tags in the policy are evaluated ... If the
  `<Variable>` tag does not evaluate to a valid field in the JSON or XML, then
  the corresponding variable is not created." (EV)

### 2.9 Synchronous versus asynchronous

Q = <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
C = <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>

- Quota `<Synchronous>` default `false`. `true`: counters update at the same
  time the quota is checked. `false`: "it is possible that some API calls
  exceeding the quota will go through, depending on when the quota counter in
  the central repository is asynchronously updated." (Q)
- "The default asynchronous update interval is 10 seconds." (Q)
- `<AsynchronousConfiguration>` with `<SyncIntervalInSeconds>` (default 10
  seconds) and `<SyncMessageCount>`. "Apigee ignores this element when
  `<Synchronous>` is set to `true`." (Q)
- Exact async semantics (Q): interval only -> sync every N seconds;
  count only -> every M messages or every 10 seconds, whichever comes first;
  both -> every M messages or every N seconds, whichever comes first; neither
  -> every 10 seconds.
- "The sync interval must be >= 10 seconds, as described in Limits." (Q)
- The generic `async` policy attribute (C): "When set to `true`, policy
  execution is offloaded to a different thread, leaving the main thread free to
  handle additional requests... overusing async can hurt performance with too
  much thread switching."
- **Conflict:** every individual policy page I read documents the `async`
  attribute as "This attribute is deprecated." with default `false`
  (RC, LC, IC, PC, SA, JS, SC, EV, AM). The api-proxy-configuration-reference
  page (C) still documents `async` as live behaviour. Treat `async` as
  deprecated; see gotchas.
- `<IntegrationEndpoint><AsyncExecution>true|false</AsyncExecution></IntegrationEndpoint>`
  selects sync vs async for integrations (C). I did not fetch the
  integration-callout-policy page that `<AsyncExecution>` links to.
- MessageLogging is asynchronous by design: "Apigee logs messages
  asynchronously: the response is returned while the logs are still being
  written." (message-logging-policy)

---

## 3. DOCUMENTED GOTCHAS

Flows and conditions

- Only *named* flows can be conditional. PreFlow/PostFlow always run. (conditions-reference)
- Only the **first** matching conditional flow in a segment runs. Unreachable
  conditional flows are a common cause of "my policy never executes". (what-are-flows)
- A trailing condition-less flow silently behaves as an `else`. (api-proxy-configuration-reference)
- Arithmetic operators are unsupported in `<Condition>`. Use a JavaScript policy
  or `<AssignMessage><Set>` for math. (conditions-reference)
- `Matches`/`Like` is glob, NOT regex. `~~`/`JavaRegex` is regex, and it
  anchors on the whole string. (conditions-reference, flow-variables-and-conditions)
- `proxy.pathsuffix` always begins with `/`; a leading `/` in your pattern is
  part of the match. (flow-variables-and-conditions)
- `%` is the escape character in path expressions. (conditions-reference)
- Null-comparison semantics are surprising and are tabulated on the conditions
  page: with `=`, LHS null -> false; with `!=`, LHS null -> **true**;
  with `~`/`~~`/`~/`, RHS null -> N/A. (conditions-reference)

AssignMessage

- **You cannot set `target.url` from a ProxyEndpoint-attached policy.** Apigee
  initialises `target.url` in the TargetEndpoint. Attach the AssignMessage (with
  `<AssignVariable><Name>target.url</Name>`) to the TargetEndpoint. (assign-message-policy)
- `<Set>` overwrites, `<Add>` appends. Use the wrong one and you silently drop
  a second header/query-param value. (assign-message-policy)
- You cannot add or change query parameters or form parameters on the
  **response**; only on the request. (assign-message-policy)
- Action order matters: `<Remove>` must be placed before `<Set>`. (assign-message-policy)
- With `<IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>` (not the
  UI default), one missing variable puts the flow into the fault state. (assign-message-policy)
- The UI-inserted default policy contains stubs for every operation; if you add
  policies without pruning, surprising behaviour results. (assign-message-policy)
- A custom message created with `createNew="true"` is **not** automatically
  used. "By default, Apigee does nothing with the custom request message" — you
  must reference it explicitly (typically from ServiceCallout). (assign-message-policy)
- **Documentation defect:** the `<Path>` (child of `<Set>`) section has no body
  text; its entire content is inside an `<aside>`. Any extractor that strips
  `<aside>` will render this section empty.

Caching

- **`<CacheLookupTimeoutInSeconds>` default is 30 on ResponseCache but 12 on
  LookupCache.** Same element name, same policy family, different documented
  default. Verify empirically before relying on either. (response-cache-policy vs lookup-cache-policy)
- **`<Scope>Exclusive` prefix is documented inconsistently.**
  `working-cachekeys` gives
  `orgName__envName__apiProxyName__deployedRevisionNumber__nameof(proxyEndpoint|targetEndpoint)__[serializedCacheKey]`
  and the example `mycompany__prod__weatherapi__16__default__hello__world`
  (note the revision number 16). `response-cache-policy` omits the revision
  number: `orgName__envName__apiProxyName__proxy|TargetName__[serializedCacheKey]`,
  example `apifactory__test__weatherapi__default__apiAccessToken`.
  (working-cachekeys vs response-cache-policy)
- The `Scope` value descriptions also disagree on naming: `Application` is
  described as `orgName__envName__apiProxyName` on ResponseCache/PopulateCache
  but `orgName__envName__applicationName` on LookupCache/InvalidateCache. (same four pages)
- `<CacheKey>` is **required**, but `<KeyFragment>` is optional — a `<CacheKey>`
  with only a `<Prefix>` is valid and produces a constant cache key. (PC, LC, IC)
- Default `<ExcludeErrorResponse>true</ExcludeErrorResponse>` means **error
  responses are not cached**. Users expecting a 500 to be cached must set it to
  `false`. (response-cache-policy)
- `<UseAcceptHeader>` defaults to `false`; without it a client that cannot
  handle gzip can be served a gzipped cached entry. (response-cache-policy)
- `<TimeOfDay>` timezone is "UTC" on PopulateCache but "default locale and time
  zone will vary depending on where the code is running" on ResponseCache.
  (PC vs RC)
- `ExpiryDate` in the past does not mean "expired" — it silently becomes the
  30-day maximum TTL. (populate-cache-policy)
- ResponseCache **cannot be attached to multiple request paths** or
  **multiple response paths** within any flow; deployment fails with
  `ResponseCacheStepAttachmentNotAllowedReq` / `...Resp`. This is the single
  most restrictive caching rule in the set. (response-cache-policy)
- After an InvalidateCache, other message processors can still serve the old
  value from their 1-second L1 cache. (cache-internals)
- L1 eviction is LRU under memory pressure and is **not configurable**. (cache-internals)
- Cache value size limit is 256 KB — large payloads are silently not cached.
  (response-cache-policy, limits)
- `InvalidateCache` can only purge entries written under the same prefix /
  CacheContext; `CacheContext` values are mandatory when clearing another
  proxy's entries without a custom prefix. (invalidate-cache-policy)
- LookupCache does not set the `AssignTo` variable on a miss. Downstream
  policies referencing it will fault. (lookup-cache-policy)
- `<CacheResource>` naming a cache that does not exist is a **deployment**
  error, not a runtime error. (RC, LC, PC, IC)

KVM

- "when accessing a map or map entry, you must specify the same scope value you
  used when the map was created." (key-value-map-operations-policy)
- `<Get index="...">` is **1-based**; index 0 or negative is a deployment
  error (`InvalidIndex`). Omitting `index` assigns a `java.util.List`. (key-value-map-operations-policy)
- `<InitialEntries>` accepts **literals only** — `<Parameter ref="...">` is not
  supported there. (key-value-map-operations-policy)
- A `PUT` refreshes the in-memory KVM cache **only on the node that served the
  request**. Other runtime nodes keep serving the old value until
  `<ExpiryTimeInSecs>` elapses. Expect apparent write-visibility lag in
  multi-node deployments. (key-value-map-operations-policy)
- Without the `private.` prefix on `assignTo`, KVM secrets appear in
  cleartext in Debug sessions. (key-value-map-operations-policy, key-value-maps)
- KVM masking is all-or-nothing per map, and is **not** retroactively enabled
  for existing KVMs. (key-value-maps)
- The Apigee UI can only create **environment-scoped** KVMs. Organization- and
  proxy-scoped KVMs require the API. (key-value-maps, key-value-map-operations-policy)
- "You will need to create a KVM with the API before accessing it with the
  KeyValueMapOperations policy." (key-value-map-operations-policy)
- The `<Get>` section says "Be sure to specify the name of the KVM either with
  the `mapIdentifier` attribute on the root element or with the `<MapName>`
  element" — i.e. `mapIdentifier` is not strictly required if `<MapName>` is
  present, but an empty `mapIdentifier` produces the runtime fault
  `steps.keyvaluemapoperations.UnsupportedOperationException`. (key-value-map-operations-policy)
- KVM key size 2 KB / value size 10 KB are listed as **"Planned"** for
  enforcement, not currently enforced. (limits)

JavaScript

- `timeLimit` is required and throws when exceeded — the message is
  `Javascript.{policy_name} failed with error: Javascript runtime exceeded
  limit of {N}ms`. (javascript-policy)
- `<ResourceURL>` and `<Source>` both present -> `<ResourceURL>` is silently
  ignored. (javascript-policy)
- `<ResourceURL>`/`<IncludeURL>` must point at a resource of type **jsc**;
  anything else is `WrongResourceType` at deploy. The referenced file must exist
  at API proxy, environment, or organization scope or deployment fails. (javascript-policy)
- System calls are not permitted: file system reads/writes, current user
  information, process lists, CPU/memory utilisation. "Although some calls might
  be functional, they are unsupported and subject to active disablement at any
  time." (javascript-policy)
- The runtime is **Rhino 1.7.13**, not Nashorn/V8. Modern JS syntax beyond
  ES5 will not run; use `languageVersion="VERSION_ES6"` carefully. (javascript-policy)
- `request`/`response` change meaning depending on which flow the policy is
  attached to. A script that works in the proxy request flow can silently act
  on a different object in the target flow. (javascript-object-model)
- `httpClient.get()` supports **no HTTP headers**. (javascript-object-model)
- No standalone Base64 helper is documented (only `digest64()` on hash objects).
  Unverified whether `Base64` exists undocumented.

ServiceCallout

- `<Timeout>` cannot be set dynamically at runtime — no `ref` support. (service-callout-policy)
- Default timeout is 55000 ms, and a timeout produces **HTTP 500** plus a fault
  state, not a 504. (service-callout-policy)
- `<HTTPTargetConnection>` and `<LocalTargetConnection>` are each documented
  Required; exactly one must be present (`ConnectionInfoMissing` otherwise). (service-callout-policy)
- `<URL>` missing or empty inside `<HTTPTargetConnection>` -> `URLMissing` deploy error. (service-callout-policy)
- `<Timeout>` of 0 or negative -> `InvalidTimeoutValue` deploy error. (service-callout-policy)
- Hybrid only: the runtime service account must hold
  `roles/iam.serviceAccountTokenCreator` on `apigee-runtime`, or
  `<GoogleAccessToken>`/`<GoogleIDToken>` fails with
  `GoogleTokenGenerationFailure`. (service-callout-policy)
- The `Request` variable must be a `Message`/`RequestMessage` type, not a
  string or a Response. (service-callout-policy)

ExtractVariables

- A non-matching pattern does not create the variable; it silently leaves it
  undefined. Downstream policies then fault. (extract-variables-policy)
- A policy with none of `URIPath`, `QueryParam`, `Header`, `FormParam`,
  `XMLPayload`, `JSONPayload` fails to deploy (`NothingToExtract`). (extract-variables-policy)
- `InvalidJSONPath` is a **runtime** error (500) even though it looks like a
  static config problem. (extract-variables-policy)
- Repeated `<Variable>` names across extraction points: last write wins. (extract-variables-policy)
- The docs' own deployment-error text for `EmptyJSONPathExpression` says
  "empty `XPath` expression within the `XMLPayload` element" — a copy-paste
  error in the source docs. (extract-variables-policy)

Routing / target servers

- `<MaxFailures>` defaults to **0**, i.e. no failover at all. Most "load
  balancing isn't failing over" reports trace to this default. (load-balancing-across-backend-servers)
- An HTTP 500 from the target **resets** the failure counter rather than
  incrementing it, unless the code is listed in `<ServerUnhealthyResponse>`.
  (load-balancing-across-backend-servers)
- Failure counters are per-load-balancer, not per-target-server, so two target
  endpoints sharing servers behave independently. (load-balancing-across-backend-servers)
- `<Path>` in `HTTPTargetConnection` is **ignored** unless `<LoadBalancer>` is
  present. (load-balancing-across-backend-servers)
- Exactly one target server may have `<IsFallback>true</IsFallback>`. (load-balancing-across-backend-servers)
- Health monitors cannot be created in the UI — bundle upload required. (load-balancing-across-backend-servers)
- Health monitors cannot use target-server keystores/truststores unless
  `<UseTargetServerSSLInfo>true</UseTargetServerSSLInfo>`. (load-balancing-across-backend-servers)
- `BasePath` must be unique per environment; wildcards are allowed except
  `/**/` and a leading `*`. "Apigee does NOT support using a wildcard `*` as the
  first element of a base path. For example, this is NOT supported:
  `/*/search`." (api-proxy-configuration-reference)

Policy behaviour

- The `async` attribute is documented as **deprecated** on every individual
  policy page, yet still documented as functional on
  api-proxy-configuration-reference. Treat it as deprecated and do not build
  on it. (both pages — conflict)
- Policy `name` attribute: letters, numbers, spaces, hyphens, underscores and
  periods are permitted per the policy pages, but api-proxy-configuration-reference
  restricts names to `A-Za-z0-9._\- $ %`. The UI additionally "automatically
  removes characters that are not alphanumeric". (conflict; all pages)
- Quota `<StartTime>` is supported **only** for `type="calendar"`. (quota-policy)
- `<Identifier>` and `<Class>` "cannot be used ... in the same Quota policy". (quota-policy)
- If the quota `Identifier` variable is `developer.id` or `developer.app.id`,
  the docs warn those values "may change, during some future maintenance
  period", during which the quota would not be strictly enforced. (quota-policy)
- `<SyncIntervalInSeconds>` must be >= 10 seconds. (quota-policy)
- SpikeArrest `<UseEffectiveCount>` defaults to `false` (token-bucket rate
  smoothing), but the docs state: "Although the default value is `false`,
  **Apigee organizations should set this element to `true`**." Rate smoothing
  "can potentially deny multiple legitimate requests coming in over a short
  time interval". (spike-arrest-policy)
- MessageLogging: "Proxy calls succeed when logging fails" — because logging is
  buffered, a logging failure does not fail the API call, and "There might be
  occasions when a log is not written without an error being returned".
  Buffer overflow shows as `steps.messagelogging.TooManyPendingLoggingRequest`
  (2500 pending per runtime pod) or "Log message size exceeded". Syslog message
  size is `max.log.message.size.in.kb`, default 128 KB. (message-logging-policy)
- MessageLogging `<Syslog>` and `<CloudLogging>` cannot both be present in the
  same policy. (message-logging-policy)
- `response` flow variables are unavailable in the Error Flow, and unavailable
  in PostClientFlow if the preceding flow was the Error Flow. Use `message`
  instead. (message-logging-policy)
- Shared flows must be in the same organization **and the same environment**
  as the consuming proxies, and must be deployed first. A FlowCallout to an
  undeployed shared flow gives runtime 500 `flow.SharedFlowNotFound`. (shared-flows, flow-callout-policy)
- CORS: "The `AllowOrigins` field is a required policy element and the default
  should not be set to allow all (`*`)" — `*` "effectively disables the
  same-origin protection". (cors-policy)

---

## 4. FAULT CODES BY POLICY

Sources: the `## Error reference` / `## Error codes` sections of the pages in
section 1. Runtime faults carry an HTTP status. Deployment errors have none —
they mean the revision was rejected at upload.

### AssignMessage

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/assign-message-policy>

Runtime:

- `steps.assignmessage.SetVariableFailed` / 500 — policy could not set a
  variable; see the fault string for the unresolved variable name.
- `steps.assignmessage.VariableOfNonMsgType` / 500 — the `source` attribute of
  `<Copy>` names a variable that is not of type message.
- `steps.assignmessage.UnresolvedVariable` / 500 — variable is out of scope
  for the flow, or cannot be resolved.

Deployment:

- `InvalidIndex` — index in `<Copy>` and/or `<Remove>` is 0 or negative.
- `InvalidVariableName` — `<Name>` empty or missing inside `<AssignVariable>`.
- `InvalidPayload` — payload in the policy is invalid.

Fault variables: `fault.name="FAULT_NAME"`, `assignmessage.POLICY_NAME.failed`.

### ResponseCache

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/response-cache-policy>

Runtime: "This policy does not throw any runtime errors." (Corroborated: the
corresponding troubleshoot runtime URL returns HTTP 200 but is a stub page
reading "The equivalent page does not exist in Apigee.")

Deployment:

- `InvalidTimeout` — `<CacheLookupTimeoutInSeconds>` set to a negative number.
- `InvalidCacheResourceReference` — `<CacheResource>` names a cache that does
  not exist in the deploy environment.
- `ResponseCacheStepAttachmentNotAllowedReq` — same ResponseCache policy
  attached to multiple request paths within any flow.
- `ResponseCacheStepAttachmentNotAllowedResp` — same, for response paths.
- `InvalidMessagePatternForErrorCode` — invalid condition in `<SkipCacheLookup>`
  or `<SkipCachePopulation>`.
- `CacheNotFound` — the cache named in the error message has not been created
  on a specific message processor.

Fault variables: N/A (policy-level).

### LookupCache

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/lookup-cache-policy>

Runtime: none.
Deployment: `InvalidCacheResourceReference`, `InvalidTimeout`, `CacheNotFound`
(same causes as above).
Fault variables: N/A.

### InvalidateCache

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/invalidate-cache-policy>

Runtime: none.
Deployment: `InvalidCacheResourceReference`, `CacheNotFound`.
Fault variables: N/A.

### PopulateCache

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/populate-cache-policy>

Runtime:

- `policies.populatecache.EntryCannotBeCached` / 500 — the message being cached
  is not an instance of a Serializable class.

Deployment:

- `InvalidCacheResourceReference` — `<CacheResource>` names a nonexistent cache.
- `CacheNotFound` — the cache specified in `<CacheResource>` does not exist.

Fault variables: `fault.name="fault_name"`, `populatecache.POLICY_NAME.failed`.
Example response faultstring: `[entry] can not be cached. Only serializable
entries are cached.`

### KeyValueMapOperations

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/key-value-map-operations-policy>

Runtime:

- `steps.keyvaluemapoperations.UnsupportedOperationException` / 500 — the
  `mapIdentifier` attribute is set to an empty string.

Deployment:

- `InvalidIndex` — `index` attribute of `<Get>` is zero or negative (index
  starts at 1).
- `KeyIsMissing` — `<Key>` missing, or `<Parameter>` missing inside `<Key>`,
  under `<Entry>` under `<InitialEntries>`.
- `ValueIsMissing` — `<Value>` missing under `<Entry>` under `<InitialEntries>`.

### Quota

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>

Runtime:

- `policies.ratelimit.FailedToResolveQuotaIntervalReference` / 500 — `<Interval>`
  not defined.
- `policies.ratelimit.FailedToResolveQuotaIntervalTimeUnitReference` / 500 —
  `<TimeUnit>` not defined.
- `policies.ratelimit.InvalidMessageWeight` / 500 — `<MessageWeight>` resolved
  to a non-integer.
- `policies.ratelimit.QuotaViolation` / 500 — quota limit exceeded.

Deployment:

- `InvalidQuotaInterval` — `<Interval>` is not an integer.
- `InvalidQuotaTimeUnit` — unsupported time unit; valid are `minute`, `hour`,
  `day`, `week`, `month`.
- `InvalidQuotaType` — invalid `type` attribute; valid are `default`,
  `calendar`, `flexi`, `rollingwindow`.
- `InvalidStartTime` — bad `<StartTime>` format; valid is `yyyy-MM-dd HH:mm:ss`.
- `StartTimeNotSupported` — `<StartTime>` used with a non-`calendar` quota type.
- `InvalidSynchronizeIntervalForAsyncConfiguration` — `<SyncIntervalInSeconds>`
  less than zero.
- `InvalidAsynchronizeConfigurationForSynchronousQuota` — async configuration
  combined with a synchronous quota.

Fault variables: `fault.name="fault_name"`, `ratelimit.POLICY_NAME.failed`.

### SpikeArrest

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy>

Runtime:

- `policies.ratelimit.FailedToResolveSpikeArrestRate` / 500 — `<Rate>` reference
  cannot be resolved; rate is mandatory in the form `intpm` or `intps`.
- `policies.ratelimit.InvalidMessageWeight` / 500 — `<MessageWeight>` non-integer.
- `policies.ratelimit.SpikeArrestViolation` / **429** — rate limit exceeded.

Deployment:

- `InvalidAllowedRate` — `<Rate>` is not an integer, or lacks a `ps`/`pm` suffix.

Fault variables: `fault.name="fault_name"`, `ratelimit.POLICY_NAME.failed`.

### JavaScript

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/javascript-policy>

Runtime (all 500):

- `steps.javascript.ScriptExecutionFailed` — many underlying types; documented
  ones are RangeError, ReferenceError, SyntaxError, TypeError, URIError.
- `steps.javascript.ScriptExecutionFailedLineNumber` — JS error; see fault string.
- `steps.javascript.ScriptSecurityError` — security error during execution.

Deployment:

- `InvalidResourceUrlFormat` — bad format in `<ResourceURL>` or `<IncludeURL>`.
- `InvalidResourceUrlReference` — referenced JS file does not exist at API
  proxy, environment, or organization level.
- `WrongResourceType` — resource is not of type `jsc`.
- `NoResourceURLOrSource` — `<ResourceURL>` not declared, or `<IncludeURL>`
  declared without a resource URL.

Fault variables: `fault.name="fault_name"`, `javascript.POLICY_NAME.failed`.
Note: the policy's `timeLimit` overrun produces a runtime failure message
(`Javascript.<name> failed with error: Javascript runtime exceeded limit of
Nms`) that is not listed in the runtime errors table.

### ServiceCallout

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/service-callout-policy>

Runtime:

- `steps.servicecallout.ExecutionFailed` / 500 — malformed input, **or** the
  backend returns an error status (by default 4xx or 5xx).
- `steps.servicecallout.RequestVariableNotMessageType` / 500 — the `Request`
  variable is not of type `Message`.
- `steps.servicecallout.RequestVariableNotRequestMessageType` / 500 — the
  `Request` variable is not of type `RequestMessage` (e.g. it is a Response).
- `googletoken.EmptyIDTokenAudience` / 500 — `<GoogleIDToken>` enabled but
  `useTargetUrl` false and no `<Audience>` value.
- `messaging.adaptors.http.filter.GoogleTokenGenerationFailure` / 500 — service
  account missing/disabled, `roles/iam.serviceAccountTokenCreator` not granted
  (hybrid), IAMCredentials API disabled, or invalid `<GoogleAccessToken>` scopes.

Deployment:

- `URLMissing` — `<URL>` inside `<HTTPTargetConnection>` missing or empty.
- `ConnectionInfoMissing` — neither `<HTTPTargetConnection>` nor
  `<LocalTargetConnection>` present.
- `InvalidTimeoutValue` — `<Timeout>` negative or zero.
- `FAILED_PRECONDITION` — service account missing while `<Authentication>` is
  configured.
- `PERMISSION_DENIED` — service account permission problem.

### ExtractVariables

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/extract-variables-policy>

Runtime (all 500):

- `steps.extractvariables.ExecutionFailed` — empty input payload, or invalid /
  malformed JSON or XML.
- `steps.extractvariables.ImmutableVariable` — the policy tried to set an
  immutable variable.
- `steps.extractvariables.InvalidJSONPath` — invalid JSON path in `<JSONPath>`.

Deployment:

- `NothingToExtract`, `NONEmptyPrefixMappedToEmptyURI`, `DuplicatePrefix`,
  `NoXPathsToEvaluate`, `EmptyXPathExpression`, `NoJSONPathsToEvaluate`,
  `EmptyJSONPathExpression`, `MissingName`, `PatternWithoutVariable`,
  `CannotBeConvertedToNodeset`, `JSONPathCompilationFailed`,
  `InstantiationFailed`, `XPathCompilationFailed`, `InvalidPattern`.

### FlowCallout

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/flow-callout-policy>

Runtime:

- `flow.SharedFlowNotFound` / 500 — "Either the shared flow does not exist, or
  the shared flow exists but is **not deployed**."

Deployment: N/A.

### MessageLogging

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/message-logging-policy>

Runtime (all 500):

- `steps.messagelogging.StepDefinitionExecutionFailed` — see fault string.
- `steps.messagelogging.InvalidGoogleCloudLogName` — `<LogName>` does not
  evaluate to `projects/{project}/logs/{logid}`.
- `steps.messagelogging.InvalidJsonMessage` — `contentType` is
  `application/json` but the message is not valid JSON.
- `steps.messagelogging.TooManyPendingLoggingRequest` — more than **2500**
  pending requests per Apigee runtime pod not yet written to Cloud Logging.
- For `<Syslog>`, the analogous failure is the log line
  `Log message size exceeded. Increase the max message size setting`.

### CORS

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/cors-policy>
Fetched but not fully mined for this section; the page has `## Error codes`
with Runtime / Deployment / Fault variables subsections.

---

## 5. 404 / NOT FOUND

All verified 404 by `curl -w "%{http_code}"` on
`https://cloud.google.com/apigee/docs/<path>`:

- api-platform/reference/policies/basic-auth-policy (real page is `basic-authentication-policy`)
- api-platform/reference/policies/target-server-policy (no such policy exists)
- api-platform/reference/policies/routing-policy (no such policy)
- api-platform/reference/policies/key-value-map-policy (real page is `key-value-map-operations-policy`)
- api-platform/debug/debug-runtime-errors
- api-platform/reference/policies/response-cache-policy-hybrid
- api-platform/deploy/target-servers (target servers are covered by `deploy/load-balancing-across-backend-servers`)
- api-platform/reference/target-server-reference
- api-platform/reference/policies/cache-policy
- api-platform/reference/policies/concurrent-rate-limit-policy
- api-platform/reference/policies/target-endpoint-policy
- api-platform/fundamentals/what-is-a-target-server
- api-platform/cache/cache-size-limits (limits live on `reference/limits`)
- api-platform/reference/policies/jsc-policy (real page is `javascript-policy`)
- api-platform/reference/policies/key-value-map-operations (missing `-policy`)
- api-platform/reference/policies/quota
- api-platform/reference/policies/response-cache
- api-platform/reference/policies/javascript
- api-platform/reference/policies/service-callout
- api-platform/reference/policies/extract-variables
- api-platform/reference/policies/flow-callout
- api-platform/cache/key-value-map (real page is `cache/key-value-maps`)
- api-platform/reference/cache-keys (real page is `reference/policies/working-cachekeys`)
- api-platform/fundamentals/flow-variables (real pages are
  `fundamentals/flow-variables-and-conditions` and `reference/variables-reference`)

**HTTP 200 but no content** (different failure mode, worth its own warning):

- api-platform/troubleshoot/policies/runtime/responsecache-runtime-errors —
  200, 1371 bytes, body reads "## The equivalent page does not exist in Apigee."

---

## Explicitly NOT verified

- A standalone `Base64` object in the JavaScript object model. The page
  documents only `digest64()` on SHA-1/SHA256/SHA512/MD5 objects. I could not
  verify a general Base64 encoder/decoder and am not claiming one exists or does
  not exist.
- `integration-callout-policy` / `<AsyncExecution>` detail. The element is named
  on api-proxy-configuration-reference but I did not fetch that policy page.
- The complete fault-code tables for CORS, MessageLogging deployment errors,
  RaiseFault, and the individual troubleshoot playbook pages. Those pages were
  fetched and verified but not mined line by line for this scope.
- Behaviour of `<ScriptTarget>` — mentioned as a thing not to combine with
  `HTTPTargetConnection`/`LocalTargetConnection`, but never documented in the
  sections I read.
- Any claim about Apigee Edge for Private Cloud. Every page I read carries the
  banner "This page applies to **Apigee** and **Apigee hybrid**" and links out
  to docs.apigee.com for Edge. Nothing here is verified for OPDK.
