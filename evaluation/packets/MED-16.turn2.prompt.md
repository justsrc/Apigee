You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-16

The customer has replied with more information.

## Diagnostic Evidence
A trace of the failing request shows the request entering the flow whose `<Condition>` is
`proxy.pathsuffix == "/oauth/authorizationcode"`, not the `"/oauth/accesstoken"` flow. The
proxy was deployed with a deployment base path that did not match the base path in the
bundle, so the request path resolved into the wrong flow.
