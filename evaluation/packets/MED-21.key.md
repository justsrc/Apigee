# MED-21 answer key, do not show to the agent

## Ground-Truth Resolution
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

## Correct Remediation
Keep TLS on the target server. If the installed linter predates v2.67.0, suppress TD012 and TD006
for that proxy rather than restructuring the TargetEndpoint.

Do not add MaxFailures to satisfy TD015 on a single-server load balancer. Either leave it at the
documented default of 0, or add a `<HealthMonitor>`, which is the documented way to get a removed
server back into rotation without a redeploy.

## Verification
Lint the proxy on a version at or after v2.67.0 and confirm none of TD006, TD012 or TD015 fire on
this shape. Then confirm the connection to the target server actually negotiates TLS with the
expected certificate.

## Common Incorrect Answers
Adding SSLInfo to the TargetEndpoint to satisfy the first warning. It triggers the second warning and
misleads anyone reading the config later.

Adding SSLInfo to the TargetEndpoint because the security scan demands it, without checking whether
a LoadBalancer is in use. The rule differs by case and the agent should state which case applies.

Adding MaxFailures to silence TD015. That trades a lint warning for the documented antipattern,
where a single transient failure takes the only server out of rotation permanently.

Assuming one of the two authorities is simply wrong. Both are describing a real conflict created by
a tool that cannot see the target server.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Adds SSLInfo to TargetEndpoint | Names the contradiction | Explains the tool's limited reach and the MaxFailures antipattern |
| Diagnostic method | Picks a side | Checks both configs | Checks whether TargetServers are in the bundle and how many servers exist |
| Handling of competing causes | Declares one wrong | Hedges | States both rules are reachable and why |
| Quality of next step | Adds config | Suppresses the rule | Keeps TLS on the target server, cites v2.67.0, leaves MaxFailures alone |

## References
- Real report of the contradictory warnings, with the maintainer's fix plan and the v2.67.0
  confirmation:
  <https://github.com/apigee/apigeelint/issues/526>
- MaxFailures antipattern:
  <https://cloud.google.com/apigee/docs/api-platform/antipatterns/load-balancing-maxfailures>
- Load balancing across backend servers:
  <https://cloud.google.com/apigee/docs/api-platform/deploy/load-balancing-across-backend-servers>

## Critical failures
adding `SSLInfo` to `HTTPTargetConnection` without establishing whether a `<LoadBalancer>` is in use; adding `MaxFailures` to silence the linter; telling the customer one of
the two authorities is simply wrong.
