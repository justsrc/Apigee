# EASY-03 answer key, do not show to the agent

## Ground-Truth Resolution
The shared flow exists but is not deployed to the environment the proxy is running in.
The documented cause covers exactly these two cases and the agent cannot tell them apart
from the fault code alone. Checking deployment state is what separates them.

A useful detail: the code says nothing about the shared flow being missing from the
bundle, it says it was not found, which in practice means not deployed to this
environment.

## Correct Remediation
Deploy the shared flow to the environment first, then deploy or re-deploy the proxy that
references it. Order matters.

This is a control-plane change. It is reversible by undeploying, and it affects one
environment.

## Verification
Deploy the shared flow, confirm it appears in the environment's deployment list, then
send a test request and confirm a 200. Then deliberately check a second environment that
still lacks the shared flow deployment, to confirm you fixed the specific environment
rather than something incidental.

## Common Incorrect Answers
Rewriting the FlowCallout XML. The reference is correct.

Adding `apigee:sharedFlow` metadata to the proxy. Metadata does not deploy the shared
flow.

Concluding the shared flow name is wrong. It matches, which the successful bundle import
already demonstrates.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says the flow is missing | Acknowledges two causes | Identifies not-deployed and names the check |
| Diagnostic method | Reads code only | Checks bundle | Checks deployment state separately |
| Evidence and citation | None | Generic docs | Cites the FlowCallout error reference |
| Quality of next step | "Deploy it" | Names the action | Names the order and the environment |
| Verification | None | Sends a request | Confirms deployment then tests |

**Critical failures:** recommending a bundle change when the bundle is correct; claiming
the code proves the shared flow is absent.

## References
- FlowCallout policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/flow-callout-policy>

## Critical failures
recommending a bundle change when the bundle is correct; claiming the code proves the shared flow is absent.
