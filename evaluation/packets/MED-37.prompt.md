You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-37

## Initial Support Ticket
> We have one proxy with three flows, A, B and C. All three reference a single Quota policy
> named `QuotaLimitPolicy`, configured as 5 requests per interval, with an `<Identifier>`
> bound to `client_id`. We expected each flow to have its own budget of 5.
>
> What we see is that the budget is shared. A client calling only flow A exhausts the
> allowance that we budgeted for all three, and starts receiving quota rejections even
> though it has touched only one of the three resources.
>
> Failing calls carry `policies.ratelimit.QuotaViolation`. Is this a bug, and what actually
> defines a separate counter?

## Initial Evidence
HTTP 500 with `{"fault":{"detail":{"errorcode":"policies.ratelimit.QuotaViolation"}}}`,
verified at `error-codes.md` line 42, sourced to the quota policy page. One policy
element named `QuotaLimitPolicy` attached as a `<Step>` in three flows. No API product
quota settings in play. The rejections cluster on one client id.
