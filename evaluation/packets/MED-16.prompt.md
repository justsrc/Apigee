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

## Initial Support Ticket
> Our authorization code flow is broken. The token endpoint returns
> `{"ErrorCode" : "invalid_request", "Error" :"The request is missing a required parameter :
> response_type"}`. We are calling the token endpoint, not the authorize endpoint, so
> `response_type` should not apply. Please confirm our proxy is misconfigured.

## Initial Evidence
The client POSTs to the documented token path with `grant_type=authorization_code`, `code`,
and `redirect_uri`. The proxy bundle is the vendor's own OAuth sample. The authorize leg
works: a code is issued and returned. Nothing in the bundle changed; the proxy was redeployed
last week and the token leg worked before that.
