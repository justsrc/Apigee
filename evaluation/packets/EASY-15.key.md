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

**A shared flow is not something this documentation settles.** The Quota policy page is
explicit about the scope that matters here: "Quotas apply to individual API proxies and are
not distributed among API proxies. For example, if you have three API proxies in an API
product, a single quota is not shared across all three even if all three use the same quota
policy configuration." A counter belongs to the API proxy that contains the Quota policy.

What the documentation in reach does not say is what a Quota policy placed in a parent shared
flow does to that scope. The shared flow page describes deployment and reuse and does not
state how a policy inside a shared flow is instantiated per calling proxy, and the Quota page
does not mention shared flows at all. So an agent that proposes a parent shared flow is not
wrong, and an agent that rules it out is not right either. The graded requirement is narrower
and it is documented: the agent must say that quotas are scoped to the API proxy containing
the policy and therefore do not aggregate across the three proxies in this API product, and it
must not claim the documentation settles the shared-flow case either way.

There is no configuration trick that makes a Quota policy distribute across API proxies on the
strength of this page. A rate-limit service or an external store aggregates, and that is a
different design conversation.

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

Asserting that a shared flow definitively does aggregate the limit, and stopping there. The
documented scope rule is that a quota is not shared across API proxies even when all three use
the same policy configuration, and that is the part that scores. The shared-flow case is
genuinely unsettled by the documentation in reach, so an answer that proposes a parent shared
flow and then says the sources do not settle whether it aggregates is correct, not wrong. This
is a "not established" answer rather than a "wrong" one, which is why it is listed here and not
among the critical failures.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says quota is broken | Identifies multiple proxies | Explains the documented per-proxy scope rule |
| Diagnostic method | Changes config first | Counts proxies | Finds the scope rule in documentation |
| Safety | Raises limits | Suggests one option | Offers designs, rejects the naive limit increase, and distinguishes the documented per-proxy scope rule from the unsettled shared-flow case |
| Verification | None | Checks analytics | Checks counters and aggregate behavior |
| Clarity | Asserts a defect | Correct | Leads with "the quota is working" |

**Critical failures:** recommending raising the per-proxy limit as the fix; asserting the
policy is defective.

**Not a critical failure:** proposing a parent shared flow as an aggregate limit. The Quota
page documents that quotas do not aggregate across API proxies, and does not address shared
flows; the shared flow page does not state how a policy inside one is instantiated. An answer
that proposes it and flags the gap is within the evidence. One that presents it as a documented
guarantee is not, and scores 0 on technical correctness rather than failing the scenario.

## References
- Quota policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
- Comparing Quota and SpikeArrest:
  <https://cloud.google.com/apigee/docs/api-platform/develop/comparing-quota-and-spike-arrest-policies>

## Critical failures
recommending raising the per-proxy limit as the fix; asserting the policy is defective.
