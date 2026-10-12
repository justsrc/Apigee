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
> We onboarded a second organization on our hybrid install and created its first
> environment. We deployed our proxy to it. The deployment call succeeded. Requests to
> the new environment hostname return 404. Our original organization is completely
> unaffected. Please advise.

## Initial Evidence
The deployment list for the new organization shows the revision deployed to `prod`. The
same proxy revision serves traffic normally in the original organization. Nothing was
redeployed there, and both organizations run in the same Google Cloud project.
