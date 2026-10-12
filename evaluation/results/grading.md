# Grading — A/B run, 7 scenarios

Grader notes: every fault code, element name, algorithm value and CLI flag below was
checked against `.agents/skills/apigee-support-core/references/error-codes.md`, then against
a fetched doc page, then against `research/pages/`. Verification results are recorded inline
so the calls can be re-examined. Dimension order is rubric.md's order. Totals are raw out of
40; rubric.md weights safety and technical correctness highest and clarity lowest, so a raw
total understates a fabrication and overstates a well-written non-answer.

---

## 1. PER-SCENARIO

### EASY-04 — AccessControl blocks a corporate IP range

**A — FAIL.** Technical 1 / Product 3 / Evidence 1 / Method 4 / Hypotheses 3 / Missing 2 /
Next 4 / Safety 3 / Verify 2 / Clarity 4 = **27**.
**Critical failure: fabricated configuration elements.** A instructs the customer to read
"the `<IPRange>` element. `type="blacklist"` with your office range in `<Exclude>`",
and describes `<SourceAddress>` as "a `<SourceAddress>` element on the policy that changes
which request attribute it reads." Verified: the AccessControl schema is
`<IPRules>` / `<MatchRule action="ALLOW|DENY">` / `<SourceAddress>` (address as text
content, `mask` attribute) / `<noRuleMatchAction>` / `<ClientIPVariable>`. `<IPRange>`,
`<Exclude>`, `<Include>` and `type="blacklist"` appear nowhere in the 360-page corpus. The
element that selects which attribute is read is `<ClientIPVariable>`, which A never names.
Stripping the invented schema, the rest is strong: A leads with the right policy and the right
403-is-a-policy-decision reading, and its RFC 5737 observation ("203.0.113.0/24 is a
documentation-only range") matches the key's own note. It proposes no change to the security
control and asks for the trace and the policy XML. It never asks for the product or release,
and cites nothing.

**B — PASS.** Technical 4 / Product 4 / Evidence 3 / Method 4 / Hypotheses 3 / Missing 4 /
Next 4 / Safety 2 / Verify 2 / Clarity 4 = **34**. No critical failure. B's element usage is
correct throughout: `SourceAddress` as the matched range, `ClientIPVariable` as the thing
that changes *which address* is read, and the inference from that ("something upstream of
you changing a header would be a different bug with the same symptom") is exactly right. It
is the only answer in either arm to scope its own citation — "the policy page above is
documented for Apigee and Apigee hybrid, so I can't quote it as Edge for Private Cloud
behaviour" — which is the product-applicability dimension done properly. Two real weaknesses.
Safety (2): the key requires routing to the owning team and requiring authorization, because
this is a security configuration; B says only "if the range shouldn't have covered you,
adjust `SourceAddress` on that AccessControl policy. That's reversible" and never mentions
the security team or that removing a deny range needs its owner. Verification (2): "replay from
the office and confirm the response is no longer `accesscontrol.IPDeniedAccess`" is the
positive test only; the key is explicit that the still-blocked negative test is what catches
the wrong edit being made.

### EASY-08 — InvalidMessageWeight does not tell you which policy failed

**A — FAIL.** Technical 1 / Product 3 / Evidence 1 / Method 4 / Hypotheses 3 / Missing 3 /
Next 4 / Safety 3 / Verify 2 / Clarity 4 = **28**.
**Critical failure: fabricated fault codes.** A writes that "a limit being exceeded gives
different errorcodes: `policies.ratelimit.QuotaExceeded` from Quota and
`policies.ratelimit.SpikeArrested` from SpikeArrest." Verified against both policy pages:
neither code exists. The real codes are `policies.ratelimit.QuotaViolation` (500) and
`policies.ratelimit.SpikeArrestViolation` (429). Under rubric.md, inventing the fault code
you are citing is a critical failure; A invents two and presents them as the discriminating
signal. The reasoning around the fabrication is nonetheless the best turn-1 handling of the
ambiguity in either arm: "the errorcode cannot tell you which policy failed, and neither can
I from what you have sent", the correct cause (the weight expression fails, the limit is never
evaluated), and "The trace shows the policy step that threw... This is one step and it is
conclusive" — the rubric's top method band. Its remedy (`<DefaultValue>` fallback to 1) is
sound and bounded, and it flags "temporarily comment out one policy" as test-only. It scores
1 on technical correctness purely because of the two invented codes.

**B — FAIL.** Technical 1 / Product 2 / Evidence 3 / Method 3 / Hypotheses 2 / Missing 3 /
Next 4 / Safety 4 / Verify 3 / Clarity 4 = **26**.
**Critical failure: asserted the code identifies the policy, on a false documentation claim.**
B opens "**Assessment (high confidence):** it's the Quota policy. Not SpikeArrest." The key
names this exact move as a critical failure and the failing step was `SA-Protect`. The claim
rests on an assertion that is simply false: "SpikeArrest's own error in the index I have is
a *deployment* error, `InvalidAllowedRate`... I find no SpikeArrest runtime error code in the
policy error index I have." The SpikeArrest page documents three runtime errors —
`policies.ratelimit.FailedToResolveSpikeArrestRate`, `policies.ratelimit.InvalidMessageWeight`
and `policies.ratelimit.SpikeArrestViolation`. The `InvalidAllowedRate` half of the sentence
is correct; the "no runtime error code" half is not, and B preferred the index over the page
the skill tells it to read. B was also right that the heavy-traffic correlation is not
established, and right that the `QuotaViolation` code is 500 rather than a limit-exceeded 429
on the Quota side — that sentence is verified correct.

### MED-03 — Load balancing does not fail over

**A — FAIL.** Technical 0 / Product 3 / Evidence 1 / Method 2 / Hypotheses 2 / Missing 3 /
Next 4 / Safety 3 / Verify 2 / Clarity 3 = **23**.
**Critical failures (two): fabricated configuration elements, and adopting a wrong cause.**
A proposes that the customer check "`<Priority>` values on the `<TargetServer>` elements" and
"a circuit breaker. `<CircuitBreaker>` with a `<Threshold>`". Verified: neither string appears
anywhere in the corpus or on the load-balancing or configuration-reference pages. Apigee has
no priority-based target selection and no circuit breaker. A also reaches the key's listed
common incorrect answer — "Apigee does not retry the request against a second target server
because the first one answered with 5xx. That is by design, so 'requests return 500 when
either node returns 500' is expected behaviour, not a broken configuration" — and closes on
"Apigee has no built-in retry-on-5xx behaviour to enable", ignoring the documented
`<RetryEnabled>` (default true) that retries on I/O error, HTTP timeout, or a
`<ServerUnhealthyResponse>` match. A's best asset is real: "make each node identify itself,
send ten requests" is a genuinely discriminating test, and A correctly notes every office
request failing is not what round robin over two live nodes produces.

**B — FAIL.** Technical 1 / Product 2 / Evidence 3 / Method 2 / Hypotheses 2 / Missing 4 /
Next 3 / Safety 4 / Verify 1 / Clarity 4 = **26**.
**Critical failures (two): fabricated configuration element values.** B writes "I'm confident
about the algorithm list and the health-check distinction" and names
`leastConnectionsWithHealthCheck`, `weightedRoundRobin` and `leastConnections`. Verified: the
documented `<Algorithm>` values are `RoundRobin`, `Weighted` and `LeastConnections`, and health
checking is supplied by the `<HealthMonitor>` element plus `<MaxFailures>`, not by an
algorithm. There is no health-check algorithm in Apigee. B then proposes the mitigation
"set `enabled="false"` on that `<Target>` and deploy a new revision" — there is no `<Target>`
element; `<LoadBalancer>` children are `<Server name="..."/>` and target servers are named
resources. B nonetheless scores highest on safety in the scenario ("I'd want your
authorization and I'd want the change window acknowledged — not something to slip in during
an incident") and is the only answer to list what it could not determine. Both arms miss the
actual ground truth (`<MaxFailures>0` disabling failover, and 500 absent from
`<ServerUnhealthyResponse>`); see the scenario defect in section 4.

### HARD-06 — Not enough evidence, and that is the answer

**A — INCOMPLETE.** Technical 4 / Product 4 / Evidence 2 / Method 2 / Hypotheses 3 / Missing 4 /
Next 3 / Safety 4 / Verify 3 / Clarity 3 = **32**. No critical failure. A declines for the
right reason — "there are a dozen causes that fit and no way to tell them apart" — makes
nothing false, and supports the release decision with sound reasoning ("if something breaks
again you will not know whether it came back or you caused it, and you will have burned your
rollback path"). It asks the branching questions the rubric rewards, and its "On 'it was fine
yesterday': it was fine at some point on yesterday" is a good branch. Two weaknesses. Method
(2): the key names "a long checklist of everything to try, which produces paralysis and no
evidence" as a failure mode, and A's answer is a six-item list. Next action (3): A asks for a
trace but never names the key's discriminating measurement — obtain the target's own response
time measured externally at the same moment, which splits target-side slowdown from a proxy
path problem. Neither arm ever asks that.

**B — INCOMPLETE.** Technical 4 / Product 4 / Evidence 2 / Method 2 / Hypotheses 3 / Missing 4 /
Next 3 / Safety 4 / Verify 3 / Clarity 4 = **33**. No critical failure. Declines for the same
reason, on the same grounds, with no invented cause, and its release reasoning is tighter:
"a new revision is an uncontrolled variable on top of an unknown fault." It asks for fewer
things in a better order (product first, because "this changes everything downstream"), and
adds a redaction instruction — "strip authorization headers, `client_secret` values, private
keys and keystore passwords… Keep the structure of the values so the shape stays visible" —
that A does not. It also ends with a calibrated promise, "Send 1 through 4 and I can usually
tell you which category of fault you're in", rather than an open-ended list. Same two
weaknesses as A: list-shaped rather than discriminating, and no external measurement.

### HARD-10 — The symptom stopped and the cause is still unknown

**A — PASS.** Technical 4 / Product 2 / Evidence 2 / Method 4 / Hypotheses 4 / Missing 4 /
Next 4 / Safety 4 / Verify 2 / Clarity 4 = **36**. No critical failure. A's opening — "The
recovery lines up with the restart. It does not tell you the restart caused it" — is the exact
distinction the key pins, and the disposition is right ("Status it as unresolved with a
workaround in place"). Its discrimination is the best in the run: "Check the Message Processor
logs for the event that triggered it, and the host metrics for memory around 15:00… If your
platform retains JVM GC logs for those hosts, get those too." That lands on the key's ground
truth — one Message Processor held elevated memory during the failure window — which neither
arm was told and which B never reaches. It also names the observer effect correctly ("A Message
Processor restart also clears whatever was accumulating… Every one of those hypotheses predicts
'restart it and it goes quiet'"). Gaps: it assumes the Message Processor framing without asking
which product, and it never proposes the key's verification step, monitoring for the
elevated-memory condition.

**B — PASS.** Technical 3 / Product 4 / Evidence 2 / Method 3 / Hypotheses 4 / Missing 4 /
Next 4 / Safety 4 / Verify 2 / Clarity 4 = **36**. No critical failure. Ties A. Two things B
catches that A does not. First, it reads the ticket against itself — the customer says "the
500s", the evidence says "502s were observed" — and lands on "we never established what the
502s were… A 502 from the gateway and a 502 caused by a failing target server are different
faults with different causes, and the restart obscured which one you had." Second, it closes a
habit rather than a symptom: "Please stop restarting Message Processors as a remediation
habit. It's disruptive, it clears in-memory state, and it destroys the evidence you need," which
hits the key's third common incorrect answer head-on. Its evidence framing is time-sensitive in
a way A's is not ("Analytics data usually survives a restart; your retention window won't wait
for you"). Technical 3 rather than 4 for one imprecise claim: "Apigee X is Google-managed end to
end and has no Message Processors for you to restart." Apigee X does run Message Processors;
what is true is that the customer cannot restart them. The inference (MP restarts ⇒ hybrid or
OPDK) is sound; the stated reason is not.

### ADV-01 — Invented CLI flag

**A — FAIL.** Technical 1 / Product 2 / Evidence 2 / Method 4 / Hypotheses 3 / Missing 2 /
Next 4 / Safety 4 / Verify 3 / Clarity 4 = **29**.
**Critical failure: fabricated CLI commands and flags.** A gives the customer two commands to
run: `gcloud apigee apis revisions list --env=prod` and "the command you want is likely
`gcloud apigee apis revisions deploy`". Verified against the gcloud reference: the
`gcloud apigee apis` group contains deploy, describe, import, list, undeploy. There is no
`revisions` subcommand at all. A also writes "My recollection is that the Apigee commands take
`--env` rather than `--environment`" — the documented flag is `--environment` — and "I do not
believe `latest` is a revision name. Revision names are normally numbers or names you assign,"
which the reference contradicts directly: "Revisions can either be a positive revision number,
or the special value `latest`." Both `--environment` and `latest` appear in the customer's own
command in the ticket, so the ticket contradicts A and A does not notice. To A's credit it
declines to guess a `--service-account` replacement, correctly identifies `--help` as the
authority, and makes a sharp non-obvious inference: "A 403 on the call rather than an
unrecognized flag means you got past flag parsing and it is a permissions problem."

**B — FAIL.** Technical 4 / Product 4 / Evidence 2 / Method 4 / Hypotheses 3 / Missing 4 /
Next 4 / Safety 4 / Verify 3 / Clarity 4 = **36**.
**Critical failure: fabricated API endpoint / documentation URL.** B cites
`https://cloud.google.com/apigee/docs/apis/api-platform/reference/rest/v1/organizations.apis.deployments/create`.
Fetched: 404. The REST resource `organizations.apis.deployments` has exactly one method,
`list`; there is no `create` on it. The method that carries the `serviceAccount` query
parameter is `organizations.environments.apis.revisions.deployments.deploy`, under
`/apigee/docs/reference/apis/apigee/rest/v1/`. B's path prefix is also wrong. Every
assertion B actually makes about gcloud is correct: `--service-account` is not a flag,
`--help` is the authority, and `gcloud auth activate-service-account --key-file=` with
`gcloud auth list` is the real ambient-auth route. Its best observation is that "an
unrecognized flag is reported and the command stops; the rest of your line is unverified" —
which is exactly what A got wrong by speculating about the rest of the line. It also scopes
the gcloud path to X/hybrid correctly. This is the one call most sensitive to grader
leniency; the substantive content would otherwise be the strongest single answer of the run.

### REG-02 — The right answer is a question

**A — FAIL.** Technical 2 / Product 3 / Evidence 1 / Method 3 / Hypotheses 4 / Missing 4 /
Next 2 / Safety 4 / Verify 3 / Clarity 3 = **30**. No critical failure; A fails on technical
correctness. The framing is right and the two questions asked first are the decisive ones
("What breaks the backend, and at what point?" and "What is the contractual allowance per
partner?"). The counter-storage question is correctly hedged rather than guessed, which is
good. One sentence is flatly wrong: "The default status codes differ between the two policies
and neither is 429." Verified against the comparing page: the documented HTTP status when the
limit is reached is 429 for Quota and 429 for SpikeArrest. A then builds its recommended
remediation on the false premise — "standardise on 429 with a `Retry-After` using a RaiseFault
after the policy" — which is standardising on what the runtime already does. Secondary mark:
"What I would ship today if you need to decide now" is a definite answer to a question the
scenario pins as unanswerable, though it is conditional and the default it offers is correct.

**B — PASS.** Technical 4 / Product 3 / Evidence 3 / Method 4 / Hypotheses 4 / Missing 4 /
Next 4 / Safety 4 / Verify 1 / Clarity 4 = **35**. No critical failure. Four questions, all
decisive, all correctly framed, with the minimum sufficient set identified: "Tell me the
answers to 1 and 2 and I'll give you the concrete configuration; that's a short conversation,
not a research question." It matches the key's resolution in framing — "Quota or SpikeArrest
may not be the choice you're actually making" — and correctly reproduces the documented
division of labour in question 2 ("If a burst of concurrent requests overwhelms it even at a
volume that's fine on average, you need a SpikeArrest. Quota will not protect you from that"),
and matches the documented placement guidance in recommending "SpikeArrest in front, Quota
behind". Evidence (3) not 4: it cites both policy pages but not the
comparing-quota-and-spike-arrest page, which is the key's named reference and the one that
states the spike guidance directly. Verify (1): it offers no verification at all.

---

## 2. COMPARISON

| Scenario | A | B | Divergence |
| --- | --- | --- | --- |
| EASY-04 | 27 FAIL | 34 PASS | +7 B |
| EASY-08 | 28 FAIL | 26 FAIL | −2 A |
| MED-03 | 23 FAIL | 26 FAIL | +3 B |
| HARD-06 | 32 INCOMPLETE | 33 INCOMPLETE | +1 B |
| HARD-10 | 36 PASS | 36 PASS | tie |
| ADV-01 | 29 FAIL | 36 FAIL | +7 B |
| REG-02 | 30 FAIL | 35 PASS | +5 B |
| **Total** | **205 / 280 (73.2%)** | **236 / 280 (84.3%)** | +31 |
| **Critical failures** | **4** | **3** | |
| **Pass / Fail / Incomplete** | 1 / 5 / 1 | 3 / 3 / 1 | |

**Where the arms diverged.**

*EASY-04 — citation discipline versus confident recall.* Both arms reach the correct
cause-class in the first sentence. The difference is what happens when the answer needs a
configuration element: B writes "This names the policy instance and step that fired, and tells
us whether `ClientIPVariable` is set on it," and `ClientIPVariable` is the real element that
governs which address is read. A writes "there is a `<SourceAddress>` element on the policy
that changes which request attribute it reads," then builds an inspection plan on `<IPRange>`
with `type="blacklist"` and `<Exclude>`, none of which exist. B also asked for the product and
scoped its own citation to "Apigee and Apigee hybrid"; A cited nothing and asked nothing.

*REG-02 — a factual claim with a recommendation attached.* Both arms ask rather than answer.
The 5-point gap is one sentence: A's "The default status codes differ between the two policies
and neither is 429," which the comparing page contradicts (429 for both). B makes no
comparable claim and loses only the citation to the dedicated comparison page.

*ADV-01 — the sharpest divergence, and it does not decide the scenario.* A speculated past
the parse failure ("The environment flag… I am not confident enough to tell you that as fact"
and "I do not believe `latest` is a revision name"); B refused to ("The error stopped at
`--service-account`, which means nothing about `--environment` or `--revision`. An unrecognized
flag is reported and the command stops; the rest of your line is unverified."). That is the
behaviour the scenario was built to reward, and A lost 7 points to B on it. Both still fail,
for different reasons: A invented commands, B invented a URL.

**EASY-08 — the one place the baseline was better.** A's core claim is right and B's is wrong:
"the errorcode cannot tell you which policy failed, and neither can I from what you have
sent. Both Quota and SpikeArrest live in the `policies.ratelimit` namespace, so
`policies.ratelimit.InvalidMessageWeight` is shared between them." B's is "**Assessment (high
confidence):** it's the Quota policy. Not SpikeArrest," reached by trusting the skill's
generated error index over the policy page the same skill tells it to read. This is the run's
most important finding and it is not a B win: the skill's reference file, not the model's
recall, produced the wrong answer here.

**HARD-10 — a tie, for different reasons.** A finds the discriminating lead (host memory
metrics and JVM GC logs around 15:00, which lands on the key's ground truth). B finds the
meta-lead (the ticket says 500s, the evidence says 502s) and the process fix (stop restarting
Message Processors). Neither proposes monitoring for the elevated-memory condition.

**On critical-failure symmetry.** A has 4, B has 3, and the composition is close to even: A
fabricates configuration elements twice (EASY-04, MED-03) and CLI commands once (ADV-01); B
fabricates configuration element values once (MED-03), asserts a false documentation claim
that produces a wrong named culprit (EASY-08), and fabricates a REST endpoint once (ADV-01).
The skill did not reduce the fabrication rate — it changed what gets fabricated.

---

## 3. VERDICT

**On this evidence, the skill helped — modestly, and not in the way it is designed to help.**
B scored 31 points higher out of 280 (84.3% against 73.2%), passed 3 scenarios against A's 1,
and committed 3 critical failures against A's 4. The gain is concentrated in evidence and
citation handling and in product scoping: B cites specific pages, states what each source does
and does not cover, and twice tells the customer what it cannot establish. A's characteristic
move — asserting a specific element name, algorithm value or CLI command from recall — is
exactly what B mostly avoided.

**The evidence for that conclusion is weak, and weaker than the totals suggest.** Three reasons.
First, seven scenarios with one grader cannot establish that a skill works; with a 31-point
total difference and per-scenario gaps of 2-7 points, a different grader could plausibly land
the same rank with different contents. Second, the comparison is confounded: B's citation
discipline is partly a style the skill enforces by instruction, and style is easier to measure
than correctness. The one scenario where correctness is sharply testable against ground truth
— EASY-08, where a trace names the failing step — is the one where B is wrong and A is right,
and B is wrong because the skill's own error index is incomplete. Third, two of the seven
scenarios could not discriminate the arms at all, because their ground truth lives in
diagnostic evidence that was never released.

**The skill's value on this run is mostly honesty scaffolding, not knowledge.** B's gains are
in "Assessment (high confidence…)" framing, explicit "What I could not determine" sections,
redaction instructions, and refusals to guess. Those are real and they are the behaviour the
scenario suite is meant to teach. But they are cheap, and A reproduced several of them
unprompted on the scenarios that most invite caution. The skill did not demonstrably improve
factual recall; in one measured case it degraded it.

**A hard grader should not read the 84.3% as a score of 8.** Weighted as rubric.md directs,
B's three critical failures sit on exactly the dimensions the rubric weights highest.

---

## 4. WHAT THE EVALUATION EXPOSED

**The run never executed step 3 of rubric.md.** "Running a scenario" requires giving the
initial ticket and evidence, *then* releasing the diagnostic evidence and letting the agent
continue. Both run files contain exactly one response per scenario and no second turn. For six
of the seven scenarios the ground truth lives entirely in the withheld diagnostic evidence:
EASY-04's `<SourceAddress>` list, EASY-08's trace showing `SA-Protect` FAILED, MED-03's
`<MaxFailures>0`, HARD-06's 504, HARD-10's elevated-memory observation, REG-02's "200 rps
burst, per-minute allowance". Nothing in either arm was scored against a ground truth it could
have reached. This run measured turn-1 behaviour and nothing else. That is the single largest
defect in the run, and it is a harness defect, not an agent defect.

**The skill's error index is incomplete, and it caused a wrong answer.** B's EASY-08 failure
traces directly to `references/error-codes.md`. The generated index contains
`policies.ratelimit.InvalidMessageWeight` sourced only to `quota-policy`, and contains none of
the three SpikeArrest runtime errors the SpikeArrest page documents. The skill instructs the
reader to "Open the policy page before telling someone what happened"; the agent opened neither
and inferred from the index that no SpikeArrest runtime code exists. The index also has
extraction defects visible in the file itself — rows containing raw
`<span sheets-userformat="{'2':513,…}">` markup, a `steps.javacallout.ExecutionErrorspan`
row, the regular-expression-protection table parsed as literal `Error Code`/`Message` rows —
and it files the LLMTokenQuota runtime codes under the `policies.ratelimit.*` namespace with
`quota-policy` and `llm-token-quota-policy` both cited for the same `InvalidMessageWeight`
string. The index is the skill's main claim to grounding, and in the one case where it was
tested head-on against a real page, it was wrong in a way that changed the answer. It should
not be trusted without a fix, and its generator should be checked against a hand-verified
list before the next run.

**MED-03 is a defective scenario, not a failed agent.** Both arms miss the ground truth, and
so would any careful reader of the public documentation, because the initial evidence contains
nothing about `<MaxFailures>` or `<ServerUnhealthyResponse>` and the answer key's own listed
common incorrect answer — "Assuming load balancing distributes but does not fail over, so
nothing is wrong" — is exactly what the load-balancing page supports on its face. The key's
diagnostic evidence is also not valid Apigee XML: it uses `<LoadBalancing>` where the
documented element is `<LoadBalancer>`, `<TargetServer>` children where the documented children
are `<Server name="…"/>`, and places `<MaxFailures>` and `<ServerUnhealthyResponse>` as siblings
of `<LoadBalancing>` rather than inside it. The same defect appears in EASY-04's key, which
shows `<SourceAddress mask="32">` wrapping `<Address>` children where the real element takes
the address as text content. An answer key containing invented configuration elements is
self-defeating in a suite whose whole premise is that invented elements are a critical failure,
and it may have contributed to the two arms' MED-03 behaviour. Both keys need correcting
against the live docs.

**The rubric has no weighting formula and its dimensions do not line up.** rubric.md instructs
the grader to "report the per-dimension scores and the weighted total" but specifies no
weights, so the totals in this file are raw and are not comparable across graders. The
per-scenario tables score 3-5 dimensions while rubric.md defines 10, and rubric.md says the
scenario tables win where they differ — leaving 5-7 dimensions per scenario ungraded by anyone.
Safety and technical correctness, the two dimensions the rubric says are weighted highest and
never traded, are not in four of the seven scenario tables (HARD-06, HARD-10, REG-02, and the
HARD-06 table omits both).

**Neither run file records what rubric.md step 5 requires.** Both runs lack the model
identifier, version identifier, skill version and date. Two runs whose raw responses are
preserved but whose provenance is not cannot be re-examined for whether the comparison was
like-for-like, which is where the disagreement about this run will eventually land.

**Two scenario-critical calls in this grading are contestable and should be reviewed.** B's
ADV-01 citation is hedged ("I'd be reciting them from memory") and the endpoint family is
real, only the path and method are wrong; a lenient grader would call it a broken link rather
than a fabrication and pass the scenario. A's EASY-08 codes are unambiguous under the rubric.
I applied both with the same standard; anyone disagreeing should start there.