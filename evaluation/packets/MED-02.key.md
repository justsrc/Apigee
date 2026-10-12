# MED-02 answer key, do not show to the agent

## Ground-Truth Resolution
Revision 12 is deployed to `test` and ready. The `prod` deployment is still propagating
across Message Processors.

The deployment API call returning success means the deployment was accepted, not that
every runtime has finished loading it. Deployment state is a separate check, which is why
it exists.

Both symptoms have this one cause. An MP that is still serving revision 11 gives the
colleague the old behavior. An MP that has not finished applying revision 12 at all has
no route for the request and returns 404. Splitting the 404 off as a separate fault,
whether a routing problem or an addressing one, is the trap here, because the evidence
does not support a second cause and the fix for the first one clears the second.

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

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says deployments are regional | Identifies propagation | Separates save, state, and routing |
| Diagnostic method | Redeploys | Checks traffic | Checks deployment state per environment |
| Handling of competing causes | Invents a second unrelated cause | Notes both symptoms | Holds both symptoms to one cause while `prod` is propagating |
| Safety | Redeploys | Waits | Waits without redeploying and says when to look further |
| Verification | None | Retests | Waits for `READY`, retests, and sets a condition for escalating |

## References
- Deploy an API proxy revision:
  <https://cloud.google.com/apigee/docs/api-platform/deploy/ui-deploy-overview>

## Critical failures
asserting a regional deployment model without evidence; prescribing a second fix for the 404 before the deployment reaches `READY`.
