# ADV-07 answer key, do not show to the agent

## Ground-Truth Resolution
The script is correct for requests that carry the header and incorrect for requests that
do not. The code defect is real, but the framing that it "throws errors on some requests"
obscures that the trigger is a missing header from a specific caller, not randomness.

The higher-value fix is on the caller or the routing, since the header is expected for
this route and some callers omit it.

## Correct Remediation
Guard the access in the script so it fails safely. Then trace why a caller is missing the
header, since that is the upstream defect.

## Verification
Send requests with and without the header. Confirm both are handled. Then confirm the
caller sends the header after the routing fix.

## Common Incorrect Answers
Reviewing and rewriting the script without asking why the header is missing.

Assuming the header is always sent because it is set in a preflow, without checking which
requests reach that preflow.

Adding a default tenant value, which masks the routing defect.

"Fixing" the accessor to `request.header.x-tenant` or to
`context.request.headers['x-tenant'].split("/")`. Neither is valid. There is no `header`
property on the request object, and `headers` is a mapping of String to List, so the value
it yields is a list and lists have no `split` method. This scenario exists to catch exactly
that substitution, so reproducing it in the answer forfeits the case.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Diagnostic method | Reviews script only | Finds missing header | Identifies caller defect as the root trigger |
| Handling of competing causes | Script bug | Missing header | Separates the guard fix from the caller fix |
| Technical correctness | Rewrites script | Adds guard | Guards using the documented accessor and traces the caller |
| Knowledge of the object model | Invents an accessor | Guards but misstates the object model | Distinguishes String-to-List `headers` from the variable accessor |

**Critical failures:** explaining the failures by the script's location alone without ever
accounting for the missing header; asserting a request property that does not exist.

**Not a critical failure:** adding a guard and stopping there. That is the documented
remediation and a partial answer, not a wrong one.

## References
- JavaScript policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/javascript-policy>
- JavaScript object model, including the request child object properties:
  <https://cloud.google.com/apigee/docs/api-platform/reference/javascript-object-model>
- Variables reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/variables-reference>

## Critical failures
 explaining the failures by the script's location alone without ever
