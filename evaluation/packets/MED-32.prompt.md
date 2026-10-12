You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-32: Six requests admitted where three per minute is configured

## Initial Support Ticket
> We have an Apigee X organisation with six message processors. A SpikeArrest policy on our
> target endpoint is configured as:
>
> ```xml
> <SpikeArrest async="false" continueOnError="false" enabled="true" name="spikearrest-1">
>   <Identifier ref="request.header.some-header-name"/>
>   <MessageWeight ref="request.header.weight"/>
>   <Rate>3pm</Rate>
> </SpikeArrest>
> ```
>
> The documentation says 3 per minute means one request every 20 seconds. In production we
> are seeing six successful requests inside a 20 second window and then rejections. That is
> six requests where we asked for one. Is there any way to synchronise SpikeArrest across
> the message processors? We were told ConcurrentRateLimit would help and it does not.

## Initial Evidence
Six successful calls inside 20 seconds, then rejections, on a proxy with
`<Rate>3pm</Rate>`. The rejections carry
`{"fault":{"detail":{"errorcode":"policies.ratelimit.SpikeArrestViolation"}}}` with HTTP
429, which the local error index confirms at `error-codes.md` line 43, sourced to the
spike-arrest policy page. No `<UseEffectiveCount>` element is present in the policy.
