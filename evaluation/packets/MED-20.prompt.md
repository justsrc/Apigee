You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-20

## Initial Support Ticket
> We raised `io.timeout.millis` from 5000 to 15000 on our search proxy and redeployed. Some
> requests still time out at 5 seconds as if the old value is in force. Others behave as expected.
> The deployment reported success. We are on hybrid 1.15.5.

## Initial Evidence
The deployment reported success. Behaviour is inconsistent across requests. The upstream
service itself is healthy and responds within 4 seconds. No proxy configuration is included.
