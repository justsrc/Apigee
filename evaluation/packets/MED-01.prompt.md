You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-01

## Initial Support Ticket
> We deployed our proxy to the `prod` environment about an hour ago. The deployment call
> returned success. Every request to the proxy host returns 404. The same proxy works
> perfectly in `test`. Can you redeploy it?

## Initial Evidence
Deployment list for `prod` shows the revision deployed. A request to the proxy hostname
returns 404 with an Apigee error body. The proxy has no conditional flows on the request
path.
