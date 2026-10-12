# EASY-11 answer key, do not show to the agent

## Ground-Truth Resolution
`InvalidQuotaTimeUnit` fires when the `<TimeUnit>` value is unsupported. The `<TimeUnit>`
element reference is the normative list and reads: select from `minute`, `hour`, `day`,
`week`, `month`, or `year`. `minutes` is not among them.

The deployment-error table on the same page gives a shorter list that omits `year`. Both are
official, and the element reference is the one that governs what the element accepts, so
quote it rather than the table. Naming the full list including `year` is correct and should
not be marked down.

The revision was rejected, so the currently deployed revision continues to serve.

## Correct Remediation
Use the singular form matching the intent:

```xml
<Quota name="PerDay">
  <Interval>1</Interval>
  <TimeUnit>day</TimeUnit>
</Quota>
```

## Verification
Deploy, confirm it saves, then send more requests than the limit and confirm a
`QuotaViolation`. Confirm the counter resets on the documented boundary rather than
assuming a rolling window, since the quota `type` determines the reset behavior.

## Common Incorrect Answers
Accepting `minutes` as an alias. It is not documented as one, and the documented list is
singular.

Recommending `60` with `TimeUnit` minute to express an hour. That works but changes the
reset semantics depending on quota type, so the `hour` unit is clearer.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Guesses accepted values | Identifies singular/plural | Names the full list from the `<TimeUnit>` element reference, including `year` |
| Evidence and citation | None | Generic | Cites the Quota deployment error reference |
| Quality of next step | "Use minute" | Gives a value | Gives a value and asks about intent |
| Verification | None | Retests | Retests and checks reset semantics |

**Critical failures:** asserting undocumented units are accepted.

## References
- Quota policy deployment errors:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>

## Critical failures
asserting undocumented units are accepted.
