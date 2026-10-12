You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case HARD-11

The customer has replied with more information.

## Diagnostic Evidence
The ProxyEndpoint carries a proxy-level budget that nobody remembers adding:

```xml
<HTTPProxyConnection>
  <Properties>
    <Property name="api.timeout">10000</Property>
  </Properties>
</HTTPProxyConnection>
```

The flow also contains a ServiceCallout whose `<Timeout>` is left at its documented default
of 55000 milliseconds. The failing responses carry:

```json
{"fault": {"detail": {"errorcode": "flow.APITimedOut"}}}
```
