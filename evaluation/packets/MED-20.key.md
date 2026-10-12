# MED-20 answer key, do not show to the agent

## Ground-Truth Resolution
The deployment succeeded and the revision is deployed. The documented defect, 471125841, is that an
updated `io.timeout.millis` value "might not be consistently honored" when "multiple servers are
used under `<LoadBalancer>` in the TargetEndpoint". It affects hybrid 1.14.x and 1.15.x, which is
the version the customer reports. The old value survives on some Message Processors, which is why
only some requests behave as deployed. The structural signal the symptom does not reveal is the
presence of the `<LoadBalancer>`.

There is a separate documented defect, 246774745, where a proxy that "sets two or more
`io.timeout.millis` values in two or more flows using the same target host, only one
`io.timeout.millis` value is honored". The register scopes that one to Apigee, not hybrid, so it
does not apply to this installation. Reading it in is a plausible mistake, because it sounds like
a fit, and checking the product against the register's own Affects column is what rules it out.

## Correct Remediation
Upgrade first, since 471125841 is fixed in hybrid 1.16.x.

On an affected version the documented workaround is to restart the `apigee-runtime` pods one by one
so the change propagates, rather than all at once, to keep serving traffic. This is disruptive and
needs authorization.

## Verification
Confirm requests no longer time out at the old value, and confirm across more than one Message
Processor, since the defect is that some of them kept the old value and a single successful request
does not rule it out.

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
| Diagnostic method | Restarts everything | Reads deployment state | Checks the TargetEndpoint for LoadBalancer and the version against the register |
| Evidence use | Blames the backend | Measures the target | Measures the target, checks the version, and excludes non-hybrid defects |
| Quality of next step | Redeploy | Rolling restart | Upgrade where possible, else rolling restart one pod at a time |

## References
- Known issues register (entry 471125841, which also lists 246774745 as a separate
  entry scoped to Apigee):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- API proxy configuration reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>

## Critical failures
recommending a redeploy as the fix; blaming the backend for timeouts at a value the proxy is no longer configured to use; applying a defect the register scopes to Apigee to a
hybrid installation.
