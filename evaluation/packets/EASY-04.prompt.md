You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case EASY-04

## Initial Support Ticket
> Since this morning our office gets a 403 from the orders API. Nothing changed in the
> proxy. Home wifi works fine. What is blocking us?

## Initial Evidence
```json
  {
    "fault": {
      "detail": {
        "errorcode": "accesscontrol.IPDeniedAccess"
      },
      "faultstring": "Access denied for IP address 203.0.113.47"
    }
  }
```

HTTP response status 403.

The request from the office network fails. The same credentials from home succeed.
