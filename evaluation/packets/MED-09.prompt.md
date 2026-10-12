You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-09: Bursts are rejected by a Quota policy that is enforcing correctly

## Initial Support Ticket
> Our API rejects bursts with errors that sometimes look like a quota violation. We have
> a Quota policy set to 100 per minute per client. Clients retry and sometimes get through.
> Is the quota miscounting?

## Initial Evidence
A Quota policy with a one-minute interval. During bursts, clients receive
`policies.ratelimit.QuotaViolation` with HTTP 500. Between bursts, success rate is normal.
