# MED-16 answer key, do not show to the agent

## Ground-Truth Resolution
Nothing is wrong with the client and nothing is wrong with the OAuth policy. The token request
is being served by the authorization-code flow because of how the proxy was deployed. Every
fix proposed against the error text, adding `response_type`, adding `client_id`, "fixing"
`redirect_uri`, makes the error text change without making the flow work.

This is also why the authorize leg still works. The proxy is partly correct, which is exactly
the shape of evidence that sends an agent looking at client parameters instead of at routing.

## Correct Remediation
Undeploy the proxy and redeploy it so the deployment base path matches the proxy base path in
the bundle, then confirm each flow's `<Condition>` is distinct. Deployment base path and proxy
base path are separate settings; the deployment base path cannot be set from the UI and
defaults to `/` when unset.

Treat this as a deployment-record change, not a bundle change. Do not modify the sample
policies to satisfy the error messages.

## Verification
Call the token endpoint with a fresh authorization code and confirm an access token is
returned. Then call the authorize endpoint and confirm it returns a code. Confirm both,
because a fix that makes one work can leave the other broken.

## Common Incorrect Answers
Adding `response_type=code` to the token request. That parameter belongs to the authorize
request and this is the most commonly repeated wrong answer in this area.

Telling the client to fix its `redirect_uri`. The registered callback URL is correct.

Rewriting the OAuth policy to generate the error manually. That hides the routing defect.

Treating the error text as a documented list of required parameters. The reference collapses
all of these into `steps.oauth.v2.InvalidRequest`.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Adds response_type | Suspects routing | Identifies wrong-flow dispatch from deployment base path |
| Diagnostic method | Edits client request | Reads error text | Reads error text as a routing signal and checks flow conditions |
| Handling of competing causes | Accepts the literal error | Hedges | Separates client, policy, and routing explicitly |
| Quality of next step | Changes parameters | Redeploys blindly | Redeploys with the base path matched, then verifies both flows |

## References
- OAuthV2 policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>
- Real report of this failure:
  <https://github.com/apigee/api-platform-samples/issues/7>

## Critical failures
recommending adding `response_type` or `client_id` to the token request; asserting the OAuth policy is misconfigured.
