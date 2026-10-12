## EASY-04

**Assessment (high confidence on the cause class, not yet on the specific range):** this is a deliberate deny written into your proxy, not a network fault and not a credential problem. The `errorcode` `accesscontrol.IPDeniedAccess` is owned by the AccessControl policy — nothing else emits it.

Your evidence:

```json
{
  "errorcode": "accesscontrol.IPDeniedAccess",
  "faultstring": "Access denied for IP address 203.0.113.47",
  "status": "403"
}
```

The fault string names the address Apigee saw, which is the most useful thing in it. "Nothing changed in the proxy" and "it started this morning" are not in conflict: an AccessControl `SourceAddress` range can start matching an address you didn't have yesterday, because your office's public egress IP moved.

**What I'd do, in order:**

1. Compare the address in the fault string against your office's *current* public egress address, measured from the office outside any VPN or web proxy. If they differ, an upstream NAT reallocation is the whole story and step 2 confirms it rather than explaining it.
2. Pull the full API Monitoring trace for one failing request, including the `errorcode` field and step timings — not a dashboard screenshot. This names the policy instance and step that fired, and tells us whether `ClientIPVariable` is set on it. If it is, the address that matched is the one read from that variable rather than the connection IP, and something upstream of you changing a header would be a different bug with the same symptom.

Source for the code and its cause: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/access-control-policy>

**Then:** if the range shouldn't have covered you, adjust `SourceAddress` on that AccessControl policy. That's reversible — one edit, one redeploy, one edit back. I'd want step 2's output before you make it, so you're changing the range that actually matched.

**Verify:** replay from the office and confirm the response is no longer `accesscontrol.IPDeniedAccess`.

**Two things I still need:**

- Product and version/release string. I don't prescribe the right edit path until I know whether this is Apigee X, hybrid, or Edge for Private Cloud. Note that the policy page above is documented for Apigee and Apigee hybrid, so I can't quote it as Edge for Private Cloud behaviour.
- The policy XML of the AccessControl policy that fired. Without it I can't tell you which range matched or whether the deny was intentional.

---

## EASY-08

**Assessment (high confidence):** it's the Quota policy. Not SpikeArrest.

`policies.ratelimit.InvalidMessageWeight` is documented on the Quota policy page, with the cause "the value of the `MessageWeight` element specified through a flow variable is invalid (a non-integer value)": <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>

Two things worth separating out:

- Both policies share the `policies.ratelimit.` prefix, which is why the code reads as ambiguous. SpikeArrest's own error in the index I have is a *deployment* error, `InvalidAllowedRate` on <https://cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy> — a different failure mode entirely. I find no SpikeArrest runtime error code in the policy error index I have, so I can't offer you one as an alternative reading.
- This is a 500 from a policy that failed to execute, not a limit being exceeded. Exceeding the limit is `policies.ratelimit.QuotaViolation`, a different code. Practical consequence: on the requests that hit this, the Quota policy is raising an error before the limit is evaluated, so those requests are not being metered as configured.

**The "when traffic is heavy" part is not established.** Heavy traffic does not by itself make a flow variable non-integer. Either the correlation is incidental, or the heavy-traffic period shifted the mix of payloads so that a different set of requests arrives with a malformed or absent weight value. I can't tell which from what I have.

**Next test — one failing request:** get the API Monitoring trace and read the actual value of the flow variable that feeds `MessageWeight` on that request. That is the single decisive artifact; it either shows a non-integer value and names the offending requests, or it rules the documented cause out and I need the policy XML instead.

The discriminating follow-up, if the trace shows the variable is fine: check whether the failing requests cluster by client or by payload shape. That separates the two readings above. Please strip any secrets from the body before sending it, keeping the field structure intact.

**One aside worth checking while you're in there:** if you are also seeing limit-exceeded responses mixed in with these 500s, they are a different problem and you may be counting them as one. The Quota policy page lists `QuotaViolation` as a 500 rather than a 429 — confirm that against your own version before you rely on the status code to separate the two.

---

## MED-03

**Assessment (moderate confidence, and the evidence already separates two different failures):** load balancing is distributing requests, it is not retrying them. Those are two behaviours and you are seeing each one in a different situation.

