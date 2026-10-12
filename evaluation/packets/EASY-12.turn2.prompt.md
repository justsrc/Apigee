You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case EASY-12

The customer has replied with more information.

## Diagnostic Evidence
The failing requests omit the `revoke_since_timestamp` query parameter, so the variable
ref resolves to an empty value and the policy is handed `0`. A captured failing request
confirms the parameter is absent. Requests that pass a normal millisecond timestamp
succeed.

A second, related failure mode is worth checking because it produces the same code: one
caller sends Unix **seconds** (for example `1767225600`) where the policy documents
milliseconds. Fed to the policy as milliseconds, that value is January 1970, which is also
before the bound.
