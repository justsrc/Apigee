You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# EASY-03: FlowCallout cannot find the shared flow

The customer has replied with more information.

## Diagnostic Evidence
The shared flow exists in the bundle and imports fine. Querying deployments for the
environment shows the shared flow has never been deployed there. The proxy deployment
succeeded because the shared flow reference is resolved at request time, not at upload.
