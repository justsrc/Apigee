You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-10

The customer has replied with more information.

## Diagnostic Evidence
A trace of the failing proxy has no `VerifyAccessToken` step at all. The first token policy
on that path is `GetOAuthV2Info`, and the failure occurs there. The working proxy's trace
shows `VerifyAccessToken` running before the info policies, and failing.
