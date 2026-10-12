# MED-15 answer key, do not show to the agent

## Ground-Truth Resolution
The documented runtime error for this policy is `steps.javacallout.ExecutionError`, HTTP
500, raised "when Java code throws an exception or returns null during the execution of a
JavaCallout policy". That is the whole runtime error table, and the code carries the
`steps.` prefix. The bare `javacallout.ExecutionError` form appears in the example error
response further down the same page, so a reader copying the example rather than the
runtime errors table will reproduce it wrong; the runtime errors table and the
`error-codes.md` reference both carry the prefix.

The names an agent might reach for instead, `JavaClassNotFoundInJavaResource`,
`JavaCalloutInstantiationFailed`, `JavaClassDefinitionNotFound`, `NoAppropriateConstructor`,
`ResourceDoesNotExist` and `NoResourceForURL`, are all in the deployment error table, with
no HTTP status, because they fire when the proxy is deployed. A successful deployment rules
every one of them out, and none of them can appear in a request-time trace.

The failure is request-scoped and the pattern is stateful: the callout's own logic is failing
on repeat invocations, not the runtime failing to load the class.

An honest answer stops short of naming the exact line of Java. The fault code and the generic
faultstring do not carry the exception, so the cause has to come from the source or a full
stack trace.

## Correct Remediation
Request the full stack trace or the callout source. The fault code alone will not identify
which exception was thrown.

Review the callout for per-request state assumptions, such as a resource initialised on first
use and then assumed present on later calls.

If a later run does show a class-resolution failure, that is a separate case and belongs to
the deployment table: confirm the jar is packaged under `/resources/java` in the proxy bundle
and that only one copy of a given JAR is deployed, since multiple copies can cause
non-deterministic runtime behaviour through ClassLoader conflicts.

## Verification
Replay the request sequence that reproduces it, confirm the failure pattern disappears after
the fix, and confirm the first-request behaviour still works.

## Common Incorrect Answers
Rebuilding and redeploying the jar. It deployed successfully and the jar did not change.

Concluding `JavaClassNotFoundInJavaResource` from a runtime failure. That name is a
deployment error; it cannot be the cause when the deployment succeeded.

Removing the callout from the flow, which silently removes whatever validation it
performed.

Asserting a specific Java exception from the fault code alone. The code does not carry it.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Rebuilds the jar | Recognizes request-scoped | Uses the runtime table and rules out the deployment table |
| Diagnostic method | Redeploys | Reads trace | Establishes deploy versus runtime before naming a cause |
| Handling of uncertainty | Invents an exception | Hedges | States what cannot be known without the stack trace |
| Quality of next step | Removes callout | Asks for source | Asks for stack trace and reviews state assumptions |

## References
- Java callout policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/java-callout-policy>
- What you need to know about policy errors:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/what-you-need-know-about-policy-errors>

## Critical failures
naming a deployment error name as the runtime cause; asserting a specific Java exception from a fault code alone; removing a validation callout to make the
symptom disappear.
