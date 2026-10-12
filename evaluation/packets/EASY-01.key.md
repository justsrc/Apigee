# EASY-01 answer key, do not show to the agent

## Ground-Truth Resolution
`InvalidQuotaInterval` fires when the `<Interval>` element is not an integer. `0.5` is
not an integer, so the revision is rejected at upload. This is a deployment error, which
means it has no HTTP status and never reaches the runtime.

The reason it worked before is that the previously deployed revision predates the change
to the bundle. The revision that was live was built from an older bundle.

## Correct Remediation
Set `<Interval>` to a positive integer and specify the fraction through `<TimeUnit>`.

```xml
<Quota name="OrdersPerMinute" type="rollingwindow">
  <Interval>30</Interval>
  <TimeUnit>second</TimeUnit>
</Quota>
```

Confirm `second` is a supported `<TimeUnit>` value before recommending it. If the team
needs sub-minute windows, SpikeArrest is the documented recommendation rather than
abusing Quota. This is a configuration change in source control, so it is reversible, and
it affects only the next revision deployed.

## Verification
Re-deploy the revision. A successful save confirms the deployment error is gone. Then
send requests exceeding the intended rate and confirm a `QuotaViolation` with HTTP 500,
which is the documented runtime behaviour for an exceeded quota and proves the policy is
executing rather than merely parsing.

A superficial check is that the UI no longer shows an error. That proves the revision
saved. It does not prove the quota behaves as intended.

## Common Incorrect Answers
Recommending `<Interval>0.5</Interval>` with `<TimeUnit>minute</TimeUnit>` is the same
configuration restated, and still fails.

Treating this as a runtime fault and suggesting they look at API Monitoring traces is
wrong, because the revision never deployed and there is no trace.

Claiming the Quota policy does not support fractional intervals at all is an
overstatement. The restriction is that `<Interval>` must be an integer; the granularity
comes from `<TimeUnit>`.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Misdiagnoses as runtime | Correct cause, imprecise detail | Names `InvalidQuotaInterval` and the integer requirement |
| Product and version | Applies Edge procedures | Correct product, unstated | Correct product and product-appropriate steps |
| Evidence and citation | No source | Policy page referenced loosely | Cites the Quota policy error reference |
| Diagnostic method | Suggests log hunting | Identifies deployment stage | Explicitly excludes runtime investigation |
| Handling of uncertainty | Asserts without support | Reasonable | States what is confirmed and what remains unknown |
| Safety | Recommends production changes | Suggests a redeploy | Notes the change is source-controlled and reversible |
| Verification | "Deploy and check" | Checks save succeeded | Checks save plus resulting runtime behaviour |

**Critical failures:** treating this as a runtime fault; recommending a change to the
live revision without noting the current one keeps serving.

## References
- Quota policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
- What you need to know about policy errors:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/what-you-need-know-about-policy-errors>

## Critical failures
treating this as a runtime fault; recommending a change to the live revision without noting the current one keeps serving.
