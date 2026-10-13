# MED-09 answer key, do not show to the agent

## Not A Critical Failure
raising the `500` versus `429` question. The Quota policy
reference documents `500` in its runtime error table and `429` in a closing note on the
same page, so noticing that the observed status is not the one an agent would expect is
correct reading of the evidence rather than a dispute with the scenario. An answer that
keeps the diagnosis intact and asks how the Quota fault is being surfaced is the correct
answer; stopping there without completing the remediation is incomplete, not wrong.

## Not A Critical Failure
noting that `<Distributed>` and `<Synchronous>` both default
to `false`, and that the Quota policy page says you might exceed the quota on that
configuration. The evidence does not disclose either element, so an agent that raises the
counter-distribution caveat has read the reference correctly and must not be scored below 4
on Technical correctness for it. The caveat does not rescue "the quota is miscounting",
because the diagnostic evidence says counting per client per minute is accurate; treat the
two as separable claims, as the scenario's own analysis of the status code does.

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
Move the allowance to a longer window and put the bursts in SpikeArrest. The comparison
chart puts Quota at "longer time intervals like days, weeks, or months" and SpikeArrest at
"seconds or minutes", so the existing one-minute Quota sits in SpikeArrest's column and
cannot stay as the sustained allowance. Change that Quota's interval to the window the
commercial terms actually imply, and add SpikeArrest to shed the bursts.

SpikeArrest has no `rateLimit` element and no `timeWindow` element. Its
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

Adding a second Quota policy alongside the one-minute one and leaving that one in place.
Two Quota policies do not compose into burst protection, and the fix is to change the
existing interval rather than to stack another policy on top of it.

Naming `rateLimit` or `timeWindow` as SpikeArrest elements. Neither exists. The rate is the
body of `<Rate>` and must carry a `ps` or `pm` suffix, such as `<Rate>30ps</Rate>`.

Describing the observed rejections as spike rejections because the traffic is bursty. The
proxy has no SpikeArrest policy and the fault body is
`policies.ratelimit.QuotaViolation`; the burst shape is what makes a correctly enforced
Quota visible, not evidence that a different policy is firing.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says the quota is miscounting, or calls the observed fault a spike rejection | Identifies burst behavior | Explains enforcement is correct and policy choice is wrong |
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
