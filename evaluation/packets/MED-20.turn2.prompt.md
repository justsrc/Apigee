You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-20

The customer has replied with more information.

## Diagnostic Evidence
The TargetEndpoint contains a `<LoadBalancer>` with multiple servers. Runtime pod logs show the
contract version advancing. Requests that still time out at 5 seconds correlate with a Message
Processor that has not applied the new contract value.
