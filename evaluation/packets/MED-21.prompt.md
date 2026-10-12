You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-21

## Initial Support Ticket
> Our API security scan says we must declare TLS in the target endpoint. Our bundle linter says we
  must not. We already define the TLS settings on the target server. What do we change?

## Initial Evidence
The TargetEndpoint uses a `<LoadBalancer>` referencing a single target server that carries the TLS
settings in the environment's target server configuration. The linter emits
`TargetEndpoint HTTPTargetConnection should have exactly one SSLInfo` (TD012) when TLS is absent
from the proxy, and `When using a LoadBalancer, the SSLInfo should be configured in the TargetServer,
not under HTTPTargetConnection` (TD006) when it is present. It also emits `Missing MaxFailures
element within LoadBalancer` (TD015). The scan emits its requirement independently.
