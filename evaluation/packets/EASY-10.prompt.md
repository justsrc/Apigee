You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case EASY-10

## Initial Support Ticket
> The deployment of our webhook receiver proxy is being rejected with an HMAC error. The
> same proxy has been running for months. We updated the secret in our secret manager and
> re-ran the bundle renderer that pulls it into the policy. We did not hand-edit the
> policy itself.

## Initial Evidence
The save returns HTTP 400. The body names `steps.hmac.MissingConfigurationElement`.
Requests to the already-deployed revision still work.
