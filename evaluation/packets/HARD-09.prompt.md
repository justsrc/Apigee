You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case HARD-09

## Initial Support Ticket
> Our pricing API has been returning errors continuously since about 11:00. The backend
> team confirmed at 11:15 that their node is healthy and serving normally. Our monitoring
> agrees. We have not redeployed and there is no config change. Please advise urgently.

## Initial Evidence
Response status is 503 for roughly 98% of requests, with a small number still succeeding.
A trace of a failing request shows no time spent on any backend step.

The target endpoint:

```xml
<HTTPTargetConnection>
  <LoadBalancer>
    <Algorithm>RoundRobin</Algorithm>
    <Server name="pricing-primary" />
    <MaxFailures>5</MaxFailures>
  </LoadBalancer>
</HTTPTargetConnection>
```
