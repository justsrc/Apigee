You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# EASY-01: Quota policy rejects the revision over a fractional interval

The customer has replied with more information.

## Diagnostic Evidence
If asked what the deployment error message says in full, the user supplies:

```
Error Saving Revision 4
InvalidQuotaInterval: The quota interval is not a valid integer.
```

If asked whether `<Interval>` was changed recently, the user says it was set to `0.5`
about six weeks ago and the previous revision saved fine with the same value, which
implies an earlier revision was created when the policy differed.
