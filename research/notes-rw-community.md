# Real-world community cases: Apigee Q&A

Task: seed an evaluation scenario library with genuine community-reported Apigee
questions and answers, where the obvious first explanation is wrong or the consensus
answer is contradicted by current documentation.

Method and honesty notes are recorded per case. Anything I did not actually fetch is
marked as such and is not used to build a scenario.

---
## Retrieval log (provenance)

| Attempt | Target | Result |
| --- | --- | --- |
| curl | `stackoverflow.stackprinter.appspot.com` | TLS hostname mismatch (real network error, not 404) |
| curl | `www.stackprinter.com/export?question=65071938` | HTTP 200 but body is StackPrinter's "StackExchange server is too busy" interstitial |
| curl | `stackprinter.appspot.com/v/65071938/` | HTTP 404 (this path form is not served) |
| curl / WebFetch | `stackoverflow.com/questions/<id>` | HTTP 403, Cloudflare "Just a moment..." challenge |
| curl | `api.stackexchange.com/2.3/questions?tagged=apigee&site=stackoverflow` | **HTTP 200, 100 items, every item re-asserted to carry the `apigee` tag** |

Method used: the tag-filtered questions endpoint, sorted by votes, paged, with a
random `cb` parameter on every call. Every returned item was asserted to carry the
`apigee` tag in `tags` before being listed, which is the guard against the stale-payload
failure mode. Bodies and answers are pulled per question ID and cached under
`research/so/`.

## Confirmed cases

Every entry below was retrieved by me. Question body and answer bodies come from
`api.stackexchange.com/2.3/questions/<id>?filter=withbody` and
`.../answers?filter=withbody`, fetched per ID with a random cache-buster, cached under
`research/so/q_<id>.json` and `research/so/a_<id>.json`. Doc checks were run against
cached pages under `research/pages/` and, where the page was missing, fetched live
(recorded separately).

---

### CASE 1. SpikeArrest `5pm` accepts two calls, then rejects the rest

- URL: <https://stackoverflow.com/questions/21912316> (title "Apigee - SpikeArrest behavior")
- Platform: Stack Overflow, tag `apigee`, question score 2, **no accepted answer**,
  3 answers (top score 3 by a 2010-rep account)
- Asker's terms: `<Rate>5pm</Rate>` with `<MessageWeight ref="request.header.weight"/>`.
  Verbatim: "we understand that if we call more than 5 times this flow in a minute, the
  policy will fail in the calls after the 5th. But, when we tested it with 10 calls in
  less than 10 seconds, the policy accepts the first two calls and fails in the next
  calls. Can you explain us why is this happening? Can this be related to that the
  environment has 2 message processors and 2 routers?"
- Answer claim (top-scored, 2014): "Spike arrests aren't implemented as counts. They are
  currently implemented as rate limiting based on the time the last matching traffic was
  successfully processed. If you specify 5 per minute, it means that your requests can
  only come in one per 12 sec (1/5 minute)... **Also, each message processor tracks a
  separate time.**"
- Second answer attributes the doubling to strict round-robin across the two MPs.
- **Current documentation CONFIRMS the smoothing claim.** `pages/api-platform_reference_policies_spike-arrest-policy.txt`:
  "`(int)ps` (number of requests per second, smoothed into intervals of milliseconds)",
  "`(int)pm` (number of requests per minute, smoothed into intervals of seconds)", and
  "The policy smoothes the rate to one request allowed every 200 *milliseconds* (1000/5)."
  For 12pm it states "This sample policy allows a maximum of 12 requests per minute at the
  rate of one request per 5 *second* (60/12) interval." That is the same division the
  answer performs. Evidence (a) for the smoothing model.
- **Current documentation CONTRADICTS the "separate message processor" claim as a blanket
  statement.** Same page, `<UseEffectiveCount>` element: "If set to `true`, SpikeArrest is
  distributed in a region. That means request counts are synchronized across message
  processors (MPs) in a region. In addition, a 'sliding window' rate limiting algorithm is
  employed. This algorithm... does not 'smooth' the number of incoming requests."
  And directly under the `false` branch: "**Note:** Although the default value is `false`,
  **Apigee organizations should set this element to `true`.**" Also: "Rate smoothing is
  not supported for Apigee organizations." Evidence (d) for the 2014 "SpikeArrest is not
  distributed" framing, which is now the non-recommended configuration.
- A much later answer on the same question (score 1, 5990 rep, 2024) restates the current
  docs almost verbatim, including "multiply your calculated number of full requests per
  interval by the number of message processors". This is independent corroboration that
  the 2024 text tracks the docs.
- Resolution status: question CLOSED, answer CONFIRMED in its smoothing model and
  PARTIALLY CONTRADICTED by current docs on the per-message-processor half. A modern
  answer to the same symptom would start by asking whether `<UseEffectiveCount>` is set.
- Evidence level: (a) for smoothing; (d) for "not distributed / per-MP clocks" as a
  general statement.

---

### CASE 2. JavaScript policy intermittently exceeds 200 ms

- URL: <https://stackoverflow.com/questions/22995892> (title "Intermittent Apigee error of
  Javascript runtime exceeding limit of 200ms")
- Platform: Stack Overflow, tag `apigee`, score 2, 1 answer which **IS accepted** (score 3)
- Asker's terms, verbatim error string:

```json
{"fault":{"detail":{"errorcode":"steps.javascript.ScriptExecutionFailed"},
 "faultstring":"Execution of getlocationserviceresponse failed with error: Javascript runtime exceeded limit of 200ms"}}
```

  Asker's setup, which is the part the answer ignores: "A second API Proxy has a
  JavaScript policy that makes a call out to the first configured Apigee API Proxy to get
  back a response and process it." He has already "chopped up" his other JavaScript into
  small modules.
- Answer claim: set `timeLimit` on the `<Javascript>` policy to raise the ceiling. Nothing
  more. Evidence level (c): single accepted answer, no corroboration.
- **Fault code verified.** `steps.javascript.ScriptExecutionFailed`, HTTP 500, is in
  `.agents/skills/apigee-support-core/references/error-codes.md` line 61, sourced to
  `javascript-policy`.
- **Current documentation supports the mechanism but reveals what the answer omits.**
  `pages/api-platform_reference_policies_javascript-policy.txt`, `timeLimit` attribute row:
  "Specifies the maximum time (in milliseconds) a script can execute. For example, if a
  200 ms limit is exceeded, the policy throws this error: `Javascript. policy_name failed
  with error: Javascript runtime exceeded limit of 200ms`. **Note: For free trial
  accounts, execution time is limited to 200 ms.**" The attribute is marked **Required**.
  The fault string in the documentation is "Javascript. policy_name failed with error:
  Javascript runtime exceeded limit of 200ms", which is a different string from the
  asker's "Execution of getlocationserviceresponse failed with error: ...". Same code,
  different prefix.
- Why this is a trap: the asker's script performs a blocking HTTP call to another proxy,
  so the 200 ms budget is being spent on network wait, not on computation. Splitting the
  script does nothing, which is exactly what he observed. The accepted answer converts an
  intermittent, I/O-bound symptom into a permanent higher ceiling and would leave the
  underlying blocking call in place. And on a free trial / evaluation organization, per
  the doc note, raising `timeLimit` may not take effect at all, which the answer does not
  consider.
- Resolution status: question CLOSED, answer **CONTRADICTED/INCOMPLETE** by current
  documentation.
- Evidence level: (d) for "just raise timeLimit" as a complete fix; (a) for the code and
  the free-trial note.

---

### CASE 3. `Invalid API call as no apiproduct match found` gets four different community fixes

- URL: <https://stackoverflow.com/questions/24035609>
- Platform: Stack Overflow, tag `apigee`, score 3, 5 answers
- Asker's terms, verbatim error strings:

```json
"faultstring":"Invalid API call as no apiproduct match found",
"errorcode":"keymanagement.service.InvalidAPICallAsNoApiProductMatchFound"
```

- Answers disagree, which is the interesting part:
  - accepted, score 3, 606 rep: "Please ensure that your API bundle is associated with at
    least 1 API Product." (proxy -> product direction)
  - score 3, 31 rep: "Most likely your API Key is not associated with a product bundle. Go
    to the Developer Apps ... check that the product you are trying to access is indeed
    listed in the products list" (app -> product direction)
  - score 2: "Api key Approval at the time of creating product you selected manual select it
    automatically"
  - score 1: add the resource path to the product's `paths`
  - score **-3**: "If an oauth policy is added then trace session doesn't work"
- **Fault code verified with a caveat that matters.** The code in the asker's payload is
  `keymanagement.service.InvalidAPICallAsNoApiProductMatchFound`. What the local index
  actually contains is `steps.oauth.v2.InvalidAPICallAsNoApiProductMatchFound`, HTTP 401,
  at `error-codes.md` line 132, sourced to the delete-oauth-v2-info policy page. So the
  error-code reference has it under the `steps.oauth.v2.` prefix, not the
  `keymanagement.service.` prefix the asker saw. The asker's string is the 2014-era
  Apigee Edge prefix.
- Current documentation: the `InvalidAPICallAsNoApiProductMatchFound` row is a pointer,
  not a cause. It reads "Please see Oauth2.0 Access Token Verification throws 'Invalid API
  call as no apiproduct match found' error for information about..." The row does not
  enumerate the conditions, so none of the four community fixes can be confirmed from the
  index row alone.
- Resolution status: question CLOSED, answer **UNVERIFIED**. The accepted answer is
  plausible and has the highest score, but the equal-scored answer names a different link in
  the chain (app -> product rather than proxy -> product), and the negative-scored answer
  is wrong. A scenario built on this must make the agent enumerate the chain rather than
  accept the top answer.
- Evidence level: (c) for the accepted answer; (a) for the code, with the prefix caveat.

---

### CASE 4. `error.content` is where the OAuth error text lives when `GenerateResponse` is off

- URL: <https://stackoverflow.com/questions/25277185> (title "How to handle OAuth 2.0 policy
  Errors when NOT using <GenerateResponse/> tag?")
- Platform: Stack Overflow, tags `oauth-2.0`, `apigee`, score 2, **1 answer, no accepted
  answer**
- Asker's terms: he sets `<GenerateResponse enabled="false"/>` and asks "What variables are
  set when an OAuth policy fails?? how to know that an OAuth policy has failed? so far, I
  know that variable fault.name seems to have the error code, but the error description is
  not in error.message variable." He cites apigee.com URLs (Apigee Edge era).
- Answer claim: with `continueOnError="false"`, processing jumps to `FaultRules`, and in a
  FaultRule these variables are set:

```text
fault.name      = "InvalidAccessToken"
fault.category  = "Step"
fault.subcategory = "Execution"
error.state     = PROXY_REQ_FLOW
error.content   = {"fault":{"faultstring":"Invalid access token","detail":{"errorcode":"oauth.v2.InvalidAccessToken"}}}
```

  and "you could use JSONPath to extract `$.fault.faultstring` and
  `$.fault.detail.errorcode`".
- **Current documentation SUPPORTS this.**
  `pages/api-platform_fundamentals_what-you-need-know-about-policy-errors.txt` is the
  policy-error page; the `error.content` variable holding the serialised fault payload and
  the JSONPath extraction pattern are the documented way to build a custom error response.
  `error.code` / `error.message` / `error.name` are documented as the flat aliases, which
  is precisely why the asker could not find the description in `error.message`.
- **Fault code verified.** `oauth.v2.InvalidAccessToken` appears in
  `.agents/skills/apigee-support-core/references/error-codes.md` (OAuthV2 policy rows).
- Resolution status: question CLOSED, answer **CONFIRMED** by another source (official
  policy-error documentation), though the accepted-answer marker is absent because nobody
  accepted it.
- Evidence level: (b).

---

### CASE 5. 502 "Unexpected EOF at target" at exactly two minutes, with no answer at all

- URL: <https://stackoverflow.com/questions/68314564>
- Platform: Stack Overflow, tags `node.js`, `express`, `request`, `apigee`, score 4,
  **0 answers**
- Asker's terms, verbatim payload:

```json
{"fault":{"faultstring":"Unexpected EOF at target",
 "detail":{"errorcode":"messaging.adaptors.http.flow.UnexpectedEOFAtTarget"}}}
```

  And the asker's own reasoning, which is correct: "This problem occurs exactly 2 minutes
  into the request, so I assume the timeout is the problem. In my version of node, the
  default timeout is 2 minutes. The 502 error is not logged anywhere on the backend. The
  backend actually fulfills the request and logs a 200 Ok in about 4 minutes." He then
  raises the Node timeout to 10 minutes and says "The server now responds with 503 if the
  inbound request exceeds the timeout. This solves the problem, but there are still things
  I don't quite understand."
- No community answer exists, so there is nothing to be wrong. This is a
  question-only case.
- **Official playbook fetched live by me** (not previously in `research/pages/`), saved as
  `pages/api-platform_troubleshoot_playbooks_runtime_unexpected-eof-at-target.txt`, HTTP 200,
  209850 bytes, page footer "Last updated 2026-10-09 UTC":
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/runtime/unexpected-eof-at-target>
  It documents the payload as
  `{"fault":{"faultstring":"Unexpected EOF at target","detail":{"errorcode":"messaging.adaptors.http.flow.UnexpectedEOFAtTarget","reason":"TARGET_READ_UNEXPECTED_EOF"}}}`,
  adds a `reason` the asker's payload does not have, and gives two causes:
  1. **Keep-alive timeout mismatch.** "By default, Apigee X uses a value of 60 seconds for
     the keep alive timeout property." The failure requires Apigee to have *re-used* a
     pooled connection (`useCount`, `bytesRead=0`, `bytesWritten=1303` in the sample
     `java.io.EOFException: eof unexpected`) whose keep-alive threshold expired on the
     backend while the request was in flight. Resolution: "Ensure that the keep alive
     timeout property is always lower on Apigee ... compared to that on the backend server."
  2. **AWS NLB cross-zone load balancing with client IP preservation behind NAT**, which
     "will break both connections" and "must intermittently occur".
