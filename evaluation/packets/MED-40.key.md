# MED-40 answer key, do not show to the agent

## Ground-Truth Resolution
This is a documented limitation, not a broken deployment. Deploying proxies with the same path
to multiple environments attached to the same instance and environment group is not allowed, and
should return a warning about a base path conflict. It does not. Instead, no error is shown and
the deployments appear to succeed.

That wording is the whole lesson: the deploy genuinely succeeded, and the platform has recorded
an ambiguity it will later resolve by choosing one winner. The loser 404s. The 404 is correct
behaviour for an undefined routing situation, not a routing fault.

An agent that treats "deploy succeeded" as proof that the environment is consistent has adopted
the exact assumption the register warns against. Note also that this produces no fault code, so
there is nothing in any error-code index to grep for.

## Correct Remediation
Rename the base path on one of the two proxies so the two are distinct, and redeploy that one.
Renaming the path is a routing change that clients depend on, so it needs to be scheduled with
the owning team rather than applied as a reflex.

Going forward, verify after each deployment that no other proxy in the same environment group
claims the same base path. There is no platform warning to rely on, because there is no platform
warning.

## Verification
Send a request to each proxy host and confirm both resolve. Then confirm no other proxy in the
group shares either base path, since a third conflict is as invisible as the first.

## Common Incorrect Answers
Redeploying both proxies. Redeployment is not the defect and will reproduce the same state.

Recommending a redeploy as a "clean slate". There is nothing to clean; the conflict is in the
declared paths.

Looking for a routing or environment-group misconfiguration. The group is correctly configured
and both attachments are correct.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Redeploys | Identifies duplicate base paths | States it is an unreported base path conflict within one instance and environment group |
| Diagnostic method | Re-runs the deploys | Compares the two base paths | Confirms shared instance, shared group, and identical declared path |
| Handling of the green deploy | Trusts it | Doubts it | Explains why the absence of an error is the defect |
| Quality of next step | Restarts or redeploys | Asks the team to rename a path | Names the path change, the client impact, and the missing verification step |

## References
- Known issues register (entry 300660653):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Environment groups:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/environmentgroups-working-with>

## Critical failures
recommending a redeploy as the fix; treating a successful deployment as proof the environment is internally consistent.
Not a critical failure: not being able to say which proxy 404s. That is exactly the customer
problem, and the register gives no way to determine it.
