# Outstanding scenario errors

> **Superseded as a list of what is outstanding.** The findings below are preserved as
> written. Most have since been fixed, and the file has not been rewritten to hide that.
> The current record of what is still open is `evaluation/defect-register.md`, and the
> current verdict is `evaluation/RELEASE-REPORT.md` section 0.
>
> Still live as of 2026-10-13:
>
> - **Unsourced trace step names.** `AM-VerifyToken` is still used as if it came from a real
>   trace (`scenarios/hard.md`). The other invented name this entry cites, `AM-Count-Tokens`,
>   no longer appears anywhere in the repository.
> - **EASY-14's fault code is still not in the policy error index.**
>   `messaging.adaptors.http.flow.SslHandshakeFailed` is not raised by a policy page. The
>   scenario now says so in a caveat of its own, so the gap is disclosed rather than silent,
>   but the code is still absent from `references/error-codes.md`.
>
> No longer live: the two-turn release (`make_packets.py` implements turn 2), the rubric's
> missing weights and pass mark (`evaluation/rubric.md` now defines both),
> `context.request.getValue`, `REG-06`'s invented `location` attribute, `HARD-03`'s
> `ClientCertStore`, `HARD-05`'s environment-group traffic split, `HARD-07`'s claim that
> there is no in-place certificate update, `HARD-11`'s 504 from a callout `<Timeout>`,
> `HARD-14`'s Postgres store, `EASY-12`'s wrong fault code, `MED-03` and `EASY-04`'s
> unbuildable XML, and `MED-15`. The one claim this list made about the recorded eval runs,
> that they recorded no model, version, skill version or date, remains true of those runs and
> cannot be fixed retroactively; `evaluation/test-protocol.md` now requires all four.

Tracked deliberately rather than quietly fixed. Two hostile reviews found 16 material
errors across 65 scenarios, roughly 25%. Eight are fixed. The rest are listed here with
the finding and the doc that contradicts each one, so a fix is mechanical rather than a
fresh investigation.

Reviews: `evaluation/review-easy-medium.md` (30 scenarios, 12 material errors) and
`evaluation/review-hard-adv-reg.md` (33 scenarios, 4 material errors, plus HARD-03 and
HARD-14 called out). A third agent reviewing real-world research independently reached the
same conclusion about MED-07 without having seen either review.

Round two also imported seven new scenarios (MED-16 to MED-22) derived from real public
issue reports, bringing the library to 72 scenarios, and added `references/hybrid.md`
covering hybrid sync, key-value maps, logging defaults and upgrades, which had previously
been an acknowledged gap.

## Fixed

**Error payload shape, all 45 graded scenarios.** Every body showed a flat
`{"errorcode", "faultstring", "status"}`. The documented shape is nested under `fault`,
and there is no `status` field in the body at all. Corrected via `tests/fix_error_shape.py`.
This was worse than cosmetic: the core skill tells agents to trap `errorcode`, and that
advice is only actionable if you know where the field lives.

**EASY-06** stated `IgnoreUnresolvedVariables` must be set for the fault to fire. The doc
says it can only occur when it is **false**. The scenario also used `<SourceVariable>`; the
real element is `<Source>`.

**EASY-09** was premised on a client's HTTP `Content-Type`. `InvalidSourceType` is about
the *type of the flow variable* named in `<Source>`, valid types `message` and `string`.
The scenario's own "common incorrect answers" section had it right, contradicting its own
ground truth. Rewritten.

**`references/error-codes.md` was dropping every SpikeArrest runtime code.** The table on
that page renders one cell per line, not as a pipe table, while the Deployment errors
table on the same page renders as pipes. The parser only handled pipes. Fixed, plus a
coverage guard that reports any page with an error section that parsed to nothing. Count
went 165 to 174 runtime codes, and `policies.ratelimit.SpikeArrestViolation` (HTTP **429**)
is now present against `QuotaViolation` (HTTP **500**).

That last one caused the only failing scenario in the assisted eval arm: the agent trusted
the incomplete index over the page and asserted with false confidence that the failing
policy was Quota. A generated reference that is quietly incomplete is worse than none,
because it is trusted.

