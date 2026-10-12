You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# HARD-11: A timeout that is not the timeout

## Initial Support Ticket
> We get 504s from the proxy. We raised the target timeout to 30 seconds and they
> still happen after exactly 10 seconds. Our config says 30.

## Initial Evidence
504 responses arrive consistently at about 10 seconds. The target endpoint is configured
as `<Property name="io.timeout.millis">30000</Property>`, which is the setting the team
means when they say "the target timeout".
