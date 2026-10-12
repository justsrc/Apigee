You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case EASY-01

The customer has replied with more information.

## Diagnostic Evidence
If asked what the deployment error message says in full, the user supplies:

```
Error Saving Revision 4
InvalidQuotaInterval: The quota interval is not a valid integer.
```

If asked whether `<Interval>` was changed recently, the user says it was set to `0.5`
about six weeks ago. Whether a revision with that value was ever saved successfully is not
known and the customer is not sure: the deployed revision is three weeks older than the
edit, and nobody can recall whether the edit was ever deployed. If it was, then something
other than the documented rule was in effect at the time, and that is worth establishing
before drawing a conclusion.
