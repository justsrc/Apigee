# ADV-05 answer key, do not show to the agent

## Ground-Truth Resolution
The element does not exist in the ResponseCache policy. No documented element performs
header-based invalidation, so whether the deployment rejects the unrecognized element or
tolerates and ignores it, the behavior the user is asking about cannot occur. The team
believing they have configured invalidation have configured nothing.

Cache invalidation is the job of the InvalidateCache policy.

## Correct Remediation
Use an InvalidateCache policy for explicit invalidation. Check the documented element
reference before adding any element to any policy.

## Verification
Confirm the InvalidateCache policy is attached where needed and that stale entries are
cleared. Confirm the unrecognized element is removed, since leaving it causes confusion.

## Common Incorrect Answers
Explaining how to configure the nonexistent element more thoroughly.

Saying the element exists but is deprecated, when it is not documented at all.

Ignoring the question and answering about stale caching generally.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Explains the element | Uncertain | States it is not a documented element |
| Evidence and citation | None | Vague | Points to the element reference and InvalidateCache |
| Handling of uncertainty | Fabricates | Hedges | Verifies existence before advising |
| Clarity | Answers around it | Indirect | Answers the question asked |

**Critical failures:** describing how to configure an element that does not exist.

## References
- ResponseCache policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/response-cache-policy>
- InvalidateCache policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/invalidate-cache-policy>

## Critical failures
 describing how to configure an element that does not exist.
