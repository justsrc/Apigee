# Easy scenarios

Fifteen narrow cases. Each has enough information to reach a cause or to ask one
essential question, and a short path to confirming the answer.

Every fault code in this file was extracted from a real policy page by
`research/build_error_index.py`. Do not add a code here that is not in
`.agents/skills/apigee-support-core/references/error-codes.md`. The single exception is
EASY-14, which uses a non-policy code and says so explicitly in the scenario.

Each scenario is labelled by origin. **Documented** cases come from a documented
behaviour. **Synthetic** cases are constructed from verified behaviour and never claim a
real incident happened. Nothing here reproduces a private support ticket.

---

### EASY-01. Quota policy rejects the revision over a fractional interval

#### Scenario metadata

- ID: EASY-01
- Difficulty: easy
- Primary topic: Quota policy configuration
- Secondary topics: deployment errors, revision lifecycle
- Product: Apigee or hybrid (deployment behaviour is shared)
- Origin: documented
- Versions: current documentation, checked 2026-10-11
- Evaluation objectives: separate a deployment error from a runtime error; match the
  documented error name; do not propose a runtime investigation
- Skills expected: apigee-support-core

#### Initial support ticket

> We cannot deploy our proxy any more. It worked last week. The API call to save the
> revision fails and the UI says "Error Saving Revision 4". Nothing in our flow config
> changed that I can see. What is it complaining about?

#### Initial evidence

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

#### Expected investigation

A capable agent should notice immediately that the symptom is a rejected revision, not a
failing request. No trace, no runtime log and no target investigation is relevant. It
should locate the Quota policy, match `InvalidQuotaInterval`, and read the documented
cause: the interval must be an integer.

A weaker agent tends to look for a recent change or start collecting runtime logs, which
cannot help because nothing is running.

#### Diagnostic evidence

If asked what the deployment error message says in full, the user supplies:

```
Error Saving Revision 4
InvalidQuotaInterval: The quota interval is not a valid integer.
```

If asked whether `<Interval>` was changed recently, the user says it was set to `0.5`
about six weeks ago. Whether a revision with that value was ever saved successfully is not
known and the customer is not sure: the deployed revision is three weeks older than the
edit, and nobody can recall whether the edit was ever deployed. If it was, then something
other than the documented rule was in effect at the time, and that is worth establishing
before drawing a conclusion.

#### Ground-truth resolution

`InvalidQuotaInterval` fires when the `<Interval>` element is not an integer. `0.5` is
not an integer, so the revision is rejected at upload. This is a deployment error, which
means it has no HTTP status and never reaches the runtime.

The reason the current revision is rejected is the value, not a recent change to anything.
That is the whole answer here, and it does not depend on the deployment history.

Do not build a story out of the history you were given. The scenario offers two facts that
do not fit together: a `0.5` interval that cannot have been saved under the documented rule,
and a customer who believes an earlier revision was saved with it. An agent should give the
cause the documentation supports and flag the inconsistency rather than inventing a
mechanism to reconcile it. Claiming an undetected platform change, a prior
`IgnoreValidationErrors` setting, or any other story to make both facts true is a
fabrication, and it is worth more marks to say the history cannot be reconciled from the
evidence supplied than to produce a tidy explanation.

An agent that treats this as a runtime fault because the ticket says the proxy "cannot be
deployed any more" has missed the distinction the rest of the scenario is about.

#### Correct remediation

Set `<Interval>` to a positive integer and specify the fraction through `<TimeUnit>`.

```xml
<Quota name="OrdersPerMinute" type="rollingwindow">
  <Interval>30</Interval>
  <TimeUnit>second</TimeUnit>
</Quota>
```

Confirm `second` is a supported `<TimeUnit>` value before recommending it. If the team
needs sub-minute windows, SpikeArrest is the documented recommendation rather than
abusing Quota. This is a configuration change in source control, so it is reversible, and
it affects only the next revision deployed.

#### Verification

Re-deploy the revision. A successful save confirms the deployment error is gone. Then
send requests exceeding the intended rate and confirm a `QuotaViolation` with HTTP 500,
which is the documented runtime behaviour for an exceeded quota and proves the policy is
executing rather than merely parsing.

A superficial check is that the UI no longer shows an error. That proves the revision
saved. It does not prove the quota behaves as intended.

#### Common incorrect answers

Recommending `<Interval>0.5</Interval>` with `<TimeUnit>minute</TimeUnit>` is the same
configuration restated, and still fails.

Treating this as a runtime fault and suggesting they look at API Monitoring traces is
wrong, because the revision never deployed and there is no trace.

Claiming the Quota policy does not support fractional intervals at all is an
overstatement. The restriction is that `<Interval>` must be an integer; the granularity
comes from `<TimeUnit>`.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Misdiagnoses as runtime | Correct cause, imprecise detail | Names `InvalidQuotaInterval` and the integer requirement |
| Product and version | Applies Edge procedures | Correct product, unstated | Correct product and product-appropriate steps |
| Evidence and citation | No source | Policy page referenced loosely | Cites the Quota policy error reference |
| Diagnostic method | Suggests log hunting | Identifies deployment stage | Explicitly excludes runtime investigation |
| Handling of uncertainty | Asserts without support | Reasonable | States what is confirmed and what remains unknown |
| Safety | Recommends production changes | Suggests a redeploy | Notes the change is source-controlled and reversible |
| Verification | "Deploy and check" | Checks save succeeded | Checks save plus resulting runtime behaviour |

**Critical failures:** treating this as a runtime fault; recommending a change to the
live revision without noting the current one keeps serving.

#### References

- Quota policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
- What you need to know about policy errors:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/what-you-need-know-about-policy-errors>

---

### EASY-02. Missing Interval produces a runtime 500, not a deploy failure

#### Scenario metadata

- ID: EASY-02
- Difficulty: easy
- Primary topic: Quota policy configuration
- Secondary topics: runtime versus deployment errors, fault codes
- Product: Apigee or hybrid
- Origin: documented
- Versions: checked 2026-10-11
- Evaluation objectives: recognise that a missing element and an invalid element produce
  different failure modes; this is the deliberate pair to EASY-01
- Skills expected: apigee-support-core

#### Initial support ticket

> Our orders API started returning 500 to about 3% of requests. The error body mentions
> a quota interval reference. We did not change the proxy. Did something get deployed by
> mistake?

#### Initial evidence

A response body:

```json
  {
    "fault": {
      "detail": {
        "errorcode": "policies.ratelimit.FailedToResolveQuotaIntervalReference"
      },
      "faultstring": "Unable to resolve interval reference"
    }
  }
```

HTTP response status 500.

Only about 3% of requests fail. Requests on a different proxy that shares the same
backend are unaffected.

#### Expected investigation

The agent should read `errorcode` rather than the prose, look it up in the error
reference, and find that `<Interval>` is mandatory. It should then find the Quota policy
with the element genuinely absent, as opposed to present and invalid.

The interesting part is the 3% figure. It suggests the failing path is conditional, so
the agent should check whether the Quota policy sits inside a conditional flow or is
reached only for certain requests.

#### Diagnostic evidence

On request, the proxy shows:

```xml
<Flow name="rate-limited">
  <Condition>(request.header.x-route == "v2")</Condition>
  <Quota name="PerMinute">
    <TimeUnit>minute</TimeUnit>
  </Quota>
</Flow>
```

The `<Interval>` element is absent. The flow carries a condition, which explains why only
some requests fail.

#### Ground-truth resolution

Two findings, both confirmed.

The `<Interval>` element is mandatory. Its absence causes the runtime fault
`policies.ratelimit.FailedToResolveQuotaIntervalReference` with HTTP 500. This is a
runtime error, so a request reached the proxy and failed while executing a policy.

The failure is partial because the Quota policy sits in a conditional flow gated on a
request header, so only requests carrying that header execute it.

Nothing was deployed by mistake necessarily. If the condition was added recently, only
the `v2` route started failing.

#### Correct remediation

Add the element with an integer value, keeping the existing condition:

```xml
<Quota name="PerMinute">
  <Interval>1</Interval>
  <TimeUnit>minute</TimeUnit>
</Quota>
```

This is a proxy source change deployed as a new revision. Do not edit a live revision in
the management UI, since the next import overwrites it and the change becomes
unreproducible.

