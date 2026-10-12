# MED-10 answer key, do not show to the agent

## Ground-Truth Resolution
The token is expired, which is a single condition. The status differs because the two
proxies use different policies to handle it: `VerifyAccessToken` surfaces 401, while
`GetOAuthV2Info` and `SetOAuthV2Info` surface 500 for an expired token.

An expired token cannot pass `VerifyAccessToken`, so a trace showing that step succeeding
would contradict the ground truth rather than explain the difference. What the trace
establishes is which policies are on each path, and that is what makes the status
difference legible.

The client's experience is consistent, not contradictory, once you know the status codes
are policy-specific.

## Correct Remediation
Treat both as the same condition in client-facing handling, keyed on `errorcode` rather
than on status. Normalize the client to handle 401 and 500 for token problems, or align
the two proxies to use the same policies.

The fault rules matter too: catching `invalid_client` and `InvalidClientIdentifier` covers
one condition that splits on `<GenerateResponse>`.

## Verification
Use an expired token against both proxies and confirm both are treated as auth failures
after the fix. Then confirm a valid token produces 200 on both.

## Common Incorrect Answers
Calling the 500 a server fault and alerting on it. It is an auth failure with an
inconsistent status.

Telling them to regenerate tokens client-side, which does not address why two proxies
disagree.

Assuming one proxy is misconfigured. Both behave as documented.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Calls it a server fault | Notes status differs | Identifies policy-specific statuses |
| Diagnostic method | Compares configs | Reads trace | Identifies which policy produced the status |
| Quality of next step | Rotates tokens | Normalizes client | Normalizes on errorcode and aligns proxies |
| Verification | None | Retests | Tests expired and valid on both |

## References
- OAuthV2 policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>
- GetOAuthV2Info policy, which documents the 500 for an expired token:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/get-oauth-v2-info-policy>
- SetOAuthV2Info policy, same code at 500:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/set-oauth-v2-info-policy>
- OAuth HTTP status codes, deprecated but informative:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauth-http-status-code-reference>

## Critical failures
recommending escalation as a platform bug without checking which policy produced the status.