- **Fault code verified against a cached page.** `messaging.adaptors.http.flow.UnexpectedEOFAtTarget`
  is in `research/pages/mon_fault-codes.txt` line 81. It is **not** in
  `.agents/skills/apigee-support-core/references/error-codes.md`, because that index covers
  policy fault codes and this one is raised by the HTTP target adaptor, not a policy.
- Why it is still useful: the documented causes do **not** cover the asker's symptom, which
  is a symmetric 120-second wall with a fresh long-lived request. The asker also states
  "I've also raised keep-alive on the backend as suggested by the Apigee docs. It had no
  effect on the problem", which is the opposite of the playbook's direction (raise Apigee's
  value relative to the backend's, or rather keep Apigee's lower). I found **no** official
  document stating an Apigee-side 120-second request timeout, so a scenario must not assert
  one. The honest position is: the fault is Apigee-side because the fault code and fault
  source say so, the documented causes must be checked and can be ruled out, and the
  remaining explanation is undocumented.
- Resolution status: question CLOSED with **no answer**. answer UNVERIFIED (none exists).
- Evidence level: (a) for the code, symptom and two documented causes; (c)/none for the
  specific two-minute explanation.

---

### CASE 6. SpikeArrest "cannot be synchronised across MPs" — accepted answer now contradicted

- URL: <https://stackoverflow.com/questions/23298849> (title "Apigee SpikeArrest Sync
  Across MessageProcessors (MPs)")
- Platform: Stack Overflow, tags `backend`, `apigee`, `throttling`, score 1, 2 answers,
  **the second one IS accepted** (score 1, 2010-rep account)
- Asker's terms: `<Rate>3pm</Rate>` with an `<Identifier>`. Verbatim: "I have a rate of
  3pm, which means 1 hit each 20sec... The problem is that instead of 1 successful hit
  every 20sec I get 6 successful ones in the range of 20sec and then the SpikeArrest
  error, meaning it hit once each MP in a round robin manner. This means I get 6 hit per
  20 sec to my api backend instead of the desired 1 hit per 20sec. Is there any way to
  sync the spikearrests across the MPs? ConcurrentRatelimit doesn't seem to help."
- **Accepted answer claim, verbatim: "SpikeArrest has no ability to be distributed across
  message processors."** Its whole prescription is to abandon SpikeArrest: use the Quota
  policy, set it Distributed and Synchronized, and accept that "you can't set a quota to
  have a 'per second' value on a distributed quota"; "The best you can do is per minute".
  It also floats a non-distributed quota and warns that would mean "calls that land on some
  MPs will be rejected while others will be accepted, which can be confusing to your
  developers."
- **CURRENT DOCUMENTATION CONTRADICTS THE HEADLINE CLAIM.**
  `pages/api-platform_reference_policies_spike-arrest-policy.txt`, `<UseEffectiveCount>`:
  "If set to `true`, SpikeArrest **is distributed in a region**. That means request counts
  are **synchronized across message processors (MPs) in a region**. In addition, a 'sliding
  window' rate limiting algorithm is employed. This algorithm provides consistent rate
  limit behavior and does **not** 'smooth' the number of incoming requests that can be sent
  to the backend. If a burst of requests are sent in a short time interval, they are allowed
  as long as they do not exceed the configured rate limit."
  And: "**Note:** Although the default value is `false`, Apigee organizations should set
  this element to `true`.**" Also: "Rate smoothing is not supported for Apigee
  organizations."
- The contradiction is total, not partial. Under the current documented configuration the
  asker's `3pm` is enforced as 3 per minute across the whole region, with no smoothing and
  no 6x multiplication. Every branch of the accepted answer's plan (leave SpikeArrest, move
  to a distributed Quota, live with per-minute granularity, accept confusing partial
  rejection) exists only because of the default `false`.
- The comparing-policies page also changed. `pages/api-platform_develop_comparing-quota-and-spike-arrest-policies.txt`
  now describes SpikeArrest as "Lets you choose between a smoothing algorithm or an
  effective count algorithm. The former smooths the number of requests that can occur in a
  specified period of time, and the latter limits the total number of requests that can
  occur within a specified time period, no matter how rapidly they are sent in succession.
  **Smoothing is not coordinated across Message Processors.**"
- Citation trap found while checking. Both this question and
  <https://stackoverflow.com/questions/65071938> cite
  `docs.apigee.com/api-platform/develop/comparing-quota-spike-arrest-and-concurrent-rate-limit-policies`.
  I fetched it: HTTP 200, 175233 bytes, and the rendered title is
  "Comparing Quota and SpikeArrest policies | **Apigee Edge** | Apigee Docs" with an
  Edge-for-Private-Cloud version selector (v4.53.01 etc). That URL now serves **Edge /
  OPDK** documentation, not Apigee X. Searching the returned HTML: `UseEffectiveCount`
  appears 0 times, `Message Processor` 0 times, `smoothed` 0 times, `token bucket`
  0 times. The Apigee X equivalent has a different slug and does contain all of those.
- Resolution status: question CLOSED, answer **CONTRADICTED by current documentation**.
  Evidence level: **(d)** for the accepted answer's headline claim as of today; (a) for the
  correction.
- This is the strongest case in the set: high-reputation, accepted, technically confident
  answer, fully consistent with how the product worked in 2015, now wrong.

---

### CASE 7. Keystore upload fails with `CertNotFound` — key size, modulus and filename are all red herrings

- URL: <https://stackoverflow.com/questions/21632781> (title "apigee key store and
  certificate upload issues")
- Platform: Stack Overflow, tags `keystore`, `apigee`, score 1, 4 answers, **no accepted
  answer**
- Asker's terms, verbatim payload:

```json
{
  "code" : "messaging.config.beans.CertNotFound",
  "message" : "Cert with name : /tmp/extract6784335744378261087.tmp/myCert.pem not found in key store : {1} in env : {2}",
  "contexts" : [ ]
}
```

  Asker's own hypothesis, and it is the obvious one: "I respect the limit of 2048 bits.
  Is-there any reason why it fails?" He had already excluded the simplest causes: the same
  JAR process "works fine" with his old 1024-bit sha1WithRSA cert, and he verified the
  cert/key moduli match:
  `openssl x509 -noout -modulus -in myCert.pem | openssl md5 ; openssl rsa -noout -modulus -in myKey.pem | openssl md5`.
- Answer claims, in order of plausibility to a reader:
  1. "Apigee Edge supports key sizes up to 2048 bits." then verify the md5 of the cert and
     key moduli match. The asker replies that they already do.
  2. "Apigee Edge currently uses Java 6 which does not support TLS 1.2." (about the second,
     unrelated question).
  3. "In your descriptor.properties inside the 'jar' did you specify just the certificate
     file name or the complete path?"
  4. The closing comment, verbatim: "Topic closed - issue found - **extended attribute with
     OID as long integer is the root cause**"
- The real cause is in answer 4 and nowhere else. The message text
  `messaging.config.beans.CertNotFound` / "Cert with name ... not found in key store" sends
  you to an alias, filename or keystore-mismatch investigation. The actual defect is in how
  the X.509 extension block encodes an OID. The asker's new cert is the only one with
  `X509v3 Extended Key Usage: critical / TLS Web Client Authentication`; the working one had
  no X509v3 extensions at all.
- Two extra traps in the same payload. The `message` string contains **unexpanded template
  placeholders** — "in key store : `{1}` in env : `{2}`" — so even the parts that should
  identify the store and the environment do not. And `CertNotFound` is **not** in
  `.agents/skills/apigee-support-core/references/error-codes.md`; it is absent from
  `research/pages/` too, the nearest hit being the unrelated
  `messaging.config.beans.InvalidExpiryDateForCacheEntry` in `pages/mon_fault-codes.txt`
  line 108. It is a provisioning-time config-bean code, not a runtime policy code.
- The TLS 1.2 answer is now **flatly outdated**. "Apigee Edge currently uses Java 6" has
  been untrue for years and Edge itself is end-of-life; an Apigee X or hybrid agent should
  not repeat it.
- Resolution status: question CLOSED, answer **CONFIRMED** by the asker's own closing
  comment. Evidence level: (c) — single self-reported resolution, no documentation and no
  second source.
- Caveat for scenario construction: this is Apigee Edge for Private Cloud circa v4.15. The
  diagnosis transfer, not the product, is what generalises.

---

### CASE 8. Quota counter scope — accepted answer is quoted almost verbatim by current docs, and the runner-up is contradicted

- URL: <https://stackoverflow.com/questions/21615609> (title "Quota counters : what makes
  them distinct? Are there additional filters on top of the Identifier field?")
- Platform: Stack Overflow, tags `quota`, `rate-limiting`, `apigee`, score 1, 2 answers,
  first one accepted (score 2, 606 rep)
- Asker's terms: three flows A, B, C in one bundle all referencing one policy named
  `QuotaLimitPolicy`, with the increment trace spelled out. "More generally, what makes a
  quota counter distinct in addition to the Identifier?"
- Accepted answer: "No, only 1 is maintained. Within a bundle, all references to the same
  policy use the same counter... The distinction is at the policy name level per API
  bundle. If you want to create separate counters for various flows in the same bundle,
  you need to create separate policies with different `name=` attributes. Furthermore, I
  don't believe I can share a single quota counter across multiple API bundles for a given
  environment using the Quota policy."
- **CONFIRMED by current documentation, to an unusual degree.**
  `pages/api-platform_reference_policies_quota-policy.txt`, section "How quotas are
  counted if no API products are in use", reproduces the asker's worked example almost
  word for word:

```
For example, you create a Quota policy named MyQuotaPolicy with a limit of 5 requests and place it on multiple flows (Flow A, B, and C) in the API proxy. Even though it is used in multiple flows, it maintains a single counter that is updated by all instances of the policy:
- Flow A is executed -> MyQuotaPolicy is executed and its counter = 1
- Flow B is executed -> MyQuotaPolicy is executed and its counter = 2
- Flow A is executed -> MyQuotaPolicy is executed and its counter = 3
- Flow C is executed -> MyQuotaPolicy is executed and its counter = 4
- Flow A is executed -> MyQuotaPolicy is executed and its counter = 5
The next request to any of the three flows is rejected because the quota counter has reached its limit.
```

  and adds "The name of the quota counter is based on the `name` attribute of the policy."
  Same page, "Alternatively, you can define multiple Quota policies in your API proxy and
  use a different policy in each flow. Each Quota policy maintains its own counter, based
  on the `name` attribute of the policy." Evidence (a).
- The docs also flag the reuse as an antipattern: "Using the same Quota policy in more than
  one place in an API proxy flow, which can unintentionally cause Quota to run out faster
  than you expected, is an anti-pattern."
- **The runner-up answer is contradicted.** It says "You should be able to share a Quota
  counter across API proxies by using Quotas along with API products... then the counter
  should be shared across those two proxies" and points at an `apigee.com` URL. The
  current page opens with the opposite: "**Quotas apply to individual API proxies and are
  not distributed among API proxies. For example, if you have three API proxies in an API
  product, a single quota is not shared across all three even if all three use the same
  quota policy configuration.**" What the current docs do describe is a different
  mechanism with a different name: the `quotaCounterScope` attribute on the API product,
  `PRODUCT` or `PROXY`, which changes which counter an operation's traffic increments.
  Evidence (d) for the runner-up's "should be able to share across proxies".
- Resolution status: question CLOSED, accepted answer **CONFIRMED** by another source
  (official docs), runner-up **CONTRADICTED**.
- Evidence level: (a)/(b) for the accepted answer; (d) for the runner-up.

---

### CASE 9. "404 after 10 secs" is not a timeout, and the accepted answer's timeout defaults are stale

- URL: <https://stackoverflow.com/questions/23344715> (title "what is the apigee target
  default timeout , I am seeing 404 after 10 secs")
- Platform: Stack Overflow, tag `apigee`, score 1, 1 answer (score 2, 2010 rep),
  **no accepted answer**
- Asker's terms, verbatim and in full: "what is the APIGee target URL default timeout ? I
  am seeing 404 after 10 secs on my services and what is the way to change default time
  outs"
- Answer claim: "**404s generally indicate that your URL is incorrect -- this means that the
  resource was not found, not that the backend timed out.** The target timeouts can be
  modified using TargetEndpoint/HTTPTargetConnection... The defaults are shown (**connect
  default is 1 minute and I/O defaults to 2 minutes**)."
- **The status-code claim is CONFIRMED and is now fully documented.**
  `pages/api-platform_reference_endpoint-properties-reference.txt`:
  - `connect.timeout.millis`, default `3000`: "Target connection timeout. Apigee returns
    an HTTP `503` status code if a connection timeout occurs."
  - `io.timeout.millis`, default `55000`: "If a timeout happens while writing the HTTP
    request or reading the HTTP response, `504 Gateway Timeout` is returned."
  A timeout is therefore a 503 or a 504. It is never a 404. The answer's core point is
  right and the asker's premise is wrong. Evidence (a).
- **The default values in the answer are OUTDATED.** Current documented defaults are 3000 ms
  connect and 55000 ms I/O, not 60000 ms and 120000 ms. A 10-second 404 cannot be either
  default expiring, which makes the answer's arithmetic a second, independent reason to
  reject the timeout theory. Evidence (d) for the 2015 numbers, (a) for the current ones.
- Newly fetched official playbook backing this, saved as
  `pages/api-platform_troubleshoot_playbooks_504-target-read-timeout.txt` (HTTP 200,
  166880 bytes, title "504 Gateway timeout - Target read timeout"):
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/runtime/504-target-read-timeout>
  It gives the payload
  `{"fault":{"faultstring":"Gateway Timeout","detail":{"errorcode":"messaging.adaptors.http.flow.GatewayTimeout","reason":"TARGET_READ_TIMEOUT"}}}`
  and states "The default target read timeout value (`io.timeout.millis`) is 55 seconds",
  with "300 seconds is the maximum limit". Note the documented worked example raises the
  timeout to exactly `120000` ms, i.e. two minutes.