#### Verification

Send requests both with and without `x-route: v2`. All should succeed once deployed.
Confirm the 500 no longer appears in API Monitoring for the v2 route, and confirm the
quota counters appear in analytics so the policy is demonstrably running rather than
silently skipped.

#### Common incorrect answers

Claiming the 3% failure rate proves a partial deployment is in flight. The condition
explains it fully.

Recommending `<Interval>1.0</Interval>`. Still a deployment error.

Suggesting the proxy be redeployed without a change. It already is deployed, and it is
failing at runtime.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Wrong fault meaning | Correct fault, wrong stage | Correct fault, correct stage, explains the conditional flow |
| Diagnostic method | Guesses at deployment | Finds the policy | Finds the policy and explains the 3% |
| Handling of uncertainty | Asserts a deployment cause | Hedges | Separates confirmed from unconfirmed cleanly |
| Safety | Edits the live revision | Suggests redeploy | Explicitly says change source and deploy a new revision |
| Verification | "Retest" | Tests v2 only | Tests both branches and checks analytics |

**Critical failures:** editing a deployed revision in place rather than changing source.

#### References

- Quota policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
- Policy error model:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/what-you-need-know-about-policy-errors>

---

### EASY-03. FlowCallout cannot find the shared flow

#### Scenario metadata

- ID: EASY-03
- Difficulty: easy
- Primary topic: shared flows and FlowCallout
- Secondary topics: deployment order, runtime faults
- Product: Apigee or hybrid
- Origin: documented
- Versions: checked 2026-10-11
- Evaluation objectives: distinguish "does not exist" from "not deployed"; both produce
  the same code
- Skills expected: apigee-support-core

#### Initial support ticket

> After we refactored the token validation into a shared flow, every request fails with a
> 500. The shared flow is in the same bundle as the proxy. What did we get wrong?

#### Initial evidence

```json
  {
    "fault": {
      "detail": {
        "errorcode": "flow.SharedFlowNotFound"
      }
    }
  }
```

HTTP response status 500.

The proxy bundle contains `policies/validate-token.xml` attached via FlowCallout, and
`sharedflows/token-validation/` with its own policies.

#### Expected investigation

The documented cause is two possibilities: the shared flow does not exist, or it exists
but is not deployed to the environment. The agent must check deployment state rather than
stop at the first reading, because the bundle looks correct.

#### Diagnostic evidence

The shared flow exists in the bundle and imports fine. Querying deployments for the
environment shows the shared flow has never been deployed there. The proxy deployment
succeeded because the shared flow reference is resolved at request time, not at upload.

#### Ground-truth resolution

The shared flow exists but is not deployed to the environment the proxy is running in.
The documented cause covers exactly these two cases and the agent cannot tell them apart
from the fault code alone. Checking deployment state is what separates them.

A useful detail: the code says nothing about the shared flow being missing from the
bundle, it says it was not found, which in practice means not deployed to this
environment.

#### Correct remediation

Deploy the shared flow to the environment first, then deploy or re-deploy the proxy that
references it. Order matters.

This is a control-plane change. It is reversible by undeploying, and it affects one
environment.

#### Verification

Deploy the shared flow, confirm it appears in the environment's deployment list, then
send a test request and confirm a 200. Then deliberately check a second environment that
still lacks the shared flow deployment, to confirm you fixed the specific environment
rather than something incidental.

#### Common incorrect answers

Rewriting the FlowCallout XML. The reference is correct.

Adding `apigee:sharedFlow` metadata to the proxy. Metadata does not deploy the shared
flow.

Concluding the shared flow name is wrong. It matches, which the successful bundle import
already demonstrates.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says the flow is missing | Acknowledges two causes | Identifies not-deployed and names the check |
| Diagnostic method | Reads code only | Checks bundle | Checks deployment state separately |
| Evidence and citation | None | Generic docs | Cites the FlowCallout error reference |
| Quality of next step | "Deploy it" | Names the action | Names the order and the environment |
| Verification | None | Sends a request | Confirms deployment then tests |

**Critical failures:** recommending a bundle change when the bundle is correct; claiming
the code proves the shared flow is absent.

#### References

- FlowCallout policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/flow-callout-policy>

---

### EASY-04. AccessControl blocks a corporate IP range

#### Scenario metadata

- ID: EASY-04
- Difficulty: easy
- Primary topic: AccessControl policy
- Secondary topics: HTTP status interpretation
- Product: Apigee or hybrid
- Origin: documented
- Versions: checked 2026-10-11
- Evaluation objectives: read the fault code and its documented status; note that 403
  here is a policy decision, not a credential failure
- Skills expected: apigee-support-core

#### Initial support ticket

> Since this morning our office gets a 403 from the orders API. Nothing changed in the
> proxy. Home wifi works fine. What is blocking us?

#### Initial evidence

```json
  {
    "fault": {
      "detail": {
        "errorcode": "accesscontrol.IPDeniedAccess"
      },
      "faultstring": "Access denied for IP address 203.0.113.47"
    }
  }
```

HTTP response status 403.

The request from the office network fails. The same credentials from home succeed.

#### Expected investigation

Read the code, note it is AccessControl and the documented status is 403, then look at
the policy's configured ranges. The asymmetry between office and home is the strongest
clue and should drive the next question.

#### Diagnostic evidence

The AccessControl policy contains:

```xml
<AccessControl name="ACL">
  <IPRules noRuleMatchAction="ALLOW">
    <MatchRule action="DENY">
      <SourceAddress mask="24">203.0.113.0</SourceAddress>
      <SourceAddress mask="24">198.51.100.0</SourceAddress>
    </MatchRule>
  </IPRules>
</AccessControl>
```

`noRuleMatchAction="ALLOW"` is why every caller outside those two ranges is unaffected.
The office egress address is 203.0.113.47, inside the 203.0.113.0/24 block. A change
record shows the range was added two days ago by a security team hardening a blocklist.

#### Ground-truth resolution

AccessControl matched the client IP against a configured deny range. The documented cause
for `accesscontrol.IPDeniedAccess` is a client IP matching an address specified in a
`SourceAddress` element in the policy, with HTTP 403.

The policy is doing what it was configured to do. Nothing is broken, and nothing is
misbehaving. The question is whether the blocklist entry is still intended to cover this
range.

Note the IP `203.0.113.0` is from the TEST-NET-3 documentation range, which is worth
flagging as suspicious in a real environment, since it suggests example values were
pasted into a live policy.

#### Correct remediation

This is a security configuration owned by another team. Do not remove the range. Confirm
with the team that added it whether the office egress address is still meant to be
blocked, and if the block was a temporary incident response, agree an expiry.

Removing a blocklist entry is a security-weakening change and needs the owner to
authorize it, not just the reporter.

#### Verification

Confirm with the security team first. After any authorized change, test from the office
network and confirm a 200, and test from an address that remains blocked and confirm it
still returns 403. The second check matters, because removing the wrong entry would pass
the first test.

#### Common incorrect answers

Telling them to rotate API keys. This is an IP policy, not a credential check.

Removing the AccessControl policy to unblock traffic. That silently removes a security
control for every caller, not just the office.

Recommending they use the home network. That hides the problem rather than resolving it,
and leaves office users broken.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Misreads as auth failure | Right policy, wrong cause | Right code, right cause, notes 403 is a policy decision |
| Diagnostic method | Suggests key rotation | Finds the policy | Correlates policy range with the client IP |
| Safety | Removes the block | Suggests escalation | Routes to the owning team and requires authorization |
| Verification | None | Retests once | Tests both allowed and still-blocked |
| Clarity | Buries the answer | Clear | Leads with the cause |

**Critical failures:** recommending removal of a security control without authorization;
recommending credential rotation.

#### References

- AccessControl policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/access-control-policy>

---

### EASY-05. JavaScript policy blocked by a security violation

#### Scenario metadata

- ID: EASY-05
- Difficulty: easy
- Primary topic: JavaScript policy
- Secondary topics: security model, runtime faults
- Product: Apigee or hybrid
- Origin: documented
- Versions: checked 2026-10-11
- Evaluation objectives: recognise that the documented fix column for this code sends you to
  the fault string; do not invent a mechanism from the code alone, and do not relabel the
  code the evidence actually shows
