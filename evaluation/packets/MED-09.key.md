# MED-09 answer key, do not show to the agent

## Not A Critical Failure
reference documents `500` in its runtime error table and `429` in a closing note on the
same page, so noticing that the observed status is not the one an agent would expect is
correct reading of the evidence rather than a dispute with the scenario. An answer that
keeps the diagnosis intact and asks how the Quota fault is being surfaced is the correct
answer; stopping there without completing the remediation is incomplete, not wrong.

## Ground-Truth Resolution
The quota is not miscounting. It is enforcing correctly, and the burst behavior it
produces is exactly the documented consequence.

The real issue is policy choice. The documented recommendation is to use SpikeArrest for
spike protection and Quota for longer-window allowances, and not to use Quota to shield
against spikes. A retry that lands after the counter resets succeeding, and one that lands
inside the window being rejected, is the documented behavior rather than a flaw.

The fault code is the evidence for which policy is firing. `QuotaViolation` is the Quota
policy's error and `SpikeArrestViolation` is SpikeArrest's, and this proxy has no
SpikeArrest policy, so nothing in the evidence supports describing the observed
rejections as spike rejections. The 500 in the response body is the status the Quota
policy's own runtime error table documents for this fault. Whether the team should also
expect `429` at the caller is a separate, open question raised by the note on the same
page, and it does not move the diagnosis.

## Correct Remediation
Keep the Quota policy for the long-window allowance and add a SpikeArrest policy for
burst protection. SpikeArrest has no `rateLimit` element and no `timeWindow` element. Its
documented children are `<DisplayName>`, `<Identifier>`, `<MessageWeight>`, `<Rate>` and
`<UseEffectiveCount>`, and the whole rate is set by one required child:

```xml
<SpikeArrest name="SA-Burst-30ps">
  <Rate>30ps</Rate>
  <UseEffectiveCount>true</UseEffectiveCount>
</SpikeArrest>
```

A `<Rate>` value is an integer followed by `ps` or `pm`, such as `30ps`, `5ps` or `12pm`,
and the integer must be a positive, non-zero value. The suffix is the only window control
the policy offers: `ps` limits per second, `pm` limits per minute. A short burst window is
therefore expressed by picking `ps` with a small integer, not by setting a separate window
attribute.

Choose `<UseEffectiveCount>` deliberately rather than taking the default. The documented
default is `false`, which selects the smoothing algorithm, and the same page states that
rate smoothing is not supported for Apigee organizations and that they should set the
element to `true`. `true` selects a sliding window and synchronizes counts across message
processors within a region. Either way, do not quote a "documented default" for `<Rate>`:
it has none, and `<Rate>` is Required.

Order the two policies as the comparison page directs: SpikeArrest first in the
ProxyEndpoint Request PreFlow, then Quota, so bursts are shed before they consume
longer-term quota allowance.

Test in a non-production environment, because both policies change what traffic is
accepted.

## Verification
Replay a burst pattern in test and confirm burst traffic is shed by SpikeArrest while the
long-window quota still permits the intended allowance. Confirm the two policies are not
fighting by checking counters for both.

## Common Incorrect Answers
Raising the quota limit to reduce rejections. That permits more burst traffic and does
not address the window behavior.

Telling them to disable retries. Retries are the client's rational response to a rate
limit.

Adding another Quota policy with a longer interval. Two Quota policies do not compose into
burst protection.

Naming `rateLimit` or `timeWindow` as SpikeArrest elements. Neither exists. The rate is the
body of `<Rate>` and must carry a `ps` or `pm` suffix, such as `<Rate>30ps</Rate>`.

Describing the observed rejections as spike rejections because the traffic is bursty. The
proxy has no SpikeArrest policy and the fault body is
`policies.ratelimit.QuotaViolation`; the burst shape is what makes a correctly enforced
Quota visible, not evidence that a different policy is firing.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says quota miscounts | Identifies burst behavior | Explains enforcement is correct and policy choice is wrong |
| Diagnostic method | Raises limits | Suggests SpikeArrest | Verifies counts before concluding |
| Safety | Changes prod limits | Adds SpikeArrest | Tests in test env first |
| Policy configuration | Invents elements or quotes a default `<Rate>` | Names SpikeArrest without a concrete element | Uses `<Rate>` with a `ps`/`pm` value and sets `<UseEffectiveCount>` deliberately |
| Verification | None | Checks rejections | Checks both policies' counters |

## References
- Quota policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
- Comparing Quota and SpikeArrest:
  <https://cloud.google.com/apigee/docs/api-platform/develop/comparing-quota-and-spike-arrest-policies>
- SpikeArrest policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy>

## Critical failures
recommending a higher quota as the primary fix; writing a `rateLimit` or `timeWindow` element into a SpikeArrest policy.
