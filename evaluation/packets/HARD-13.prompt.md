You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case HARD-13

## Initial Support Ticket
> 20% of requests to our reports API are coming back 401 starting this morning. We have
> a Quota policy, a VerifyJWT policy and a backend that is "probably fine". Please find the
> cause.

## Initial Evidence
401s on 20% of requests. No deploys. The three components named in the ticket are the
three candidates.

The status code is the first discriminator and should be used as one. A request rejected by
Quota is surfaced to the caller as 429, not 401. VerifyJWT returns 401 on every documented
runtime error, so a batch of 401s narrows the field before any trace is read.