- Skills expected: apigee-support-core

#### Initial support ticket

> A JavaScript policy we have had for a year suddenly fails with a security error. It
> just reads a header and sets a variable. Nothing changed in the script. Did a runtime
> update break it?

#### Initial evidence

```json
  {
    "fault": {
      "detail": {
        "errorcode": "steps.javascript.ScriptSecurityError"
      }
    }
  }
```

HTTP response status 500.

The script:

```javascript
var token = context.getVariable("request.header.computeToken");
context.setVariable("token", loadCredential(token));
```

#### Expected investigation

The agent should distinguish this from `steps.javascript.ScriptExecutionFailed`, which
indicates a runtime error in the code. ScriptSecurityError indicates a security error
occurred when the script executed. The distinction matters because the fix is different:
one is a code bug, the other is the sandbox refusing something.

#### Diagnostic evidence

Rewriting the second line as:

```javascript
context.setVariable("token", token);
```

now succeeds, which confirms the first line is fine and the helper call is what was
blocked.

#### Ground-truth resolution

Start from what the evidence actually shows: the response carries
`steps.javascript.ScriptSecurityError`. The JavaScript policy page documents that code as
"A security error occurred when the `JavaScript` executed. See the fault string for
details", and nothing more. The code alone does not name the blocked call, and the page
sends you to the fault string for that.

So the first real step is to ask for the fault string, not to theorise about the code. An
agent that stops at the error code and asserts a cause is guessing; the documentation
explicitly declines to carry enough information to identify the call.

What the script does tell you is that `loadCredential` is not in the documented JavaScript
object model. That is a defect in the script regardless of which code Apigee raises: the
script references an identifier that does not exist. Note the trap here. An undeclared
identifier is normally a `ReferenceError`, and the page maps `ReferenceError` to
`steps.javascript.ScriptExecutionFailed`, not to `ScriptSecurityError`. So do not reason
backwards from "ReferenceError must be involved" to "it is therefore a security error", and
do not rename the code in the response. The evidence says `ScriptSecurityError`; take it at
face value and get the fault string, which is the only thing that will tell you what was
actually refused.

"Nothing changed in the script" is what makes this worth asking about rather than assuming a
runtime regression. The customer believes a runtime update changed the behaviour. The
documented answer is that the page does not support that conclusion either way: it records
what the fault means, not what changed between releases. Say that, and say what would
settle it.

#### Correct remediation

Replace the restricted call with a documented object model equivalent, or with a Java
callout if no equivalent exists. `loadCredential` is a script-local helper, not part of
the object model, so the right substitute depends on what the header actually needs. Ask
before choosing.

Check the JavaScript object model reference for an equivalent before writing any code. Do
not guess at a method name.

#### Verification

Deploy to a test environment, send a request carrying the header, and confirm the variable
is set correctly. Then confirm requests without the header still behave as before.

Also worth removing the now-unused callout if nothing else uses it.

#### Common incorrect answers

Claiming this is a bug in Apigee and that it should be filed. It is documented sandbox
behavior.

Raising the JavaScript timeout. Timeout failures are a different code and a different
symptom.

Suggesting migrating the policy to a Java callout as the first move. That is a larger
change than the problem warrants and should come after confirming no JS equivalent exists.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Confuses the two codes | Right code, weak explanation | Distinguishes security from execution failure and says why |
| Diagnostic method | Proposes a rewrite blind | Looks at object model | Confirms the call is restricted before substituting |
| Evidence and citation | None | Generic | Cites the JavaScript policy error reference |
| Handling of uncertainty | Confident guess | Hedges | Asks what the header is used for |

**Critical failures:** proposing a different method name that was not verified against the
JavaScript object model.

#### References

- JavaScript policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/javascript-policy>
- JavaScript object model:
  <https://cloud.google.com/apigee/docs/api-platform/reference/javascript-object-model>

---

### EASY-06. BasicAuthentication cannot resolve its source variable

#### Scenario metadata

- ID: EASY-06
- Difficulty: easy
- Primary topic: BasicAuthentication policy
- Secondary topics: flow variable scope, policy execution order
- Product: Apigee or hybrid
- Origin: documented
- Versions: current documentation, checked 2026-10-11
- Evaluation objectives: read the documented cause, which names two candidates, and use
  the faultstring to identify which variable failed; note that the fault only appears when
  `IgnoreUnresolvedVariables` is `false`
- Skills expected: apigee-support-core

#### Initial support ticket

> Our partner endpoint started returning 500 for every request. The body mentions an
> unresolved variable. We did not touch the BasicAuthentication policy file itself, though
> we did do some cleanup in that flow last week.

#### Initial evidence

```json
  {
    "fault": {
      "detail": {
        "errorcode": "steps.basicauthentication.UnresolvedVariable"
      }
    }
  }
```

HTTP response status 500.

The policy:

```xml
<BasicAuthentication name="DecodeBasicAuth">
  <Operation>Decode</Operation>
  <Source>encodedBasicAuth</Source>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
</BasicAuthentication>
```

#### Expected investigation

The documented cause for `steps.basicauthentication.UnresolvedVariable` has exactly two
candidates, and both are worth quoting precisely: the variable named in `<Source>` is
either **out of scope, not available in the specific flow where the policy is being
executed**, or it **cannot be resolved, is not defined**. That is the same pair of causes
the JSONToXML policy documents for `steps.jsontoxml.SourceUnavailable`, so the two codes
share a failure mode even though the policies have nothing else in common.

The documentation is also explicit that this error can only occur when
`IgnoreUnresolvedVariables` is `false`. Seeing that value in the config confirms the
configuration directly rather than by inference.

The faultstring is what names the failing variable, so the agent should ask for it rather
than guess which variable in the proxy is at fault.

#### Diagnostic evidence

The user supplies the full body:

```
Unresolved variable : encodedBasicAuth
```

The proxy bundle shows two steps in the same flow, in this order:

```xml
<Flow name="partner-auth">
  <Request>
    <Step><Name>DecodeBasicAuth</Name></Step>
    <Step><Name>BuildBasicAuthVariable</Name></Step>
  </Request>
</Flow>
```

`BuildBasicAuthVariable` is the step that assigns `encodedBasicAuth`.

#### Ground-truth resolution

The variable named in `<Source>` is not available in the flow where the policy is being
executed, because the step that assigns it runs after the policy that reads it. The
documented diagnosis step is exactly this check: determine whether the variable is defined
and available in the flow in which the policy is being executed.

This is a runtime fault. The policy parsed and deployed fine and fails on every request at
execution time, which is why the 500 is universal rather than intermittent.

`IgnoreUnresolvedVariables` being `false` is what turned an unavailable variable into an
error instead of silently continuing. With the flag set to `true` the policy does not
throw when a variable cannot be resolved, so the same ordering bug would let requests
through with no decoded credentials instead of failing loudly.

#### Correct remediation

Put the assigning step before the policy that reads it. Step order inside the flow is the
fix, not the policy configuration:

```xml
<Flow name="partner-auth">
  <Request>
    <Step><Name>BuildBasicAuthVariable</Name></Step>
    <Step><Name>DecodeBasicAuth</Name></Step>
  </Request>
</Flow>
```

If the partner actually sends a standard header, the intermediate step is unnecessary. The
documented example for this policy points `<Source>` at the request header variable:

```xml
<BasicAuthentication name="DecodeBasicAuth">
  <Operation>Decode</Operation>
  <Source>request.header.Authorization</Source>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
</BasicAuthentication>
```

Confirm which of the two the partner contract actually implies before choosing. Do not
write either variant on a guess.

#### Verification

Send a request carrying credentials and confirm the decoded username and password
variables are populated, not merely that the request returned 200, because a decode policy
with nothing to decode can still return 200. Then confirm a request without credentials
still fails, which proves the policy is checking rather than passing through.

#### Common incorrect answers

Setting `IgnoreUnresolvedVariables` to `true`. That hides the 500 while letting requests
through with no credentials. The element reference says this setting is usually `false` for
a BasicAuthentication policy precisely because it is beneficial to throw an error when the
username or password cannot be found.

Reading it as a malformed Base64 payload, that is, a decoding problem. The faultstring
reports an unresolved variable, which is a failure to resolve the variable, not a failure
to decode its contents.

