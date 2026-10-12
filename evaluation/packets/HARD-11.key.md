# HARD-11 answer key, do not show to the agent

## Ground-Truth Resolution
The firing setting is the proxy-level `api.timeout`, not the target timeout. The documented
order is: the Ingress sends its own timeout, which defaults to 300 seconds and is not
configurable; the Message Processor then sets `api.timeout` to the lesser of the Ingress
timeout and the proxy-level value, so 10 seconds here; and before connecting to the target
it sets `io.timeout.millis` to the lesser of `api.timeout` minus elapsed time and
`io.timeout.millis`, so the target's effective budget becomes 10 seconds as well. A
timeout writing the request or reading the response returns 504.

That is why raising the target timeout changed nothing. The team raised the larger of the
two numbers, and the smaller one kept winning.

The ServiceCallout is a red herring that can be eliminated on evidence rather than
hypothesis: a ServiceCallout timeout is documented to return 500 and put the proxy into an
error state, not 504, and this one is not near 10 seconds in any case.

Still unestablished: why the `api.timeout` property is there, whether it was copied from
another proxy, and whether every 504 in their traffic shares this cause. The discriminator
is in the body, since `flow.APITimedOut` and
`messaging.adaptors.http.flow.GatewayTimeout` are different findings.

## Correct Remediation
Decide the intended budget for the whole proxy, then set the two values so they agree.
`api.timeout` must be shorter than the standard Message Processor timeout of 300 seconds
and cannot be set with a variable, so changing it is a proxy change: new revision, new
deployment. Keep `io.timeout.millis` below it, because the lesser of the two is what
applies.

If the outbound call the proxy makes is slow, fix the inefficiency rather than the budget.
The documented recommendation is to cache the JWKS instead of fetching it per request.

## Verification
Confirm the 504s stop and that no request now runs materially longer, since a raised
timeout trades failures for latency. Confirm traces show the step completing rather than
timing out, and confirm the fault code on previously failing requests has changed.

## Common Incorrect Answers
Raisasing `io.timeout.millis` further. It was already the larger of the two values, so
this changes nothing and hides the cause.

Raising the ServiceCallout timeout. The callout cannot produce a 504, and the ticket
already tried the same reasoning on the target timeout.

Removing the callout to stop the timeouts, which silently removes whatever it fetched.

Concluding the target is slow because the request took 10 seconds. The 10 seconds is the
proxy's own budget, and the target never used it.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Diagnostic method | Raises timeouts | Notices the mismatch | Applies the documented precedence and names `api.timeout` |
| Technical correctness | More timeouts | Partial | Names `api.timeout` and the lesser-of rule that clamps the target |
| Handling of competing hypotheses | Callout | Two candidates | Eliminates the callout on status code, leaves the property's origin open |
| Verification | None | Retests | Checks the fault code and the latency cost of the change |

**Critical failures:** recommending further timeout increases without identifying which
timeout fires; naming the ServiceCallout timeout as the cause of a 504.

## References
- Endpoint properties reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/endpoint-properties-reference>
- ServiceCallout policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/service-callout-policy>
- JWT policies overview, JWKS caching guidance:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/jwt-policies-overview>
- API Monitoring fault codes:
  <https://cloud.google.com/apigee/docs/api-monitoring/fault-codes>

## Critical failures
 recommending further timeout increases without identifying which
