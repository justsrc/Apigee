# MED-08 answer key, do not show to the agent

## Ground-Truth Resolution
Mutual TLS requires the `clientAuth` extended key usage on the client certificate. Without
it, mTLS fails in both directions, client to Apigee and Apigee to backend, because the
same class of certificate is used on both sides.

Nothing about the Apigee configuration changed. The renewal dropped a property that the
old certificate happened to carry.

## Correct Remediation
Have the CA reissue client certificates including the `clientAuth` extended key usage.
This is a certificate request change on the customer's side, not an Apigee change.

Keep the old certificates until the new ones are confirmed working in both directions,
since the two-sided failure means a partial test proves nothing.

## Verification
Confirm the EKU on the new certificate before deploying it anywhere. Then test northbound
and southbound independently, because a northbound pass does not imply a southbound pass.

## Common Incorrect Answers
Re-uploading the certificate to the keystore. It is already correct, and the defect is in
the certificate's contents.

Setting `IgnoreValidationErrors`. That does not address extended key usage.

Checking the truststore for the CA. Trusting the CA is necessary and already satisfied;
the client certificate is the problem.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Re-uploads certificate | Identifies certificate issue | Names `clientAuth` EKU as the cause |
| Diagnostic method | Checks truststore | Inspects certificate | Inspects the EKU extension specifically |
| Handling of uncertainty | Assumes chain problem | Hedges | States what is confirmed and what to check |
| Verification | None | Tests one side | Tests both directions separately |

## References
- API proxy configuration reference, TLS section:
  <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>
- Configuring TLS:
  <https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls>

## Critical failures
recommending `IgnoreValidationErrors` as the fix. #### References
- API proxy configuration reference, TLS section:
  <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>
- Configuring TLS:
  <https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls>
---
