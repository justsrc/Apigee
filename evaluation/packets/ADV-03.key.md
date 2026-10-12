# ADV-03 answer key, do not show to the agent

## Ground-Truth Resolution
Hybrid. The Message Processor terminology persists in hybrid documentation, which is
exactly what makes this trap work: the hybrid overview has a Message Processor section
and describes Message Processors running on the runtime plane. A ticket can use OPDK
vocabulary while describing a hybrid install.

Log access is through Kubernetes. The hybrid runtime-logs page documents `kubectl logs`
against `apigee-runtime` pods and does not document `/opt/apigee/var/log` paths at all.
Those paths are OPDK, which is the wrong architecture here.

## Correct Remediation
Use Kubernetes to inspect the runtime pod logs. Confirm the workload namespace and name
before assuming any of them.

## Verification
Confirm the crash is gone and the pod is running. Then confirm the signing key rotation
completed, since a repeated crash after a rotation suggests the key was never applied.

## Common Incorrect Answers
Giving `/opt/apigee/var/log/edge-message-processor/logs/system.log` paths. Wrong
architecture.

Assuming OPDK because of the Message Processor wording.

Not asking, and going with the stronger signal.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Product and version | OPDK assumed | Uncertain | Identifies hybrid from mixed evidence |
| Diagnostic method | Gives OPDK paths | Asks late | Asks and uses Kubernetes log access |
| Handling of competing causes | Ignores conflict | Notes it | Explicitly resolves contradictory signals |

**Critical failures:** giving OPDK filesystem paths for a hybrid install.

## References
- What is Apigee hybrid:
  <https://cloud.google.com/apigee/docs/hybrid/latest/what-is-hybrid>
- Hybrid runtime logs:
  <https://cloud.google.com/apigee/docs/hybrid/latest/runtime-logs>

## Critical failures
 giving OPDK filesystem paths for a hybrid install.
