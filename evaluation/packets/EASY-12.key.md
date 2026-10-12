# EASY-12 answer key, do not show to the agent

## Ground-Truth Resolution
The policy received a timestamp before January 1, 2014 and refused it with
`steps.oauth.v2.InvalidEarlyTimestamp`, HTTP 500.

A zero value, or a seconds value read as milliseconds, both land in 1970 by the policy's
own reading of its input, and the lower bound rejects them. This is not clock skew, and
nothing about the deployment or the runtime clock is involved.

Note the element is optional and defaults to the current time when absent. The fault
therefore comes from a value that was supplied and resolved badly, not from omitting the
element. A missing element on its own would not produce this code.

The sibling `steps.oauth.v2.InvalidFutureTimestamp` covers the other half of the bound,
and `steps.oauth.v2.InvalidTimestamp` covers a value that is not a valid timestamp at all.
All three are 500. The three should not be collapsed into "token expired".

## Correct Remediation
Make the caller send a millisecond timestamp, and reject the call at the edge when it
does not. A missing query parameter should produce a clear client-side error rather than
being passed through as `0`.

Check the other end of the bound while you are there. A client that passes a value in the
future, for example from a device with a badly wrong clock, hits
`InvalidFutureTimestamp` instead, and both failures deserve a guard.

## Verification
Replay the failing request with a valid millisecond timestamp and confirm it succeeds.
Then confirm a request with `revoke_since_timestamp=0` still fails, which proves the
validation is present rather than absent. Then confirm the future-dated case fails with
the other code.

## Common Incorrect Answers
Treating this as clock skew and telling the team to sync clocks or widen `nbf` leeway.
There is no `nbf` involved; this policy does not set flow variables at all.

Saying the endpoint returns 401 because it is an OAuth endpoint. The documented status
for this code is 500.

Raising token lifetime. Lifetime is `exp` on the access token, a different concept from
the timestamp this policy filters on.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says clock skew or token invalid | Names the lower bound | Names the 2014-01-01 bound, 500, and the RevokeOAuthV2 page |
| Evidence and citation | None | Generic OAuth docs | Cites the RevokeOAuthV2 policy error reference |
| Diagnostic method | Blames clocks | Asks for the value | Asks for the value and checks the parameter is absent |
| Handling of uncertainty | Asserts a cause | Hedges | Separates the confirmed cause from the seconds-vs-millis variant |
| Verification | None | Retests once | Tests valid, zero, and future-dated values |

**Critical failures:** attributing the fault to clock skew or to `nbf`; quoting a 401
status for this code.

## References
- RevokeOAuthV2 policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/revoke-oauth-v2-policy>

## Critical failures
attributing the fault to clock skew or to `nbf`; quoting a 401 status for this code.
