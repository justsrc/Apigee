# Medium scenarios

Thirty cases that need more than one hypothesis tested. Each has a plausible first
explanation that turns out to be wrong, or a genuine interaction between components that
a single-look diagnosis will misread.

MED-01 through MED-15 are documented or synthetic. MED-16 through MED-30 are imported from
real reports and known issues; where a source record is closed rather than fixed, the
scenario says so. MED-23 through MED-30 come from public GitHub issues in the apigee
GitHub organization, each cross-checked against the repository's own source where the
claim was about code.

Fault codes are real and live in
`.agents/skills/apigee-support-core/references/error-codes.md`. Do not add codes that are
not in that file.

---

### MED-01. Deployed successfully, every request returns 404

#### Scenario metadata

- ID: MED-01
- Difficulty: medium
- Primary topic: environments and environment groups
- Secondary topics: deployment state, routing
- Product: Apigee (environment groups do not exist on Edge)
- Origin: documented
- Versions: checked 2026-10-11
- Evaluation objectives: the deployment genuinely succeeded; resist the urge to redeploy.
  The correct first move is to establish product and environment membership.
- Skills expected: apigee-support-core

#### Initial support ticket

> We deployed our proxy to the `prod` environment about an hour ago. The deployment call
> returned success. Every request to the proxy host returns 404. The same proxy works
> perfectly in `test`. Can you redeploy it?

#### Initial evidence

Deployment list for `prod` shows the revision deployed. A request to the proxy hostname
returns 404 with an Apigee error body. The proxy has no conditional flows on the request
path.

#### Expected investigation

The agent should resist the redeploy request. A successful deploy plus a universal 404
points at environment addressing, not at the proxy. It should establish the product first,
because environment groups do not exist on Edge, then check whether `prod` belongs to at
least one environment group.

#### Diagnostic evidence

Querying environment group attachments shows `test` is a member of a group and `prod` is
not attached to any. The documented requirement is that an environment must be a member
of at least one environment group before proxies deployed within it can be accessed.

#### Ground-truth resolution

The proxy is deployed and working. `prod` is not attached to an environment group, so the
proxy hostname resolves to nothing that serves this environment.

The deployment succeeded because attachment is a separate configuration step. Nothing
about the proxy or the revision is wrong.

#### Correct remediation

Attach the environment to an environment group, through the Management API or the
console. This is a control-plane change affecting address resolution, so it is
significant and should be scheduled rather than done as a reflex.

Confirm the intended hostname and group before attaching, since the group determines
which proxy versions that hostname serves.

#### Verification

Confirm the attachment exists, then send a request to the proxy hostname. Then confirm
requests to other environments attached to the same group still resolve, since a
misconfigured group can affect more than the environment you were fixing.

#### Common incorrect answers

Redeploying the proxy. It is already deployed and the redeploy changes nothing.

Raising an "Error Saving Revision" support case. There is no save error.

Telling them to check the proxy endpoint path. The 404 is environmental, and the same
path works in `test`.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Suggests redeploy | Suspects environment config | Identifies the environment group requirement |
| Product and version | Applies Edge advice | Correct product unstated | Establishes product before prescribing |
| Diagnostic method | Retries deployment | Checks deployment state | Checks group membership separately |
| Safety | Acts immediately | Suggests the change | Schedules and confirms group intent first |
| Verification | None | Retests | Retests and checks other environments |

#### Critical failures: recommending a redeploy as the fix; asserting the deploy failed.

#### References

- Fundamentals, environments overview:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/environments-overview>
- Compare Apigee products:
  <https://cloud.google.com/apigee/docs/api-platform/get-started/compare-apigee-products>

---

### MED-02. Works for some users, 404s for others, same deployment

#### Scenario metadata

- ID: MED-02
- Difficulty: medium
- Primary topic: runtime propagation after deployment
- Secondary topics: eventual consistency, environments
- Product: Apigee
- Origin: documented
- Versions: checked 2026-10-11
- Evaluation objectives: separate "deployment reported success" from "runtime is serving
  the new revision"; the two are different questions with different answers
- Skills expected: apigee-support-core

#### Initial support ticket

> We deployed revision 12 about ten minutes ago. Our own tests pass. A colleague in
> another region still gets the old behavior and one customer reports 404. Are the
> deployments not global?

#### Initial evidence

The deployment call returned success. Requests from the deploying team succeed with new
behavior. The colleague in the other region still gets the old behavior, and one customer
reports 404 on the `prod` hostname. Analytics shows traffic in both regions.

#### Expected investigation

The agent should separate three things that are easy to conflate: whether the revision was
saved, whether the runtime reports the revision as ready, and whether a given route
serves it. The documented model is eventually consistent: Message Processors act
independently of one another and any given MP can be in a different state than the
others. Two different symptoms in two different places is the expected shape of a
deployment that is still propagating, not evidence of two separate faults.

#### Diagnostic evidence

Checking deployment state shows the `test` environment deployment reported as `READY`,
while the `prod` deployment has not reached that state and its per-pod deployment status
is not `deployed`. The colleague and the customer both use the `prod` environment
hostname.

#### Ground-truth resolution

Revision 12 is deployed to `test` and ready. The `prod` deployment is still propagating
across Message Processors.

The deployment API call returning success means the deployment was accepted, not that
every runtime has finished loading it. Deployment state is a separate check, which is why
it exists.

Propagation explains one of the two symptoms and the documentation does not reach the other.
An MP that has not finished applying revision 12 is still serving revision 11, which is the
old behavior, so that accounts for the colleague. It does not account for the 404: deployment
is zero-downtime, the new revision is applied before the old one is undeployed, so there is no
documented window in which a Message Processor serves neither. An agent that says so is
reading the deployment model correctly, not splitting hairs.

The 404 therefore needs its own cause, and the evidence does not supply one. That is the
honest state of the case: wait for `READY` on `prod`, and if the 404 is still there, keep
looking. What the evidence rules out is the opposite move, which is to declare a routing or
environment-group fault while the deployment is still propagating, because it fits the
symptom and not the evidence.

#### Correct remediation

This needs time and observation, not intervention. Confirm the `prod` deployment reaches
`READY`.

Do not redeploy to "speed it up". Redeploying does not shorten propagation and adds a
revision to the history.

#### Verification

Wait for `READY` on `prod`, then confirm requests from the second region serve revision
12. If the 404 persists after the deployment reports `READY`, it is a different fault and
needs its own investigation, which is the point at which to start looking beyond
deployment state.

#### Common incorrect answers

Redeploying to force propagation.

Claiming deployments are regional by design. Nothing in the evidence supports a regional
deployment model, and that framing would mislead the team about their topology.

Diagnosing the 404 as an environment group or routing problem while `prod` is still
propagating. It fits the symptom and not the evidence.

Claiming propagation explains the 404 as well as the stale behavior. The deployment model is
zero-downtime, so a Message Processor mid-propagation is still serving the previous revision.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says deployments are regional | Identifies propagation | Separates save, state, and routing |
| Diagnostic method | Redeploys | Checks traffic | Checks deployment state per environment |
| Handling of competing causes | Invents a routing or environment-group cause while `prod` is propagating | Notes both symptoms | Ties the stale behavior to propagation and says the 404 is not covered by the documented deployment model, naming what to check next |
| Safety | Redeploys | Waits | Waits without redeploying and says when to look further |
| Verification | None | Retests | Waits for `READY`, retests, and sets a condition for escalating |

#### Critical failures: asserting a regional deployment model without evidence; declaring the
404 solved by propagation without saying that the documented deployment model does not cover
it.

#### References

- Deploy an API proxy revision:
  <https://cloud.google.com/apigee/docs/api-platform/deploy/ui-deploy-overview>

---

### MED-03. Load balancing does not fail over to a healthy backend

#### Scenario metadata

- ID: MED-03
- Difficulty: medium
- Primary topic: target servers and load balancing
- Secondary topics: HTTP error handling, resilience
- Product: Apigee or hybrid
- Origin: documented
- Versions: checked 2026-10-11
- Evaluation objectives: find the documented default that disables failover; the obvious
  "the backend is down so it must fail over" framing hides two separate settings
- Skills expected: apigee-support-core

#### Initial support ticket

> Our orders backend has two nodes. When one of them starts returning 500, load balancing
> keeps sending it about half the traffic and those requests keep failing. When one node is
> stopped outright, every other request gets noticeably slower before it succeeds. Load
> balancing is configured. Why is it not protecting us?

#### Initial evidence

Two target servers configured under a `<LoadBalancer>`. Requests routed to a node that
returns 500 fail. When a node is stopped entirely, those requests eventually succeed via
the other node, but only after a failed connection attempt.

#### Expected investigation

Two documented settings govern this and both default in a way that surprises people. The
agent should check `<MaxFailures>`, whose documented default of 0 means Apigee never removes
a target server from rotation, and check how HTTP 500 responses are classified.

#### Diagnostic evidence

The target endpoint config shows:

```xml
<TargetEndpoint name="default">
  <HTTPTargetConnection>
    <LoadBalancer>
      <Algorithm>RoundRobin</Algorithm>
      <Server name="orders-1" />
      <Server name="orders-2" />
    </LoadBalancer>
    <Path>/orders</Path>
  </HTTPTargetConnection>
</TargetEndpoint>
```

#### Ground-truth resolution

Two independent causes.

`<MaxFailures>` is absent, and the documented default is 0: "Apigee always tries to connect
to the target for each request and never removes the target server from the rotation." That
is why the stopped node keeps receiving traffic indefinitely. Individual failing requests
can still be retried against another server, which is why the requests eventually succeed,
but the dead node never leaves rotation, so every other request pays a failed connection
attempt first. The documented default for `<RetryEnabled>` is `true`, and retries are
triggered by I/O exceptions and HTTP timeouts, not by HTTP error codes.

Even with failover enabled, an HTTP 500 from the target does not count as a failure.
The documented behaviour is that when Apigee receives a response from a target, "even if the
response is an HTTP error (such as `404` or `500`), that counts as a response from the target
server, and the failure counter is reset." Only codes listed under
`<ServerUnhealthyResponse>` increment the counter.

So the two-node setup behaves differently depending on failure mode, which is exactly what
the ticket describes: a stopped node produces a connection failure that can be retried
elsewhere but never removes the node, and a 500-returning node is never treated as unhealthy
at all.

#### Correct remediation

Set a real failure threshold, classify the error codes the backends actually return, and
pair it with a health monitor so a recovered server returns to rotation:

```xml
<TargetEndpoint name="default">
  <HTTPTargetConnection>
    <LoadBalancer>
      <Algorithm>RoundRobin</Algorithm>
      <Server name="orders-1" />
      <Server name="orders-2" />
      <MaxFailures>5</MaxFailures>
      <ServerUnhealthyResponse>
        <ResponseCode>500</ResponseCode>
        <ResponseCode>502</ResponseCode>
        <ResponseCode>503</ResponseCode>
      </ServerUnhealthyResponse>
    </LoadBalancer>
    <Path>/orders</Path>
    <HealthMonitor>
      <IsEnabled>true</IsEnabled>
      <IntervalInSec>5</IntervalInSec>
      <TCPMonitor>
        <ConnectTimeoutInSec>10</ConnectTimeoutInSec>
      </TCPMonitor>
    </HealthMonitor>
  </HTTPTargetConnection>
</TargetEndpoint>
```

Enabling a health monitor requires `<MaxFailures>` greater than 0, and the documentation
recommends both together. Deploy to `test` first and confirm failover works there. This
changes live traffic routing, so it needs authorization and a rollback plan.

#### Verification

Stop one node and confirm requests succeed via the other, then restore it and confirm
traffic distributes again. Separately, make one node return 500 and confirm it leaves
rotation once the threshold is reached. Test both failure modes separately, since a stopped
node and a 500-returning node exercise different settings.

Note that the documentation says individual server failures that trigger a failover are not
displayed in Trace sessions; use Cloud Logging to observe failover events.

#### Common incorrect answers

Raising `<MaxFailures>` alone. Failover still will not trigger for a 500 unless 500 is
classified.

Adding a retry policy to the proxy. That retries at a different layer and does not mark a
server unhealthy.

Assuming load balancing distributes but does not fail over, so nothing is wrong. The
configuration explicitly asked for failover behavior that is disabled by default.

Writing `<Algorithm>weightedRoundRobin</Algorithm>` or a `leastConnectionsWithHealthCheck`
variant. Neither exists. The only documented algorithm values are `RoundRobin`, `Weighted`,
and `LeastConnections`, and `RoundRobin` is the default.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says load balancing is not failover | Finds MaxFailures | Finds both MaxFailures and 500 classification |
| Diagnostic method | Adds retries | Reads target config | Reads both settings and separates failure modes |
| Safety | Changes prod config | Suggests the change | Tests in test env first with rollback plan |
| Verification | None | Tests one mode | Tests both failure modes |

#### Critical failures: changing only MaxFailures and declaring the problem solved.

#### References

- Load balancing across backend servers:
  <https://cloud.google.com/apigee/docs/api-platform/deploy/load-balancing-across-backend-servers>
- MaxFailures antipattern:
  <https://cloud.google.com/apigee/docs/api-platform/antipatterns/load-balancing-maxfailures>

---

### MED-04. Cached responses are stale and nobody can reproduce it

#### Scenario metadata

- ID: MED-04
- Difficulty: medium
- Primary topic: response caching
- Secondary topics: cache keys, upstream data freshness
- Product: Apigee or hybrid
- Origin: synthetic, constructed from verified caching behavior
- Versions: checked 2026-10-11
- Evaluation objectives: caching is a strong hypothesis, but the agent must verify what
  the cache key actually is before recommending cache changes. The element that builds
  the key is `<CacheKey>` with `<KeyFragment>` children, not `<Key>`, and two official
  pages document the `Exclusive` prefix differently, so neither the element name nor the
  expanded key string should be assumed
- Skills expected: apigee-support-core

#### Initial support ticket

> Users occasionally see old pricing data for a few minutes after we update it upstream.
> We think it is the Apigee cache. Can you tell us how to turn it off?

#### Initial evidence

A ResponseCache policy on the response path with a short `<TimeoutInSeconds>` inside
`<ExpirySettings>`. The upstream pricing service updates about once every ten minutes.
Users report a window of a few minutes during which data is stale.

#### Expected investigation

The agent should treat "it is the cache" as a hypothesis, not a conclusion, and establish
what the cache key includes. A cache that keys on the wrong components can serve one
user's response to another, which is a different and more serious problem than staleness.

#### Diagnostic evidence

The cache key is composed from the `<CacheKey>` element and its `<KeyFragment>` children.
The only fragment here is the request URI, so nothing in the key varies by caller or by
pricing version:

```xml
<ResponseCache async="false" continueOnError="false" enabled="true" name="Response-Cache-1">
    <DisplayName>Response Cache 1</DisplayName>
    <CacheKey>
        <KeyFragment ref="request.uri" />
    </CacheKey>
    <Scope>Exclusive</Scope>
    <ExpirySettings>
        <TimeoutInSeconds>300</TimeoutInSeconds>
    </ExpirySettings>
    <CacheResource>pricing_cache</CacheResource>
</ResponseCache>
```

Two different tenants hitting the same URL share a cache entry.

ResponseCache has no `<Key>` element. That name belongs to `<Algorithms>` in the
GenerateJWT and VerifyJWT policies, where it names the key algorithm, not a cache
fragment. An agent that writes or searches for `<Key>` in this policy is reading the
wrong reference. The documented ResponseCache elements are `<DisplayName>`, `<CacheKey>`
with its `<Prefix>` and `<KeyFragment>` children, and `<Scope>`.

The two official pages also disagree about what an `Exclusive` scope puts in front of
the fragment, and the disagreement matters for this ticket. The ResponseCache policy
reference gives the form as
`orgName__envName__apiProxyName__proxy|TargetName__[serializedCacheKey]`, with the
example `apifactory__test__weatherapi__default__apiAccessToken` and no revision number.
Working with cache keys gives the form as
`orgName__envName__apiProxyName__deployedRevisionNumber__nameof(proxyEndpoint|targetEndpoint)__[serializedCacheKey]`,
with the example `mycompany__prod__weatherapi__16__default__hello__world`, which
carries revision 16. Both pages agree that `Exclusive` is the default `<Scope>` value
and that a `<Prefix>` inside `<CacheKey>` supersedes the scope value.

An agent must not quietly pick one. Which of the two forms is implemented determines
whether a newly deployed revision starts from an empty cache or inherits the previous
revision's entries. That follows from reading the two forms against each other; neither
page states it outright, so it is an inference and not a documented guarantee. Either
way, the honest answer attributes the key form to the page it came from, and a question
about whether a deploy clears the cache cannot be settled from documentation alone. It
has to be tested against the running proxy.

Separately, the upstream confirms its own cache holds pricing for up to five minutes.

#### Ground-truth resolution

Two contributors, and the ticket only names one.

The Apigee cache with a short expiry contributes directly to the staleness window.

The upstream service has its own cache with a five-minute TTL, which alone accounts for the
observed window. Turning off the Apigee cache would not reduce it below five minutes.

Separately, the cache key does not vary by caller, so responses may be shared across
tenants that should see different pricing. This is a correctness risk that nobody has
noticed yet, and it is more serious than the staleness being reported.

#### Correct remediation

Do not disable the cache reflexively. First establish whether the staleness is dominated
by the upstream cache by comparing response times and content across the boundary.

Then widen the cache key so it varies by the inputs that actually change the response,
which here means tenant identity and any pricing version. Add `<KeyFragment>` children
to the existing `<CacheKey>`; the documented composition rules are in Working with cache
keys, so build the key from those rules rather than inventing an expression:

```xml
<CacheKey>
    <KeyFragment ref="request.uri" />
    <KeyFragment ref="request.header.x-tenant-id" />
    <KeyFragment ref="request.header.x-pricing-version" />
</CacheKey>
```

Leave `<Scope>Exclusive</Scope>` alone. Setting a `<Prefix>` would be a real change to the
namespace rather than a widening of the key, and it would remove the org, environment, and
proxy names from the prefix.

Changing the key changes what existing entries are read as, so entries written under the
old key become unreachable rather than being invalidated. Deploy to `test` first and let
the old entries expire on their own schedule.

Read the actual cache key off the `responsecache.{policy_name}.cachekey` read-only
variable rather than reasoning about it, since the two official pages disagree on the
`Exclusive` prefix form.

#### Verification

Change pricing upstream and measure end-to-end staleness with the proxy cache enabled and
disabled, so the contribution of each layer is measured rather than argued. Then confirm
two tenants with different pricing see different cached entries, which is the check that
catches the key problem.

#### Common incorrect answers

Setting `<TimeoutInSeconds>` to 0 and calling it done. That removes the Apigee
contribution and leaves the upstream five-minute cache untouched.

Assuming the cache key is safe because the URL is in it. URL-keyed caches still cross
tenant boundaries.

Naming `<Key>` as the ResponseCache element that holds the key. That element belongs to
`<Algorithms>` in the JWT policies and does not exist in ResponseCache.

Quoting one `Exclusive` prefix form as settled fact. The two official pages differ on
whether the deployed revision number appears in it.

Claiming the cache is definitely the cause. The evidence supports a shared contribution.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Disables cache | Attributes to cache | Identifies both layers and the key defect |
| Diagnostic method | Acts immediately | Suggests key review | Inspects the `<CacheKey>` fragments and the upstream TTL |
| Safety | Disables in prod | Suggests change | Measures before changing |
| Verification | None | Checks freshness | Measures per layer and checks tenant separation |

#### Critical failures: disabling the cache without measuring the upstream contribution;
missing the cross-tenant cache key defect.

#### References

- ResponseCache policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/response-cache-policy>
- Working with cache keys:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/working-cachekeys>

---

### MED-05. Key value map updates are not visible everywhere

#### Scenario metadata

- ID: MED-05
- Difficulty: medium
- Primary topic: key-value maps
- Secondary topics: caching, eventual consistency, secrets
- Product: Apigee or hybrid
- Origin: documented
- Versions: checked 2026-10-11
- Evaluation objectives: the single-node cache refresh is documented for the
  KeyValueMapOperations policy `PUT`, not for a Management API update. The agent has to
  establish which write path is in use before quoting it, and must notice that the debugging
  suggestion in common answers leaks secrets
- Skills expected: apigee-support-core

#### Initial support ticket

> We rotate an API endpoint URL in a key-value map about once a week. After the update,
> requests fail from some regions for a few minutes and then recover. Is the key-value map
> corrupt?

#### Initial evidence

The new value is written at runtime by a `PUT` operation in a KeyValueMapOperations policy,
with `<ExpiryTimeInSecs>` set to 60 on the policy. A policy reads the value at runtime. Some
requests receive an empty or stale value immediately after the update.

#### Expected investigation

The agent should look for documented propagation behavior before suspecting corruption, and
should first establish which write path is in use, because the documented single-node refresh
is specific to the policy.

#### Diagnostic evidence

Repeating the `PUT` and immediately reading from different runtime nodes returns different
values for roughly as long as the configured `<ExpiryTimeInSecs>`.

#### Ground-truth resolution

The map is not corrupt. The documented behaviour for the policy is that a `PUT` "will only
refresh the cache in the single runtime node that services the request. To refresh the cache
in each distributed runtime node, use the `<ExpiryTimeInSecs>` element to specify refresh
intervals for each node." Other nodes pick up the new value when their own cache entry
expires. The pattern of brief partial failure after an update follows from that.

The scoping matters and is easy to get wrong. This is documented for the KeyValueMapOperations
policy, not for the management path. The same reference states that "Updating a KVM with the
Apigee UI or API does not reset the KVM cache", so a Management API write has no
single-node refresh to explain anything. An agent that applies the policy behaviour to a
Management API update is quoting a real fact about the wrong thing.

The operational cost is real even when the cause is benign: a rotating endpoint is briefly
serving different values to different nodes.

#### Correct remediation

Treat the update as eventually consistent. Shorten `<ExpiryTimeInSecs>` on the read side if
the visibility window is too wide, and stage the new value alongside the current one if a
hard cutover is needed: switch traffic to the new key and retire the old key after a window
longer than the observed propagation delay.

There is no policy-level way to flush the KVM cache across nodes. The documentation is
explicit that there is no mechanism to invalidate a cached entry across all runtime nodes
from a single policy execution, and that attempting to expire a value by `PUT`ing a
placeholder overwrites the stored value permanently. Staging with two keys is the supported
pattern.

For secrets, all KVM values are encrypted at rest; what exposes them is the variable name.
The `private.` prefix is what keeps a retrieved value out of Debug sessions. Without it the
value still comes back decrypted and appears in cleartext in any Debug session, with no
error raised.

#### Verification

Update, then poll the value from every runtime node and record how long convergence takes
against the configured `<ExpiryTimeInSecs>`. Repeat several times to see the worst case
rather than a single good run.

#### Common incorrect answers

Recreating the map. That destroys the current value and does not address propagation.

Telling them to enable debug and print the value. For a value read into a variable without
the `private.` prefix, that prints the value in cleartext into debug output.

Restarting runtimes to force cache refresh. Disruptive, and unnecessary given the
documented per-node expiry behaviour.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says map is corrupt | Identifies per-node cache expiry | Names the single-node `PUT` refresh and scopes it to the policy |
| Diagnostic method | Recreates map | Suggests polling | Establishes the write path, then polls per node |
| Safety | Recreates or restarts | Suggests shortening `ExpiryTimeInSecs` | Stages with a cutover window, avoids the placeholder trick |
| Verification | None | Checks once | Measures worst case across nodes |

#### Critical failures: applying the single-node `PUT` refresh to a Management API update;
recommending debug output of a KVM value without flagging the `private.` prefix.

#### References

- Key-value maps:
  <https://cloud.google.com/apigee/docs/api-platform/cache/key-value-maps>
- KeyValueMap operations policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/key-value-map-operations-policy>

---

### MED-06. Latency jumped and nobody knows which layer moved

#### Scenario metadata

- ID: MED-06
- Difficulty: medium
- Primary topic: latency diagnosis
- Secondary topics: tracing, timeouts, measurement
- Product: Apigee or hybrid
- Origin: synthetic
- Versions: checked 2026-10-11
- Evaluation objectives: separate gateway processing time from upstream time using
  evidence, not assumption; guessing "it's the network" is the failure mode
- Skills expected: apigee-support-core

#### Initial support ticket

> p95 latency on our search API went from 180ms to 900ms overnight. No deploys. Can you
> tell us if it's Apigee?

#### Initial evidence

API Monitoring shows request latency up. No revision changes in the last week. The
upstream team has not yet been contacted.

#### Expected investigation

The agent should not attribute the change to Apigee or to the upstream without measuring.
It should request a trace and the target's own response time measured from outside Apigee.

#### Diagnostic evidence

A trace shows the target endpoint step consuming about 820ms. A direct request to the
upstream from outside Apigee, using the same path and payload, returns in about 800ms.
Step names are customer-defined and differ between proxies, so read the step by its elapsed
time rather than by a hardcoded label.

#### Ground-truth resolution

The latency is upstream. Apigee's own processing in the trace is small, and an independent
measurement of the target reproduces the delay without Apigee in the path.

The overnight timing and the lack of deploys are consistent with an upstream change, but
they are not the proof. The measurement is.

#### Correct remediation

Route this to the upstream team with the trace excerpt and the external measurement, since
that is the evidence they need. No Apigee change is indicated.

Worth noting for the future that timeouts configured against the old latency may now fire
intermittently, which would produce a second, confusing symptom.

#### Verification

Confirm the target's external response time returns to baseline. Then confirm Apigee's
measured processing time, which should be small, and confirm no new timeout faults appear
in API Monitoring.

#### Common incorrect answers

Raising the Apigee timeout. That masks the upstream delay rather than fixing it and makes
requests hang longer.

Adding a cache to hide the latency, which trades a latency problem for a staleness problem.

Claiming "no deploys, so it must be the upstream". The absence of a deploy eliminates one class of
cause. It does not establish the other, and the remaining candidates still have to be
tested.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Blames Apigee | Suspects upstream | Attributes with measured evidence |
| Diagnostic method | Guesses | Requests a trace | Requires trace plus external measurement |
| Safety | Raises a timeout or adds a cache as the fix, changing production behaviour on a guess | Recommends a change without saying where it would be tested | Routes the investigation upstream and changes nothing in the proxy until the measurements say so |
| Verification | None | Checks p95 | Checks target baseline and Apigee share |

#### Critical failures: recommending a timeout increase as the primary remedy; attributing
cause without measurement.

#### References

- Trace and debug:
  <https://cloud.google.com/apigee/docs/api-platform/debug/trace-overview>
- API Monitoring fault codes:
  <https://cloud.google.com/apigee/docs/api-monitoring/fault-codes>

---

### MED-07. Deployment succeeds on hybrid but the runtime never applies it

#### Scenario metadata

- ID: MED-07
- Difficulty: medium
- Primary topic: hybrid deployment propagation
- Secondary topics: IAM, control plane to runtime sync
- Product: Apigee hybrid
- Origin: documented
- Versions: checked 2026-10-11
- Evaluation objectives: the ticket reads like Apigee X, where a successful deployment
  call is close to the end of the story. On hybrid it is one of at least four separate
  steps, and the usual first guess, network or runtime, is wrong
- Skills expected: apigee-support-core

#### Initial support ticket

> We onboarded a second organization on our hybrid install and created its first
> environment. We deployed our proxy to it. The deployment call succeeded. Requests to
> the new environment hostname return 404. Our original organization is completely
> unaffected. Please advise.

#### Initial evidence

The deployment list for the new organization shows the revision deployed to `prod`. The
same proxy revision serves traffic normally in the original organization. Nothing was
redeployed there, and both organizations run in the same Google Cloud project.

#### Expected investigation

On hybrid the control plane and runtime plane are separate, and the agent should treat
"the deployment API returned success" as only the first of several steps rather than as
completion. The documented steps are: the revision is saved, the Synchronizer pulls the
contract, the Message Processor applies it, and the Watcher reports status.

#### Diagnostic evidence

The Message Processor log for the new organization contains no line of the form
`Switched to newer version N from version M`, which is the documented marker that the
MP applied a newer contract version. Reading the sync authorization for the new
organization returns no identities. The same service account that is registered for the
original organization holds the Apigee Synchronizer Manager role, so the identity was
available and was simply never registered against the new organization.

#### Ground-truth resolution

The Synchronizer has no registered identity for this organization, so it never fetches
artifacts for it and the Message Processor never receives a contract to apply. Nothing
is wrong with the proxy, the revision, or the runtime.

The documented requirement is that `setSyncAuthorization` is called once per hybrid
organization, against `organizations/{org}`, listing the service account that holds the
Apigee Synchronizer Manager role. A second organization on the same cluster needs its
own call; the registration made for the first organization does not carry over. That
silence is what makes this hard to see from the outside, and it is why a ticket that
looks like a routing problem is really an authorization one.