Treating it as a deployment or configuration validation failure. The policy deployed and
parsed; it fails at request time, and no revision was re-saved.

Removing the BasicAuthentication policy. That silently removes authentication for every
caller, not just the affected route.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Blames Base64 or the deployment | Identifies the unresolved variable | Names the scope cause and quotes both documented candidates |
| Diagnostic method | Guesses | Asks for the faultstring | Asks for the faultstring and checks step order in the flow |
| Evidence and citation | None | Generic | Cites the BasicAuthentication runtime error reference |
| Quality of next step | Suppresses the error | Reorders the steps | Reorders the steps and offers the header-source alternative |
| Safety | Removes the policy | Reorders without asking | Changes step order and asks which contract applies |
| Verification | None | Retests once | Confirms decoded values and confirms missing credentials still fail |

**Critical failures:** recommending `IgnoreUnresolvedVariables` be set to `true` as the
fix; removing the BasicAuthentication policy; treating the fault as a deployment error.

#### References

- BasicAuthentication policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/basic-authentication-policy>
- BasicAuthentication runtime errors:
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/runtime/basic-authentication-runtime-errors>
- Flow variables and conditions:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/flow-variables-and-conditions>

---

### EASY-07. JWS algorithm does not match between generate and verify

#### Scenario metadata

- ID: EASY-07
- Difficulty: easy
- Primary topic: JWS signing and verification
- Secondary topics: key configuration, 401 handling
- Product: Apigee or hybrid
- Origin: documented
- Versions: checked 2026-10-11
- Evaluation objectives: match the documented cause, which names both policies; note the
  difference between a sign and verify algorithm mismatch and a key problem
- Skills expected: apigee-support-core, apigee-support-core references/security.md

#### Initial support ticket

> Our partner updated their signing library and now our API returns 401 for their tokens.
> The tokens look structurally correct. Their team says nothing changed in our config.

#### Initial evidence

```json
  {
    "fault": {
      "detail": {
        "errorcode": "steps.jws.AlgorithmMismatch"
      }
    }
  }
```

HTTP response status 401.

Partner tokens have an `alg` header of `PS256`. The VerifyJWS policy is configured with
`<Algorithm>RS256</Algorithm>`.

#### Expected investigation

Read the code and the documented cause: the algorithm in the header produced by the
Generate policy did not match the one expected in the Verify policy. Since the partner is
the signer, compare their `alg` header against the configured algorithm.

#### Diagnostic evidence

A decoded token header shows `"alg": "PS256"`. The proxy bundle shows `<Algorithm>RS256
</Algorithm>`. The previous library produced `RS256`.

#### Ground-truth resolution

The partner's library changed its default signing algorithm from RS256 to PS256. The
VerifyJWS policy expects RS256. The documented cause of `steps.jws.AlgorithmMismatch` is
exactly this mismatch, and it returns 401.

This is not a key problem. The signature may well be valid under PS256; the policy simply
refuses to verify anything that is not RS256.

Note that PS256 is a supported algorithm in Apigee generally. The constraint here is the
single configured value, not the platform.

#### Correct remediation

Two options, and the choice belongs to the partner relationship rather than to whoever
is debugging.

Ask the partner to revert to RS256, which is the smaller change and preserves the
existing policy. Or accept PS256 deliberately by adding it to the policy configuration
and testing both. The supported algorithm list is documented, so whichever is chosen
should be checked against it.

Do not silently accept any algorithm the partner sends.

#### Verification

Send a token signed with RS256 and confirm it verifies. Then send one signed with PS256
and confirm the new configuration handles it. Then confirm an unsupported algorithm still
fails, which proves the policy is checking rather than ignoring.

#### Common incorrect answers

Replacing the signing key. Algorithm mismatch is not a key problem, and rotating keys
would break a partner integration that is currently working.

Adding `*` or a wildcard to accept any algorithm. VerifyJWS does not document a wildcard,
and accepting arbitrary algorithms is a security regression.

Concluding the tokens are invalid. The document says the algorithm did not match, which
is a different condition from a bad signature.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says the signature is bad | Identifies algorithm mismatch | Matches the documented cause precisely |
| Diagnostic method | Suggests key rotation | Compares alg to config | Reads the token header and compares |
| Safety | Weakens algorithm policy | Offers two options | Offers options and requires a deliberate choice |
| Verification | None | Tests one path | Tests old, new, and still-unsupported algorithms |
| Evidence and citation | None | Generic | Cites the VerifyJWS error reference |

**Critical failures:** recommending acceptance of arbitrary or unverified algorithms.

#### References

- VerifyJWS policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jws-policy>
- JWT policies overview:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/jwt-policies-overview>

---

### EASY-08. InvalidMessageWeight does not tell you which policy failed

#### Scenario metadata

- ID: EASY-08
- Difficulty: easy
- Primary topic: Quota and SpikeArrest
- Secondary topics: fault code ambiguity, weight configuration
- Product: Apigee or hybrid
- Origin: documented
- Versions: checked 2026-10-11
- Evaluation objectives: recognise that this one code is shared by two policies, so the
  code alone cannot identify the culprit; the trace step name can
- Skills expected: apigee-support-core

#### Initial support ticket

> We get intermittent 500s from our LLM-backed endpoint, roughly when traffic is heavy.
> The errorcode is the same every time. We have both a Quota and a SpikeArrest policy in
> that proxy. Which one is it?

#### Initial evidence

```json
  {
    "fault": {
      "detail": {
        "errorcode": "policies.ratelimit.InvalidMessageWeight"
      }
    }
  }
```

HTTP response status 500.

The proxy has a Quota policy and a SpikeArrest policy. The LLM token weight is set by a
flow variable read from the request body.

#### Expected investigation

The key insight is that `policies.ratelimit.InvalidMessageWeight` is documented on both
the Quota and SpikeArrest pages. The error code alone cannot identify the policy, so the
agent must use the trace step name to find which policy actually executed.

This is a good test of whether the agent reaches for a second source of evidence when a
code is ambiguous.

#### Diagnostic evidence

An API Monitoring trace shows the step that failed. Step names below are abbreviated
to policy types, since real step names are whatever the team named each policy:

```
VerifyAccessToken        OK       2ms
Quota policy (token count)  OK       11ms
SpikeArrest policy       FAILED   0ms  policies.ratelimit.InvalidMessageWeight
```

The failing step is the SpikeArrest policy.

#### Ground-truth resolution

The SpikeArrest policy failed. The documented cause of
`policies.ratelimit.InvalidMessageWeight` is that the value specified through a flow
variable is invalid because it is not an integer. The same code and cause are documented
on both the Quota and SpikeArrest pages.

The weight variable resolved to null or a non-numeric value under heavy traffic, which is
consistent with a counting step that falls back or fails to parse on an unusually shaped
request.

The heavy-traffic correlation is the clue worth following next, but it does not change
which policy failed.

#### Correct remediation

Make the counting step always produce an integer, with a default:

```javascript
var count = parseInt(context.getVariable("tokenCount"), 10);
if (isNaN(count) || count < 0) { count = 1; }
context.setVariable("tokenCount", count);
```

Then confirm what the counting step emits for the specific request shape seen under heavy
traffic, because a default prevents the failure without explaining it.

#### Verification

Replay the request shape that triggered the fault and confirm the weight variable is a
positive integer. Then confirm quota and spike behaviour still behave as configured, so
the fallback did not silently change the effective rate limit.

#### Common incorrect answers

Changing only the Quota policy because the error mentions rate limiting. The failing step
was SpikeArrest.

Asserting the code identifies the policy. It does not, which is documented.

Raising the weight to 0 to stop the error. A non-positive weight changes what the limit
means rather than fixing the parse.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Names the wrong policy | Acknowledges ambiguity | Names SpikeArrest from the trace and explains the shared code |
| Diagnostic method | Guesses from the prefix | Reads the code only | Uses the trace step name as the discriminator |
| Evidence and citation | None | One policy page | Cites both policy pages for the shared code |
| Handling of uncertainty | Asserts a policy | Hedges | States the code is ambiguous and names the test |

**Critical failures:** asserting the error code uniquely identifies a policy; editing the
Quota policy when SpikeArrest is the failing step.

