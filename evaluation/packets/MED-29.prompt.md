You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-29: The same TLS error, two different causes, and the accepted fix works for one of them

## Initial Support Ticket
> Our Apigee deployment tool cannot connect to the runtime. It fails on TLS verification. We need
> to deploy to a private instance behind our corporate firewall. Someone told us there is a flag to
> skip certificate checking. It did not help.

## Initial Evidence
The tool fails on the outbound connection to the management endpoint. One variant of the error
names a leaf signature that cannot be verified. Another variant reports that the first certificate
in the chain cannot be verified. The host is reachable, credentials are accepted elsewhere, and the
same tool works from a network outside the corporate perimeter.
