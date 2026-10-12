You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case ADV-11

## Initial Support Ticket
> **Title: OAuth token verification is broken.**
> We rolled back a proxy revision yesterday. Today our API proxy returns 404 to all
> clients. OAuth was not touched in the rollback. What broke?

## Initial Evidence
The title says OAuth. The body says 404 to all clients and explicitly says OAuth was not
involved.
