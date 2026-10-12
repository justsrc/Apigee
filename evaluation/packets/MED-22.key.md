# MED-22 answer key, do not show to the agent

## Ground-Truth Resolution
cert-manager 1.18 changed the default of `Certificate.Spec.PrivateKey.rotationPolicy` from `Never`
to `Always`. Fresh hybrid installs already set `Never`; upgraded clusters keep whatever the older
cert-manager default was, so the new default takes effect on them only. The register is explicit
that this "only applies to upgraded Apigee hybrid clusters".

From this point the cluster will rotate the `apigee-ca` private key on cert-manager's schedule. The
documented consequence is blunt: "When this key is rotated for the `apigee-ca` certificate, it will
cause an outage."

Two things follow, and the second is the one that matters. First, the clusters differ despite
sharing a hybrid version, because fresh and upgraded installations differ. Second, the current
intermittent connection failures are not themselves explained by this register entry, which
describes a rotation-triggered outage rather than a present fault. The agent should say so rather
than claim the entry accounts for the symptom, and treat the entry as the reason to act now rather
than as the diagnosis of what is already happening.

## Correct Remediation
Patch the certificate to `Never` before rotating anything further, then verify:

```terminal
kubectl patch Certificate \
  -n cert-manager \
  --type=json \
  -p='[{"op": "replace", "path": "/spec/privateKey/rotationPolicy", "value": "Never"}]' \
  apigee-ca
```

Alternative, per the documentation: do not upgrade cert-manager above 1.17.x.

The order matters and the documentation warns about it: perform these steps before upgrading
cert-manager, otherwise a rotation may already be triggered.

## Verification
Confirm `rotationPolicy: Never` on `apigee-ca` with
`kubectl get certificate apigee-ca -n cert-manager -o yaml`. Then confirm the runtime components
are healthy. Separately, verify Cassandra backup and restore across the clusters, because
Cassandra backup and restore cannot work with mixed hybrid versions.

## Common Incorrect Answers
Restarting the affected pods to clear the connection failures. It masks the symptom until the next
rotation and destroys the evidence.

Comparing the two clusters only by hybrid version. The documented defect separates upgraded
clusters from fresh installs at the same version, so version alone cannot discriminate.

Rebuilding the `apigee-ca` certificate from scratch. That forces a rotation immediately, which is
the outcome being avoided.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Restarts pods | Inspects certificates | Identifies the rotationPolicy default change |
| Diagnostic method | Compares hybrid versions only | Compares the two clusters | Inspects apigee-ca rotationPolicy on both |
| Product and version | Gives Apigee X advice | Identifies hybrid | Names cert-manager 1.18 default and the fresh-vs-upgraded split |
| Quality of next step | Restarts | Rebuilds the CA | Patches rotationPolicy to Never before any further change |

## References
- Known issues register (entry 465834046):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Upgrading Apigee hybrid (cert-manager section):
  <https://cloud.google.com/apigee/docs/hybrid/v1.17/upgrade>
- Supported platforms and versions:
  <https://cloud.google.com/apigee/docs/hybrid/supported-platforms>

## Critical failures
recommending a CA rebuild or an immediate rotation; treating identical hybrid versions as proof that both clusters behave the same way.
