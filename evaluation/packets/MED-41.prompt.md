You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-41: "Operation group limit of 51 exceeded in Operation Config"

## Initial Support Ticket
> Our team tried to add a few more paths to an existing API product in the console. The save
> failed with `Operation group limit of 51 exceeded in Operation Config`. We did not change any
> proxy. Is our proxy misconfigured?

## Initial Evidence
An API product in one environment holds 50 resource paths. Adding a 51st fails on save. No proxy
was edited, no revision was deployed, and no runtime error exists because nothing reached the
runtime.
