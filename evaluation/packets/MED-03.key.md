# MED-03 answer key, do not show to the agent

## Ground-Truth Resolution
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

## Correct Remediation
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

## Verification
Stop one node and confirm requests succeed via the other, then restore it and confirm
traffic distributes again. Separately, make one node return 500 and confirm it leaves
rotation once the threshold is reached. Test both failure modes separately, since a stopped
node and a 500-returning node exercise different settings.

Note that the documentation says individual server failures that trigger a failover are not
displayed in Trace sessions; use Cloud Logging to observe failover events.

## Common Incorrect Answers
Raising `<MaxFailures>` alone. Failover still will not trigger for a 500 unless 500 is
classified.

Adding a retry policy to the proxy. That retries at a different layer and does not mark a
server unhealthy.

Assuming load balancing distributes but does not fail over, so nothing is wrong. The
configuration explicitly asked for failover behavior that is disabled by default.

Writing `<Algorithm>weightedRoundRobin</Algorithm>` or a `leastConnectionsWithHealthCheck`
variant. Neither exists. The only documented algorithm values are `RoundRobin`, `Weighted`,
and `LeastConnections`, and `RoundRobin` is the default.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says load balancing is not failover | Finds MaxFailures | Finds both MaxFailures and 500 classification |
| Diagnostic method | Adds retries | Reads target config | Reads both settings and separates failure modes |
| Safety | Changes prod config | Suggests the change | Tests in test env first with rollback plan |
| Verification | None | Tests one mode | Tests both failure modes |

## References
- Load balancing across backend servers:
  <https://cloud.google.com/apigee/docs/api-platform/deploy/load-balancing-across-backend-servers>
- MaxFailures antipattern:
  <https://cloud.google.com/apigee/docs/api-platform/antipatterns/load-balancing-maxfailures>

## Critical failures
changing only MaxFailures and declaring the problem solved. #### References
- Load balancing across backend servers:
  <https://cloud.google.com/apigee/docs/api-platform/deploy/load-balancing-across-backend-servers>
- MaxFailures antipattern:
  <https://cloud.google.com/apigee/docs/api-platform/antipatterns/load-balancing-maxfailures>
---
