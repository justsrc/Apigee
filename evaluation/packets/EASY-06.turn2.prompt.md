You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# EASY-06: BasicAuthentication cannot resolve its source variable

The customer has replied with more information.

## Diagnostic Evidence
The user supplies the full body:

```
Unresolved variable : encodedBasicAuth
```

The proxy bundle shows two steps in the same flow, in this order:

```xml
<Flow name="partner-auth">
  <Request>
    <Step><Name>DecodeBasicAuth</Name></Step>
    <Step><Name>BuildBasicAuthVariable</Name></Step>
  </Request>
</Flow>
```

`BuildBasicAuthVariable` is the step that assigns `encodedBasicAuth`.
