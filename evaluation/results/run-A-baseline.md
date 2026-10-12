# Baseline run (unassisted)

## EASY-04

The 403 is coming from an AccessControl policy inside your proxy, not from the orders backend.

```json
"errorcode": "accesscontrol.IPDeniedAccess",
"faultstring": "Access denied for IP address 203.0.113.47"
```

That errorcode is only produced by the AccessControl policy, and only when the source address of the request matches an entry in the policy's IP range list. Home wifi works because it arrives from a different source address. Same credentials, different network, different answer. Your credentials and your backend are not involved.

Three things to check, in this order.

**1. What address is actually being evaluated.** AccessControl reads the source address from `request.header.X-Forwarded-For` by default, and there is a `<SourceAddress>` element on the policy that changes which request attribute it reads. If a corporate proxy, forward proxy, or CDN sits in front of Apigee, the address in the fault string may be your proxy's address rather than your office egress address. Send one request from the office with `-v` and compare the address in the fault against your office's real public egress IP.

One thing to sanity check: 203.0.113.0/24 is a documentation-only range reserved by RFC 5737, so it should not be a real office egress address. Either that value was anonymised when the ticket was filed, or something upstream is rewriting the header. Worth confirming which, because the second case changes the fix.

**2. What the policy says, and in which revision.** Look at the deployed bundle for the orders proxy and find the AccessControl step, usually in the pre-flow. Check the `<IPRange>` element. `type="blacklist"` with your office range in `<Exclude>` blocks the address. `type="whitelist"` blocks anything not in `<Include>`, which fails closed for any range you did not add. Either can produce this error, and the two need different fixes.

**3. Whether a deploy actually happened this morning.** "Nothing changed in the proxy" usually means nothing changed in version control, not that nothing was deployed. Check the deployment history for the orders proxy across every environment. A CI promotion, a manual deploy by someone else, or a bundle change that passed review can put a new IP list on a live revision. If the AccessControl policy has been unchanged for months, go back to point 1 and test the address assumption instead.

Fastest path to an answer: open a debug trace for the proxy, send one failing request from the office, and the failing step plus the address the policy evaluated will both be on the trace. Send me that trace and the AccessControl policy XML and I can point at the exact line that is rejecting you.

## EASY-08

Short answer: the errorcode cannot tell you which policy failed, and neither can I from what you have sent. Both Quota and SpikeArrest live in the `policies.ratelimit` namespace, so `policies.ratelimit.InvalidMessageWeight` is shared between them. What it does tell you is something more useful than which policy: neither policy rejected you for exceeding a limit. `InvalidMessageWeight` is raised when the message weight expression fails to resolve to an integer the policy can use. The limit itself was never evaluated.

That also explains the load correlation without needing the traffic story. Your weight comes from a flow variable read out of the request body, so it fails on requests whose body does not match the JSONPath you expect, not on requests that are merely numerous. Heavy traffic is when clients start sending different payload shapes, retries with different bodies, or a body that arrives empty or truncated. One of those is resolving to unset, empty, or a non-integer.

How to identify the policy, in order of speed:

1. Run a trace. Send a failing request with a debug trace open and read the failed step. The trace shows the policy step that threw, which is Quota or SpikeArrest by name. This is one step and it is conclusive.
2. If you cannot trace, temporarily comment out one policy and send the failing request. Crude, and not something to do in production traffic, but it works in a test environment.
3. Behaviourally, a limit being exceeded gives different errorcodes: `policies.ratelimit.QuotaExceeded` from Quota and `policies.ratelimit.SpikeArrested` from SpikeArrest. You are seeing neither, which again points at the weight expression rather than the limit.

While you are in there, print the variable. Put a `<AssignMessage>` or a debug header on the request ahead of the policy and look at what the expression actually produced on a failing request. Empty string, `null`, or something like `12.5` are the usual culprits. A weight also has to be a positive integer; zero, negative, and fractional values will not do.

The fix is to stop the expression from failing open or closed. Assign the weight with a `<DefaultValue>1</DefaultValue>` on the `<AssignVariable>` step so a body that does not parse counts as one request instead of erroring, and tighten the JSONPath so it matches the payloads your clients actually send. If a small percentage of requests legitimately carry no weight, defaulting to 1 is the right behaviour for both policies.

Send me the trace and the two policy XML snippets and I will confirm which one is throwing and what the weight expression is doing on the failing requests.

## MED-03

There are two separate behaviours in what you are describing, and I think they are being read as one problem.

**A 500 from the backend is not a failover trigger.** Apigee picks one target server for a request. If that server returns a response, that response is what the client gets, including a 500. Apigee does not retry the request against a second target server because the first one answered with 5xx. That is by design, so "requests return 500 when either node returns 500" is expected behaviour, not a broken configuration.

