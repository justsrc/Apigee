# MED-13 answer key, do not show to the agent

## Ground-Truth Resolution
Two unrelated conditions produce the same error code and the same error description. A
malformed body reaches `ParseJSONResponse`, and a request with no `items` query parameter
reaches the other policy. Neither is a timeout, and neither is a bug in Apigee.

The discriminator is not the code and not even the description, both of which are shared.
It is the policy name and source line carried in the fault string. An agent that stops at
`ScriptExecutionFailed` cannot tell the two apart, and will keep fixing whichever policy
it happened to open first.

The correlation with peak traffic is because peak traffic includes proportionally more of
the client traffic that omits the parameter and sends the empty array.

## Correct Remediation
Guard both accesses, keyed on the fault string's policy name:

```javascript
// ParseJSONResponse.js
var parsed = context.getVariable("response.content");
var body = parsed ? JSON.parse(parsed) : [];
var first = body.length > 0 ? body[0] : null;
```

```javascript
// the query-parameter policy
var raw = context.getVariable("request.queryparam.items");
var items = raw ? String(raw).split(",") : [];
```

Treat the fault string as a diagnostic aid here while still keying any error handling on
the fault code.

## Verification
Send requests with and without the parameter, and with an empty array, a populated array
and no body. Confirm all succeed and that behavior for the well-formed cases is unchanged.
Confirm from the trace that the two conditions are now distinguishable by policy name.

## Common Incorrect Answers
Raising the JavaScript timeout, which does not apply to a null dereference.

Treating `ScriptExecutionFailed` as one specific bug and rewriting a single script blind.
The code is shared by two conditions in two policies.

Fixing only the policy whose name the team mentioned. The fault string names the one that
actually failed, and it may not be that one.

Ignoring the fault string because matching on prose is discouraged. It is discouraged for
error handling and useful for diagnosis, and conflating the two is its own error.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says code is insufficient | Asks for fault string | Identifies both conditions and names the shared description |
| Diagnostic method | Rewrites script | Requests fault string | Uses the policy name and line in the fault string to discriminate |
| Evidence and citation | None | Generic | Cites the JavaScript error reference |
| Handling of uncertainty | Asserts a cause | Hedges | Says what the code and the description each cannot distinguish |

## References
- JavaScript policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/javascript-policy>
- JavaScript runtime errors, including the full fault string format and the
  `Cannot read property "length" from undefined` example:
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/runtime/javascript-runtime-errors>
- Handling faults:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/fault-handling>

## Critical failures
recommending error handling that matches on `faultstring`; concluding one cause from the error description alone without reading the policy name in the fault
string.
