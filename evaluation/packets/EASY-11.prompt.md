You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# EASY-11: Unsupported TimeUnit blocks the revision

## Initial Support Ticket
> Deployment rejected again after our config change. The error says the quota time unit
> is invalid. The developer wrote `minutes` because that reads better. Is that the
> problem?

## Initial Evidence
HTTP 400 on save, error name `InvalidQuotaTimeUnit`. The policy:

```xml
<Quota name="PerDay">
  <Interval>1</Interval>
  <TimeUnit>minutes</TimeUnit>
</Quota>
```
