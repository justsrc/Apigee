You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case EASY-06

## Initial Support Ticket
> Our partner endpoint started returning 500 for every request. The body mentions an
> unresolved variable. We did not touch the BasicAuthentication policy file itself, though
> we did do some cleanup in that flow last week.

## Initial Evidence
```json
  {
    "fault": {
      "detail": {
        "errorcode": "steps.basicauthentication.UnresolvedVariable"
      }
    }
  }
```

HTTP response status 500.

The policy:

```xml
<BasicAuthentication name="DecodeBasicAuth">
  <Operation>Decode</Operation>
  <Source>encodedBasicAuth</Source>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
</BasicAuthentication>
```
