You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-28

The customer has replied with more information.

## Diagnostic Evidence
```terminal
apigee-remote-service-cli provision --tls-cert client.crt --tls-key client.key --tls-ca ca.crt ...
# ... resources created ...
# verification: GET /certs -> 400, GET /products -> 400, POST /verifyApiKey -> 400
```

Two details from the tool's own behaviour. First, verification explicitly tolerates 401 and 500
and treats them as acceptable outcomes, because a missing secret or an invalid key legitimately
produces those. A 400 is outside the tolerated set, which means the request reached the gateway
and was rejected for a reason the tool never expected. Second, and more important: the command
returns the verification errors on SaaS and Edge for Private Cloud, but on hybrid it prints them
as a warning and exits successfully. The same 400 is a command failure in one runtime and a
non-event in another.