**A stopped node produces a 503 instead**, which is a connection-level failure to the target server. That is a different failure class and it is the one Apigee's built-in health handling is built around. So the question becomes which node your requests are actually going to, because your description says every request fails, which is not what round-robin across two live nodes would give you.

The decisive test is to prove where each request lands. Have each backend return a response header containing its own hostname, or check the backend access logs for the Apigee source addresses. If every office request hits the same node, then Apigee is not balancing at all, and the cause is in your target server configuration rather than in failover behaviour. Look at:

- Whether there is really one target server. If both "nodes" are addressed through a single hostname, a VIP, or a single `<TargetServer>` entry, Apigee sees one server and is not load balancing. This is the most common version of this ticket.
- `<Priority>` values on the `<TargetServer>` elements. Differing priorities make Apigee prefer one server and only fall back on failure, which looks exactly like "no load balancing" until you read the config.
- A circuit breaker. `<CircuitBreaker>` with a `<Threshold>` will take a target server out of rotation once it accumulates enough failures. If one node tripped it earlier and stayed out, all traffic lands on the other. Check the Message Processor logs for circuit breaker messages.

If the test shows traffic is genuinely split across both nodes and a 500 from one still reaches the client, then there is nothing to fix in the target server config, and you need failover somewhere else. Apigee has no built-in retry-on-5xx behaviour to enable. Your options are to put a health-checking load balancer in front of the two nodes so it never sends Apigee to a sick one, or to handle it in the proxy with a conditional flow that retries on a specific status and routes to a second target server.

I do not want to guess which of those you are in, so: make each node identify itself, send ten requests, and tell me what you see. That answer splits this cleanly and the rest is quick.

## HARD-06

I cannot diagnose this from the ticket, and I would rather say that than guess. With no status code, no error text, no product, and a time window of "yesterday", there are a dozen causes that fit and no way to tell them apart. What I need from you, in priority order:

**One failing request, captured exactly.** Run it with `curl -v` and paste the full output, status line, headers and body. Or the equivalent from your APM. If the request never reaches Apigee, that changes the whole investigation.

**The product and the org.** Apigee Edge for Cloud, Apigee X or hybrid, or Edge for Private Cloud. The environment and the proxy or API base path. Half the diagnostic paths differ between products and I do not want to send you down the wrong one.

**A failed trace.** Start a debug trace for the proxy, send the failing request, stop the trace and send it. The trace shows the step that failed and the response the target returned, which usually turns this into a ten minute conversation instead of a two hour one.

**Exact timestamps.** When it was last confirmed working, and the first failure, with timezones. Then your monitoring or analytics error rate for the payments API over the last 48 hours. That bounds the start of the incident precisely. It is often earlier than what gets reported, because people notice when their own calls fail.

**What changed at the boundary.** Deployment history for the payments proxy and any change to the backend it points at in the window between those two times. Also worth checking: a certificate or key rotation, a DNS or upstream change, a target server edit, and a change in the org or environment itself.

**Scope.** One caller or all of them. Every request or some. Every endpoint on the proxy or only the payment path.

Two things while you gather that.

On the release this afternoon: I would hold it. Deploying a change on top of an unexplained outage means that if something breaks again you will not know whether it came back or you caused it, and you will have burned your rollback path. An hour of delay is worth more than that.

On "it was fine yesterday": it was fine at some point on yesterday. The exact last-good timestamp is usually the single most valuable fact in a ticket like this, and it is the one that turns "was fine" into a change to go and look at.

If anyone can reproduce it right now, start there. A live reproduction with a trace attached beats a description every time.

## HARD-10

No, do not close it. Not because 502s coming back would be better for you, but because you do not know yet whether the restart fixed anything, and that matters for the next time this happens.

The recovery lines up with the restart. It does not tell you the restart caused it. A Message Processor restart also clears whatever was accumulating: cached state, stuck or pooled connections, threads waiting on a backend that never answered, exhausted buffers. Every one of those hypotheses predicts "restart it and it goes quiet", and they need completely different fixes. Twenty minutes of quiet is also a short observation window. If the cause was load-correlated, the next peak will tell us.

What I want before this goes cold:

**Why the Message Processors were restarted.** This is the most important fact on the list and I do not have it. If the restart was automatic, an OOM kill or a watchdog event, then the restart is itself evidence and it points straight at memory pressure or a stuck thread pool. If someone restarted them by hand for an unrelated reason, then the restart is close to meaningless as a data point. Check the Message Processor logs for the event that triggered it, and the host metrics for memory around 15:00.

**The Message Processor logs from before 15:00.** That window is where the cause is. Once the processes restart, the evidence that would explain it is gone. Pull it now even if it feels like overkill. If your platform retains JVM GC logs for those hosts, get those too; they will show whether the processors were starved of memory or stuck on garbage collection.

**Whether all Message Processors were affected, or some.** A single sick node suggests something node-specific. The whole fleet at once suggests something on the request path.

