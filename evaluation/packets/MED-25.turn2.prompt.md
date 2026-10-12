You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-25

The customer has replied with more information.

## Diagnostic Evidence
```terminal
grep -n -B3 -A8 "<Quota name=" apiproxy/policies/*/policy.xml
```

Every attachment carries the same `<Quota name="...">` reference. The surrounding `<Step>` and
`<Condition>` elements differ, and the attachments span two `<TargetEndpoint>` definitions as well
as several flows within one endpoint.