#### References

- Quota policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
- SpikeArrest policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy>

---

### EASY-09. JSONToXML cannot resolve its source variable

#### Scenario metadata

- ID: EASY-09
- Difficulty: easy
- Primary topic: JSONToXML policy
- Secondary topics: flow variables, source variable scope
- Product: Apigee or hybrid
- Origin: documented
- Versions: checked 2026-10-11
- Evaluation objectives: read the specific code rather than the generic execution failure,
  and recognise that one code carries two documented causes so the trace, not the code,
  decides between them
- Skills expected: apigee-support-core

#### Initial support ticket

> Our XML endpoint returns 500 for some requests but works for most. The proxy converts
> the JSON body to XML before forwarding it. We did not change the policy, but we changed
> the upstream contract last week.

#### Initial evidence

A response body:

```json
  {
    "fault": {
      "detail": {
        "errorcode": "steps.jsontoxml.SourceUnavailable"
      }
    }
  }
```

HTTP response status 500.

The policy:

```xml
<JSONToXML name="BodyToXml">
  <Source>payload</Source>
  <OutputVariable>xmlBody</OutputVariable>
</JSONToXML>
```

A JavaScript policy earlier in the request flow runs only when a flow condition is true,
and that step is what assigns `payload`.

#### Expected investigation

The documented cause of `steps.jsontoxml.SourceUnavailable` names two candidates, and both
are worth quoting precisely: the message variable specified in `<Source>` is either **out
of scope, not available in the specific flow where the policy is being executed**, or it
**cannot be resolved, is not defined**. The code alone does not say which one applies, so
the agent needs a trace to choose, rather than stopping at "the variable did not resolve".

The documented sibling `InvalidSourceType` is a different condition and should not be
reached for here. That one fires when the type of the variable used to define `<Source>` is
invalid, and it names the valid types as `message` and `string`. A variable that resolves
to nothing has no type to check, so it cannot produce that code.

#### Diagnostic evidence

A trace for a failing request shows the JavaScript step was skipped, because the condition
on its flow evaluates false for those requests, so `payload` was never assigned. On requests
where the step does run, `payload` holds a string and the conversion succeeds.

#### Ground-truth resolution

The `<Source>` variable is not defined on the failing requests. The assigning step sits
behind a flow condition that evaluates false for them, so `payload` is never created, and
that is exactly the documented second cause for `steps.jsontoxml.SourceUnavailable`:
"Can't be resolved (is not defined)". HTTP 500.

This policy has no deployment errors; the documented deployment error list for JSONToXML
is "None". The failure is entirely at request time.

The upstream contract change is not in the causal chain. It is real and still unverified,
which is why the verification step checks the produced XML against it, but it did not
produce this fault. On the requests where the assigning step runs, the same proxy converts
the same payload with the same policy and succeeds, which rules the contract change out as
the cause of the failures.

#### Correct remediation

Fix the flow so the variable the policy depends on exists on every request. Either move
the assigning step out of the conditional, or widen the condition. If the condition is
deliberate, then the conversion cannot be unconditional, and the policy should be guarded
by a matching `<Condition>` so it is skipped rather than faulting on the requests where
there is nothing to convert.

The `<OutputVariable>` element is already present here and should stay. The documented
rule is that it is mandatory when the `<Source>` variable is of type `string`, and the
trace shows `payload` resolves as a string. Removing it, or pointing `<Source>` at a
`message`-typed variable such as `request` or `request.content`, changes which rule
applies, so check the type before editing either one.

#### Verification

Send requests that hit the conditional and requests that skip it. Both should succeed.
Confirm the produced XML matches what the upstream contract now expects, since that
contract change is the other thing in this ticket that nobody has checked yet.

#### Common incorrect answers

Reading the fault as a problem with the client's HTTP `Content-Type` header. Neither
documented cause involves the header, and `Content-Type` is not in play.

Settling on `steps.jsontoxml.InvalidSourceType`. That code is about the type of a variable
that resolved, and it names `message` and `string` as the valid types. Nothing resolved
here, so there is no type to report.

Concluding it is `steps.jsontoxml.ExecutionFailed`, which fires when the input payload is
empty or malformed. That is the right suspicion if the contract change produced bad JSON,
but the evidence contradicts it: requests carrying the same payloads convert successfully
whenever the assigning step runs.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Chases Content-Type or the contract change | Identifies the unresolved source variable | Names SourceUnavailable, quotes both documented causes, and picks the one the trace supports |
| Diagnostic method | Guesses | Reads the policy | Reads the exact code and checks the conditional in a trace |
| Handling of uncertainty | Asserts one cause | Hedges | States that the code alone does not decide between the two causes, then says which one the trace shows |
| Quality of next step | Rewrites the contract handling | Moves the assigning step | Makes the assignment unconditional or guards the policy with a matching condition, and checks the OutputVariable rule |
| Verification | None | Retests | Tests both branches and checks the upstream contract |

**Critical failures:** attributing the fault to the client Content-Type header; removing
`<OutputVariable>` without first establishing whether `<Source>` resolves as `string`;
naming an element the JSONToXML policy does not have.

**Not a critical failure:** saying that `SourceUnavailable` names two documented causes and
that the code by itself does not identify which applies, and that the trace is needed to
choose. That is the accurate reading of the reference and earns full credit at the
Handling of uncertainty level. Observing that the fault code does not by itself settle the
question is a strength here, not a hedge. The fault code and the evidence are the same
code and the same condition, so an answer that reports them as matching is also correct.

#### References

- JSONToXML policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/json-xml-policy>
- Variables reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/variables-reference>

---

### EASY-10. HMAC policy missing a required element

#### Scenario metadata

- ID: EASY-10
- Difficulty: easy
- Primary topic: HMAC policy
- Secondary topics: signature verification, configuration review
- Product: Apigee or hybrid
- Origin: documented
- Versions: checked 2026-10-11
- Evaluation objectives: recognize a deployment-time configuration error from a runtime
  code; no traffic investigation helps
- Skills expected: apigee-support-core

#### Initial support ticket

> The deployment of our webhook receiver proxy is being rejected with an HMAC error. The
> same proxy has been running for months. We updated the secret in our secret manager and
> re-ran the bundle renderer that pulls it into the policy. We did not hand-edit the
> policy itself.

#### Initial evidence

The save returns HTTP 400. The body names `steps.hmac.MissingConfigurationElement`.
Requests to the already-deployed revision still work.

#### Expected investigation

Despite the `steps.` prefix, this appears as a deployment rejection rather than a runtime
fault in the reported case, and the first job is to establish which stage failed. If the
error came back from the save call, the policy configuration is incomplete.

#### Diagnostic evidence

The deployed bundle contains:

```xml
<HMAC name="VerifySignature">
  <Algorithm>SHA256</Algorithm>
</HMAC>
```

There is no `<SecretKey>` and no secret reference of any kind, and there is no
`<VerificationValue>`. The team updated an external secret manager, and a templating step
that previously injected the secret element now renders nothing.

#### Ground-truth resolution

The HMAC policy is missing a required element. The HMAC error reference lists
`steps.hmac.MissingConfigurationElement` among its deployment errors, which the reference
states can occur when you deploy a proxy containing the policy, so the save call is what
fails and the new revision never deployed. The currently deployed revision predates the
change and still carries the secret, which is why traffic still works.

`<SecretKey>` is the element at fault. The reference documents it as Required, states that
there is no default value for the referenced variable, and that the `ref` attribute is
itself required.

The trigger is a broken template, not the secret value. An empty rendered value removes the
element entirely, which is different from an element holding a wrong value.

That distinction is worth making explicitly: missing element, wrong value, and unresolved
variable are three different failures with three different codes.

`<VerificationValue>` is a separate and quieter problem. It is documented as Optional, and
including it is what directs the policy to check the computed signature against a known
value rather than only calculate it. Its absence produces no deployment error at all,
which is exactly why a policy named `VerifySignature` deserves a second look before anyone
concludes it verifies.

#### Correct remediation

Fix the template so the `<SecretKey>` element renders, then confirm the element is present
in the bundle before deploying.

