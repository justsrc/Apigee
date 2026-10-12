You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# EASY-10: HMAC policy missing a required element

The customer has replied with more information.

## Diagnostic Evidence
The deployed bundle contains:

```xml
<HMAC name="VerifySignature">
  <Algorithm>SHA256</Algorithm>
</HMAC>
```

There is no `<SecretKey>` and no secret reference of any kind, and there is no
`<VerificationValue>`. The team updated an external secret manager, and a templating step
that previously injected the secret element now renders nothing.