#### Correct remediation

Call `setSyncAuthorization` for the new organization with the Synchronizer manager
service account, after confirming that account holds the Apigee Synchronizer Manager
role. Confirm the grant before calling the API, since the API will accept an identity
that lacks the role.

This is an IAM change in Google Cloud. It is reversible, and it is scoped to the one
organization being added, so confirm which service account the platform team intends to
use.

#### Verification

Confirm the deployment reaches `READY` and that the contract version line in the pod log changes, then send a request. The reliable check is
the `Switched to newer version N from version M` line appearing in the runtime pod log
for that organization, not the Management API response, because on hybrid the API cannot
tell you whether the runtime applied anything.

Also confirm the original organization still serves, since the same service account is
now registered against two organizations.

#### Common incorrect answers

Redeploying the proxy. It already deployed, and the contract is not being pulled.

Investigating DNS or the environment group. The 404 has nothing to do with address
resolution here, and the environments that share the group are working.

Replacing the runtime pods. A restart does not grant the Synchronizer permission.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Product and version | Gives an Apigee X answer and checks only the Management API | Suspects hybrid | Names the four deployment steps and where the failure can sit in them |
| Technical correctness | Redeploys | Looks at runtime | Identifies that sync authorization is per organization |
| Diagnostic method | Checks DNS | Reads pod logs | Reads pod logs for the contract version line and reads sync authorization |
| Quality of next step | Redeploy | Restarts pods | Registers the identity against that organization |
| Verification | None | Waits and retries | Waits for the contract version line to change, then checks the other organization too |
| Safety | Recommends the Management API call with no role check | Says to verify the role but not the call | Checks the identity holds `Apigee Synchronizer Manager` before calling, since the call succeeds for an identity that lacks it |

#### Critical failures: recommending a redeploy as the fix; treating a successful Management
API call as proof the runtime applied the change; claiming `setSyncAuthorization` is
configured per environment.

#### References

- Synchronizer service account access, including the per-organization
  `setSyncAuthorization` and `getSyncAuthorization` calls, and the
  `Apigee Synchronizer Manager` role the identity must hold:
  <https://cloud.google.com/apigee/docs/hybrid/latest/synchronizer-access>
- Runtime logs, including the `Switched to newer version N from version M` contract version
  line that this scenario's whole discriminator rests on:
  <https://cloud.google.com/apigee/docs/hybrid/latest/runtime-logs>
- Service configuration, for the Watcher's role in fetching deployment status from the
  Message Processors:
  <https://cloud.google.com/apigee/docs/hybrid/latest/service-config>

---

### MED-08. Mutual TLS broke after a certificate authority renewal

#### Scenario metadata

- ID: MED-08
- Difficulty: medium
- Primary topic: mutual TLS
- Secondary topics: certificates, both directions of the connection
- Product: Apigee or hybrid
- Origin: documented
- Versions: checked 2026-10-11
- Evaluation objectives: check the extended key usage before anything else; the renewed
  certificate is almost certainly missing `clientAuth`
- Skills expected: apigee-support-core, references/security.md

#### Initial support ticket

> Our CA renewed our client certificates last week. Since then mutual TLS fails in both
> directions. We replaced the certificates exactly as before. What changed?

#### Initial evidence

Northbound client-to-Apigee fails and southbound Apigee-to-backend fails. The
configuration is unchanged. The new client certificates come from the same CA.

#### Expected investigation

The timing and the two-sided failure both point at the certificate itself. The agent
should inspect the extended key usage before looking at chains, protocols, or keystore
state.

#### Diagnostic evidence

Inspecting the new certificate shows no `clientAuth` extended key usage in the EKU
extension. The previous certificate had it. The CA has discontinued issuing it.

#### Ground-truth resolution

Mutual TLS requires the `clientAuth` extended key usage on the client certificate. Without
it, mTLS fails in both directions, client to Apigee and Apigee to backend, because the
same class of certificate is used on both sides.

Nothing about the Apigee configuration changed. The renewal dropped a property that the
old certificate happened to carry.

#### Correct remediation

Have the CA reissue client certificates including the `clientAuth` extended key usage.
This is a certificate request change on the customer's side, not an Apigee change.

Keep the old certificates until the new ones are confirmed working in both directions,
since the two-sided failure means a partial test proves nothing.

#### Verification

Confirm the EKU on the new certificate before deploying it anywhere. Then test northbound
and southbound independently, because a northbound pass does not imply a southbound pass.

#### Common incorrect answers

Re-uploading the certificate to the keystore. It is already correct, and the defect is in
the certificate's contents.

Setting `IgnoreValidationErrors`. That does not address extended key usage.

Checking the truststore for the CA. Trusting the CA is necessary and already satisfied;
the client certificate is the problem.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Re-uploads certificate | Identifies certificate issue | Names `clientAuth` EKU as the cause |
| Diagnostic method | Checks truststore | Inspects certificate | Inspects the EKU extension specifically |
| Handling of uncertainty | Assumes chain problem | Hedges | States what is confirmed and what to check |
| Verification | None | Tests one side | Tests both directions separately |

#### Critical failures: recommending `IgnoreValidationErrors` as the fix.

#### References

- API proxy configuration reference, TLS section:
  <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>
- Configuring TLS:
  <https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls>

---

### MED-09. Bursts are rejected by a Quota policy that is enforcing correctly

#### Scenario metadata

- ID: MED-09
- Difficulty: medium
- Primary topic: Quota versus SpikeArrest
- Secondary topics: rate limiting, client behavior, error codes
- Product: Apigee or hybrid
- Origin: documented
- Versions: checked 2026-10-11
- Evaluation objectives: the team is using the wrong policy for the job; the documented
  guidance is explicit about which handles bursts. The observed fault code is
  `policies.ratelimit.QuotaViolation`, not `policies.ratelimit.SpikeArrestViolation`, so
  the evidence names Quota and the answer must not quietly promote it to a spike problem
- Skills expected: apigee-support-core

#### Initial support ticket

> Our API rejects bursts with errors that sometimes look like a quota violation. We have
> a Quota policy set to 100 per minute per client. Clients retry and sometimes get through.
> Is the quota miscounting?

#### Initial evidence

A Quota policy with a one-minute interval. During bursts, clients receive
`policies.ratelimit.QuotaViolation` with HTTP 500. Between bursts, success rate is normal.

#### Expected investigation

The agent should check whether the observed behavior is a miscount or a correctly
enforced limit being hit. The documented guidance says not to use the Quota policy to
shield against overall traffic spikes, and points to SpikeArrest for that.

The evidence carries two separate status claims and the agent has to hold them apart
rather than pick the one it expects. The Quota policy reference's runtime error table
maps `policies.ratelimit.QuotaViolation` to HTTP `500`. The same page closes with a note
that when incoming requests exceed the thresholds set by Quota or SpikeArrest, the system
returns `429 Too Many Requests`, and the Quota/SpikeArrest comparison table lists `429`
as the status code when a Quota limit is reached. A `429` in this position would not by
itself change the diagnosis, because it would still be a correctly enforced limit, and
the fault body names Quota rather than SpikeArrest either way. What it does change is
what the team is looking at: if callers are seeing a 500 where they expect a 429, that is
a question about how the Quota fault is being surfaced, and it is worth asking before
the remediation is written.

#### Diagnostic evidence

Counting requests per client per minute shows the quota is enforced accurately. A retry
issued inside the same window is rejected as well, because the documented behavior is that
requests are rejected until the counter resets. Only retries that land after the window
boundary succeed.

#### Ground-truth resolution

The quota is not miscounting. It is enforcing correctly, and the burst behavior it
produces is exactly the documented consequence.

The real issue is policy choice. The documented recommendation is to use SpikeArrest for
spike protection and Quota for longer-window allowances, and not to use Quota to shield
against spikes. A retry that lands after the counter resets succeeding, and one that lands
inside the window being rejected, is the documented behavior rather than a flaw.

The fault code is the evidence for which policy is firing. `QuotaViolation` is the Quota
policy's error and `SpikeArrestViolation` is SpikeArrest's, and this proxy has no
SpikeArrest policy, so nothing in the evidence supports describing the observed
rejections as spike rejections. The 500 in the response body is the status the Quota
policy's own runtime error table documents for this fault. Whether the team should also
expect `429` at the caller is a separate, open question raised by the note on the same
page, and it does not move the diagnosis.

#### Correct remediation

Move the allowance to a longer window and put the bursts in SpikeArrest. The comparison
chart puts Quota at "longer time intervals like days, weeks, or months" and SpikeArrest at
"seconds or minutes", so the existing one-minute Quota sits in SpikeArrest's column and
cannot stay as the sustained allowance. Change that Quota's interval to the window the
commercial terms actually imply, and add SpikeArrest to shed the bursts.

SpikeArrest has no `rateLimit` element and no `timeWindow` element. Its
documented children are `<DisplayName>`, `<Identifier>`, `<MessageWeight>`, `<Rate>` and
`<UseEffectiveCount>`, and the whole rate is set by one required child:

```xml
<SpikeArrest name="SA-Burst-30ps">
  <Rate>30ps</Rate>
  <UseEffectiveCount>true</UseEffectiveCount>
</SpikeArrest>
```

A `<Rate>` value is an integer followed by `ps` or `pm`, such as `30ps`, `5ps` or `12pm`,
and the integer must be a positive, non-zero value. The suffix is the only window control
the policy offers: `ps` limits per second, `pm` limits per minute. A short burst window is
therefore expressed by picking `ps` with a small integer, not by setting a separate window
attribute.

Choose `<UseEffectiveCount>` deliberately rather than taking the default. The documented
default is `false`, which selects the smoothing algorithm, and the same page states that
rate smoothing is not supported for Apigee organizations and that they should set the
element to `true`. `true` selects a sliding window and synchronizes counts across message
processors within a region. Either way, do not quote a "documented default" for `<Rate>`:
it has none, and `<Rate>` is Required.

Order the two policies as the comparison page directs: SpikeArrest first in the
ProxyEndpoint Request PreFlow, then Quota, so bursts are shed before they consume
longer-term quota allowance.

Test in a non-production environment, because both policies change what traffic is
accepted.

#### Verification

Replay a burst pattern in test and confirm burst traffic is shed by SpikeArrest while the
long-window quota still permits the intended allowance. Confirm the two policies are not
fighting by checking counters for both.

#### Common incorrect answers

Raising the quota limit to reduce rejections. That permits more burst traffic and does
not address the window behavior.

Telling them to disable retries. Retries are the client's rational response to a rate
limit.

Adding a second Quota policy alongside the one-minute one and leaving that one in place.
Two Quota policies do not compose into burst protection, and the fix is to change the
existing interval rather than to stack another policy on top of it.

Naming `rateLimit` or `timeWindow` as SpikeArrest elements. Neither exists. The rate is the
body of `<Rate>` and must carry a `ps` or `pm` suffix, such as `<Rate>30ps</Rate>`.

Describing the observed rejections as spike rejections because the traffic is bursty. The
proxy has no SpikeArrest policy and the fault body is
`policies.ratelimit.QuotaViolation`; the burst shape is what makes a correctly enforced
Quota visible, not evidence that a different policy is firing.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says the quota is miscounting, or calls the observed fault a spike rejection | Identifies burst behavior | Explains enforcement is correct and policy choice is wrong |
| Diagnostic method | Raises limits | Suggests SpikeArrest | Verifies counts before concluding |
| Safety | Changes prod limits | Adds SpikeArrest | Tests in test env first |
| Policy configuration | Invents elements or quotes a default `<Rate>` | Names SpikeArrest without a concrete element | Uses `<Rate>` with a `ps`/`pm` value and sets `<UseEffectiveCount>` deliberately |
| Verification | None | Checks rejections | Checks both policies' counters |

#### Critical failures: recommending a higher quota as the primary fix; writing a
`rateLimit` or `timeWindow` element into a SpikeArrest policy.

#### Not a critical failure: raising the `500` versus `429` question. The Quota policy
reference documents `500` in its runtime error table and `429` in a closing note on the
same page, so noticing that the observed status is not the one an agent would expect is
correct reading of the evidence rather than a dispute with the scenario. An answer that
keeps the diagnosis intact and asks how the Quota fault is being surfaced is the correct
answer; stopping there without completing the remediation is incomplete, not wrong.

#### Not a critical failure: noting that `<Distributed>` and `<Synchronous>` both default
to `false`, and that the Quota policy page says you might exceed the quota on that
configuration. The evidence does not disclose either element, so an agent that raises the
counter-distribution caveat has read the reference correctly and must not be scored below 4
on Technical correctness for it. The caveat does not rescue "the quota is miscounting",
because the diagnostic evidence says counting per client per minute is accurate; treat the
two as separable claims, as the scenario's own analysis of the status code does.

#### References

- Quota policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
- Comparing Quota and SpikeArrest:
  <https://cloud.google.com/apigee/docs/api-platform/develop/comparing-quota-and-spike-arrest-policies>
- SpikeArrest policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy>

---

### MED-10. Token works against one API and fails against another

#### Scenario metadata

- ID: MED-10
- Difficulty: medium
- Primary topic: OAuth 2.0
- Secondary topics: API products, fault handling, response generation
- Product: Apigee or hybrid
- Origin: documented
- Versions: checked 2026-10-11
- Evaluation objectives: find the fault rule difference between policies; the token is
  fine and the handling differs
- Skills expected: apigee-support-core, references/security.md

#### Initial support ticket

> Our mobile app gets a clean 401 on one API and a confusing 500 on another, using the
> same token. Both use OAuthV2. Why is the behavior different?

#### Initial evidence

The team reports both proxies use OAuthV2 with `VerifyAccessToken`. One returns 401, the
other returns 500. The token is expired.

#### Expected investigation

The agent should recall that status codes vary by policy rather than by the underlying
condition. Expired tokens return 401 from `VerifyAccessToken` and 500 from
`GetOAuthV2Info` or `SetOAuthV2Info`. Both proxies turn out to carry the info policies, so
the difference has to come from somewhere else.

#### Diagnostic evidence

A trace of the failing proxy has no `VerifyAccessToken` step at all. The first token policy
on that path is `GetOAuthV2Info`, and the failure occurs there. The working proxy's trace
shows `VerifyAccessToken` running before the info policies, and failing.

#### Ground-truth resolution

The token is expired, which is a single condition. The status differs because the two
proxies use different policies to handle it: `VerifyAccessToken` surfaces 401, while
`GetOAuthV2Info` and `SetOAuthV2Info` surface 500 for an expired token.

An expired token cannot pass `VerifyAccessToken`, so a trace showing that step succeeding
would contradict the ground truth rather than explain the difference. What the trace
establishes is which policies are on each path, and that is what makes the status
difference legible.

The client's experience is consistent, not contradictory, once you know the status codes
are policy-specific.

#### Correct remediation

Treat both as the same condition in client-facing handling, keyed on `errorcode` rather
than on status. Normalize the client to handle 401 and 500 for token problems, or align
the two proxies to use the same policies.

The fault rules matter too: catching `invalid_client` and `InvalidClientIdentifier` covers
one condition that splits on `<GenerateResponse>`.

#### Verification

Use an expired token against both proxies and confirm both are treated as auth failures
after the fix. Then confirm a valid token produces 200 on both.

#### Common incorrect answers

Calling the 500 a server fault and alerting on it. It is an auth failure with an
inconsistent status.

Telling them to regenerate tokens client-side, which does not address why two proxies
disagree.

Concluding one of the two proxies is simply broken, without reporting that the failing
proxy has no `VerifyAccessToken` step. That gap is a real finding in its own right: a
proxy protecting an API with only an info policy is not verifying tokens at all, which is
a security gap independent of the 500.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Calls it a server fault | Notes status differs | Identifies policy-specific statuses |
| Diagnostic method | Compares configs | Reads trace | Identifies which policy produced the status |
| Quality of next step | Rotates tokens | Normalizes client | Normalizes on errorcode and aligns proxies |
| Verification | None | Retests | Tests expired and valid on both |

#### Critical failures: recommending escalation as a platform bug without checking which
policy produced the status.

#### References

- OAuthV2 policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>
- GetOAuthV2Info policy, which documents the 500 for an expired token:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/get-oauth-v2-info-policy>
- SetOAuthV2Info policy, same code at 500:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/set-oauth-v2-info-policy>
- OAuth HTTP status codes, deprecated but informative:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauth-http-status-code-reference>

---

### MED-11. Everything works in test and fails in production

#### Scenario metadata

- ID: MED-11
- Difficulty: medium
- Primary topic: environment-specific configuration
- Secondary topics: deployment, secrets, comparison discipline
- Product: Apigee or hybrid
- Origin: synthetic
- Versions: checked 2026-10-11
- Evaluation objectives: the agent must diff environments rather than assume the
  environments are identical, and must get the direction right: the failing environment
  is the one missing the entry, not the one holding a well-formed value
- Skills expected: apigee-support-core

#### Initial support ticket

> Identical proxy bundle, identical policies. Works in `test`, fails in `prod` with 500.
> We deploy the same artifact to both. Why would production behave differently?

#### Initial evidence

Same bundle deployed to both. Production returns 500 with an error body. Test returns 200
for the same request.

#### Expected investigation

The bundle being identical does not mean the environments are. The agent should diff
environment-scoped configuration, and should start with the things that are configured
outside the bundle.

#### Diagnostic evidence

A key-value map lookup differs, and the difference is an absent key rather than a
differing value: `prod` has no `orders.timeout` key at all, while `test` has it set to
`30`. The policy is the same in both environments:

```xml
<KeyValueMapOperations name="GetOrdersTimeout" mapIdentifier="orders-config">
  <Get assignTo="private.orders.timeout" index="1">
    <Key>
      <Parameter>orders.timeout</Parameter>
    </Key>
  </Get>
  <Scope>environment</Scope>
</KeyValueMapOperations>
```

A JavaScript policy reads `private.orders.timeout` and sets the target request timeout from
it. In `test` the lookup returns `30` and the timeout is set. In `prod` there is nothing to
retrieve, so nothing is assigned to the `assignTo` variable, and the script is left holding
no timeout value, which is what produces the 500.

#### Ground-truth resolution

The environments differ in a map entry that lives outside the bundle, so deploying the same
artifact to both produces different behavior. The bundle is not the variable.

The direction matters, and getting it backwards is the whole bug. `prod` is the failing
environment and `prod` is the one missing the key. A well-formed value cannot cause an
unresolved variable; a missing one does. `<Get>` documents itself as retrieving the value
for the key specified and assigning it to the `assignTo` variable, so with no entry for
`orders.timeout` in the production map, that variable is never assigned and the downstream
script reads nothing. In `test` the same policy retrieves `30` and the request succeeds.

The `<Scope>environment</Scope>` setting is why this is possible at all: entries are scoped
to an environment, so the two environments can hold different maps without anything being
mis-deployed. An identical bundle is not an identical environment.

This is the general shape of most "works in one environment" tickets: the proxy config is
deployed identically and something environment-scoped is not.

#### Correct remediation

Decide what production is supposed to do, because "add the key" and "stop depending on the
key" are both defensible and they are different changes. The first is to populate the map
entry in `prod` through a documented, repeatable mechanism rather than by hand, so the
value is visible in source control and survives the next deployment.

The second is often better: a default in the policy that handles a missing variable makes
the proxy behave the same in both environments whether or not the key is present, and it
removes a per-environment value that has to be kept in sync. Choose one deliberately
rather than letting the difference persist unnoticed.

If the map entry is left environment-scoped and missing, record that as a known difference
rather than an accident.

#### Verification

Confirm the same request behaves identically in both environments. Then diff environment
configuration deliberately and record what differs, because there are usually more
differences than the one that broke.

#### Common incorrect answers

Redeploying the production revision. The bundle is already identical.

Copying the `test` map into `prod` by hand. That fixes today and drifts tomorrow.

Reading the well-formed `30` as the problem because it is a string rather than an integer.
A value that is present and well-formed cannot leave a variable unresolved. The failing
environment is the one with no key at all.

Concluding that the environments must be identical, and therefore that one of them has
been mis-deployed. Nothing in the evidence says they are identical, and the whole
question is whether environment-scoped configuration is the variable.

Blaming the target or the runtime for a difference that is between two control-plane
configurations, neither of which is in the bundle.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Redeploys | Suspects env config | Identifies the missing map entry in the failing environment |
| Diagnostic method | Compares bundles | Compares env config | Diffs environment-scoped configuration and checks which key is absent |
| Quality of next step | Manual copy | Sets the value | Moves it into a managed configuration path or gives the policy a default |
| Verification | None | Retests | Retests and records remaining differences |

#### Critical failures: recommending repeated manual map edits as the durable fix; blaming
the `30` value in `test` for the production failure.

#### Not a critical failure: stating that the two environments differ. That is the
finding, not a wrong answer. It becomes wrong only when it is turned into a claim that
both environments are broken, or that the difference alone proves a misconfiguration,
which is the opposite of what the evidence supports.

#### References

- Key-value maps:
  <https://cloud.google.com/apigee/docs/api-platform/cache/key-value-maps>
- Environments overview:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/environments-overview>

---

### MED-12. Service callout times out and takes the request with it

#### Scenario metadata

- ID: MED-12
- Difficulty: medium
- Primary topic: service callouts
- Secondary topics: timeouts, fault handling, target configuration
- Product: Apigee or hybrid
- Origin: synthetic
- Versions: checked 2026-10-11
- Evaluation objectives: distinguish the callout's own timeout from the request target's
  timeout, and from each other recognize which is which. They do not look the same on the
  wire: a callout `<Timeout>` expiry fails the policy with HTTP 500, while a target read or
  write timeout surfaces as HTTP 504. Getting that mapping backwards sends the agent to the
  wrong element
- Skills expected: apigee-support-core

#### Initial support ticket

> Our enrichment callout started timing out for about 1% of requests. The enrichment
> service is fast. We raised its timeout and it did not help.

#### Initial evidence

A ServiceCallout policy with a configured timeout. Roughly 1% of requests return 500. The
enrichment service's own p95 is under 50ms.

#### Expected investigation

The agent should identify which timeout is firing. Raising the wrong one produces
exactly the "we fixed it and nothing happened" report in the ticket.

#### Diagnostic evidence

The trace shows the ServiceCallout step failing at its configured `<Timeout>` of 200ms. The
policy is named `SC-Enrich` in the customer's bundle; the name is theirs, not an Apigee
convention. The enrichment service's slow requests are long-tail cases, not p95 cases, so p95
looked fine while p99.9 exceeded 200ms.

#### Ground-truth resolution

The callout's own timeout is the one firing. The documented behaviour is that when a
ServiceCallout hits its timeout, an HTTP 500 is returned, the policy fails, and the proxy goes
into an error state. The upstream's p95 being healthy did not rule out a timeout, because
timeouts are tail-sensitive and p95 hides the tail entirely.

The status is what separates this from a target timeout. A target read or write timeout
surfaces as HTTP 504, not 500. Seeing 500 is itself evidence that the callout's own timeout
is the failing one, and an answer that maps callout timeouts to 504 has the mechanism
backwards.

Raising the enrichment service's timeout, as they did, was addressing a different timeout
that was not the failing one.

#### Correct remediation

Decide what should happen when enrichment is slow, because a longer timeout on a
synchronous callout lengthens every affected request. Options are to raise the callout
timeout within a latency budget, to make enrichment non-blocking with a fault rule that
degrades gracefully, or to cache enrichment results.

Handle it in a fault flow rather than letting the callout fault surface as a 500.

#### Verification

Replay slow enrichment requests and confirm the intended behavior, whether that is
succeeding, degrading, or failing fast. Then confirm p99.9 latency, not p95, since p95 is
what hid this in the first place.

#### Common incorrect answers

Raising the callout timeout without a fault rule. That converts timeouts into long
requests.

Adding retries inside the callout, which multiplies the latency under exactly the
conditions where latency is already the problem.

Looking at the enrichment service's dashboard averages rather than its tail.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Raises a timeout blindly | Identifies callout timeout | Names which timeout fires, why p95 misled, and the 500 versus 504 split |
| Diagnostic method | Trusts averages | Reads trace | Reads the failing step in the trace and the status it returned |
| Quality of next step | Raises timeout | Suggests fault flow | Offers degradation with a budget |
| Verification | None | Retests | Tests tail behavior explicitly |

#### Critical failures: recommending a timeout increase with no fault handling; reasoning
from p95 to rule out a tail problem; mapping a callout timeout to HTTP 504 or a target
timeout to 500.

#### References

- ServiceCallout policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/service-callout-policy>
- Handling faults:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/fault-handling>

---

### MED-13. Two conditions produce the same error code

#### Scenario metadata

- ID: MED-13
- Difficulty: medium
- Primary topic: fault rules
- Secondary topics: debugging, fault-string reading
- Product: Apigee or hybrid
- Origin: synthetic, constructed from the documented fault-string format and one
  verified runtime example
- Versions: checked 2026-10-11
- Evaluation objectives: one error code, several causes; the policy name carried inside
  the fault string is the discriminator, not the code and not the description
- Skills expected: apigee-support-core

#### Initial support ticket

> We get a JavaScript policy failure roughly once an hour. Every time it is the same
> `ScriptExecutionFailed`. Two different policies are involved and both look fine. What is
> it failing on?

#### Initial evidence

Two JavaScript policies doing small amounts of work: one parses a JSON body, the other
reads a query parameter list. Roughly one failure per hour, always at peak. Their log
export captures only the `errorcode` column, so "the same error" in their report means the
code, not the full `faultstring` field, which is not recorded at all.

#### Expected investigation

The documented cause of `steps.javascript.ScriptExecutionFailed` is that the policy can
throw many different types of errors, and the fault string is where the detail lives. The
documented fault string is built from the policy name, the error type, the error
description and the source file and line, so it identifies the policy as well as the
failure. The agent should ask for the fault string in full, not just the code, and note
that this is the one case where reading the prose is useful as a diagnostic aid even though
matching on it is fragile.

#### Diagnostic evidence

The full fault strings from two failing requests read:

```
Execution of ParseJSONResponse failed with error: Javascript runtime error: "TypeError: Cannot read property "length" from undefined. (ParseJSONResponse.js:7)"
```

```
Execution of ReadItemList failed with error: Javascript runtime error: "TypeError: Cannot read property "length" from undefined. (ReadItemList.js:11)"
```

The code is identical and so is the inner description. What differs is the policy name and
the source line, which is what says which script to open. On the requests that fail, the
client either sends a body that is an empty array or omits the `items` query parameter. The
first script parses `response.content` with `JSON.parse` and then reads `body[0].length`;
the second reads `request.queryparam.items` and then `.length` on it.

#### Ground-truth resolution

Two unrelated conditions produce the same error code and the same error description. A
malformed body reaches `ParseJSONResponse`, and a request with no `items` query parameter
reaches the other policy. Neither is a timeout, and neither is a bug in Apigee.

The discriminator is not the code and not even the description, both of which are shared.
It is the policy name and source line carried in the fault string. An agent that stops at
`ScriptExecutionFailed` cannot tell the two apart, and will keep fixing whichever policy
it happened to open first.

The correlation with peak traffic is because peak traffic includes proportionally more of
the client traffic that omits the parameter and sends the empty array.

#### Correct remediation

Guard both dereferences, keyed on the policy named in the fault string:

```javascript
// ParseJSONResponse.js
var parsed = context.getVariable("response.content");
var body = [];
if (parsed) {
  try {
    body = JSON.parse(parsed) || [];
  } catch (e) {
    body = [];
  }
}
var first = body.length > 0 ? body[0] : null;
var len = first && typeof first.length === "number" ? first.length : 0;
```

```javascript
// the query-parameter policy
var raw = context.getVariable("request.queryparam.items");
var items = raw ? String(raw).split(",") : [];
```

The parse needs the `try` because the ground truth names a malformed body as one of the
two conditions, and an unguarded `JSON.parse` throws a `SyntaxError` that surfaces as the
same `ScriptExecutionFailed`.

Treat the fault string as a diagnostic aid here while still keying any error handling on
the fault code.

#### Verification

Send requests with and without the parameter, and with an empty array, a populated array,
no body, and a body that is not valid JSON. Confirm all succeed and that behavior for the
well-formed cases is unchanged. Confirm from the trace that the two conditions are now
distinguishable by policy name.

#### Common incorrect answers

Raising the JavaScript timeout, which does not apply to a null dereference.

Treating `ScriptExecutionFailed` as one specific bug and rewriting a single script blind.
The code is shared by two conditions in two policies.

Fixing the one policy named in the first fault string pasted, without noticing that a
second fault string names a different policy. The customer reported a single repeated
error; the log had dropped the field that distinguished them.