```xml
<HMAC name="VerifySignature">
  <Algorithm>SHA256</Algorithm>
  <SecretKey encoding="base64" ref="private.webhook.secret"/>
  <VerificationValue ref="request.header.x-hub-signature-256"/>
</HMAC>
```

`<VerificationValue>` is listed here separately on purpose. Adding `<SecretKey>` alone makes
the policy compute a digest and do nothing with it. The HMAC reference states the policy
"can optionally verify the computed signature against an expected value. The optional
`VerificationValue` element (if present) directs the policy to check the computed value
against a known or given value." Without it, every webhub signature passes, and the failure
is silent.

Do not commit the secret itself. The reference documents `steps.hmac.InvalidSecretInConfig`
for a text value explicitly provided for `SecretKey`, and `steps.hmac.InvalidVariableName`
when the `SecretKey` variable lacks the `private.` prefix, so a reference is the safe shape
and an inline literal is not.

Deploy to a test environment first. This is a source change and is reversible, but a
broken HMAC policy silently rejects every webhook rather than failing loudly, so test
before production.

#### Verification

Deploy to test, send a correctly signed webhook and confirm it verifies. Then send an
incorrectly signed one and confirm it is rejected. Both checks together prove the policy
is verifying rather than merely present, which is the failure mode an absent
`<VerificationValue>` would leave in place.

The second check is only meaningful once `<VerificationValue>` is present. If the
remediation stops at `<SecretKey>`, an incorrectly signed webhook is accepted exactly like a
correctly signed one and the check cannot be performed, so a verification that requires
rejection while omitting `<VerificationValue>` is not a verification.

#### Common incorrect answers

Rotating the secret. The error is about a missing element, not a value, and the secret is
not the thing the policy complained about.

Telling them the revision deployed. It did not, and the evidence is that traffic is still
being served by the old one.

Adding the secret inline in the proxy XML. That commits a credential to source control, and
the reference documents a specific error for a text value supplied to `SecretKey`.

Treating this as a runtime fault worth tracing. The reference lists it among the deployment
errors, so no request ever reaches it.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Treats as runtime | Identifies missing element | Names `<SecretKey>` and explains why traffic still works |
| Diagnostic method | Rotates secrets | Reads the policy | Reads the policy and checks the template |
| Safety | Commits the secret | Suggests adding a value | Fixes the template and uses a `private.` reference |
| Verification | None | Tests one path | Tests both accept and reject |
| Clarity | Buries the answer | Clear | Leads with the cause, the old revision, and the optional element |

**Critical failures:** recommending committing a secret to the proxy bundle; treating the
fault as a runtime error worth tracing; naming absent elements that do not exist in the
HMAC policy schema.

#### References

- HMAC policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/hmac-policy>

---

### EASY-11. Unsupported TimeUnit blocks the revision

#### Scenario metadata

- ID: EASY-11
- Difficulty: easy
- Primary topic: Quota policy configuration
- Secondary topics: deployment errors, documentation reading
- Product: Apigee or hybrid
- Origin: documented
- Versions: checked 2026-10-11
- Evaluation objectives: find the documented list of supported time units rather than
  guessing; the error name does not enumerate them
- Skills expected: apigee-support-core

#### Initial support ticket

> Deployment rejected again after our config change. The error says the quota time unit
> is invalid. The developer wrote `minutes` because that reads better. Is that the
> problem?

#### Initial evidence

HTTP 400 on save, error name `InvalidQuotaTimeUnit`. The policy:

```xml
<Quota name="PerDay">
  <Interval>1</Interval>
  <TimeUnit>minutes</TimeUnit>
</Quota>
```

#### Expected investigation

Read the Quota policy deployment error reference, then the `<TimeUnit>` element reference,
which is the normative list: `minute`, `hour`, `day`, `week`, `month` or `year`. The
deployment-error summary is shorter than that and does not mention `year`, so a reader who
stops at the summary will omit a valid value. Taking the longer list from the element
reference is more accurate, not less. The developer is right about the cause: `minutes` is
not a valid value, and the unit is singular.

A good answer also flags that `1 minutes` is doubly wrong, since the interval of 1 with
`minute` would mean one minute rather than one day, which is probably not the intent.

#### Diagnostic evidence

On request, the developer confirms the intent was a daily limit.

#### Ground-truth resolution

`InvalidQuotaTimeUnit` fires when the `<TimeUnit>` value is unsupported. The `<TimeUnit>`
element reference is the normative list and reads: select from `minute`, `hour`, `day`,
`week`, `month`, or `year`. `minutes` is not among them.

The deployment-error table on the same page gives a shorter list that omits `year`. Both are
official, and the element reference is the one that governs what the element accepts, so
quote it rather than the table. Naming the full list including `year` is correct and should
not be marked down.

The revision was rejected, so the currently deployed revision continues to serve.

#### Correct remediation

Use the singular form matching the intent:

```xml
<Quota name="PerDay">
  <Interval>1</Interval>
  <TimeUnit>day</TimeUnit>
</Quota>
```

#### Verification

Deploy, confirm it saves, then send more requests than the limit and confirm a
`QuotaViolation`. Confirm the counter resets on the documented boundary rather than
assuming a rolling window, since the quota `type` determines the reset behavior.

#### Common incorrect answers

Accepting `minutes` as an alias. It is not documented as one, and the documented list is
singular.

Recommending `60` with `TimeUnit` minute to express an hour. That works but changes the
reset semantics depending on quota type, so the `hour` unit is clearer.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Guesses accepted values | Identifies singular/plural | Names the full list from the `<TimeUnit>` element reference, including `year` |
| Evidence and citation | None | Generic | Cites the Quota deployment error reference |
| Quality of next step | "Use minute" | Gives a value | Gives a value and asks about intent |
| Verification | None | Retests | Retests and checks reset semantics |

**Critical failures:** asserting undocumented units are accepted.

#### References

- Quota policy deployment errors:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>

---

### EASY-12. RevokeOAuthV2 rejects a timestamp before 2014-01-01

#### Scenario metadata

- ID: EASY-12
- Difficulty: easy
- Primary topic: RevokeOAuthV2 policy
- Secondary topics: timestamp units, reading the documented bound
- Product: Apigee or hybrid
- Origin: documented
- Versions: checked 2026-10-11
- Evaluation objectives: match `InvalidEarlyTimestamp` to its documented cause, a lower
  date bound, rather than to clock skew or generic token invalidity; note the code is
  documented on the RevokeOAuthV2 page and returns 500, not 401
- Skills expected: apigee-support-core

#### Initial support ticket

> Our bulk token revocation endpoint started returning 500. We call it with a
> "revoke everything issued before this timestamp" argument. The same call worked last
> month. Nothing about our clocks changed.

#### Initial evidence

```json
  {
    "fault": {
      "detail": {
        "errorcode": "steps.oauth.v2.InvalidEarlyTimestamp"
      }
    }
  }
```

HTTP response status 500.

The policy:

```xml
<RevokeOAuthV2 name="RevokeOld">
  <RevokeBeforeTimestamp ref="request.queryparam.revoke_since_timestamp"/>
</RevokeOAuthV2>
```

#### Expected investigation

The agent should look the code up and find that `InvalidEarlyTimestamp` is documented on
the RevokeOAuthV2 policy page with HTTP 500 and the cause "Timestamp cannot be earlier
than January 1, 2014." That is a fixed lower bound, not a comparison against the current
time, which is what makes the "Early" in the name misleading.

The element reference for `<RevokeBeforeTimestamp>` gives the same bound plus the other
half of the rule: the timestamp cannot be in the future either. Both halves matter,
because they are two different codes.

#### Diagnostic evidence

The failing requests omit the `revoke_since_timestamp` query parameter, so the variable
ref resolves to an empty value and the policy is handed `0`. A captured failing request
confirms the parameter is absent. Requests that pass a normal millisecond timestamp
succeed.

A second, related failure mode is worth checking because it produces the same code: one
caller sends Unix **seconds** (for example `1767225600`) where the policy documents
milliseconds. Fed to the policy as milliseconds, that value is January 1970, which is also
before the bound.

#### Ground-truth resolution

The policy received a timestamp before January 1, 2014 and refused it with
`steps.oauth.v2.InvalidEarlyTimestamp`, HTTP 500.

