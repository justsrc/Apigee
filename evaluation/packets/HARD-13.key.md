# HARD-13 answer key, do not show to the agent

## Ground-Truth Resolution
The VerifyJWT policy is the cause, and the mechanism is clock skew between the minting
service and the Message Processors. A token that is 30 seconds from expiry on the issuer's
clock is already past expiry on the gateway, so it fails with `steps.jwt.TokenExpired` and
returns 401. This is why 20% of requests fail and why the failures look unrelated to any
particular client or endpoint: they fail at one narrow point in a token's life, and roughly
one token in five is minted into that point at any moment.

Quota is ruled out on two independent grounds: the caller-visible response to an exceeded
threshold is 429, and no `QuotaViolation` appears. The Quota policy error table does map
`policies.ratelimit.QuotaViolation` to a 500, but that is the status of the fault the policy
throws, which reaches a caller only if it propagates unhandled. Neither figure is a 401,
and an answer that spots this table entry and says so has strengthened the case rather than
weakened it. The backend is ruled out because failing requests never reach the target step.

Still open, and needing one measurement rather than a guess: the actual offset between the
Message Processors and the issuer. The correlation bounds it but does not measure it.

## Correct Remediation
Measure the clock offset on the Message Processors against the issuer and correct the
underlying time sync, which is the actual defect. If a tolerance is wanted in the
interim, VerifyJWT takes a `<TimeAllowance>` element that acts as a grace period for clock
skew on both `exp` and `nbf`. That widens how long an expired token is accepted, so it is
a security tradeoff to be stated and bounded rather than a default.

## Verification
Replay tokens minted at a range of offsets from expiry. Confirm tokens outside the skew
band are unaffected, and confirm the chosen allowance does not widen acceptance broadly.

## Common Incorrect Answers
Raising the Quota limit because 20% sounds like a rate problem.

Concluding the backend is slow, because the ticket named it as a candidate.

Concluding the signing key rotated or the tokens are forged, which would not produce a
failure confined to one expiry band.

Asserting the skew is a specific number of seconds and remediating against that number
without measuring it.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Handling of competing hypotheses | Checks sequentially | Keeps a list | Uses one discriminating test and a ledger |
| Diagnostic method | Guesses | Requests traces | Requests traces of failing and passing requests, and uses the status code to eliminate Quota early |
| Handling of uncertainty | Declares a cause | Partial | Ruled out two, confirmed one, leaves the measured offset open |
| Verification | None | Retests | Replays tokens at controlled offsets from expiry |

**Critical failures:** ruling out a candidate without evidence that excludes it.

**Not a critical failure:** recommending `<TimeAllowance>` to absorb the skew without
elaborating on the security cost. That is the documented remedy, and an incomplete answer
about it is not a wrong one.

## References
- What you need to know about policy errors:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/what-you-need-know-about-policy-errors>
- VerifyJWT policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jwt-policy>

## Critical failures
 ruling out a candidate without evidence that excludes it.