**What the 502s were.** Whether the Message Processor generated them or your backend sent them through. That points at different components. If you have request-level data for the incident window, the failing proxy paths and the caller pattern will narrow it quickly.

**Analytics for the incident.** The start time, the peak, the proxy paths involved, and whether the rate was climbing before it stopped or flat. A rate that climbed steadily for hours before the restart points at a leak or an accumulation problem, which is a strong lead.

Status it as unresolved with a workaround in place. That is accurate and it keeps the incident open for the follow-up. Twenty minutes of no errors after an unexplained restart is a mitigation, not a resolution.

I will keep the case open. Send me the restart reason and the pre-15:00 logs and I will take it from there.

## ADV-01

I would rather point you at the authoritative flag list than guess a replacement, because the whole class of problem here is inventing a flag that does not exist and getting a second error. Your error already names the problem: `--service-account` is not a flag on that command, for this CLI version, in your project.

Confirm it in one command:

```
gcloud apigee apis deploy --help
```

That prints the flags the command accepts on the version you actually have installed. Read the environment and revision flags off that output and use them verbatim. The gcloud CLI reference for the command is the other authority, and the local help is faster because it matches your installed version.

Two other things I would check in the same pass.

**The environment flag.** My recollection is that the Apigee commands take `--env` rather than `--environment`, but I am not confident enough to tell you that as fact, and I am not going to have you find out the hard way. If `--help` shows `--environment`, use it; if it shows `--env`, use that.

**`--revision=latest`.** I do not believe `latest` is a revision name. Revision names are normally numbers or names you assign. Run:

```
gcloud apigee apis revisions list --env=prod
```

and use a name from that list. If you are trying to promote an existing revision to an environment rather than upload a new bundle, the command you want is likely `gcloud apigee apis revisions deploy`, with the revision name as the argument. Confirm that with `--help` as well.

On the service account itself, in case that was the part you were after: gcloud picks the active account for the project from `gcloud config`, and `gcloud auth list` shows which one is in use. If you genuinely need a specific service account for one call, check whether the command you are on supports it before assuming this flag does, and also confirm the account has the Apigee Admin role in the right org and project. A 403 on the call rather than an unrecognized flag means you got past flag parsing and it is a permissions problem, not a syntax problem.

If you would rather not fight the CLI, `apigee-maven-plugin` with the `apigee:deploy` goal is the other common route, and your CI may already have it configured.

Post the `--help` output and the exact error text and I will give you the correct command line for your version.

## REG-02

I cannot recommend one yet, and I would be doing you a disservice if I picked one off the top of my head for an API that goes live to a partner. But you do not need to leave today without a decision, so here are both the questions and a default you can ship with.

First, the framing. Quota and SpikeArrest are not competing choices for the same job, and the most common good outcome is both in the same proxy:

- **Quota** caps consumption over a long window. Ten thousand calls a day per client, one million a month. It enforces an allocation and it is the one that maps to a contract.
- **SpikeArrest** caps the instantaneous rate and the burst. Thirty a second, with a burst allowance, so a partner's batch job cannot flatten the backend even though it is well inside its monthly allowance.

What I need to answer properly:

1. **What breaks the backend, and at what point?** Instantaneous concurrency and rate, or accumulated volume over a day or a month? If it is the first, Quota alone will not save you. If it is the second, SpikeArrest alone will not.
2. **What is the backend's safe instantaneous rate**, measured, not guessed? One slow LLM call occupies capacity far longer than one cheap lookup, which makes "requests per second" the wrong unit for you.
3. **What is the cost per call?** If one partner call costs you materially more than another, you want message weight so one expensive call counts as several, not one. That works in both policies.
4. **Who is the limit per?** Per API key, per developer app, or per IP? IP is the wrong key for a partner integration, since partners put several services behind one address.
5. **What is the contractual allowance per partner**, and does it differ per partner? That is a Quota question, and if the numbers vary by client it needs to come from your plan data rather than a static policy.
6. **What should the client see when it hits the limit?** The default status codes differ between the two policies and neither is 429. If partners are going to hit these limits, I would standardise on 429 with a `Retry-After` using a RaiseFault after the policy, so the behaviour is the same whichever limit they hit.
7. **Do you need the limits to be consistent across Message Processors and survive a restart?** How the counters are stored for your runtime affects that. I am not going to assert how yours behaves without checking, and it matters if you run more than one processor.

**What I would ship today if you need to decide now.** SpikeArrest set just under the measured safe instantaneous rate, to protect the backend from bursts. Quota set to the contractual daily allowance per partner, so the numbers are enforced even if the burst limit is never reached. Weighted by cost so an expensive call counts for more. Both failing over into a RaiseFault that returns 429 with `Retry-After`. Review the numbers once you have a week of real traffic, which is the only thing that will actually tell you what the right values are.

Send me the answers to questions 2, 3 and 5 and I will give you the actual policy configuration.