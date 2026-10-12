You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case EASY-08

The customer has replied with more information.

## Diagnostic Evidence
An API Monitoring trace shows the step that failed. Step names below are abbreviated
to policy types, since real step names are whatever the team named each policy:

```
VerifyAccessToken        OK       2ms
Quota policy (token count)  OK       11ms
SpikeArrest policy       FAILED   0ms  policies.ratelimit.InvalidMessageWeight
```

The failing step is the SpikeArrest policy.
