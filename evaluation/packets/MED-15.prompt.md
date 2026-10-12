You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-15

## Initial Support Ticket
> Our Java callout started failing on some requests only. It works on the first request of
> an hour and fails on the rest. We did not change the jar.

## Initial Evidence
The trace shows a Java callout step failing. Deployment succeeded. The failure payload is:

```json
{"fault":{"detail":{"errorcode":"steps.javacallout.ExecutionError"}}}
```

The `faultstring` is the generic `Failed to execute JavaCallout. [policy_name]`, which
carries no Java detail.
