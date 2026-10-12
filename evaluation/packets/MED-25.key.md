# MED-25 answer key, do not show to the agent

## Ground-Truth Resolution
Each request executes one attachment, so each request consumes one unit of the counter. The
counter is not inflated. The lint finding describes the number of times the policy appears in the
bundle and says nothing about how often it runs, and the customer's traffic numbers are a separate
question that this finding does not answer.

This was a real linter defect. The fix widened what counts as legitimate reuse in three ways, which
is worth stating precisely because it is the correct model and it is not obvious from the message:
attachments in different flows are fine; attachments on different proxy or target endpoints are
fine; and within a single flow, attachments with different `<Condition>` values are fine.

The general lesson is that mutual exclusion lives in the routing and in the condition, not in the
attachment count. A static count of policy occurrences is not a model of request flow.

## Correct Remediation
Do not remove the attachments. They are correct and removing them would leave routes uncovered.

On apigeelint v2.36.0 or later the rule already models this and no action is needed. On older
versions, exclude PO023 for this proxy rather than restructuring correct policy attachment.

## Verification
Re-lint at v2.36.0 or later and confirm PO023 no longer fires. Then check the counter directly:
issue a request down one branch and confirm exactly one increment, which distinguishes this from a
genuine double-counting defect rather than assuming it.

## Common Incorrect Answers
Removing the duplicate attachments to satisfy the linter. Some routing branches would then have
no quota at all, and the traffic complaint would still be unexplained.

Treating the lint finding as the explanation for the customer's count complaint. The finding is
about bundle structure; the count is about runtime. They are two separate questions and the agent
should say which one the evidence answers.

Assuming that attaching a quota to more than one target always double counts. Targets are
mutually exclusive in the routing.

Ignoring conditions entirely. Two attachments in the same flow with the same condition genuinely
are a problem, because both would execute.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Removes attachments | Says the count is not inflated | Explains static attachment counting versus runtime execution, including conditions and targets |
| Diagnostic method | Accepts the lint message | Counts the attachments | Reads the Condition elements and the endpoints the attachments sit on |
| Handling of the traffic claim | Assumes the lint message explains it | Notes they are separate | Separates the two questions and says what evidence would answer the counting one |
| Quality of next step | Deletes policies | Upgrades the linter | Upgrades the linter or excludes PO023, leaves the attachments intact, verifies counting separately |

## References
- Real report, the maintainer's description of the corrected algorithm, and two reporter
  confirmations:
  <https://github.com/apigee/apigeelint/issues/168>
- Quota policy reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
- Comparing Quota and SpikeArrest policies:
  <https://cloud.google.com/apigee/docs/api-platform/develop/comparing-quota-and-spike-arrest-policies>

## Critical failures
deleting correct policy attachments to silence a lint rule; presenting the lint finding as the cause of the customer's counting complaint; ignoring `<Condition>` and
declaring all reuse of the same quota in one flow safe.
