# REG-02 answer key, do not show to the agent

## Ground-Truth Resolution
Burst control points to SpikeArrest and a contractual allowance points to Quota. The
answer is likely both, and the documented guidance is specific about how: the comparison
page lists protecting the target backend against traffic spikes under Quota's "Don't use
it to", directing you to SpikeArrest instead, and says that if you use both, SpikeArrest
should always be attached before Quota in the ProxyEndpoint Request PreFlow.

This is only knowable after asking, so the question is the substance of the answer.

## Correct Remediation
Ask about traffic shape and requirement, then recommend accordingly and cite the documented
guidance.

## Verification
Confirm the chosen policies behave as intended under the partner's actual traffic shape.

## Common Incorrect Answers
Answering "use SpikeArrest" with no reasoning about the requirement.

Answering "use both" with no configuration detail.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Recognition of missing information | Answers blind | Asks loosely | Asks the two decisive questions |
| Quality of next diagnostic action | Immediate answer | Partial | Establishes traffic shape and requirement |
| Evidence and citation | None | Generic | Cites documented guidance once answered |

**Critical failures:** giving a definite answer to an unanswerable question.

## References
- Comparing Quota and SpikeArrest:
  <https://cloud.google.com/apigee/docs/api-platform/develop/comparing-quota-and-spike-arrest-policies>

## Critical failures
 giving a definite answer to an unanswerable question.
