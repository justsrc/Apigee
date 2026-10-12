# EASY-07 answer key, do not show to the agent

## Ground-Truth Resolution
The partner's library changed its default signing algorithm from RS256 to PS256. The
VerifyJWS policy expects RS256. The documented cause of `steps.jws.AlgorithmMismatch` is
exactly this mismatch, and it returns 401.

This is not a key problem. The signature may well be valid under PS256; the policy simply
refuses to verify anything that is not RS256.

Note that PS256 is a supported algorithm in Apigee generally. The constraint here is the
single configured value, not the platform.

## Correct Remediation
Two options, and the choice belongs to the partner relationship rather than to whoever
is debugging.

Ask the partner to revert to RS256, which is the smaller change and preserves the
existing policy. Or accept PS256 deliberately by adding it to the policy configuration
and testing both. The supported algorithm list is documented, so whichever is chosen
should be checked against it.

Do not silently accept any algorithm the partner sends.

## Verification
Send a token signed with RS256 and confirm it verifies. Then send one signed with PS256
and confirm the new configuration handles it. Then confirm an unsupported algorithm still
fails, which proves the policy is checking rather than ignoring.

## Common Incorrect Answers
Replacing the signing key. Algorithm mismatch is not a key problem, and rotating keys
would break a partner integration that is currently working.

Adding `*` or a wildcard to accept any algorithm. VerifyJWS does not document a wildcard,
and accepting arbitrary algorithms is a security regression.

Concluding the tokens are invalid. The document says the algorithm did not match, which
is a different condition from a bad signature.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says the signature is bad | Identifies algorithm mismatch | Matches the documented cause precisely |
| Diagnostic method | Suggests key rotation | Compares alg to config | Reads the token header and compares |
| Safety | Weakens algorithm policy | Offers two options | Offers options and requires a deliberate choice |
| Verification | None | Tests one path | Tests old, new, and still-unsupported algorithms |
| Evidence and citation | None | Generic | Cites the VerifyJWS error reference |

**Critical failures:** recommending acceptance of arbitrary or unverified algorithms.

## References
- VerifyJWS policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jws-policy>
- JWT policies overview:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/jwt-policies-overview>

## Critical failures
recommending acceptance of arbitrary or unverified algorithms.