Ignoring the fault string because matching on prose is discouraged. It is discouraged for
error handling and useful for diagnosis, and conflating the two is its own error.

Guarding `body.length` but leaving `JSON.parse` bare, which leaves the malformed-body case
throwing the same fault code.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says code is insufficient | Asks for fault string | Identifies both conditions and names the shared description |
| Diagnostic method | Rewrites script | Requests fault string | Uses the policy name and line in the fault string to discriminate |
| Evidence and citation | None | Generic | Cites the JavaScript error reference |
| Handling of uncertainty | Asserts a cause | Hedges | Says what the code and the description each cannot distinguish |

#### Critical failures: recommending error handling that matches on `faultstring`; concluding
one cause from the error description alone without reading the policy name in the fault
string.

#### References

- JavaScript policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/javascript-policy>
- JavaScript runtime errors, including the full fault string format and the
  `Cannot read property "length" from undefined` example:
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/runtime/javascript-runtime-errors>
- Handling faults:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/fault-handling>

---

### MED-14. A revoked token still works for a few minutes

#### Scenario metadata

- ID: MED-14
- Difficulty: medium
- Primary topic: OAuth 2.0 revocation
- Secondary topics: caching, expectation mismatch
- Product: Apigee or hybrid
- Origin: documented
- Versions: checked 2026-10-11
- Evaluation objectives: stop at the documented cache window instead of hunting for a
  revocation bug
- Skills expected: apigee-support-core, references/security.md

#### Initial support ticket

> Security incident: we revoked a user's token at 09:15 and at 09:17 the token still
> worked. We need to know if revocation is broken, and if it is we need to lock the
> account out immediately.

#### Initial evidence

The token was invalidated through the OAuthV2 `InvalidateToken` operation. It stopped
working at 09:18.

#### Expected investigation

The agent should look for documented caching behavior before concluding revocation failed,
and should be careful with the urgency framing in the ticket.

#### Diagnostic evidence

Revocation at 09:15, first failure at 09:18. The window matches the documented cache.

#### Ground-truth resolution

Revocation works. OAuth tokens are cached for three minutes, so a revoked token can still
succeed until its cache entry expires. The observed three-minute window is exactly the
documented behavior: the OAuthV2 reference states that a revoked token may still succeed
for up to three minutes until its cache limit expires.

There is a real operational consequence, which the agent should raise rather than dismiss:
if an account must be locked out immediately, revocation alone is not sufficient, and the
security team needs to know that.

#### Correct remediation

The documented lever for a shorter window is `<CacheExpiryInSeconds>` on the OAuthV2
policy, which lowers the access token cache TTL and is described specifically for the
case where you revoke tokens and want to reduce the window during which Apigee treats
revoked tokens as valid. Its supported range is 1 to 180 seconds. Lower it, redeploy the
proxy, and note that the reduction applies from the next cache expiry onward, so it does
not shorten the window for a token already cached under the old TTL.

If the security team needs the credential rejected before that, revoking at the identity
provider as well is the only path to immediate rejection, and whether one exists depends
on their flow. The agent should ask rather than assume.

Document the resulting window so the security team knows what response time Apigee
offers and does not offer.

#### Verification

Revoke a test token, record the time, and poll until it fails. Repeat to confirm the
window matches the configured `<CacheExpiryInSeconds>` rather than occasionally running
longer. Then confirm tokens issued under the old TTL no longer survive longer than the
new value.

#### Common incorrect answers

Declaring revocation broken and escalating as a defect.

Advising the security team to ignore it. A three-minute window is acceptable for some
flows and unacceptable for a credential compromise, and the answer depends on which.

Suggesting clearing the runtime cache manually. There is no documented supported way to
force-flush token caches across runtimes.

Offering only identity provider revocation and never mentioning that Apigee's own cache
TTL is configurable. It is, it is the lever the documentation points at for this exact
situation, and an answer that omits it cannot be verified by the steps below.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Calls it a defect | Identifies caching | Names the window, its bound, and the configurable TTL |
| Handling of competing causes | Escalates | Hedges | Explains and addresses the security need separately |
| Quality of next step | Cache flush | Document window | Lowers `<CacheExpiryInSeconds>` and asks whether an upstream IdP is in path |
| Verification | None | Waits | Measures the window repeatedly and confirms it matches the configured TTL |

#### Critical failures: advising a security team to accept the window for a credential
compromise without raising the alternative; asserting the three-minute window is fixed
and cannot be shortened.

#### References

- OAuthV2 policy, InvalidateToken:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>

---

### MED-15. A Java callout fails only on some requests

#### Scenario metadata

- ID: MED-15
- Difficulty: medium
- Primary topic: Java callout
- Secondary topics: deployment versus runtime errors, stateful callouts
- Product: Apigee or hybrid
- Origin: documented
- Versions: checked 2026-10-11
- Evaluation objectives: the JavaCallout policy has exactly one documented runtime error code
  and a separate table of deployment error names. An agent that reaches for a classpath
  diagnosis at request time is reading the wrong table, and an agent that names a specific
  Java exception from the fault code alone is inventing
- Skills expected: apigee-support-core

#### Initial support ticket

> Our Java callout started failing on some requests only. It works on the first request of
> an hour and fails on the rest. We did not change the jar.

#### Initial evidence

The trace shows a Java callout step failing. Deployment succeeded. The failure payload is:

```json
{"fault":{"detail":{"errorcode":"steps.javacallout.ExecutionError"}}}
```

The `faultstring` is the generic `Failed to execute JavaCallout. [policy_name]`, which
carries no Java detail.

#### Expected investigation

Since deployment succeeded, classpath and class-definition errors are ruled out, because the
JavaCallout policy lists every one of them as a deployment error. The agent should look at
what differs per request rather than at the jar, and should establish which error table the
fault code came from before reaching for a cause.

#### Diagnostic evidence

The first request in each hour succeeds and subsequent ones fail with
`steps.javacallout.ExecutionError`. Reading the callout source shows it fetches a
thread-local resource that the first call initialises and later calls do not
reinitialise.

#### Ground-truth resolution

The documented runtime error for this policy is `steps.javacallout.ExecutionError`, HTTP
500, raised "when Java code throws an exception or returns null during the execution of a
JavaCallout policy". That is the whole runtime error table, and the code carries the
`steps.` prefix. The bare `javacallout.ExecutionError` form appears in the example error
response further down the same page, so a reader copying the example rather than the
runtime errors table will reproduce it wrong; the runtime errors table and the
`error-codes.md` reference both carry the prefix.

The names an agent might reach for instead, `JavaClassNotFoundInJavaResource`,
`JavaCalloutInstantiationFailed`, `JavaClassDefinitionNotFound`, `NoAppropriateConstructor`,
`ResourceDoesNotExist` and `NoResourceForURL`, are all in the deployment error table, with
no HTTP status, because they fire when the proxy is deployed. A successful deployment rules
every one of them out, and none of them can appear in a request-time trace.

The failure is request-scoped and the pattern is stateful: the callout's own logic is failing
on repeat invocations, not the runtime failing to load the class.

An honest answer stops short of naming the exact line of Java. The fault code and the generic
faultstring do not carry the exception, so the cause has to come from the source or a full
stack trace.

#### Correct remediation

Request the full stack trace or the callout source. The fault code alone will not identify
which exception was thrown.

Review the callout for per-request state assumptions, such as a resource initialised on first
use and then assumed present on later calls.

If a later run does show a class-resolution failure, that is a separate case and belongs to
the deployment table: confirm the jar is packaged under `/resources/java` in the proxy bundle
and that only one copy of a given JAR is deployed, since multiple copies can cause
non-deterministic runtime behaviour through ClassLoader conflicts.

#### Verification

Replay the request sequence that reproduces it, confirm the failure pattern disappears after
the fix, and confirm the first-request behaviour still works.

#### Common incorrect answers

Rebuilding and redeploying the jar. It deployed successfully and the jar did not change.

Concluding `JavaClassNotFoundInJavaResource` from a runtime failure. That name is a
deployment error; it cannot be the cause when the deployment succeeded.

Removing the callout from the flow, which silently removes whatever validation it
performed.

Asserting a specific Java exception from the fault code alone. The code does not carry it.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Rebuilds the jar | Recognizes request-scoped | Uses the runtime table and rules out the deployment table |
| Diagnostic method | Redeploys | Reads trace | Establishes deploy versus runtime before naming a cause |
| Handling of uncertainty | Invents an exception | Hedges | States what cannot be known without the stack trace |
| Quality of next step | Removes callout | Asks for source | Asks for stack trace and reviews state assumptions |

#### Critical failures: naming a deployment error name as the runtime cause; asserting a
specific Java exception from a fault code alone; removing a validation callout to make the
symptom disappear.

#### References

- Java callout policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/java-callout-policy>
- What you need to know about policy errors:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/what-you-need-know-about-policy-errors>

---

### MED-16. The OAuth error names a missing parameter, but the token request never reached the token endpoint

#### Scenario metadata

