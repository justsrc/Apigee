You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case EASY-09

## Initial Support Ticket
> Our XML endpoint returns 500 for some requests but works for most. The proxy converts
> the JSON body to XML before forwarding it. We did not change the policy, but we changed
> the upstream contract last week.

## Initial Evidence
A response body:

```json
  {
    "fault": {
      "detail": {
        "errorcode": "steps.jsontoxml.SourceUnavailable"
      }
    }
  }
```

HTTP response status 500.

The policy:

```xml
<JSONToXML name="BodyToXml">
  <Source>payload</Source>
  <OutputVariable>xmlBody</OutputVariable>
</JSONToXML>
```

A JavaScript policy earlier in the request flow runs only when a flow condition is true,
and that step is what assigns `payload`.
