# MED-07 answer key, do not show to the agent

## Ground-Truth Resolution
The Synchronizer has no permission to pull artifacts for this environment, so it never
fetches the contract and the Message Processor never receives anything to apply. Nothing
is wrong with the proxy, the revision, or the runtime.

The documented requirement is that `setSyncAuthorization` is called with an identity
holding the Apigee Synchronizer Manager role. When it is skipped, nothing syncs and there
is no obvious error at any layer. That silence is what makes this hard to see from the
outside, and it is why a ticket that looks like a routing problem is really an
authorization one.

## Correct Remediation
Call `setSyncAuthorization` for the organization with the Synchronizer manager service
account, after granting that account the Apigee Synchronizer Manager role. Confirm the
grant before calling the API, since the API will accept an identity that lacks the role.

This is an IAM change in Google Cloud. It is reversible and it affects the whole
organization, so confirm the intended service account with whoever owns it.

## Verification
Confirm the deployment reaches a served state, then send a request. The reliable check is
the contract version line appearing in the runtime pod log, not the Management API
response, because on hybrid the API cannot tell you whether the runtime applied anything.

Also confirm the pre-existing environments still serve, since the change is
organization-wide.

## Common Incorrect Answers
Redeploying the proxy. It already deployed, and the contract is not being pulled.

Investigating DNS or the environment group. The 404 has nothing to do with address
resolution here, and the environments that share the group are working.

Replacing the runtime pods. A restart does not grant the Synchronizer permission.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Product and version | Applies X reasoning | Suspects hybrid | Treats deployment as four separate steps |
| Technical correctness | Redeploys | Looks at runtime | Identifies missing `setSyncAuthorization` and the role |
| Diagnostic method | Checks DNS | Reads pod logs | Reads pod logs for the contract version line and checks IAM |
| Quality of next step | Redeploy | Restarts pods | Grants the role then calls the API |
| Verification | None | Sends a request | Uses the pod log marker and checks other environments |

## References
- What is Apigee hybrid:
  <https://cloud.google.com/apigee/docs/hybrid/latest/what-is-hybrid>
- Compare Apigee products:
  <https://cloud.google.com/apigee/docs/api-platform/get-started/compare-apigee-products>

## Critical failures
recommending a redeploy as the fix; treating a successful Management API call as proof the runtime applied the change.