A zero value, or a seconds value read as milliseconds, both land in 1970 by the policy's
own reading of its input, and the lower bound rejects them. This is not clock skew, and
nothing about the deployment or the runtime clock is involved.

Note the element is optional and defaults to the current time when absent. The fault
therefore comes from a value that was supplied and resolved badly, not from omitting the
element. A missing element on its own would not produce this code.

The sibling `steps.oauth.v2.InvalidFutureTimestamp` covers the other half of the bound,
and `steps.oauth.v2.InvalidTimestamp` covers a value that is not a valid timestamp at all.
All three are 500. The three should not be collapsed into "token expired".

#### Correct remediation

Make the caller send a millisecond timestamp, and reject the call at the edge when it
does not. A missing query parameter should produce a clear client-side error rather than
being passed through as `0`.

Check the other end of the bound while you are there. A client that passes a value in the
future, for example from a device with a badly wrong clock, hits
`InvalidFutureTimestamp` instead, and both failures deserve a guard.

#### Verification

Replay the failing request with a valid millisecond timestamp and confirm it succeeds.
Then confirm a request with `revoke_since_timestamp=0` still fails, which proves the
validation is present rather than absent. Then confirm the future-dated case fails with
the other code.

#### Common incorrect answers

Treating this as clock skew and telling the team to sync clocks or widen `nbf` leeway.
There is no `nbf` involved; this policy does not set flow variables at all.

Saying the endpoint returns 401 because it is an OAuth endpoint. The documented status
for this code is 500.

Raising token lifetime. Lifetime is `exp` on the access token, a different concept from
the timestamp this policy filters on.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says clock skew or token invalid | Names the lower bound | Names the 2014-01-01 bound, 500, and the RevokeOAuthV2 page |
| Evidence and citation | None | Generic OAuth docs | Cites the RevokeOAuthV2 policy error reference |
| Diagnostic method | Blames clocks | Asks for the value | Asks for the value and checks the parameter is absent |
| Handling of uncertainty | Asserts a cause | Hedges | Separates the confirmed cause from the seconds-vs-millis variant |
| Verification | None | Retests once | Tests valid, zero, and future-dated values |

**Critical failures:** attributing the fault to clock skew or to `nbf`; quoting a 401
status for this code.

#### References

- RevokeOAuthV2 policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/revoke-oauth-v2-policy>

---

### EASY-13. JWKS verification fails because the token has no key id

#### Scenario metadata

- ID: EASY-13
- Difficulty: easy
- Primary topic: VerifyJWT with JWKS
- Secondary topics: key rotation, asymmetric verification
- Product: Apigee or hybrid
- Origin: documented
- Versions: checked 2026-10-11
- Evaluation objectives: find the documented `kid` requirement; a structurally valid token
  can still fail
- Skills expected: apigee-support-core

#### Initial support ticket

> Our identity provider rotated keys last week. Most of our traffic is fine but some
> tenants now get 401. The failing tokens look perfectly normal.

#### Initial evidence

401 responses on some tenants only. A decoded failing token header contains `alg` and
`typ` but no `kid`. A working token from another tenant has `kid`.

#### Expected investigation

The documented JWKS resolution sequence includes a step that is easy to miss: if the
inbound JWT does not include a key ID in the header, Apigee throws a fault, because
mapping `kid` to a verification key is not possible.

The key rotation in the ticket is the setup, but the rotation itself is not the fault.

#### Diagnostic evidence

The JWKS endpoint returns a valid key set. The failing tenant's tokens contain no `kid`
because their client library was configured with a single static key and omits it.

#### Ground-truth resolution

Apigee cannot map `kid` to a verification key when the token header has none, and it
faults. The token may be perfectly valid, and the signature may check out, but the
resolution step fails before verification happens.

This only affects tokens from a tenant whose client omits `kid`, which is why the failure
is partial.

#### Correct remediation

The fix belongs in the client or the identity provider: emit `kid` in the token header.
Apigee's JWKS mode requires it.

If a tenant genuinely cannot emit `kid`, that is a real constraint. In that case verify
against an explicit public key or a secret key configured directly rather than through
JWKS, and note that this removes automatic key rotation, which is a meaningful loss worth
stating rather than glossing over.

#### Verification

Confirm tokens with `kid` verify. Confirm a token without `kid` still fails under the
JWKS configuration, so the requirement is enforced. If you took the explicit-key path,
confirm rotation now needs a manual proxy change and record that.

#### Common incorrect answers

Rotating the Apigee JWKS cache. The endpoint serves valid keys.

Adding a `kid` manually in Apigee. You cannot alter the inbound token header before
verification in a way that resolves this.

Replacing JWKS with a hardcoded key without mentioning the loss of rotation. That works
but trades a real property for the fix, and the tradeoff should be stated.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Blames the JWKS endpoint | Identifies missing kid | Explains the documented resolution step |
| Diagnostic method | Rotates cache | Decodes tokens | Decodes headers and compares tenants |
| Quality of next step | Cache clear | Says emit kid | Says emit kid and offers the fallback with its cost |
| Verification | None | Retests | Tests both and states the rotation consequence |

**Critical failures:** recommending JWKS cache rotation as the fix; hiding the loss of
automatic rotation behind the explicit-key fallback.

#### References

- JWT policies overview, JWKS section:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/jwt-policies-overview>
- VerifyJWT policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jwt-policy>

---

### EASY-14. Target handshake fails against a legacy TLS backend

#### Scenario metadata

- ID: EASY-14
- Difficulty: easy
- Primary topic: TLS on target endpoints
- Secondary topics: handshake failures, network diagnosis
- Product: Apigee or hybrid
- Origin: documented, with a caveat noted below
- Versions: checked 2026-10-11
- Evaluation objectives: recognize that a handshake failure is often a protocol
  version problem rather than a network problem, and that `IgnoreValidationErrors` does
  not fix it; state honestly where the fault code is documented
- Skills expected: apigee-support-core, apigee-support-core references/security.md

#### Caveat on the fault code

`messaging.adaptors.http.flow.SslHandshakeFailed` is the one code in this file that does
not come from a policy page. It is documented in two places instead: the API Monitoring
fault code list, where it maps to the gateway fault
`FailedHandshakeWithTargetEndpoint` under the Target component, and the Configuring TLS
page, which names it directly as the result of configuring an unsupported protocol
version. It is not in the policy error index, because no policy raises it.

#### Initial support ticket

> One of our backends started returning 502 for every request. Nothing changed in Apigee.
> The backend team says nothing changed on their side either. We can reach the host on
> port 443 from the runtime.

#### Initial evidence

502 on all requests to one proxy. The target endpoint config:

```xml
<SSLInfo>
  <Enabled>true</Enabled>
</SSLInfo>
```

No `<Protocols>` element is present, so the Apigee side permits every protocol the JVM
supports. The backend advertises TLS 1.0 as its highest supported version.

If asked what the Apigee side offers, the operator confirms `<Protocols>` is absent from the
target endpoint configuration and that the runtime has not been restricted by configuration.

#### Expected investigation

A reachable port that still fails at handshake points at the TLS negotiation, not
connectivity.

Read the Configuration TLS page carefully rather than stopping at the first sentence. Its
trigger is conditional on Apigee's own configuration: "If you use these protocols in your
target endpoint configuration, the Apigee target endpoint throws the error
`messaging.adaptors.http.flow.SslHandshakeFailed`." The evidence here has an `<SSLInfo>`
carrying only `<Enabled>true</Enabled>` with no `<Protocols>` element, which means every JVM
protocol is permitted on the Apigee side. So the documented Apigee-side restriction has not
been triggered, and the reason the handshake fails is that the backend offers TLS 1.0 as its
highest version and Apigee has nothing higher to agree on.

Both readings lead to `SslHandshakeFailed`, so the code alone does not discriminate. The
distinguishing step is checking who is offering what, and the scenario supplies exactly
enough to do it.
configuring them on a target makes the target endpoint throw
`messaging.adaptors.http.flow.SslHandshakeFailed`.

The agent should establish this from the Configuring TLS reference and the monitoring
fault code list rather than from a policy error page, and should say so rather than
implying a policy raised it.

#### Diagnostic evidence

An openssl probe from the runtime host shows the backend accepts only TLS 1.0. The trace
shows `FailedHandshakeWithTargetEndpoint` with the underlying
`messaging.adaptors.http.flow.SslHandshakeFailed`.

