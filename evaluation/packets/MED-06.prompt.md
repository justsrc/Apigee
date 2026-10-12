You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-06

## Initial Support Ticket
> p95 latency on our search API went from 180ms to 900ms overnight. No deploys. Can you
> tell us if it's Apigee?

## Initial Evidence
API Monitoring shows request latency up. No revision changes in the last week. The
upstream team has not yet been contacted.
