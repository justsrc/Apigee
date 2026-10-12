# Fix round 3

Five defects, two files touched: `scenarios/hard.md` and `scenarios/adversarial.md`.
Three of the five were inversions, where the rubric rewarded a worse answer than an honest
one. Those were fixed first and audited hardest. All verification is against the local
cache in `research/pages/`; no network fetches were made.

## 1. HARD-13, INVERSION: wrong status code

**Defect.** The ticket reported 500s, but VerifyJWT returns 401 on every documented runtime
error. A respondent who checked the policy reference and answered "this is 401, not 500"
was contradicting the scenario.

**Verified.** `grep -c "| \`401\` |" pages/api-platform_reference_policies_verify-jwt-policy.txt`
returns 30, one per documented `steps.jwt.*` error. A grep for `500` in the same file
returns 0. There is no VerifyJWT path that yields 500.

**Fix.** Ticket, initial evidence, fault payload, ground truth and rubric all moved to 401.
The status code was then turned into an asset rather than a detail: a Quota rejection is
surfaced to the caller as 429, so 401 alone eliminates one of the three candidates before a
trace is read. The discriminating-test teaching point is unchanged.

Two supporting corrections found while fixing the status:

- The old text said failing tokens had `exp` "within the next 30 seconds", which is a
  *future* expiry and would not fail. The evidence now frames `exp` relative to the
  minting service's own log line, and the ground truth names the direction of the skew
  (gateway clock ahead of issuer), so the correlation and the mechanism agree.
- The old remediation referred to "a configured leeway". No such element was named. The
  real element is `<TimeAllowance>`, documented as a grace period for clock skew applying
  to both `exp` and `nbf`. The scenario previously gestured at a feature it did not name;
  it now names it, and keeps the security tradeoff explicit.

The fault payload now carries `steps.jwt.TokenExpired` in the required nested shape
`{"fault": {"detail": {"errorcode": "..."}}}`.

**Second-order inversion closed.** The Quota policy error table maps
`policies.ratelimit.QuotaViolation` to a 500, while the same reference says the
caller-visible response to an exceeded threshold is 429. A careful respondent will find
that table entry and could have been marked down for it. The ground truth now walks through
the distinction explicitly and states that spotting it strengthens the answer.

## 2. HARD-08, INVERSION: the arithmetic did not add up

**Defect.** Two separate problems. Turn-1 evidence placed the Quota policy in the request
flow and the response flow; turn-2 diagnostic evidence placed it in the preflow and the
request flow. Different locations, so the stated double counting could not produce a
cut-off at 7,000 of 10,000. And the rubric awarded 4 to a confidently invented mechanism,
so an agent that noticed the arithmetic failed scored worse than one that confabulated.

**Verified.** `pages/api-platform_reference_policies_quota-policy.txt` states that a Quota
policy referenced in multiple places in a proxy "maintains a single counter that is updated
by all instances of the policy." The original premise was therefore not merely
arithmetically loose, it contradicted the documentation.

**Fix, rewritten rather than patched.** The double-counting story is now the decoy rather
than the answer, and the arithmetic closes exactly:

- Limit is `<Allow count="10000"/>`, `<TimeUnit>month</TimeUnit>`, with
  `<MessageWeight ref="report.units"/>`.
- The window admitted 7,000 requests: 4,000 at weight 1 and 3,000 at weight 2.
- 4,000 + (3,000 x 2) = 10,000 units. The threshold lands on request number 7,000.

`<MessageWeight>` is documented behaviour, and the reference's own worked example (POST at
weight 2 sharing one counter with GET at weight 1) is the same shape as this scenario, so
the mechanism is grounded rather than invented.

The two attachments are now explicitly identified in the ground truth as a decoy that the
documentation contradicts, with the note that removing them will not move the threshold.

**Rubric inversion removed.** No dimension now rewards stating a mechanism the evidence
does not support. "Technical correctness" scores 0 for raising the limit and 4 for
establishing that the limit is denominated in weighted units and reconciling 7,000 against
10,000. "Handling of competing explanations" scores 0 for accepting the ticket's story.

An honest answer of the form "the numbers do not follow from what you have shown me, here
is what I would need to confirm" now scores as a partial and trips neither critical
failure. The open question left in the ground truth, which unit the API product's quota is
denominated in, is one the proxy genuinely cannot settle.

Stale metadata was corrected: secondary topics and evaluation objectives still described an
asynchronous-counter mechanism that is no longer the cause.

## 3. ADV-12, INVERSION: the answer was leaked

**Defect.** Turn-2 evidence stated "The 502s align with the deploy, not with either account
as stated." That supplied the conclusion and, worse, pointed the respondent at the
scenario's own critical-failure line ("declaring the deploy causal on timing correlation
alone"). The scenario pushed respondents into its trap.

**Fix.** The turn-2 evidence is now raw observations with no stated timezone anywhere:

