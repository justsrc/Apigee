You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-05

## Initial Support Ticket
> We rotate an API endpoint URL in a key-value map about once a week. After the update,
> requests fail from some regions for a few minutes and then recover. Is the key-value map
> corrupt?

## Initial Evidence
The new value is written at runtime by a `PUT` operation in a KeyValueMapOperations policy,
with `<ExpiryTimeInSecs>` set to 60 on the policy. A policy reads the value at runtime. Some
requests receive an empty or stale value immediately after the update.
