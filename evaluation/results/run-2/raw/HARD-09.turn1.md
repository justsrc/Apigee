# 503s with no backend step time, on a single-server LoadBalancer

**Assessment.** Requests are not reaching your backend. A trace with no time spent on any
backend step means the proxy rejected or discarded the request before it left for the target,
so the backend team and your monitoring are both telling you the truth about a service that
the proxy has stopped calling. `<MaxFailures>5</MaxFailures>` with no health monitor is the
mechanism I would look at first.

**Two things I want to flag before you act.**

The first is the 2% that still succeed. I am not going to write you a clean story that
accounts for 98% and ignores the other 2%, because with a single `<Server>` in the
`<LoadBalancer>`, "the server was removed from rotation" predicts total failure, not 98%. So
either the successes are all from before the failure threshold was reached, or something
else is intermittently getting through. That distinction matters for the fix, and your
monitoring is the cheapest way to settle it.

The second is that I am not confident about recovery. I have seen the load-balancing
documentation and the antipatterns documentation disagree on what happens to a server that
has been removed under `<MaxFailures>`, and I have not established which is current. One says
the server is re-checked on an interval and returned, the other says it is not returned and
the proxy must be redeployed. I am not going to pick the one that suits the fix I want to
recommend. That is a documentation conflict I would want resolved before telling you to wait
it out.

**Product.** No Edge for Private Cloud markers, so I am assuming Apigee X or hybrid. If it is
a hybrid runtime, tell me the version.

## Established

- Response status 503 on roughly 98% of requests, with a minority still succeeding.
- A failing request shows no time spent on any backend step.
- One target server, `pricing-primary`, under `<LoadBalancer>`.
- `<MaxFailures>` is 5 and no health monitor is configured.
- No redeploy and no config change since the failures started.

## Assumed

- That "no backend step time" means the request did not leave the proxy. If your trace tool
  omits steps that fail to schedule, that reading breaks and I would want a raw trace.

## Ledger

| Hypothesis | Supporting | Contradicting | Missing | Test | Status |
| --- | --- | --- | --- | --- | --- |
| `pricing-primary` was removed from rotation after 5 failures and the LoadBalancer has no server left | no backend step time; `<MaxFailures>` set; no health monitor to reintroduce it | 2% still succeed | whether the 2% cluster before or after 11:00 | plot response status by minute since 11:00 | strongly supported |
| Requests are failing before the LoadBalancer is consulted | 503 without a backend step | `<LoadBalancer>` with an empty pool also produces exactly this | step trace from the ProxyEndpoint | confirm which ProxyEndpoint step produces the 503 | plausible, unverified |
| A separate Apigee-side fault, unrelated to the target | no change since 11:00 argues against a config cause | the target config is exactly the shape this antipattern describes | router or runtime logs for 11:00 | read the Message Processor logs for 11:00 | disfavoured |

## What to do now

1. Read-only first: pull the router and Message Processor logs for 11:00 and look for the
   target server being taken out of rotation. That tells you when it happened, which is the
   fact every later decision depends on.
2. Check whether the succeeding 2% are timestamped before or after 11:00. If they are spread
   across the window, the pool is not simply empty and I have the wrong mechanism.
3. When you are ready to change something: redeploy the revision, or restart the routers, to
   put `pricing-primary` back into the pool. That is disruptive, so authorise it and expect
   brief traffic movement. It is also a mitigation, not a fix, and I want to be plain about
   that: whatever made the server fail 5 times is still there.
4. Separately, and this is the part that stops the recurrence: decide whether you want a
   single-server `<LoadBalancer>` with a failure counter and no health monitor at all. With
   one server, taking it out leaves nothing behind it. Either give it a second target or set
   `<MaxFailures>0</MaxFailures>` so a failing server is retried rather than discarded, and
   accept the latency of failures while it is down. Which of those you want depends on
   whether the backend has a failover you can point at, which I do not know yet.

## How to confirm

After the change, confirm the success rate from every Message Processor, not from one
request. A single successful call after a router restart tells you the server was reachable
once, which is not the same as the pool being healthy.

## What I could not determine

Whether a removed target server comes back on its own or needs a redeploy, because the two
official pages I have read contradict each other and I did not resolve which is current. And
what `pricing-primary` was doing before it accumulated 5 failures, which is the actual
incident and which none of the above fixes.