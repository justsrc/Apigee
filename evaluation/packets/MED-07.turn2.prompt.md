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

The customer has replied with more information.

## Diagnostic Evidence
The Message Processor log for the new organization contains no line of the form
`Switched to newer version N from version M`, which is the documented marker that the
MP applied a newer contract version. Reading the sync authorization for the new
organization returns no identities. The same service account that is registered for the
original organization holds the Apigee Synchronizer Manager role, so the identity was
available and was simply never registered against the new organization.
