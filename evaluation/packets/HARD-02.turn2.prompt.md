You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# HARD-02: The config and the logs disagree

The customer has replied with more information.

## Diagnostic Evidence
Checking the deployment state for the `prod` environment shows revision 19 as `READY` and
revision 20 still in `PROGRESSING`. API Monitoring traces show the executing revision as
19. The deployment record for revision 20 carries a start timestamp, and what it says is
not supplied, which is what keeps the two accounts apart rather than resolving them.
