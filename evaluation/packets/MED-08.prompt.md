You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-08

## Initial Support Ticket
> Our CA renewed our client certificates last week. Since then mutual TLS fails in both
> directions. We replaced the certificates exactly as before. What changed?

## Initial Evidence
Northbound client-to-Apigee fails and southbound Apigee-to-backend fails. The
configuration is unchanged. The new client certificates come from the same CA.
