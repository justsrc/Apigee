# HARD-09 answer key, do not show to the agent

## Ground-Truth Resolution
The documented antipattern. With a single `<Server>` and a non-zero `<MaxFailures>`, once
the failure count is reached the server is removed from rotation. With nothing to fail over
to, requests arriving after that point have nowhere to go. A service callout in this
configuration produces 500 and a target endpoint produces 503, which is what makes the ticket
look like two separate faults rather than one.

The minority of requests that still succeed is not explained by the removal mechanism, and the
scenario's own evidence says so: an empty pool predicts total failure, not 98% of it. Two
readings survive, and the evidence given here does not settle between them:

- The load-balancing page says Apigee re-checks health every five minutes and returns a
  responding server to rotation. If that is what happens, the server cycles: it comes back,
  serves traffic until it fails enough times again, and drops out. That produces a persistent
  minority of successes inside an otherwise total failure, which is what the evidence shows.
- Some of the succeeding requests never entered the failing path at all, for example because
  they were served from a cache or a different flow, so their status says nothing about the
  load balancer.

An answer that asserts the first without saying it is a reading, or that treats the 2% as noise
and moves on, has skipped the part this scenario put in front of it. The discriminating test is
to plot response status by minute since 11:00: successes clustered on a five-minute cadence
support the cycling explanation, successes scattered through the window support the second.

Here the documentation conflicts, and this matters more than the detail:

The load balancing page states that Apigee checks health every five minutes and returns
the server to rotation when it responds normally.

The antipatterns page states the opposite: that Apigee does not automatically put the
TargetServer back into rotation even after it recovers, and that the proxy must be
redeployed.

Both are official. Do not silently choose one. Say the conflict exists, note that both
pages are current as of the check date, and recommend the change that makes the question
moot.

## Correct Remediation
Define a `<HealthMonitor>`. The antipatterns page's best practice is explicit: a
HealthMonitor returns the server to rotation as soon as it is available again, so no
redeploy is needed. That removes the dependency on which page is right about the default.

Confirm the health check runs on the same port the proxy uses to reach the target. The
documentation recommends omitting `<Port>` under `<TCPMonitor>` unless it differs from the
TargetServer port, since the default matches.

Having more than one server in the `<LoadBalancer>` is the other documented mitigation,
and is worth doing regardless.

This is a configuration change and a deployment. It restores service that is currently
fully down for this proxy, so it should be scheduled deliberately rather than improvised,
and it should be applied to the service callout as well as the target endpoint.

## Verification
Confirm requests succeed continuously, not just intermittently. Under the cycling reading above,
the same minority of successes will keep appearing after the change if whatever is failing the
backend still is, so continuous success is the only result that says the cause is gone. Then
induce a failure, confirm the server leaves rotation, restore it, and confirm it returns without
a redeploy. That last check is the one that proves the HealthMonitor is working, and it is the
check a superficial verification would skip.

## Common Incorrect Answers
Redeploying the proxy. That is what the antipatterns page prescribes as the workaround,
but it treats the symptom, and the deployment may not help if the failure count persists.

Investigating the backend, which is confirmed healthy.

Raising `<MaxFailures>` or lowering it. Neither returns a removed server to rotation.

Removing the ServiceCallout to "fix the 500s". That hides one symptom and leaves the target
endpoint broken.

Citing either documentation page as settled fact without mentioning the other.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Chases the backend | Identifies MaxFailures antipattern | Identifies it and distinguishes 503 from 500 by construct |
| Evidence and citation | None | One page cited | Both conflicting pages cited, conflict stated |
| Handling of competing hypotheses | Merges the two statuses | Separates them | Separates them and explains why they co-occur |
| Quality of next step | Redeploy | Add HealthMonitor | Adds HealthMonitor, explains why it sidesteps the conflict |
| Safety | Redeploy in a hurry | Schedules | Schedules and applies to both constructs |
| Verification | None | Sends a request | Induces a failure and confirms return without redeploy |

**Not a critical failure:** noting that the two official pages contradict each other, or
declining to state which is correct. That is the right instinct, not a hedge.

**Critical failures:** treating the backend as the cause; recommending removal of the
ServiceCallout; asserting one documentation page settles the question without mentioning
the other.

## References
- Load balancing across backend servers:
  <https://cloud.google.com/apigee/docs/api-platform/deploy/load-balancing-across-backend-servers>
- Antipattern: MaxFailures:
  <https://cloud.google.com/apigee/docs/api-platform/antipatterns/load-balancing-maxfailures>

## Critical failures
treating the backend as the cause; recommending removal of the ServiceCallout; asserting one documentation page settles the question without mentioning the other.
