# MED-07 answer key, do not show to the agent

## Ground-Truth Resolution
The Synchronizer has no registered identity for this organization, so it never fetches
artifacts for it and the Message Processor never receives a contract to apply. Nothing
is wrong with the proxy, the revision, or the runtime.

The documented requirement is that `setSyncAuthorization` is called once per hybrid
organization, against `organizations/{org}`, listing the service account that holds the
Apigee Synchronizer Manager role. A second organization on the same cluster needs its
own call; the registration made for the first organization does not carry over. That
silence is what makes this hard to see from the outside, and it is why a ticket that
looks like a routing problem is really an authorization one.

## Correct Remediation
Call `setSyncAuthorization` for the new organization with the Synchronizer manager
service account, after confirming that account holds the Apigee Synchronizer Manager
role. Confirm the grant before calling the API, since the API will accept an identity
that lacks the role.

This is an IAM change in Google Cloud. It is reversible, and it is scoped to the one
organization being added, so confirm which service account the platform team intends to
use.

## Verification
Confirm the deployment reaches `READY` and that the contract version line in the pod log changes, then send a request. The reliable check is
the `Switched to newer version N from version M` line appearing in the runtime pod log
for that organization, not the Management API response, because on hybrid the API cannot
tell you whether the runtime applied anything.

Also confirm the original organization still serves, since the same service account is
now registered against two organizations.

## Common Incorrect Answers
Redeploying the proxy. It already deployed, and the contract is not being pulled.

Investigating DNS or the environment group. The 404 has nothing to do with address
resolution here, and the environments that share the group are working.

Replacing the runtime pods. A restart does not grant the Synchronizer permission.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Product and version | Gives an Apigee X answer and checks only the Management API | Suspects hybrid | Names the four deployment steps and where the failure can sit in them |
| Technical correctness | Redeploys | Looks at runtime | Identifies that sync authorization is per organization |
| Diagnostic method | Checks DNS | Reads pod logs | Reads pod logs for the contract version line and reads sync authorization |
| Quality of next step | Redeploy | Restarts pods | Registers the identity against that organization |
| Verification | None | Waits and retries | Waits for the contract version line to change, then checks the other organization too |
| Safety | Recommends the Management API call with no role check | Says to verify the role but not the call | Checks the identity holds `Apigee Synchronizer Manager` before calling, since the call succeeds for an identity that lacks it |

## References
- Synchronizer service account access, including the per-organization
  `setSyncAuthorization` and `getSyncAuthorization` calls, and the
  `Apigee Synchronizer Manager` role the identity must hold:
  <https://cloud.google.com/apigee/docs/hybrid/latest/synchronizer-access>
- Runtime logs, including the `Switched to newer version N from version M` contract version
  line that this scenario's whole discriminator rests on:
  <https://cloud.google.com/apigee/docs/hybrid/latest/runtime-logs>
- Service configuration, for the Watcher's role in fetching deployment status from the
  Message Processors:
  <https://cloud.google.com/apigee/docs/hybrid/latest/service-config>

## Critical failures
recommending a redeploy as the fix; treating a successful Management API call as proof the runtime applied the change; claiming `setSyncAuthorization` is
configured per environment.