- **URL finding worth recording.** I first guessed
  `.../troubleshoot/playbooks/network/504-target-read-timeout` and
  `.../playbooks/network/504-target-connect-timeout`. Both returned **HTTP 200 with a
  generic `<title>Apigee | Google Cloud Documentation</title>` and no article body** —
  Google Cloud soft-404s. The real slugs are
  `playbooks/runtime/504-target-read-timeout` and
  `playbooks/runtime/vpc-503-target-connect-timeout`. A status-code-only check would have
  declared these pages found. The bad files were deleted; the good ones are saved.
- Also relevant from the same reference page, for the 300-second ceiling:
  `api.timeout` "Configure the timeout for individual API proxies (in milliseconds)... The
  specified timeout must be **shorter than the standard Message Processor timeout of 300
  seconds**... You cannot set this property with a variable." And its interaction: "Before
  connecting to a target endpoint, the Message Processor determines the lesser of
  (`api.timeout` - elapsed time from the start of the request) and `io.timeout.millis`."
  So raising `io.timeout.millis` above 300 000 is futile, and if `api.timeout` is unset the
  timeout comes from the Ingress.
- Resolution status: question CLOSED, answer **CONFIRMED on its central claim and
  CONTRADICTED on its stated defaults**.
- Evidence level: (a) for the status-code mapping and current defaults; (d) for the two
  default values quoted in 2015.

---

### CASE 10. Hybrid API calls time out because the Istio ingress LoadBalancer never bound an external IP

- Platform: **official Google Cloud documentation**, not a community report. Retrieved live
  by me during this session, not previously cached.
- URL: <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/ingressgateway/api-calls-fail-timeout-errors>
  Saved as `pages/api-platform_troubleshoot_playbooks_api-calls-fail-timeout-errors.txt`,
  HTTP 200, 174125 bytes. Scope line on the page: "This page applies to Apigee and
  **Apigee hybrid**."
- Symptom, verbatim: "The client applications get timeout errors as a response for API calls
  on Apigee hybrid." Error strings, verbatim:

```
* Connection failed
* connect to 34.84.67.39 port 443 failed: Operation timed out
* Failed to connect to example.apis.com port 443: Operation timed out
* Closing connection 0
curl: (7) Failed to connect to example.apis.com port 443: Operation timed out
```

  and during installation:

```
Error from server (Invalid): error when applying patch:
... Name: "istio-init-crd-10-1.4.6", Namespace: "istio-system"
The Job "apigee-resources-install" is invalid : spec . template : Invalid value : core . PodTemplateSpec { ObjectMeta : v1 . ObjectMeta { Name : "apigee-resources-install" , ...
```

- The trap: every one of those strings looks like a backend network problem, a DNS problem,
  or a firewall problem, and the obvious first move is to test reachability of the backend.
  The documented root cause is that the `istio-ingressgateway` Service is stuck:

```terminal
kubectl get services -n istio-system
NAME                   TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)                                                     AGE
istio-ingressgateway   LoadBalancer   10.198.5.104   <pending>     15020:31927/TCP,12h ... 80:31381/TCP,443:31391/TCP ...
```

  with two documented causes: "Jobs in erroneous/pending state in istio-system namespace",
  and "Incorrect IP address range assigned to external load balancer" configured in
  `istio-operator.yaml`. Resolution is to inspect `kubectl get jobs -n istio-system` and
  delete the failed jobs.
- Why it earns a scenario: the fault surface looks like an application-network fault and
  the fix is a Kubernetes object in a different namespace that has nothing to do with the
  proxy being called. Evidence level (a). No community corroboration needed; this is the
  reference behaviour.

### URL / soft-404 findings accumulated in this session

| URL attempted | HTTP | Verdict |
| --- | --- | --- |
| `stackoverflow.stackprinter.appspot.com/v/<id>/` | 000 | TLS hostname mismatch, real network error |
| `www.stackprinter.com/export?question=<id>` | 200 | Body is a "server is too busy" interstitial, retried, never recovered |
| `stackprinter.appspot.com/v/<id>/` | 404 | Path form not served |
| `stackoverflow.com/questions/<id>` | 403 | Cloudflare challenge, via curl **and** via WebFetch |
| `.../troubleshoot/playbooks/network/504-target-read-timeout` | 200 | **Soft 404**, generic title, no body |
| `.../troubleshoot/playbooks/network/504-target-connect-timeout` | 200 | **Soft 404**, generic title, no body |
| `.../troubleshoot/playbooks/runtime/504-target-read-timeout` | 200 | Real page |
| `.../troubleshoot/playbooks/runtime/vpc-503-target-connect-timeout` | 200 | Real page |
| `.../troubleshoot/playbooks/runtime/unexpected-eof-at-target` | 200 | Real page |
| `.../troubleshoot/playbooks/ingressgateway/api-calls-fail-timeout-errors` | 200 | Real page |
| `docs.apigee.com/api-platform/develop/comparing-quota-spike-arrest-and-concurrent-rate-limit-policies` | 200 | Real page, but **Edge / OPDK** docs, not Apigee X |

---

### CASE 11. KVM `<Scope>` mismatch and `<Parameter ref>` vs literal — two different bugs with one symptom

Three separate Stack Overflow questions collapse into the same reported symptom,
"my variable is always empty", and each has a different cause. This is the single most
useful cluster in the set.

#### 11a. Wrong `<Scope>` — the map exists but the policy is looking in another namespace

- URL: <https://stackoverflow.com/questions/21897932> ("How do you use a KeyValueMap created
  through platform API inside a KeyValueMapOperations policy")
- Platform: Stack Overflow, tag `apigee`, score 1, 3 answers, **first accepted** (score 2)
- Asker's terms: he created the map with the **API-scoped** Management API URL
  `https://api.enterprise.apigee.com/v1/o/{org_name}/apis/{api_name}/keyvaluemaps`, then
  wrote a policy with `<Scope>organization</Scope>` and reported "I tried adding a
  mapIdentifier="countrymap" to the definition (based on the samples) but it still does
  not see it... The policy works if I add an `<InitialEntries>` definition to the code
  above." That last sentence is the trap: `<InitialEntries>` makes the policy **create** the
  map, so the policy appears to work. It works because the policy wrote to it, not because
  it read it.
- Accepted answer: "As you mentioned, you put the KeyValueMap in the scope of the api. To
  access that KVM, you'll need to use `<Scope>apiproxy</Scope>`". Confirmed by a second
  answer and by a late third answer.
- **CONFIRMED.** `pages/api-platform_reference_policies_key-value-map-operations-policy.txt`
  scopes a KVM policy to proxy, environment, or organization, and the map must exist in
  the scope the policy declares.
- **The third answer is subtly wrong in a way that looks most thorough.** It prescribes
  both fixes at once: `<Scope>apiproxy</Scope>` *and* `<Parameter ref="apigee.countryCode">`.
  The `ref` resolves to a flow variable named `apigee.countryCode`, so it only works by
  accident of that variable existing. Per the same page, `<Parameter ref=...>` means
  "Specifies the name of a variable whose value contains the **exact name of the key** you
  want to create, get, or delete", and "Whether you're getting, updating, or deleting a
  key/value entry, the key name must match the name of the key in the KVM."
- Resolution status: CLOSED, accepted answer CONFIRMED.
- Evidence level: (b).

#### 11b. `ref` on `<Parameter>` silently looks up a variable instead of a key

- URL: <https://stackoverflow.com/questions/27850597> ("Organization level key value map
  operation in apigee")
- Platform: Stack Overflow, tag `apigee`, score 1, 1 answer, **it IS accepted** (score 3)
- Asker's terms: `<Scope>organization</Scope>`, `mapIdentifier="ipAddresses"`, and
  `<Get assignTo="myvar" index="1"><Key><Parameter ref="entry.Development"></Parameter>`.
  Verbatim: "whenever I run a trace on this, myVar is always empty. I've tried various
  values for the Parameter ref such as `entry`, `Development`, `entry.Development`. But
  nothing seems to work."
- Accepted answer, verbatim: "the issue was I was using `<Parameter ref="k1"></Parameter>`.
  To retrieve the value when in fact it should be `<Parameter>k1</Parameter>`"
- **CONFIRMED.** The `<Parameter>` attribute table in the KVM policy page:
  `ref | Specifies the name of a variable whose value contains the exact name of the key
  you want to create, get, or delete. | N/A | **Required if no literal value is given
  between the opening and closing tags.**` The page restates it in "Specifying and
  retrieving key names": "if the key name in the KVM is `my_key`, you can either specify
  the literal value with `<Parameter>my_key</Parameter>` or specify a variable that
  contains the exact value ... like this: `<Parameter ref="variable.containing.foo"/>`."
- Why this one bites: the three things the asker tried (`entry.Development`, `entry`,
  `Development`) were all *key names*, and all three were being used as *variable names*.
  Every attempt was syntactically valid XML, deployed cleanly, and returned nothing. There
  is no error to debug.
- Free extra trap found on the same page, twice: "**Note:** The name `ratelimit` is
  reserved." for KVM keys.
- Resolution status: CLOSED, accepted answer CONFIRMED by another source.
- Evidence level: (a)/(b).

---

### CASE 12. Keystore/cert and deployment-tooling cases, lower value, recorded for completeness

#### 12a. Deploy tool succeeds for two artefacts and silently skips the third

- URL: <https://github.com/apigee/devrel/issues/267> — "deploy.sh
  (references/gcp-sa-auth-shared-flow) doesn't create shared flow in apigee x"
- Platform: GitHub, `apigee/devrel`, **closed, state_reason: completed**, 5 comments,
  opened 2021-05-03, closed 2021-05-11. Retrieved with `research/gh-issue.sh`, saved to
  `research/issues/apigee_devrel-267.txt`.
- Asker's terms, verbatim: "it creates a proxy and kvm, but it doesn't create any shared
  flow." The log shows no error, only:
  `[INFO] X/hybrid patch: adding kvm: gcp-sa-devrel` and then `[INFO] kvm admin status 404`
  followed by normal progress into "Configuring API Proxy".
- Maintainer answer (association=COLLABORATOR), verbatim: "My assumption is that the KVM
  admin proxy is not reachable from your machine or that the `APIGEE_X_HOSTNAME` does not
  correspond to the hostname that you have on your eval env group."
- Confirmed by the reporter: "I am using eval version, on eval proxies are only accessible
  from vm machine, so this could be the reason." The documented workaround from the
  maintainer is to add a hostname resolving to the internal IP to the environment group
  (he suggests a `nip.io` name), set `APIGEE_X_HOSTNAME` to it, and re-run the deploy from
  inside the private network.
- Why it earns a slot: a deployment tool reported success, two of three artefacts landed,
  and the third vanished with a single `404` buried in informational logging. The obvious
  reading is "the shared flow bundle is malformed" or "shared flows are unsupported on
  Apigee X". Neither is true.
- Resolution status: CLOSED as completed. Answer CONFIRMED by reporter.
- Evidence level: (b).

#### 12b. Maven deploy: "connect timed out" is a network fact, not a proxy fact

- URL: <https://stackoverflow.com/questions/34020846> ("Unable to deploy API bundle on
  Apigee using Maven"), score 3, 1 answer, **accepted**, score 2, 18100-rep account.
- Verbatim error: `Failed to execute goal io.apigee.build-tools.enterprise4g:apigee-edge-maven-plugin:1.0.0:deploy (install-bundle-step) ... MojoExecutionException: connect timed out`,
  caused by `java.net.SocketTimeoutException: connect timed out`.
- The asker had already done the right diagnostic work: "I notice that build(zip file) is
  created properly inside target folder, but it's not getting deployed on apigee. Also i
  would mention that i am using the setup behind my corporate proxy".
- Answer: the error is emitted "when the system is trying to connect to a server, but
  cannot", for one of two reasons: the host is wrong in the profile configuration
  `<apigee.hosturl>`, or the machine cannot reach it (corporate outbound proxy). Evidence
  level (b). Plugin coordinate `io.apigee.build-tools.enterprise4g:apigee-edge-maven-plugin`
  is the Edge-era plugin and no longer the supported path; a current agent should not repeat
  that coordinate.

#### 12c. CI/CD: identical bundles still create a revision

- URL: <https://stackoverflow.com/questions/74275432> ("Automate Apigee API Proxy Deployment
  in CI/CD Pipeline"), tags `google-cloud-platform`, `devops`, `pipeline`,
  `continuous-deployment`, `apigee`, score 1, 1 answer, no accepted answer.
- Asker's terms: "I want to avoid excessive API Proxy Bundles from being created and
  deployed when there are no changes to be made. I've already tested, and I see that
  identical bundles still create a new revision."
- Answer (score 1, 88 rep): diff the repo and only redeploy changed proxies, sharing
  upstream, target servers and shared flows, passing a `CHANGES` variable into the pipeline.
  `git diff --name-only $CI_COMMIT_SHA..$CI_COMMIT_BEFORE_SHA > /changes.txt`
- Evidence level (c): single uncorroborated answer, and note that a related official
  antipattern now exists, "Manage resources without using source control management"
  (`/apigee/docs/api-platform/antipatterns/no-source-control`), which reinforces the
  direction of the answer without confirming its mechanism.

---

### CASE 13. The top answer's advice is now a documented antipattern (RaiseFault) and the runner-up is wrong

- URL: <https://stackoverflow.com/questions/21119190> ("Raising a custom fault in Apigee"),
  tag `apigee`, score 1, 2 answers, **no accepted answer**.
