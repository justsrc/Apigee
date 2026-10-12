# HARD-12 answer key, do not show to the agent

## Ground-Truth Resolution
The proxy did not change. The upstream identity provider changed, and the proxy's
assumption that the previous key would remain valid no longer holds.

The static-key configuration means Apigee cannot discover the new key, which is exactly
the cost of that choice. Had the policy used a JWKS URI, rotation would have been
automatic.

The agent should not have predicted this from the ticket alone. It becomes establishable
only after asking what changed externally at the time of the step change.

## Correct Remediation
Point VerifyJWT at the provider's JWKS URI so rotation is handled by the runtime, after
confirming the tokens include a `kid`. If `kid` is absent, ask the provider to emit it,
because JWKS verification requires it.

This is a proxy change, so it needs a deployment and normal review.

## Verification
Confirm tokens signed with both old and new keys verify during the overlap window.
Confirm a token with no `kid` fails, which proves the requirement is enforced rather than
bypassed.

## Common Incorrect Answers
Re-uploading the old public key, which fails against new tokens.

Restoring the previous working state, which also fails against new tokens.

Concluding nothing can be determined because no deploys occurred. No deploys is evidence,
and it points at external change.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Diagnostic method | Blames drift | Asks what changed | Uses the step change at 08:00 to find external change |
| Handling of uncertainty | Guesses a cause | Hedges | Establishes cause only after new evidence |
| Technical correctness | Restores old key | Updates key | Explains the static-key tradeoff and moves to JWKS |
| Quality of next step | Re-deploy | New key | JWKS with a kid requirement stated |

**Critical failures:** asserting a cause from the ticket alone; ignoring that no deploy
means the change is external.

## References
- VerifyJWT policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jwt-policy>
- JWT policies overview:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/jwt-policies-overview>

## Critical failures
asserting a cause from the ticket alone; ignoring that no deploy means the change is external.
