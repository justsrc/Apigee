You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-44: Headers that were removed, then put back, and are still pinned

The customer has replied with more information.

## Diagnostic Evidence
The org is on a release in the affected window where the headers stopped being sent when
Distributed Trace is disabled. A sibling org on the same version that was pinned to the old
behaviour still receives the headers.
