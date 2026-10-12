# MED-02 answer key, do not show to the agent

## Ground-Truth Resolution
Revision 12 is deployed to `test` and ready. The `prod` deployment is still propagating
across Message Processors.

The deployment API call returning success means the deployment was accepted, not that
every runtime has finished loading it. Deployment state is a separate check, which is why
it exists.

Propagation explains one of the two symptoms and the documentation does not reach the other.
An MP that has not finished applying revision 12 is still serving revision 11, which is the
old behavior, so that accounts for the colleague. It does not account for the 404: deployment
is zero-downtime, the new revision is applied before the old one is undeployed, so there is no
documented window in which a Message Processor serves neither. An agent that says so is
reading the deployment model correctly, not splitting hairs.

The 404 therefore needs its own cause, and the evidence does not supply one. That is the
honest state of the case: wait for `READY` on `prod`, and if the 404 is still there, keep
looking. What the evidence rules out is the opposite move, which is to declare a routing or
environment-group fault while the deployment is still propagating, because it fits the
symptom and not the evidence.

## Correct Remediation
This needs time and observation, not intervention. Confirm the `prod` deployment reaches
`READY`.

Do not redeploy to "speed it up". Redeploying does not shorten propagation and adds a
revision to the history.

## Verification
Wait for `READY` on `prod`, then confirm requests from the second region serve revision
12. If the 404 persists after the deployment reports `READY`, it is a different fault and
needs its own investigation, which is the point at which to start looking beyond
deployment state.

## Common Incorrect Answers
Redeploying to force propagation.

Claiming deployments are regional by design. Nothing in the evidence supports a regional
deployment model, and that framing would mislead the team about their topology.

Diagnosing the 404 as an environment group or routing problem while `prod` is still
propagating. It fits the symptom and not the evidence.

Claiming propagation explains the 404 as well as the stale behavior. The deployment model is
zero-downtime, so a Message Processor mid-propagation is still serving the previous revision.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says deployments are regional | Identifies propagation | Separates save, state, and routing |
| Diagnostic method | Redeploys | Checks traffic | Checks deployment state per environment |
| Handling of competing causes | Invents a routing or environment-group cause while `prod` is propagating | Notes both symptoms | Ties the stale behavior to propagation and says the 404 is not covered by the documented deployment model, naming what to check next |
| Safety | Redeploys | Waits | Waits without redeploying and says when to look further |
| Verification | None | Retests | Waits for `READY`, retests, and sets a condition for escalating |

## References
- Deploy an API proxy revision:
  <https://cloud.google.com/apigee/docs/api-platform/deploy/ui-deploy-overview>

## Critical failures
asserting a regional deployment model without evidence; declaring the 404 solved by propagation without saying that the documented deployment model does not cover
it.
