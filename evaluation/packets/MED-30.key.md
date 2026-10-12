# MED-30 answer key, do not show to the agent

## Ground-Truth Resolution
This is documented behaviour, not a defect. The OAuthV2 policy reference documents a
non-compliance section and states that by default the policy exhibits non-RFC-compliant behaviour,
and that this is the default. The documented differences are four: the token type value, the
absence of cache-control headers, the lifetime values being quoted strings, and the shape of the
error returned for an expired refresh token.

The last one is the trap that makes this more than a token type fix. Enabling compliance changes
the expired-refresh-token error from a proprietary shape to the standard shape. Any client, log
parser, dashboard or alerting rule that matches on the non-compliant shape will stop matching the
moment compliance is switched on. Enabling this element is a client-visible behaviour change across
all four fields at once, and it should be presented as one.

The documentation itself lagged the behaviour by more than a year. The issue records the behaviour
being reported in 2019, the documentation being updated in November 2019, and the underlying
documentation defect not closing until December 2020. That gap is why this looked like an
unsolvable bug to the people who hit it.

## Correct Remediation
Set the compliance element on the token-generating policy:

```xml
<RFCCompliantRequestResponse>true</RFCCompliantRequestResponse>
```

Then audit every consumer before and after, because four fields change at once:

- the token type value becomes `Bearer`;
- lifetime values become numbers instead of quoted strings, which breaks consumers doing string
  comparison on them;
- cache-control headers appear on responses containing tokens;
- the expired-refresh-token error changes shape, which breaks anything matching on the previous
  field names.

If the token endpoint must keep the legacy shape for an existing consumer, issue compliant tokens
from a separate endpoint or on a separate API product rather than changing the endpoint in place.

## Verification
Request a token and confirm the token type is `Bearer`. Confirm the lifetime values are serialised
as numbers. Then exercise an expired refresh token and confirm the error carries the standard
fields. Confirm a client that echoes the token type back now constructs a correct authorization
header.

## Common Incorrect Answers
Fixing the developer portal or regenerating the SDKs. Both are consuming the token type as
supplied, which is what the specification asks them to do.

Raising the backend or the API key policy, since the symptom is a 401 downstream. Nothing about the
credential is wrong; the header is malformed before it reaches the backend.

Switching compliance on without auditing consumers. It fixes the header and breaks anything
matching the previous error field names or comparing lifetime values as strings.

Assuming this is an Apigee bug and filing it. The behaviour is documented and the documentation
describes this element as the way to change it.

Treating only the token type as the difference. The other three changes ship with it.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Fixes the portal or SDK | Names the token type | Identifies the documented default and enumerates all four fields that change |
| Diagnostic method | Investigates the backend | Inspects the token response | Inspects the raw token response and the value types of the lifetime fields |
| Handling of the change | Sets compliance immediately | Sets compliance and warns | Presents it as a client-visible behaviour change and audits consumers for all four fields |
| Quality of next step | Tells the customer to regenerate SDKs | Sets the element | Sets the element and enumerates the downstream audit, with a separate endpoint as the safe alternative |

## References
- Real report of the non-compliant token type affecting a portal and SDKs:
  <https://github.com/apigee/apigee-api-catalog-drupal/issues/46>
- OAuthV2 policy reference, non-RFC-compliant behaviour and the compliance element:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>
- OAuth 2.0 access token overview:
  <https://cloud.google.com/apigee/docs/api-platform/security/oauth/access-tokens>

---### MED-40. Two green deploys, one invisible conflict

## Critical failures
editing the developer portal or SDKs instead of the token endpoint; enabling compliance without warning that the error response shape and the lifetime value types
also change; describing the non-compliant default as an Apigee defect.
