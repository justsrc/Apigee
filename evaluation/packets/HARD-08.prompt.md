You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case HARD-08

## Initial Support Ticket
> Our monthly quota is rejecting requests earlier than the configured limit. With a limit
> of 10,000 we are being cut off around 7,000. The counter in analytics agrees with the
> policy. Is the counter double counting?

## Initial Evidence
The Quota policy is named `reports-quota`, is `<Allow count="10000"/>` with
`<TimeUnit>month</TimeUnit>`, and it is attached twice: once to the ProxyEndpoint PreFlow
and once to the ProxyEndpoint Request flow. `<MessageWeight ref="report.units"/>` is set
on the policy. Counters are configured synchronously.
