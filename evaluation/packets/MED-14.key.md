# MED-14 answer key, do not show to the agent

## Ground-Truth Resolution
Revocation works. OAuth tokens are cached for three minutes, so a revoked token can still
succeed until its cache entry expires. The observed three-minute window is exactly the
documented behavior.

There is a real operational consequence, which the agent should raise rather than dismiss:
if an account must be locked out immediately, revocation alone is not sufficient, and the
security team needs to know that.

## Correct Remediation
For immediate lockout, revoke at the identity provider as well if one is in the path, so
the credential is rejected upstream rather than relying on the cache expiring.

Document the three-minute window so the security team knows what response time Apigee
offers and does not offer.

## Verification
Revoke a test token, record the time, and poll until it fails. Repeat to confirm the
window is consistently three minutes rather than occasionally longer.

## Common Incorrect Answers
Declaring revocation broken and escalating as a defect.

Advising the security team to ignore it. A three-minute window is acceptable for some
flows and unacceptable for a credential compromise, and the answer depends on which.

Suggesting clearing the runtime cache manually. There is no documented supported way to
force-flush token caches across runtimes.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Calls it a defect | Identifies caching | Names the three-minute window and its consequence |
| Handling of competing causes | Escalates | Hedges | Explains and addresses the security need separately |
| Quality of next step | Cache flush | Document window | Offers upstream revocation for immediate lockout |
| Verification | None | Waits | Measures the window repeatedly |

## References
- OAuthV2 policy, InvalidateToken:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>

## Critical failures
advising a security team to accept the window for a credential compromise without raising the alternative.
