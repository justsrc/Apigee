You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case EASY-07

## Initial Support Ticket
> Our partner updated their signing library and now our API returns 401 for their tokens.
> The tokens look structurally correct. Their team says nothing changed in our config.

## Initial Evidence
```json
  {
    "fault": {
      "detail": {
        "errorcode": "steps.jws.AlgorithmMismatch"
      }
    }
  }
```

HTTP response status 401.

Partner tokens have an `alg` header of `PS256`. The VerifyJWS policy is configured with
`<Algorithm>RS256</Algorithm>`.
