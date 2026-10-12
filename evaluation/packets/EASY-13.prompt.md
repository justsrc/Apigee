You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case EASY-13

## Initial Support Ticket
> Our identity provider rotated keys last week. Most of our traffic is fine but some
> tenants now get 401. The failing tokens look perfectly normal.

## Initial Evidence
401 responses on some tenants only. A decoded failing token header contains `alg` and
`typ` but no `kid`. A working token from another tenant has `kid`.
