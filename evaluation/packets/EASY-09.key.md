# EASY-09 answer key, do not show to the agent

## Ground-Truth Resolution
The `<Source>` variable is not defined on the failing requests. The assigning step sits
behind a flow condition that evaluates false for them, so `payload` is never created, and
that is exactly the documented second cause for `steps.jsontoxml.SourceUnavailable`:
"Can't be resolved (is not defined)". HTTP 500.

This policy has no deployment errors; the documented deployment error list for JSONToXML
is "None". The failure is entirely at request time.

The upstream contract change is not in the causal chain. It is real and still unverified,
which is why the verification step checks the produced XML against it, but it did not
produce this fault. On the requests where the assigning step runs, the same proxy converts
the same payload with the same policy and succeeds, which rules the contract change out as
the cause of the failures.

## Correct Remediation
Fix the flow so the variable the policy depends on exists on every request. Either move
the assigning step out of the conditional, or widen the condition. If the condition is
deliberate, then the conversion cannot be unconditional, and the policy should be guarded
by a matching `<Condition>` so it is skipped rather than faulting on the requests where
there is nothing to convert.

The `<OutputVariable>` element is already present here and should stay. The documented
rule is that it is mandatory when the `<Source>` variable is of type `string`, and the
trace shows `payload` resolves as a string. Removing it, or pointing `<Source>` at a
`message`-typed variable such as `request` or `request.content`, changes which rule
applies, so check the type before editing either one.

## Verification
Send requests that hit the conditional and requests that skip it. Both should succeed.
Confirm the produced XML matches what the upstream contract now expects, since that
contract change is the other thing in this ticket that nobody has checked yet.

## Common Incorrect Answers
Reading the fault as a problem with the client's HTTP `Content-Type` header. Neither
documented cause involves the header, and `Content-Type` is not in play.

Settling on `steps.jsontoxml.InvalidSourceType`. That code is about the type of a variable
that resolved, and it names `message` and `string` as the valid types. Nothing resolved
here, so there is no type to report.

Concluding it is `steps.jsontoxml.ExecutionFailed`, which fires when the input payload is
empty or malformed. That is the right suspicion if the contract change produced bad JSON,
but the evidence contradicts it: requests carrying the same payloads convert successfully
whenever the assigning step runs.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Chases Content-Type or the contract change | Identifies the unresolved source variable | Names SourceUnavailable, quotes both documented causes, and picks the one the trace supports |
| Diagnostic method | Guesses | Reads the policy | Reads the exact code and checks the conditional in a trace |
| Handling of uncertainty | Asserts one cause | Hedges | States that the code alone does not decide between the two causes, then says which one the trace shows |
| Quality of next step | Rewrites the contract handling | Moves the assigning step | Makes the assignment unconditional or guards the policy with a matching condition, and checks the OutputVariable rule |
| Verification | None | Retests | Tests both branches and checks the upstream contract |

**Critical failures:** attributing the fault to the client Content-Type header; removing
`<OutputVariable>` without first establishing whether `<Source>` resolves as `string`;
naming an element the JSONToXML policy does not have.

**Not a critical failure:** saying that `SourceUnavailable` names two documented causes and
that the code by itself does not identify which applies, and that the trace is needed to
choose. That is the accurate reading of the reference and earns full credit at the
Handling of uncertainty level. Observing that the fault code does not by itself settle the
question is a strength here, not a hedge. The fault code and the evidence are the same
code and the same condition, so an answer that reports them as matching is also correct.

## References
- JSONToXML policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/json-xml-policy>
- Variables reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/variables-reference>

## Critical failures
attributing the fault to the client Content-Type header; removing `<OutputVariable>` without first establishing whether `<Source>` resolves as `string`; naming an element the JSONToXML policy does not have.
