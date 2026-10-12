# EASY-08 answer key, do not show to the agent

## Ground-Truth Resolution
The SpikeArrest policy failed. The documented cause of
`policies.ratelimit.InvalidMessageWeight` is that the value specified through a flow
variable is invalid because it is not an integer. The same code and cause are documented
on both the Quota and SpikeArrest pages.

The weight variable resolved to null or a non-numeric value under heavy traffic, which is
consistent with a counting step that falls back or fails to parse on an unusually shaped
request.

The heavy-traffic correlation is the clue worth following next, but it does not change
which policy failed.

## Correct Remediation
Make the counting step always produce an integer, with a default:

```javascript
var count = parseInt(context.getVariable("tokenCount"), 10);
if (isNaN(count) || count < 0) { count = 1; }
context.setVariable("tokenCount", count);
```

Then confirm what the counting step emits for the specific request shape seen under heavy
traffic, because a default prevents the failure without explaining it.

## Verification
Replay the request shape that triggered the fault and confirm the weight variable is a
positive integer. Then confirm quota and spike behaviour still behave as configured, so
the fallback did not silently change the effective rate limit.

## Common Incorrect Answers
Changing only the Quota policy because the error mentions rate limiting. The failing step
was SpikeArrest.

Asserting the code identifies the policy. It does not, which is documented.

Raising the weight to 0 to stop the error. A non-positive weight changes what the limit
means rather than fixing the parse.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Names the wrong policy | Acknowledges ambiguity | Names SpikeArrest from the trace and explains the shared code |
| Diagnostic method | Guesses from the prefix | Reads the code only | Uses the trace step name as the discriminator |
| Evidence and citation | None | One policy page | Cites both policy pages for the shared code |
| Handling of uncertainty | Asserts a policy | Hedges | States the code is ambiguous and names the test |

**Critical failures:** asserting the error code uniquely identifies a policy; editing the
Quota policy when SpikeArrest is the failing step.

## References
- Quota policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
- SpikeArrest policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy>

## Critical failures
 asserting the error code uniquely identifies a policy; editing the
