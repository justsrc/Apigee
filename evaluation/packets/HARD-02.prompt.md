You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case HARD-02

## Initial Support Ticket
> We removed the rate limiting from our API last month and the change was deployed
> successfully. But clients still receive rate limit errors. Either the deployment did not
> take effect or something is caching the old policy. Please advise.

## Initial Evidence
The bundle for revision 20 contains no Quota or SpikeArrest policy. The deployment list
shows revision 20 deployed to `prod`. Clients receive `policies.ratelimit.QuotaViolation`.
