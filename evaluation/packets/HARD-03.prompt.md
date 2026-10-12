You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# HARD-03: mTLS fails in one direction only, after a keystore change

## Initial Support Ticket
> After we rotated our client certificate, southbound calls to the backend started failing
> with a TLS error. Northbound client connections still work. We followed the rotation
> runbook and the new certificate uploaded without complaint.

## Initial Evidence
Southbound fails, northbound works. A new keystore was created and the new client
certificate uploaded into it. The failing responses are Apigee-generated, not backend
bodies:

```json
{"fault": {"detail": {"errorcode": "messaging.adaptors.http.flow.SslHandshakeFailed"}}}
```

The faultstring is what distinguishes a handshake rejection from a store or alias that
cannot be resolved, so it is worth reading before concluding anything.
