You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-29

The customer has replied with more information.

## Diagnostic Evidence
```terminal
# from the affected host, compare the certificate the client actually receives
openssl s_client -connect mgmt.example.internal:443 -servername mgmt.example.internal </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -ext subjectAltName
```

In the working case the issuer is the organisation's own internal CA and the subject alternative
names match the hostname being requested. In the broken case the issuer is the corporate proxy,
the subject names the proxy, and there is an additional certificate in the chain that is not part
of the server's own PKI. The tool also works from a host with no route through the proxy, which
localises the fault to the path rather than the destination.
