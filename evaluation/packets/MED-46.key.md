# MED-46 answer key, do not show to the agent

## Ground-Truth Resolution
Cert validation failures may return a 502 instead of a 503 error response when users add the tag
`<Enforce>true</Enforce>` in the target `<SSLInfo>` block for default validation of TLS target
endpoint certificates. This is a limitation and it is still OPEN, so the correct answer is not to
wait for a fix.

The status code is actively misleading here, which is the whole point of the entry. A 502 reads
as "the upstream returned something unusable", so an engineer checks target health, L7 routing
and gateway reachability, and finds all of them fine, because nothing is down. The cause is the
target certificate, and the code conceals it.

It is also worth being precise about what the customer did. They added `<Enforce>true</Enforce>`
*because* they wanted certificate validation. They did not weaken it. Default validation is being
enforced and the platform is reporting the result with the wrong code.

A related documented behaviour from the same register, entry 205666368, states that Apigee hybrid
does not validate the target certificate by default. Read together the two entries say that the
default is no validation, and that turning validation on produces a misleading status code.

## Correct Remediation
Fix the target's certificate chain, or add the issuing authority to the appropriate truststore.
There is no configuration change that makes a 502 become a 503, because the code is the
platform's, and the register has the issue open rather than resolved.

## Verification
Confirm the target certificate validates against the runtime trust store, then confirm the status
code is 200 or whatever the backend genuinely returns. Do not use the status code alone as proof,
since it is known to be wrong in this case.

## Common Incorrect Answers
Investigating target availability and load balancing. The target is up; that is established.

Recommitting the proxy or restarting runtime pods. Neither changes certificate validation.

Telling the customer to remove `<Enforce>true</Enforce>` to make the error go away. That silently
returns them to no certificate validation at all, which is the opposite of what they asked for.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Investigates target availability | Suspects the certificate | States 502 here means target certificate validation failed |
| Diagnostic method | Trusts the status code | Notes the code contradicts the evidence | Recognises the documented 502-instead-of-503 behaviour with `<Enforce>` set |
| Component attribution | Blames the gateway | Blames the backend broadly | Blames the target certificate chain against the runtime trust store |
| Quality of next step | Removes `<Enforce>` | Suggests restarting pods | Fixes the chain or truststore, and does not disable enforcement |

## References
- Known issues register (entries 310384001 and 205666368):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- API calls failing with TLS errors:
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/ingressgateway/api-calls-failing-tls-errors>

## Critical failures
advising removal of `<Enforce>true</Enforce>` as the fix; opening a load balancing or gateway investigation and closing it as an upstream outage.
Not a critical failure: not knowing the corresponding 503. The register gives only the observed
502, and inferring the intended 503 is a bonus rather than a requirement.
