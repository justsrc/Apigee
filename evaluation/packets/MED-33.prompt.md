You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-33: Rate of 5 per minute, but the third call in ten seconds is rejected

## Initial Support Ticket
> We have a SpikeArrest policy on our request PreFlow:
>
> ```xml
> <SpikeArrest enabled="true" continueOnError="true" async="false" name="SpikeArrest">
>   <Rate>5pm</Rate>
>   <MessageWeight ref="request.header.weight"/>
> </SpikeArrest>
> ```
>
> The documentation says that if we call more than five times in a minute the policy fails
> after the fifth call. We tested by sending ten calls in under ten seconds. The policy
> accepted the first two calls and rejected everything after that. We are not calling more
> than five times a minute. Our environment has two message processors and two routers. Is
> that the cause?

## Initial Evidence
Two successful calls then rejections, for a configured `5pm`. Rejections carry
`policies.ratelimit.SpikeArrestViolation`, HTTP 429, verified at `error-codes.md` line 43.
The policy has a `<MessageWeight>` bound to a request header, which is a second live
variable that has not been examined. `continueOnError` is `true`, which is unusual for a
throttling policy and is not discussed.
