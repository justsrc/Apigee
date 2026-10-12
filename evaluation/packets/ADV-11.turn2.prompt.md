You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# ADV-11: Paraphrased case with a misleading title

The customer has replied with more information.

## Diagnostic Evidence
Checking the environment group attachments for the organization shows the environment is
not currently a member of any group. The only attachment record returned for it carries
a `createdAt` of eight months earlier, and no attachment for this environment has been
deleted or replaced since. The deployment record shows the rollback created a new revision
yesterday.
