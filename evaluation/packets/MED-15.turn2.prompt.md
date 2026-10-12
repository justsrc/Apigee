You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-15: A Java callout fails only on some requests

The customer has replied with more information.

## Diagnostic Evidence
The first request in each hour succeeds and subsequent ones fail with
`steps.javacallout.ExecutionError`. Reading the callout source shows it fetches a
thread-local resource that the first call initialises and later calls do not
reinitialise.
