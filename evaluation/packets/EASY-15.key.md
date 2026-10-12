# EASY-15 answer key, do not show to the agent

## Ground-Truth Resolution
The Quota policy is working. Quotas apply to individual API proxies and are not
distributed among API proxies, so three proxies with the same 10,000 limit allow roughly
30,000 requests in total.

The configuration is correct per proxy and wrong relative to the team's intent. This is an
expectation mismatch, not a fault.

## Correct Remediation
Decide where the limit should live. Either accept per-proxy counting and document it, or
apply the limit at a single shared point such as a parent shared flow, or move all
traffic behind one proxy.

Do not raise the per-proxy number to 30,000 as a fix, because that couples the limit to the
current proxy count and silently breaks when a proxy is added.

## Verification
Confirm the counter in analytics for one proxy reaches its limit and further requests from
that proxy are rejected. Then confirm the intended aggregate behavior across whichever
design you chose.

## Common Incorrect Answers
Raising the limit to 30,000 per proxy. That encodes the current proxy count into the
configuration.

Concluding the quota policy is defective. It enforces exactly as documented.

Adding a spike arrest policy. That addresses bursts, not monthly totals.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says quota is broken | Identifies multiple proxies | Explains the documented per-proxy scope rule |
| Diagnostic method | Changes config first | Counts proxies | Finds the scope rule in documentation |
| Safety | Raises limits | Suggests one option | Offers designs and rejects the naive limit increase |
| Verification | None | Checks analytics | Checks counters and aggregate behavior |
| Clarity | Asserts a defect | Correct | Leads with "the quota is working" |

**Critical failures:** recommending raising the per-proxy limit as the fix; asserting the
policy is defective.

## References
- Quota policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
- Comparing Quota and SpikeArrest:
  <https://cloud.google.com/apigee/docs/api-platform/develop/comparing-quota-and-spike-arrest-policies>

## Critical failures
recommending raising the per-proxy limit as the fix; asserting the policy is defective.
