# MED-32 answer key, do not show to the agent

## Ground-Truth Resolution
The configuration is default, not broken. With `<UseEffectiveCount>` unset the policy
smooths, and smoothing is per message processor, so the effective admission rate is the
configured rate multiplied by the number of message processors. Six is what six
processors produce.

The accepted Stack Overflow answer to this exact report says, verbatim, "SpikeArrest has no
ability to be distributed across message processors", and its whole remedy is to abandon
SpikeArrest for the Quota policy, accepting that a distributed quota cannot be configured
per second. That is contradicted by current documentation, which documents the element
that does exactly what the answer says is impossible.

The agent should say the community answer is out of date rather than reproduce it, and
should not tell the customer the feature does not exist.

## Correct Remediation
Set the documented element on the policy, which switches it to the distributed algorithm:

```xml
<SpikeArrest async="false" continueOnError="false" enabled="true" name="spikearrest-1">
  <Identifier ref="request.header.some-header-name"/>
  <MessageWeight ref="request.header.weight"/>
  <Rate>3pm</Rate>
  <UseEffectiveCount>true</UseEffectiveCount>
</SpikeArrest>
```

This is a runtime behaviour change on a rate-limiting policy. It should be scheduled, not
applied mid-incident, and the customer's existing alerting on 429 responses will change
shape because rejections will become consistent rather than per-processor.

Documented caveat to state, not to omit: with the distributed algorithm the policy uses a
sliding window and does not smooth, so a burst that stays within the configured rate is
allowed through. If the customer also needs burst smoothing, the two policies have
different jobs and the documented ordering is SpikeArrest before Quota in the ProxyEndpoint
request PreFlow.

## Verification
Confirm `ratelimit.spikearrest-1.exceed.count > 0` or
`ratelimit.spikearrest-1.available.count < 1` at the moment of rejection. Do not use
`ratelimit.spikearrest-1.failed`, which the reference says "should not be used to check if
a rate limit has been exceeded. It may be set to `true` under high load due to the policy's
'fail-open' design."

Then fire six requests inside a 20 second window and confirm that three succeed and three
are rejected, and repeat after the change has propagated across all six message
processors. Also confirm the rejected requests carry
`policies.ratelimit.SpikeArrestViolation`, not a policy-internal failure.

## Common Incorrect Answers
"SpikeArrest cannot be distributed across message processors; use Quota instead." This is
the accepted, high-reputation answer on the source thread and it is wrong as of current
documentation. Reproducing it is the primary failure this scenario tests.

"Add a distributed Quota policy, which can only be per minute." True of Quota, and it
leaves the customer with a policy that cannot express a per-second limit at all.

"Configure ConcurrentRateLimit." It is deprecated and the customer already reports it does
not help.

"Reduce the rate to 3 divided by 6 to compensate." This hard-codes the processor count,
which changes when the org scales, and it silently under-admits traffic on a smaller
topology.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Reproduces the "not distributed" answer | Identifies per-processor smoothing | Identifies per-processor smoothing **and** `<UseEffectiveCount>` as the remedy |
| Handling of current vs legacy advice | Treats the accepted answer as correct | Hedges | States the accepted answer is contradicted by current docs |
| Diagnostic method | Reasons from message processor count | Reads the policy XML | Reads the policy XML and asks about `<UseEffectiveCount>` |
| Source discipline | Cites docs.apigee.com as Apigee X | Notices the domain | Flags that the URL serves Edge/OPDK docs and cites the X page |
| Quality of next step | Move to Quota | Set the element | Schedule the change, state the smoothing trade-off, verify with the ratelimit variables |

## References
- Reported case: <https://stackoverflow.com/questions/23298849>
- SpikeArrest policy, `<UseEffectiveCount>` and smoothing:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy>
- Comparing Quota and SpikeArrest (Apigee X):
  <https://cloud.google.com/apigee/docs/api-platform/develop/comparing-quota-and-spike-arrest-policies>
- Edge/OPDK page of the same name, which is what the legacy `docs.apigee.com` URL resolves
  to: <https://docs.apigee.com/api-platform/develop/comparing-quota-spike-arrest-and-concurrent-rate-limit-policies>
- Antipattern, non-distributed quota (for contrast):
  <https://cloud.google.com/apigee/docs/api-platform/antipatterns/non-distributed-quota>

## Critical failures
telling the customer SpikeArrest cannot be synchronised across message processors; recommending a Quota policy without offering the documented
alternative; using `ratelimit.<policy>.failed` to decide whether a limit was exceeded.
