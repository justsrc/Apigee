You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case EASY-12

## Initial Support Ticket
> Our bulk token revocation endpoint started returning 500. We call it with a
> "revoke everything issued before this timestamp" argument. The same call worked last
> month. Nothing about our clocks changed.

## Initial Evidence
```json
  {
    "fault": {
      "detail": {
        "errorcode": "steps.oauth.v2.InvalidEarlyTimestamp"
      }
    }
  }
```

HTTP response status 500.

The policy:

```xml
<RevokeOAuthV2 name="RevokeOld">
  <RevokeBeforeTimestamp ref="request.queryparam.revoke_since_timestamp"/>
</RevokeOAuthV2>
```
