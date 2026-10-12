# MED-44 answer key, do not show to the agent

## Ground-Truth Resolution
In Apigee 1-15-0-apigee-5 and hybrid 1.15.0, Apigee stopped sending `x-b3` headers to target
endpoints when Distributed Trace is disabled. Some installations were relying on `x-b3` headers
being sent regardless of whether Distributed Trace was enabled or disabled. The change was
therefore reverted starting in Apigee 1-15-0-apigee-7.

Three properties make this hard to resolve by version alone.

The behaviour is **non-monotonic**. It was present, it disappeared, it came back. "Fixed in
1-15-0-apigee-7" does not mean a newer org has the new behaviour; it means the removal was
undone. An agent that assumes the present state is the newest behaviour will be wrong twice.

The fix is **not enabled by default**. The register says that anyone experiencing the issue
should reach out to Apigee to revert the change for now in their org. That is a per-org pin. Two
orgs on the same version can behave differently, and version cannot tell them apart.

The headers were a **latent default in use**. Nobody configured them. They were injected because
something depended on them once, and nothing recorded that dependency.

The register closes with a caution worth surfacing to the customer: Apigee does not recommend
relying on `x-b3` headers when Distributed Trace is disabled, because doing so will not guard
against a future change to this behaviour.

## Correct Remediation
Ask Apigee to re-pin this org to the previous behaviour, as the register directs, and
simultaneously start removing the backend's dependence on `x-b3` headers. The reversion is a
reprieve with an explicit warning attached, not a permanent answer, and a support engineer who
applies only the first half is handing the customer the same problem later.

## Verification
Confirm the target receives `x-b3` headers again, and confirm Distributed Trace remains disabled so
the change was not achieved by turning tracing on.

## Common Incorrect Answers
Enabling Distributed Trace to get headers back. That changes the customer's tracing behaviour and
costs money to fix a correlation problem.

Asserting the org must be on 1-15-0-apigee-7 or later. The org may already be, and still be
affected, because the fix is per-org opt-in.

Telling the customer the header removal was a bug they must live with. It was reverted, at their
request, on request.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Enables Distributed Trace | Identifies the `x-b3` removal window | States it was reverted and that the reversion is per-org opt-in |
| Diagnostic method | Inspects proxy policies | Checks org version | Checks org version and whether the org is pinned to old behaviour |
| Version handling | Assumes newer means current behaviour | Notices the reversion | Recognises the behaviour is non-monotonic across versions |
| Quality of next step | Turns tracing on | Requests the pin | Requests the pin and starts removing the backend dependency |

## References
- Known issues register (entry 422757662):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Distributed trace: <https://cloud.google.com/apigee/docs/api-platform/debug/trace-overview>

## Critical failures
enabling Distributed Trace as the remedy; concluding that an org on a version at or past 1-15-0-apigee-7 cannot be affected.
Not a critical failure: recommending removing the `x-b3` dependency first, without requesting the
pin. It is the better long-term advice but does not restore the customer's current behaviour.
