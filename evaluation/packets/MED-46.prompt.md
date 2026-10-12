You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-46

## Initial Support Ticket
> We turned on certificate checking on our target endpoint because we wanted to stop accepting
> expired certs. Now that backend returns 502 Bad Gateway. The host is up, it answers on 443, and
> the same URL works from a browser. The gateway cannot reach it.

## Initial Evidence
The target `<SSLInfo>` block contains `<Enforce>true</Enforce>`. The target responds to `502`. The
target is reachable and healthy by every other measure. The status code is 502 rather than the
503 that would suggest a target certificate problem.
