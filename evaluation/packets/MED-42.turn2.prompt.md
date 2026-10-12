You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-42: The proxy limit that depends on how long your base paths are

The customer has replied with more information.

## Diagnostic Evidence
The failing environment group's base paths exceed 15 characters. The working group does not. The
environment containing the failing group has a total base path count above 1000, counting base
paths rather than revisions.
