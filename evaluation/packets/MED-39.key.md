# MED-39 answer key, do not show to the agent

## Ground-Truth Resolution
The ingress Service has no external IP, so nothing is listening on the address clients
resolve, and every client connection times out with no HTTP response. The absence of any
HTTP status is the diagnostic: an Apigee policy fault always produces a response, because
faults are turned into responses. A pure connect timeout means the request never reached
Apigee, which moves the investigation to the cluster rather than the proxy.

Both documented causes chain from the same object. Incomplete or erroneous Jobs in
`istio-system` block the Service from ever binding, and the install-time `Job "..." is
invalid` errors are the evidence of those Jobs. A misconfigured IP range in
`istio-operator.yaml` produces the same pending state without any Job error, so both checks
are needed.

## Correct Remediation
Confirm the Job status first and remove the failed Jobs so the Service can complete binding:

```terminal
kubectl get jobs -n istio-system
kubectl -n istio-system delete job <failed-job-name>
```

Then confirm the Service acquires an address:

```terminal
kubectl get services -n istio-system
```

If no Jobs are in an error state, the cause is the external load balancer configuration:
check the IP address range in `istio-operator.yaml` against the range provisioned for the
cluster and correct it, then reinstall or re-apply.

Because this is the ingress layer, the blast radius is the entire environment, not one
proxy. Deleting Jobs in `istio-system` affects every API proxy served by that ingress, so
it should be scheduled and the environment's consumers told, even though every consumer is
already failing.

## Verification
Confirm `EXTERNAL-IP` is populated rather than `<pending>`. Then call a known API proxy
through the external hostname from outside the cluster and confirm a response of any
status, including a 4xx, because the point is that a response arrives at all.

Then confirm the install itself completed cleanly, so the same Jobs do not fail again on
the next reconcile.

## Common Incorrect Answers
"Debug the target backend." The backend is not reached. Nothing Apigee-side, including any
policy, has run.

"Check DNS for example.apis.com." The record resolves; the address it resolves to has no
listener. The `curl: (7)` connect failure is consistent with either, which is exactly why
DNS alone cannot be ruled out from the client error string.

"Check the API proxy deployment and revision." No deployment state is involved. Nothing
reached the message processors.

"Restart the message processor pods." They are healthy and restarting them changes nothing,
because the failure is upstream of them.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Investigates the backend | Checks ingress networking | Identifies the pending ingress Service as the root cause |
| Diagnostic method | Tests client DNS | Reads the Service | Reads the Service and the istio-system Jobs as one causal chain |
| Handling of the error strings | Takes "Operation timed out" at face value | Notes no response arrives | Uses the absence of any HTTP response to exclude the policy layer entirely |
| Product knowledge | Treats it as an Apigee proxy fault | Moves to hybrid | Names Istio ingress, the `istio-system` namespace and both documented causes |
| Quality of next step | Retries the calls | Deletes Jobs | Checks Jobs, fixes the IP range if needed, schedules because blast radius is the whole environment |

## References
- Playbook, API calls fail with timeout errors, retrieved live this session and saved to
  `research/pages/api-platform_troubleshoot_playbooks_api-calls-fail-timeout-errors.txt`:
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/ingressgateway/api-calls-fail-timeout-errors>
- Playbook index, which lists the other runtime and ingress playbooks:
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/introduction>
- Note: guessed slugs under `.../playbooks/network/` return HTTP 200 with a generic title
  and no body. They are soft 404s. Real slugs live under `runtime/`, `ingressgateway/`,
  `deployment/` and `cassandra/`.

## Critical failures
restarting message processors; debugging the backend; asserting an Apigee policy is at fault when no HTTP response was ever produced.
