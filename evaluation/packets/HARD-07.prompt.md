You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# HARD-07: Certificate rotation, and the question that decides the path

## Initial Support Ticket
> Our certificate expires in 10 days. We want to upload the new cert and keep the same
> keystore so nothing has to change in our proxies. What is the API call?

## Initial Evidence
The user wants to replace the certificate in an existing keystore without changing proxy
configuration. The ticket does not say whether the proxy names the store through a
`ref://` reference or directly, and that omission decides everything downstream.
