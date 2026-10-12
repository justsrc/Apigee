You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case EASY-05

## Initial Support Ticket
> A JavaScript policy we have had for a year suddenly fails with a security error. It
> just reads a header and sets a variable. Nothing changed in the script. Did a runtime
> update break it?

## Initial Evidence
```json
  {
    "fault": {
      "detail": {
        "errorcode": "steps.javascript.ScriptSecurityError"
      }
    }
  }
```

HTTP response status 500.

The script:

```javascript
var token = context.getVariable("request.header.computeToken");
context.setVariable("token", loadCredential(token));
```
