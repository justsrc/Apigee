# HARD-15 answer key, do not show to the agent

## Ground-Truth Resolution
Not a platform defect. The documented restriction explains the behavior completely, and
the update timing is coincidence.

The important skill is recognizing when to stop. An agent that assumed "after an update"
implied a defect would file noise, and filing noise costs real support time.

## Correct Remediation
Move the `target.url` assignment into the TargetEndpoint using an AssignVariable attached
there. Confirm against the AssignMessage documentation before writing the element.

## Verification
Replay the exact sequence and confirm a 200. Then confirm other sequences still work, so
the change did not alter unrelated behavior.

## Common Incorrect Answers
Confirming it is a platform bug without checking the documented restriction.

Refusing to engage because "it works on other requests".

Filing an escalation as the first response rather than after the documentation check.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Confirms a defect | Suspects coincidence | Finds the documented restriction |
| Diagnostic method | Files immediately | Investigates | Checks documented restrictions before escalating |
| Handling of uncertainty | Asserts a bug | Hedges | States the cause and the evidence |
| Quality of next step | Escalates | Recommends a change | Gives the correct location for the policy |

**Critical failures:** filing a defect without checking documented restrictions; asserting
a platform bug as established.

## References
- AssignMessage policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/assign-message-policy>
- API proxy configuration reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>

## Critical failures
 filing a defect without checking documented restrictions; asserting
