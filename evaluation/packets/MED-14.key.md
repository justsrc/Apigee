# MED-14 answer key, do not show to the agent

## Ground-Truth Resolution
Revocation works. OAuth tokens are cached for three minutes, so a revoked token can still
succeed until its cache entry expires. The observed three-minute window is exactly the
documented behavior: the OAuthV2 reference states that a revoked token may still succeed
for up to three minutes until its cache limit expires.

There is a real operational consequence, which the agent should raise rather than dismiss:
if an account must be locked out immediately, revocation alone is not sufficient, and the
security team needs to know that.

## Correct Remediation
The documented lever for a shorter window is `<CacheExpiryInSeconds>` on the OAuthV2
policy, which lowers the access token cache TTL and is described specifically for the
case where you revoke tokens and want to reduce the window during which Apigee treats
revoked tokens as valid. Its supported range is 1 to 180 seconds. Lower it, redeploy the
proxy, and note that the reduction applies from the next cache expiry onward, so it does
not shorten the window for a token already cached under the old TTL.

If the security team needs the credential rejected before that, revoking at the identity
provider as well is the only path to immediate rejection, and whether one exists depends
on their flow. The agent should ask rather than assume.

Document the resulting window so the security team knows what response time Apigee
offers and does not offer.

## Verification
Revoke a test token, record the time, and poll until it fails. Repeat to confirm the
window matches the configured `<CacheExpiryInSeconds>` rather than occasionally running
longer. Then confirm tokens issued under the old TTL no longer survive longer than the
new value.

## Common Incorrect Answers
Declaring revocation broken and escalating as a defect.

Advising the security team to ignore it. A three-minute window is acceptable for some
flows and unacceptable for a credential compromise, and the answer depends on which.

Suggesting clearing the runtime cache manually. There is no documented supported way to
force-flush token caches across runtimes.

Offering only identity provider revocation and never mentioning that Apigee's own cache
TTL is configurable. It is, it is the lever the documentation points at for this exact
situation, and an answer that omits it cannot be verified by the steps below.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Calls it a defect | Identifies caching | Names the window, its bound, and the configurable TTL |
| Handling of competing causes | Escalates | Hedges | Explains and addresses the security need separately |
| Quality of next step | Cache flush | Document window | Lowers `<CacheExpiryInSeconds>` and asks whether an upstream IdP is in path |
| Verification | None | Waits | Measures the window repeatedly and confirms it matches the configured TTL |

## References
- OAuthV2 policy, InvalidateToken:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>

## Critical failures
advising a security team to accept the window for a credential compromise without raising the alternative; asserting the three-minute window is fixed
and cannot be shortened.
