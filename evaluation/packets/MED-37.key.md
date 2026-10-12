# MED-37 answer key, do not show to the agent

## Ground-Truth Resolution
The behaviour is correct and the mental model is wrong. The current Quota policy reference
reproduces the reporter's own worked example, with the same flow letters:

> For example, you create a Quota policy named `MyQuotaPolicy` with a limit of 5 requests
> and place it on multiple flows (Flow A, B, and C) in the API proxy. Even though it is
> used in multiple flows, it maintains a single counter that is updated by all instances of
> the policy: Flow A is executed -> counter = 1; Flow B -> 2; Flow A -> 3; Flow C -> 4;
> Flow A -> 5. The next request to any of the three flows is rejected.

and the same page states the rule directly: "If there is no API product associated with an
API proxy, a quota policy maintains a single counter, regardless of how many times you
reference it in an API proxy. **The name of the quota counter is based on the `name`
attribute of the policy.**"

So the counter identity is the policy `name` plus the identifier value, in a proxy with no
API product. Flow does not appear in it. Separation is achieved by using different policy
elements with different `name` attributes.

The page then adds the part that changes the answer depending on configuration: "By
default, Apigee maintains a separate quota counter for each operation defined in an API
product", with operation-level quota settings taking precedence over product-level ones,
and `quotaCounterScope` of `PRODUCT` or `PROXY` deciding which operations collapse onto a
shared counter.

Finally, the reference names the reuse as an antipattern: "Using the same Quota policy in
more than one place in an API proxy flow, which can unintentionally cause Quota to run out
faster than you expected, is an anti-pattern."

## Correct Remediation
Pick one of two intents, because they are different configurations.

To give each flow its own budget, use a separate Quota policy element per flow with
distinct `name` attributes. That is what the documentation prescribes and it is the
minimal change. Note that it multiplies policy instances, which is the cost the antipattern
page is warning about elsewhere in the product.

To keep one shared budget but control how the counter is scoped, use API products and
`quotaCounterScope`. This is the right tool when several proxies should contribute to one
budget, and it is worth naming explicitly because a common but incorrect claim in community
threads is that a single counter can be shared across API proxies by a Quota policy alone.
The reference is explicit that quotas "apply to individual API proxies and are not
distributed among API proxies... a single quota is not shared across all three even if all
three use the same quota policy configuration." Sharing across proxies is done through API
product configuration, not by pointing two policies at one counter.

## Verification
Confirm the counter now increments per flow, or per product scope, as intended, by reading
the quota variables across the flows in a debug trace rather than by inferring from
rejection counts.

Then confirm the intended per-resource budget empirically: a client that spends its whole
allowance on one resource should still have budget on the others.

Check whether other proxies share the same policy name and identifier and are silently
drawing on the same allowance, since that is the failure mode the customer is reporting.

## Common Incorrect Answers
"Each flow has its own counter because they are different flows." The documented rule is
the opposite, and it is the specific misconception the reporter brought to the question.

"Set a different `<Identifier>` per flow." The identifier keys the counter by client, not by
flow. Changing it would segment clients, not resources, and would make the problem worse.

"Share one counter across three proxies by using the same policy name and identifier." The
reference says quotas are not distributed among API proxies. This is the most common wrong
answer in the community on this exact question.

"Increase the allow count to 15 so all three flows fit." That concedes the shared-counter
behaviour silently and removes the per-resource protection the customer was trying to get.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says one counter per flow | Says one counter per policy name | Says one counter per policy name plus identifier, and states it is documented |
| Diagnostic method | Reads the fault code only | Inspects the policy | Confirms counter sharing in a trace with the quota variables |
| Completeness | Answers only the specific question | Adds the antipattern note | Adds the API-product per-operation model and `quotaCounterScope` |
| Handling of competing advice | Repeats "share across proxies" | Hedged | States plainly that quotas are not distributed among API proxies |
| Quality of next step | Raise the allow count | Separate policy names | Separates policy names or moves to product-scoped counters, depending on stated intent |

## References
- Reported case: <https://stackoverflow.com/questions/21615609>
- Quota policy, "Understand quota counters", "How quotas are counted", and
  `quotaCounterScope`:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
- Antipattern, reusing a Quota policy:
  <https://cloud.google.com/apigee/docs/api-platform/antipatterns/reusing-quota>
- Antipattern, non-distributed quota:
  <https://cloud.google.com/apigee/docs/api-platform/antipatterns/non-distributed-quota>
- Error index entry for `policies.ratelimit.QuotaViolation`:
  `.agents/skills/apigee-support-core/references/error-codes.md`

## Critical failures
asserting one counter per flow; asserting a Quota policy alone can share a counter across proxies; raising the allow count to compensate without raising the
per-resource protection problem.