## Not yet fixed, highest severity first

**HARD-07 is the worst and is close to inverted.** The scenario asserts there is no
in-place certificate update, and lists "inventing an update endpoint" as a critical
failure. But the cited keystore aliases reference documents `update` ("Updates the
certificate in an alias", `PUT .../keystores/*/aliases/*`, IAM
`apigee.keystorealiases.update`), and the TLS page names two methods literally titled
"In-place update". The scenario therefore scores a correct answer as a critical failure,
twice. Either the ground truth or the scenario premise is wrong. Verify the current
methods before rewriting.

**HARD-14 names the wrong store.** The documented coordinated-restore guidance covers
LDAP, ZooKeeper and Cassandra. The scenario says Postgres and never mentions LDAP, while
quoting the guidance as support.

**REG-06 quotes elements that do not exist.** `<APIKey>` has exactly one attribute,
`ref`. The scenario writes `name="apikey" location="header"` and then makes "the
documented meaning of the `location` attribute" the discriminator of the whole scenario.

**HARD-03** uses `<ClientCertStore>` and `<ClientCertAlias>`, which appear nowhere. The
documented elements are `KeyStore`, `KeyAlias` and `TrustStore`.

**HARD-05** builds on an "environment group traffic split". Environment groups carry
hostnames, not weights, and a deployment overwrites the prior revision. The remediation
manipulates a control that does not exist.

**HARD-11** attributes 504s to a ServiceCallout `<Timeout>` expiry. A callout timeout
returns HTTP 500. 504 comes from `io.timeout.millis`, `api.timeout` or target read/write
timeouts.

**EASY-12** is premised on a wrong fault code entirely.
`steps.oauth.v2.InvalidEarlyTimestamp` is documented on the RevokeOAuthV2 page, not
OAuthV2. Its status is **500**, not 401. Its documented cause is "Timestamp cannot be
earlier than January 1, 2014", not `nbf` clock skew. The whole clock-skew narrative is
invented and needs replacing.

**MED-15 is unsatisfiable as written.** It asserts a deployment-only error firing at
runtime while its own evidence says the deployment succeeded.

**MED-07** claimed a documented hybrid-versus-Apigee shared-flow validation difference that
appeared in neither cited page and flatly contradicted EASY-03. **FIXED.** Two
independent reviewers confirmed it was unsourced, and it was rewritten around a verified
hybrid failure: a deployment that succeeds while the Synchronizer silently fails to pull
the contract because `setSyncAuthorization` was never called with an identity holding the
Apigee Synchronizer Manager role.

**MED-03 and EASY-04 supply XML that cannot produce the fault described.** MED-03 uses
`<LoadBalancing>`, `<TargetServer>`, `<MinTimeBetweenFailures>`; EASY-04 uses `<Address>`
with `mask="32"`. The documented schema is different in both cases.

## Suite-level defects

**`context.request.getValue` does not exist** in the JavaScript object model. It appears in
scenario bodies and sample code.

**Trace step names are unsourced.** Invented names such as `AM-VerifyToken` and
`AM-Count-Tokens` are presented as if they came from a real trace.

**EASY-14 uses a fault code absent from `error-codes.md`**, violating the suite's own rule
that every code must come from the index.

**The protocol never released diagnostic evidence.** `tests/make_packets.py` extracts only
the ticket and initial evidence, and the two-turn release described in
`evaluation/test-protocol.md` step 3 was never implemented. Six of the seven evaluated
ground truths were unreachable, which is part of why both arms scored poorly.

**`evaluation/rubric.md` says "weighted total" but specifies no weights**, and the
per-scenario tables score 3 to 5 of its 10 dimensions.

**Neither eval run recorded model, version, skill version or date.**

## What this says about round one

The error rate is the honest headline. Thirty scenarios, two reviewer agents, and roughly
a quarter had a material defect. Most were invented XML and misattributed fault codes, in
exactly the categories the suite is supposed to catch. Round one passed every mechanical
check and every URL check while being wrong at that rate, which is the clearest evidence
in this project that a passing harness says almost nothing about content.