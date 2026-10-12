# MED-33 answer key, do not show to the agent

## Ground-Truth Resolution
There is no fault. Two independent effects compound. SpikeArrest is documented as a rate
limiter rather than a counter: it "smoothes the rate to one request allowed every
200 *milliseconds* (1000/5)" for per-second rates, and per-minute rates are smoothed into
intervals of seconds, so `5pm` becomes one request per 12 seconds. And smoothing is
documented as "not coordinated across Message Processors". With two message processors the
observed allowance doubles to two requests per 12 seconds, which is exactly what the
customer saw.

The customer's mental model, a per-minute counter, is the thing that is wrong. Their
question, whether the two message processors are the cause, is the right question and the
answer is yes.

## Correct Remediation
Decide which of two things the customer actually wants, because they need different
configurations. If they want burst protection, keep the token-bucket smoothing and choose
a rate that reflects the interval their backend can absorb, understanding the effective
admission rate is the configured rate multiplied by the number of message processors. If
they want an accurate count of requests per period, that is the Quota policy's job; the
SpikeArrest reference itself points there.

If the customer wants both, the documented combination is SpikeArrest first in the
ProxyEndpoint request PreFlow for burst protection, then Quota for the longer-term count.
The comparison page states SpikeArrest "should always be attached before the Quota policy
in the ProxyEndpoint Request PreFlow... This prevents spikes from prematurely exhausting
quota."

Raise `<MessageWeight>` handling regardless: bind it to a header the clients actually send
or remove it. An unset `ref` currently resolves to 1, which means the policy silently
accepts a configuration the operator believes is active.

## Verification
Send requests at the documented interval and confirm exactly one per processor per
interval succeeds. Then confirm the rejection path: check
`ratelimit.SpikeArrest.failed` separately from
`ratelimit.SpikeArrest.exceed.count > 0`, since the reference warns that `failed` "should
not be used to check if a rate limit has been exceeded".

Re-test after any change to the rate so the multiplication by message processor count is
re-derived from the trace rather than assumed, because the trace is what established it.

## Common Incorrect Answers
"Your SpikeArrest policy is counting wrong; five requests should have been allowed." It is
not counting, it is smoothing, and the documentation states that explicitly.

"Increase the rate to 10pm to compensate." This doubles the real allowance and, with two
processors, admits four per 12 seconds, which is not what anyone asked for.

"Switch to a Quota policy." Legitimate only if the customer wants counts. Offered as a
general fix it replaces burst protection with a window count and lets the burst through.

"Remove the two routers, they are causing double counting." Routers do not hold policy
counters.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Assumes a per-minute counter | Applies smoothing, misses processor multiplication | Applies smoothing **and** the per-processor multiplication, and checks message weight |
| Diagnostic method | Restates the rate | Suggests raising it | Uses a debug trace to separate weight from topology |
| Safety | Changes the rate immediately | Proposes a change | Establishes whether the customer wants burst protection or counts before changing |
| Handling of competing causes | Ignores MessageWeight | Mentions it | Confirms the unset `ref` resolves to 1 and recommends fixing the binding |
| Verification | None | Retests once | Checks the documented ratelimit variables and keeps `failed` separate from `exceed.count` |

## References
- Reported case: <https://stackoverflow.com/questions/21912316>
- SpikeArrest policy, `<Rate>`, `<MessageWeight>`, smoothing:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy>
- Comparing Quota and SpikeArrest:
  <https://cloud.google.com/apigee/docs/api-platform/develop/comparing-quota-and-spike-arrest-policies>
- Error index entry for `policies.ratelimit.SpikeArrestViolation`:
  `.agents/skills/apigee-support-core/references/error-codes.md`

## Critical failures
treating SpikeArrest as a request counter; raising the rate as the first move; ignoring `<MessageWeight ref=...>`.