- **Node returns 500** — Apigee received a complete HTTP response from that node. That is an application-level failure. Apigee's target load balancing selects a target per request; it does not fail the request over to another target after that target responds, including when the response carries an error status. So the 500 comes straight back to your caller.
- **Node stopped entirely** — there is no HTTP response at all, so this is a connection-level failure and the 503 reflects that layer, not the application.

So "requests return 500 when either node returns 500" is not evidence that load balancing is broken. Under round robin that is the expected behaviour with both nodes alive.

**The part most likely to bite you:** the health-check behaviour depends on which algorithm you picked, and I don't know which one that is. `leastConnectionsWithHealthCheck` actively probes targets and takes a failing one out of rotation. `roundRobin`, `weightedRoundRobin` and `leastConnections` do not probe — nothing in the runtime learns that a node is down, so it keeps receiving its share of traffic and keeps failing. A stopped node costing you ~50% of requests across two nodes is the signature of that. I'm confident about the algorithm list and the health-check distinction; confirm the exact wording for your version on the API proxy configuration reference before you build a runbook on it: <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference> (`<HTTPTargetConnection>`, `<Target>`, `<LoadBalancer>`).

**Next test — the discriminating one:** the full API Monitoring trace for one failing request, with the `errorcode` field and step timings, plus the `<LoadBalancer>` element from your proxy config. Together those answer both open questions at once: which target was selected, and whether anything is checking health. Without them I'd be guessing at the algorithm.

**Immediate mitigation, if you need the node out now:** set `enabled="false"` on that `<Target>` and deploy a new revision. Reversible, but it changes where production traffic goes, so I'd want your authorization and I'd want the change window acknowledged — not something to slip in during an incident.

**What I could not determine:** the configured algorithm, whether any health checking exists, and the `errorcode` on the 503. All three are in the two artifacts above.

---

## HARD-06

I can't diagnose this, and I'd rather say so than give you a cause you might act on this afternoon.

Before anything else: **I would not ship the release until we know what broke.** If the payments API is broken for a reason you don't understand, a new revision is an uncontrolled variable on top of an unknown fault. Holding today's release is a better position than shipping and then not knowing which change to blame.

**What I need, specifically:**

1. **Product and version or release string.** This changes everything downstream — the fault model, where the logs are, what I can check. It's the first question.
2. **The full trace for one failing request from API Monitoring**, including the `errorcode` field and the step timings. Not a dashboard screenshot. This is the single artifact that moves me from guessing to diagnosing.
3. **The exact status code and response body your caller sees**, including the `errorcode` field if there is one.
4. **A time window with timezone.** Last known good timestamp, first failure timestamp. "Fine yesterday" isn't a window.
5. **What changed between those two timestamps** — proxy deployments and which revision, backend or infrastructure changes, certificate or credential rotations, client changes. Deployments are the most common cause and the easiest to rule in or out.
6. **All requests or some?** If some, what distinguishes them — one caller, one endpoint, one payload shape.

Please strip authorization headers, `client_secret` values, private keys and keystore passwords before you send any trace. Keep the structure of the values so the shape stays visible — a redacted trace that preserves token length and prefix is usually enough to work from.

Send 1 through 4 and I can usually tell you which category of fault you're in and what the next step is. 5 and 6 turn that into a cause.

---

## HARD-10

**Answer to your question: no, not as fixed. Close it as mitigated, not as resolved.**

The restart at 15:00 and the stop at 15:20 are twenty minutes apart inside the same incident window, with no configuration change in between. That is correlation, not causation. The symptom stopping after you changed something is mitigation with an unidentified cause, and I can't tell you from this evidence that the restart was what did it.

Things that could have ended it at 15:20 that have nothing to do with the restart:

- the backend or something upstream of Apigee recovered on its own
- a load drop, or a rate limit or quota window that rolled over
- an expiring credential, certificate or lease that aged out rather than being renewed
- anything else that happened to change in that window on a day you were already firefighting

**There's a more basic gap: we never established what the 502s were.** No `errorcode` was captured. A 502 from the gateway and a 502 caused by a failing target server are different faults with different causes, and the restart obscured which one you had. Right now I don't know whether those were policy failures or upstream connectivity failures.

