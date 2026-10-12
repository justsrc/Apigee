You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# EASY-08: InvalidMessageWeight does not tell you which policy failed

## Initial Support Ticket
> We get intermittent 500s from our LLM-backed endpoint, roughly when traffic is heavy.
> The errorcode is the same every time. We have both a Quota and a SpikeArrest policy in
> that proxy. Which one is it?

## Initial Evidence
```json
  {
    "fault": {
      "detail": {
        "errorcode": "policies.ratelimit.InvalidMessageWeight"
      }
    }
  }
```

HTTP response status 500.

The proxy has a Quota policy and a SpikeArrest policy. The LLM token weight is set by a
flow variable read from the request body.