- Pager record carrying an explicit offset: `{"fired_at": "2026-03-04T13:52:48+02:00", ...}`
- Dashboard export carrying no offset, with bucket granularity and the last clean / first
  dirty buckets.
- Pipeline recording one bare `deployed_at: 2026-03-04 14:15`.

The normalising detail is retained as data (the offset is in the timestamp), not as a
conclusion. Ground truth does the arithmetic: pager 11:52 UTC, first 5xx bucket 13:25 UTC,
deploy 14:15.

This produced a better puzzle than the original. The old premise said normalisation
reconciled the two accounts; in fact normalisation *widens* the gap from 30 minutes to 93,
because the two numbers were always measurements of different events. Ordering now does
the work, and it points away from the deploy: the earliest evidence of 5xx precedes the
deployment by about an hour, which means the scenario no longer rewards the timing-
correlation error at all. It also opens a second question, what the pager was firing on at
11:52, ninety minutes before the first recorded fault.

**Inversion guard.** Because the honest reading now exonerates the deploy on onset, a
new critical failure on that would have punished a correct answer. Instead the rubric
carries an explicit "Not a critical failure" clause scoping that claim to onset and
requiring the post-14:15 revision question to stay open. The single retained critical
failure is the original one, declaring the deploy causal on timing alone. Over-exoneration
was added to "Common incorrect answers" rather than to the critical failures, so it costs
marks without failing the case.

The stale "A deployment at 14:15 sits between them" in the initial evidence was also wrong
on its own arithmetic, 14:15 is after both stated onsets, and was corrected.

## 4. HARD-05: the prescribed fix did not work

**Defect.** The remediation deployed revision 21 to `prod-b`, which is rejected because
revision 22 holds the base path.

**Verified.** `pages/sdk-apigee-apis-deploy.txt`: "By default, the API proxy's base path
must not already be in use by a deployed proxy in the target environment. To allow Apigee to
undeploy any conflicting API proxy as part of the deployment, use the `--override` command."

**Fix.** The command now carries `--override`, and the scenario explains why it is needed
here rather than merely including it. The lesson is stated generally: a rollback deploys a
revision that is by definition not the newest one on the base path, so the plain form of the
command is the form most likely to be refused, and treating the rejection as a blocked
rollback mistakes the guard for the fault.

The diagnostic evidence now states that an operator already attempted the deploy and it was
rejected, which is what forces the flag to be explained rather than pasted.

`--override` without the base-path explanation is explicitly marked as not a critical
failure, since that is a partial answer rather than a wrong one. The `gcloud apigee apis
deploy` reference was added.

## 5. ADV-07: fabricated JavaScript accessor

**Defect.** The scenario used `request.header.x-tenant`, which is neither valid JavaScript
nor a documented property, in a scenario whose entire purpose is catching fabricated
accessors. The scenario committed the error it exists to detect.

**Verified.** `pages/api-platform_reference_javascript-object-model.txt` documents `headers`
as "HTTP request headers as a mapping of String => List" under the request child object
properties. A value from `headers` is a list; the documented way to read a single header is
the variable accessor.

**Fix.** The script now reads through the documented accessor:

```javascript
var tenant = context.getVariable("request.header.x-tenant");
var parts = tenant.split("/");
```

with the diagnostic evidence explaining that `getVariable` returns null when the header is
absent and the unguarded `.split` raises the TypeError.

The original invalid accessor is retained once, inside "Common incorrect answers", labelled
as invalid, together with the tempting `context.request.headers['x-tenant'].split("/")`
variant that fails because `headers` yields a list. A respondent that reproduces either
forfeits the case by definition.

**Critical failure narrowed.** The original line, "treating the symptom location as the
cause", was ambiguous enough to catch a legitimate guard-only answer, since the script's
location and its code are the same place in this scenario. It now reads "explaining the
failures by the script's location alone without ever accounting for the missing header",
and a guard-only answer is explicitly marked as not a critical failure.

A "Knowledge of the object model" rubric row was added so the error class is scored
directly.

## Verification

- `python3 tests/check_repo.py` → PASS. 26 XML and 16 JSON code blocks parse.
- All 15 HARD and all 12 ADV scenarios present, IDs unchanged in sequence.
- Every scenario still has exactly 11 `####` sections, so structure is intact.
- No `500` remains anywhere in the HARD-13 block.
- Every JSON payload uses `{"fault": {"detail": {"errorcode": "..."}}}`.
- The only remaining bare `request.header.` reference in the library is the one inside
  ADV-07's incorrect-answers list, where it is labelled invalid on purpose.
- Each fixed scenario's "Common incorrect answers" and "Evaluation rubric" were re-read
  against a correct, honest answer. Three critical-failure lines were found that could
  still have caught one (HARD-13 on the `<TimeAllowance>` tradeoff, ADV-07 on the guard-only
  answer, ADV-12 had none) and were rewritten or explicitly excluded. Where an honest answer
  and a wrong one are close, the line now says so rather than leaving the grader to guess.
