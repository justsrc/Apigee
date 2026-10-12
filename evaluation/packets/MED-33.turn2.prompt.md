You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-33: Rate of 5 per minute, but the third call in ten seconds is rejected

The customer has replied with more information.

## Diagnostic Evidence
```xml
<SpikeArrest enabled="true" continueOnError="true" async="false" name="SpikeArrest">
  <Rate>5pm</Rate>
  <MessageWeight ref="request.header.weight"/>
</SpikeArrest>
```

A debug trace shows `request.header.weight` is **absent** on the client requests. With the
reference unset the weight falls back to 1, so weight is not the cause here, and the
trace shows two distinct message processors serving the two successful requests.
