You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-38

## Initial Support Ticket
> We are integrating a new client against our Apigee proxy and every call fails with:
>
> ```json
> {"fault":{"faultstring":"Invalid API call as no apiproduct match found",
>   "detail":{"errorcode":"steps.oauth.v2.InvalidAPICallAsNoApiProductMatchFound"}}}
> ```
>
> HTTP 401. The access token is issued by us, it is not expired, and the client is sending
> it correctly. We have read that the fix is to associate the API bundle with an API
> product, but our proxy is already in a product and the developer app is already
> associated with a product. Can you confirm which one is wrong?

## Initial Evidence
HTTP 401, `steps.oauth.v2.InvalidAPICallAsNoApiProductMatchFound`, verified at
`error-codes.md` line 132, sourced to the delete-oauth-v2-info policy page. The token
validates against the token endpoint. The proxy appears in at least one API product and
the developer app appears in at least one API product.

Note a discrepancy worth surfacing to the agent: the customer quotes a
`keymanagement.service.`-prefixed variant, which is the Apigee Edge-era string. The current
index carries the `steps.oauth.v2.`-prefixed form.