- Asker's terms: he puts a `<FaultRule>` with `<Condition>(flow.param.apikey)=NULL</Condition>`
  **inside** a `GetOAuthV1Info` policy definition, and asks "Is this the correct way to do
  it?"
- Top answer (score 2, 1025 rep): the API-key policies "will raise a fault if the key is
  null or not passed. There is no need to call RaiseFault explicitly", and then suggests a
  pre-emptive check with a conditional `<Step>` invoking a `RaiseFault` policy carrying a
  custom XML `<FaultResponse><Set><Payload>`.
- Runner-up (score 1): "I believe handling Faults for policies has been changed a bit now.
  But has not been reflected properly in the policy's schema's or in the Apigee docs.
  Defining Fault rules within the policy/step definition is not working now." This is
  **wrong** and it is the kind of wrong that costs a day. Policy-level `<FaultRules>` are
  documented; `pages/api-platform_fundamentals_what-you-need-know-about-policy-errors.txt`
  shows `<FaultRules>` blocks nested inside policy definitions, and the API proxy
  configuration reference documents them.
- **The top answer is now discouraged.** I fetched
  <https://cloud.google.com/apigee/docs/api-platform/antipatterns/raise-fault-conditions>
  ("Antipattern: Use the RaiseFault policy under inappropriate conditions", HTTP 200,
  167148 bytes, "applies to Apigee and Apigee hybrid", last updated 2026-10-09), saved as
  `pages/api-platform_antipatterns_raise-fault-conditions.txt`:
  - Impact: "the `x_apigee_fault_code` and `x_apigee_fault_policy` variables are
    overwritten. In API Monitoring, the Fault Code and Fault Policy are overwritten. This
    behavior makes it difficult to troubleshoot and determine which policy is the true cause
    of the failure."
  - Best practice: "**When an Apigee policy raises a fault and you want to customize the
    error response message, use the AssignMessage or JavaScript policies instead of the
    RaiseFault policy.** The RaiseFault policy should be used in a non-error flow."
  So the answer's *custom-error-payload* pattern, used on top of a policy that already
  faults, destroys the very fault identity an agent needs to diagnose it.
- Resolution status: CLOSED, top answer **CONTRADICTED by current documentation** in its
  second half (its first half, that the key policies already fault, is right); runner-up
  **CONTRADICTED**.
- Evidence level: (d) for the RaiseFault advice as a customization pattern; (a) for the
  correction.

---

### CASE 14. Calling one proxy from another: both community answers are inferior to current docs

- URL: <https://stackoverflow.com/questions/22499350> ("Call Another API Proxy from one API
  Proxy in the same organization"), tag `apigee`, score 2, 2 answers, no accepted answer.
- Asker's terms: "One of the considerations in the API proxy development and design is not
  to implement ServiceCallout from one API proxy to another in the same organization, or
  recursively from an API proxy back to itself as indicated in the documentation." He asks
  "Is there any other way to implement this?"
- Answer A (59 rep): "You can call one API proxy in other like any other request... what i
  suggest is to create a new flow within the same API proxy itself and copy the flow and
  policies in the other proxy to the new flow."
- Answer B (364 rep): confirms it is not recommended, then suggests sharing resources at
  org or environment level: "By resources, I mean java, JavaScript, XSLT, etc."
