# MED-17 answer key, do not show to the agent

## Ground-Truth Resolution
The deployment succeeded. The plugin waits a fixed interval, then makes a follow-up call to read
deployment state, and treats a not-yet-set deployed revision as a failure. The two delays are
different things: in the source thread the reporter asserted that making the 10 second wait
configurable was the fix, and the maintainer's position was the opposite, that the hardcoded
sleep "is just used to get the deployment details and see if the deployment is completed" and
that `apigee.override.delay` applies to the deployment call, not to the activation check. The
maintainer in fact asked the reporter to lower the delay from 30 to 10 and to find out why
deployments were taking that long at all.

The honest answer stops there. It is not established why the deployments take 30 seconds. The
maintainer's own hypothesis was environmental slowness, and the thread was closed for
inactivity without a fix.

## Correct Remediation
Change the tooling so the activation check polls deployment state instead of sampling it once,
or work around the fixed interval. Both are tooling changes and belong to the customer's CI,
not to Apigee.

Establish the real deployment time in this environment before changing anything, since that
number is the actual unknown.

## Verification
Deploy a proxy and a shared flow, and confirm both revisions are serving. Then confirm the build
passes on the deployments that previously passed, so the change has not narrowed what deploys.

## Common Incorrect Answers
Increasing `apigee.override.delay` to 60 and declaring victory. The delay is not what the check
reads. In the source thread the reporter raised exactly this and was told it would not help.

Blaming the Management API or raising a platform defect. The deployment is verifiably fine.

Treating "the tool said failed" as proof the proxy is not deployed. Check the deployment directly.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Attributes to the delay | Identifies tool-side check | Separates acceptance, revision, and serving |
| Diagnostic method | Raises the delay | Reads the log | Runs the same deploy via the Management API |
| Handling of uncertainty | Asserts a cause | Hedges | States that the 30-second deployment time is unexplained |
| Quality of next step | Increases delay | Retries | Changes the check to poll deployment state |

## References
- Real report, with the disputed diagnosis and the closure for inactivity:
  <https://github.com/apigee/apigee-deploy-maven-plugin/issues/213>
- Deploy an API proxy revision:
  <https://cloud.google.com/apigee/docs/api-platform/deploy/ui-deploy-overview>

## Critical failures
asserting the delay setting is the root cause; opening a platform defect against Apigee for a tool-generated message.