#### Ground-truth resolution

The backend only offers TLS 1.0, which Apigee does not support. The handshake fails and
the proxy returns 502.

Be careful which documented sentence you reach for. The Configuration TLS page says Apigee
does not support TLS 1.0 or 1.1 and then describes a specific trigger: "If you use these
protocols in your target endpoint configuration." That trigger is on the Apigee side, and the
configuration here sets only `<Enabled>true</Enabled>` with no `<Protocols>`, so it is not
met. Citing the restriction as if it applied here is citing a conditional without its
condition. The failure arises from the other end of the handshake: the backend offers
nothing Apigee can agree on.

The code is `messaging.adaptors.http.flow.SslHandshakeFailed` either way, so the code is not
what discriminates between the two readings. The `<Protocols>` check is. The remediation
differs too: an Apigee-side misconfiguration is fixed in the target endpoint, a
backend-side limitation means the backend must be upgraded or Apigee pointed elsewhere.

Connectivity is fine, which is why a port check passes and confuses people.

`IgnoreValidationErrors` does not help here. It affects certificate validation, not
protocol version negotiation, so setting it changes nothing about this failure.

The `<Protocols>` element under `<SSLInfo>` exists to restrict which protocols are
offered, and when it is omitted all protocols available to the JVM are permitted. So
adding an explicit `<Protocols>` list is a way to make the client side of the negotiation
narrower, never wider. It cannot make a TLS 1.0-only backend reachable.

#### Correct remediation

The backend must support TLS 1.2 or later. That is a change on the backend side and is
the correct fix.

There is no Apigee setting that makes a TLS 1.0-only backend work, and anyone offering one
is guessing. If the backend cannot change, the options are a TLS-terminating proxy in
front of it, which is a significant architecture change and should be presented as such
rather than as a quick fix.

#### Verification

Re-test after the backend is updated, and confirm the trace no longer shows the handshake
fault. Also confirm certificate validation still occurs, since a misconfiguration that
disables validation would also produce a successful handshake and hide a worse problem.

#### Common incorrect answers

Setting `IgnoreValidationErrors` to true. It does not address protocol version.

Disabling TLS on the target to use plain HTTP. That sends client data unencrypted and is
a security regression.

Telling them to check the firewall. Connectivity is already proven good.

Adding `<Protocols>` with TLSv1.0 to make the handshake agree. It only restricts what the
client offers, and TLS 1.0 is unsupported regardless.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Blames the network | Identifies TLS | Names the TLS 1.0 restriction and the fault |
| Evidence and citation | None | One page | Cites Configuring TLS and the monitoring fault code list, and says the code is not a policy code |
| Diagnostic method | Suggests firewall checks | Checks handshake | Probes negotiated version from the runtime |
| Safety | Disables TLS | Suggests ignore-validation | Correctly states no Apigee-side workaround exists |
| Verification | None | Retests | Retests and confirms validation still enforced |

**Critical failures:** recommending `IgnoreValidationErrors` as the fix for a protocol
version failure; recommending plain HTTP as a remedy; citing a policy error reference for
a code no policy raises.

#### References

- Configuring TLS:
  <https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls>
- API Monitoring fault codes:
  <https://cloud.google.com/apigee/docs/api-monitoring/fault-codes>
- API proxy configuration reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>

---

### EASY-15. Quota counter behaves differently than the team expects

#### Scenario metadata

- ID: EASY-15
- Difficulty: easy
- Primary topic: Quota policy semantics
- Secondary topics: expectation mismatch, verification
- Product: Apigee or hybrid
- Origin: documented
- Versions: checked 2026-10-11
- Evaluation objectives: the first-pass explanation is often wrong; find the documented
  scope rule before suggesting a config change
- Skills expected: apigee-support-core

#### Initial support ticket

> We set a limit of 10,000 requests per month on our Pro tier. We are seeing around 30,000
> requests go through. Either the quota is not working or something is wrong. Please fix
> the quota.

#### Initial evidence

The proxy has a Quota policy with a monthly interval. Traffic is spread across three API
proxies in one API product.

#### Expected investigation

The first hypothesis, that the quota is broken, is weak. The agent should check the
documented scope rule before changing anything.

#### Diagnostic evidence

Checking the proxy configuration shows three proxies, each with its own Quota policy at
10,000 per month. All three enforce successfully.

#### Ground-truth resolution

The Quota policy is working. Quotas apply to individual API proxies and are not
distributed among API proxies, so three proxies with the same 10,000 limit allow roughly
30,000 requests in total.

The configuration is correct per proxy and wrong relative to the team's intent. This is an
expectation mismatch, not a fault.

#### Correct remediation

Decide where the limit should live, and be careful which of the two options you propose.

**Moving all traffic behind one proxy** gives a single limit that actually aggregates. That
works, because a quota counter belongs to a proxy.

**A shared flow is not something this documentation settles.** The Quota policy page is
explicit about the scope that matters here: "Quotas apply to individual API proxies and are
not distributed among API proxies. For example, if you have three API proxies in an API
product, a single quota is not shared across all three even if all three use the same quota
policy configuration." A counter belongs to the API proxy that contains the Quota policy.

What the documentation in reach does not say is what a Quota policy placed in a parent shared
flow does to that scope. The shared flow page describes deployment and reuse and does not
state how a policy inside a shared flow is instantiated per calling proxy, and the Quota page
does not mention shared flows at all. So an agent that proposes a parent shared flow is not
wrong, and an agent that rules it out is not right either. The graded requirement is narrower
and it is documented: the agent must say that quotas are scoped to the API proxy containing
the policy and therefore do not aggregate across the three proxies in this API product, and it
must not claim the documentation settles the shared-flow case either way.

There is no configuration trick that makes a Quota policy distribute across API proxies on the
strength of this page. A rate-limit service or an external store aggregates, and that is a
different design conversation.

So the honest answer is either aggregate by putting the traffic somewhere that is genuinely
one counter, or accept per-proxy counting and document that the effective ceiling is the
per-proxy number.

Do not raise the per-proxy number to 30,000 as a shortcut fix, because that couples the
limit to the current proxy count and silently changes the ceiling whenever a proxy is added.

#### Verification

Confirm the counter in analytics for one proxy reaches its limit and further requests from
that proxy are rejected. Then confirm the intended aggregate behavior across whichever
design you chose.

#### Common incorrect answers

Raising the limit to 30,000 per proxy. That encodes the current proxy count into the
configuration.

Concluding the quota policy is defective. It enforces exactly as documented.

Adding a spike arrest policy. That addresses bursts, not monthly totals.

Asserting that a shared flow definitively does aggregate the limit, and stopping there. The
documented scope rule is that a quota is not shared across API proxies even when all three use
the same policy configuration, and that is the part that scores. The shared-flow case is
genuinely unsettled by the documentation in reach, so an answer that proposes a parent shared
flow and then says the sources do not settle whether it aggregates is correct, not wrong. This
is a "not established" answer rather than a "wrong" one, which is why it is listed here and not
among the critical failures.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says quota is broken | Identifies multiple proxies | Explains the documented per-proxy scope rule |
| Diagnostic method | Changes config first | Counts proxies | Finds the scope rule in documentation |
| Safety | Raises limits | Suggests one option | Offers designs, rejects the naive limit increase, and distinguishes the documented per-proxy scope rule from the unsettled shared-flow case |
| Verification | None | Checks analytics | Checks counters and aggregate behavior |
| Clarity | Asserts a defect | Correct | Leads with "the quota is working" |

**Critical failures:** recommending raising the per-proxy limit as the fix; asserting the
policy is defective.

**Not a critical failure:** proposing a parent shared flow as an aggregate limit. The Quota
page documents that quotas do not aggregate across API proxies, and does not address shared
flows; the shared flow page does not state how a policy inside one is instantiated. An answer
that proposes it and flags the gap is within the evidence. One that presents it as a documented
guarantee is not, and scores 0 on technical correctness rather than failing the scenario.

#### References

- Quota policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
- Comparing Quota and SpikeArrest:
  <https://cloud.google.com/apigee/docs/api-platform/develop/comparing-quota-and-spike-arrest-policies>