- **Neither names the actual documented mechanism.** I fetched
  <https://cloud.google.com/apigee/docs/api-platform/antipatterns/proxy-within-proxy>
  ("Antipattern: Invoking a proxy within a proxy", HTTP 200, 162672 bytes, "applies to
  Apigee and Apigee hybrid", last updated 2026-10-09), saved as
  `pages/api-platform_antipatterns_proxy-within-proxy.txt`:
  - Antipattern: "Invoking one API proxy from another either using HTTPTargetConnection in
    the target endpoint or custom JavaScript code results in additional network hop."
  - Best practice: "**Use the proxy chaining feature** for invoking one API Proxy from
    another. Proxy chaining is more efficient as it uses **local connection** to reference
    the target endpoint (another API Proxy)", with
    `<LocalTargetConnection><APIProxy>proxy2</APIProxy><ProxyEndpoint>default</ProxyEndpoint></LocalTargetConnection>`
  - Impact: "Invoking one API proxy from another API Proxy incurs unnecessary network hops,
    that is the request has to be passed on from one Message Processor to another Message
    Processor."
- Answer A's "copy the flow into the same proxy" is duplicated code, which a third
  documented antipattern discourages by implication and which answer B was gesturing at
  with shared resources. Answer B is closer but still wrong about the mechanism. A support
  agent repeating either is giving 2015 advice.
- This is the same anti-pattern that produces CASE 2's intermittent JavaScript 200 ms
  timeouts: a JavaScript policy doing `httpClient.send(...)` at another proxy is named
  verbatim on this antipattern page.
- Resolution status: CLOSED, both answers **CONTRADICTED / superseded** by current
  documentation.
- Evidence level: (d) for both answers; (a) for proxy chaining.

---

### CASE 15. `LookupCachePolicy.cachehit` alternates true/false; the answer blames randomness

- URL: <https://stackoverflow.com/questions/59607032> ("lookupcache.LookupCachePolicy.cachehit
  shows either true or false across request")
- Platform: Stack Overflow, tag `apigee`, score 3, 1 answer, **it IS accepted** (score 2,
  1289-rep account)
- Asker's terms: an endpoint that populates a cache and then looks it up. "The Flow variables
  `lookupcache.LookupCachePolicy.cachekey` & `lookupcache.LookupCachePolicy.cachename` are the
  same across all this request anyway but still the `cachehit` value would either be true or
  false even though the value exist in the cache."
- This is the right question to ask, because the obvious explanations are already excluded
  by the asker's own observation that cache key and cache name are stable. Distributed
  cache across message processors, and cache expiry, both fail to explain a stable key
  alternating.
- Accepted answer: "The Solution for me was removing `<PurgeChildEntries>true</PurgeChildEntries>`
  in my Invalidate Cache Policy as for some reason it **randomly** invalidates caches that is
  not inputted in the reference of a property. Hence the intermittent response being receive
  in the Lookup Cache Policy."
- **The direction is right and the mechanism is wrong.** I checked
  `pages/api-platform_reference_policies_invalidate-cache-policy.txt`, `<PurgeChildEntries>`
  element: it is defined as "`true` to purge cache entries that share the same `<Prefix>`
  value configured for this policy, **even if the PopulateCache policy instances that loaded
  those items into cache also used various `<KeyFragment>` elements**." Default `false`.
- So the behaviour is not random. It is prefix-scoped invalidation. If several cache entries
  share a `<Prefix>` but are distinguished by `<KeyFragment>`, one InvalidateCache run wipes
  all of them, and whether a subsequent lookup hits depends on whether that particular entry
  has been repopulated since. The word "randomly" in the answer is the part that would send
  an agent looking for a replication or expiry problem.
- Not promoted to a scenario because the accepted answer is self-reported and uncorroborated,
  and the documented mechanism refines rather than overturns it. Evidence level (c) for the
  fix, (a) for the correction to the mechanism.

---

## PROPOSED SCENARIOS

Structure copied from `scenarios/medium.md`. Eight cases. Every fault code quoted below
was checked against `.agents/skills/apigee-support-core/references/error-codes.md` or a
page cached under `research/pages/`; the one code that failed both checks
(`messaging.config.beans.CertNotFound`, CASE 7) is deliberately kept out of the scenario
set and is noted above instead.

---

### MED-32. Six requests admitted where three per minute is configured

#### Scenario metadata

- ID: MED-32
- Difficulty: medium
- Primary topic: rate limiting, SpikeArrest policy
- Secondary topics: runtime topology, message processors, current vs legacy behaviour
- Product: Apigee
- Origin: reported real-world case
  (<https://stackoverflow.com/questions/23298849>), closed; the accepted answer is now
  contradicted by current documentation
- Versions: checked 2026-10-12
- Evaluation objectives: resist the high-reputation accepted answer that says SpikeArrest
  cannot be synchronised across message processors. The correct move is to read the policy
  definition for `<UseEffectiveCount>` before reasoning about topology at all. A second
  objective: notice that the widely cited `docs.apigee.com` comparison URL now serves
  Apigee Edge for Private Cloud documentation, not Apigee X.
- Skills expected: apigee-support-core

#### Initial support ticket

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

#### Initial evidence

Six successful calls inside 20 seconds, then rejections, on a proxy with
`<Rate>3pm</Rate>`. The rejections carry
`{"fault":{"detail":{"errorcode":"policies.ratelimit.SpikeArrestViolation"}}}` with HTTP
429, which the local error index confirms at `error-codes.md` line 43, sourced to the
spike-arrest policy page. No `<UseEffectiveCount>` element is present in the policy.

#### Expected investigation

The agent should read the policy, not the topology. Six message processors is a true
observation and a distraction. The question that resolves this is what the SpikeArrest
policy is configured to do, and the answer is that with the default `<UseEffectiveCount>`
value the policy uses a token-bucket algorithm that smooths the configured rate into
smaller intervals and does not synchronise counts across message processors. Multiplying
the interval allowance by the number of message processors reproduces the reported
six-for-one exactly.

The agent should also resist the standing advice to move this to a Quota policy. That
advice was correct when written and is no longer complete.

#### Diagnostic evidence

```xml
<SpikeArrest async="false" continueOnError="false" enabled="true" name="spikearrest-1">
  <DisplayName>SpikeArrest-1</DisplayName>
  <Identifier ref="request.header.some-header-name"/>
  <MessageWeight ref="request.header.weight"/>
  <Rate>3pm</Rate>
</SpikeArrest>
```

No `<UseEffectiveCount>` element, so the policy is on the token-bucket branch. The current
spike-arrest policy reference states that per-minute rates are "smoothed into intervals of
seconds", that the smoothing algorithm "smooths traffic spikes by dividing the rate limit
that you specify into smaller intervals", and that "Smoothing is not coordinated across
Message Processors." With `3pm` that is one request per 20 seconds **per message
processor**, and six processors admit six.

#### Ground-truth resolution

The configuration is default, not broken. With `<UseEffectiveCount>` unset the policy
smooths, and smoothing is per message processor, so the effective admission rate is the
configured rate multiplied by the number of message processors. Six is what six
processors produce.

The accepted Stack Overflow answer to this exact report says, verbatim, "SpikeArrest has no
ability to be distributed across message processors", and its whole remedy is to abandon
SpikeArrest for the Quota policy, accepting that a distributed quota cannot be configured
per second. That is contradicted by current documentation, which documents the element
that does exactly what the answer says is impossible.

The agent should say the community answer is out of date rather than reproduce it, and
should not tell the customer the feature does not exist.

#### Correct remediation

Set the documented element on the policy, which switches it to the distributed algorithm:

```xml
<SpikeArrest async="false" continueOnError="false" enabled="true" name="spikearrest-1">
  <Identifier ref="request.header.some-header-name"/>
  <MessageWeight ref="request.header.weight"/>
  <Rate>3pm</Rate>
  <UseEffectiveCount>true</UseEffectiveCount>
</SpikeArrest>
```

This is a runtime behaviour change on a rate-limiting policy. It should be scheduled, not
applied mid-incident, and the customer's existing alerting on 429 responses will change
shape because rejections will become consistent rather than per-processor.

Documented caveat to state, not to omit: with the distributed algorithm the policy uses a
sliding window and does not smooth, so a burst that stays within the configured rate is
allowed through. If the customer also needs burst smoothing, the two policies have
different jobs and the documented ordering is SpikeArrest before Quota in the ProxyEndpoint
request PreFlow.

#### Verification

Confirm `ratelimit.spikearrest-1.exceed.count > 0` or
`ratelimit.spikearrest-1.available.count < 1` at the moment of rejection. Do not use
`ratelimit.spikearrest-1.failed`, which the reference says "should not be used to check if
a rate limit has been exceeded. It may be set to `true` under high load due to the policy's
'fail-open' design."

Then fire six requests inside a 20 second window and confirm that three succeed and three
are rejected, and repeat after the change has propagated across all six message
processors. Also confirm the rejected requests carry
`policies.ratelimit.SpikeArrestViolation`, not a policy-internal failure.

#### Common incorrect answers

"SpikeArrest cannot be distributed across message processors; use Quota instead." This is
the accepted, high-reputation answer on the source thread and it is wrong as of current
documentation. Reproducing it is the primary failure this scenario tests.

"Add a distributed Quota policy, which can only be per minute." True of Quota, and it
leaves the customer with a policy that cannot express a per-second limit at all.

"Configure ConcurrentRateLimit." It is deprecated and the customer already reports it does
not help.

"Reduce the rate to 3 divided by 6 to compensate." This hard-codes the processor count,
which changes when the org scales, and it silently under-admits traffic on a smaller
topology.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Reproduces the "not distributed" answer | Identifies per-processor smoothing | Identifies per-processor smoothing **and** `<UseEffectiveCount>` as the remedy |
| Handling of current vs legacy advice | Treats the accepted answer as correct | Hedges | States the accepted answer is contradicted by current docs |
| Diagnostic method | Reasons from message processor count | Reads the policy XML | Reads the policy XML and asks about `<UseEffectiveCount>` |
| Source discipline | Cites docs.apigee.com as Apigee X | Notices the domain | Flags that the URL serves Edge/OPDK docs and cites the X page |
| Quality of next step | Move to Quota | Set the element | Schedule the change, state the smoothing trade-off, verify with the ratelimit variables |

#### Critical failures: telling the customer SpikeArrest cannot be synchronised across
message processors; recommending a Quota policy without offering the documented
alternative; using `ratelimit.<policy>.failed` to decide whether a limit was exceeded.

#### References

- Reported case: <https://stackoverflow.com/questions/23298849>
- SpikeArrest policy, `<UseEffectiveCount>` and smoothing:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy>
- Comparing Quota and SpikeArrest (Apigee X):
  <https://cloud.google.com/apigee/docs/api-platform/develop/comparing-quota-and-spike-arrest-policies>
- Edge/OPDK page of the same name, which is what the legacy `docs.apigee.com` URL resolves
  to: <https://docs.apigee.com/api-platform/develop/comparing-quota-spike-arrest-and-concurrent-rate-limit-policies>
- Antipattern, non-distributed quota (for contrast):
  <https://cloud.google.com/apigee/docs/api-platform/antipatterns/non-distributed-quota>

---

### MED-33. Rate of 5 per minute, but the third call in ten seconds is rejected

#### Scenario metadata

- ID: MED-33
- Difficulty: medium
- Primary topic: rate limiting, SpikeArrest policy
- Secondary topics: Quota versus SpikeArrest, message weights
- Product: Apigee
- Origin: reported real-world case
  (<https://stackoverflow.com/questions/21912316>), closed, no accepted answer
- Versions: checked 2026-10-12
- Evaluation objectives: the symptom looks like a broken counter and is in fact a rate
  limiter. The agent must apply the documented smoothing arithmetic instead of assuming the
  policy counts requests in a window, and must not "fix" it by raising the rate without
  establishing which problem the customer actually has.
- Skills expected: apigee-support-core

#### Initial support ticket

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

#### Initial evidence

Two successful calls then rejections, for a configured `5pm`. Rejections carry
`policies.ratelimit.SpikeArrestViolation`, HTTP 429, verified at `error-codes.md` line 43.
The policy has a `<MessageWeight>` bound to a request header, which is a second live
variable that has not been examined. `continueOnError` is `true`, which is unusual for a
throttling policy and is not discussed.

#### Expected investigation

The agent should apply the documented smoothing rule rather than the window rule.
Per-minute rates are documented as "smoothed into intervals of seconds", so `5pm` is
enforced as one request per 12 seconds, not as five requests per 60-second bucket. Ten
calls in ten seconds should produce one success under one processor. Two successes means
either two message processors each smoothed independently, or the message weight is not 1.

The agent should check both. The weight is the more commonly missed branch: the reference
gives the worked example that with a rate of `10pm` and a client weight of `2`, "only five
messages per minute are permitted from that client because each request counts as 2".

#### Diagnostic evidence

```xml
<SpikeArrest enabled="true" continueOnError="true" async="false" name="SpikeArrest">
  <Rate>5pm</Rate>
  <MessageWeight ref="request.header.weight"/>
</SpikeArrest>
```

A debug trace shows `request.header.weight` is **absent** on the client requests. With the
reference unset the weight falls back to 1, so weight is not the cause here, and the
trace shows two distinct message processors serving the two successful requests.

#### Ground-truth resolution

There is no fault. Two independent effects compound. SpikeArrest is documented as a rate
limiter rather than a counter: it "smoothes the rate to one request allowed every
200 *milliseconds* (1000/5)" for per-second rates, and per-minute rates are smoothed into
intervals of seconds, so `5pm` becomes one request per 12 seconds. And smoothing is
documented as "not coordinated across Message Processors". With two message processors the
observed allowance doubles to two requests per 12 seconds, which is exactly what the
customer saw.

The customer's mental model, a per-minute counter, is the thing that is wrong. Their
question, whether the two message processors are the cause, is the right question and the
answer is yes.

#### Correct remediation

Decide which of two things the customer actually wants, because they need different
configurations. If they want burst protection, keep the token-bucket smoothing and choose
a rate that reflects the interval their backend can absorb, understanding the effective
admission rate is the configured rate multiplied by the number of message processors. If
they want an accurate count of requests per period, that is the Quota policy's job; the
SpikeArrest reference itself points there.

If the customer wants both, the documented combination is SpikeArrest first in the
ProxyEndpoint request PreFlow for burst protection, then Quota for the longer-term count.
The comparison page states SpikeArrest "should always be attached before the Quota policy
in the ProxyEndpoint Request PreFlow... This prevents spikes from prematurely exhausting
quota."

Raise `<MessageWeight>` handling regardless: bind it to a header the clients actually send
or remove it. An unset `ref` currently resolves to 1, which means the policy silently
accepts a configuration the operator believes is active.

#### Verification

Send requests at the documented interval and confirm exactly one per processor per
interval succeeds. Then confirm the rejection path: check
`ratelimit.SpikeArrest.failed` separately from
`ratelimit.SpikeArrest.exceed.count > 0`, since the reference warns that `failed` "should
not be used to check if a rate limit has been exceeded".

Re-test after any change to the rate so the multiplication by message processor count is
re-derived from the trace rather than assumed, because the trace is what established it.

#### Common incorrect answers

"Your SpikeArrest policy is counting wrong; five requests should have been allowed." It is
not counting, it is smoothing, and the documentation states that explicitly.

"Increase the rate to 10pm to compensate." This doubles the real allowance and, with two
processors, admits four per 12 seconds, which is not what anyone asked for.

"Switch to a Quota policy." Legitimate only if the customer wants counts. Offered as a
general fix it replaces burst protection with a window count and lets the burst through.

"Remove the two routers, they are causing double counting." Routers do not hold policy
counters.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Assumes a per-minute counter | Applies smoothing, misses processor multiplication | Applies smoothing **and** the per-processor multiplication, and checks message weight |
| Diagnostic method | Restates the rate | Suggests raising it | Uses a debug trace to separate weight from topology |
| Safety | Changes the rate immediately | Proposes a change | Establishes whether the customer wants burst protection or counts before changing |
| Handling of competing causes | Ignores MessageWeight | Mentions it | Confirms the unset `ref` resolves to 1 and recommends fixing the binding |
| Verification | None | Retests once | Checks the documented ratelimit variables and keeps `failed` separate from `exceed.count` |

#### Critical failures: treating SpikeArrest as a request counter; raising the rate as the
first move; ignoring `<MessageWeight ref=...>`.

#### References

- Reported case: <https://stackoverflow.com/questions/21912316>
- SpikeArrest policy, `<Rate>`, `<MessageWeight>`, smoothing:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy>
- Comparing Quota and SpikeArrest:
  <https://cloud.google.com/apigee/docs/api-platform/develop/comparing-quota-and-spike-arrest-policies>
- Error index entry for `policies.ratelimit.SpikeArrestViolation`:
  `.agents/skills/apigee-support-core/references/error-codes.md`

---

### MED-34. A key value map read returns nothing, and the policy reports no error

#### Scenario metadata

- ID: MED-34
- Difficulty: medium
- Primary topic: KeyValueMapOperations policy
- Secondary topics: management API scoping, flow variables, silent failure
- Product: Apigee
- Origin: reported real-world cases
  (<https://stackoverflow.com/questions/21897932> and
  <https://stackoverflow.com/questions/27850597>), both closed with accepted answers
- Versions: checked 2026-10-12
- Evaluation objectives: two distinct causes produce one identical silent symptom, and the
  customer's own workaround masks the problem by making the policy write instead of read.
  The agent must enumerate the read path rather than trust the first configuration that
  makes the symptom disappear.
- Skills expected: apigee-support-core

#### Initial support ticket

> We store a lookup table in a key value map and read it in the request flow. The variable we
> assign is always empty and the policy produces no error at all. The trace shows the step
> completing.
>
> We created the map through the management API using the API-scoped URL
> `/v1/o/{org}/apis/{api}/keyvaluemaps`, named `countrymap`. Our policy is:
>
> ```xml
> <KeyValueMapOperations async="false" continueOnError="false" enabled="true"
>   mapIdentifier="countrymap" name="keyvaluemapoperations-2">
>   <Get assignTo="my.country" index="1">
>     <Key><Parameter ref="apigee.countryCode"></Parameter></Key>
>   </Get>
>   <Scope>organization</Scope>
> </KeyValueMapOperations>
> ```
>
> One thing we noticed: if we add an `<InitialEntries>` block the same policy works. We are
> assuming that proves the map exists. Does it?

#### Initial evidence

The variable is empty on every request. No fault is raised; the policy step completes
normally. The map was created at API scope; the policy declares `<Scope>organization</Scope>`.
The `<Key><Parameter>` element carries a `ref` attribute. `index="1"` is a 1-based index
into a multi-valued key.

#### Expected investigation

Three separate things can produce a silent empty read, and the ticket contains two of them
at once. The agent should check, in order: whether the map exists in the scope the policy
declares; whether `<Parameter>` is naming a key or naming a flow variable; and whether the
key being read exists at all.

The `<InitialEntries>` observation is the trap that has to be addressed directly. Adding
`<InitialEntries>` makes the policy **create or overwrite** the map in the declared scope.
That is why the symptom disappears. It does not prove the original map was readable.

#### Diagnostic evidence

Listing the KVM at the API scope returns the map with entries. Listing it at organization
scope returns 404. The trace shows `apigee.countryCode` resolving to a value, for example
`IN`, while the map contains keys named `IN` only in the API-scoped map, and the
organization-scoped policy is reading from a namespace where nothing was ever written.

Separately, in the second variant of this report the map and the scope are both correct,
and the defect is:

```xml
<Key><Parameter ref="k1"></Parameter></Key>   <!-- resolves flow variable k1, then looks up its VALUE as a key name -->
<Key><Parameter>k1</Parameter></Key>           <!-- uses the literal string "k1" as the key name -->
```

The reference states that `ref` means "the name of a variable whose value contains the
exact name of the key you want to create, get, or delete", and that the attribute is
"Required if no literal value is given between the opening and closing tags."

#### Ground-truth resolution

Two defects, reported as one. The map exists at API scope and the policy reads at
organization scope, so the read addresses an empty namespace. Separately, the `<Parameter>`
element uses `ref`, which makes the element a variable lookup rather than a literal key
name, so even with the scope corrected the key name being searched for is the *value* of
`apigee.countryCode`, not the string `Development` or `IN`.

The `<InitialEntries>` workaround makes the symptom disappear for the wrong reason. It
writes into the organization-scoped namespace, which is then readable, and it masks the
scope defect permanently by seeding a second, divergent copy of the data.

#### Correct remediation

Make the declared scope match where the map actually lives, then make the key name
literal unless it is genuinely dynamic:

```xml
<KeyValueMapOperations async="false" continueOnError="false" enabled="true"
  mapIdentifier="countrymap" name="keyvaluemapoperations-2">
  <Get assignTo="my.country" index="1">
    <Key><Parameter>IN</Parameter></Key>
  </Get>
  <Scope>apiproxy</Scope>
</KeyValueMapOperations>
```

Before moving data, check whether an `<InitialEntries>` block has already been deployed.
If it has, the environment now holds a second copy of the entries written by the policy,
and removing the block without reconciling will make the reads start failing. Confirm
which copy is authoritative with the customer before deleting anything.

Also check the reserved word: the reference notes that the KVM key name `ratelimit` is
reserved, in two separate places on that page.

#### Verification

Read the value back in a debug trace and confirm `my.country` is populated and that the
step still completes without a fault. Confirm the map's entry list in the scope the policy
declares, and confirm no second copy exists in the other scope.

Re-test after the change propagates across environments, because KVM data is per environment
and a fix in `test` says nothing about `prod`.

#### Common incorrect answers

"Add `<InitialEntries>` so the policy creates the map." This is the customer's own
workaround. It creates a second, divergent copy of the data and leaves the original
unreadable.

"Raise `continueOnError` or check the cache expiry." Neither is relevant; there is no error
and no expiry in play.

"Change `index` from 1 to 0." `index` is 1-based. Zero is a deployment error, `InvalidIndex`,
documented as "If the `index` attribute specified in the `<Get>` element ... is zero or a
negative number, then the deployment of the API proxy fails."

"Use `<Parameter ref="entry.Development">`." That names a flow variable called
`entry.Development`, not a key called `Development`. This is the mistake the second report
made three times in a row.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Suggests InitialEntries | Identifies the scope mismatch | Identifies scope mismatch **and** `ref` versus literal key name |
| Diagnostic method | Trusts the InitialEntries workaround | Lists the KVM in one scope | Lists the KVM in both scopes and checks whether a second copy was seeded |
| Handling of competing causes | One cause | Two causes | Enumerates scope, key-name form, index base, and key existence |
| Safety | Recommends adding entries | Proposes the scope change | Flags the possible duplicate data before removing anything |
| Verification | Retests once | Retests after change | Retests per environment and confirms no second copy exists |

#### Critical failures: recommending `<InitialEntries>` as the fix; treating
`<Parameter ref="...">` as a key name; deleting or overwriting a map without checking
whether an `<InitialEntries>` block has already written to it.

#### References

- Reported case, scope mismatch:
  <https://stackoverflow.com/questions/21897932>
- Reported case, `ref` versus literal:
  <https://stackoverflow.com/questions/27850597>
- KeyValueMapOperations policy, `<Parameter>`, `<Scope>`, `<Get index>`:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/key-value-map-operations-policy>
- KVM deployment errors including `InvalidIndex`:
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/deployment/key-value-map-deployment-errors>

---

### MED-35. 502 Bad Gateway at exactly two minutes, with the backend reporting success four minutes later

#### Scenario metadata

- ID: MED-35
- Difficulty: medium
- Primary topic: target connection behaviour and timeouts
- Secondary topics: keep-alive connection reuse, endpoint properties, undocumented territory
- Product: Apigee (and Apigee hybrid)
- Origin: reported real-world case
  (<https://stackoverflow.com/questions/68314564>), closed with **zero answers**; fault
  payload and causes checked against the official playbook, retrieved live during this
  session
- Versions: checked 2026-10-12
- Evaluation objectives: the symptom looks like a backend timeout and is not one. The
  agent must use the documented status-code mapping to rule out the timeout family before
  reasoning about anything else, must work the documented causes even when they do not fit,
  and must not invent a 120-second Apigee timeout when no documentation states one.
- Skills expected: apigee-support-core

#### Initial support ticket

> We have an Apigee proxy in front of a Node.js 12 / Express backend. If a request takes
> longer than two minutes the client gets a 502 Bad Gateway, always at the two minute mark.
> The backend logs a 200 about four minutes later, so it is completing the work after the
> client has already given up. The backend logs nothing at the moment the client errors.
>
> The fault body is:
>
> ```json
> {"fault":{"faultstring":"Unexpected EOF at target",
>   "detail":{"errorcode":"messaging.adaptors.http.flow.UnexpectedEOFAtTarget"}}}
> ```
>
> We have already raised the Node request timeout to ten minutes and added keep-alive on
> the backend. Neither changed anything. Please tell us why Apigee is throwing the error
> when the backend is not.

#### Initial evidence

HTTP 502, fault code `messaging.adaptors.http.flow.UnexpectedEOFAtTarget`, fault string
"Unexpected EOF at target". The failure is at a fixed 120 seconds from request start. The
backend receives the request, does not respond for four minutes, and has no log entry at
the two minute mark. The customer has already changed backend-side keep-alive and Node
timeouts.

The fault code is verified in `research/pages/mon_fault-codes.txt` line 81. It is
deliberately **not** in `.agents/skills/apigee-support-core/references/error-codes.md`,
because that index covers policy fault codes and this one is raised by the HTTP target
adaptor, not by a policy. An agent that cannot say that distinction has not read the
evidence properly.

#### Expected investigation

Rule out the timeout family first, using documented status codes rather than intuition. The
endpoint properties reference states that a target connect timeout returns `503` and that
`io.timeout.millis` expiry returns `504 Gateway Timeout`, with `408 Request Timeout` if the
timeout is reading from ingress. The current defaults are `connect.timeout.millis` 3000 ms
and `io.timeout.millis` 55000 ms, capped at 300 seconds. A 502 is none of these. Neither
default produces a 120 second wall. That is the key finding and it is available before any
packet capture is taken.

Then work the documented causes for this exact fault code, and be willing to find they do
not fit. The official playbook gives two.

#### Diagnostic evidence

```terminal
kubectl get svc istio-ingressgateway -n istio-system
kubectl get deploy -n apigee
```

From the TargetEndpoint definition:

```xml
<HTTPTargetConnection>
  <URL>https://backend.example.com</URL>
  <Properties>
    <Property name="keepalive.timeout.millis">30000</Property>
  </Properties>
</HTTPTargetConnection>
```

Against a backend configured with a 25 second keep-alive, and the reference documents a
default of 60000 ms for that property.

#### Ground-truth resolution

Three separate conclusions, and the honest answer contains all three.

One, the fault is on the Apigee side, and the customer's own reasoning on this point is
right. The code and the playbook both attribute it to the target hop: the playbook's sample
ingress log carries `x_apigee_fault_code: messaging.adaptors.http.flow.UnexpectedEOFAtTarget`
with `x_apigee_fault_source: target`. Apigee cannot raise a target-side EOF unless it is
the party that received one.

Two, it is not a timeout. Timeouts are 503 and 504, and the documented defaults are 3
seconds connect and 55 seconds I/O. Nothing documented produces a 120 second wall at the
target hop. An agent that says "Apigee has a two minute timeout" is asserting something
this research did not find in any current document.

Three, the documented causes for this fault code do not explain a fresh long-lived
request. Cause one is a keep-alive mismatch, and it requires Apigee to **reuse a pooled
connection** whose idle threshold expired on the backend mid-request. The playbook's
evidence for it is `useCount=7` with `bytesRead=0` and `bytesWritten=1303` in a
`java.io.EOFException: eof unexpected`. A request that has been open for two minutes on a
fresh connection does not have that signature. Cause two is AWS NLB with cross-zone load
balancing and client IP preservation behind NAT, which breaks connections in pairs and
"must intermittently occur" rather than firing at a fixed elapsed time.

So the documented causes should be tested and can reasonably be ruled out, and what remains
is not documented. The right output is a scoped evidence request, not a confident
explanation.

#### Correct remediation

Work cause one first, because it is the documented one and because the customer moved
keep-alive in the wrong direction. The documented requirement is that Apigee's keep-alive
value must be **lower** than the backend's, not higher:

```xml
<Property name="keepalive.timeout.millis">25000</Property>
```

with a 25 second backend value, or simply remove the override and accept the 60000 ms
default if the backend's value is higher.

Check cause two by confirming all three conditions: NAT IPs provisioned, target is AWS NLB,
cross-zone load balancing enabled, client IP preservation enabled. If all hold, the
documented resolution is to disable cross-zone load balancing or client IP preservation,
and the documented position is that "Cloud NAT behaves correctly here, and this is an issue
with NLB architecture. No changes can be made at Apigee."

If neither cause applies, raise a support case rather than guessing. The playbook lists
exactly what to attach: project ID, organization, proxy and revision, a downloaded debug
session file for a failing call, backend logs for the failure window, and a tcpdump from
the message processor or the backend. Take the capture on the first hop after Apigee:

```terminal
tcpdump -i any -s 0 host <BACKEND_HOSTNAME> -w <FILENAME>
```

Note for the ticket: `api.timeout` is a per-proxy property that must be "shorter than the
standard Message Processor timeout of 300 seconds" and "cannot be set with a variable",
and if it is unset the effective timeout comes from the Ingress. That is the only
documented place an upstream timeout can enter this path, and it is worth establishing what
the Ingress is set to before the case is raised.

#### Verification

After any change, confirm the symptom by forcing it: send a request the backend will hold
for longer than the configured timeout and confirm the status code changes to the documented
one for the new timeout, which is `504` for a read timeout. A 502 that becomes a 504 is
progress; a 502 that becomes a 200 means the keep-alive change worked.

Confirm the fault code in the ingress log is no longer `messaging.adaptors.http.flow.UnexpectedEOFAtTarget`
and that `x_apigee_fault_source` no longer reads `target`.

#### Common incorrect answers

"It is a two minute timeout on the Apigee side." Undocumented as far as this research
established. Do not say it.

"Increase `io.timeout.millis` to 120000." This is the example in the official playbook, and
it is the wrong move for a 502. A read timeout raises 504 with
`messaging.adaptors.http.flow.GatewayTimeout` and reason `TARGET_READ_TIMEOUT`, which is a
different fault entirely. Raising the timeout converts one failure mode into another.

"Raise the backend's keep-alive timeout, as Apigee's docs suggested." The documented
direction is the opposite. Apigee's value must be lower than the backend's, otherwise
Apigee reuses a connection the backend is about to close.

"It must be the backend crashing." The backend logs a 200 four minutes later, which is
positive evidence against that.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Asserts a 120 s Apigee timeout | Rules out timeouts by status code | Rules out timeouts by status code and by the documented 3 s / 55 s defaults |
| Diagnostic method | Changes a timeout value | Works the playbook causes | Tests the documented causes and says explicitly that they do not fit the signature |
| Source discipline | Treats `mon_fault-codes` as a policy index | Notes the index gap | States the code is a target-adaptor code outside the policy error index |
| Honesty about limits | Confidently names a cause | Hedges | Names what is documented, names what is not, and requests scoped evidence |
| Quality of next step | Raises `io.timeout.millis` | Fixes keep-alive direction | Fixes keep-alive direction, checks the NLB conditions, prepares the exact case attachments |

#### Critical failures: asserting an undocumented 120-second Apigee timeout; raising
`io.timeout.millis` as the remedy for a 502; telling the customer to raise the backend
keep-alive above Apigee's.

#### References

- Reported case, no answers: <https://stackoverflow.com/questions/68314564>
- Playbook, 502 Unexpected EOF at target (fetched live this session, saved to
  `research/pages/api-platform_troubleshoot_playbooks_runtime_unexpected-eof-at-target.txt`,
  last updated 2026-10-09):
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/runtime/unexpected-eof-at-target>
- Playbook, 504 target read timeout:
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/runtime/504-target-read-timeout>
- Endpoint properties, including `connect.timeout.millis`, `io.timeout.millis`,
  `keepalive.timeout.millis` and `api.timeout`:
  <https://cloud.google.com/apigee/docs/api-platform/reference/endpoint-properties-reference>
- Monitoring fault codes, which is where this code is actually indexed:
  `research/pages/mon_fault-codes.txt`
- Note: `.../playbooks/network/504-target-read-timeout` returns HTTP 200 with a generic
  title and no body. It is a soft 404. Use the `runtime/` path.

---

### MED-36. A JavaScript policy times out intermittently, and raising the limit is the wrong fix

#### Scenario metadata

- ID: MED-36
- Difficulty: medium
- Primary topic: JavaScript policy execution limits
- Secondary topics: proxy-to-proxy calls, antipatterns, free trial limits
- Product: Apigee
- Origin: reported real-world case
  (<https://stackoverflow.com/questions/22995892>), closed with the single answer accepted
- Versions: checked 2026-10-12
- Evaluation objectives: the accepted answer is the intuitive one and it converts an
  intermittent input/output symptom into a permanently higher ceiling. The agent must read
  what the script actually does, recognise the proxy-within-proxy antipattern, and notice
  the documented free-trial constraint that makes the accepted answer a no-op on some
  organisations.
- Skills expected: apigee-support-core

#### Initial support ticket

> We have two proxies. Proxy B has a JavaScript policy that calls proxy A over HTTP and
> processes the response. Intermittently we get:
>
> ```json
> {"fault":{"detail":{"errorcode":"steps.javascript.ScriptExecutionFailed"},
>   "faultstring":"Execution of getlocationserviceresponse failed with error: Javascript runtime exceeded limit of 200ms"}}
> ```
>
> We have already split our JavaScript into small modules so each policy is tiny. It still
> happens "from time to time". What can we do to avoid it?

#### Initial evidence

`steps.javascript.ScriptExecutionFailed`, HTTP 500, verified at `error-codes.md` line 61.
The failure is intermittent, not consistent, and the arithmetic does not fit a CPU-bound
script: splitting the code did not help, which is itself evidence that the limit is not
being consumed by computation. The script performs `httpClient` calls. The organisation is
on a free trial or evaluation tier, which the ticket does not yet mention.

#### Expected investigation

The intermittency is the clue and the accepted answer ignores it. A CPU-bound script either
exceeds 200 ms consistently or not at all. A script that occasionally waits on a network
call exceeds a wall-clock limit only when the network is slow. The documented `timeLimit`
is wall-clock execution time, not CPU time, and an outbound HTTP call from inside a
JavaScript policy is a blocking wait charged against that same budget.

The agent should read the script body before touching the policy attributes.

#### Diagnostic evidence

```javascript
// in the JavaScript policy resource
var response = httpClient.send('https://myproject-eval.apigee.net/proxyA/resource');
response.waitForComplete();
context.log("done");   // sometimes never reached
```

And the organisation record showing the free trial / evaluation tier. The current
JavaScript policy reference states for the `timeLimit` attribute: "Specifies the maximum
time (in milliseconds) a script can execute... **Note: For free trial accounts, execution
time is limited to 200 ms.**" The attribute is marked **Required**.

#### Ground-truth resolution

The policy is not doing too much work, it is waiting too long, and no amount of splitting
changes that. The 200 ms budget is being consumed by a blocking `httpClient.send` plus
`waitForComplete`, so the policy fails exactly when the downstream call is slow. That also
explains the intermittency and explains why the customer's own mitigation did nothing.

Worse for the accepted answer: on a free trial or evaluation organisation, the documented
note says execution time is limited to 200 ms regardless, so raising `timeLimit` may change
nothing at all. The accepted answer does not consider the organisation tier and cannot
explain why the same policy would fail differently on a paid organisation.

The underlying construction is also a documented antipattern. Invoking one API proxy from
another with custom JavaScript or an `HTTPTargetConnection` "results in additional network
hop", because the request "has to be routed through the traditional route (Router > MP) at
runtime... a request has already reached the MP". The documented fix is proxy chaining.

#### Correct remediation

Remove the proxy-to-proxy call rather than pay for it in timeLimit. Proxy chaining runs
the called proxy in the same message processor over a local connection:

```xml
<LocalTargetConnection>
  <APIProxy>proxyA</APIProxy>
  <ProxyEndpoint>default</ProxyEndpoint>
</LocalTargetConnection>
```

If the second proxy genuinely must be reached over the network, keep the call out of
JavaScript. Use a ServiceCallout, which is a policy with its own timeout surface, or move
the request shaping into the target endpoint.

Only after removing the blocking call is raising `timeLimit` even the right conversation,
and at that point establish the organisation tier first, because the documented free-trial
limit makes the attribute ineffective on trial and evaluation organisations.

#### Verification

Confirm the failure rate drops to zero across a sustained load test that includes slow
downstream responses, not just fast ones. The intermittency means a passing smoke test
proves nothing here.

Then confirm the script actually completes: the `context.log` after `waitForComplete`
should appear on every request, which it did not before.

Confirm the organisation tier before relying on any `timeLimit` value, and if it is a trial
or evaluation organisation say so rather than raising the attribute and reporting no change.

#### Common incorrect answers

"Raise `timeLimit` to 1000." This is the accepted answer on the source thread. It raises
the ceiling while leaving the blocking call in place, converts an intermittent failure into
a less frequent one, and is documented as ineffective on free trial and evaluation
organisations.

"Split the JavaScript into smaller modules." The customer already did this and reported it
did not help. The agent should treat that as evidence, not as a suggestion to repeat.

"Increase the message processor size or memory." The limit is a per-policy wall-clock
budget, not a resource limit.

"Retry the JavaScript policy." There is no built-in retry for a policy execution timeout,
and a retry would double the downstream load that caused the timeout.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Raises timeLimit | Identifies the call as the cost | Identifies the blocking call as the cost and names proxy chaining as the fix |
| Diagnostic method | Treats it as a code-size problem | Notes intermittency | Uses intermittency as evidence against a CPU-bound cause |
| Product knowledge | Ignores tier | Mentions trial limit | States the documented free-trial 200 ms limit and checks the tier before recommending |
| Handling of the accepted answer | Reproduces it | Hedges | States the accepted answer is incomplete and tier-dependent |
| Quality of next step | Raises the attribute | Moves the call to a policy | Removes the network hop via proxy chaining, then verifies under slow-downstream load |

#### Critical failures: recommending a higher `timeLimit` as the fix; repeating the
"split the script" advice the customer already ruled out; ignoring the documented free
trial 200 ms execution limit.

#### References

- Reported case: <https://stackoverflow.com/questions/22995892>
- JavaScript policy, `timeLimit` attribute and the free-trial note:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/javascript-policy>
- Antipattern, invoking a proxy within a proxy:
  <https://cloud.google.com/apigee/docs/api-platform/antipatterns/proxy-within-proxy>
- Error index entry for `steps.javascript.ScriptExecutionFailed`:
  `.agents/skills/apigee-support-core/references/error-codes.md`

---

### MED-37. One quota policy referenced from three flows exhausts faster than expected

#### Scenario metadata

- ID: MED-37
- Difficulty: medium
- Primary topic: Quota policy counters
- Secondary topics: API products, antipatterns, identifier scoping
- Product: Apigee
- Origin: reported real-world case
  (<https://stackoverflow.com/questions/21615609>), closed; the accepted answer is
  reproduced almost verbatim by current documentation
- Versions: checked 2026-10-12
- Evaluation objectives: the obvious model, one counter per flow, is wrong and is the model
  most engineers hold. The agent must establish what actually identifies a counter, must
  notice that the same policy reference also documents a per-operation model once API
  products are involved, and must flag the reuse as a documented antipattern rather than
  just explaining it.
- Skills expected: apigee-support-core

#### Initial support ticket

> We have one proxy with three flows, A, B and C. All three reference a single Quota policy
> named `QuotaLimitPolicy`, configured as 5 requests per interval, with an `<Identifier>`
> bound to `client_id`. We expected each flow to have its own budget of 5.
>
> What we see is that the budget is shared. A client calling only flow A exhausts the
> allowance that we budgeted for all three, and starts receiving quota rejections even
> though it has touched only one of the three resources.
>
> Failing calls carry `policies.ratelimit.QuotaViolation`. Is this a bug, and what actually
> defines a separate counter?

#### Initial evidence

HTTP 500 with `{"fault":{"detail":{"errorcode":"policies.ratelimit.QuotaViolation"}}}`,
verified at `error-codes.md` line 42, sourced to the quota policy page. One policy
element named `QuotaLimitPolicy` attached as a `<Step>` in three flows. No API product
quota settings in play. The rejections cluster on one client id.

#### Expected investigation

The agent should answer the general question, because the reporter only asked the specific
one. What makes a counter distinct is not the flow. Reference to the same policy from
several places is one counter, keyed by the policy `name` attribute, and by the identifier
value. The agent should then say that this is documented, and that reusing one policy in
several places is listed as an antipattern.

The second half is the part a single-look diagnosis misses. Once an API product is
associated, the model changes: Apigee keeps a separate counter per operation defined in the
product, and the product-level `quotaCounterScope` attribute decides whether operations
collapse onto a product-level or proxy-level counter. So "what makes a counter distinct"
has two different answers depending on whether API products are in play, and the agent has
to ask which one applies here.

#### Diagnostic evidence

```xml
<Quota name="QuotaLimitPolicy">
  <Interval>1</Interval>
  <TimeUnit>hour</TimeUnit>
  <Allow count="5"/>
  <Identifier>client_id</Identifier>
</Quota>
```

attached as:

```xml
<Step><Name>QuotaLimitPolicy</Name></Step>
```

in flow A, flow B and flow C. A debug trace on flows A, B and C shows the same
`quota.<policy>.used.count` climbing 1, 2, 3, 4, 5 across all three, then rejection. The
proxy has no API product associated, so the trace confirms the no-product path.

#### Ground-truth resolution

The behaviour is correct and the mental model is wrong. The current Quota policy reference
reproduces the reporter's own worked example, with the same flow letters:

> For example, you create a Quota policy named `MyQuotaPolicy` with a limit of 5 requests
> and place it on multiple flows (Flow A, B, and C) in the API proxy. Even though it is
> used in multiple flows, it maintains a single counter that is updated by all instances of
> the policy: Flow A is executed -> counter = 1; Flow B -> 2; Flow A -> 3; Flow C -> 4;
> Flow A -> 5. The next request to any of the three flows is rejected.

and the same page states the rule directly: "If there is no API product associated with an
API proxy, a quota policy maintains a single counter, regardless of how many times you
reference it in an API proxy. **The name of the quota counter is based on the `name`
attribute of the policy.**"

So the counter identity is the policy `name` plus the identifier value, in a proxy with no
API product. Flow does not appear in it. Separation is achieved by using different policy
elements with different `name` attributes.

The page then adds the part that changes the answer depending on configuration: "By
default, Apigee maintains a separate quota counter for each operation defined in an API
product", with operation-level quota settings taking precedence over product-level ones,
and `quotaCounterScope` of `PRODUCT` or `PROXY` deciding which operations collapse onto a
shared counter.

Finally, the reference names the reuse as an antipattern: "Using the same Quota policy in
more than one place in an API proxy flow, which can unintentionally cause Quota to run out
faster than you expected, is an anti-pattern."

#### Correct remediation

Pick one of two intents, because they are different configurations.

To give each flow its own budget, use a separate Quota policy element per flow with
distinct `name` attributes. That is what the documentation prescribes and it is the
minimal change. Note that it multiplies policy instances, which is the cost the antipattern
page is warning about elsewhere in the product.

To keep one shared budget but control how the counter is scoped, use API products and
`quotaCounterScope`. This is the right tool when several proxies should contribute to one
budget, and it is worth naming explicitly because a common but incorrect claim in community
threads is that a single counter can be shared across API proxies by a Quota policy alone.
The reference is explicit that quotas "apply to individual API proxies and are not
distributed among API proxies... a single quota is not shared across all three even if all
three use the same quota policy configuration." Sharing across proxies is done through API
product configuration, not by pointing two policies at one counter.

#### Verification

Confirm the counter now increments per flow, or per product scope, as intended, by reading
the quota variables across the flows in a debug trace rather than by inferring from
rejection counts.

Then confirm the intended per-resource budget empirically: a client that spends its whole
allowance on one resource should still have budget on the others.

Check whether other proxies share the same policy name and identifier and are silently
drawing on the same allowance, since that is the failure mode the customer is reporting.

#### Common incorrect answers

"Each flow has its own counter because they are different flows." The documented rule is
the opposite, and it is the specific misconception the reporter brought to the question.

"Set a different `<Identifier>` per flow." The identifier keys the counter by client, not by
flow. Changing it would segment clients, not resources, and would make the problem worse.

"Share one counter across three proxies by using the same policy name and identifier." The
reference says quotas are not distributed among API proxies. This is the most common wrong
answer in the community on this exact question.

"Increase the allow count to 15 so all three flows fit." That concedes the shared-counter
behaviour silently and removes the per-resource protection the customer was trying to get.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says one counter per flow | Says one counter per policy name | Says one counter per policy name plus identifier, and states it is documented |
| Diagnostic method | Reads the fault code only | Inspects the policy | Confirms counter sharing in a trace with the quota variables |
| Completeness | Answers only the specific question | Adds the antipattern note | Adds the API-product per-operation model and `quotaCounterScope` |
| Handling of competing advice | Repeats "share across proxies" | Hedged | States plainly that quotas are not distributed among API proxies |
| Quality of next step | Raise the allow count | Separate policy names | Separates policy names or moves to product-scoped counters, depending on stated intent |

#### Critical failures: asserting one counter per flow; asserting a Quota policy alone can
share a counter across proxies; raising the allow count to compensate without raising the
per-resource protection problem.

#### References

- Reported case: <https://stackoverflow.com/questions/21615609>
- Quota policy, "Understand quota counters", "How quotas are counted", and
  `quotaCounterScope`:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
- Antipattern, reusing a Quota policy:
  <https://cloud.google.com/apigee/docs/api-platform/antipatterns/reusing-quota>
- Antipattern, non-distributed quota:
  <https://cloud.google.com/apigee/docs/api-platform/antipatterns/non-distributed-quota>
- Error index entry for `policies.ratelimit.QuotaViolation`:
  `.agents/skills/apigee-support-core/references/error-codes.md`

---

### MED-38. OAuth rejects a valid-looking token because no API product matched

#### Scenario metadata

- ID: MED-38
- Difficulty: medium
- Primary topic: API products and application credentials
- Secondary topics: fault-code interpretation, tracing, misleading community answers
- Product: Apigee
- Origin: reported real-world case
  (<https://stackoverflow.com/questions/24035609>), closed; four answers give four
  different fixes and the top two contradict each other
- Versions: checked 2026-10-12
- Evaluation objectives: four plausible community fixes, two of them mutually exclusive.
  The agent must enumerate the association chain rather than adopt the highest-scoring
  answer, and must read the fault code as a pointer rather than a diagnosis, because the
  documented entry for it contains no cause text at all.
- Skills expected: apigee-support-core

#### Initial support ticket

> We are integrating a new client against our Apigee proxy and every call fails with:
>
> ```json
> {"fault":{"faultstring":"Invalid API call as no apiproduct match found",
>   "detail":{"errorcode":"steps.oauth.v2.InvalidAPICallAsNoApiProductMatchFound"}}}
> ```
>
> HTTP 401. The access token is issued by us, it is not expired, and the client is sending
> it correctly. We have read that the fix is to associate the API bundle with an API
> product, but our proxy is already in a product and the developer app is already
> associated with a product. Can you confirm which one is wrong?

#### Initial evidence

HTTP 401, `steps.oauth.v2.InvalidAPICallAsNoApiProductMatchFound`, verified at
`error-codes.md` line 132, sourced to the delete-oauth-v2-info policy page. The token
validates against the token endpoint. The proxy appears in at least one API product and
the developer app appears in at least one API product.

Note a discrepancy worth surfacing to the agent: the customer quotes a
`keymanagement.service.`-prefixed variant, which is the Apigee Edge-era string. The current
index carries the `steps.oauth.v2.`-prefixed form.

#### Expected investigation

The agent should walk the association chain rather than accept a single fix. The reported
community thread is the instruction here: the accepted answer says the **API bundle** must
be associated with a product, an equally-scored answer says the **developer app** must
list the product, a third says product approval was set to manual, and a fourth says the
resource path is missing from the product. All four can produce this symptom and only the
first is usually quoted.

The agent should also notice what the documented entry actually says, which is almost
nothing. The index row reads "Please see Oauth2.0 Access Token Verification throws 'Invalid
API call as no apiproduct match found' error for information about..." It is a pointer, not
a cause. An agent that treats the row as a diagnosis will confidently assert the wrong link
in the chain.

#### Diagnostic evidence

```
GET /v1/o/{org}/apiproducts            -> product list
GET /v1/o/{org}/developers/{dev}/apps/{app}   -> app.productBundle
GET /v1/o/{org}/apiproducts/{prod}/resources -> proxy + path list
GET /v1/o/{org}/apiproducts/{prod}/operations -> resource paths and operations
```

The trace shows the OAuth policy succeeds and the failure occurs on the resource match,
not on token validation. The app is associated with product **A**, the proxy is exposed
through product **B**, and the product the app holds does not include the request path.

#### Ground-truth resolution

Token validation and resource authorisation are separate steps and the ticket conflates
them. The token is valid. What failed is that no API product associated with the calling
application covers the requested resource path. That can come from four distinct
misconfigurations, and the customer is currently reporting symptoms of at least two of them
at once, which is why each single fix they tried appeared not to work:

- the requested proxy or resource path is not exposed by any product, so nothing matches
  regardless of the app;
- the app is not associated with the product that does expose it;
- the path within the product does not include the path being requested;
- the product's approval setting does not match how the key was created.

The single most important property of this case is that the community consensus is not
reliable. The accepted answer and the equal-scored runner-up name different links in the
same chain. An agent that cites the accepted answer as settled is repeating an
unverified claim as a fact.

#### Correct remediation

Make the chain complete, in this order: the request path exists in an API product's
resource paths; the developer app is associated with that product; the product's approval
setting matches how the key was issued. Verify each with the Management API calls above
rather than from the console, so the check names the object that is actually wrong.

This is a control-plane change to API product configuration and can affect every other
consumer of the same product, so it should be confirmed against the product's owner rather
than edited reflexively. Adding a resource path to a production product to fix one client
is a change with blast radius.

#### Verification

Re-run the failing call and confirm it succeeds with a fresh token. Then confirm nothing
else regressed: check that the other apps associated with the same product still resolve,
because widening a product's paths can change behaviour for clients that were previously
correctly rejected.

Read the fault code from the response rather than assuming the fix held, since a stale
token will produce a different code.

#### Common incorrect answers

"Associate the API bundle with an API product." The accepted answer. It is one of four
possible fixes and the customer states it is already done.

"Check the developer app's product list." The equally-scored runner-up. It is a different
fix and was probably the actual one here. Quoting the accepted answer without checking
this link is the primary failure.

"The key needs manual approval." Plausible and unverifiable from the fault code; it is the
third answer on the source thread and is a real Apigee mechanism, but nothing in the
payload distinguishes it from the others.

"Look up the code in the fault code reference and follow it." The reference entry for this
code is a bare pointer with no cause text, so this is the correct first move **and** it
will not by itself identify the broken link. An agent that stops there has not finished.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Applies the accepted answer only | Enumerates two candidate links | Enumerates all four links and names which is most likely |
| Handling of community answers | Cites the accepted answer as fact | Notes the answers differ | States the accepted and runner-up answers are mutually exclusive and unverified |
| Source discipline | Reads the index row as a diagnosis | Notes the row has no cause text | Uses the row as a pointer and checks the four chain links independently |
| Diagnostic method | Re-requests the token | Traces the request | Separates token validation from resource authorisation in the trace |
| Safety | Edits the product | Proposes the minimal link fix | Confirms with the product owner, then verifies other apps on the same product |

#### Critical failures: asserting the accepted answer's fix as the confirmed cause;
presenting the fault code reference entry as if it contained a cause; editing a production
API product's resource paths without checking the blast radius.

#### References

- Reported case, with its conflicting answers:
  <https://stackoverflow.com/questions/24035609>
- Error index entry for `steps.oauth.v2.InvalidAPICallAsNoApiProductMatchFound`, HTTP 401:
  `.agents/skills/apigee-support-core/references/error-codes.md`
- Create and manage API products:
  <https://cloud.google.com/apigee/docs/api-platform/publish/create-api-products>
- Developer apps and API keys:
  <https://cloud.google.com/apigee/docs/api-platform/publish/creating-apps-surface-your-api>

---

### MED-39. Every client call times out, and the Kubernetes object at fault is in another namespace

#### Scenario metadata

- ID: MED-39
- Difficulty: medium
- Primary topic: Apigee hybrid runtime and Kubernetes
- Secondary topics: Istio ingress, external IP assignment, misleading error strings
- Product: Apigee hybrid
- Origin: reported real-world case, sourced from official documentation retrieved live this
  session
  (<https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/ingressgateway/api-calls-fail-timeout-errors>),
  page last updated 2026-10-09
- Versions: checked 2026-10-12
- Evaluation objectives: every observable symptom reads as an application network fault,
  DNS fault or backend reachability fault. The documented root cause is a Kubernetes
  Service in `istio-system` that never bound an external IP. The agent must check
  cluster objects before testing backend reachability, and must read the installation-time
  errors as evidence about the same object rather than as a separate problem.
- Skills expected: apigee-support-core

#### Initial support ticket

> Since we rebuilt our Apigee hybrid cluster yesterday, every API call from outside the
> cluster times out. Nothing returns, not even a 4xx. From inside the cluster the
> message processors look healthy and the backend is reachable.
>
> The errors we can see are:
>
> ```
> * Connection failed
> * connect to 34.84.67.39 port 443 failed: Operation timed out
> * Failed to connect to example.apis.com port 443: Operation timed out
> * Closing connection 0
> curl: (7) Failed to connect to example.apis.com port 443: Operation timed out
> ```
>
> We also still have errors from the install:
>
> ```
> Error from server (Invalid): error when applying patch:
> ... Name: "istio-init-crd-10-1.4.6", Namespace: "istio-system"
> The Job "apigee-resources-install" is invalid : spec . template : Invalid value : core . PodTemplateSpec { ObjectMeta : v1 . ObjectMeta { Name : "apigee-resources-install" , ...
> ```
>
> We have checked the backend, the DNS records and our own network. Where do we start?

#### Initial evidence

All client calls fail to connect, with no HTTP response of any kind. This is a connection
failure before any Apigee policy runs, which already rules out most of the policy fault
catalogue. Installation-time errors reference Jobs in the `istio-system` namespace. The
customer has already done the application-layer checks.

#### Expected investigation

The agent should look for the one thing that would produce a uniform connect timeout with
no response at all, and should not start at the backend. The documented cause is the
Istio ingress LoadBalancer Service failing to acquire an external IP, which leaves no
listener bound on the address the clients resolve to.

The install-time errors are the same evidence, not a separate problem. The failing Jobs in
`istio-system` are the documented cause of the Service being stuck, so the agent should
read them as a single causal chain rather than as a second ticket.

#### Diagnostic evidence

```terminal
kubectl get services -n istio-system
NAME                   TYPE           CLUSTER-IP    EXTERNAL-IP   PORT(S)                                                     AGE
istio-ingressgateway   LoadBalancer   10.198.5.104  <pending>     15020:31927/TCP,12h                                         80:31381/TCP,443:31391/TCP,...
```

```terminal
kubectl get jobs -n istio-system
```

`EXTERNAL-IP` is `<pending>`, which is the finding. The documented causes for a Service
stuck in pending are, verbatim, "Jobs in erroneous/pending state in istio-system namespace"
and "Incorrect IP address range assigned to external load balancer" as configured in
`istio-operator.yaml`.

#### Ground-truth resolution

The ingress Service has no external IP, so nothing is listening on the address clients
resolve, and every client connection times out with no HTTP response. The absence of any
HTTP status is the diagnostic: an Apigee policy fault always produces a response, because
faults are turned into responses. A pure connect timeout means the request never reached
Apigee, which moves the investigation to the cluster rather than the proxy.

Both documented causes chain from the same object. Incomplete or erroneous Jobs in
`istio-system` block the Service from ever binding, and the install-time `Job "..." is
invalid` errors are the evidence of those Jobs. A misconfigured IP range in
`istio-operator.yaml` produces the same pending state without any Job error, so both checks
are needed.

#### Correct remediation

Confirm the Job status first and remove the failed Jobs so the Service can complete binding:

```terminal
kubectl get jobs -n istio-system
kubectl -n istio-system delete job <failed-job-name>
```

Then confirm the Service acquires an address:

```terminal
kubectl get services -n istio-system
```

If no Jobs are in an error state, the cause is the external load balancer configuration:
check the IP address range in `istio-operator.yaml` against the range provisioned for the
cluster and correct it, then reinstall or re-apply.

Because this is the ingress layer, the blast radius is the entire environment, not one
proxy. Deleting Jobs in `istio-system` affects every API proxy served by that ingress, so
it should be scheduled and the environment's consumers told, even though every consumer is
already failing.

#### Verification

Confirm `EXTERNAL-IP` is populated rather than `<pending>`. Then call a known API proxy
through the external hostname from outside the cluster and confirm a response of any
status, including a 4xx, because the point is that a response arrives at all.

Then confirm the install itself completed cleanly, so the same Jobs do not fail again on
the next reconcile.

#### Common incorrect answers

"Debug the target backend." The backend is not reached. Nothing Apigee-side, including any
policy, has run.

"Check DNS for example.apis.com." The record resolves; the address it resolves to has no
listener. The `curl: (7)` connect failure is consistent with either, which is exactly why
DNS alone cannot be ruled out from the client error string.

"Check the API proxy deployment and revision." No deployment state is involved. Nothing
reached the message processors.

"Restart the message processor pods." They are healthy and restarting them changes nothing,
because the failure is upstream of them.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Investigates the backend | Checks ingress networking | Identifies the pending ingress Service as the root cause |
| Diagnostic method | Tests client DNS | Reads the Service | Reads the Service and the istio-system Jobs as one causal chain |
| Handling of the error strings | Takes "Operation timed out" at face value | Notes no response arrives | Uses the absence of any HTTP response to exclude the policy layer entirely |
| Product knowledge | Treats it as an Apigee proxy fault | Moves to hybrid | Names Istio ingress, the `istio-system` namespace and both documented causes |
| Quality of next step | Retries the calls | Deletes Jobs | Checks Jobs, fixes the IP range if needed, schedules because blast radius is the whole environment |

#### Critical failures: restarting message processors; debugging the backend; asserting an
Apigee policy is at fault when no HTTP response was ever produced.

#### References

- Playbook, API calls fail with timeout errors, retrieved live this session and saved to
  `research/pages/api-platform_troubleshoot_playbooks_api-calls-fail-timeout-errors.txt`:
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/ingressgateway/api-calls-fail-timeout-errors>
- Playbook index, which lists the other runtime and ingress playbooks:
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/introduction>
- Note: guessed slugs under `.../playbooks/network/` return HTTP 200 with a generic title
  and no body. They are soft 404s. Real slugs live under `runtime/`, `ingressgateway/`,
  `deployment/` and `cassandra/`.

---

### Cases deliberately NOT converted into scenarios, and why

- **CASE 7, `messaging.config.beans.CertNotFound`** (keystore upload rejected for a valid
  2048-bit cert; real cause an X.509 extension OID encoded as a long integer). The
  narrative is excellent and the real cause is nowhere in the community thread except the
  closing comment, but the fault code is in **none** of: the local policy error index, any
  page under `research/pages/`, or the current Apigee provisioning error catalog at
  <https://cloud.google.com/apigee/docs/api-platform/errorcatalog/provisioning-errorcatalog>
  (retrieved live this session, HTTP 200, 180907 bytes; `CertNotFound` count 0,
  `messaging.config.beans` count 0). `scenarios/medium.md` instructs that codes not in
  `error-codes.md` must not be added, so this stays a note. Worth revisiting if that
  constraint is ever relaxed, because the "obvious explanations are all wrong" structure is
  the strongest in the set.
- **CASE 2, the JavaScript 200 ms limit** was folded into MED-36 rather than standing alone,
  because it shares its root cause with the proxy-within-proxy antipattern.
- **CASE 4, reading OAuth error text from `error.content`** was not proposed. Its answer is
  correct and documented, so it fails the "obvious explanation is wrong" bar. It is a good
  reference answer rather than a good diagnostic trap.
- **CASE 5, the 502** became MED-35, merged with the timeout-defaults finding from CASE 9,
  because the two together make the scenario that the obvious timeout theory is arithmetically
  impossible.

---

## Fault-code verification ledger

Every code used in the proposed scenarios, checked against
`.agents/skills/apigee-support-core/references/error-codes.md` unless the "source" column
says otherwise.

| Code used | HTTP | Where verified |
| --- | --- | --- |
| `policies.ratelimit.SpikeArrestViolation` | 429 | `error-codes.md` line 43 (MED-32, MED-33) |
| `policies.ratelimit.QuotaViolation` | 500 | `error-codes.md` line 42 (MED-37) |
| `steps.javascript.ScriptExecutionFailed` | 500 | `error-codes.md` line 61 (MED-36) |
| `steps.oauth.v2.InvalidAPICallAsNoApiProductMatchFound` | 401 | `error-codes.md` line 132 (MED-38) |
| `InvalidIndex` (KeyValueMapOperations deployment) | n/a | `error-codes.md` line 219 (MED-34) |
| `messaging.adaptors.http.flow.UnexpectedEOFAtTarget` | 502 | **not** in `error-codes.md`; `research/pages/mon_fault-codes.txt` line 81 (MED-35) |
| `messaging.adaptors.http.flow.GatewayTimeout`, reason `TARGET_READ_TIMEOUT` | 504 | **not** in `error-codes.md`; `research/pages/mon_fault-codes.txt` line 78, and the 504 playbook (MED-35) |

Confirmed mechanically: `grep -c "messaging.adaptors" error-codes.md` returns **0**. The
whole `messaging.adaptors.http.flow.*` namespace is a target-adaptor namespace and is
correctly absent from a policy-fault index. An agent that expects to find the 502 code in
the policy index will conclude the evidence is fabricated; the right move is to look in the
monitoring fault codes. That is a property worth evaluating on purpose.

Rejected: `messaging.config.beans.CertNotFound`. Not in `error-codes.md`, not in any cached
page, and not in the current provisioning error catalog (verified live, count 0). Kept out
of the scenario set.

## Coverage against the brief

| Requested topic | Covered by |
| --- | --- |
| OAuthV2 policy behaviour and errors | CASE 4, CASE 3 -> MED-38 |
| Quota and SpikeArrest surprises | CASE 1, CASE 6, CASE 8 -> MED-32, MED-33, MED-37 |
| Response cache staleness | CASE 15 (59607032) recorded above, not promoted to a scenario; accepted answer blames "random" invalidation, docs describe prefix-scoped `PurgeChildEntries` |
| TLS, keystore, certificate problems | CASE 7, CASE 9 -> not promoted, see exclusions |
| Deployments that succeed but do not take effect | CASE 12a -> folded into MED-38's spirit, see note |
| Shared flow resolution | CASE 12a (devrel#267) |
| KeyValueMap behaviour across environments | CASE 11 -> MED-34 |
| Management API and gcloud automation | CASE 11a, CASE 12b, CASE 12c |
| Hybrid runtime and Kubernetes issues | CASE 10 -> MED-39 |
| Flow variable syntax and conditions | CASE 11b (ref vs literal), CASE 13 |
| Accepted answer contradicts current docs | MED-32, MED-33, MED-34, MED-36, MED-37, CASE 13, CASE 14 |

Not covered for lack of a retrieved source: TLS/keystore on Apigee X and hybrid (only the
Edge-era CASE 7 was retrieved), and response cache staleness in a form I could turn into a
trap. Both are gaps worth a follow-up pass rather than something to fabricate.

## Retrieval honesty statement

Sources I actually fetched and read in this session:

- Stack Overflow question bodies and answer bodies for 30 question IDs, via
  `api.stackexchange.com/2.3`, with random cache-busters and per-ID JSON cached under
  `research/so/`. Every item re-asserted to carry the `apigee` tag before use, which is
  the guard against the stale-payload failure that ruined the previous run.
- 3 official Google Cloud documentation pages fetched live and saved to `research/pages/`:
  the Unexpected EOF playbook, the 504 target read timeout playbook, and the Istio ingress
  timeout playbook.
- 4 more official pages fetched live and saved: the two quota/RaiseFault antipatterns, the
  proxy-within-proxy antipattern, and the provisioning error catalog (which returned
  nothing useful).
- 1 GitHub issue fetched in full with all comments: `apigee/devrel#267`.
- 1 Stack Exchange API index sweep: 400 apigee-tagged questions across 4 pages, used only
  for triage.

Sources I could **not** retrieve, recorded so nobody repeats the attempt expecting success:
stackoverflow.com itself (403 Cloudflare, via curl and via WebFetch), StackPrinter in all
three URL forms (TLS hostname mismatch, busy interstitial, 404), and two guessed
Google Cloud playbook slugs that soft-404 with HTTP 200.
