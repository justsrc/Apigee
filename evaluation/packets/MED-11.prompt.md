You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-11: Everything works in test and fails in production

## Initial Support Ticket
> Identical proxy bundle, identical policies. Works in `test`, fails in `prod` with 500.
> We deploy the same artifact to both. Why would production behave differently?

## Initial Evidence
Same bundle deployed to both. Production returns 500 with an error body. Test returns 200
for the same request.
