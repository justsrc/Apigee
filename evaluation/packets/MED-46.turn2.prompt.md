You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-46: The 502 that means your certificate is bad

The customer has replied with more information.

## Diagnostic Evidence
The target's certificate chain does not validate against the runtime's trust store. `<Enforce>` is
set to `true` in the target `<SSLInfo>` block, which selects default validation.
