# MED-36 answer key, do not show to the agent

## Ground-Truth Resolution
The policy is not doing too much work, it is waiting too long, and no amount of splitting
changes that. The 200 ms budget is being consumed by a blocking `httpClient.send` plus
`waitForComplete`, so the policy fails exactly when the downstream call is slow. That also
explains the intermittency and explains why the customer's own mitigation did nothing.

Worse for the accepted answer: on a free trial or evaluation organisation, the documented
note says execution time is limited to 200 ms regardless, so raising `timeLimit` may change
nothing at all. The accepted answer does not consider the organisation tier and cannot
explain why the same policy would fail differently on a paid organisation.

The underlying construction is also a documented antipattern. Invoking one API proxy from
another with custom JavaScript or an `HTTPTargetConnection` "results in additional network
hop", because the request "has to be routed through the traditional route (Router > MP) at
runtime... a request has already reached the MP". The documented fix is proxy chaining.

## Correct Remediation
Remove the proxy-to-proxy call rather than pay for it in timeLimit. Proxy chaining runs
the called proxy in the same message processor over a local connection:

```xml
<LocalTargetConnection>
  <APIProxy>proxyA</APIProxy>
  <ProxyEndpoint>default</ProxyEndpoint>
</LocalTargetConnection>
```

If the second proxy genuinely must be reached over the network, keep the call out of
JavaScript. Use a ServiceCallout, which is a policy with its own timeout surface, or move
the request shaping into the target endpoint.

Only after removing the blocking call is raising `timeLimit` even the right conversation,
and at that point establish the organisation tier first, because the documented free-trial
limit makes the attribute ineffective on trial and evaluation organisations.

## Verification
Confirm the failure rate drops to zero across a sustained load test that includes slow
downstream responses, not just fast ones. The intermittency means a passing smoke test
proves nothing here.

Then confirm the script actually completes: the `context.log` after `waitForComplete`
should appear on every request, which it did not before.

Confirm the organisation tier before relying on any `timeLimit` value, and if it is a trial
or evaluation organisation say so rather than raising the attribute and reporting no change.

## Common Incorrect Answers
"Raise `timeLimit` to 1000." This is the accepted answer on the source thread. It raises
the ceiling while leaving the blocking call in place, converts an intermittent failure into
a less frequent one, and is documented as ineffective on free trial and evaluation
organisations.

"Split the JavaScript into smaller modules." The customer already did this and reported it
did not help. The agent should treat that as evidence, not as a suggestion to repeat.

"Increase the message processor size or memory." The limit is a per-policy wall-clock
budget, not a resource limit.

"Retry the JavaScript policy." There is no built-in retry for a policy execution timeout,
and a retry would double the downstream load that caused the timeout.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Raises timeLimit | Identifies the call as the cost | Identifies the blocking call as the cost and names proxy chaining as the fix |
| Diagnostic method | Treats it as a code-size problem | Notes intermittency | Uses intermittency as evidence against a CPU-bound cause |
| Product knowledge | Ignores tier | Mentions trial limit | States the documented free-trial 200 ms limit and checks the tier before recommending |
| Handling of the accepted answer | Reproduces it | Hedges | States the accepted answer is incomplete and tier-dependent |
| Quality of next step | Raises the attribute | Moves the call to a policy | Removes the network hop via proxy chaining, then verifies under slow-downstream load |

## References
- Reported case: <https://stackoverflow.com/questions/22995892>
- JavaScript policy, `timeLimit` attribute and the free-trial note:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/javascript-policy>
- Antipattern, invoking a proxy within a proxy:
  <https://cloud.google.com/apigee/docs/api-platform/antipatterns/proxy-within-proxy>
- Error index entry for `steps.javascript.ScriptExecutionFailed`:
  `.agents/skills/apigee-support-core/references/error-codes.md`

## Critical failures
recommending a higher `timeLimit` as the fix; repeating the "split the script" advice the customer already ruled out; ignoring the documented free
trial 200 ms execution limit.
