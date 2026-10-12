# HARD-10 answer key, do not show to the agent

## Ground-Truth Resolution
Mitigation is established. Diagnosis is not.

The restart plausibly cleared a degraded runtime, which is consistent with the memory
observation. It is also consistent with the failures having coincided with something
else that ended at 15:00. The evidence does not distinguish these.

What can be said: restarting the runtime restored service, memory on that runtime was
elevated during the failure window, and the cause of the elevation is unestablished.

## Correct Remediation
Do not close on the grounds that restarting fixed it. Collect the evidence that would
close it: the elevated runtime's memory profile before the restart if still available,
the logs from the failure window, and whether anything else changed at 15:00.

Record the incident as mitigated with cause unconfirmed, and add monitoring for the
condition that was observed.

## Verification
There is nothing to verify in the traffic sense, since traffic is fine. The verification
is of the future: confirm the memory condition is monitored and that a recurrence would
be caught.

## Common Incorrect Answers
Confirming the fix and closing.

Attributing it to the restart as established cause.

Recommending more restarts as a mitigation strategy, which converts an undiagnosed issue
into a recurring routine.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Handling of uncertainty | Declares fixed | Hedges | Separates mitigation from diagnosis explicitly |
| Evidence quality | None | Cites timing | States what is known, unknown, and what would close it |
| Quality of next step | Close | Add monitoring | Collect specific evidence, do not close |
| Clarity | Conclusive | Qualified | Clear distinction between restored and explained |

**Critical failures:** declaring the root cause confirmed because the symptom stopped.

## References
- Trace and debug:
  <https://cloud.google.com/apigee/docs/api-platform/debug/trace-overview>
- Compare Apigee products:
  <https://cloud.google.com/apigee/docs/api-platform/get-started/compare-apigee-products>

## Critical failures
declaring the root cause confirmed because the symptom stopped.
