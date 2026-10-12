You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# EASY-03: FlowCallout cannot find the shared flow

## Initial Support Ticket
> After we refactored the token validation into a shared flow, every request fails with a
> 500. The shared flow is in the same bundle as the proxy. What did we get wrong?

## Initial Evidence
```json
  {
    "fault": {
      "detail": {
        "errorcode": "flow.SharedFlowNotFound"
      }
    }
  }
```

HTTP response status 500.

The proxy bundle contains `policies/validate-token.xml` attached via FlowCallout, and
`sharedflows/token-validation/` with its own policies.
