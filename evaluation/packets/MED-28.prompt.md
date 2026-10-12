You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-28: Provisioning over mutual TLS succeeds, then the tool fails its own verification

## Initial Support Ticket
> We provision a private cloud tenant with mutual TLS. The proxies and key value maps are created
> fine, and then the tool reports HTTP 400 during its verification step and the command fails. We
> are told to check deployment status. Is the provision actually broken?

## Initial Evidence
Provisioning with a client certificate, key and CA succeeds for the proxy resources and the key
value map. The tool then calls its own verification endpoints and gets 400. External calls with
the same certificate succeed, so the chain is trusted at the operating system level.
