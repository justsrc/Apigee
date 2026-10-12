You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-25

## Initial Support Ticket
> The linter says our quota policy is used more than once and that we should not do that. Our
> traffic is being counted more than we expect. Should we remove the duplicates?

## Initial Evidence
Three shared flows and two target endpoints in one proxy all attach the same Quota policy. Each
attachment sits in a flow guarded by a `<Condition>`, and the flows and targets are mutually
exclusive at runtime, so exactly one of them executes per request.
