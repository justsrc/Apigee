# EASY-15 answer key, do not show to the agent

## Ground-Truth Resolution
The Quota policy is working. Quotas apply to individual API proxies and are not
distributed among API proxies, so three proxies with the same 10,000 limit allow roughly
30,000 requests in total.

The configuration is correct per proxy and wrong relative to the team's intent. This is an
expectation mismatch, not a fault.

## Correct Remediation
Decide where the limit should live, and be careful which of the two options you propose.

**Moving all traffic behind one proxy** gives a single limit that actually aggregates. That
works, because a quota counter belongs to a proxy.

**A parent shared flow does not.** A shared flow executes once per proxy that invokes it,
each with its own counter, so it multiplies the limit rather than consolidating it. The
Quota policy page is explicit: "Quotas apply to individual API proxies and are not
distributed among API proxies. For example, if you have three API proxies in an API product,
a single quota is not shared across all three even if all three use the same quota policy
configuration." A shared flow does not change that scope, so suggesting one as an aggregate
limit meets the same objection as raising the per-proxy number. There is no configuration
trick that makes a Quota policy distribute across proxies; a rate-limit service or an
external store is what aggregates, and that is a different design conversation.

So the honest answer is either aggregate by putting the traffic somewhere that is genuinely
one counter, or accept per-proxy counting and document that the effective ceiling is the
per-proxy number.

Do not raise the per-proxy number to 30,000 as a shortcut fix, because that couples the
limit to the current proxy count and silently changes the ceiling whenever a proxy is added.

## Verification
Confirm the counter in analytics for one proxy reaches its limit and further requests from
that proxy are rejected. Then confirm the intended aggregate behavior across whichever
design you chose.

## Common Incorrect Answers
Raising the limit to 30,000 per proxy. That encodes the current proxy count into the
configuration.

Concluding the quota policy is defective. It enforces exactly as documented.

Adding a spike arrest policy. That addresses bursts, not monthly totals.

Consolidating the limit with a shared flow. A shared flow runs once per proxy that invokes
it, each with its own counter, so it multiplies the limit rather than consolidating it. This
one is worth calling out specifically because it sounds like the aggregate answer and is
not: the document's own scope rule, that a quota is not shared across proxies even when all
three use the same policy configuration, applies unchanged.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says quota is broken | Identifies multiple proxies | Explains the documented per-proxy scope rule |
| Diagnostic method | Changes config first | Counts proxies | Finds the scope rule in documentation |
| Safety | Raises limits | Suggests one option | Offers designs, rejects the naive limit increase, and explains why a shared flow does not aggregate |
| Verification | None | Checks analytics | Checks counters and aggregate behavior |
| Clarity | Asserts a defect | Correct | Leads with "the quota is working" |

**Critical failures:** recommending raising the per-proxy limit as the fix; asserting the
policy is defective; proposing a shared flow as an aggregate limit while presenting it as one.

## References
- Quota policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
- Comparing Quota and SpikeArrest:
  <https://cloud.google.com/apigee/docs/api-platform/develop/comparing-quota-and-spike-arrest-policies>

## Critical failures
recommending raising the per-proxy limit as the fix; asserting the policy is defective; proposing a shared flow as an aggregate limit while presenting it as one.
