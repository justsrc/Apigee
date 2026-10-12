You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-07

## Initial Support Ticket
> We created a new environment in our hybrid install and deployed our proxy to it. The
> deployment call succeeded. Requests to the new environment hostname return 404. The
> other environments on the same cluster are fine. Please advise.

## Initial Evidence
The deployment list shows the revision deployed to `prod2`. The new environment was
created in the same Google Cloud project as the existing ones. Nothing was redeployed
elsewhere.
