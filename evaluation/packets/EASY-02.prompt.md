You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case EASY-02

## Initial Support Ticket
> Our orders API started returning 500 to about 3% of requests. The error body mentions
> a quota interval reference. We did not change the proxy. Did something get deployed by
> mistake?

## Initial Evidence
A response body:

```json
  {
    "fault": {
      "detail": {
        "errorcode": "policies.ratelimit.FailedToResolveQuotaIntervalReference"
      },
      "faultstring": "Unable to resolve interval reference"
    }
  }
```

HTTP response status 500.

Only about 3% of requests fail. Requests on a different proxy that shares the same
backend are unaffected.
