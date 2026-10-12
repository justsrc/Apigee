# Policy mechanics: targets, timeouts, deployment, variables, conditions

Verified reference for the places an answer is most often invented. Everything below was
read out of `research/pages/` on a cached fetch. Where the documentation is silent or
self-contradictory it says so, because a wrong confident answer costs more than a gap.

Evidence labels follow `references/sources.md`: Documented means it is on a verified page.

## Target endpoints, target servers, load balancing

### Target servers are environment resources, not proxy XML

A target server is a named host/port/protocol record stored in an environment, created
through the UI, the Management API, or the Apigee API. It is referenced by name from a
`<TargetEndpoint>` or from a ServiceCallout policy. It is not an element you write inside
proxy XML. Limit: 8,000 target servers per environment.
Source: [load-balancing-across-backend-servers](https://cloud.google.com/apigee/docs/api-platform/deploy/load-balancing-across-backend-servers)

```
POST https://apigee.googleapis.com/v1/organizations/$ORG/environments/$ENV/targetservers
{ "name": "target1", "host": "1.mybackendservice.com",
  "protocol": "http", "port": "80", "isEnabled": "true" }
```

In environments enabled for archive deployments you cannot manage target servers through
the UI, API, or gcloud at all. Source: same page.

### Element shape

`<LoadBalancer>` is a child of `<HTTPTargetConnection>`. Its documented children are
`<Algorithm>`, `<Server>` (with optional `<Weight>` and `<IsFallback>`), `<MaxFailures>`,
`<ServerUnhealthyResponse>` (containing `<ResponseCode>`), and `<RetryEnabled>`.
`<HTTPTargetConnection>` also accepts `<URL>`, `<Path>`, `<SSLInfo>`, `<Properties>`,
`<Authentication>`, and `<HealthMonitor>`.
Sources: [load-balancing](https://cloud.google.com/apigee/docs/api-platform/deploy/load-balancing-across-backend-servers),
[api-proxy-configuration-reference](https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference)

```xml
<TargetEndpoint name="default">
  <HTTPTargetConnection>
    <LoadBalancer>
      <Algorithm>RoundRobin</Algorithm>
      <Server name="target1" />
      <Server name="target2">
        <Weight>2</Weight>
      </Server>
      <MaxFailures>5</MaxFailures>
      <ServerUnhealthyResponse>
        <ResponseCode>404</ResponseCode>
        <ResponseCode>500</ResponseCode>
        <ResponseCode>502</ResponseCode>
        <ResponseCode>503</ResponseCode>
      </ServerUnhealthyResponse>
    </LoadBalancer>
    <Path>/test</Path>
  </HTTPTargetConnection>
</TargetEndpoint>
```

### Algorithms

Exactly three documented values: `RoundRobin`, `Weighted`, `LeastConnections`. RoundRobin
is the default. Weighted requires a `<Weight>` on every `<Server>`.
Source: [load-balancing](https://cloud.google.com/apigee/docs/api-platform/deploy/load-balancing-across-backend-servers)

### MaxFailures

**The default is 0, and 0 means no failover at all.** The documentation states it this
way: "The MaxFailures default is 0. This means that Apigee always tries to connect to the
target for each request and never removes the target server from the rotation." A health
monitor requires MaxFailures greater than 0. Both regular API calls and health monitor
calls count toward the total. The running count is kept per load balancer, not per target
server, so two target endpoints each with their own `<LoadBalancer>` do not share counts.
Sources: [load-balancing](https://cloud.google.com/apigee/docs/api-platform/deploy/load-balancing-across-backend-servers),
[load-balancing-maxfailures antipattern](https://cloud.google.com/apigee/docs/api-platform/antipatterns/load-balancing-maxfailures)

**Documentation conflict worth naming.** The load-balancing page says that with MaxFailures
greater than 0 and no health monitor, Apigee "will automatically take the target server out
of rotation when the first failure is detected" and "will check the health of the target
server every five minutes and return it to the rotation when it responds normally". The
antipatterns page says the opposite for the single-target case: Apigee "does not
automatically put the TargetServer back in rotation" and "the API Proxy must be
redeployed". Both are on official pages. Treat recovery-without-a-health-monitor as
unestablished and recommend a health monitor rather than picking a side.

The antipatterns page also states that with a single target server and MaxFailures greater
than 0, requests fail continuously with `503` at the target endpoint and `500` when the
same shape is used in a ServiceCallout policy, until the proxy is redeployed. It states
that without a health monitor Apigee removes the target on the **first** failure, not on
the Nth.

### ServerUnhealthyResponse

By default any response from a target, including `404` or `500`, **resets** the failure
counter. Retries are not triggered by HTTP error codes. Adding `<ServerUnhealthyResponse>`
with `<ResponseCode>` children makes Apigee count those responses as failures, which is
what actually takes an unhealthy server out of rotation.
Source: [load-balancing](https://cloud.google.com/apigee/docs/api-platform/deploy/load-balancing-across-backend-servers)

Documented example values are `404`, `500`, `502`, `503`. The page does **not** enumerate an
allowed set, so do not assert a closed list. In particular `200` is not documented here;
the only `<ResponseCode>200</ResponseCode>` on that page sits inside the health monitor's
`<SuccessResponse>` block, which is a different element.

### Retry and fallback

`<RetryEnabled>` defaults to `true`. Retry fires on I/O exceptions, HTTP timeouts, and on
responses matching `<ServerUnhealthyResponse>`. At least two target servers are required for
retry to work. One and only one `<Server>` may carry `<IsFallback>true</IsFallback>`. If the
fallback server is unhealthy, API calls return `503`. Failover events are not shown as
individual server failures in Trace; consult Cloud Logging.
Source: [load-balancing](https://cloud.google.com/apigee/docs/api-platform/deploy/load-balancing-across-backend-servers)

`<Path>` is only used when `<LoadBalancer>` is present, and is ignored otherwise. It accepts
a literal string or a message template. In an `<HTTPMonitor>` the `<Path>` element does not
support variables. Source: same page.

### SSLInfo

For a `<TargetEndpoint>` the documented children are `Enabled`, `Enforce`, `TrustStore`,
`ClientAuthEnabled`, `KeyStore`, `KeyAlias`, `IgnoreValidationErrors`, `Ciphers`,
`Protocols`, `CommonName`. There is no `ClientCertStore` and no `ClientCertAlias`.
`KeyStore` and `KeyAlias` are required if `ClientAuthEnabled` is true. If `<sSLInfo>` is
set in both the target server and the target endpoint, the target server wins.
Source: [api-proxy-configuration-reference](https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference)

## Timeouts and which status code you get

| Property | Default | Where | Documented status code |
| --- | --- | --- | --- |
| `connect.timeout.millis` | 3000 | `<HTTPTargetConnection>` | `503` on connection timeout; `504` in some cases when a `<LoadBalancer>` is used |
| `io.timeout.millis` | 55000 | `<HTTPTargetConnection>` | `504` on write to target or read from target; `408` on read from ingress |
| `api.timeout` | none | `<HTTPProxyConnection>` | `504` when the proxy exceeds the budget |
| `keepalive.timeout.millis` | 60000 | `<HTTPTargetConnection>` | n/a, connection pool idle close |
| `ignore.allow.header.for.405` | true | | returns `405` to the client instead of `502` |

Source: [endpoint-properties-reference](https://cloud.google.com/apigee/docs/api-platform/reference/endpoint-properties-reference)

How the two main timeouts interact, as documented:

1. The Ingress sends its timeout to the Message Processor. It defaults to 300 seconds and
   is not configurable.
2. The Message Processor sets `api.timeout`. If unset it uses the Ingress timeout; if set
   it uses the lesser of the Ingress timeout and the configured value.
3. `api.timeout` is the whole-request budget from API request to response. After each
   policy, and before calling the target, the processor computes
   `api.timeout - elapsed`. If negative, it returns `504 Gateway Timeout`.
4. `io.timeout.millis` is the budget for the target. Before connecting it becomes the lesser
   of `api.timeout - elapsed` and `io.timeout.millis`.

Other documented details from the same page:

- With a `<LoadBalancer>` configured and `<RetryEnabled>` true, Apigee retries the connection
  up to three times automatically, so total retry time can exceed `connect.timeout.millis`.
  A plain `<URL>` target does not retry.
- `api.timeout` must be shorter than the standard Message Processor timeout of 300 seconds
  and cannot be set with a variable.

**Where the docs are silent.** No page here maps a specific timeout value to `502`. Do not
assert one.

## Deployment and the Management API

### The deploy call

```
POST https://apigee.googleapis.com/v1/{name=organizations/*/environments/*/apis/*/revisions/*}/deployments
```

The resource name is `organizations/{org}/environments/{env}/apis/{api}/revisions/{rev}`.
The request body must be empty. Success returns a `Deployment` resource.
Query parameters: `override` (default `false`; when false the deployment is rejected if
another revision of the same proxy is already deployed), `sequencedRollout` (default false),
and `serviceAccount` (`{ACCOUNT_ID}@{PROJECT}.iam.gserviceaccount.com`, which additionally
requires `iam.serviceAccounts.actAs`).
OAuth scope: `https://www.googleapis.com/auth/cloud-platform`.
Source: [organizations.environments.apis.revisions.deployments/deploy](https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.environments.apis.revisions.deployments/deploy)

### IAM permissions for that call

Two are required, on two different resources:

- `apigee.deployments.create` on `organizations/{org}/environments/{env}`
- `apigee.proxyrevisions.deploy` on `organizations/{org}/apis/{api}/revisions/{rev}`

Source: same page. A caller with only one of the two gets a permission error, which is a
common and easily misread support ticket.

### Equivalent command line

```
gcloud apigee apis deploy [REVISION] --api=API --environment=ENV [--organization=ORG] [--override]
```

REVISION defaults to `latest`. Without `--override`, the command fails if a conflicting
revision is already deployed. `gcloud apigee apis` has exactly five subcommands: `deploy`,
`describe`, `import`, `list`, `undeploy`. There is no `revisions` subcommand.
Sources: [gcloud apis deploy](https://cloud.google.com/sdk/gcloud/reference/apigee/apis/deploy),
[gcloud apis](https://cloud.google.com/sdk/gcloud/reference/apigee/apis)

`gcloud apigee developers` has exactly two subcommands, `describe` and `list`. There is no
`developers create`.
Source: [gcloud developers](https://cloud.google.com/sdk/gcloud/reference/apigee/developers)

### A successful deploy call does not mean the runtime applied the change

Documented: Apigee runs an "eventually consistent deployment model". Message Processors act
independently and any given MP can be in a different state from the others, and "Deploying
an API proxy on Apigee does not make it immediately available. It takes time for the API
proxy to be synchronized across all MPs in the runtime plane." The pages here give no
numeric propagation time, so do not quote one.
Source: [ui-deploy-overview](https://cloud.google.com/apigee/docs/api-platform/deploy/ui-deploy-overview)

To confirm the runtime state rather than the API state, read the deployment status:

```
GET https://apigee.googleapis.com/v1/organizations/$ORG/environments/$ENV/apis/$API/revisions/$REV/deployments
gcloud alpha apigee deployments describe --api=$API --environment=$ENV
```

The response carries `deploymentStatus` (`deployed`) and `statusCodeDetails` (`Deployment
Success`). Source: [ui-deploy-overview](https://cloud.google.com/apigee/docs/api-platform/deploy/ui-deploy-overview)

Other documented properties of deployment, same page: a deployed revision is read-only and
cannot be edited; all successful deployments are zero downtime, where the new revision is
deployed to the MPs before the old one is undeployed; if the new revision fails to deploy
the previous one stays live; Message Processors deploy a bundle only in its entirety.

On hybrid, the deploy call also validates shared flow dependencies. A FlowCallout policy
referencing a shared flow that does not exist or is not deployed fails the deployment with
`flow.SharedFlowNotFound`. Source: deploy reference page, and
[flow-callout-policy](https://cloud.google.com/apigee/docs/api-platform/reference/policies/flow-callout-policy)

## Reading headers, query params and payloads from a JavaScript policy

`context` has four child objects: `context.proxyRequest`, `context.proxyResponse`,
`context.targetRequest`, `context.targetResponse`. There are also shorthands `request` and
`response`, which point at whichever pair is in scope where the script runs.
Source: [javascript-object-model](https://cloud.google.com/apigee/docs/api-platform/reference/javascript-object-model)

**`context.request` does not exist.** The string does not appear on that page and is not a
documented member. The same applies to `request.getValue(...)`; the documented accessors are
`context.getVariable`, `context.setVariable` and the property tables below.

### Headers

```js
context.proxyRequest.headers['Content-Type']   // "application/json"
context.targetRequest.headers['TARGET-HEADER-X'] = 'foo';   // set on outbound only
context.getVariable("request.header.x-apikey") // flow variable form
```

### Query parameters

```js
context.proxyRequest.queryParams['city']  // list; doc example shows 'PaloAlto'
context.getVariable("request.queryparam.user")
```

The doc's own example is internally inconsistent: it writes
`queryParams['city'][0] == 'PaloAlto'` while elsewhere using `[1] == 'NewYork'`, which is
one-based indexing, not JavaScript's zero-based. Do not rely on the index; use the flow
variable form or read the list.

### Payload

```js
context.proxyRequest.body.asJSON.a           // == 1
context.targetRequest.body.asXML.name        // element text
context.targetRequest.body.asXML.@number     // attribute
context.proxyRequest.body.asForm['vehicle'][0]
context.getVariable("request.content")       // whole payload as a string
```

For responses: `context.targetResponse.status.code`, `.status.message`,
`.headers['Set-Cookie']`, `.content.asJSON`.

Flow variable reference for the same values:
[variables-reference](https://cloud.google.com/apigee/docs/api-platform/reference/variables-reference)
documents `request.header.<name>`, `request.header.<name>.N`, `request.header.<name>.values`,
`request.header.<name>.values.string`, `request.queryparam.<name>`, `request.queryparam.<name>.N`,
`request.queryparam.<name>.values`, `request.formparam.<name>`, `request.formparams.count`,
`request.headers.count`, `request.headers.names`, `request.content`,
`request.content.as.base64`.

**Where the docs are silent.** The cached object model page does not document
`request.getHeader()`, `request.getParameter()` or `request.getContent()` as methods. Use
the mapping properties above.

## Conditional flows and Condition syntax

Basic form, spaces required around the operator:

```xml
<Condition>VARIABLE_NAME OPERATOR "VALUE"</Condition>
<Condition>request.verb = "GET"</Condition>
<Condition>(proxy.pathsuffix MatchesPath "/statuses") and (request.verb = "GET")</Condition>
```

Operators, with the word forms accepted: `=`/`Equals`/`Is`, `!=`/`NotEquals`/`IsNot`,
`:=`/`EqualsCaseInsensitive`, `>`/`>=`/`<`/`<=`, `&&`/`And`, `||`/`Or`, `~`/`Matches`/`Like`,
`~~`/`JavaRegex`, `~/`/`MatchesPath`/`LikePath`, `=|`/`StartsWith`, `!`/`Not`, `()` for
grouping.
Source: [conditions-reference](https://cloud.google.com/apigee/docs/api-platform/reference/conditions-reference)

Restrictions stated on that page: operators cannot be used as variable names; a space is
required before and after the operator; to include an operator character in a variable name,
quote the name in single quotes; arithmetic operators (`+ * - / %`) are not supported;
Java precedence applies; matching uses `java.util.regex`. The Apigee UI does not support the
literal `<` or `<=`.

Where `<Condition>` attaches, with the documented child order:

- `<Flow>`: only **named** flows can be conditional. Preflows and postflows on both
  `<ProxyEndpoint>` and `<TargetEndpoint>` always execute.
- `<Step>`: `<Condition>` then `<Name>`.
- `<RouteRule>`: `<Condition>` then `<TargetEndpoint>`.
- `<FaultRule>`: `<Condition>` then `<Step>`.

Literals: `null`, `true`, `false`. Operand comparison coerces to a common type, so
`response.status.code = "400"` and `= 400` are equivalent. A null left-hand side with `=`
evaluates to false, and `!=` evaluates to true.

### Common errors

- **Double quotes inside a JavaRegex expression.** The condition syntax requires the regex
  to be wrapped in double quotes, so an inner `"` produces an `Invalid Condition` error.
  Replace it with the Unicode escape `\u0022`.
  Source: [flow-variables-and-conditions](https://cloud.google.com/apigee/docs/api-platform/fundamentals/flow-variables-and-conditions)
- **JavaRegex matches the whole subject.** `returned_roles ~~ "editor"` fails when the value
  is `editor, author, guest`. Use `~~ ".*\beditor\b.*"`.
- **An empty `<Condition>` element** is not a condition. `<Condition></Condition>` is
  shown as the empty starting point, not as a passing match.
- **Quotes in the docs are inconsistent about `<` and `<=`** in the UI. If a condition was
  authored in the UI and does not parse, check for a mangled `<`.

## AccessControl element shape

```
<AccessControl name="ACL">
  <ClientIPVariable>FLOW_VARIABLE</ClientIPVariable>
  <IPRules noRuleMatchAction="ALLOW">
    <MatchRule action="ALLOW">
      <SourceAddress mask="32">198.51.100.1</SourceAddress>
    </MatchRule>
    <MatchRule action="DENY">
      <SourceAddress mask="24">198.51.100.1</SourceAddress>
    </MatchRule>
  </IPRules>
  <ValidateBasedOn>X_FORWARDED_FOR_ALL_IP</ValidateBasedOn>
</AccessControl>
```

`noRuleMatchAction` and `MatchRule/@action` both take `ALLOW` or `DENY`, both default to
`ALLOW`, and both are required. `SourceAddress/@mask` is required: IPv4 range 1 to 32, IPv6
range 1 to 128. Both the mask and the address accept message templates. `ValidateBasedOn`
takes `X_FORWARDED_FOR_ALL_IP` (default), `X_FORWARDED_FOR_FIRST_IP`, or
`X_FORWARDED_FOR_LAST_IP`. `ClientIPVariable` takes any flow variable; `client.resolved.ip`
is the documented choice.
Source: [access-control-policy](https://cloud.google.com/apigee/docs/api-platform/reference/policies/access-control-policy)

Real fault codes on that page: `accesscontrol.IPDeniedAccess` (403) and
`accesscontrol.InvalidIPAddressInVariable` (500). Both are in `references/error-codes.md`.

There is no `<IPRange>`, no `type="blacklist"`, no `<Include>` and no `<Exclude>`. There is
no `<Products>` element in this policy.

## THINGS AGENTS INVENT

Each of these was searched across all 408 cached pages and appears in none of them. If an
answer contains one, it is fabricated.

| Invented | Reality |
| --- | --- |
| `policies.ratelimit.QuotaExceeded` | Does not exist. Real code is `policies.ratelimit.QuotaViolation`. |
| `policies.ratelimit.SpikeArrested` | Does not exist. Real code is `policies.ratelimit.SpikeArrestViolation`. |
| `<Priority>` in target config | Does not exist anywhere in the configuration schema. |
| `<CircuitBreaker>` in target config | Does not exist. Health checks are `<HealthMonitor>`, and there is no breaker element. |
| `<Threshold>` in target config | Does not exist. The failover threshold is `<MaxFailures>`. |
| `leastConnectionsWithHealthCheck` | Does not exist. Only `RoundRobin`, `Weighted`, `LeastConnections`. |
| `weightedRoundRobin` | Does not exist. The algorithm is `Weighted`. |
| `<Target enabled="false">` | Does not exist. There is no `<Target>` element. Servers are listed as `<Server name="...">` inside `<LoadBalancer>`; disabling a target server is done through the target server resource `isEnabled`. |
| `<ClientCertStore>` | Does not exist. `<SSLInfo>` uses `KeyStore` and `KeyAlias` with `ClientAuthEnabled`. |
| `<ClientCertAlias>` | Does not exist, same reason. |
| `<IPRange type="blacklist">` | Does not exist. `AccessControl` uses `<IPRules>` with a `noRuleMatchAction` attribute. |
| `<Include>` / `<Exclude>` in AccessControl | Do not exist. Rules are `<MatchRule>` with `action="ALLOW"` or `action="DENY"`. |
| `<APIKey name="..." location="...">` | Does not exist. `VerifyAPIKey` has only `<APIKey ref="...">`. |
| `<MinTimeBetweenFailures>` | Does not exist. The recovery mechanism is `<HealthMonitor>` with `IntervalInSec`. |
| `<LoadBalancing>` | Does not exist. The element is `<LoadBalancer>`, a child of `<HTTPTargetConnection>`. Confusing these two is a common error, so state which one you mean. |
| `<TargetServer>` as proxy XML | Does not exist as a proxy config element. A target server is an environment resource referenced by name. One antipatterns page shows a `<TargetServer>` XML block, which contradicts the rest of the documentation. Do not emit that XML. |
| `context.request.getValue(...)` | Does not exist. Use `context.getVariable("request.header.x")`, or the `context.proxyRequest` / `context.targetRequest` property tables. |
| `gcloud apigee apis revisions` | Does not exist. `gcloud apigee apis` has deploy, describe, import, list, undeploy. |
| `gcloud apigee developers create` | Does not exist. That group has describe and list only. |
| `organizations.apis.deployments.create` | Does not exist. The resource is `organizations/{org}/environments/{env}/apis/{api}/revisions/{rev}/deployments` and the call is `POST` on it. |

Sources for every real value in the right-hand column:
[quota-policy](https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy),
[spike-arrest-policy](https://cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy),
[load-balancing](https://cloud.google.com/apigee/docs/api-platform/deploy/load-balancing-across-backend-servers),
[api-proxy-configuration-reference](https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference),
[access-control-policy](https://cloud.google.com/apigee/docs/api-platform/reference/policies/access-control-policy),
[verify-api-key-policy](https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-api-key-policy),
[javascript-object-model](https://cloud.google.com/apigee/docs/api-platform/reference/javascript-object-model),
[gcloud apis](https://cloud.google.com/sdk/gcloud/reference/apigee/apis),
[gcloud developers](https://cloud.google.com/sdk/gcloud/reference/apigee/developers),
[deploy REST reference](https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.environments.apis.revisions.deployments/deploy)

## Where the documentation is genuinely silent

Say so rather than filling the gap. No page in the cache gives:

- a numeric deployment propagation time across Message Processors
- a closed set of permitted `<ServerUnhealthyResponse>/<ResponseCode>` values
- a `502` cause tied to a specific timeout
- whether a removed target server returns to rotation without a health monitor (the two
  pages contradict each other, see above)
- `getHeader()` / `getParameter()` / `getContent()` methods on the `request` object