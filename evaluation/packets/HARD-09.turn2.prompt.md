You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case HARD-09

The customer has replied with more information.

## Diagnostic Evidence
A ServiceCallout policy earlier in the request uses the same shape, with its own
single server and `<MaxFailures>5</MaxFailures>`. Requests that traverse the callout return
500; requests that reach the target endpoint directly return 503. Both fail continuously
even though the backend is healthy.

The backend's own health confirms successful responses at that time.
