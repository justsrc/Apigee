You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-14

## Initial Support Ticket
> Security incident: we revoked a user's token at 09:15 and at 09:17 the token still
> worked. We need to know if revocation is broken, and if it is we need to lock the
> account out immediately.

## Initial Evidence
The token was invalidated through the OAuthV2 `InvalidateToken` operation. It stopped
working at 09:18.
