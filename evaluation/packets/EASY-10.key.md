# EASY-10 answer key, do not show to the agent

## Ground-Truth Resolution
The HMAC policy is missing a required element. The HMAC error reference lists
`steps.hmac.MissingConfigurationElement` among its deployment errors, which the reference
states can occur when you deploy a proxy containing the policy, so the save call is what
fails and the new revision never deployed. The currently deployed revision predates the
change and still carries the secret, which is why traffic still works.

`<SecretKey>` is the element at fault. The reference documents it as Required, states that
there is no default value for the referenced variable, and that the `ref` attribute is
itself required.

The trigger is a broken template, not the secret value. An empty rendered value removes the
element entirely, which is different from an element holding a wrong value.

That distinction is worth making explicitly: missing element, wrong value, and unresolved
variable are three different failures with three different codes.

`<VerificationValue>` is a separate and quieter problem. It is documented as Optional, and
including it is what directs the policy to check the computed signature against a known
value rather than only calculate it. Its absence produces no deployment error at all,
which is exactly why a policy named `VerifySignature` deserves a second look before anyone
concludes it verifies.

## Correct Remediation
Fix the template so the `<SecretKey>` element renders, then confirm the element is present
in the bundle before deploying.

```xml
<HMAC name="VerifySignature">
  <Algorithm>SHA256</Algorithm>
  <SecretKey encoding="base64" ref="private.webhook.secret"/>
</HMAC>
```

Do not commit the secret itself. The reference documents `steps.hmac.InvalidSecretInConfig`
for a text value explicitly provided for `SecretKey`, and `steps.hmac.InvalidVariableName`
when the `SecretKey` variable lacks the `private.` prefix, so a reference is the safe shape
and an inline literal is not.

Deploy to a test environment first. This is a source change and is reversible, but a
broken HMAC policy silently rejects every webhook rather than failing loudly, so test
before production.

## Verification
Deploy to test, send a correctly signed webhook and confirm it verifies. Then send an
incorrectly signed one and confirm it is rejected. Both checks together prove the policy
is verifying rather than merely present, which is the failure mode an absent
`<VerificationValue>` would leave in place.

## Common Incorrect Answers
Rotating the secret. The error is about a missing element, not a value, and the secret is
not the thing the policy complained about.

Telling them the revision deployed. It did not, and the evidence is that traffic is still
being served by the old one.

Adding the secret inline in the proxy XML. That commits a credential to source control, and
the reference documents a specific error for a text value supplied to `SecretKey`.

Treating this as a runtime fault worth tracing. The reference lists it among the deployment
errors, so no request ever reaches it.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Treats as runtime | Identifies missing element | Names `<SecretKey>` and explains why traffic still works |
| Diagnostic method | Rotates secrets | Reads the policy | Reads the policy and checks the template |
| Safety | Commits the secret | Suggests adding a value | Fixes the template and uses a `private.` reference |
| Verification | None | Tests one path | Tests both accept and reject |
| Clarity | Buries the answer | Clear | Leads with the cause, the old revision, and the optional element |

**Critical failures:** recommending committing a secret to the proxy bundle; treating the
fault as a runtime error worth tracing; naming absent elements that do not exist in the
HMAC policy schema.

## References
- HMAC policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/hmac-policy>

## Critical failures
 recommending committing a secret to the proxy bundle; treating the
