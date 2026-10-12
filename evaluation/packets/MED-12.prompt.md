You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-12: Service callout times out and takes the request with it

## Initial Support Ticket
> Our enrichment callout started timing out for about 1% of requests. The enrichment
> service is fast. We raised its timeout and it did not help.

## Initial Evidence
A ServiceCallout policy with a configured timeout. Roughly 1% of requests return 500. The
enrichment service's own p95 is under 50ms.
