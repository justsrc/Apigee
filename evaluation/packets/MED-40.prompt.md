You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-40

## Initial Support Ticket
> We deployed `/v1/orders` to `prod` last month and it works. This week we deployed `/v1/orders`
> to `uat`. Both deploy calls returned success and both show as deployed. Now traffic for one of
> them 404s and we cannot tell which. Nobody can tell us which proxy is at fault. Can you check
> the deployments?

## Initial Evidence
The Management API reports both revisions deployed in their respective environments. Both
environments are attached to the same environment group. Requests to one proxy host resolve and
succeed. Requests to the other return 404. No error is logged at deploy time or since.
