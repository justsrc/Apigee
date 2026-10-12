You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# EASY-02: Missing Interval produces a runtime 500, not a deploy failure

The customer has replied with more information.

## Diagnostic Evidence
On request, the proxy shows:

```xml
<Flow name="rate-limited">
  <Condition>(request.header.x-route == "v2")</Condition>
  <Quota name="PerMinute">
    <TimeUnit>minute</TimeUnit>
  </Quota>
</Flow>
```

The `<Interval>` element is absent. The flow carries a condition, which explains why only
some requests fail.
