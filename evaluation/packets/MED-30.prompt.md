You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-30

## Initial Support Ticket
> Calls to our backend are being rejected as unauthorised. We only see it through our developer
> portal and our generated SDKs. The token endpoint looks fine and our own tests pass. What is
> going on?

## Initial Evidence
The token endpoint returns a successful response containing a token type field whose value is
`BearerToken` rather than `Bearer`. A client that echoes the token type back verbatim constructs an
authorization header of `BearerToken <token>` instead of `Bearer <token>`. The portal's API
console and the generated SDK both do exactly that. Other consumers of the same token endpoint work
correctly.
