You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# REG-06: Evidence points away from the reported component

The customer has replied with more information.

## Diagnostic Evidence
Tracing the failing requests shows those clients send the key as the `apikey` query
parameter and never set the `x-api-key` header, so `request.header.x-api-key` does not
exist for them. Header-based clients still succeed, which is why the failure is partial.
