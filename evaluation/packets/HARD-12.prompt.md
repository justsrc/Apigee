You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# HARD-12: Nothing changed, but the numbers moved

## Initial Support Ticket
> Error rate on the checkout API went from 0.1% to 4% this morning. No deploys for three
> weeks. We did not change any proxy config. Please tell us what drifted.

## Initial Evidence
Error rate rose at 08:00. No proxy revision changes. No recent policy edits.
