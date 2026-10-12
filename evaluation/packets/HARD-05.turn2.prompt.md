You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case HARD-05

The customer has replied with more information.

## Diagnostic Evidence
API Monitoring traces show the failing requests all report revision 22 as the serving
revision, while successful requests report revision 21. The trace does not name an
environment. The failing responses carry:

```json
{"fault": {"detail": {"errorcode": "messaging.adaptors.http.flow.UnexpectedEOFAtTarget"}}}
```

The deployment list for `prod` shows revision 21 in `READY` after the rollback. A second
environment, `prod-b`, is a member of the same environment group, serves hostname
`api.example.com` with the same base path, and its deployment list shows revision 22 in
`READY`.

An operator has already tried deploying revision 21 to `prod-b` in order to finish the
rollback. The command was rejected, and they moved on without reading the message.
