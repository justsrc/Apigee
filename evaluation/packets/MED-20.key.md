# MED-20 answer key, do not show to the agent

## Ground-Truth Resolution
The deployment succeeded and the revision is deployed. The documented defect, 471125841, is that an
updated `io.timeout.millis` value "might not be consistently honored" when "multiple servers are
used under `<LoadBalancer>` in the TargetEndpoint". It affects hybrid 1.14.x and 1.15.x. The old
value survives on some Message Processors, which is why only some requests behave as deployed.
The structural signal the symptom does not reveal is the presence of the `<LoadBalancer>`.

A second documented defect, 246774745, compounds it: when a proxy "sets two or more
`io.timeout.millis` values in two or more flows using the same target host, only one
`io.timeout.millis` value is honored".

## Correct Remediation
Upgrade first, since 471125841 is fixed in hybrid 1.16.x.

On an affected version the documented workaround is to restart the `apigee-runtime` pods one by one
so the change propagates, rather than all at once, to keep serving traffic. This is disruptive and
needs authorization.

Separately, if several flows set different timeouts against the same target host, consolidate them,
because the per-flow values will collapse to one regardless.

## Verification
Confirm requests no longer time out at the old value. Then exercise every flow that sets a timeout
for that target host, because the collapse to a single value will only show up there.

## Common Incorrect Answers
Redeploying. The revision is already deployed and the redeploy changes nothing.

Raising the timeout further, or blaming the backend. The backend responds in 4 seconds.

Rolling every runtime pod at once. That turns a partial problem into a full outage.

Reading the ticket as version-neutral. The defect is version scoped, so "we are on 1.16.x or later"
rules it out and changes the answer.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Redeploys | Suspects propagation | Identifies the LoadBalancer-conditioned timeout defect |
| Diagnostic method | Restarts everything | Reads deployment state | Checks TargetEndpoint for LoadBalancer and per-flow timeouts |
| Evidence use | Blames the backend | Measures the target | Measures the target and checks the version against the register |
| Quality of next step | Redeploy | Rolling restart | Upgrade where possible, else rolling restart, plus consolidating conflicting timeouts |

## References
- Known issues register (entries 471125841 and 246774745):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- API proxy configuration reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>

## Critical failures
recommending a redeploy as the fix; blaming the backend for timeouts at a value the proxy is no longer configured to use.