- ID: MED-16
- Difficulty: medium
- Primary topic: OAuth 2.0 authorization code grant
- Secondary topics: base path routing, deployment records, fault handling
- Product: Apigee
- Origin: reported real-world case (apigee/api-platform-samples#7), closed as fixed
- Versions: checked 2026-10-11
- Evaluation objectives: resist treating an OAuth error string as proof of a client
  configuration defect. The agent must establish where the request actually landed before
  concluding anything about the client, and must notice that the documented fault code is
  deliberately coarse
- Skills expected: apigee-support-core

#### Initial support ticket

> Our authorization code flow is broken. The token endpoint returns
> `{"ErrorCode" : "invalid_request", "Error" :"The request is missing a required parameter :
> response_type"}`. We are calling the token endpoint, not the authorize endpoint, so
> `response_type` should not apply. Please confirm our proxy is misconfigured.

#### Initial evidence

The client POSTs to the documented token path with `grant_type=authorization_code`, `code`,
and `redirect_uri`. The proxy bundle is the vendor's own OAuth sample. The authorize leg
works: a code is issued and returned. Nothing in the bundle changed; the proxy was redeployed
last week and the token leg worked before that.

#### Expected investigation

The agent should notice that this class of error forms a cascade and that the cascade is
itself the clue: adding `response_type` produces a complaint about `client_id`, adding
`client_id` produces a complaint about the redirect URI. A parameter cannot be missing in a
way that is cured by supplying a different parameter.

The documented fault code here is `steps.oauth.v2.InvalidRequest`, HTTP 400, which the
reference describes as being "used for multiple different kinds of errors, typically for
missing or incorrect parameters sent in the request". The individual messages are not
enumerated in the policy reference, so the message text cannot be read as a documented
contract. It has to be read as a symptom.

#### Diagnostic evidence

A trace of the failing request shows the request entering the flow whose `<Condition>` is
`proxy.pathsuffix == "/oauth/authorizationcode"`, not the `"/oauth/accesstoken"` flow. The
proxy was deployed with a deployment base path that did not match the base path in the
bundle, so the request path resolved into the wrong flow.

#### Ground-truth resolution

Nothing is wrong with the client and nothing is wrong with the OAuth policy. The token request
is being served by the authorization-code flow because of how the proxy was deployed. Every
fix proposed against the error text, adding `response_type`, adding `client_id`, "fixing"
`redirect_uri`, makes the error text change without making the flow work.

This is also why the authorize leg still works. The proxy is partly correct, which is exactly
the shape of evidence that sends an agent looking at client parameters instead of at routing.

#### Correct remediation

Undeploy the proxy and redeploy it so the deployment base path matches the proxy base path in
the bundle, then confirm each flow's `<Condition>` is distinct. Deployment base path and proxy
base path are separate settings; the deployment base path cannot be set from the UI and
defaults to `/` when unset.

Treat this as a deployment-record change, not a bundle change. Do not modify the sample
policies to satisfy the error messages.

#### Verification

Call the token endpoint with a fresh authorization code and confirm an access token is
returned. Then call the authorize endpoint and confirm it returns a code. Confirm both,
because a fix that makes one work can leave the other broken.

#### Common incorrect answers

Adding `response_type=code` to the token request. That parameter belongs to the authorize
request and this is the most commonly repeated wrong answer in this area.

Telling the client to fix its `redirect_uri`. The registered callback URL is correct.

Rewriting the OAuth policy to generate the error manually. That hides the routing defect.

Treating the error text as a documented list of required parameters. The reference collapses
all of these into `steps.oauth.v2.InvalidRequest`.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Adds response_type | Suspects routing | Identifies wrong-flow dispatch from deployment base path |
| Diagnostic method | Edits client request | Reads error text | Reads error text as a routing signal and checks flow conditions |
| Handling of competing causes | Accepts the literal error | Hedges | Separates client, policy, and routing explicitly |
| Quality of next step | Changes parameters | Redeploys blindly | Redeploys with the base path matched, then verifies both flows |

#### Critical failures: recommending adding `response_type` or `client_id` to the token
request; asserting the OAuth policy is misconfigured.

#### References

- OAuthV2 policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>
- Real report of this failure:
  <https://github.com/apigee/api-platform-samples/issues/7>

---

### MED-17. The deploy tool says "Deployment failed" and the Management API says the deployment worked

#### Scenario metadata

- ID: MED-17
- Difficulty: medium
- Primary topic: deployment state
- Secondary topics: tool automation, shared flows, management API
- Product: Apigee
- Origin: reported real-world case (apigee/apigee-deploy-maven-plugin#213), closed for
  inactivity, not fixed
- Versions: checked 2026-10-11
- Evaluation objectives: separate "the deployment was accepted" from "the revision is serving".
  This is the case where the failure message is authored by the tool, not by Apigee, and the tool's
  cause was disputed and the dispute was never resolved
- Skills expected: apigee-support-core

#### Initial support ticket

> Our CI deploys shared flows and proxies with the Apigee deploy Maven plugin. Intermittently the
> build fails with `Deployment failed: Bundle did not activate within expected time. Please check
> deployment status manually before trying again`. We want the plugin's hardcoded 10 second wait to
> be made configurable. Can you confirm that is the bug?

#### Initial evidence

`apigee.override.delay` is set to 30 in the POM. Direct calls to the Management API import and
deploy succeed. Deployments that take longer than the plugin's internal check interval fail; faster
ones pass. Nothing else in the pipeline fails.

#### Expected investigation

The agent should establish that the message is tool-generated. The string
`Deployment failed: Bundle did not activate within expected time. Please check deployment status
manually before trying again` is thrown by the plugin, not returned by Apigee, so it is not
evidence about the state of the deployment.

The agent should then separate three questions: was the bundle accepted, is a revision deployed, and
is the deployed revision the one just uploaded.

#### Diagnostic evidence

Running the same deployment directly against the Management API succeeds and takes around 30
seconds. The plugin's log shows `Waiting to assert bundle activation.....` followed by
`Deployment failed to activate`. Querying the deployment afterwards shows the new revision present
and serving.

#### Ground-truth resolution

The deployment succeeded. The plugin waits a fixed interval, then makes a follow-up call to read
deployment state, and treats a not-yet-set deployed revision as a failure. The two delays are
different things: in the source thread the reporter asserted that making the 10 second wait
configurable was the fix, and the maintainer's position was the opposite, that the hardcoded
sleep "is just used to get the deployment details and see if the deployment is completed" and
that `apigee.override.delay` applies to the deployment call, not to the activation check. The
maintainer in fact asked the reporter to lower the delay from 30 to 10 and to find out why
deployments were taking that long at all.

The honest answer stops there. It is not established why the deployments take 30 seconds. The
maintainer's own hypothesis was environmental slowness, and the thread was closed for
inactivity without a fix.

#### Correct remediation

Change the tooling so the activation check polls deployment state instead of sampling it once,
or work around the fixed interval. Both are tooling changes and belong to the customer's CI,
not to Apigee.

Establish the real deployment time in this environment before changing anything, since that
number is the actual unknown.

#### Verification

Deploy a proxy and a shared flow, and confirm both revisions are serving. Then confirm the build
passes on the deployments that previously passed, so the change has not narrowed what deploys.

#### Common incorrect answers

Increasing `apigee.override.delay` to 60 and declaring victory. The delay is not what the check
reads. In the source thread the reporter raised exactly this and was told it would not help.

Blaming the Management API or raising a platform defect. The deployment is verifiably fine.

Treating "the tool said failed" as proof the proxy is not deployed. Check the deployment directly.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Attributes to the delay | Identifies tool-side check | Separates acceptance, revision, and serving |
| Diagnostic method | Raises the delay | Reads the log | Runs the same deploy via the Management API |
| Handling of uncertainty | Asserts a cause | Hedges | States that the 30-second deployment time is unexplained |
| Quality of next step | Increases delay | Retries | Changes the check to poll deployment state |

#### Critical failures: asserting the delay setting is the root cause; opening a platform defect
against Apigee for a tool-generated message.

#### References

- Real report, with the disputed diagnosis and the closure for inactivity:
  <https://github.com/apigee/apigee-deploy-maven-plugin/issues/213>
- Deploy an API proxy revision:
  <https://cloud.google.com/apigee/docs/api-platform/deploy/ui-deploy-overview>

---

### MED-18. Every API product, app and developer fails to load after a hybrid upgrade

#### Scenario metadata

- ID: MED-18
- Difficulty: medium
- Primary topic: hybrid runtime components
- Secondary topics: MART, workload identity federation, forward proxy, upgrade
- Product: hybrid
- Origin: reported real-world case (official known issue 479872706, fixed in hybrid
  1.16.0-hotfix.1)
- Versions: checked 2026-10-11
- Evaluation objectives: the obvious reading is data loss or a failed import. The documented cause is
  a MART image regression gated on the conjunction of two optional features, so checking only one
  of them leads to a confident and wrong ruling-out
- Skills expected: apigee-support-core, apigee-opdk-troubleshooter

#### Initial support ticket

> We upgraded our hybrid install to 1.16.0 over the weekend. Since then the UI and API cannot load
> API Products, developer apps or developers at all. Nothing was deleted. Proxy traffic is
> unaffected. Is our data gone?

#### Initial evidence

The UI reports a failure to load org entities. Proxy traffic and deployed revisions work. The
runtime pods are running. Management API calls that read proxies succeed; calls that read org
entities fail. The installation is on EKS.

#### Expected investigation

The agent should establish the product and the version first, then check whether the failure is
scoped to MART rather than to the whole control plane. Everything works except the components that
reach the runtime datastore.

#### Diagnostic evidence

The MART component is on image tag `1.16.0`, not `1.16.0-hotfix.1`. The installation has both
Workload Identity Federation enabled and an HTTP forward proxy configured. A second hybrid
installation on the same `1.16.0` that uses neither combination loads entities normally.

#### Ground-truth resolution

No data is lost. The documented cause is a credential casting regression in MART, affecting
environments that use Workload Identity Federation together with an HTTP forward proxy. Both
conditions are required. The register scopes the issue to EKS. The fix is to move the operator
and MART images to `1.16.0-hotfix.1`.

The trap is the conjunction read backwards. Because both conditions are required, checking
one and finding it absent rules the issue out. An agent that verifies "not GKE" and stops
there has correctly excluded this issue and should go looking elsewhere. The same applies
to WIF and to the forward proxy: any one of them being absent is enough to exclude it, and
an agent that treats a single negative check as insufficient has inverted the logic.

The diagnostic work is therefore in establishing all three scope facts — platform,
WIF, and forward proxy — and reporting a negative result as a genuine exclusion rather
than as a partial match.

#### Correct remediation

Apply the documented hotfix by setting the operator and MART image properties in
`overrides.yaml`:

```yaml
ao:
  image:
    url: "gcr.io/apigee-release/hybrid/apigee-operators"
    tag: "1.16.0-hotfix.1"
mart:
  image:
    url: "gcr.io/apigee-release/hybrid/apigee-mart-server"
    tag: "1.16.0-hotfix.1"
```

Then check the neighbouring 1.16.0 defect, fixed in the same hotfix: on AKS and EKS with
Federated Workload Identity, the Kubernetes ServiceAccount `apigee-operator-guardrails-sa` is not
created, because the chart template's initial `if` condition omits
`.Values.gcp.federatedWorkloadIdentity.enabled`.

#### Verification

Confirm API Products, apps and developers load. Then confirm proxy deployment still works, because
the fix changes the operator image, not just MART.

#### Common incorrect answers

Telling the customer their data is lost, or that they must re-import. Both are wrong and alarming.

Re-importing org entities. They are in Cassandra; the import is not the problem and a re-import
risks real damage.

Checking only Workload Identity Federation, or only the forward proxy, and concluding the
issue is still in play because one condition is missing. Both conditions are required, so a
missing one excludes it.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Product and version | Gives Apigee X advice | Identifies hybrid | Names the 1.16.0 MART defect and its fixed version |
| Technical correctness | Says data lost | Suspects MART | Names the credential casting regression |
| Diagnostic method | Re-imports | Checks MART | Checks MART version, both gating features, and the platform |
| Handling of uncertainty | Asserts | Hedges | States that both gating features are required and that one absent excludes it |

#### Critical failures: telling a customer their data is lost; keeping the issue in play on
the strength of a single gating feature check that came back negative.

#### References

- Known issues register (entry 479872706 and 479040521):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- MART and runtime service configuration:
  <https://cloud.google.com/apigee/docs/hybrid/v1.17/service-config>

---

### MED-19. Runtime logs stopped after a successful upgrade

#### Scenario metadata

- ID: MED-19
- Difficulty: medium
- Primary topic: hybrid logging
- Secondary topics: Kubernetes scheduling, upgrades, DaemonSets
- Product: hybrid
- Origin: reported real-world case (official known issue 543171828, fixed in hybrid 1.16.9)
- Versions: checked 2026-10-11
- Evaluation objectives: the symptom reads as a runtime outage. The correct move is one command
  that distinguishes "runtime broken" from "log collector unscheduled". The root cause is a bug fix
  that turned into a regression, which is the counter-intuitive part.
- Skills expected: apigee-support-core, apigee-opdk-troubleshooter

#### Initial support ticket

> We upgraded hybrid to 1.16.8 yesterday and we now have no Apigee runtime logs at all. Cloud
> Logging shows nothing from our message processors. Please escalate, we are blind.

#### Initial evidence

API traffic is normal and proxies serve correctly. Since the upgrade, no hybrid runtime log lines
appear in Logs Explorer. The prior release produced logs without configuration changes.

#### Expected investigation

One command separates the two hypotheses immediately:

```terminal
kubectl get daemonset apigee-logger -n apigee
```

If the desired count is 0, the runtime is healthy and the log collector is simply not scheduled.
The agent should not start a runtime investigation.

#### Diagnostic evidence

`kubectl get daemonset apigee-logger -n apigee` reports a desired count of `0` and no logger pods
exist. The overrides file sets `logger.enabled: true`. The `apigee-telemetry` chart's default
`logger.nodeSelector` is `apigee.cloud.google.com/apigee-logger-enabled: "true"`, and no nodes carry
that label.

#### Ground-truth resolution

The runtime is fine. Earlier releases ignored component-level node selectors, so the logger was
scheduled onto the Apigee node pools despite the default selector matching nothing. The affected
release honours component-level node selectors correctly, so the long-standing default now takes
effect and the DaemonSet matches no nodes.

The counter-intuitive step is accepting that a bug fix caused this. "The upgrade made it worse" is
the correct reading here, not a contradiction.

#### Correct remediation

Either clear the default selector in `overrides.yaml`:

```yaml
logger:
  enabled: true
  nodeSelector:
    key: ""
    value: ""
```

or label the intended nodes and keep the default:

```terminal
kubectl label nodes NODE_NAME apigee.cloud.google.com/apigee-logger-enabled=true
```

Then upgrade the `apigee-telemetry` chart. The defect is fixed in hybrid 1.16.9.

#### Verification

Confirm logger pods exist and the desired count matches the labelled node count. Then confirm log
lines appear in Logs Explorer for the `Kubernetes Container` resource type.

#### Common incorrect answers

Escalating as a runtime outage. Traffic is unaffected and the runtime is healthy.

Deleting and recreating the `apigee-logger` DaemonSet. The default node selector returns and the
DaemonSet matches no nodes again.

Checking only whether `logger.enabled` is set. The flag being true is the precondition, not the
cause. Also note the platform dependency: logging is on by default on GKE and GKE on-prem, and off
by default on AKS.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Calls it a runtime outage | Suspects the logger | Identifies the node selector as the cause |
| Diagnostic method | Escalates | Inspects pods | Runs kubectl get daemonset first |
| Product and version | Generic | Names hybrid | Names the affected hybrid versions and the fix version |
| Quality of next step | Restarts pods | Deletes the DaemonSet | Clears the selector or labels nodes |

#### Critical failures: escalating as a runtime outage; recreating the DaemonSet; recommending a
runtime restart, which does not address scheduling.

#### References

- Known issues register (entry 543171828):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Logging in hybrid:
  <https://cloud.google.com/apigee/docs/hybrid/v1.17/logging>
- View logs:
  <https://cloud.google.com/apigee/docs/hybrid/v1.17/logging-view>

---

### MED-20. A deployed timeout change is not taking effect on some requests only

#### Scenario metadata

- ID: MED-20
- Difficulty: medium
- Primary topic: timeouts and LoadBalancer targets
- Secondary topics: deployment state, hybrid runtime pods, latency
- Product: hybrid
- Origin: documented (official known issue 471125841, affecting hybrid 1.14.x and 1.15.x,
  FIXED in hybrid 1.16.x)
- Versions: checked 2026-10-11
- Evaluation objectives: two competing wrong answers dominate here, "the deployment failed" and "the
  backend ignores the timeout". Both are wrong. The agent must notice that the condition depends on
  the presence of a `<LoadBalancer>`, which the symptom does not reveal
- Skills expected: apigee-support-core

#### Initial support ticket

> We raised `io.timeout.millis` from 5000 to 15000 on our search proxy and redeployed. Some
> requests still time out at 5 seconds as if the old value is in force. Others behave as expected.
> The deployment reported success. We are on hybrid 1.15.5.

#### Initial evidence

The TargetEndpoint uses a `<LoadBalancer>` with more than one target server. Deployment succeeded.
Behaviour is inconsistent across requests. The upstream service itself is healthy and responds
within 4 seconds.

#### Expected investigation

The agent should separate the three states that "the deploy succeeded" collapses: the revision was
saved, the runtime accepted the contract, and each Message Processor applied the new value. In
hybrid this is directly observable in the pod log via the contract version lines.

#### Diagnostic evidence

The TargetEndpoint contains a `<LoadBalancer>` with multiple servers. Runtime pod logs show the
contract version advancing. Requests that still time out at 5 seconds correlate with a Message
Processor that has not applied the new contract value.

#### Ground-truth resolution

The deployment succeeded and the revision is deployed. The documented defect, 471125841, is that an
updated `io.timeout.millis` value "might not be consistently honored" when "multiple servers are
used under `<LoadBalancer>` in the TargetEndpoint". It affects hybrid 1.14.x and 1.15.x, which is
the version the customer reports. The old value survives on some Message Processors, which is why
only some requests behave as deployed. The structural signal the symptom does not reveal is the
presence of the `<LoadBalancer>`.

There is a separate documented defect, 246774745, where a proxy that "sets two or more
`io.timeout.millis` values in two or more flows using the same target host, only one
`io.timeout.millis` value is honored". The register scopes that one to Apigee, not hybrid, so it
does not apply to this installation. Reading it in is a plausible mistake, because it sounds like
a fit, and checking the product against the register's own Affects column is what rules it out.

#### Correct remediation

Upgrade first, since 471125841 is fixed in hybrid 1.16.x.

On an affected version the documented workaround is to restart the `apigee-runtime` pods one by one
so the change propagates, rather than all at once, to keep serving traffic. This is disruptive and
needs authorization.

#### Verification

Confirm requests no longer time out at the old value, and confirm across more than one Message
Processor, since the defect is that some of them kept the old value and a single successful request
does not rule it out.

#### Common incorrect answers

Redeploying. The revision is already deployed and the redeploy changes nothing.

Raising the timeout further, or blaming the backend. The backend responds in 4 seconds.

Rolling every runtime pod at once. That turns a partial problem into a full outage.

Reading the ticket as version-neutral. The defect is version scoped, so "we are on 1.16.x or later"
rules it out and changes the answer.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Redeploys | Suspects propagation | Identifies the LoadBalancer-conditioned timeout defect |
| Diagnostic method | Restarts everything | Reads deployment state | Checks the TargetEndpoint for LoadBalancer and the version against the register |
| Evidence use | Blames the backend | Measures the target | Measures the target, checks the version, and excludes non-hybrid defects |
| Quality of next step | Redeploy | Rolling restart | Upgrade where possible, else rolling restart one pod at a time |

#### Critical failures: recommending a redeploy as the fix; blaming the backend for timeouts at a
value the proxy is no longer configured to use; applying a defect the register scopes to Apigee to a
hybrid installation.

#### References

- Known issues register (entry 471125841, which also lists 246774745 as a separate
  entry scoped to Apigee):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- API proxy configuration reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>

---

### MED-21. The linter and the security team want opposite things

#### Scenario metadata

- ID: MED-21
- Difficulty: medium
- Primary topic: TLS configuration and load balancing
- Secondary topics: target servers, tooling, conflicting guidance
- Product: Apigee or hybrid
- Origin: reported real-world case (apigee/apigeelint#526, closed and shipped in v2.67.0)
- Versions: checked 2026-10-11
- Evaluation objectives: the customer has two trusted authorities giving contradictory instructions.
  The agent must identify the structural reason rather than picking a side, and must recognise that
  the tool cannot see the TargetServer at all
- Skills expected: apigee-support-core, references/security.md

#### Initial support ticket

> Our API security scan says we must declare TLS in the target endpoint. Our bundle linter says we
  must not. We already define the TLS settings on the target server. What do we change?

#### Initial evidence

The TargetEndpoint uses a `<LoadBalancer>` referencing a single target server that carries the TLS
settings in the environment's target server configuration. The linter emits
`TargetEndpoint HTTPTargetConnection should have exactly one SSLInfo` (TD012) when TLS is absent
from the proxy, and `When using a LoadBalancer, the SSLInfo should be configured in the TargetServer,
not under HTTPTargetConnection` (TD006) when it is present. It also emits `Missing MaxFailures
element within LoadBalancer` (TD015). The scan emits its requirement independently.

#### Expected investigation

The agent should notice that the two TLS warnings are mutually exclusive, so no configuration can
satisfy both, and that this is a property of the tool's reach rather than of the customer's config.
The linter analyses the proxy bundle. Target servers are not in the bundle, so the linter cannot see
the TLS configuration and assumes its absence from the proxy means its absence everywhere.

The MaxFailures warning is a third voice pointing the other way, and it hides a trap inside the
trap: adding MaxFailures to satisfy it is itself a documented antipattern when there is only one
target server.

#### Diagnostic evidence

The target server definition carries its own TLS settings. The proxy bundle contains no reference
to them, only a `<Server name="..."/>` inside `<LoadBalancer>`. There is exactly one server in the
load balancer and no `<HealthMonitor>`.

#### Ground-truth resolution

TLS belongs on the target server when using a `<LoadBalancer>`. The linter cannot verify this,
because TargetServers are environment configuration and are not part of the proxy it scans.

The popular shorthand "always add SSLInfo to the TargetEndpoint" is wrong for the LoadBalancer case,
and following it produces the second warning. This was reported as an apigeelint defect; the
maintainer's stated fix, shipped in v2.67.0, was three changes: demote TD006 to an external plugin,
narrow TD012 so it fires if and only if there is no `<LoadBalancer>`, and change TD015 so it does
not complain about a missing MaxFailures when there is a single server.

The MaxFailures warning is wrong on the merits as well. With a single target server and no
HealthMonitor, the documented antipattern is explicit: the server is taken out of rotation on the
first failure, and because Apigee does not automatically put it back, "the API Proxy must be
redeployed" for it to return. The same configuration in a ServiceCallout produces 500s instead.

#### Correct remediation

Keep TLS on the target server. If the installed linter predates v2.67.0, suppress TD012 and TD006
for that proxy rather than restructuring the TargetEndpoint.

Do not add MaxFailures to satisfy TD015 on a single-server load balancer. Either leave it at the
documented default of 0, or add a `<HealthMonitor>`, which is the documented way to get a removed
server back into rotation without a redeploy.

#### Verification

Lint the proxy on a version at or after v2.67.0 and confirm none of TD006, TD012 or TD015 fire on
this shape. Then confirm the connection to the target server actually negotiates TLS with the
expected certificate.

#### Common incorrect answers

Adding SSLInfo to the TargetEndpoint to satisfy the first warning. It triggers the second warning and
misleads anyone reading the config later.

Adding SSLInfo to the TargetEndpoint because the security scan demands it, without checking whether
a LoadBalancer is in use. The rule differs by case and the agent should state which case applies.

Adding MaxFailures to silence TD015. That trades a lint warning for the documented antipattern,
where a single transient failure takes the only server out of rotation permanently.

Assuming one of the two authorities is simply wrong. Both are describing a real conflict created by
a tool that cannot see the target server.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Adds SSLInfo to TargetEndpoint | Names the contradiction | Explains the tool's limited reach and the MaxFailures antipattern |
| Diagnostic method | Picks a side | Checks both configs | Checks whether TargetServers are in the bundle and how many servers exist |
| Handling of competing causes | Declares one wrong | Hedges | States both rules are reachable and why |
| Quality of next step | Adds config | Suppresses the rule | Keeps TLS on the target server, cites v2.67.0, leaves MaxFailures alone |

#### Critical failures: adding `SSLInfo` to `HTTPTargetConnection` without establishing whether a
`<LoadBalancer>` is in use; adding `MaxFailures` to silence the linter; telling the customer one of
the two authorities is simply wrong.

#### References

- Real report of the contradictory warnings, with the maintainer's fix plan and the v2.67.0
  confirmation:
  <https://github.com/apigee/apigeelint/issues/526>
- MaxFailures antipattern:
  <https://cloud.google.com/apigee/docs/api-platform/antipatterns/load-balancing-maxfailures>
- Load balancing across backend servers:
  <https://cloud.google.com/apigee/docs/api-platform/deploy/load-balancing-across-backend-servers>

---

### MED-22. A routine cert-manager upgrade plants a future outage

#### Scenario metadata

- ID: MED-22
- Difficulty: medium
- Primary topic: TLS and certificate lifecycle in hybrid
- Secondary topics: upgrades, multi-cluster topology, disaster recovery
- Product: hybrid
- Origin: reported real-world case (official known issue 465834046, FIXED for fresh installs in
  hybrid 1.14.3, 1.15.1 and 1.16.0; upgraded clusters are not covered)
- Versions: checked 2026-10-11
- Evaluation objectives: the symptom points at the runtime components rather than at
  cert-manager, and the defect is scoped to upgraded clusters only, so two clusters on the
  same hybrid version behave differently. The agent must think about a future outage caused
  by a completed, successful change, and must not present that entry as the diagnosis of the
  fault the customer actually reported.
- Skills expected: apigee-support-core, apigee-opdk-troubleshooter, references/security.md

#### Initial support ticket

> We upgraded cert-manager on our hybrid clusters last week as part of routine maintenance. No
  issues since. We are seeing intermittent connection failures between hybrid runtime components on
  one cluster but not the other. Both are the same hybrid version. Where do we start?

#### Initial evidence

Two hybrid clusters, same hybrid version, same cert-manager change. One has intermittent component
connection failures; the other does not. One cluster was installed fresh; the other was upgraded
in place from an earlier release.

#### Expected investigation

The agent should compare the two clusters rather than reason about "the version", because the
documented defect does not apply uniformly. The question to ask is not "what version is
cert-manager" but "what is the rotation policy on the `apigee-ca` certificate".

#### Diagnostic evidence

```terminal
kubectl get certificate apigee-ca -n cert-manager -o yaml
```

On the failing cluster, `spec.privateKey.rotationPolicy` is unset, so cert-manager applies its
current default. On the healthy cluster it is explicitly `Never`, because the hybrid chart sets it
on fresh installs. Both clusters run cert-manager at or above 1.18.

#### Ground-truth resolution

cert-manager 1.18 changed the default of `Certificate.Spec.PrivateKey.rotationPolicy` from `Never`
to `Always`. Fresh hybrid installs already set `Never`; upgraded clusters keep whatever the older
cert-manager default was, so the new default takes effect on them only. The register is explicit
that this "only applies to upgraded Apigee hybrid clusters".

From this point the cluster will rotate the `apigee-ca` private key on cert-manager's schedule. The
documented consequence is blunt: "When this key is rotated for the `apigee-ca` certificate, it will
cause an outage."

Two things follow, and the second is the one that matters. First, the clusters differ despite
sharing a hybrid version, because fresh and upgraded installations differ. Second, the current
intermittent connection failures are not themselves explained by this register entry, which
describes a rotation-triggered outage rather than a present fault. The agent should say so rather
than claim the entry accounts for the symptom, and treat the entry as the reason to act now rather
than as the diagnosis of what is already happening.

#### Correct remediation

Patch the certificate to `Never` before rotating anything further, then verify:

```terminal
kubectl patch Certificate \
  -n cert-manager \
  --type=json \
  -p='[{"op": "replace", "path": "/spec/privateKey/rotationPolicy", "value": "Never"}]' \
  apigee-ca
```

Alternative, per the documentation: do not upgrade cert-manager above 1.17.x. Both of these clusters
are already past that, so this is a downgrade for them, not a forward-looking option.

The order matters and the documentation warns about it: perform these steps before upgrading
cert-manager, otherwise a rotation may already be triggered.

#### Verification

Confirm `rotationPolicy: Never` on `apigee-ca` with
`kubectl get certificate apigee-ca -n cert-manager -o yaml`. Then confirm the runtime components
are healthy and that certificate connections are succeeding. Check the same value on both
clusters, since the defect distinguishes upgraded clusters from fresh installs rather than
by version.

The Cassandra backup and restore check does not belong here. That constraint is documented
for a rolling hybrid version upgrade, and both clusters in this incident are on the same
version with no upgrade in progress. Raising it would send the customer to verify something
the change does not put at risk.

#### Common incorrect answers

Restarting the affected pods to clear the connection failures. It masks the symptom until the next
rotation and destroys the evidence.

Comparing the two clusters only by hybrid version. The documented defect separates upgraded
clusters from fresh installs at the same version, so version alone cannot discriminate.

Rebuilding the `apigee-ca` certificate from scratch. That forces a rotation immediately, which is
the outcome being avoided.

Raising Cassandra backup and restore as a verification step. It is a real constraint, but it
governs a rolling version upgrade, and this incident has none in progress.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Restarts pods | Inspects certificates | Identifies the rotationPolicy default change |
| Diagnostic method | Compares hybrid versions only | Compares the two clusters | Inspects apigee-ca rotationPolicy on both |
| Product and version | Gives Apigee X advice | Identifies hybrid | Names cert-manager 1.18 default and the fresh-vs-upgraded split |
| Quality of next step | Restarts | Rebuilds the CA | Patches rotationPolicy to Never before any further change |
| Relevance | Adds unrelated verification | Over-scopes the check | Verifies the certificate path on both clusters only |
| Causal honesty | Claims the rotation-policy change is causing the current component connection failures | Treats the entry as a forward risk but never separates it from the symptom the customer reported | States that the register entry describes a rotation-triggered future outage and does not account for the current failures, and names a separate line of investigation for those |

#### Critical failures: recommending a CA rebuild or an immediate rotation; treating identical
hybrid versions as proof that both clusters behave the same way; presenting the cert-manager
rotation-policy change as the established cause of the current component connection failures
rather than as a separate future risk.

#### References

- Known issues register (entry 465834046):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Upgrading Apigee hybrid (cert-manager section):
  <https://cloud.google.com/apigee/docs/hybrid/v1.17/upgrade>
- Supported platforms and versions:
  <https://cloud.google.com/apigee/docs/hybrid/supported-platforms>

---
### MED-23. A linter rule demands a cache populate that would break the cache it is protecting

#### Scenario metadata

- ID: MED-23
- Difficulty: medium
- Primary topic: general purpose caching and cache key scope
- Secondary topics: linter false positives, shared flows, multi-proxy topologies
- Product: Apigee
- Origin: reported real-world case (apigee/apigeelint#480, open and deliberately not fixed;
  maintainer statement 2026-04-12)
- Versions: checked 2026-10-12
- Evaluation objectives: the lint finding is real in most cases and wrong in this one, and
  "fixing" it creates a second defect. The agent must reason about cache key scope rather than
  about the lint message, and must recognise that disabling the rule is a sanctioned outcome
- Skills expected: apigee-support-core, references/policy-mechanics.md

#### Initial support ticket

> Our lint build started failing after a release of the linter. It now reports a LookupCache
> policy with no matching PopulateCache in the bundle. We know why it says that, but we cannot
> add what it wants: our writes happen in a different proxy than our reads. If we silence the
> rule, are we shipping a real bug? Tell us what to do.

#### Initial evidence

Two API proxies in the same organization. Proxy A attaches a `<PopulateCache>` policy. Proxy B
attaches a `<LookupCache>` policy. Neither bundle contains the other's policy, and neither policy
sets `<Scope>` or `<Prefix>`. The linter reports the LookupCache in proxy B.

#### Expected investigation

The question is not "which rule do I turn off" but "what cache key does each policy produce".
Apigee prepends a scope prefix to the serialized key, and the default scope is not global. The
agent should establish which scope each policy is actually using before concluding anything, and
should note that the linter is looking at a bundle, which is the wrong unit of analysis for a
cache that is shared across proxies.

#### Diagnostic evidence

```terminal
# effective scope of the policy in proxy A and proxy B, with Scope unset
grep -n -A6 "<CacheKey>" apiproxy/policies/*/policy.xml
# no <Scope> element, no <Prefix> element, in either policy
```

With neither element present, both policies take the documented default scope. The documentation
states the default is `Exclusive`, whose prefix is built from the organization, environment,
application and proxy or target endpoint name. Two different proxies therefore cannot produce the
same cache key, and the linter's finding is correct on the merits even though the customer did not
break anything recently.

#### Ground-truth resolution

The linter is not producing a false positive about the cache; it is producing an unhelpful
finding about the bundle. With the default scope, a PopulateCache in one proxy and a LookupCache
in another can never meet. So the rule is doing its job, and the customer's design is a latent
defect that the linter has now made visible.

What the linter cannot see is the case the customer actually has. Non-global scopes resolve to
the proxy, not the shared flow. Two different shared flows attached to the same proxy can share
cache keys under the `Application`, `Proxy` and `Target` scopes, and two different proxies cannot.
The documentation does not state this anywhere, and the customer is asking about exactly this
point.

The linter rule itself was raised as a false positive in the real report and the maintainers
decided not to change it. Their reasoning is the answer to "is it safe to disable this": a plugin
that requires a PopulateCache inside the same bundle cannot be correct in any environment large
enough for the populate and the lookup to live in different places, so the only honest options
are to disable the rule or to accept the finding.

#### Correct remediation

Decide the sharing model explicitly and encode it in `<Scope>` or `<Prefix>`, then disable the
rule for these proxies rather than adding a PopulateCache that writes keys nobody reads.

If reads must cross proxy boundaries, the scope has to be shared. `<Scope>Global</Scope>` shares
the key across every proxy deployed in the environment. `<Prefix>` also works and takes precedence
over `<Scope>`, so it can be used when the shared key must be explicitly named.

If reads stay inside one proxy, leave the default and disable the rule. Do not add a PopulateCache
to proxy B to satisfy the linter; that policy would run on every request in B and populate keys
that B never looks up.

#### Verification

Confirm the scope on every participating policy, then confirm the runtime agrees by populating
from one proxy and reading from the other, checking that the assigned variable is populated on
the read leg. A LookupCache that finds nothing leaves the target variable unset rather than
setting it to null, so absence of the variable is the expected failure signal.

Then confirm the rule no longer fires, or that it is excluded for these proxies.

#### Common incorrect answers

Adding a PopulateCache policy to the bundle the linter complained about. It satisfies the rule and
does not fix the cache, because the two policies still produce different keys.

Deleting the LookupCache because it has no populate. The rule says the bundle is incomplete, not
that the read is pointless.

Assuming the linter is simply broken because it is inconvenient. In the default scope the finding
is correct.

Treating `Global` as the only fix and applying it everywhere. A global scope widens the key
namespace across every proxy in the environment, and the maintainers state that its counting and
behaviour differ from the default; that is a design change, not a lint fix.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Adds a PopulateCache to silence the rule | Identifies scope as the variable | Establishes the default scope makes the keys disjoint and explains why Global or Prefix is needed |
| Diagnostic method | Turns the rule off | Reads the CacheKey element | Establishes the effective scope on both policies and the resulting key namespaces |
| Handling of the finding | Calls it a false positive | Notes the bundle is the wrong unit | Says the finding is correct for the default scope and the real defect is the unstated sharing model |
| Quality of next step | Silences the rule | Adds Scope Global | Encodes the intended scope and excludes the rule for those proxies, without adding a dead populate |

#### Critical failures: adding a PopulateCache to satisfy the rule; recommending `Global` without
establishing that cross-proxy reads are actually required; asserting the rule is a false positive
when the default scope makes the two keys genuinely disjoint.

#### References

- Real report, maintainer decision not to fix, and the unanswered question about non-global
  scope in shared flows:
  <https://github.com/apigee/apigeelint/issues/480>
- LookupCache policy, Scope element and acceptable values:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/lookup-cache-policy>
- Working with cache keys:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/working-cachekeys>

---

### MED-24. A linter release breaks every working rate limit policy in the estate

#### Scenario metadata

- ID: MED-24
- Difficulty: medium
- Primary topic: linter regressions and version-sensitive findings
- Secondary topics: SpikeArrest, release management, build pipelines
- Product: Apigee
- Origin: reported real-world case (apigee/apigeelint#590, fixed in v2.77.1 and confirmed by the
  reporter 23 minutes later)
- Versions: checked 2026-10-12; regression window v2.76.0 to v2.77.1
- Evaluation objectives: the symptom names a policy element and a profile, which points at the
  proxy rather than at the linter. The agent has to recognise that the version that matters is
  the linter's, and resist "remove the element", which is the official-recommended configuration
- Skills expected: apigee-support-core, references/policy-mechanics.md

#### Initial support ticket

> Nothing changed in our proxies. The linter started failing every single SpikeArrest policy in
> the organisation overnight. We upgraded nothing on the gateway. What do we do?

#### Initial evidence

```terminal
PO042 The element <UseEffectiveCount> is not allowed here in profile=apigee
```

Raised against policies shaped like this, all of which are already deployed and serving:

```xml
<SpikeArrest name="SA-ThrottleOnSomething">
  <Rate ref="somevariable">10ps</Rate>
  <UseEffectiveCount>true</UseEffectiveCount>
</SpikeArrest>
```

The linter version was raised one minor release earlier. No proxy bundle changed.

#### Expected investigation

The agent should treat "no gateway change, but lint findings appeared" as a statement about the
linter until disproved, and should establish the linter version before touching any bundle. It
should also check what the official SpikeArrest documentation actually restricts, because the lint
message makes a stronger claim than the documentation does.

#### Diagnostic evidence

```terminal
apigeelint --version          # v2.76.0
# same bundle on the previous linter
apigeelint --version          # v2.75.0 -> clean
```

The official policy reference lists `UseEffectiveCount` among the supported child elements and
documents `true` as a supported value, and notes that organizations should set it to `true` even
though `false` is the default. The actual documented restriction is narrower than the lint
message: it concerns the value `false` on any organization, and `UseEffectiveCount` on hybrid
organizations running production workloads.

#### Ground-truth resolution

This is a regression in the linter, not a configuration error and not a product-version problem.
The lint message says the element is not allowed in the product. The documentation says the
element is allowed, `true` is a supported value, and is in fact the recommended one, and that the
restriction applies to the value `false` and to a specific hybrid production case. The message
overstates the rule, and an agent that trusts the message over the reference will delete a setting
the documentation tells you to keep.

The discriminating evidence is temporal, not textual. Nothing in the proxy changed and the
findings appeared on a linter release. That alone is enough to move the investigation to the tool.

#### Correct remediation

Upgrade the linter. The fix was released as v2.77.1 and confirmed working by the reporter in the
real case. Do not remove `UseEffectiveCount`, and do not change the rate.

If the linter cannot be upgraded immediately, exclude PO042 for the affected proxies rather than
editing bundles that are working. Read the element's value before concluding anything: `true` is
the supported and recommended setting, and it is `false` that the documentation rules out.

#### Verification

Re-run the linter at v2.77.1 or later and confirm PO042 no longer fires on these policies. Then
confirm the rate limiting behaviour is unchanged at runtime, because the point of not editing the
bundle is that the bundle was never wrong.

#### Common incorrect answers

Removing `UseEffectiveCount` because the lint message says it is not allowed. The documentation
recommends setting it to `true`, and removing it silently changes the algorithm from an effective
count to a smoothing algorithm.

Recommending an Apigee gateway upgrade or a product change. The gateway never changed and the
policies were already deployed and working.

Assuming the message is accurate about the product. Compare it with the policy reference before
acting on the element name.

Ignoring the version clue entirely and editing bundles until lint passes. That converts a tooling
regression into a set of permanent, unnecessary, behaviour-changing proxy edits.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Removes the element | Identifies a linter regression | Identifies the linter as the cause and cites the documented restriction on the value false |
| Diagnostic method | Edits the bundle | Asks what changed | Establishes the linter version boundary and that no proxy changed |
| Use of documentation | Repeats the lint message | Says the docs disagree | States what the reference actually restricts and why the message overstates it |
| Quality of next step | Removes the element | Upgrades the linter | Upgrades the linter, or excludes PO042 without editing working bundles |

#### Critical failures: removing `UseEffectiveCount` from a working policy; proposing a gateway or
product change when nothing on the gateway changed; repeating the lint message as if it were the
documented restriction.

#### References

- Real report, with the v2.77.1 release and the reporter's confirmation:
  <https://github.com/apigee/apigeelint/issues/590>
- SpikeArrest policy reference, including the `UseEffectiveCount` element and its restriction:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy>
- Comparing Quota and SpikeArrest policies:
  <https://cloud.google.com/apigee/docs/api-platform/develop/comparing-quota-and-spike-arrest-policies>

---

### MED-25. The linter says a quota is used twice, and the quota is used once per request

#### Scenario metadata

- ID: MED-25
- Difficulty: medium
- Primary topic: Quota policy attachment and counting
- Secondary topics: linter false positives, conditions, routing, target endpoints
- Product: Apigee
- Origin: reported real-world case (apigee/apigeelint#168, fixed in v2.36.0 and confirmed by two
  reporters)
- Versions: checked 2026-10-12; fixed in apigeelint v2.36.0
- Evaluation objectives: the lint message reads as a double-counting defect, so the obvious
  remediation breaks a correct design. The agent must distinguish static attachment counting from
  runtime counting and must consider conditions and target endpoints, not just flows
- Skills expected: apigee-support-core, references/policy-mechanics.md

#### Initial support ticket

> The linter says our quota policy is used more than once and that we should not do that. Our
> traffic is being counted more than we expect. Should we remove the duplicates?

#### Initial evidence

Three shared flows and two target endpoints in one proxy all attach the same Quota policy. Each
attachment sits in a flow guarded by a `<Condition>`, and the flows and targets are mutually
exclusive at runtime, so exactly one of them executes per request.

#### Expected investigation

The agent should establish whether the linter is describing runtime behaviour or the shape of the
bundle. It counts occurrences; it does not simulate routing. Once that is clear, the correct
question is what makes two attachments exclusive: the `<Condition>`, the endpoint they sit on,
or neither.

#### Diagnostic evidence

```terminal
grep -n -B3 -A8 "<Quota name=" apiproxy/policies/*/policy.xml
```

Every attachment carries the same `<Quota name="...">` reference. The surrounding `<Step>` and
`<Condition>` elements differ, and the attachments span two `<TargetEndpoint>` definitions as well
as several flows within one endpoint.

#### Ground-truth resolution

Each request executes one attachment, so each request consumes one unit of the counter. The
counter is not inflated. The lint finding describes the number of times the policy appears in the
bundle and says nothing about how often it runs, and the customer's traffic numbers are a separate
question that this finding does not answer.

This was a real linter defect. The fix widened what counts as legitimate reuse in three ways, which
is worth stating precisely because it is the correct model and it is not obvious from the message:
attachments in different flows are fine; attachments on different proxy or target endpoints are
fine; and within a single flow, attachments with different `<Condition>` values are fine.

The general lesson is that mutual exclusion lives in the routing and in the condition, not in the
attachment count. A static count of policy occurrences is not a model of request flow.

#### Correct remediation

Do not remove the attachments. They are correct and removing them would leave routes uncovered.

On apigeelint v2.36.0 or later the rule already models this and no action is needed. On older
versions, exclude PO023 for this proxy rather than restructuring correct policy attachment.

#### Verification

Re-lint at v2.36.0 or later and confirm PO023 no longer fires. Then check the counter directly:
issue a request down one branch and confirm exactly one increment, which distinguishes this from a
genuine double-counting defect rather than assuming it.

#### Common incorrect answers

Removing the duplicate attachments to satisfy the linter. Some routing branches would then have
no quota at all, and the traffic complaint would still be unexplained.

Treating the lint finding as the explanation for the customer's count complaint. The finding is
about bundle structure; the count is about runtime. They are two separate questions and the agent
should say which one the evidence answers.

Assuming that attaching a quota to more than one target always double counts. Targets are
mutually exclusive in the routing.

Ignoring conditions entirely. Two attachments in the same flow with the same condition genuinely
are a problem, because both would execute.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Removes attachments | Says the count is not inflated | Explains static attachment counting versus runtime execution, including conditions and targets |
| Diagnostic method | Accepts the lint message | Counts the attachments | Reads the Condition elements and the endpoints the attachments sit on |
| Handling of the traffic claim | Assumes the lint message explains it | Notes they are separate | Separates the two questions and says what evidence would answer the counting one |
| Quality of next step | Deletes policies | Upgrades the linter | Upgrades the linter or excludes PO023, leaves the attachments intact, verifies counting separately |

#### Critical failures: deleting correct policy attachments to silence a lint rule; presenting the
lint finding as the cause of the customer's counting complaint; ignoring `<Condition>` and
declaring all reuse of the same quota in one flow safe.

#### References

- Real report, the maintainer's description of the corrected algorithm, and two reporter
  confirmations:
  <https://github.com/apigee/apigeelint/issues/168>
- Quota policy reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
- Comparing Quota and SpikeArrest policies:
  <https://cloud.google.com/apigee/docs/api-platform/develop/comparing-quota-and-spike-arrest-policies>

---

### MED-26. A deployment fails with a Java callout error, and the build tool corrupted the artifact

#### Scenario metadata

- ID: MED-26
- Difficulty: medium
- Primary topic: Java callout packaging and build pipelines
- Secondary topics: deployment troubleshooting, Maven, artifact integrity, support boundaries
- Product: Apigee
- Origin: reported real-world case (apigee/apigee-deploy-maven-plugin#155, still open; root cause
  identified by a second reporter, not by Apigee or by the plugin maintainer)
- Versions: checked 2026-10-12; apigee-edge-maven-plugin 2.3.1 named in the report
- Evaluation objectives: two wrong conclusions are available and both are plausible. The obvious
  one is that the bundle activated slowly and should be retried; the second, which the reporter
  himself drew and which support formally endorsed as the only place to look, is that the
  deployment plugin is at fault. Neither holds
- Skills expected: apigee-support-core, references/policy-mechanics.md

#### Initial support ticket

> Our Maven deploy fails. The UI says the revision is deployed but traffic cannot flow. Support
> told us it is a Java callout instantiation failure and said they cannot look further because the
> deployment plugin is open source. Uploading the same jar by hand works every time. Where do we
> look?

#### Initial evidence

Three messages for one deployment. The UI shows `Error in deployment for environment dev. The
revision is deployed, but traffic cannot flow`. Maven reports `Deployment failed: Bundle did not
activate within the expected time. Please check deployment status manually before trying again`.
The deployments API, queried directly, reports `JavaCalloutInstantiationFailed`.

#### Expected investigation

The agent should note that "the revision is deployed, but traffic cannot flow" and "the bundle did
not activate" are not two symptoms, they are one, and the message inviting a retry is misleading:
the bundle will never activate, so retrying produces the same result indefinitely.

The fault prefix identifies the policy, not the reason. The Java Callout policy page states the
cause of `JavaCalloutInstantiationFailed` as "The class file specified in the `<ClassName>`
element is not in the jar", and it is a deployment error, not a runtime fault. So the jar is
in the bundle and the class cannot be loaded out of it. That has a small number of causes,
and a corrupted jar is one of them.

#### Diagnostic evidence

```terminal
# Is the jar in the bundle byte-identical to the one in the repository?
unzip -p target/apiproxy/resources/java/edge-micro-javacallout.jar \
    io/apigee/microgateway/javacallout/Callout.class | head -c 64 | xxd | head
# 7f454c46 is the ELF magic, 4a6f736e is ".json" - a text header where a class header must be
```

The class file in the packaged jar begins with text rather than the `CAFEBABE` class magic. It is
a valid text file that used to be a valid class file. The upload that works by hand is a different
byte sequence from the one the pipeline produced, which is what makes this a packaging defect
rather than an Apigee defect.

#### Ground-truth resolution

The gateway is fine and the bundle layout is fine. The build is rewriting the binary. A resource
filter applied to a directory containing a jar treats the jar as text, substitutes placeholders,
and writes it back. The result is a well-formed zip containing a corrupted class, so the runtime
loads the jar, finds the entry, and fails to instantiate the class.

The diagnostic detail is the disagreement between paths. If a manual UI upload of the same jar
works, the gateway, the policy, the class name and the keystore are all exonerated. That leaves
one variable, the bytes. And if the bytes differ between the pipeline artifact and the uploaded
one, nothing in Apigee can explain a difference that exists before the upload.

This is worth separating from the original poster's conclusion. The original report states that
the problem "is pointing to the problem in Maven deployment plugin", and Apigee support declined
further investigation on exactly that basis. A second reporter found the cause in their own POM and
said so honestly: they had `<filtering>true</filtering>` on a directory that included the jar, and
disabling filtering fixed it, while noting it was unlikely to be the original poster's exact issue.

#### Correct remediation

Exclude binary resources from filtering. Scope resource filtering to the directories that
actually contain text templates, or turn it off and do substitutions explicitly. Then rebuild and
redeploy.

Keep binary artifacts out of any text-processing step, including token replacement, property
interpolation and archive repacking that rewrites entries.

#### Verification

Rebuild and verify the class magic bytes in the packaged jar before deploying. Confirm the
deployment reaches a state other than ERROR, and confirm the callout executes by exercising the
path that runs it, since a deployment can succeed with a policy that never runs.

#### Common incorrect answers

Retrying the deployment. The activation timeout message invites this and it cannot succeed; it only
produces more failed revisions.

Upgrading the deployment Maven plugin, which is what the original report and the support response
both pointed at. The artifact was already corrupted before the plugin ever saw it.

Assuming the class name, the jar path or the policy XML is wrong because the error names a class.
The documented cause of this error is already a missing or unreadable class file, so pointing at
the class name restates the error rather than testing it. `ResourceDoesNotExist` is a different
error and refers to the `<ResourceURL>` element, not to the class.

Rebuilding the jar by hand or uploading it through the UI and declaring victory. That works once
and leaves the pipeline broken, so the next deploy fails again.

Assuming the deployment plugin is at fault because support said so. Check the artifact before
accepting the boundary; the defect was in the reporter's build configuration.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Retries the deployment | Blames the plugin | Identifies binary corruption during packaging and names filtering as the mechanism |
| Diagnostic method | Trusts the timeout message | Compares manual upload to pipeline | Inspects the packaged jar bytes and the class magic |
| Handling of support's boundary | Accepts the escalation | Still escalates | Checks the artifact before accepting the boundary, and explains why the gateway is exonerated |
| Quality of next step | Uploads by hand | Upgrades the plugin | Scopes filtering to text resources and rebuilds, then verifies the bytes |

#### Critical failures: recommending a retry loop; concluding that the open source deployment plugin
is at fault without inspecting the packaged artifact; editing the policy XML or the class name in
response to an instantiation failure.

#### References

- Real report, with the identical symptom reported by a second user and the filtering cause:
  <https://github.com/apigee/apigee-deploy-maven-plugin/issues/155>
- JavaCallout policy reference and its error conditions:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/java-callout-policy>
- Fault code index, `JavaCalloutInstantiationFailed`:
  `.agents/skills/apigee-support-core/references/error-codes.md`

---

### MED-27. The deployment tool says it succeeded, and the revision is in ERROR

#### Scenario metadata

- ID: MED-27
- Difficulty: medium
- Primary topic: deployment automation and result verification
- Secondary topics: shared flows, bundle paths, CI pipelines, state that is not reported
- Product: Apigee
- Origin: reported real-world case (apigee/apigeecli#276, fixed by the relative-path fix, shipped
  and confirmed by the reporter; a companion issue #273 was closed as a duplicate)
- Versions: checked 2026-10-12; reported against apigeecli 1.122, fixed from v1.124.0
- Evaluation objectives: three wrong conclusions are available, including the socially cheap one,
  which is to declare it unreproducible. The maintainers took that route twice and were wrong.
  The evidence needed is already in the error string
- Skills expected: apigee-support-core

#### Initial support ticket

> Our shared flow deploys. The command prints the deploy response and returns success. The revision
> shows as ERROR in the UI with "Failed to load file". We only see it because someone checked.
> Nothing in our pipeline would catch this.

#### Initial evidence

The create succeeds. The deploy command prints a response containing an environment name, a proxy
name, a revision number and a start time, and the pipeline continues. A direct query of the
deployments resource for that revision returns a state of ERROR with a per-instance error naming a
file inside the shared flows directory that does not exist in the bundle. The failure only occurs
when the bundle path given to the create step begins with a dot-slash prefix.

#### Expected investigation

The agent should separate three distinct signals that are being conflated: the HTTP result of the
deploy call, the state of the resulting revision, and the exit status of the command. Only the
first is present in the tool output. The deployments resource carries the other two.

It should also resist closing the case as unreproducible. Reproducing this requires reproducing
the reporter's environment, which is the point.

#### Diagnostic evidence

```terminal
apigeecli sharedflows listdeploy -e "$ENV" -n "$SF" -o "$ORG" -r "$REV"
```

The response contains a state field that is not ERROR on a healthy deployment, and an errors array
on an unhealthy one. The path inside the error message begins at the root of the shared flows
directory rather than relative to the submitted bundle, and the filename in that path does not match
the bundle's own XML filename. A path that is neither a real bundle entry nor the path the user
typed means the stored path was derived from something other than the bundle contents.

#### Ground-truth resolution

Two failures are stacked here and they need separate answers.

The first is that the deploy reported success. The deploy call only confirms that a deployment was
started. It does not confirm activation, so a pipeline that checks the command's exit status is
checking the wrong thing. The revision state is the real result and it has to be queried.

The second is why the revision went to ERROR. The bundle path was stored with its local form
intact, so the runtime looked for the bundle's XML at a location that does not correspond to
anything the user submitted. Because the path is derived from the local input, the filename in the
error changes with the input, which is why it looked random to the reporter.

The social pressure in this case is the part worth naming. Two maintainers tried to reproduce it
on their own machines, on two separate days, with the same version, and failed, and said so. The
natural conclusion was that the reporter's environment was unusual. The reporter's own experiment
disproved the universal version of that: the identical commands against the repository's own test
bundle worked, and the same commands against a copy of that bundle placed elsewhere in his own
repository did not. So the difference was in the input path, not in the tool or the organisation.

#### Correct remediation

Verify every deployment by reading the revision state from the deployments resource after the
deploy call, and fail the pipeline on anything other than a healthy state. Where the tooling
supports it, use the option that waits for the deployment to complete rather than returning as
soon as it starts.

For the underlying defect, normalise the bundle path before it is stored so the submitted local
form does not survive into the deployment record. The fix shipped in apigeecli v1.124.0 as a
change to how bundle paths with relative prefixes are handled.

#### Verification

Confirm the deploy command's exit status is non-zero when a deployment fails, by forcing a failure
such as an unrecoverable error in the bundle, and confirm the pipeline goes red. Then confirm a
successful run reports a healthy revision state and not merely a start time.

#### Common incorrect answers

Trusting the deploy command's output because it printed a JSON object. It prints the same shape for
a revision that is about to fail.

Declaring it unreproducible because the maintainers could not reproduce it. That was tried, twice,
and was wrong. Reproduction on a clean checkout of the sample bundle is not reproduction of the
reporter's path.

Rebuilding the shared flow from scratch or re-importing it, which clears the revision and the bad
stored path together and masks the defect for one more deploy.

Blaming the shared flow configuration. The policy list in the created entity is correct and the
failure is a file path inside the deployment.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Trusts the tool output | Queries the revision state | Separates deploy accepted, revision state, and exit status as three signals |
| Diagnostic method | Declares it unreproducible | Re-runs the commands | Reads the failing path in the error and concludes it was not derived from the bundle |
| Handling of non-reproduction | Closes the case | Asks for more detail | Treats non-reproduction as a statement about the environment and identifies the discriminating variable |
| Quality of next step | Re-imports the flow | Adds a state check | Waits for and asserts revision state in the pipeline, and normalises the bundle path |

#### Critical failures: accepting the deploy response as proof the revision is live; closing the
case as unreproducible on the basis of clean-environment attempts; removing the bad revision
without adding a state check so the next failure is silent again.

#### References

- Real report, with the maintainers' failed reproductions, the reporter's discriminating
  experiment, the merged fix and his confirmation:
  <https://github.com/apigee/apigeecli/issues/276>
- The duplicate report, which records that the command "will exit fine and act as though it
  deploys":
  <https://github.com/apigee/apigeecli/issues/273>
- Deployments resource reference:
  <https://cloud.google.com/apigee/docs/api-platform/deploy/ui-deploy-overview>

---

### MED-28. Provisioning over mutual TLS succeeds, then the tool fails its own verification

#### Scenario metadata

- ID: MED-28
- Difficulty: medium
- Primary topic: Edge for Private Cloud and hybrid provisioning
- Secondary topics: mutual TLS, client certificates, verification semantics, runtime differences
- Product: Edge for Private Cloud, hybrid
- Origin: reported real-world case (apigee/apigee-remote-service-cli#261, open with no maintainer
  response; the structural claim was verified against the published source)
- Versions: checked 2026-10-12; issue filed 2025-01-09 with no version stated
- Evaluation objectives: the failure appears in the verification step, which invites the
  conclusion that provisioning failed and should be retried. It did not fail. The tool then fails
  differently depending on runtime type, which is the part the report itself missed
- Skills expected: apigee-opdk-troubleshooter, apigee-support-core, references/security.md

#### Initial support ticket

> We provision a private cloud tenant with mutual TLS. The proxies and key value maps are created
> fine, and then the tool reports HTTP 400 during its verification step and the command fails. We
> are told to check deployment status. Is the provision actually broken?

#### Initial evidence

Provisioning with a client certificate, key and CA succeeds for the proxy resources and the key
value map. The tool then calls its own verification endpoints and gets 400. External calls with
the same certificate succeed, so the chain is trusted at the operating system level.

#### Expected investigation

The agent should notice that the tool is reporting two different things in one run, and that the
second thing happens after the first has already succeeded. Retrying is not indicated, and
"check deployment status" is the wrong next step because the deployment completed.

It should then work out what the verification requests actually carry, and what the tool considers
an acceptable verification result.

#### Diagnostic evidence

```terminal
apigee-remote-service-cli provision --tls-cert client.crt --tls-key client.key --tls-ca ca.crt ...
# ... resources created ...
# verification: GET /certs -> 400, GET /products -> 400, POST /verifyApiKey -> 400
```

Two details from the tool's own behaviour. First, verification explicitly tolerates 401 and 500
and treats them as acceptable outcomes, because a missing secret or an invalid key legitimately
produces those. A 400 is outside the tolerated set, which means the request reached the gateway
and was rejected for a reason the tool never expected. Second, and more important: the command
returns the verification errors on SaaS and Edge for Private Cloud, but on hybrid it prints them
as a warning and exits successfully. The same 400 is a command failure in one runtime and a
non-event in another.

#### Ground-truth resolution

The provisioning leg and the verification leg do not use the same TLS configuration. The client
that performs verification is built with a transport that only sets the skip-verification option;
it never loads the client certificate and key into the TLS configuration, so no client certificate
is presented on the verification requests. On a gateway configured to require mutual TLS, a
request without a client certificate is rejected, and the rejection surfaces as a 400 rather than
the 401 or 500 the tool knows how to interpret.

Two conclusions follow, and the second is the one that catches people. First, the environment is
not broken and the resources were created; the 400s are from the tool checking its own work.
Second, whether this matters depends entirely on runtime type. On hybrid the command succeeds
despite the 400s, so an operator can see a clean run that verified nothing. On SaaS and Edge for
Private Cloud the same run fails, so the same environment produces a different operational
outcome.

The report is also useful as an example of what not to do with a claim. It contains a version
template that the reporter never filled in, no maintainer has replied, and the thread has zero
comments. The structural claim checks out against the source, but nothing about it has been
confirmed by anyone with authority over the tool.

#### Correct remediation

Verify by hand, from outside the tool, with the client certificate presented, so the question of
whether the environment is correct is answered independently of the tool's own check.

Treat a verification failure on hybrid as a warning to investigate, not as a success, because the
tool does not fail the run. If the tool's verification is not presenting the client certificate,
treat every successful hybrid provision as unverified until an out-of-band check confirms it.

#### Verification

From a host outside the provisioning container, call the verification endpoints with the client
certificate, key and CA supplied, and confirm the responses are the tolerated 401 or 500 rather
than a 400. On hybrid, record that the tool's exit status is not evidence of verification.

#### Common incorrect answers

Re-running the provision command. The resources were created successfully; repeating it changes
nothing and risks creating duplicates.

Telling the operator to check deployment status of the proxy. The proxy deployed. The failure came
from a verification call the tool made after the deployment finished.

Rotating or re-importing the client certificate or truststore. External calls with the same
certificate succeed, so the material is fine.

Reading a successful hybrid provision as proof that verification passed. On hybrid the tool does not
return verification errors, so a clean exit code carries no verification information.

Installing the client certificate system-wide to work around it. The gap is that the tool's own HTTP
client is not configured with it.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Re-runs provisioning | Identifies it as a verification failure | Identifies the missing client certificate on the verification leg and says provisioning succeeded |
| Diagnostic method | Rotates certificates | Compares with external calls | Notes that 401 and 500 are tolerated and 400 is not, and reads the path in the tool |
| Product handling | Gives one answer | Notices runtime differences | States that hybrid returns success despite the failures and SaaS and OPDK do not |
| Quality of next step | Re-provisions | Upgrades the tool | Verifies out of band with the client certificate and treats hybrid success as unverified |

#### Critical failures: telling the operator the provision failed and to retry; treating a
successful hybrid provision as verified; rotating valid certificate material because the tool's own
client is misconfigured.

#### References

- Real report, with the code location and the two verification endpoints:
  <https://github.com/apigee/apigee-remote-service-cli/issues/261>
- Provisioning a tenant with Edge for Private Cloud:
  <https://cloud.google.com/apigee/docs/hybrid/latest/upgrade>
- Hybrid architecture and gateway components:
  <https://cloud.google.com/apigee/docs/hybrid/latest/config-prop-ref>

---

### MED-29. The same TLS error, two different causes, and the accepted fix works for one of them

#### Scenario metadata

- ID: MED-29
- Difficulty: medium
- Primary topic: TLS trust and certificate validation from the client side
- Secondary topics: corporate proxies, tooling flags, private deployments
- Product: Edge for Private Cloud
- Origin: reported real-world cases (apigee/apigeetool-node#6, merged and confirmed;
  apigee/apigeetool-node#33, still open, where the same fix was tried and did not work)
- Versions: checked 2026-10-12; reported 2014-12 and 2015-12 against the Node tool of that era
- Evaluation objectives: two reports with nearly identical symptoms and opposite remedies. An
  agent that learned the first answer will confidently give the wrong one for the second. The
  discriminator is environmental and must be elicited, not assumed
- Skills expected: apigee-opdk-troubleshooter, apigee-support-core, references/security.md

#### Initial support ticket

> Our Apigee deployment tool cannot connect to the runtime. It fails on TLS verification. We need
> to deploy to a private instance behind our corporate firewall. Someone told us there is a flag to
> skip certificate checking. It did not help.

#### Initial evidence

The tool fails on the outbound connection to the management endpoint. One variant of the error
names a leaf signature that cannot be verified. Another variant reports that the first certificate
in the chain cannot be verified. The host is reachable, credentials are accepted elsewhere, and the
same tool works from a network outside the corporate perimeter.

#### Expected investigation

The agent should resist the urge to treat "TLS verification failed" as a certificate validity
problem and start checking expiry and chain completeness on the server. In both real cases the
server certificate was fine.

It should ask what sits between the client and the endpoint, and specifically whether a TLS
terminating proxy re-signs traffic. That question separates the two cases, and it cannot be
answered from the error string.

#### Diagnostic evidence

```terminal
# from the affected host, compare the certificate the client actually receives
openssl s_client -connect mgmt.example.internal:443 -servername mgmt.example.internal </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -ext subjectAltName
```

In the working case the issuer is the organisation's own internal CA and the subject alternative
names match the hostname being requested. In the broken case the issuer is the corporate proxy,
the subject names the proxy, and there is an additional certificate in the chain that is not part
of the server's own PKI. The tool also works from a host with no route through the proxy, which
localises the fault to the path rather than the destination.

#### Ground-truth resolution

Two different problems that produce the same class of error.

Where the endpoint uses a private certificate authority that the client does not trust, the fix is
to give the tool the CA to validate against. A `cafile` option was added for exactly this, and the
original reporter confirmed it worked. This is the correct fix and it keeps verification on.

Where a corporate proxy terminates TLS and presents a certificate for itself, suppressing
validation is not the same operation as trusting the internal CA. Chain validation and hostname
identity are separate checks, and the presented certificate fails the identity check regardless of
how much chain validation is relaxed. Adding the corporate root to the trust store works because it
makes the proxy's own certificate legitimately valid for the connection. A reporter who tried the
skip-verification option in this case reported that it did not solve the problem and that other
errors resulted.

The trap is that the popular answer generalises. In the real thread the reporter of the second
case explicitly asked whether the fix from the first case applied, and the answer recorded in the
thread is that it did not.

#### Correct remediation

First establish which case applies, by inspecting the certificate the client actually receives from
the affected host.

If the endpoint's own CA is simply untrusted, supply that CA to the tool and keep verification
enabled. This is the preferred outcome and it should be reached whenever possible.

If a TLS-intercepting proxy is in the path, add the corporate root CA to the host trust store so
the connection is genuinely valid. Treat disabling verification as a last resort scoped to the one
endpoint and one host, never as a global default, and say plainly that it removes the protection
that would otherwise detect interception.

#### Verification

From the affected host, confirm the certificate presented is the one expected and that its issuer
chains to a CA the host already trusts. Then connect with the tool and confirm both that it
succeeds and that validation is still enabled, so the fix has not been to stop checking.

#### Common incorrect answers

Recommending the skip-verification flag as the standard fix because a similar error was solved that
way. In the interception case it does not address hostname identity, and a reporter who tried it
reported it did not work.

Adding the endpoint's own certificate to the trust store in the interception case. The endpoint's
certificate is never presented, because the proxy's is.

Treating this as a server certificate expiry or chain problem. Both reports had working server-side
certificates and a working tool outside the perimeter.

Setting a package manager's strict-TLS setting to false. That governs the package manager's own
downloads, not the deployment tool's outbound connection to the management endpoint.

Claiming the gateway's TLS is misconfigured. The gateway is fine; the client's view of the chain
is not.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Disables verification | Offers the CA file option | Distinguishes an untrusted internal CA from a TLS-intercepting proxy and gives the matching fix |
| Diagnostic method | Checks server certificate dates | Asks about the network path | Inspects the certificate actually presented from the affected host and compares subject and issuer |
| Handling of the prior answer | Repeats the flag advice | Recommends it as a fallback | States why the same remedy does not generalise across the two cases |
| Quality of next step | Turns validation off globally | Supplies the CA | Supplies the corporate root so validation stays on, and scopes any fallback explicitly |

#### Critical failures: disabling certificate verification as the default recommendation; assuming
the two cases share a remedy because the error text is the same; attributing the failure to the
gateway certificate.

#### References

- Report of the certificate authority option, with the merged change and the reporter's
  confirmation:
  <https://github.com/apigee/apigeetool-node/issues/6>
- Report of the corporate-firewall case where that option did not help:
  <https://github.com/apigee/apigeetool-node/issues/33>
- Protecting credentials with TLS in Edge for Private Cloud:
  <https://cloud.google.com/apigee/docs/hybrid/latest/scale-and-autoscale>

---

### MED-30. The token endpoint is correct and the client is sending a malformed header

#### Scenario metadata

- ID: MED-30
- Difficulty: medium
- Primary topic: OAuth 2.0 token issuance and RFC compliance
- Secondary topics: developer portals, SDK behaviour, interoperability, version-specific response shapes
- Product: Apigee
- Origin: reported real-world case (apigee/apigee-api-catalog-drupal#46, still open; the behaviour
  is now documented in the OAuthV2 policy reference and a documented defect was closed in Dec 2020)
- Versions: checked 2026-10-12; the behaviour is the documented default and still applies unless
  RFC compliance is requested
- Evaluation objectives: the failure surfaces in a downstream system and looks like an integration
  bug in that system. The token endpoint is behaving exactly as documented, and the fix is one
  element that also changes two other response shapes the customer has not audited
- Skills expected: apigee-support-core, references/policy-mechanics.md

#### Initial support ticket

> Calls to our backend are being rejected as unauthorised. We only see it through our developer
> portal and our generated SDKs. The token endpoint looks fine and our own tests pass. What is
> going on?

#### Initial evidence

The token endpoint returns a successful response containing a token type field whose value is
`BearerToken` rather than `Bearer`. A client that echoes the token type back verbatim constructs an
authorization header of `BearerToken <token>` instead of `Bearer <token>`. The portal's API
console and the generated SDK both do exactly that. Other consumers of the same token endpoint work
correctly.

#### Expected investigation

The agent should resist treating this as a backend authorization problem, and should resist
assuming the portal or the SDK is broken. Both are behaving reasonably given what they were
handed: the specification's token type is a value to be used as returned, and this value is not
the specified one.

The question to ask is what the token endpoint returned, not what failed downstream.

#### Diagnostic evidence

```terminal
curl -s -X POST "$TOKEN_URL" -d grant_type=client_credentials -u "$CLIENT:$SECRET" | jq .token_type
# "BearerToken"

curl -s -X POST "$TOKEN_URL" -d grant_type=client_credentials -u "$CLIENT:$SECRET" \
  | jq '{expires_in_type: (.expires_in|type), refresh_type: (.refresh_token_expires_in|type)}'
# expires_in_type: "string"
# refresh_type: "string"
```

Both facts matter. The token type is non-compliant, and the lifetime values are serialised as
quoted strings rather than numbers.

#### Ground-truth resolution

This is documented behaviour, not a defect. The OAuthV2 policy reference documents a
non-compliance section and states that by default the policy exhibits non-RFC-compliant behaviour,
and that this is the default. The documented differences are four: the token type value, the
absence of cache-control headers, the lifetime values being quoted strings, and the shape of the
error returned for an expired refresh token.

The last one is the trap that makes this more than a token type fix. Enabling compliance changes
the expired-refresh-token error from a proprietary shape to the standard shape. Any client, log
parser, dashboard or alerting rule that matches on the non-compliant shape will stop matching the
moment compliance is switched on. Enabling this element is a client-visible behaviour change across
all four fields at once, and it should be presented as one.

The documentation itself lagged the behaviour by more than a year. The issue records the behaviour
being reported in 2019, the documentation being updated in November 2019, and the underlying
documentation defect not closing until December 2020. That gap is why this looked like an
unsolvable bug to the people who hit it.

#### Correct remediation

Set the compliance element on the token-generating policy:

```xml
<RFCCompliantRequestResponse>true</RFCCompliantRequestResponse>
```

Then audit every consumer before and after, because four fields change at once:

- the token type value becomes `Bearer`;
- lifetime values become numbers instead of quoted strings, which breaks consumers doing string
  comparison on them;
- cache-control headers appear on responses containing tokens;
- the expired-refresh-token error changes shape, which breaks anything matching on the previous
  field names.

If the token endpoint must keep the legacy shape for an existing consumer, issue compliant tokens
from a separate endpoint or on a separate API product rather than changing the endpoint in place.

#### Verification

Request a token and confirm the token type is `Bearer`. Confirm the lifetime values are serialised
as numbers. Then exercise an expired refresh token and confirm the error carries the standard
fields. Confirm a client that echoes the token type back now constructs a correct authorization
header.

#### Common incorrect answers

Fixing the developer portal or regenerating the SDKs. Both are consuming the token type as
supplied, which is what the specification asks them to do.

Raising the backend or the API key policy, since the symptom is a 401 downstream. Nothing about the
credential is wrong; the header is malformed before it reaches the backend.

Switching compliance on without auditing consumers. It fixes the header and breaks anything
matching the previous error field names or comparing lifetime values as strings.

Assuming this is an Apigee bug and filing it. The behaviour is documented and the documentation
describes this element as the way to change it.

Treating only the token type as the difference. The other three changes ship with it.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Fixes the portal or SDK | Names the token type | Identifies the documented default and enumerates all four fields that change |
| Diagnostic method | Investigates the backend | Inspects the token response | Inspects the raw token response and the value types of the lifetime fields |
| Handling of the change | Sets compliance immediately | Sets compliance and warns | Presents it as a client-visible behaviour change and audits consumers for all four fields |
| Quality of next step | Tells the customer to regenerate SDKs | Sets the element | Sets the element and enumerates the downstream audit, with a separate endpoint as the safe alternative |

#### Critical failures: editing the developer portal or SDKs instead of the token endpoint;
enabling compliance without warning that the error response shape and the lifetime value types
also change; describing the non-compliant default as an Apigee defect.

#### References

- Real report of the non-compliant token type affecting a portal and SDKs:
  <https://github.com/apigee/apigee-api-catalog-drupal/issues/46>
- OAuthV2 policy reference, non-RFC-compliant behaviour and the compliance element:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>
- OAuth 2.0 access token overview:
  <https://cloud.google.com/apigee/docs/api-platform/security/oauth/access-tokens>

---

### MED-40. Two green deploys, one invisible conflict

#### Scenario metadata

- ID: MED-40
- Difficulty: medium
- Primary topic: environment groups and base paths
- Secondary topics: deployment state, routing, silent misconfiguration
- Product: Apigee
- Origin: reported real-world case (official known issue 300660653, closed as FIXED)
- Versions: checked 2026-10-12
- Evaluation objectives: every deploy signal is green. The only thing that is wrong is
  something Apigee declines to report. The correct move is to distrust the absence of an error,
  not to look for a failing deploy
- Skills expected: apigee-support-core

#### Initial support ticket

> We deployed `/v1/orders` to `prod` last month and it works. This week we deployed `/v1/orders`
> to `uat`. Both deploy calls returned success and both show as deployed. Now traffic for one of
> them 404s and we cannot tell which. Nobody can tell us which proxy is at fault. Can you check
> the deployments?

#### Initial evidence

The Management API reports both revisions deployed in their respective environments. Both
environments are attached to the same environment group. Requests to one proxy host resolve and
succeed. Requests to the other return 404. No error is logged at deploy time or since.

#### Expected investigation

The agent should resist the invitation to inspect deployments, because deployments are not the
thing that is wrong. It should notice that "which one 404s" is the actual question, and that
this is an address-resolution problem caused by two proxies claiming one base path within a
single instance and environment group.

#### Diagnostic evidence

Both environments are members of the same environment group, and both environments belong to the
same Apigee instance. Both proxies declare the identical base path `/v1/orders`. No deployment
error was ever produced because Apigee does not raise one for this case.

#### Ground-truth resolution

This is a documented limitation, not a broken deployment. Deploying proxies with the same path
to multiple environments attached to the same instance and environment group is not allowed, and
should return a warning about a base path conflict. It does not. Instead, no error is shown and
the deployments appear to succeed.

That wording is the whole lesson: the deploy genuinely succeeded, and the platform has recorded
an ambiguity it will later resolve by choosing one winner. The loser 404s. The 404 is correct
behaviour for an undefined routing situation, not a routing fault.

An agent that treats "deploy succeeded" as proof that the environment is consistent has adopted
the exact assumption the register warns against. Note also that this produces no fault code, so
there is nothing in any error-code index to grep for.

#### Correct remediation

Rename the base path on one of the two proxies so the two are distinct, and redeploy that one.
Renaming the path is a routing change that clients depend on, so it needs to be scheduled with
the owning team rather than applied as a reflex.

Going forward, verify after each deployment that no other proxy in the same environment group
claims the same base path. There is no platform warning to rely on, because there is no platform
warning.

#### Verification

Send a request to each proxy host and confirm both resolve. Then confirm no other proxy in the
group shares either base path, since a third conflict is as invisible as the first.

#### Common incorrect answers

Redeploying both proxies. Redeployment is not the defect and will reproduce the same state.

Recommending a redeploy as a "clean slate". There is nothing to clean; the conflict is in the
declared paths.

Looking for a routing or environment-group misconfiguration. The group is correctly configured
and both attachments are correct.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Redeploys | Identifies duplicate base paths | States it is an unreported base path conflict within one instance and environment group |
| Diagnostic method | Re-runs the deploys | Compares the two base paths | Confirms shared instance, shared group, and identical declared path |
| Handling of the green deploy | Trusts it | Doubts it | Explains why the absence of an error is the defect |
| Quality of next step | Restarts or redeploys | Asks the team to rename a path | Names the path change, the client impact, and the missing verification step |

#### Critical failures: recommending a redeploy as the fix; treating a successful deployment as
proof the environment is internally consistent.

Not a critical failure: not being able to say which proxy 404s. That is exactly the customer
problem, and the register gives no way to determine it.

#### References

- Known issues register (entry 300660653):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Environment groups:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/environmentgroups-working-with>

---

### MED-41. "Operation group limit of 51 exceeded in Operation Config"

#### Scenario metadata

- ID: MED-41
- Difficulty: medium
- Primary topic: API products and resource paths
- Secondary topics: hard limits, error triage, monetization of the design
- Product: Apigee
- Origin: reported real-world case (official known issue 402739748, still OPEN)
- Versions: checked 2026-10-12
- Evaluation objectives: the error message is not an Apigee fault code, names a component the
  customer is not editing, and reports 51 when the limit is 50. An agent that treats it as a
  proxy fault, or that greps an error-code index for it, will fail
- Skills expected: apigee-support-core

#### Initial support ticket

> Our team tried to add a few more paths to an existing API product in the console. The save
> failed with `Operation group limit of 51 exceeded in Operation Config`. We did not change any
> proxy. Is our proxy misconfigured?

#### Initial evidence

An API product in one environment holds 50 resource paths. Adding a 51st fails on save. No proxy
was edited, no revision was deployed, and no runtime error exists because nothing reached the
runtime.

#### Expected investigation

The agent should locate the error in the API product rather than in any proxy, and should
recognise that the string is a limit-enforcement message rather than a runtime fault. There is
no `{"fault":{"detail":{"errorcode":...}}}` payload here at all.

#### Diagnostic evidence

The API product contains 50 paths. The message reads `Operation group limit of 51 exceeded in
Operation Config`. The count of 50 matches a documented limit exactly.

#### Ground-truth resolution

API products are limited to 50 paths. This is a limitation, not a defect, and it is still OPEN
on the register, so the correct answer is not to wait for a fix.

Two details deserve attention. The message says 51 because it reports the first value that
breaches a limit of 50, so "51" is the ceiling plus one and not an off-by-one bug. And
"Operation Config" is not an Apigee component a support engineer can look up; it is an internal
operation-config limit surfacing through the save path, which is why the message names something
the customer is not editing and why it appears in no Apigee fault-code reference.

An agent that reads "Operation Config" as a proxy or deployment component will go and inspect
proxies that were never touched.

#### Correct remediation

The first published workaround is to combine resource paths and operations using wildcard
patterns, which reduces the number of separate paths without changing what clients call.

The second is to create multiple API products. The register states this has been verified as
viable, and it includes the sentence that matters most operationally: the App associated with
the API products must be updated to include the new one, but credentials and client-side
request details have been proven not to need changing. That is what allows a support engineer to
tell the customer their existing clients are unaffected.

#### Verification

Save the API product and confirm the limit error is gone. Then confirm the App now references
every product a client needs, because that is the step the workaround actually requires and the
step most likely to be forgotten.

#### Common incorrect answers

Blaming the proxy. No proxy was modified and no proxy is misconfigured.

Treating "51" as a miscount and arguing the limit is really 51. The limit is 50; the message
reports the breaching value.

Searching for `Operation group limit` in an Apigee error-code index. It is not an Apigee error
code and will not be there.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Investigates the proxy | Identifies the API product path limit | Names the 50-path limit and explains the 51 in the message |
| Diagnostic method | Greps fault codes | Reads the message | Recognises it is a limit message, not a runtime fault payload |
| Product knowledge | Suggests a new environment | Suggests wildcards | Gives both published workarounds, including splitting into multiple products |
| Client impact | Advises re-issuing credentials | Says clients still work | States the App must be updated but credentials and client-side details do not change |

#### Critical failures: attributing the failure to a proxy; telling the customer their
credentials must be re-issued.

Not a critical failure: proposing multiple API products without noting the App update. It is an
oversight rather than a wrong answer, and the register itself flags the same omission in its own
second workaround.

#### References

- Known issues register (entry 402739748):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Configuring resource paths:
  <https://cloud.google.com/apigee/docs/api-platform/publish/create-api-products#behavior-resource-path>

---

### MED-42. The proxy limit that depends on how long your base paths are

#### Scenario metadata

- ID: MED-42
- Difficulty: medium
- Primary topic: deployment scale limits
- Secondary topics: environment groups, two-factor causation, counting rules
- Product: Apigee
- Origin: reported real-world cases (official known issues 301845257 and 329304975, both closed
  as FIXED)
- Versions: checked 2026-10-12
- Evaluation objectives: two hard limits are in play, they count different things, and one of
  them has a hidden second factor. Checking only the proxy count, or only the environment
  total, rules the case out incorrectly
- Skills expected: apigee-support-core

#### Initial support ticket

> I cannot deploy to my environment group. Two of our teams on the same Apigee org can deploy
> fine with the same number of proxies. We are not over any limit that I can find. Is the org
> full?

#### Initial evidence

One environment group holds 604 deployed proxies with base paths around 22 characters long. A
second environment group on the same org holds 604 proxies with short base paths and deploys
without error. The environment totals differ as well.

#### Expected investigation

The agent should establish that there are two independent documented ceilings, in different
scopes, counting different units. The discriminator is not the proxy count.

#### Diagnostic evidence

The failing environment group's base paths exceed 15 characters. The working group does not. The
environment containing the failing group has a total base path count above 1000, counting base
paths rather than revisions.

#### Ground-truth resolution

Two limitations are in play, both documented and both now closed.

First, attempting to deploy more than 800 proxies to an environment group fails with an error, and
the register adds the detail that actually matters: the limit at which an error is returned is
lower than 800 when the base paths are longer than 15 characters. Proxy count is therefore
necessary but not sufficient. Base path length is the second factor, and it is invisible in the
error the customer receives, which reports only that an error occurred.

Second, there is a limit of 1000 base paths per environment. The register is explicit that this
counts base paths and not revisions: "If your API proxies or revisions contain more than one
base path, the total number of base paths per environment must not exceed 1000." A revision
carrying four base paths consumes four slots.

Both are limitations described as a deliberate protective measure. The 1000-basepath limit is
introduced in the register as a temporary limit "to avoid potential failures when deploying API
proxy revisions". The word temporary should be quoted rather than promised.

The two groups on the same org are both compliant with the numbers a support engineer would
naturally check, which is why the ticket exists.

#### Correct remediation

Shorten base paths on the failing group if the owning teams can tolerate the client-visible
change, or split the group. Either reduces the effective proxy count against the length-adjusted
ceiling. Separately, count total base paths per environment rather than counting revisions,
since that is what the environment-level limit measures.

#### Verification

Deploy successfully to the failing group, then repeat the count across every environment in the
org, because the environment ceiling is per environment and a group split does not reset it.

#### Common incorrect answers

Comparing only the proxy count between the two groups. Both are 604 and the counts are not the
discriminator.

Raising a quota, ticket or support request. These are documented design limits, not a
capacity entitlement that can be negotiated.

Recounting revisions instead of base paths. A revision with several base paths consumes several
slots against the 1000 ceiling.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Diagnostic method | Compares proxy counts only | Notices base path length | Identifies both the 15-character factor and the per-environment 1000 base path limit |
| Technical correctness | Says the org is full | Names the 800 proxy limit | Explains the length-adjusted threshold and base path counting |
| Cross-group reasoning | Assumes shared org means shared limit | Notes the groups differ | Uses base path length as the discriminator between the two groups |
| Quality of next step | Opens a quota request | Advises shortening paths | Splits the group or shortens paths, and recounts per environment |

#### Critical failures: ruling the issue out after confirming both groups are under 800 proxies;
counting revisions instead of base paths.

#### References

- Known issues register (entries 301845257 and 329304975):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Environment groups:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/environmentgroups-working-with>

---

### MED-43. The 404 that a version bump does not fix

#### Scenario metadata

- ID: MED-43
- Difficulty: medium
- Primary topic: base path wildcards
- Secondary topics: opt-in fixes, routing precedence, version-gated behaviour
- Product: Apigee and Apigee hybrid
- Origin: reported real-world case (official known issue 378686709, FIXED but not enabled by
  default; hybrid 1.14.3 and 1.15.1 with a procedure required)
- Versions: checked 2026-10-12
- Evaluation objectives: the fix exists and the customer is on a version that contains it, and
  it is still 404ing, because the fix is opt-in. Version alone cannot discriminate here
- Skills expected: apigee-support-core, apigee-opdk-upgrader

#### Initial support ticket

> We upgraded hybrid to 1.14.3 last week to pick up the wildcard base path fix. `/a/v1/b` works.
> `/a/*/c` still returns 404. We are on a fixed version. What is going on?

#### Initial evidence

Two proxies in the same environment: `Proxy-1` with base path `/a/v1/b`, `Proxy-2` with base path
`/a/*/c`. Requests to `Proxy-1` resolve. Requests to `Proxy-2` return 404. Both are deployed and
listed. The environment group is healthy and other proxies on it serve traffic.

#### Expected investigation

The agent should notice that one of the two proxies in the same environment, on the same path
prefix, in the same deployment, works while the other does not. That asymmetry rules out the
environment group and the deployment and points at base path conflict resolution.

#### Diagnostic evidence

The wildcard path `/a/*/c` is being evaluated as `/a/v1/c`, which collides with the explicit
`/a/v1/b` prefix.

#### Ground-truth resolution

The use of wildcards in Apigee proxy base paths may conflict with other explicit base paths,
resulting in a `404`. In this case, calls to the explicit base path resolve successfully while
calls to `Proxy-2` may return a `404`, if the wildcard path is evaluated as `/a/v1/c`.

The important part is what the register says next: the issue is fixed in Apigee and in hybrid
1.14.3 and later, however the fix is **not enabled by default**. Enabling the use of wildcards
in base paths requires a support request for Apigee orgs, and a documented procedure for hybrid
orgs.

So the customer's premise is exactly wrong in the most confident possible way. They checked the
version, the version says fixed, and the fix has not been switched on for their org. An agent
that treats "fixed in 1.14.3" as "therefore not our problem" closes the case wrongly, and an
agent that recommends only an upgrade has already been given the upgrade.

Note the asymmetry that makes this hard to spot from the outside: an agent that establishes "the
environment group is serving traffic" has proved nothing, because a sibling proxy in the same
environment is serving fine.

#### Correct remediation

For an Apigee org, contact Apigee support to request that the wildcard base path fix be enabled.
For a hybrid org, follow the documented procedure for 1.14.3 or 1.15.1. Until then, remove the
wildcard and use explicit base paths, which is the only configuration guaranteed to be unambiguous.

#### Verification

Call the wildcard path and confirm it resolves. Then confirm the explicit path still resolves,
because the fix changes conflict resolution between them rather than in isolation.

#### Common incorrect answers

Recommending another upgrade. The customer is already on a version that contains the fix.

Concluding the environment group or the deployment is at fault. Other proxies on the same group
serve traffic, including a sibling on the same prefix.

Removing the conflicting explicit base path without asking. That is a client-visible breaking
change for whichever team owns it.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Recommends an upgrade | Identifies wildcard and explicit base path conflict | Names the `/a/v1/c` collision and the opt-in nature of the fix |
| Diagnostic method | Checks the group | Compares the two base paths | Uses the working-versus-failing asymmetry within one environment |
| Version handling | Reads "fixed" as resolved | Notices opt-in wording | States that hybrid 1.14.3 contains a fix that is disabled by default |
| Quality of next step | Upgrades again | Deletes the explicit path | Requests enablement for Apigee, follows the procedure for hybrid |

#### Critical failures: telling the customer to upgrade when they are already on a fixed version;
concluding the environment group is at fault because other proxies on it serve traffic.

#### References

- Known issues register (entry 378686709):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Upgrading Apigee hybrid: <https://cloud.google.com/apigee/docs/hybrid/v1.17/upgrade>

---

### MED-44. Headers that were removed, then put back, and are still pinned

#### Scenario metadata

- ID: MED-44
- Difficulty: medium
- Primary topic: distributed trace and `x-b3` headers
- Secondary topics: version-gated behaviour, relied-upon defaults, per-org pinning
- Product: Apigee and Apigee hybrid
- Origin: reported real-world case (official known issue 422757662, reverted in Apigee
  1-15-0-apigee-7 and the matching Apigee release)
- Versions: checked 2026-10-12
- Evaluation objectives: the behaviour is non-monotonic across versions and pinned per org, so
  neither "the version" nor "the org version" is sufficient. An agent must establish both
- Skills expected: apigee-support-core

#### Initial support ticket

> Our backend stopped receiving `x-b3` correlation headers last month. We did not change
> anything on the backend. Distributed Trace is switched off in our org, which I assumed meant
> nothing trace related was sent. Help me find what changed.

#### Initial evidence

`x-b3` headers are absent at the target. Distributed Trace is disabled in the org. No proxy
policy has been edited. The org was last upgraded recently.

#### Expected investigation

The agent should notice that the assumption embedded in the ticket, that a disabled Distributed
Trace implies no `x-b3` headers, is exactly the assumption the platform once stopped making and
then partially restored. It should establish the org's version and whether the reversion has been
pinned for this org.

#### Diagnostic evidence

The org is on a release in the affected window where the headers stopped being sent when
Distributed Trace is disabled. A sibling org on the same version that was pinned to the old
behaviour still receives the headers.

#### Ground-truth resolution

In Apigee 1-15-0-apigee-5 and hybrid 1.15.0, Apigee stopped sending `x-b3` headers to target
endpoints when Distributed Trace is disabled. Some installations were relying on `x-b3` headers
being sent regardless of whether Distributed Trace was enabled or disabled. The change was
therefore reverted starting in Apigee 1-15-0-apigee-7.

Three properties make this hard to resolve by version alone.

The behaviour is **non-monotonic**. It was present, it disappeared, it came back. "Fixed in
1-15-0-apigee-7" does not mean a newer org has the new behaviour; it means the removal was
undone. An agent that assumes the present state is the newest behaviour will be wrong twice.

The fix is **not enabled by default**. The register says that anyone experiencing the issue
should reach out to Apigee to revert the change for now in their org. That is a per-org pin. Two
orgs on the same version can behave differently, and version cannot tell them apart.

The headers were a **latent default in use**. Nobody configured them. They were injected because
something depended on them once, and nothing recorded that dependency.

The register closes with a caution worth surfacing to the customer: Apigee does not recommend
relying on `x-b3` headers when Distributed Trace is disabled, because doing so will not guard
against a future change to this behaviour.

#### Correct remediation

Ask Apigee to re-pin this org to the previous behaviour, as the register directs, and
simultaneously start removing the backend's dependence on `x-b3` headers. The reversion is a
reprieve with an explicit warning attached, not a permanent answer, and a support engineer who
applies only the first half is handing the customer the same problem later.

#### Verification

Confirm the target receives `x-b3` headers again, and confirm Distributed Trace remains disabled so
the change was not achieved by turning tracing on.

#### Common incorrect answers

Enabling Distributed Trace to get headers back. That changes the customer's tracing behaviour and
costs money to fix a correlation problem.

Asserting the org must be on 1-15-0-apigee-7 or later. The org may already be, and still be
affected, because the fix is per-org opt-in.

Telling the customer the header removal was a bug they must live with. It was reverted, at their
request, on request.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Enables Distributed Trace | Identifies the `x-b3` removal window | States it was reverted and that the reversion is per-org opt-in |
| Diagnostic method | Inspects proxy policies | Checks org version | Checks org version and whether the org is pinned to old behaviour |
| Version handling | Assumes newer means current behaviour | Notices the reversion | Recognises the behaviour is non-monotonic across versions |
| Quality of next step | Turns tracing on | Requests the pin | Requests the pin and starts removing the backend dependency |

#### Critical failures: enabling Distributed Trace as the remedy; concluding that an org on a
version at or past 1-15-0-apigee-7 cannot be affected.

Not a critical failure: recommending removing the `x-b3` dependency first, without requesting the
pin. It is the better long-term advice but does not restore the customer's current behaviour.

#### References

- Known issues register (entry 422757662):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Distributed trace: <https://cloud.google.com/apigee/docs/api-platform/debug/trace-overview>

---

### MED-45. `The URI contain illegal characters` after a version bump

#### Scenario metadata

- ID: MED-45
- Difficulty: medium
- Primary topic: proxy runtime HTTP handling
- Secondary topics: transitive dependency upgrades, request-side misdiagnosis
- Product: Apigee
- Origin: reported real-world case (official known issue 480997525, FIXED in Apigee
  1-17-0-apigee-2)
- Versions: checked 2026-10-12
- Evaluation objectives: a 400 that names the URI is blamed on the request. Nothing about the
  request changed. The discriminator is the Apigee version, not the traffic
- Skills expected: apigee-support-core

#### Initial support ticket

> Since the weekend upgrade roughly 40% of our API calls fail with `The URI contain illegal
> characters`. We looked at our base paths and our target URLs and they are all valid. We have
> not changed any URLs. Can you tell us which URL is malformed?

#### Initial evidence

Requests fail with status 400 and the message `The URI contain illegal characters`. Base paths,
target endpoints and request encoding are unchanged and valid. The failures started on a version
bump, with no proxy change.

#### Expected investigation

The agent should notice that the customer has already eliminated the request side, that the error
is a 400 pointing at the URI, and that the only thing that changed is the platform version. That
combination is the signature of a runtime dependency regression rather than a bad request.

#### Diagnostic evidence

The org is on Apigee 1-17-0-apigee-1. The proxy runtime in that release carries a Netty upgrade to
4.1.129.Final.

#### Ground-truth resolution

In Apigee version 1-17-0-apigee-1, a Netty upgrade to 4.1.129.Final introduced a regression. This
can cause API proxy calls to fail with a `400` status code and the error message `The URI contain
illegal characters`. It is tracked externally as netty/netty#16020.

The register quotes the string as `The URI contain illegal characters`, without the `s`. An agent
that silently corrects the grammar will fail an exact-match evaluation, so the string should be
quoted as it stands.

This is a bug, not a limitation, and it is fixed in the immediately following release. The
misdiagnosis risk is what makes it a medium scenario rather than a trivia question: a 400 with a
message about illegal URI characters points the engineer at the request, and the request is the
one thing that did not change. Chasing base paths, target URLs and header encoding is
well-reasoned and entirely wasted.

#### Correct remediation

Upgrade the org to Apigee 1-17-0-apigee-2. No proxy change is required and none should be made.

#### Verification

Confirm successful calls on a sample of the previously failing requests, then confirm the
unaffected traffic did not change behaviour, since the fix is in the shared runtime.

#### Common incorrect answers

Asking the customer to URL-encode a path segment. The URIs are valid and the platform broke.

Recommending a change to base paths or target endpoints. Any change here is a real client-visible
regression introduced while chasing a platform defect.

Recommending quoting the error as `The URI contains illegal characters`. It is the grammatical
form that does not appear.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Advises URL encoding | Identifies a runtime regression | Names the Netty 4.1.129.Final upgrade and 1-17-0-apigee-2 |
| Diagnostic method | Audits base paths | Checks the version | Checks the version against the single affected release |
| Error handling | Paraphrases the string | Quotes it correctly | Quotes `The URI contain illegal characters` verbatim and recognises it as client-side framing |
| Quality of next step | Changes proxy URLs | Recommends an upgrade | Recommends upgrading to 1-17-0-apigee-2 with no proxy change |

#### Critical failures: recommending a proxy or URL change; telling the customer their request is
malformed.

#### References

- Known issues register (entry 480997525):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Upstream issue: <https://github.com/netty/netty/issues/16020>

---

### MED-46. The 502 that means your certificate is bad

#### Scenario metadata

- ID: MED-46
- Difficulty: medium
- Primary topic: target endpoint TLS
- Secondary topics: status code semantics, component misattribution, certificate validation
- Product: Apigee hybrid
- Origin: reported real-world case (official known issue 310384001, still OPEN)
- Versions: checked 2026-10-12
- Evaluation objectives: the customer enabled certificate enforcement and is now told 502, which
  means upstream failure and sends the investigation to the wrong component. The correct reading
  is that the target certificate failed validation
- Skills expected: apigee-support-core, apigee-opdk-troubleshooter

#### Initial support ticket

> We turned on certificate checking on our target endpoint because we wanted to stop accepting
> expired certs. Now that backend returns 502 Bad Gateway. The host is up, it answers on 443, and
> the same URL works from a browser. The gateway cannot reach it.

#### Initial evidence

The target `<SSLInfo>` block contains `<Enforce>true</Enforce>`. The target responds to `502`. The
target is reachable and healthy by every other measure. The status code is 502 rather than the
503 that would suggest a target certificate problem.

#### Expected investigation

The agent should resist reading 502 as "upstream unavailable", because the target is demonstrably
available, and should look at what the customer's change actually asked the platform to do.

#### Diagnostic evidence

The target's certificate chain does not validate against the runtime's trust store. `<Enforce>` is
set to `true` in the target `<SSLInfo>` block, which selects default validation.

#### Ground-truth resolution

Cert validation failures may return a 502 instead of a 503 error response when users add the tag
`<Enforce>true</Enforce>` in the target `<SSLInfo>` block for default validation of TLS target
endpoint certificates. This is a limitation and it is still OPEN, so the correct answer is not to
wait for a fix.

The status code is actively misleading here, which is the whole point of the entry. A 502 reads
as "the upstream returned something unusable", so an engineer checks target health, L7 routing
and gateway reachability, and finds all of them fine, because nothing is down. The cause is the
target certificate, and the code conceals it.

It is also worth being precise about what the customer did. They added `<Enforce>true</Enforce>`
*because* they wanted certificate validation. They did not weaken it. Default validation is being
enforced and the platform is reporting the result with the wrong code.

A related documented behaviour from the same register, entry 205666368, states that Apigee hybrid
does not validate the target certificate by default. Read together the two entries say that the
default is no validation, and that turning validation on produces a misleading status code.

#### Correct remediation

Fix the target's certificate chain, or add the issuing authority to the appropriate truststore.
There is no configuration change that makes a 502 become a 503, because the code is the
platform's, and the register has the issue open rather than resolved.

#### Verification

Confirm the target certificate validates against the runtime trust store, then confirm the status
code is 200 or whatever the backend genuinely returns. Do not use the status code alone as proof,
since it is known to be wrong in this case.

#### Common incorrect answers

Investigating target availability and load balancing. The target is up; that is established.

Recommitting the proxy or restarting runtime pods. Neither changes certificate validation.

Telling the customer to remove `<Enforce>true</Enforce>` to make the error go away. That silently
returns them to no certificate validation at all, which is the opposite of what they asked for.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Investigates target availability | Suspects the certificate | States 502 here means target certificate validation failed |
| Diagnostic method | Trusts the status code | Notes the code contradicts the evidence | Recognises the documented 502-instead-of-503 behaviour with `<Enforce>` set |
| Component attribution | Blames the gateway | Blames the backend broadly | Blames the target certificate chain against the runtime trust store |
| Quality of next step | Removes `<Enforce>` | Suggests restarting pods | Fixes the chain or truststore, and does not disable enforcement |

#### Critical failures: advising removal of `<Enforce>true</Enforce>` as the fix; opening a load
balancing or gateway investigation and closing it as an upstream outage.

Not a critical failure: not knowing the corresponding 503. The register gives only the observed
502, and inferring the intended 503 is a bonus rather than a requirement.

#### References

- Known issues register (entries 310384001 and 205666368):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- API calls failing with TLS errors:
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/ingressgateway/api-calls-failing-tls-errors>

---

### MED-32. Six requests admitted where three per minute is configured

#### Scenario metadata

- ID: MED-32
- Difficulty: medium
- Primary topic: rate limiting, SpikeArrest policy
- Secondary topics: runtime topology, message processors, current vs legacy behaviour
- Product: Apigee
- Origin: reported real-world case
  (<https://stackoverflow.com/questions/23298849>), closed; the accepted answer is now
  contradicted by current documentation
- Versions: checked 2026-10-12
- Evaluation objectives: resist the high-reputation accepted answer that says SpikeArrest
  cannot be synchronised across message processors. The correct move is to read the policy
  definition for `<UseEffectiveCount>` before reasoning about topology at all. A second
  objective: notice that the widely cited `docs.apigee.com` comparison URL now serves
  Apigee Edge for Private Cloud documentation, not Apigee X.
- Skills expected: apigee-support-core

#### Initial support ticket

> We have an Apigee X organisation with six message processors. A SpikeArrest policy on our
> target endpoint is configured as:
>
> ```xml
> <SpikeArrest async="false" continueOnError="false" enabled="true" name="spikearrest-1">
>   <Identifier ref="request.header.some-header-name"/>
>   <MessageWeight ref="request.header.weight"/>
>   <Rate>3pm</Rate>
> </SpikeArrest>
> ```
>
> The documentation says 3 per minute means one request every 20 seconds. In production we
> are seeing six successful requests inside a 20 second window and then rejections. That is
> six requests where we asked for one. Is there any way to synchronise SpikeArrest across
> the message processors? We were told ConcurrentRateLimit would help and it does not.

#### Initial evidence

Six successful calls inside 20 seconds, then rejections, on a proxy with
`<Rate>3pm</Rate>`. The rejections carry
`{"fault":{"detail":{"errorcode":"policies.ratelimit.SpikeArrestViolation"}}}` with HTTP
429, which the local error index confirms at `error-codes.md` line 43, sourced to the
spike-arrest policy page. No `<UseEffectiveCount>` element is present in the policy.

#### Expected investigation

The agent should read the policy, not the topology. Six message processors is a true
observation and a distraction. The question that resolves this is what the SpikeArrest
policy is configured to do, and the answer is that with the default `<UseEffectiveCount>`
value the policy uses a token-bucket algorithm that smooths the configured rate into
smaller intervals and does not synchronise counts across message processors. Multiplying
the interval allowance by the number of message processors reproduces the reported
six-for-one exactly.

The agent should also resist the standing advice to move this to a Quota policy. That
advice was correct when written and is no longer complete.

#### Diagnostic evidence

```xml
<SpikeArrest async="false" continueOnError="false" enabled="true" name="spikearrest-1">
  <DisplayName>SpikeArrest-1</DisplayName>
  <Identifier ref="request.header.some-header-name"/>
  <MessageWeight ref="request.header.weight"/>
  <Rate>3pm</Rate>
</SpikeArrest>
```

No `<UseEffectiveCount>` element, so the policy is on the token-bucket branch. The current
spike-arrest policy reference states that per-minute rates are "smoothed into intervals of
seconds", that the smoothing algorithm "smooths traffic spikes by dividing the rate limit
that you specify into smaller intervals", and that "Smoothing is not coordinated across
Message Processors." With `3pm` that is one request per 20 seconds **per message
processor**, and six processors admit six.

#### Ground-truth resolution

The configuration is default, not broken. With `<UseEffectiveCount>` unset the policy
smooths, and smoothing is per message processor, so the effective admission rate is the
configured rate multiplied by the number of message processors. Six is what six
processors produce.

The accepted Stack Overflow answer to this exact report says, verbatim, "SpikeArrest has no
ability to be distributed across message processors", and its whole remedy is to abandon
SpikeArrest for the Quota policy, accepting that a distributed quota cannot be configured
per second. That is contradicted by current documentation, which documents the element
that does exactly what the answer says is impossible.

The agent should say the community answer is out of date rather than reproduce it, and
should not tell the customer the feature does not exist.

#### Correct remediation

Set the documented element on the policy, which switches it to the distributed algorithm:

```xml
<SpikeArrest async="false" continueOnError="false" enabled="true" name="spikearrest-1">
  <Identifier ref="request.header.some-header-name"/>
  <MessageWeight ref="request.header.weight"/>
  <Rate>3pm</Rate>
  <UseEffectiveCount>true</UseEffectiveCount>
</SpikeArrest>
```

This is a runtime behaviour change on a rate-limiting policy. It should be scheduled, not
applied mid-incident, and the customer's existing alerting on 429 responses will change
shape because rejections will become consistent rather than per-processor.

Documented caveat to state, not to omit: with the distributed algorithm the policy uses a
sliding window and does not smooth, so a burst that stays within the configured rate is
allowed through. If the customer also needs burst smoothing, the two policies have
different jobs and the documented ordering is SpikeArrest before Quota in the ProxyEndpoint
request PreFlow.

#### Verification

Confirm `ratelimit.spikearrest-1.exceed.count > 0` or
`ratelimit.spikearrest-1.available.count < 1` at the moment of rejection. Do not use
`ratelimit.spikearrest-1.failed`, which the reference says "should not be used to check if
a rate limit has been exceeded. It may be set to `true` under high load due to the policy's
'fail-open' design."

Then fire six requests inside a 20 second window and confirm that three succeed and three
are rejected, and repeat after the change has propagated across all six message
processors. Also confirm the rejected requests carry
`policies.ratelimit.SpikeArrestViolation`, not a policy-internal failure.

#### Common incorrect answers

"SpikeArrest cannot be distributed across message processors; use Quota instead." This is
the accepted, high-reputation answer on the source thread and it is wrong as of current
documentation. Reproducing it is the primary failure this scenario tests.

"Add a distributed Quota policy, which can only be per minute." True of Quota, and it
leaves the customer with a policy that cannot express a per-second limit at all.

"Configure ConcurrentRateLimit." It is deprecated and the customer already reports it does
not help.

"Reduce the rate to 3 divided by 6 to compensate." This hard-codes the processor count,
which changes when the org scales, and it silently under-admits traffic on a smaller
topology.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Reproduces the "not distributed" answer | Identifies per-processor smoothing | Identifies per-processor smoothing **and** `<UseEffectiveCount>` as the remedy |
| Handling of current vs legacy advice | Treats the accepted answer as correct | Hedges | States the accepted answer is contradicted by current docs |
| Diagnostic method | Reasons from message processor count | Reads the policy XML | Reads the policy XML and asks about `<UseEffectiveCount>` |
| Source discipline | Cites docs.apigee.com as Apigee X | Notices the domain | Flags that the URL serves Edge/OPDK docs and cites the X page |
| Quality of next step | Move to Quota | Set the element | Schedule the change, state the smoothing trade-off, verify with the ratelimit variables |

#### Critical failures: telling the customer SpikeArrest cannot be synchronised across
message processors; recommending a Quota policy without offering the documented
alternative; using `ratelimit.<policy>.failed` to decide whether a limit was exceeded.

#### References

- Reported case: <https://stackoverflow.com/questions/23298849>
- SpikeArrest policy, `<UseEffectiveCount>` and smoothing:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy>
- Comparing Quota and SpikeArrest (Apigee X):
  <https://cloud.google.com/apigee/docs/api-platform/develop/comparing-quota-and-spike-arrest-policies>
- Edge/OPDK page of the same name, which is what the legacy `docs.apigee.com` URL resolves
  to: <https://docs.apigee.com/api-platform/develop/comparing-quota-spike-arrest-and-concurrent-rate-limit-policies>
- Antipattern, non-distributed quota (for contrast):
  <https://cloud.google.com/apigee/docs/api-platform/antipatterns/non-distributed-quota>

---

### MED-33. Rate of 5 per minute, but the third call in ten seconds is rejected

#### Scenario metadata

- ID: MED-33
- Difficulty: medium
- Primary topic: rate limiting, SpikeArrest policy
- Secondary topics: Quota versus SpikeArrest, message weights
- Product: Apigee
- Origin: reported real-world case
  (<https://stackoverflow.com/questions/21912316>), closed, no accepted answer
- Versions: checked 2026-10-12
- Evaluation objectives: the symptom looks like a broken counter and is in fact a rate
  limiter. The agent must apply the documented smoothing arithmetic instead of assuming the
  policy counts requests in a window, and must not "fix" it by raising the rate without
  establishing which problem the customer actually has.
- Skills expected: apigee-support-core

#### Initial support ticket

> We have a SpikeArrest policy on our request PreFlow:
>
> ```xml
> <SpikeArrest enabled="true" continueOnError="true" async="false" name="SpikeArrest">
>   <Rate>5pm</Rate>
>   <MessageWeight ref="request.header.weight"/>
> </SpikeArrest>
> ```
>
> The documentation says that if we call more than five times in a minute the policy fails
> after the fifth call. We tested by sending ten calls in under ten seconds. The policy
> accepted the first two calls and rejected everything after that. We are not calling more
> than five times a minute. Our environment has two message processors and two routers. Is
> that the cause?

#### Initial evidence

Two successful calls then rejections, for a configured `5pm`. Rejections carry
`policies.ratelimit.SpikeArrestViolation`, HTTP 429, verified at `error-codes.md` line 43.
The policy has a `<MessageWeight>` bound to a request header, which is a second live
variable that has not been examined. `continueOnError` is `true`, which is unusual for a
throttling policy and is not discussed.

#### Expected investigation

The agent should apply the documented smoothing rule rather than the window rule.
Per-minute rates are documented as "smoothed into intervals of seconds", so `5pm` is
enforced as one request per 12 seconds, not as five requests per 60-second bucket. Ten
calls in ten seconds should produce one success under one processor. Two successes means
either two message processors each smoothed independently, or the message weight is not 1.

The agent should check both. The weight is the more commonly missed branch: the reference
gives the worked example that with a rate of `10pm` and a client weight of `2`, "only five
messages per minute are permitted from that client because each request counts as 2".

#### Diagnostic evidence

```xml
<SpikeArrest enabled="true" continueOnError="true" async="false" name="SpikeArrest">
  <Rate>5pm</Rate>
  <MessageWeight ref="request.header.weight"/>
</SpikeArrest>
```

A debug trace shows `request.header.weight` is **absent** on the client requests. With the
reference unset the weight falls back to 1, so weight is not the cause here, and the
trace shows two distinct message processors serving the two successful requests.

#### Ground-truth resolution

There is no fault. Two independent effects compound. SpikeArrest is documented as a rate
limiter rather than a counter: it "smoothes the rate to one request allowed every
200 *milliseconds* (1000/5)" for per-second rates, and per-minute rates are smoothed into
intervals of seconds, so `5pm` becomes one request per 12 seconds. And smoothing is
documented as "not coordinated across Message Processors". With two message processors the
observed allowance doubles to two requests per 12 seconds, which is exactly what the
customer saw.

The customer's mental model, a per-minute counter, is the thing that is wrong. Their
question, whether the two message processors are the cause, is the right question and the
answer is yes.

#### Correct remediation

Decide which of two things the customer actually wants, because they need different
configurations. If they want burst protection, keep the token-bucket smoothing and choose
a rate that reflects the interval their backend can absorb, understanding the effective
admission rate is the configured rate multiplied by the number of message processors. If
they want an accurate count of requests per period, that is the Quota policy's job; the
SpikeArrest reference itself points there.

If the customer wants both, the documented combination is SpikeArrest first in the
ProxyEndpoint request PreFlow for burst protection, then Quota for the longer-term count.
The comparison page states SpikeArrest "should always be attached before the Quota policy
in the ProxyEndpoint Request PreFlow... This prevents spikes from prematurely exhausting
quota."

Raise `<MessageWeight>` handling regardless: bind it to a header the clients actually send
or remove it. An unset `ref` currently resolves to 1, which means the policy silently
accepts a configuration the operator believes is active.

#### Verification

Send requests at the documented interval and confirm exactly one per processor per
interval succeeds. Then confirm the rejection path: check
`ratelimit.SpikeArrest.failed` separately from
`ratelimit.SpikeArrest.exceed.count > 0`, since the reference warns that `failed` "should
not be used to check if a rate limit has been exceeded".

Re-test after any change to the rate so the multiplication by message processor count is
re-derived from the trace rather than assumed, because the trace is what established it.

#### Common incorrect answers

"Your SpikeArrest policy is counting wrong; five requests should have been allowed." It is
not counting, it is smoothing, and the documentation states that explicitly.

"Increase the rate to 10pm to compensate." This doubles the real allowance and, with two
processors, admits four per 12 seconds, which is not what anyone asked for.

"Switch to a Quota policy." Legitimate only if the customer wants counts. Offered as a
general fix it replaces burst protection with a window count and lets the burst through.

"Remove the two routers, they are causing double counting." Routers do not hold policy
counters.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Assumes a per-minute counter | Applies smoothing, misses processor multiplication | Applies smoothing **and** the per-processor multiplication, and checks message weight |
| Diagnostic method | Restates the rate | Suggests raising it | Uses a debug trace to separate weight from topology |
| Safety | Changes the rate immediately | Proposes a change | Establishes whether the customer wants burst protection or counts before changing |
| Handling of competing causes | Ignores MessageWeight | Mentions it | Confirms the unset `ref` resolves to 1 and recommends fixing the binding |
| Verification | None | Retests once | Checks the documented ratelimit variables and keeps `failed` separate from `exceed.count` |

#### Critical failures: treating SpikeArrest as a request counter; raising the rate as the
first move; ignoring `<MessageWeight ref=...>`.

#### References

- Reported case: <https://stackoverflow.com/questions/21912316>
- SpikeArrest policy, `<Rate>`, `<MessageWeight>`, smoothing:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy>
- Comparing Quota and SpikeArrest:
  <https://cloud.google.com/apigee/docs/api-platform/develop/comparing-quota-and-spike-arrest-policies>
- Error index entry for `policies.ratelimit.SpikeArrestViolation`:
  `.agents/skills/apigee-support-core/references/error-codes.md`

---

### MED-34. A key value map read returns nothing, and the policy reports no error

#### Scenario metadata

- ID: MED-34
- Difficulty: medium
- Primary topic: KeyValueMapOperations policy
- Secondary topics: management API scoping, flow variables, silent failure
- Product: Apigee
- Origin: reported real-world cases
  (<https://stackoverflow.com/questions/21897932> and
  <https://stackoverflow.com/questions/27850597>), both closed with accepted answers
- Versions: checked 2026-10-12
- Evaluation objectives: two distinct causes produce one identical silent symptom, and the
  customer's own workaround masks the problem by making the policy write instead of read.
  The agent must enumerate the read path rather than trust the first configuration that
  makes the symptom disappear.
- Skills expected: apigee-support-core

#### Initial support ticket

> We store a lookup table in a key value map and read it in the request flow. The variable we
> assign is always empty and the policy produces no error at all. The trace shows the step
> completing.
>
> We created the map through the management API using the API-scoped URL
> `/v1/o/{org}/apis/{api}/keyvaluemaps`, named `countrymap`. Our policy is:
>
> ```xml
> <KeyValueMapOperations async="false" continueOnError="false" enabled="true"
>   mapIdentifier="countrymap" name="keyvaluemapoperations-2">
>   <Get assignTo="my.country" index="1">
>     <Key><Parameter ref="apigee.countryCode"></Parameter></Key>
>   </Get>
>   <Scope>organization</Scope>
> </KeyValueMapOperations>
> ```
>
> One thing we noticed: if we add an `<InitialEntries>` block the same policy works. We are
> assuming that proves the map exists. Does it?

#### Initial evidence

The variable is empty on every request. No fault is raised; the policy step completes
normally. The map was created at API scope; the policy declares `<Scope>organization</Scope>`.
The `<Key><Parameter>` element carries a `ref` attribute. `index="1"` is a 1-based index
into a multi-valued key.

#### Expected investigation

Three separate things can produce a silent empty read, and the ticket contains two of them
at once. The agent should check, in order: whether the map exists in the scope the policy
declares; whether `<Parameter>` is naming a key or naming a flow variable; and whether the
key being read exists at all.

The `<InitialEntries>` observation is the trap that has to be addressed directly. Adding
`<InitialEntries>` makes the policy **create or overwrite** the map in the declared scope.
That is why the symptom disappears. It does not prove the original map was readable.

#### Diagnostic evidence

Listing the KVM at the API scope returns the map with entries. Listing it at organization
scope returns 404. The trace shows `apigee.countryCode` resolving to a value, for example
`IN`, while the map contains keys named `IN` only in the API-scoped map, and the
organization-scoped policy is reading from a namespace where nothing was ever written.

Separately, in the second variant of this report the map and the scope are both correct,
and the defect is:

```xml
<Key><Parameter ref="k1"></Parameter></Key>   <!-- resolves flow variable k1, then looks up its VALUE as a key name -->
<Key><Parameter>k1</Parameter></Key>           <!-- uses the literal string "k1" as the key name -->
```

The reference states that `ref` means "the name of a variable whose value contains the
exact name of the key you want to create, get, or delete", and that the attribute is
"Required if no literal value is given between the opening and closing tags."

#### Ground-truth resolution

Two defects, reported as one. The map exists at API scope and the policy reads at
organization scope, so the read addresses an empty namespace. Separately, the `<Parameter>`
element uses `ref`, which makes the element a variable lookup rather than a literal key
name, so even with the scope corrected the key name being searched for is the *value* of
`apigee.countryCode`, not the string `Development` or `IN`.

The `<InitialEntries>` workaround makes the symptom disappear for the wrong reason. It
writes into the organization-scoped namespace, which is then readable, and it masks the
scope defect permanently by seeding a second, divergent copy of the data.

#### Correct remediation

Make the declared scope match where the map actually lives, then make the key name
literal unless it is genuinely dynamic:

```xml
<KeyValueMapOperations async="false" continueOnError="false" enabled="true"
  mapIdentifier="countrymap" name="keyvaluemapoperations-2">
  <Get assignTo="my.country" index="1">
    <Key><Parameter>IN</Parameter></Key>
  </Get>
  <Scope>apiproxy</Scope>
</KeyValueMapOperations>
```

Before moving data, check whether an `<InitialEntries>` block has already been deployed.
If it has, the environment now holds a second copy of the entries written by the policy,
and removing the block without reconciling will make the reads start failing. Confirm
which copy is authoritative with the customer before deleting anything.

Also check the reserved word: the reference notes that the KVM key name `ratelimit` is
reserved, in two separate places on that page.

#### Verification

Read the value back in a debug trace and confirm `my.country` is populated and that the
step still completes without a fault. Confirm the map's entry list in the scope the policy
declares, and confirm no second copy exists in the other scope.

Re-test after the change propagates across environments, because KVM data is per environment
and a fix in `test` says nothing about `prod`.

#### Common incorrect answers

"Add `<InitialEntries>` so the policy creates the map." This is the customer's own
workaround. It creates a second, divergent copy of the data and leaves the original
unreadable.

"Raise `continueOnError` or check the cache expiry." Neither is relevant; there is no error
and no expiry in play.

"Change `index` from 1 to 0." `index` is 1-based. Zero is a deployment error, `InvalidIndex`,
documented as "If the `index` attribute specified in the `<Get>` element ... is zero or a
negative number, then the deployment of the API proxy fails."

"Use `<Parameter ref="entry.Development">`." That names a flow variable called
`entry.Development`, not a key called `Development`. This is the mistake the second report
made three times in a row.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Suggests InitialEntries | Identifies the scope mismatch | Identifies scope mismatch **and** `ref` versus literal key name |
| Diagnostic method | Trusts the InitialEntries workaround | Lists the KVM in one scope | Lists the KVM in both scopes and checks whether a second copy was seeded |
| Handling of competing causes | One cause | Two causes | Enumerates scope, key-name form, index base, and key existence |
| Safety | Recommends adding entries | Proposes the scope change | Flags the possible duplicate data before removing anything |
| Verification | Retests once | Retests after change | Retests per environment and confirms no second copy exists |

#### Critical failures: recommending `<InitialEntries>` as the fix; treating
`<Parameter ref="...">` as a key name; deleting or overwriting a map without checking
whether an `<InitialEntries>` block has already written to it.

#### References

- Reported case, scope mismatch:
  <https://stackoverflow.com/questions/21897932>
- Reported case, `ref` versus literal:
  <https://stackoverflow.com/questions/27850597>
- KeyValueMapOperations policy, `<Parameter>`, `<Scope>`, `<Get index>`:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/key-value-map-operations-policy>
- KVM deployment errors including `InvalidIndex`:
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/deployment/key-value-map-deployment-errors>

---

### MED-35. 502 Bad Gateway at exactly two minutes, with the backend reporting success four minutes later

#### Scenario metadata

- ID: MED-35
- Difficulty: medium
- Primary topic: target connection behaviour and timeouts
- Secondary topics: keep-alive connection reuse, endpoint properties, undocumented territory
- Product: Apigee (and Apigee hybrid)
- Origin: reported real-world case
  (<https://stackoverflow.com/questions/68314564>), closed with **zero answers**; fault
  payload and causes checked against the official playbook, retrieved live during this
  session
- Versions: checked 2026-10-12
- Evaluation objectives: the symptom looks like a backend timeout and is not one. The
  agent must use the documented status-code mapping to rule out the timeout family before
  reasoning about anything else, must work the documented causes even when they do not fit,
  and must not invent a 120-second Apigee timeout when no documentation states one.
- Skills expected: apigee-support-core

#### Initial support ticket

> We have an Apigee proxy in front of a Node.js 12 / Express backend. If a request takes
> longer than two minutes the client gets a 502 Bad Gateway, always at the two minute mark.
> The backend logs a 200 about four minutes later, so it is completing the work after the
> client has already given up. The backend logs nothing at the moment the client errors.
>
> The fault body is:
>
> ```json
> {"fault":{"faultstring":"Unexpected EOF at target",
>   "detail":{"errorcode":"messaging.adaptors.http.flow.UnexpectedEOFAtTarget"}}}
> ```
>
> We have already raised the Node request timeout to ten minutes and added keep-alive on
> the backend. Neither changed anything. Please tell us why Apigee is throwing the error
> when the backend is not.

#### Initial evidence

HTTP 502, fault code `messaging.adaptors.http.flow.UnexpectedEOFAtTarget`, fault string
"Unexpected EOF at target". The failure is at a fixed 120 seconds from request start. The
backend receives the request, does not respond for four minutes, and has no log entry at
the two minute mark. The customer has already changed backend-side keep-alive and Node
timeouts.

The fault code is verified in `research/pages/mon_fault-codes.txt` line 81. It is
deliberately **not** in `.agents/skills/apigee-support-core/references/error-codes.md`,
because that index covers policy fault codes and this one is raised by the HTTP target
adaptor, not by a policy. An agent that cannot say that distinction has not read the
evidence properly.

#### Expected investigation

Rule out the timeout family first, using documented status codes rather than intuition. The
endpoint properties reference states that a target connect timeout returns `503` and that
`io.timeout.millis` expiry returns `504 Gateway Timeout`, with `408 Request Timeout` if the
timeout is reading from ingress. The current defaults are `connect.timeout.millis` 3000 ms
and `io.timeout.millis` 55000 ms, capped at 300 seconds. A 502 is none of these. Neither
default produces a 120 second wall. That is the key finding and it is available before any
packet capture is taken.

Then work the documented causes for this exact fault code, and be willing to find they do
not fit. The official playbook gives two.

#### Diagnostic evidence

```terminal
kubectl get svc istio-ingressgateway -n istio-system
kubectl get deploy -n apigee
```

From the TargetEndpoint definition:

```xml
<HTTPTargetConnection>
  <URL>https://backend.example.com</URL>
  <Properties>
    <Property name="keepalive.timeout.millis">30000</Property>
  </Properties>
</HTTPTargetConnection>
```

Against a backend configured with a 25 second keep-alive, and the reference documents a
default of 60000 ms for that property.

#### Ground-truth resolution

Three separate conclusions, and the honest answer contains all three.

One, the fault is on the Apigee side, and the customer's own reasoning on this point is
right. The code and the playbook both attribute it to the target hop: the playbook's sample
ingress log carries `x_apigee_fault_code: messaging.adaptors.http.flow.UnexpectedEOFAtTarget`
with `x_apigee_fault_source: target`. Apigee cannot raise a target-side EOF unless it is
the party that received one.

Two, it is not a timeout. Timeouts are 503 and 504, and the documented defaults are 3
seconds connect and 55 seconds I/O. Nothing documented produces a 120 second wall at the
target hop. An agent that says "Apigee has a two minute timeout" is asserting something
this research did not find in any current document.

Three, the documented causes for this fault code do not explain a fresh long-lived
request. Cause one is a keep-alive mismatch, and it requires Apigee to **reuse a pooled
connection** whose idle threshold expired on the backend mid-request. The playbook's
evidence for it is `useCount=7` with `bytesRead=0` and `bytesWritten=1303` in a
`java.io.EOFException: eof unexpected`. A request that has been open for two minutes on a
fresh connection does not have that signature. Cause two is AWS NLB with cross-zone load
balancing and client IP preservation behind NAT, which breaks connections in pairs and
"must intermittently occur" rather than firing at a fixed elapsed time.

So the documented causes should be tested and can reasonably be ruled out, and what remains
is not documented. The right output is a scoped evidence request, not a confident
explanation.

#### Correct remediation

Work cause one first, because it is the documented one and because the customer moved
keep-alive in the wrong direction. The documented requirement is that Apigee's keep-alive
value must be **lower** than the backend's, not higher:

```xml
<Property name="keepalive.timeout.millis">25000</Property>
```

with a 25 second backend value, or simply remove the override and accept the 60000 ms
default if the backend's value is higher.

Check cause two by confirming all three conditions: NAT IPs provisioned, target is AWS NLB,
cross-zone load balancing enabled, client IP preservation enabled. If all hold, the
documented resolution is to disable cross-zone load balancing or client IP preservation,
and the documented position is that "Cloud NAT behaves correctly here, and this is an issue
with NLB architecture. No changes can be made at Apigee."

If neither cause applies, raise a support case rather than guessing. The playbook lists
exactly what to attach: project ID, organization, proxy and revision, a downloaded debug
session file for a failing call, backend logs for the failure window, and a tcpdump from
the message processor or the backend. Take the capture on the first hop after Apigee:

```terminal
tcpdump -i any -s 0 host <BACKEND_HOSTNAME> -w <FILENAME>
```

Note for the ticket: `api.timeout` is a per-proxy property that must be "shorter than the
standard Message Processor timeout of 300 seconds" and "cannot be set with a variable",
and if it is unset the effective timeout comes from the Ingress. That is the only
documented place an upstream timeout can enter this path, and it is worth establishing what
the Ingress is set to before the case is raised.

#### Verification

After any change, confirm the symptom by forcing it: send a request the backend will hold
for longer than the configured timeout and confirm the status code changes to the documented
one for the new timeout, which is `504` for a read timeout. A 502 that becomes a 504 is
progress; a 502 that becomes a 200 means the keep-alive change worked.

Confirm the fault code in the ingress log is no longer `messaging.adaptors.http.flow.UnexpectedEOFAtTarget`
and that `x_apigee_fault_source` no longer reads `target`.

#### Common incorrect answers

"It is a two minute timeout on the Apigee side." Undocumented as far as this research
established. Do not say it.

"Increase `io.timeout.millis` to 120000." This is the example in the official playbook, and
it is the wrong move for a 502. A read timeout raises 504 with
`messaging.adaptors.http.flow.GatewayTimeout` and reason `TARGET_READ_TIMEOUT`, which is a
different fault entirely. Raising the timeout converts one failure mode into another.

"Raise the backend's keep-alive timeout, as Apigee's docs suggested." The documented
direction is the opposite. Apigee's value must be lower than the backend's, otherwise
Apigee reuses a connection the backend is about to close.

"It must be the backend crashing." The backend logs a 200 four minutes later, which is
positive evidence against that.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Asserts a 120 s Apigee timeout | Rules out timeouts by status code | Rules out timeouts by status code and by the documented 3 s / 55 s defaults |
| Diagnostic method | Changes a timeout value | Works the playbook causes | Tests the documented causes and says explicitly that they do not fit the signature |
| Source discipline | Treats `mon_fault-codes` as a policy index | Notes the index gap | States the code is a target-adaptor code outside the policy error index |
| Honesty about limits | Confidently names a cause | Hedges | Names what is documented, names what is not, and requests scoped evidence |
| Quality of next step | Raises `io.timeout.millis` | Fixes keep-alive direction | Fixes keep-alive direction, checks the NLB conditions, prepares the exact case attachments |

#### Critical failures: asserting an undocumented 120-second Apigee timeout; raising
`io.timeout.millis` as the remedy for a 502; telling the customer to raise the backend
keep-alive above Apigee's.

#### References

- Reported case, no answers: <https://stackoverflow.com/questions/68314564>
- Playbook, 502 Unexpected EOF at target (fetched live this session, saved to
  `research/pages/api-platform_troubleshoot_playbooks_runtime_unexpected-eof-at-target.txt`,
  last updated 2026-10-09):
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/runtime/unexpected-eof-at-target>
- Playbook, 504 target read timeout:
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/runtime/504-target-read-timeout>
- Endpoint properties, including `connect.timeout.millis`, `io.timeout.millis`,
  `keepalive.timeout.millis` and `api.timeout`:
  <https://cloud.google.com/apigee/docs/api-platform/reference/endpoint-properties-reference>
- Monitoring fault codes, which is where this code is actually indexed:
  `research/pages/mon_fault-codes.txt`
- Note: `.../playbooks/network/504-target-read-timeout` returns HTTP 200 with a generic
  title and no body. It is a soft 404. Use the `runtime/` path.

---

### MED-36. A JavaScript policy times out intermittently, and raising the limit is the wrong fix

#### Scenario metadata

- ID: MED-36
- Difficulty: medium
- Primary topic: JavaScript policy execution limits
- Secondary topics: proxy-to-proxy calls, antipatterns, free trial limits
- Product: Apigee
- Origin: reported real-world case
  (<https://stackoverflow.com/questions/22995892>), closed with the single answer accepted
- Versions: checked 2026-10-12
- Evaluation objectives: the accepted answer is the intuitive one and it converts an
  intermittent input/output symptom into a permanently higher ceiling. The agent must read
  what the script actually does, recognise the proxy-within-proxy antipattern, and notice
  the documented free-trial constraint that makes the accepted answer a no-op on some
  organisations.
- Skills expected: apigee-support-core

#### Initial support ticket

> We have two proxies. Proxy B has a JavaScript policy that calls proxy A over HTTP and
> processes the response. Intermittently we get:
>
> ```json
> {"fault":{"detail":{"errorcode":"steps.javascript.ScriptExecutionFailed"},
>   "faultstring":"Execution of getlocationserviceresponse failed with error: Javascript runtime exceeded limit of 200ms"}}
> ```
>
> We have already split our JavaScript into small modules so each policy is tiny. It still
> happens "from time to time". What can we do to avoid it?

#### Initial evidence

`steps.javascript.ScriptExecutionFailed`, HTTP 500, verified at `error-codes.md` line 61.
The failure is intermittent, not consistent, and the arithmetic does not fit a CPU-bound
script: splitting the code did not help, which is itself evidence that the limit is not
being consumed by computation. The script performs `httpClient` calls. The organisation is
on a free trial or evaluation tier, which the ticket does not yet mention.

#### Expected investigation

The intermittency is the clue and the accepted answer ignores it. A CPU-bound script either
exceeds 200 ms consistently or not at all. A script that occasionally waits on a network
call exceeds a wall-clock limit only when the network is slow. The documented `timeLimit`
is wall-clock execution time, not CPU time, and an outbound HTTP call from inside a
JavaScript policy is a blocking wait charged against that same budget.

The agent should read the script body before touching the policy attributes.

#### Diagnostic evidence

```javascript
// in the JavaScript policy resource
var response = httpClient.send('https://myproject-eval.apigee.net/proxyA/resource');
response.waitForComplete();
context.log("done");   // sometimes never reached
```

And the organisation record showing the free trial / evaluation tier. The current
JavaScript policy reference states for the `timeLimit` attribute: "Specifies the maximum
time (in milliseconds) a script can execute... **Note: For free trial accounts, execution
time is limited to 200 ms.**" The attribute is marked **Required**.

#### Ground-truth resolution

The policy is not doing too much work, it is waiting too long, and no amount of splitting
changes that. The 200 ms budget is being consumed by a blocking `httpClient.send` plus
`waitForComplete`, so the policy fails exactly when the downstream call is slow. That also
explains the intermittency and explains why the customer's own mitigation did nothing.

Worse for the accepted answer: on a free trial or evaluation organisation, the documented
note says execution time is limited to 200 ms regardless, so raising `timeLimit` may change
nothing at all. The accepted answer does not consider the organisation tier and cannot
explain why the same policy would fail differently on a paid organisation.

The underlying construction is also a documented antipattern. Invoking one API proxy from
another with custom JavaScript or an `HTTPTargetConnection` "results in additional network
hop", because the request "has to be routed through the traditional route (Router > MP) at
runtime... a request has already reached the MP". The documented fix is proxy chaining.

#### Correct remediation

Remove the proxy-to-proxy call rather than pay for it in timeLimit. Proxy chaining runs
the called proxy in the same message processor over a local connection:

```xml
<LocalTargetConnection>
  <APIProxy>proxyA</APIProxy>
  <ProxyEndpoint>default</ProxyEndpoint>
</LocalTargetConnection>
```

If the second proxy genuinely must be reached over the network, keep the call out of
JavaScript. Use a ServiceCallout, which is a policy with its own timeout surface, or move
the request shaping into the target endpoint.

Only after removing the blocking call is raising `timeLimit` even the right conversation,
and at that point establish the organisation tier first, because the documented free-trial
limit makes the attribute ineffective on trial and evaluation organisations.

#### Verification

Confirm the failure rate drops to zero across a sustained load test that includes slow
downstream responses, not just fast ones. The intermittency means a passing smoke test
proves nothing here.

Then confirm the script actually completes: the `context.log` after `waitForComplete`
should appear on every request, which it did not before.

Confirm the organisation tier before relying on any `timeLimit` value, and if it is a trial
or evaluation organisation say so rather than raising the attribute and reporting no change.

#### Common incorrect answers

"Raise `timeLimit` to 1000." This is the accepted answer on the source thread. It raises
the ceiling while leaving the blocking call in place, converts an intermittent failure into
a less frequent one, and is documented as ineffective on free trial and evaluation
organisations.

"Split the JavaScript into smaller modules." The customer already did this and reported it
did not help. The agent should treat that as evidence, not as a suggestion to repeat.

"Increase the message processor size or memory." The limit is a per-policy wall-clock
budget, not a resource limit.

"Retry the JavaScript policy." There is no built-in retry for a policy execution timeout,
and a retry would double the downstream load that caused the timeout.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Raises timeLimit | Identifies the call as the cost | Identifies the blocking call as the cost and names proxy chaining as the fix |
| Diagnostic method | Treats it as a code-size problem | Notes intermittency | Uses intermittency as evidence against a CPU-bound cause |
| Product knowledge | Ignores tier | Mentions trial limit | States the documented free-trial 200 ms limit and checks the tier before recommending |
| Handling of the accepted answer | Reproduces it | Hedges | States the accepted answer is incomplete and tier-dependent |
| Quality of next step | Raises the attribute | Moves the call to a policy | Removes the network hop via proxy chaining, then verifies under slow-downstream load |

#### Critical failures: recommending a higher `timeLimit` as the fix; repeating the
"split the script" advice the customer already ruled out; ignoring the documented free
trial 200 ms execution limit.

#### References

- Reported case: <https://stackoverflow.com/questions/22995892>
- JavaScript policy, `timeLimit` attribute and the free-trial note:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/javascript-policy>
- Antipattern, invoking a proxy within a proxy:
  <https://cloud.google.com/apigee/docs/api-platform/antipatterns/proxy-within-proxy>
- Error index entry for `steps.javascript.ScriptExecutionFailed`:
  `.agents/skills/apigee-support-core/references/error-codes.md`

---

### MED-37. One quota policy referenced from three flows exhausts faster than expected

#### Scenario metadata

- ID: MED-37
- Difficulty: medium
- Primary topic: Quota policy counters
- Secondary topics: API products, antipatterns, identifier scoping
- Product: Apigee
- Origin: reported real-world case
  (<https://stackoverflow.com/questions/21615609>), closed; the accepted answer is
  reproduced almost verbatim by current documentation
- Versions: checked 2026-10-12
- Evaluation objectives: the obvious model, one counter per flow, is wrong and is the model
  most engineers hold. The agent must establish what actually identifies a counter, must
  notice that the same policy reference also documents a per-operation model once API
  products are involved, and must flag the reuse as a documented antipattern rather than
  just explaining it.
- Skills expected: apigee-support-core

#### Initial support ticket

> We have one proxy with three flows, A, B and C. All three reference a single Quota policy
> named `QuotaLimitPolicy`, configured as 5 requests per interval, with an `<Identifier>`
> bound to `client_id`. We expected each flow to have its own budget of 5.
>
> What we see is that the budget is shared. A client calling only flow A exhausts the
> allowance that we budgeted for all three, and starts receiving quota rejections even
> though it has touched only one of the three resources.
>
> Failing calls carry `policies.ratelimit.QuotaViolation`. Is this a bug, and what actually
> defines a separate counter?

#### Initial evidence

HTTP 500 with `{"fault":{"detail":{"errorcode":"policies.ratelimit.QuotaViolation"}}}`,
verified at `error-codes.md` line 42, sourced to the quota policy page. One policy
element named `QuotaLimitPolicy` attached as a `<Step>` in three flows. No API product
quota settings in play. The rejections cluster on one client id.

#### Expected investigation

The agent should answer the general question, because the reporter only asked the specific
one. What makes a counter distinct is not the flow. Reference to the same policy from
several places is one counter, keyed by the policy `name` attribute, and by the identifier
value. The agent should then say that this is documented, and that reusing one policy in
several places is listed as an antipattern.

The second half is the part a single-look diagnosis misses. Once an API product is
associated, the model changes: Apigee keeps a separate counter per operation defined in the
product, and the product-level `quotaCounterScope` attribute decides whether operations
collapse onto a product-level or proxy-level counter. So "what makes a counter distinct"
has two different answers depending on whether API products are in play, and the agent has
to ask which one applies here.

#### Diagnostic evidence

```xml
<Quota name="QuotaLimitPolicy">
  <Interval>1</Interval>
  <TimeUnit>hour</TimeUnit>
  <Allow count="5"/>
  <Identifier>client_id</Identifier>
</Quota>
```

attached as:

```xml
<Step><Name>QuotaLimitPolicy</Name></Step>
```

in flow A, flow B and flow C. A debug trace on flows A, B and C shows the same
`quota.<policy>.used.count` climbing 1, 2, 3, 4, 5 across all three, then rejection. The
proxy has no API product associated, so the trace confirms the no-product path.

#### Ground-truth resolution

The behaviour is correct and the mental model is wrong. The current Quota policy reference
reproduces the reporter's own worked example, with the same flow letters:

> For example, you create a Quota policy named `MyQuotaPolicy` with a limit of 5 requests
> and place it on multiple flows (Flow A, B, and C) in the API proxy. Even though it is
> used in multiple flows, it maintains a single counter that is updated by all instances of
> the policy: Flow A is executed -> counter = 1; Flow B -> 2; Flow A -> 3; Flow C -> 4;
> Flow A -> 5. The next request to any of the three flows is rejected.

and the same page states the rule directly: "If there is no API product associated with an
API proxy, a quota policy maintains a single counter, regardless of how many times you
reference it in an API proxy. **The name of the quota counter is based on the `name`
attribute of the policy.**"

So the counter identity is the policy `name` plus the identifier value, in a proxy with no
API product. Flow does not appear in it. Separation is achieved by using different policy
elements with different `name` attributes.

The page then adds the part that changes the answer depending on configuration: "By
default, Apigee maintains a separate quota counter for each operation defined in an API
product", with operation-level quota settings taking precedence over product-level ones,
and `quotaCounterScope` of `PRODUCT` or `PROXY` deciding which operations collapse onto a
shared counter.

Finally, the reference names the reuse as an antipattern: "Using the same Quota policy in
more than one place in an API proxy flow, which can unintentionally cause Quota to run out
faster than you expected, is an anti-pattern."

#### Correct remediation

Pick one of two intents, because they are different configurations.

To give each flow its own budget, use a separate Quota policy element per flow with
distinct `name` attributes. That is what the documentation prescribes and it is the
minimal change. Note that it multiplies policy instances, which is the cost the antipattern
page is warning about elsewhere in the product.

To keep one shared budget but control how the counter is scoped, use API products and
`quotaCounterScope`. This is the right tool when several proxies should contribute to one
budget, and it is worth naming explicitly because a common but incorrect claim in community
threads is that a single counter can be shared across API proxies by a Quota policy alone.
The reference is explicit that quotas "apply to individual API proxies and are not
distributed among API proxies... a single quota is not shared across all three even if all
three use the same quota policy configuration." Sharing across proxies is done through API
product configuration, not by pointing two policies at one counter.

#### Verification

Confirm the counter now increments per flow, or per product scope, as intended, by reading
the quota variables across the flows in a debug trace rather than by inferring from
rejection counts.

Then confirm the intended per-resource budget empirically: a client that spends its whole
allowance on one resource should still have budget on the others.

Check whether other proxies share the same policy name and identifier and are silently
drawing on the same allowance, since that is the failure mode the customer is reporting.

#### Common incorrect answers

"Each flow has its own counter because they are different flows." The documented rule is
the opposite, and it is the specific misconception the reporter brought to the question.

"Set a different `<Identifier>` per flow." The identifier keys the counter by client, not by
flow. Changing it would segment clients, not resources, and would make the problem worse.

"Share one counter across three proxies by using the same policy name and identifier." The
reference says quotas are not distributed among API proxies. This is the most common wrong
answer in the community on this exact question.

"Increase the allow count to 15 so all three flows fit." That concedes the shared-counter
behaviour silently and removes the per-resource protection the customer was trying to get.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says one counter per flow | Says one counter per policy name | Says one counter per policy name plus identifier, and states it is documented |
| Diagnostic method | Reads the fault code only | Inspects the policy | Confirms counter sharing in a trace with the quota variables |
| Completeness | Answers only the specific question | Adds the antipattern note | Adds the API-product per-operation model and `quotaCounterScope` |
| Handling of competing advice | Repeats "share across proxies" | Hedged | States plainly that quotas are not distributed among API proxies |
| Quality of next step | Raise the allow count | Separate policy names | Separates policy names or moves to product-scoped counters, depending on stated intent |

#### Critical failures: asserting one counter per flow; asserting a Quota policy alone can
share a counter across proxies; raising the allow count to compensate without raising the
per-resource protection problem.

#### References

- Reported case: <https://stackoverflow.com/questions/21615609>
- Quota policy, "Understand quota counters", "How quotas are counted", and
  `quotaCounterScope`:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
- Antipattern, reusing a Quota policy:
  <https://cloud.google.com/apigee/docs/api-platform/antipatterns/reusing-quota>
- Antipattern, non-distributed quota:
  <https://cloud.google.com/apigee/docs/api-platform/antipatterns/non-distributed-quota>
- Error index entry for `policies.ratelimit.QuotaViolation`:
  `.agents/skills/apigee-support-core/references/error-codes.md`

---

### MED-38. OAuth rejects a valid-looking token because no API product matched

#### Scenario metadata

- ID: MED-38
- Difficulty: medium
- Primary topic: API products and application credentials
- Secondary topics: fault-code interpretation, tracing, misleading community answers
- Product: Apigee
- Origin: reported real-world case
  (<https://stackoverflow.com/questions/24035609>), closed; four answers give four
  different fixes and the top two contradict each other
- Versions: checked 2026-10-12
- Evaluation objectives: four plausible community fixes, two of them mutually exclusive.
  The agent must enumerate the association chain rather than adopt the highest-scoring
  answer, and must read the fault code as a pointer rather than a diagnosis, because the
  documented entry for it contains no cause text at all.
- Skills expected: apigee-support-core

#### Initial support ticket

> We are integrating a new client against our Apigee proxy and every call fails with:
>
> ```json
> {"fault":{"faultstring":"Invalid API call as no apiproduct match found",
>   "detail":{"errorcode":"steps.oauth.v2.InvalidAPICallAsNoApiProductMatchFound"}}}
> ```
>
> HTTP 401. The access token is issued by us, it is not expired, and the client is sending
> it correctly. We have read that the fix is to associate the API bundle with an API
> product, but our proxy is already in a product and the developer app is already
> associated with a product. Can you confirm which one is wrong?

#### Initial evidence

HTTP 401, `steps.oauth.v2.InvalidAPICallAsNoApiProductMatchFound`, verified at
`error-codes.md` line 132, sourced to the delete-oauth-v2-info policy page. The token
validates against the token endpoint. The proxy appears in at least one API product and
the developer app appears in at least one API product.

Note a discrepancy worth surfacing to the agent: the customer quotes a
`keymanagement.service.`-prefixed variant, which is the Apigee Edge-era string. The current
index carries the `steps.oauth.v2.`-prefixed form.

#### Expected investigation

The agent should walk the association chain rather than accept a single fix. The reported
community thread is the instruction here: the accepted answer says the **API bundle** must
be associated with a product, an equally-scored answer says the **developer app** must
list the product, a third says product approval was set to manual, and a fourth says the
resource path is missing from the product. All four can produce this symptom and only the
first is usually quoted.

The agent should also notice what the documented entry actually says, which is almost
nothing. The index row reads "Please see Oauth2.0 Access Token Verification throws 'Invalid
API call as no apiproduct match found' error for information about..." It is a pointer, not
a cause. An agent that treats the row as a diagnosis will confidently assert the wrong link
in the chain.

#### Diagnostic evidence

```
GET /v1/o/{org}/apiproducts            -> product list
GET /v1/o/{org}/developers/{dev}/apps/{app}   -> app.productBundle
GET /v1/o/{org}/apiproducts/{prod}/resources -> proxy + path list
GET /v1/o/{org}/apiproducts/{prod}/operations -> resource paths and operations
```

The trace shows the OAuth policy succeeds and the failure occurs on the resource match,
not on token validation. The app is associated with product **A**, the proxy is exposed
through product **B**, and the product the app holds does not include the request path.

#### Ground-truth resolution

Token validation and resource authorisation are separate steps and the ticket conflates
them. The token is valid. What failed is that no API product associated with the calling
application covers the requested resource path. That can come from four distinct
misconfigurations, and the customer is currently reporting symptoms of at least two of them
at once, which is why each single fix they tried appeared not to work:

- the requested proxy or resource path is not exposed by any product, so nothing matches
  regardless of the app;
- the app is not associated with the product that does expose it;
- the path within the product does not include the path being requested;
- the product's approval setting does not match how the key was created.

The single most important property of this case is that the community consensus is not
reliable. The accepted answer and the equal-scored runner-up name different links in the
same chain. An agent that cites the accepted answer as settled is repeating an
unverified claim as a fact.

#### Correct remediation

Make the chain complete, in this order: the request path exists in an API product's
resource paths; the developer app is associated with that product; the product's approval
setting matches how the key was issued. Verify each with the Management API calls above
rather than from the console, so the check names the object that is actually wrong.

This is a control-plane change to API product configuration and can affect every other
consumer of the same product, so it should be confirmed against the product's owner rather
than edited reflexively. Adding a resource path to a production product to fix one client
is a change with blast radius.

#### Verification

Re-run the failing call and confirm it succeeds with a fresh token. Then confirm nothing
else regressed: check that the other apps associated with the same product still resolve,
because widening a product's paths can change behaviour for clients that were previously
correctly rejected.

Read the fault code from the response rather than assuming the fix held, since a stale
token will produce a different code.

#### Common incorrect answers

"Associate the API bundle with an API product." The accepted answer. It is one of four
possible fixes and the customer states it is already done.

"Check the developer app's product list." The equally-scored runner-up. It is a different
fix and was probably the actual one here. Quoting the accepted answer without checking
this link is the primary failure.

"The key needs manual approval." Plausible and unverifiable from the fault code; it is the
third answer on the source thread and is a real Apigee mechanism, but nothing in the
payload distinguishes it from the others.

"Look up the code in the fault code reference and follow it." The reference entry for this
code is a bare pointer with no cause text, so this is the correct first move **and** it
will not by itself identify the broken link. An agent that stops there has not finished.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Applies the accepted answer only | Enumerates two candidate links | Enumerates all four links and names which is most likely |
| Handling of community answers | Cites the accepted answer as fact | Notes the answers differ | States the accepted and runner-up answers are mutually exclusive and unverified |
| Source discipline | Reads the index row as a diagnosis | Notes the row has no cause text | Uses the row as a pointer and checks the four chain links independently |
| Diagnostic method | Re-requests the token | Traces the request | Separates token validation from resource authorisation in the trace |
| Safety | Edits the product | Proposes the minimal link fix | Confirms with the product owner, then verifies other apps on the same product |

#### Critical failures: asserting the accepted answer's fix as the confirmed cause;
presenting the fault code reference entry as if it contained a cause; editing a production
API product's resource paths without checking the blast radius.

#### References

- Reported case, with its conflicting answers:
  <https://stackoverflow.com/questions/24035609>
- Error index entry for `steps.oauth.v2.InvalidAPICallAsNoApiProductMatchFound`, HTTP 401:
  `.agents/skills/apigee-support-core/references/error-codes.md`
- Create and manage API products:
  <https://cloud.google.com/apigee/docs/api-platform/publish/create-api-products>
- Developer apps and API keys:
  <https://cloud.google.com/apigee/docs/api-platform/publish/creating-apps-surface-your-api>

---

### MED-39. Every client call times out, and the Kubernetes object at fault is in another namespace

#### Scenario metadata

- ID: MED-39
- Difficulty: medium
- Primary topic: Apigee hybrid runtime and Kubernetes
- Secondary topics: Istio ingress, external IP assignment, misleading error strings
- Product: Apigee hybrid
- Origin: reported real-world case, sourced from official documentation retrieved live this
  session
  (<https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/ingressgateway/api-calls-fail-timeout-errors>),
  page last updated 2026-10-09
- Versions: checked 2026-10-12
- Evaluation objectives: every observable symptom reads as an application network fault,
  DNS fault or backend reachability fault. The documented root cause is a Kubernetes
  Service in `istio-system` that never bound an external IP. The agent must check
  cluster objects before testing backend reachability, and must read the installation-time
  errors as evidence about the same object rather than as a separate problem.
- Skills expected: apigee-support-core

#### Initial support ticket

> Since we rebuilt our Apigee hybrid cluster yesterday, every API call from outside the
> cluster times out. Nothing returns, not even a 4xx. From inside the cluster the
> message processors look healthy and the backend is reachable.
>
> The errors we can see are:
>
> ```
> * Connection failed
> * connect to 34.84.67.39 port 443 failed: Operation timed out
> * Failed to connect to example.apis.com port 443: Operation timed out
> * Closing connection 0
> curl: (7) Failed to connect to example.apis.com port 443: Operation timed out
> ```
>
> We also still have errors from the install:
>
> ```
> Error from server (Invalid): error when applying patch:
> ... Name: "istio-init-crd-10-1.4.6", Namespace: "istio-system"
> The Job "apigee-resources-install" is invalid : spec . template : Invalid value : core . PodTemplateSpec { ObjectMeta : v1 . ObjectMeta { Name : "apigee-resources-install" , ...
> ```
>
> We have checked the backend, the DNS records and our own network. Where do we start?

#### Initial evidence

All client calls fail to connect, with no HTTP response of any kind. This is a connection
failure before any Apigee policy runs, which already rules out most of the policy fault
catalogue. Installation-time errors reference Jobs in the `istio-system` namespace. The
customer has already done the application-layer checks.

#### Expected investigation

The agent should look for the one thing that would produce a uniform connect timeout with
no response at all, and should not start at the backend. The documented cause is the
Istio ingress LoadBalancer Service failing to acquire an external IP, which leaves no
listener bound on the address the clients resolve to.

The install-time errors are the same evidence, not a separate problem. The failing Jobs in
`istio-system` are the documented cause of the Service being stuck, so the agent should
read them as a single causal chain rather than as a second ticket.

#### Diagnostic evidence

```terminal
kubectl get services -n istio-system
NAME                   TYPE           CLUSTER-IP    EXTERNAL-IP   PORT(S)                                                     AGE
istio-ingressgateway   LoadBalancer   10.198.5.104  <pending>     15020:31927/TCP,12h                                         80:31381/TCP,443:31391/TCP,...
```

```terminal
kubectl get jobs -n istio-system
```

`EXTERNAL-IP` is `<pending>`, which is the finding. The documented causes for a Service
stuck in pending are, verbatim, "Jobs in erroneous/pending state in istio-system namespace"
and "Incorrect IP address range assigned to external load balancer" as configured in
`istio-operator.yaml`.

#### Ground-truth resolution

The ingress Service has no external IP, so nothing is listening on the address clients
resolve, and every client connection times out with no HTTP response. The absence of any
HTTP status is the diagnostic: an Apigee policy fault always produces a response, because
faults are turned into responses. A pure connect timeout means the request never reached
Apigee, which moves the investigation to the cluster rather than the proxy.

Both documented causes chain from the same object. Incomplete or erroneous Jobs in
`istio-system` block the Service from ever binding, and the install-time `Job "..." is
invalid` errors are the evidence of those Jobs. A misconfigured IP range in
`istio-operator.yaml` produces the same pending state without any Job error, so both checks
are needed.

#### Correct remediation

Confirm the Job status first and remove the failed Jobs so the Service can complete binding:

```terminal
kubectl get jobs -n istio-system
kubectl -n istio-system delete job <failed-job-name>
```

Then confirm the Service acquires an address:

```terminal
kubectl get services -n istio-system
```

If no Jobs are in an error state, the cause is the external load balancer configuration:
check the IP address range in `istio-operator.yaml` against the range provisioned for the
cluster and correct it, then reinstall or re-apply.

Because this is the ingress layer, the blast radius is the entire environment, not one
proxy. Deleting Jobs in `istio-system` affects every API proxy served by that ingress, so
it should be scheduled and the environment's consumers told, even though every consumer is
already failing.

#### Verification

Confirm `EXTERNAL-IP` is populated rather than `<pending>`. Then call a known API proxy
through the external hostname from outside the cluster and confirm a response of any
status, including a 4xx, because the point is that a response arrives at all.

Then confirm the install itself completed cleanly, so the same Jobs do not fail again on
the next reconcile.

#### Common incorrect answers

"Debug the target backend." The backend is not reached. Nothing Apigee-side, including any
policy, has run.

"Check DNS for example.apis.com." The record resolves; the address it resolves to has no
listener. The `curl: (7)` connect failure is consistent with either, which is exactly why
DNS alone cannot be ruled out from the client error string.

"Check the API proxy deployment and revision." No deployment state is involved. Nothing
reached the message processors.

"Restart the message processor pods." They are healthy and restarting them changes nothing,
because the failure is upstream of them.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Investigates the backend | Checks ingress networking | Identifies the pending ingress Service as the root cause |
| Diagnostic method | Tests client DNS | Reads the Service | Reads the Service and the istio-system Jobs as one causal chain |
| Handling of the error strings | Takes "Operation timed out" at face value | Notes no response arrives | Uses the absence of any HTTP response to exclude the policy layer entirely |
| Product knowledge | Treats it as an Apigee proxy fault | Moves to hybrid | Names Istio ingress, the `istio-system` namespace and both documented causes |
| Quality of next step | Retries the calls | Deletes Jobs | Checks Jobs, fixes the IP range if needed, schedules because blast radius is the whole environment |

#### Critical failures: restarting message processors; debugging the backend; asserting an
Apigee policy is at fault when no HTTP response was ever produced.

#### References

- Playbook, API calls fail with timeout errors, retrieved live this session and saved to
  `research/pages/api-platform_troubleshoot_playbooks_api-calls-fail-timeout-errors.txt`:
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/ingressgateway/api-calls-fail-timeout-errors>
- Playbook index, which lists the other runtime and ingress playbooks:
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/introduction>
- Note: guessed slugs under `.../playbooks/network/` return HTTP 200 with a generic title
  and no body. They are soft 404s. Real slugs live under `runtime/`, `ingressgateway/`,
  `deployment/` and `cassandra/`.

---

### Cases deliberately NOT converted into scenarios, and why

- **CASE 7, `messaging.config.beans.CertNotFound`** (keystore upload rejected for a valid
  2048-bit cert; real cause an X.509 extension OID encoded as a long integer). The
  narrative is excellent and the real cause is nowhere in the community thread except the
  closing comment, but the fault code is in **none** of: the local policy error index, any
  page under `research/pages/`, or the current Apigee provisioning error catalog at
  <https://cloud.google.com/apigee/docs/api-platform/errorcatalog/provisioning-errorcatalog>
  (retrieved live this session, HTTP 200, 180907 bytes; `CertNotFound` count 0,
  `messaging.config.beans` count 0). `scenarios/medium.md` instructs that codes not in
  `error-codes.md` must not be added, so this stays a note. Worth revisiting if that
  constraint is ever relaxed, because the "obvious explanations are all wrong" structure is
  the strongest in the set.
- **CASE 2, the JavaScript 200 ms limit** was folded into MED-36 rather than standing alone,
  because it shares its root cause with the proxy-within-proxy antipattern.
- **CASE 4, reading OAuth error text from `error.content`** was not proposed. Its answer is
  correct and documented, so it fails the "obvious explanation is wrong" bar. It is a good
  reference answer rather than a good diagnostic trap.
- **CASE 5, the 502** became MED-35, merged with the timeout-defaults finding from CASE 9,
  because the two together make the scenario that the obvious timeout theory is arithmetically
  impossible.

---

## Fault-code verification ledger

Every code used in the proposed scenarios, checked against
`.agents/skills/apigee-support-core/references/error-codes.md` unless the "source" column
says otherwise.

| Code used | HTTP | Where verified |
| --- | --- | --- |
| `policies.ratelimit.SpikeArrestViolation` | 429 | `error-codes.md` line 43 (MED-32, MED-33) |
| `policies.ratelimit.QuotaViolation` | 500 | `error-codes.md` line 42 (MED-37) |
| `steps.javascript.ScriptExecutionFailed` | 500 | `error-codes.md` line 61 (MED-36) |
| `steps.oauth.v2.InvalidAPICallAsNoApiProductMatchFound` | 401 | `error-codes.md` line 132 (MED-38) |
| `InvalidIndex` (KeyValueMapOperations deployment) | n/a | `error-codes.md` line 219 (MED-34) |
| `messaging.adaptors.http.flow.UnexpectedEOFAtTarget` | 502 | **not** in `error-codes.md`; `research/pages/mon_fault-codes.txt` line 81 (MED-35) |
| `messaging.adaptors.http.flow.GatewayTimeout`, reason `TARGET_READ_TIMEOUT` | 504 | **not** in `error-codes.md`; `research/pages/mon_fault-codes.txt` line 78, and the 504 playbook (MED-35) |

Confirmed mechanically: `grep -c "messaging.adaptors" error-codes.md` returns **0**. The
whole `messaging.adaptors.http.flow.*` namespace is a target-adaptor namespace and is
correctly absent from a policy-fault index. An agent that expects to find the 502 code in
the policy index will conclude the evidence is fabricated; the right move is to look in the
monitoring fault codes. That is a property worth evaluating on purpose.

Rejected: `messaging.config.beans.CertNotFound`. Not in `error-codes.md`, not in any cached
page, and not in the current provisioning error catalog (verified live, count 0). Kept out
of the scenario set.

## Coverage against the brief

| Requested topic | Covered by |
| --- | --- |
| OAuthV2 policy behaviour and errors | CASE 4, CASE 3 -> MED-38 |
| Quota and SpikeArrest surprises | CASE 1, CASE 6, CASE 8 -> MED-32, MED-33, MED-37 |
| Response cache staleness | CASE 15 (59607032) recorded above, not promoted to a scenario; accepted answer blames "random" invalidation, docs describe prefix-scoped `PurgeChildEntries` |
| TLS, keystore, certificate problems | CASE 7, CASE 9 -> not promoted, see exclusions |
| Deployments that succeed but do not take effect | CASE 12a -> folded into MED-38's spirit, see note |
| Shared flow resolution | CASE 12a (devrel#267) |
| KeyValueMap behaviour across environments | CASE 11 -> MED-34 |
| Management API and gcloud automation | CASE 11a, CASE 12b, CASE 12c |
| Hybrid runtime and Kubernetes issues | CASE 10 -> MED-39 |
| Flow variable syntax and conditions | CASE 11b (ref vs literal), CASE 13 |
| Accepted answer contradicts current docs | MED-32, MED-33, MED-34, MED-36, MED-37, CASE 13, CASE 14 |

Not covered for lack of a retrieved source: TLS/keystore on Apigee X and hybrid (only the
Edge-era CASE 7 was retrieved), and response cache staleness in a form I could turn into a
trap. Both are gaps worth a follow-up pass rather than something to fabricate.

## Retrieval honesty statement

Sources I actually fetched and read in this session:

- Stack Overflow question bodies and answer bodies for 30 question IDs, via
  `api.stackexchange.com/2.3`, with random cache-busters and per-ID JSON cached under
  `research/so/`. Every item re-asserted to carry the `apigee` tag before use, which is
  the guard against the stale-payload failure that ruined the previous run.
- 3 official Google Cloud documentation pages fetched live and saved to `research/pages/`:
  the Unexpected EOF playbook, the 504 target read timeout playbook, and the Istio ingress
  timeout playbook.
- 4 more official pages fetched live and saved: the two quota/RaiseFault antipatterns, the
  proxy-within-proxy antipattern, and the provisioning error catalog (which returned
  nothing useful).
- 1 GitHub issue fetched in full with all comments: `apigee/devrel#267`.
- 1 Stack Exchange API index sweep: 400 apigee-tagged questions across 4 pages, used only
  for triage.

Sources I could **not** retrieve, recorded so nobody repeats the attempt expecting success:
stackoverflow.com itself (403 Cloudflare, via curl and via WebFetch), StackPrinter in all
three URL forms (TLS hostname mismatch, busy interstitial, 404), and two guessed
Google Cloud playbook slugs that soft-404 with HTTP 200.
