# MED-13 answer key, do not show to the agent

## Ground-Truth Resolution
The script dereferences a query parameter that is not always present. Requests without it
fail; requests with it succeed. The correlation with peak traffic is because peak traffic
includes proportionally more requests from clients that omit the parameter.

`ScriptExecutionFailed` is a family of errors rather than one error, which is why the code
alone did not identify the problem. The documented note is to check the fault string for
details.

## Correct Remediation
Guard the access:

```javascript
var raw = context.getVariable("request.queryparam.items");
var items = raw ? String(raw).split(",") : [];
```

Treat the fault string as a diagnostic aid here while still keying any error handling on
the fault code.

## Verification
Send requests with and without the parameter. Confirm both succeed and that the behavior
with the parameter is unchanged.

## Common Incorrect Answers
Raising the JavaScript timeout, which does not apply to a null dereference.

Treating `ScriptExecutionFailed` as one specific bug and rewriting the script blind.

Ignoring the fault string because matching on prose is discouraged. It is discouraged for
error handling and useful for diagnosis, and conflating the two is its own error.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says code is insufficient | Asks for fault string | Identifies the null dereference |
| Diagnostic method | Rewrites script | Requests fault string | Requests fault string and finds the cause |
| Evidence and citation | None | Generic | Cites the JavaScript error reference |
| Handling of uncertainty | Asserts a cause | Hedges | Names what the code cannot show alone |

## References
- JavaScript policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/javascript-policy>
- Handling faults:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/fault-handling>

## Critical failures
recommending error handling that matches on `faultstring`. #### References
- JavaScript policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/javascript-policy>
- Handling faults:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/fault-handling>
---
