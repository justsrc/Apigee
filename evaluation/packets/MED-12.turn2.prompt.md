You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-12

The customer has replied with more information.

## Diagnostic Evidence
The trace shows the ServiceCallout step failing at its configured `<Timeout>` of 200ms. The
policy is named `SC-Enrich` in the customer's bundle; the name is theirs, not an Apigee
convention. The enrichment service's slow requests are long-tail cases, not p95 cases, so p95
looked fine while p99.9 exceeded 200ms.
