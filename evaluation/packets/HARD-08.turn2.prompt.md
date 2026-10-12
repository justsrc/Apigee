You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case HARD-08

The customer has replied with more information.

## Diagnostic Evidence
Replaying one request that does not carry `x-tier` moves the counter by exactly that
request's weight. Replaying one that carries `x-tier: enterprise` moves it by twice the
weight. The counter reads the same name and the same value in both cases, so there is one
counter and not two.

Reading the ProxyEndpoint XML shows why the two replays differ: the PreFlow attachment
carries `<Condition>request.header.x-tier == "enterprise"</Condition>`, and the Request
flow attachment carries none.

In the window that just closed, the proxy admitted 7,000 requests: 5,000 with
`report.units` set to 1 and 2,000 with it set to 2. Of the 7,000, exactly 1,000 carried
`x-tier: enterprise`, and all 1,000 of those are weight-1 requests. The counter ended the
window at 10,000.
