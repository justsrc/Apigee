You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-04: Cached responses are stale and nobody can reproduce it

## Initial Support Ticket
> Users occasionally see old pricing data for a few minutes after we update it upstream.
> We think it is the Apigee cache. Can you tell us how to turn it off?

## Initial Evidence
A ResponseCache policy on the response path with a short `<TimeoutInSeconds>` inside
`<ExpirySettings>`. The upstream pricing service updates about once every ten minutes.
Users report a window of a few minutes during which data is stale.
