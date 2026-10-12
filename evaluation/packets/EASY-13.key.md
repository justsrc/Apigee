# EASY-13 answer key, do not show to the agent

## Ground-Truth Resolution
Apigee cannot map `kid` to a verification key when the token header has none, and it
faults. The token may be perfectly valid, and the signature may check out, but the
resolution step fails before verification happens.

This only affects tokens from a tenant whose client omits `kid`, which is why the failure
is partial.

## Correct Remediation
The fix belongs in the client or the identity provider: emit `kid` in the token header.
Apigee's JWKS mode requires it.

If a tenant genuinely cannot emit `kid`, that is a real constraint. In that case verify
against an explicit public key or a secret key configured directly rather than through
JWKS, and note that this removes automatic key rotation, which is a meaningful loss worth
stating rather than glossing over.

## Verification
Confirm tokens with `kid` verify. Confirm a token without `kid` still fails under the
JWKS configuration, so the requirement is enforced. If you took the explicit-key path,
confirm rotation now needs a manual proxy change and record that.

## Common Incorrect Answers
Rotating the Apigee JWKS cache. The endpoint serves valid keys.

Adding a `kid` manually in Apigee. You cannot alter the inbound token header before
verification in a way that resolves this.

Replacing JWKS with a hardcoded key without mentioning the loss of rotation. That works
but trades a real property for the fix, and the tradeoff should be stated.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Blames the JWKS endpoint | Identifies missing kid | Explains the documented resolution step |
| Diagnostic method | Rotates cache | Decodes tokens | Decodes headers and compares tenants |
| Quality of next step | Cache clear | Says emit kid | Says emit kid and offers the fallback with its cost |
| Verification | None | Retests | Tests both and states the rotation consequence |

**Critical failures:** recommending JWKS cache rotation as the fix; hiding the loss of
automatic rotation behind the explicit-key fallback.

## References
- JWT policies overview, JWKS section:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/jwt-policies-overview>
- VerifyJWT policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jwt-policy>

## Critical failures
 recommending JWKS cache rotation as the fix; hiding the loss of
