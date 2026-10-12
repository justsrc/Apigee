# MED-35 answer key, do not show to the agent

## Ground-Truth Resolution
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

## Correct Remediation
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

## Verification
After any change, confirm the symptom by forcing it: send a request the backend will hold
for longer than the configured timeout and confirm the status code changes to the documented
one for the new timeout, which is `504` for a read timeout. A 502 that becomes a 504 is
progress; a 502 that becomes a 200 means the keep-alive change worked.

Confirm the fault code in the ingress log is no longer `messaging.adaptors.http.flow.UnexpectedEOFAtTarget`
and that `x_apigee_fault_source` no longer reads `target`.

## Common Incorrect Answers
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

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Asserts a 120 s Apigee timeout | Rules out timeouts by status code | Rules out timeouts by status code and by the documented 3 s / 55 s defaults |
| Diagnostic method | Changes a timeout value | Works the playbook causes | Tests the documented causes and says explicitly that they do not fit the signature |
| Source discipline | Treats `mon_fault-codes` as a policy index | Notes the index gap | States the code is a target-adaptor code outside the policy error index |
| Honesty about limits | Confidently names a cause | Hedges | Names what is documented, names what is not, and requests scoped evidence |
| Quality of next step | Raises `io.timeout.millis` | Fixes keep-alive direction | Fixes keep-alive direction, checks the NLB conditions, prepares the exact case attachments |

## References
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

## Critical failures
asserting an undocumented 120-second Apigee timeout; raising `io.timeout.millis` as the remedy for a 502; telling the customer to raise the backend
keep-alive above Apigee's.
