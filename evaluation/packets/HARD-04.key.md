# HARD-04 answer key, do not show to the agent

## Ground-Truth Resolution
The latency is in the VerifyJWT step. The plausible contributors were the target, a slow
policy, and caching; measurement rules out the target and localizes the rest to JWT
verification, which is consistent with the JWKS fetch behavior and with a gradual rise
rather than a step change.

What is not yet established is whether the slowness is the JWKS fetch itself or something
in the policy configuration. The documented recommendation to cache the JWKS rather than
executing a service callout per request is relevant, but the agent should not assert the
mechanism without a further measurement.

## Correct Remediation
Confirm whether a service callout is fetching the JWKS per request. If so, cache it as the
documentation recommends. Confirm the cached JWKS entry is being used and that the trace
step time falls.

If VerifyJWT is configured with an inline key rather than JWKS, investigate the token
verification cost itself before changing anything.

## Verification
Confirm the `JWT` step time in traces returns to baseline under the same load,
and confirm p95 and p99 both. Confirm the JWKS is not fetched per request.

## Common Incorrect Answers
Adding a response cache. That addresses the backend portion, which measurement shows is
not the problem.

Raising timeouts, which lengthens requests rather than reducing latency.

Concluding it is the backend because the step timings were not examined.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Diagnostic method | Guesses | Requests a trace | Requests per-step timings plus external measurement |
| Handling of competing causes | Picks one | Lists three | Uses measurement to localize, marks the rest unconfirmed |
| Technical correctness | Adds cache | Suspects policy | Localizes to VerifyJWT without overclaiming the mechanism |
| Quality of next step | Raises timeouts | Investigates JWKS | Investigates then applies the documented caching guidance |

**Critical failures:** asserting the cause without per-step evidence; adding a cache to
address a backend that is not the bottleneck.

## References
- VerifyJWT policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jwt-policy>
- Trace and debug:
  <https://cloud.google.com/apigee/docs/api-platform/debug/trace-overview>

## Critical failures
asserting the cause without per-step evidence; adding a cache to address a backend that is not the bottleneck.
