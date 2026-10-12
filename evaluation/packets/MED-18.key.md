# MED-18 answer key, do not show to the agent

## Ground-Truth Resolution
No data is lost. The documented cause is a credential casting regression in MART, affecting
environments that use Workload Identity Federation together with an HTTP forward proxy. Both
conditions are required. The register scopes the issue to EKS. The fix is to move the operator
and MART images to `1.16.0-hotfix.1`.

The trap is the conjunction. An agent that checks only "are you using WIF?" or only "do you have a
forward proxy?" will correctly observe one is absent and wrongly close the case. The same applies
to the platform check: an agent that verifies GKE and stops there will also wrongly close it.

## Correct Remediation
Apply the documented hotfix by setting the operator and MART image properties in
`overrides.yaml`:

```yaml
ao:
  image:
    url: "gcr.io/apigee-release/hybrid/apigee-operators"
    tag: "1.16.0-hotfix.1"
mart:
  image:
    url: "gcr.io/apigee-release/hybrid/apigee-mart-server"
    tag: "1.16.0-hotfix.1"
```

Then check the neighbouring 1.16.0 defect, fixed in the same hotfix: on AKS and EKS with
Federated Workload Identity, the Kubernetes ServiceAccount `apigee-operator-guardrails-sa` is not
created, because the chart template's initial `if` condition omits
`.Values.gcp.federatedWorkloadIdentity.enabled`.

## Verification
Confirm API Products, apps and developers load. Then confirm proxy deployment still works, because
the fix changes the operator image, not just MART.

## Common Incorrect Answers
Telling the customer their data is lost, or that they must re-import. Both are wrong and alarming.

Re-importing org entities. They are in Cassandra; the import is not the problem and a re-import
risks real damage.

Checking only Workload Identity Federation, or only the forward proxy. Either alone rules the issue
out incorrectly.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Product and version | Gives Apigee X advice | Identifies hybrid | Names the 1.16.0 MART defect and its fixed version |
| Technical correctness | Says data lost | Suspects MART | Names the credential casting regression |
| Diagnostic method | Re-imports | Checks MART | Checks MART version, both gating features, and the platform |
| Handling of uncertainty | Asserts | Hedges | States the conjunction and platform scope explicitly |

## References
- Known issues register (entry 479872706 and 479040521):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- MART and runtime service configuration:
  <https://cloud.google.com/apigee/docs/hybrid/v1.17/service-config>

## Critical failures
telling a customer their data is lost; ruling the issue out by checking only one of the two gating features.
