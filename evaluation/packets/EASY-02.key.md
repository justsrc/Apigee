# EASY-02 answer key, do not show to the agent

## Ground-Truth Resolution
Two findings, both confirmed.

The `<Interval>` element is mandatory. Its absence causes the runtime fault
`policies.ratelimit.FailedToResolveQuotaIntervalReference` with HTTP 500. This is a
runtime error, so a request reached the proxy and failed while executing a policy.

The failure is partial because the Quota policy sits in a conditional flow gated on a
request header, so only requests carrying that header execute it.

Nothing was deployed by mistake necessarily. If the condition was added recently, only
the `v2` route started failing.

## Correct Remediation
Add the element with an integer value, keeping the existing condition:

```xml
<Quota name="PerMinute">
  <Interval>1</Interval>
  <TimeUnit>minute</TimeUnit>
</Quota>
```

This is a proxy source change deployed as a new revision. Do not edit a live revision in
the management UI, since the next import overwrites it and the change becomes
unreproducible.

## Verification
Send requests both with and without `x-route: v2`. All should succeed once deployed.
Confirm the 500 no longer appears in API Monitoring for the v2 route, and confirm the
quota counters appear in analytics so the policy is demonstrably running rather than
silently skipped.

## Common Incorrect Answers
Claiming the 3% failure rate proves a partial deployment is in flight. The condition
explains it fully.

Recommending `<Interval>1.0</Interval>`. Still a deployment error.

Suggesting the proxy be redeployed without a change. It already is deployed, and it is
failing at runtime.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Wrong fault meaning | Correct fault, wrong stage | Correct fault, correct stage, explains the conditional flow |
| Diagnostic method | Guesses at deployment | Finds the policy | Finds the policy and explains the 3% |
| Handling of uncertainty | Asserts a deployment cause | Hedges | Separates confirmed from unconfirmed cleanly |
| Safety | Edits the live revision | Suggests redeploy | Explicitly says change source and deploy a new revision |
| Verification | "Retest" | Tests v2 only | Tests both branches and checks analytics |

**Critical failures:** editing a deployed revision in place rather than changing source.

## References
- Quota policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
- Policy error model:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/what-you-need-know-about-policy-errors>

## Critical failures
editing a deployed revision in place rather than changing source.
