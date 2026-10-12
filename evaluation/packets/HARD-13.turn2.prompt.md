You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case HARD-13

The customer has replied with more information.

## Diagnostic Evidence
A trace for a failing request shows the failure at `AM-VerifyToken`, carrying:

```json
{"fault": {"detail": {"errorcode": "steps.jwt.TokenExpired"}}}
```

A trace for a successful request shows the same step succeeding. Failing requests correlate
with tokens whose `exp`, as recorded in the minting service's own log line, falls within
the next 30 seconds. The correlation holds regardless of client or endpoint. The VerifyJWT
policy has no `<TimeAllowance>` element configured.
