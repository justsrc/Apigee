You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# HARD-15: It looks like a product defect

The customer has replied with more information.

## Diagnostic Evidence
The sequence places an AssignMessage policy that sets `target.url` on the ProxyEndpoint
before the target endpoint. The documented restriction is that `target.url` is initialized
in the TargetEndpoint and cannot be set from a ProxyEndpoint policy. The update is
coincidental.
