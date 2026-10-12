# MED-19 answer key, do not show to the agent

## Ground-Truth Resolution
The runtime is fine. Earlier releases ignored component-level node selectors, so the logger was
scheduled onto the Apigee node pools despite the default selector matching nothing. The affected
release honours component-level node selectors correctly, so the long-standing default now takes
effect and the DaemonSet matches no nodes.

The counter-intuitive step is accepting that a bug fix caused this. "The upgrade made it worse" is
the correct reading here, not a contradiction.

## Correct Remediation
Either clear the default selector in `overrides.yaml`:

```yaml
logger:
  enabled: true
  nodeSelector:
    key: ""
    value: ""
```

or label the intended nodes and keep the default:

```terminal
kubectl label nodes NODE_NAME apigee.cloud.google.com/apigee-logger-enabled=true
```

Then upgrade the `apigee-telemetry` chart. The defect is fixed in hybrid 1.16.9.

## Verification
Confirm logger pods exist and the desired count matches the labelled node count. Then confirm log
lines appear in Logs Explorer for the `Kubernetes Container` resource type.

## Common Incorrect Answers
Escalating as a runtime outage. Traffic is unaffected and the runtime is healthy.

Deleting and recreating the `apigee-logger` DaemonSet. The default node selector returns and the
DaemonSet matches no nodes again.

Checking only whether `logger.enabled` is set. The flag being true is the precondition, not the
cause. Also note the platform dependency: logging is on by default on GKE and GKE on-prem, and off
by default on AKS.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Calls it a runtime outage | Suspects the logger | Identifies the node selector as the cause |
| Diagnostic method | Escalates | Inspects pods | Runs kubectl get daemonset first |
| Product and version | Generic | Names hybrid | Names the affected hybrid versions and the fix version |
| Quality of next step | Restarts pods | Deletes the DaemonSet | Clears the selector or labels nodes |

## References
- Known issues register (entry 543171828):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Logging in hybrid:
  <https://cloud.google.com/apigee/docs/hybrid/v1.17/logging>
- View logs:
  <https://cloud.google.com/apigee/docs/hybrid/v1.17/logging-view>

## Critical failures
escalating as a runtime outage; recreating the DaemonSet; recommending a runtime restart, which does not address scheduling.
