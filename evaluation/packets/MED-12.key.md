# MED-12 answer key, do not show to the agent

## Ground-Truth Resolution
The callout's own timeout is the one firing. The documented behaviour is that when a
ServiceCallout hits its timeout, an HTTP 500 is returned, the policy fails, and the proxy goes
into an error state. The upstream's p95 being healthy did not rule out a timeout, because
timeouts are tail-sensitive and p95 hides the tail entirely.

Raising the enrichment service's timeout, as they did, was addressing a different timeout
that was not the failing one.

## Correct Remediation
Decide what should happen when enrichment is slow, because a longer timeout on a
synchronous callout lengthens every affected request. Options are to raise the callout
timeout within a latency budget, to make enrichment non-blocking with a fault rule that
degrades gracefully, or to cache enrichment results.

Handle it in a fault flow rather than letting the callout fault surface as a 500.

## Verification
Replay slow enrichment requests and confirm the intended behavior, whether that is
succeeding, degrading, or failing fast. Then confirm p99.9 latency, not p95, since p95 is
what hid this in the first place.

## Common Incorrect Answers
Raising the callout timeout without a fault rule. That converts timeouts into long
requests.

Adding retries inside the callout, which multiplies the latency under exactly the
conditions where latency is already the problem.

Looking at the enrichment service's dashboard averages rather than its tail.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Raises a timeout blindly | Identifies callout timeout | Names which timeout fires and why p95 misled |
| Diagnostic method | Trusts averages | Reads trace | Reads the failing step in the trace |
| Quality of next step | Raises timeout | Suggests fault flow | Offers degradation with a budget |
| Verification | None | Retests | Tests tail behavior explicitly |

## References
- ServiceCallout policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/service-callout-policy>
- Handling faults:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/fault-handling>

## Critical failures
recommending a timeout increase with no fault handling; reasoning from p95 to rule out a tail problem.
