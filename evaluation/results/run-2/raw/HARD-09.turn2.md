# Follow-up: it is the failure counter, not the backend

**Assessment, and this one I am confident about.** A single server under a
`<LoadBalancer>` with `<MaxFailures>5</MaxFailures>` gets discarded after five consecutive
failures, and with nothing else in the pool there is nothing left to send to. That is why a
healthy backend is serving 200s at the same moment your proxy returns 503 with no backend
step in the trace. The proxy has stopped calling it.

The ServiceCallout changes the status code, not the mechanism. A callout that finds no usable
server faults the policy, and a policy fault is a 500 at the caller. Same cause, different
surface, which is exactly why "does it fail as 503 or 500" was not the discriminator.

**Still unresolved.** I am not going to tell you the counter is the whole story, because the
2% that succeeded does not fit it. A pool with no server left predicts 100%. That gap is
small and it is real, and it is the one thing in this case I cannot explain from the
evidence I have. It may be the requests that completed before the fifth consecutive failure
or before a counter reset, and your monitoring should be able to tell you which.

**Product.** Still assuming Apigee X or hybrid. Version matters for the element reference and
I do not have it.

## What the new evidence settles

- The backend is healthy and was serving successfully while your proxy was returning 503. So
  this is not a backend fault and nothing the backend team does next will change it.
- The failure counter is the common mechanism across both policies, because both use the same
  single-server shape with `<MaxFailures>5</MaxFailures>`.
- The 503 versus 500 split is a symptom of *where* in the flow the empty pool is hit, not
  evidence of two problems.

## What remains open

| Hypothesis | Supporting | Contradicting | Missing | Test | Status |
| --- | --- | --- | --- | --- | --- |
| Server removed from rotation after 5 consecutive failures | both policies fail continuously, backend healthy, no backend step time | 2% of requests still succeed | Message Processor logs from 11:00 | read the target-server removal message in the runtime logs | strongly supported |
| The 2% are requests that completed before the threshold, or after a counter reset | small minority, consistent with a race at the threshold | none yet | response status by minute since 11:00 | plot it | plausible, unverified |
| Something else intermittently returns a server to the pool | 2% success | none | whether the successes cluster in time | same plot | cannot assess |

## What to do

1. Read the Message Processor logs for 11:00 and find where the target server is removed from
   rotation. That is the single artifact that turns the first row from strongly supported to
   confirmed, and it costs one log pull.
2. Restore service deliberately: redeploy the revision, or restart the routers, to return the
   server to the pool. Disruptive, so authorise it, and expect brief traffic movement. This is
   mitigation. Whatever produced five consecutive failures is still there and will do it again.
3. Then fix the shape, which is the actual defect in the design. Two options, and the choice
   is yours:
   - `<MaxFailures>0</MaxFailures>` on both policies, so a failing server is retried instead
     of discarded. Your requests pay the backend's timeout instead of an immediate 503. Right
     if you would rather fail slowly and visibly than fail fast and mysteriously.
   - Give both `<LoadBalancer>` elements more than one `<Server>`, so removing one still
     leaves somewhere to send the request. Right if you have a second address for the same
     service, for example a second instance or region.
   What I would not do is leave a single server with a failure counter and no health monitor.
   With one server, the counter has nothing to fail over to.
4. While you are in there, work out what the five failures were. The backend says it was
   healthy at 11:15, which does not tell you what it was doing at 11:00, and that is the
   actual incident.

## How to confirm

After the change, confirm the success rate from every Message Processor, not from one
request, and re-check it after more than five consecutive requests so you know the counter is
not quietly re-arming. A single 200 after a restart proves reachability once, not a healthy
pool.

## What I still could not determine

Whether a removed target server returns to the pool on its own. I have read two official pages
that contradict each other on this: one says Apigee re-checks and returns the server, the
other says it is not returned and the proxy must be redeployed. I have not established which
is current, so I have built the plan to work either way. If you have a low-traffic window,
leaving it alone for longer than five minutes is the cheapest way to find out which page is
right, and it costs you a redeploy later rather than an outage now.