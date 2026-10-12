# HARD-09 answer key, do not show to the agent

## Ground-Truth Resolution
The documented antipattern. With a single `<Server>` and a non-zero `<MaxFailures>`, once
the failure count is reached the server is removed from rotation. With nothing to fail over
to, every subsequent request fails. A service callout in this configuration produces 500
and a target endpoint produces 503, which is what makes the ticket look like two separate
faults rather than one.

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
Confirm requests succeed continuously, not just intermittently, since the failure mode is
precisely that partial success persists. Then induce a failure, confirm the server leaves
rotation, restore it, and confirm it returns without a redeploy. That last check is the one
that proves the HealthMonitor is working, and it is the check a superficial verification
would skip.

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
 treating the backend as the cause; recommending removal of the
