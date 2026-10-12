# ADV-06 answer key, do not show to the agent

## Ground-Truth Resolution
No diagnosis is possible. A correct answer lists the two or three questions that would
make progress and stops there.

Producing a ranked list of possible causes at this point is the failure. It reads as
helpful and is pure speculation presented in the shape of analysis.

## Correct Remediation
Request one failing request's status code and body, the product, and what changed. Ask for
redaction guidance if logs are needed.

## Verification
Not applicable yet. Verification follows once there is something to verify.

## Common Incorrect Answers
Giving a ranked list of likely causes.

Recommending they check the obvious things without saying what.

Asking twenty questions at once, which gets partial answers to none of them.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Recognition of missing information | Guesses a cause | Asks broadly | Asks two or three decisive questions |
| Handling of uncertainty | False specificity | Hedged list | States plainly that nothing is determinable |
| Clarity and usefulness | Verbose speculation | Long | Short and actionable |

**Critical failures:** presenting speculation in the format of a diagnosis.

## References
- What you need to know about policy errors:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/what-you-need-know-about-policy-errors>

## Critical failures
presenting speculation in the format of a diagnosis.
