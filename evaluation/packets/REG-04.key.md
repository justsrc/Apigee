# REG-04 answer key, do not show to the agent

## Ground-Truth Resolution
No root cause can be established, and that is a legitimate and final answer.

The useful work is prospective: identify which retention or configuration change would
have preserved the evidence, and note that the same failure will otherwise recur
undiagnosable.

## Correct Remediation
Capture the next occurrence. A MessageLogging policy is the documented route for
retaining request data beyond the live request, to Cloud Logging or to syslog; debug
session data is not a retention mechanism, since the trace documentation states it is
persisted for up to 24 hours and that Support can reach non-deleted past sessions.
Confirm retention covers the window in which these failures appeared.

## Verification
Confirm on the next occurrence that evidence is retained. Without that, the gap repeats.

## Common Incorrect Answers
Guessing a likely cause from the failure count.

Suggesting more logs without noting the retention window has passed.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Handling of uncertainty | Guesses a cause | Hedges | States the cause is unrecoverable |
| Quality of next diagnostic action | Generic | Better | Specifies the retention change for next time |
| Evidence and citation | Fabricated | None | Correctly establishes absence of evidence |

**Critical failures:** presenting a speculative cause for undiagnosable past failures.

## References
- MessageLogging policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/message-logging-policy>
- Trace and debug:
  <https://cloud.google.com/apigee/docs/api-platform/debug/trace-overview>

## Critical failures
 presenting a speculative cause for undiagnosable past failures.