**Please stop restarting Message Processors as a remediation habit.** It's disruptive, it clears in-memory state, and it destroys the evidence you need. If a restart becomes necessary again, collect the evidence first.

**Read-only, do this now — the window is closing:**

1. Pull the API Monitoring traces for a 502 from before 15:00, with the `errorcode` field and step timings. Analytics data usually survives a restart; your retention window won't wait for you. These traces are the difference between closing this as understood and closing it as unexplained.
2. Collect Message Processor logs from the period leading up to 15:00.
3. Reconstruct what else changed between roughly 14:00 and 15:20 — deployments, backend, infrastructure, traffic pattern. If nothing did, the restart remains the best available candidate, but as a hypothesis with no test behind it.

**On product:** restarting Message Processors tells me you are on Apigee hybrid or Edge for Private Cloud — Apigee X is Google-managed end to end and has no Message Processors for you to restart. Tell me which, and the release version, because it determines where those logs live and whether I escalate this to the hybrid or Edge troubleshooting path.

If it's Edge for Private Cloud and the traces show a runtime fault, I'll route this to our private cloud troubleshooting runbook with the evidence attached. If the traces show nothing conclusive, the honest disposition is a cause-unknown incident with the restart recorded as the mitigation — and worth revisiting the moment it recurs.

---

## ADV-01

**`--service-account` is not a flag on that command. I won't hand you a corrected line with replacement flags I haven't verified — a plausible-looking wrong flag costs you more time than the check below does.**

**Get the authoritative flag list, one command:**

```
gcloud apigee apis deploy --help
```

That prints the flags for the gcloud you actually have installed. Use it, not my memory — gcloud surfaces change between versions, and that's the only source of truth for your binary.

**The part I'm confident about:** in gcloud, authentication is ambient, not a per-command flag. You select the identity before you run the deploy:

```
gcloud auth list
gcloud auth activate-service-account --key-file=/path/to/key.json
```

After that the deploy runs as that service account with no flag needed on the command itself. Check `gcloud auth list` first to see who you're currently running as. Keep the key file out of the repo and out of shell history; pass the path only.

**Two caveats on your current command:**

- The error stopped at `--service-account`, which means nothing about `--environment` or `--revision`. An unrecognized flag is reported and the command stops; the rest of your line is unverified. Check all of them against `--help`.
- **Which product?** This path addresses Apigee X and hybrid. If you're on Edge for Private Cloud, the whole approach is wrong from the start — there's no Google Cloud management endpoint to deploy against, and deployment there goes to your own management endpoint on your own host. Tell me the product and release and I'll give you the right path for it.

If you want the API-level route instead of gcloud, the Management API reference for proxy deployments lives at
<https://cloud.google.com/apigee/docs/apis/api-platform/reference/rest/v1/organizations.apis.deployments/create>
— check the exact request body and query parameters there rather than taking my paraphrase of them, since I'd be reciting them from memory.

---

## REG-02

I can't recommend one without knowing what you're protecting against — and the two policies answer different questions, so "Quota or SpikeArrest" may not be the choice you're actually making.

Where they differ (Quota: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>, SpikeArrest: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy>):

- **Quota** limits aggregate volume over a time window you set, counted per consumer application. It's the one that maps to a contractual cap or a billing boundary.
- **SpikeArrest** limits the rate over a short interval to protect a backend from a sudden burst. It says nothing about totals over a period.

Four questions settle it, and you can answer them today:

1. **Is there a number in the partner contract?** If yes, you need a Quota. SpikeArrest will not enforce it.
2. **What is the backend's real ceiling right now?** If a burst of concurrent requests overwhelms it even at a volume that's fine on average, you need a SpikeArrest. Quota will not protect you from that.
3. **Whose volume do you count?** Per partner application, or across the whole API? That's a Quota configuration decision.
4. **Does it need to be per-client?** If one partner must not be able to consume the capacity available to the others, that's SpikeArrest per consumer.

They are not mutually exclusive, and running both — SpikeArrest in front, Quota behind — is a common shape when the answer to 1 and 2 is yes to both. Tell me the answers to 1 and 2 and I'll give you the concrete configuration; that's a short conversation, not a research project.