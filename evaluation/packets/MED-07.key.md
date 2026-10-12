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
Confirm the deployment reaches a served state, then send a request. The reliable check is
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
| Product and version | Applies X reasoning | Suspects hybrid | Treats deployment as four separate steps |
| Technical correctness | Redeploys | Looks at runtime | Identifies that sync authorization is per organization |
| Diagnostic method | Checks DNS | Reads pod logs | Reads pod logs for the contract version line and reads sync authorization |
| Quality of next step | Redeploy | Restarts pods | Registers the identity against that organization |
| Verification | None | Sends a request | Uses the pod log marker and checks the other organization |

## References
- What is Apigee hybrid:
  <https://cloud.google.com/apigee/docs/hybrid/latest/what-is-hybrid>
- Synchronizer service account access, including the per-organization
  `setSyncAuthorization` and `getSyncAuthorization` calls:
  <https://cloud.google.com/apigee/docs/hybrid/latest/synchronizer-access>

## Critical failures
recommending a redeploy as the fix; treating a successful Management API call as proof the runtime applied the change; claiming `setSyncAuthorization` is
configured per environment.
