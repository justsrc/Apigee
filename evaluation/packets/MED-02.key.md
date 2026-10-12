# MED-02 answer key, do not show to the agent

## Ground-Truth Resolution
Revision 12 is deployed to `test` and ready. The `prod` deployment is still propagating.

The deployment API call returning success means the deployment was accepted, not that
every runtime has finished loading it. Deployment state is a separate check, which is why
it exists.

The old behavior the colleague saw is the previous revision still serving on part of the
runtime, and the 404 is the environment group issue from MED-01 affecting one hostname.

## Correct Remediation
This mostly needs time and observation, not intervention. Confirm the `prod` deployment
reaches `READY`, and separately resolve the environment group membership that is causing
the 404.

Do not redeploy to "speed it up". Redeploying does not shorten propagation and adds a
revision to the history.

## Verification
Wait for `READY` on `prod`, then confirm requests from the second region serve revision 12.
Keep checking the 404 separately, because propagation and environment group membership
are independent problems that happen to present together.

## Common Incorrect Answers
Redeploying to force propagation.

Claiming deployments are regional by design. Nothing in the evidence supports a regional
deployment model, and that framing would mislead the team about their topology.

Blaming the customer's DNS without checking the deployment state.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says deployments are regional | Identifies propagation | Separates save, state, and routing |
| Diagnostic method | Redeploys | Checks traffic | Checks deployment state per environment |
| Handling of competing causes | Merges both into one | Notes both | Keeps them independent |
| Safety | Redeploys | Waits | Waits and fixes the other issue separately |

## References
- Deploy an API proxy revision:
  <https://cloud.google.com/apigee/docs/api-platform/deploy/ui-deploy-overview>

## Critical failures
asserting a regional deployment model without evidence. #### References
- Deploy an API proxy revision:
  <https://cloud.google.com/apigee/docs/api-platform/deploy/ui-deploy-overview>
---
