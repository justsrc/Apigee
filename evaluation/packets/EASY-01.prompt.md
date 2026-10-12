You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case EASY-01

## Initial Support Ticket
> We cannot deploy our proxy any more. It worked last week. The API call to save the
> revision fails and the UI says "Error Saving Revision 4". Nothing in our flow config
> changed that I can see. What is it complaining about?

## Initial Evidence
The proxy bundle contains this Quota policy:

```xml
<Quota name="OrdersPerMinute" type="rollingwindow">
  <Interval>0.5</Interval>
  <TimeUnit>minute</TimeUnit>
</Quota>
```

The save call returns HTTP 400. The body names `InvalidQuotaInterval`. No requests are
being served, because the revision was never saved. The previous revision is still
serving traffic normally.
