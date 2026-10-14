# Confirmation pass: HARD-02, HARD-08, HARD-09, ADV-08, ADV-11, MED-09, MED-11, EASY-09

Scope: verify every fault code, HTTP status, XML element and configuration value against the
local cache; confirm the ground truth is derivable from turn-1 plus turn-2 evidence; check the
arithmetic and mechanism; check difficulty honesty. Priority check: would a technically correct,
honest respondent trip a listed critical failure, or lose marks for correctly observing that the
evidence does not account for something?

No network was used. Everything below is sourced from `research/pages/`,
`research/scratch-pages/`, `research/pages/MANIFEST.tsv` and
`.agents/skills/apigee-support-core/references/error-codes.md`.

## Inversion audit (priority class)

**No true inversions found in any of the eight.** No scenario lists a critical failure that a
correct, honest answer trips, and none punishes a correct observation of an evidence gap.

Two of the eight (HARD-08, EASY-09) carry an explicit "Not a critical failure" carve-out that
does exactly the job it is meant to, and HARD-09's critical failure is scoped with "without
flagging that it weakens a security control" so that a flagged-wildcard answer survives. That
class of guard is the right one and it is present where it was needed.

Four residual exposure points are recorded below as MINOR (MED-09's title, ADV-11's unevidenced
causal link, ADV-08's `latest`/pinned tension, MED-11's loose "incorrect answer" item). None of
them is a critical-failure inversion; all are unaccounted-for observations or rubric wording that
a literal grader could misapply.

---

## HARD-02. The config and the logs disagree

### Verdict: MINOR

Verified:

- `policies.ratelimit.QuotaViolation` is real, HTTP 500 —
  `error-codes.md:42`, `research/pages/api-platform_reference_policies_quota-policy.txt:1197`.
- Deployment status enum `PROGRESSING` then `READY`, no `DEPLOYING` —
  `api-platform_fundamentals_configure-proxy-with-yaml-example.txt:395` ("Poll the revision's
  deployment status, which reports `PROGRESSING` until it becomes `READY`"); `READY` also at
  `api-platform_deploy_ui-deploy-overview.txt:111,154`; the REST enum at
  `scratch-pages/rev-env-deployments-res.txt:298-299`.
- "Traces show the executing revision" is documented: debug session data carries
  `"Revision": "1"` (`research/pages/dbg_trace.txt:373,549`) and `apiproxy.revision`
  (`dbg_trace.txt:516`). The citation is sound.
- Scenario body is byte-identical in substance to `evaluation/packets/HARD-02.key.md`. No drift.
- Ground truth derivable: deployment state and trace revision are both handed over as
  diagnostic evidence.

Issues:

1. **Unexplained timeline contradiction inside the scenario (MINOR).** The ticket says the
   change "was deployed successfully" and was made "last month"; the diagnostic evidence says
   revision 20 is *still* `PROGRESSING`. A deployment held in `PROGRESSING` for a month is itself
   an anomaly, and Apigee documents that this state can happen:
   `research/pages/hybrid_release-notes.txt:3243` and `:3667` — "API proxy deployment could become
   stuck in `PROGRESSING` state." The scenario never surfaces this, no band credits an agent who
   raises it, and neither the scenario nor the key states how long the deployment has been in
   flight. This is mildly ironic in a scenario whose subject is noticing contradictions, and a
   correct agent is likely to raise it with no rubric credit either way (it is not a critical
   failure, and "Handling of uncertainty / 4 = States what is confirmed and what is not" is a
   natural home for it). Recommend stating the elapsed time in the evidence, or adding a line to
   "Expected investigation" acknowledging that `PROGRESSING` for a month needs its own
   investigation.

Difficulty honest: yes. Competing causes (stale fault code / caching / mid-deployment) with a
discriminating test, which is the file's own bar for hard.

---

## HARD-08. Quota appears to count twice

### Verdict: CORRECT

Arithmetic closes, all three branches:

- Weight contribution: 5,000 x 1 + 2,000 x 2 = 9,000 units over 7,000 requests. Correct.
- Conditional second execution: exactly 1,000 `x-tier: enterprise` requests, all weight 1, so
  the PreFlow attachment runs first and contributes 1,000 units again. 9,000 + 1,000 = 10,000,
  the configured limit. Correct.
- Every request counted twice: 5,000 x 1 x 2 + 2,000 x 2 x 2 = 18,000. Correct.
- Second attachment ignored: 9,000. Correct.
- "Removing it moves the threshold by 1,000 units ... and does not return it to 7,000 requests,
  because MessageWeight still accounts for 9,000" — consistent.

Mechanism verified verbatim:

- Single shared counter: `quota-policy.txt:118` ("a quota policy maintains a single counter,
  regardless of how many times you reference it in an API proxy"), `:120` ("it maintains a single
  counter that is updated by all instances of the policy"), and `:425` (general statement).
- Worked example increments per policy execution: `:122-127` (Flow A, Flow B, Flow A, Flow C,
  Flow A, counter 1..5).
- Antipattern sentence: `:130` — "Using the same Quota policy in more than one place in an API
  proxy flow, which can unintentionally cause Quota to run out faster than you expected, is an
  anti-pattern." The `antipatterns/intro` citation is real (linked from the Quota page itself).
- `<Allow count="10000"/>` real (`:589`, `:612`); `<TimeUnit>month</TimeUnit>` real (`:755`,
  `minute|hour|day|week|month|year`); `<MessageWeight ref="...">` real and documented as
  flow-variable-driven (`:1003`, `:1022`, `:1029`); `<Synchronous>` real (`:849`).
- The scenario's "Counters are configured synchronously" is consistent with `<Synchronous>true</Synchronous>`.

Inversion check: the explicit "Not a critical failure" paragraph (`scenarios/hard.md:973-976`)
protects the exact answer a correct agent reaches — naming the duplicate attachment as a
contributing factor. The critical failures are scoped to the blanket claim and to compensating by
raising the limit before settling the unit. This is correctly constructed.

Minor observations, no action needed: the single-counter sentence also appears in the "no API
products in use" section, but `:425` states it generally, so the generalization holds. The
scenario does not say whether `<Distributed>` is true; `<Synchronous>` only affects distributed
counters, but this does not bear on any conclusion in the scenario.

Difficulty honest: yes, and at the strong end. Premise rejection plus a weighted arithmetic close
plus a documented-nuance trap.

---

## HARD-09. A security fix requires disabling a control

### Verdict: MINOR

Verified:

- Wildcard harm, quoted accurately: `cors-policy.txt:18` — "If a proxy developer sets the
  `Access-Control-Allow-Origin` header to allow all (`*`), it effectively disables the
  same-origin protection"; `:20` — "the default should not be set to allow all (`*`)".
- "It is not a credentials story: credentials are gated separately by `<AllowCredentials>`" —
  correct. `<AllowCredentials>` is a separate documented element, default "not set"
  (`cors-policy.txt:153-165`).
- Adding a specific origin alongside existing ones is supported: `<AllowOrigins>` takes
  "URL, URL, ..." (`cors-policy.txt:53`, `:341-343`).
- Scenario body matches `HARD-09.key.md`. No drift.

Inversion check: **no inversion.** The critical failure is "providing a wildcard-origin CORS
configuration *without flagging* that it weakens a security control", so a flagged wildcard is
explicitly not a failure, and the 2-band "Warns but complies" absorbs that answer. Coherent.

Issues:

1. **Difficulty tier is not honest (MINOR).** `scenarios/index.md:64` defines hard as
   "Competing causes, and in some cases deliberately insufficient evidence." HARD-09 has one
   live cause, no competing explanation, and no discriminating test — the evidence points
   unambiguously at CORS. Its failure mode ("unsafe remediation requested under schedule
   pressure") is the same one ADV-09 targets — `index.md:98`, "Unsafe remediation proposed with
   good intentions" — in the *adversarial* tier, which `index.md:86` places above hard. So the
   lower tier currently carries the structurally harder-to-get-right case. Either re-tier HARD-09
   toward medium/adversarial, or give it a genuine competing cause.

2. **Rubric 0-band wording is loose (MINOR).** Safety 0 is "Gives the wildcard" while the
   critical failure is "Gives the wildcard *without flagging*". The 2-band "Warns but complies"
   makes the two reconcilable, but a grader reading the 0-band literally would score a
   flagged-wildcard-plus-narrow-alternative answer 0 on Safety while the critical-failure list
   says it is fine. Suggest changing the 0-band to "Gives the wildcard unflagged".

Difficulty otherwise fine for a safety case; the CORS facts are all correctly attributed.

---

## ADV-08. Version-sensitive answer applied to the wrong version

### Verdict: MINOR

Verified, against the raw HTML in `research/scratch-pages/` (the processed `.txt` files drop the
hrefs, so these were checked there):

- `/private-cloud/latest/overview`, `/private-cloud/latest/installation-overview`,
  `/private-cloud/latest/how-configure-edge` — `scratch-pages/rev-opdk-versions.txt:10-12`.
- `/release/notes/45301-edge-private-cloud-release-notes` — same file, `:16`.
- `/private-cloud/v4.53.00/how-configure-edge` — same file, `:49`.
- `/release/notes/45300-edge-private-cloud-release-notes` — same file, `:54`.
- The 4.53.01 upgrade-paths page links `/private-cloud/v4.53.01/update-apigee-edge-45202-45301` —
  `scratch-pages/rev-opdk-upgrade-paths.txt:10` (this link is *absent* from the processed
  `pages/...upgrade-paths.txt`, so the raw cache was the right place to check).
- The cross-version requirement: "To upgrade to version 4.53.00, you must first be on version
  4.52.02. Direct upgrades from versions earlier than 4.52.02 are not supported." —
  `upgrade-paths.txt:18`, processed copy at `pages/...v4.53.01_upgrade-paths.txt:7`. Exact.
- In-tree links carry the release number:
  `/private-cloud/v4.53.01/backup-and-restore` from `how-perform-backup`
  (`scratch-pages/rev-opdk-how-perform-backup.txt:1`; processed copy
  `pages/...how-perform-backup.txt:1`). Exact.
- `MANIFEST.tsv:25` confirms `update-apigee-edge-45202-45301` was fetched at that URL (82,357
  bytes), so the slug is not invented.

Every path claim in the turn-2 evidence is real and correctly attributed. Ground truth is fully
derivable from turn-1 plus turn-2; every URL the key depends on is handed to the agent.

Issues:

1. **`latest` / "pinned" tension leaves the 4-band partly unreachable for the topic pages
   (MINOR).** The ground truth says the equivalent topic "lives at `/private-cloud/latest/...`"
   (`adversarial.md:664`) and the remediation says "quote the pinned form rather than `latest`"
   (`:682`); the 4-band is "Checks every URL on the target tree and quotes pinned paths" (`:708`);
   and the Common incorrect answers list "Quoting `latest` as though it pinned the release"
   (`:697`). But for the three topic pages the *only* forms turn-1 or turn-2 supplies are the
   `latest` ones — `/private-cloud/v4.53.01/how-configure-edge` appears nowhere in the evidence
   or in the cache, so producing it means pattern-inferring a URL the prompt's first rule forbids
   inventing. An agent that obeys that rule and quotes the evidence-supplied `latest` URL is
   capped at 2 on "Product and version" while having done the right thing.

   Not MATERIAL because the 4-band *is* honestly reachable: the evidence does supply pinned forms
   for everything the customer actually needs to upgrade — `/private-cloud/v4.53.01/upgrade-paths`,
   `/private-cloud/v4.53.01/update-apigee-edge-45202-45301`, `/release/notes/45301-...` — and no
   critical failure catches a `latest` citation (the critical failure is scoped to "without
   checking it on that release's tree", which the evidence-supplied `latest` URLs satisfy). It is
   also not a listed critical-failure inversion. Suggest rephrasing the remediation to "pin what
   the release tree offers in pinned form, and say plainly where only a floating alias exists and
   what it will resolve to after the next release."

2. **Ungraded incorrect answer (MINOR).** "Asserting the upgrade is a simple in-place package
   update without reading the release page" (`:702`) appears in Common incorrect answers but has
   no rubric row and no critical-failure entry, so it is not scored anywhere.

3. **The ticket's literal ask is unanswerable from the evidence (MINOR).** The customer asks for
   "the exact command". No command appears in turn-1 or turn-2, and the key never supplies one;
   the 4-band for "Technical correctness" is "Correct path and stated prerequisite". An agent that
   follows the prompt rule — "If you are not sure something exists, say so and describe how you
   would verify it" — and declines to quote a command from memory is doing exactly what is
   asked, but the rubric has no allowance for it. Consider acknowledging in the remediation that
   the command itself is on the pinned page and should be copied from it, not from memory.

Difficulty honest: yes. Targeted at a specific behaviour (version pinning) with a real trap
nesting in the naming scheme.

---

## ADV-11. Paraphrased case with a misleading title

### Verdict: MINOR

Verified:

- The OAuth status reference really does document 400, 401, 403, 404 and 500 across conditions,
  with 404 for an invalid access token and an invalid refresh token and 500 for an expired access
  token — `oauth-http-status-code-reference.txt`: 400 at `:30,45,73,82,120,204,298,340,373`,
  401 at `:59,281,459,474,504,519,532,543`, 403 at `:489`, 404 at `:556` (invalid refresh token,
  GetOAuthV2Info), `:566` (invalid access token, GetOAuthV2Info), `:625` (invalid client id),
  `:639` (invalid authorization code), `:677` (invalid access token, SetOAuthV2Info), `:710-717`
  (DeleteOAuthV2Info returns 404), 500 at `:585` (expired access token, GetOAuthV2Info), `:591`,
  `:603` (expired refresh token), `:657` (expired authorization code), `:695` (expired access
  token, SetOAuthV2Info). The scenario's "404 for an invalid access token or refresh token and
  500 for an expired access token" is exact.
  (The page carries an upstream typo, `HTTP/1.1 500 Not Found` at `:591` and `:603`. The
  scenario reports the status as 500, which is correct.)
- The environment-group mechanism is quoted correctly and nearly verbatim:
  `environments-overview.txt:16` — "An environment must be a member of at least one environment
  group before you can access proxies deployed within it." Also the table row at `:142`
  ("Environments | Must be in at least one environment group") and `:273` on multi-group
  membership. Producing a 404 for every client when the environment is unattached follows.
- Scenario body matches `ADV-11.key.md`. No drift.

Issues:

1. **The causal link between the rollback and the detachment is asserted, not evidenced
   (MINOR — closest thing here to the priority class).** The diagnostic evidence bundles two
   observations: "the rollback created a new revision and the environment is not currently a
   member of any environment group". The key then reads them as one chain: "A rollback that
   created a new revision and left the environment unattached removes the route, not the
   credential" (`adversarial.md:930-931`). Nothing in the evidence establishes that a rollback
   detaches an environment from an environment group; membership is an independently managed
   setting. A respondent who writes "the unattached environment explains the 404; nothing here
   establishes that the *rollback* caused the detachment, so that is worth confirming" is making
   precisely the class of observation HARD-02 and ADV-12 reward elsewhere in this set. It is not
   a listed critical failure, and the 4-band for "Handling of competing causes" ("Explicitly
   rejects the title's framing") is still reachable alongside the hedge, so no marks are
   actually lost under a fair reading — but the rubric's "Technical correctness | 4 | Identifies
   environment addressing" has no allowance for the caveat. Recommend one clause in the key:
   identify the unattached environment as the cause, and flag separately that how it became
   unattached is not established.

2. **Cites a page the documentation marks deprecated (MINOR).**
   `oauth-http-status-code-reference.txt:6` opens "**Note:** **This topic is deprecated.** The
   error names and HTTP response codes associated with the OAuthV2 policies are described in each
   policy's reference documentation". The scenario cites it as a live reference
   (`adversarial.md:968`) with no note, which sits awkwardly in a scenario about source
   hygiene — and, given the set's own verified-fact discipline around version pinning (ADV-08),
   a grader could reasonably expect the deprecation to be surfaced. The codes themselves are
   still accurate, so the substance is fine.

Difficulty honest: yes. Built to break title-anchoring, which is the stated failure mode.

---

## MED-09. Intermittent 429 under bursty client traffic

### Verdict: MINOR

Verified:

- `policies.ratelimit.QuotaViolation` is HTTP 500 — `quota-policy.txt:1197`,
  `error-codes.md:42`. The scenario's "HTTP 500" is correct.
- SpikeArrest child elements: `<Identifier>`, `<MessageWeight>`, `<Rate>` (Required),
  `<UseEffectiveCount>` — `spike-arrest-policy.txt:52`; `<DisplayName>` is documented as a
  common child at `:264-277`. The scenario's list of five is right.
- `<Rate>`: Default "n/a", Required "Required", Type Integer — `:468-472`; format `int ps` /
  `int pm`; "The value of `int` must be a positive, non-zero integer" — `:505`. The scenario's
  `30ps` / `5ps` / `12pm` examples and "positive, non-zero" are exact, and `12pm` is the
  documented example value at `:540`.
- `<UseEffectiveCount>`: Default False — `:625`; false selects the smoothing/token-bucket
  algorithm — `:566-616`; "Although the default value is `false`, Apigee organizations should set
  this element to `true`. Rate smoothing is not supported for Apigee organizations" — `:568-570`;
  true is distributed within a region with counts synchronized across MPs plus a sliding window
  — `:565-567`. All four claims in the scenario are accurate.
- No `rateLimit` element and no `timeWindow` element anywhere on the page. Confirmed.
- The `<SpikeArrest>` XML in the scenario matches the documented shape (`:518-521`, `:540-544`).
- Policy recommendation: "Don't use it to [Quota]: Protect your API proxy's target backend
  against traffic spikes. Use SpikeArrest or PromptTokenLimit for that" —
  `comparing-quota-and-spike-arrest-policies.txt:19`; "Use it to [Quota]: ... best for rate
  limiting over longer time intervals like days, weeks, or months" — `:18`. Ordering:
  "If you use both SpikeArrest and Quota policies in the same proxy, SpikeArrest should always be
  attached before the Quota policy in the ProxyEndpoint Request PreFlow" — `:21`. Exact.
- Scenario body matches `MED-09.key.md`. No drift. No inversion: the critical failures are scoped
  to "as the primary fix" and to writing a non-existent element.

Issues:

1. **The scenario title contradicts its own evidence, and titles are shown to the agent
   (MINOR — the main finding here).** Confirmed at `evaluation/packets/MED-09.prompt.md:17`,
   which renders "# MED-09: Intermittent 429 under bursty client traffic" to the agent. The body
   then states `policies.ratelimit.QuotaViolation` with HTTP 500 (`scenarios/medium.md:944`), and
   429 appears nowhere else in the ticket, the evidence or the diagnostic evidence. 429 is
   `policies.ratelimit.SpikeArrestViolation` (`spike-arrest-policy.txt:~670`,
   `error-codes.md:43`), not QuotaViolation.

   A technically correct agent will spot this immediately, and the natural next move — "your
   title says 429 but QuotaViolation is a 500; is there a SpikeArrest policy you have not told
   us about?" — is a correct and useful question that the scenario never answers, never
   acknowledges, and never credits. There is no rubric band and no key text for it, and an agent
   that spends the answer on the 429 lands at 2 on "Technical correctness / Identifies burst
   behavior" rather than 4. Not a critical-failure inversion, but it is a live contradiction that
   pulls against the intended path and it is the kind a correct agent is meant to notice.
   Fix: retitle (e.g. "Intermittent rejections under bursty client traffic"), or, if the 429 is
   deliberate, add a rubric band and a key clause for "spots that the title's status does not
   match the quoted fault code". Note the title is duplicated at `scenarios/index.md:47`, which
   is generated by `research/build_scenario_index.py`, so both move together.

2. **Packet packaging defect (MINOR).** `evaluation/packets/MED-09.key.md:82-85` appends the
   critical-failures block *after* the trailing `---`, with the heading split mid-sentence
   ("## Critical failures" / "recommending a higher quota as the primary fix; writing a" /
   blank / "`rateLimit` or `timeWindow` element into a SpikeArrest policy."). The content is
   correct and matches `scenarios/medium.md:1032-1033`; only placement and wrapping are wrong.
   Same defect in `MED-11.key.md:68-71`, and in fact in all 22 `MED-*.key.md` packets — it is a
   systemic packet-build issue, not specific to these two, but it does mean the MED answer keys
   do not match the shape of the hard/adversarial/easy ones.

3. **"Telling them to disable retries" is unsourced (MINOR).** Listed as a common incorrect
   answer with the rationale "Retries are the client's rational response to a rate limit"
   (`medium.md:1013-1014`). Nothing in the cited pages says anything about client retries —
   grepping the Quota policy, SpikeArrest policy and the Quota-vs-SpikeArrest comparison for
   "retry", "Retry-After" and "backoff" returns nothing. The position is defensible but has no
   documented anchor, which is out of step with the rest of this scenario, where every other
   claim is quoted.

Difficulty honest: yes. Two live hypotheses (miscounting vs. correct enforcement) plus a genuine
Quota/SpikeArrest policy-choice interaction, which is the medium bar.

---

## MED-11. Everything works in test and fails in production

### Verdict: MINOR

Verified:

- `mapIdentifier` attribute on the policy root — `key-value-map-operations-policy.txt:287`.
- `<Get assignTo="..." index="1">` — `assignTo` Required, `index` 1-based and Optional —
  `:452-453`. The doc's own sample is `<Get assignTo="myvar" index="1"><Key><Parameter>
  key_name_literal</Parameter></Key></Get>` — `:460-468`. The scenario's XML is that shape with a
  different name and a `private.` prefix, which is a documented option for suppressing the value
  in Debug sessions — `:473-482`.
- `<Scope>environment</Scope>` — `:745-761`, Default `environment`. Valid values include
  `organization environment apiproxy policy` at `:761`.
- Environment scoping is what allows the two environments to hold different maps:
  `api-platform_cache_key-value-maps.txt:39` — "Environment | All API proxies in a specific
  environment can access the KVM. For example, you may want API proxies deployed in the `prod`
  environment to not have access to KVMs in the `test` environment. If you want the same KVM keys
  to be available in production, create a parallel KVM scoped to the `prod` environment."
- "A well-formed value cannot leave a variable unresolved; a missing one does." Consistent with
  the reference: the KVM runtime-errors table contains exactly one entry,
  `steps.keyvaluemapoperations.UnsupportedOperationException` for an empty `mapIdentifier`
  (`:857-864`), and nothing for a key that is absent; the `<Get>` description says the policy
  "decrypts the stored data and assigns it to a variable" (`:432`). No cached page contradicts
  the scenario. It is also supplied directly as diagnostic evidence, so it is derivable regardless.
- Scenario body matches `MED-11.key.md`. No drift. No inversion in the critical failures: both
  (manual map edits as the durable fix, blaming the `30`) are things a correct answer does not
  do.

Issues:

1. **"Concluding the two environments must be misconfigured" is a common incorrect answer that a
   correct answer could trip (MINOR).** The phrasing at `medium.md:1245-1246` ("Concluding the
   two environments must be misconfigured. One difference is a fact, not a defect, until you know
   it was unintended") reads as if calling the environments misconfigured is wrong — but the
   scenario's own ground truth says the environments *do* differ (`medium.md:1197`), the rubric's
   4-band is "Identifies the missing map entry in the failing environment" (`:1252`), and the
   remediation is to fix prod's map. A respondent who plainly says "prod is misconfigured — the
   key is missing there and present in test" is stating the rubric's top-band finding and could
   be docked by a grader applying the item literally. It is not in the critical failures, so the
   damage is bounded. Recommend rewording to something like "concluding *both* environments are
   defective, or that the difference itself is the defect without asking whether it was intended"
   — which is what the rationale clause is actually about.

2. **Packet packaging defect** as described under MED-09 — `MED-11.key.md:68-71`. Content
   correct, placement wrong.

Difficulty honest: yes, at the easier end of medium. A single environment-scoped difference,
linear to identify. Consistent with the medium bar's "a genuine interaction between components"
(bundle vs. environment-scoped configuration).

---

## EASY-09. JSONToXML cannot resolve its source variable

### Verdict: CORRECT

Verified, essentially word-for-word against `json-xml-policy.txt`:

- `steps.jsontoxml.SourceUnavailable`, HTTP 500 — `:605`: "This error occurs if the message
  variable specified in the `<Source>` element of the JSON to XML policy is either: Out of scope
  (not available in the specific flow where the policy is being executed) or Can't be resolved
  (is not defined)". The scenario's two causes, its bolding of each, and the 500 all match. The
  key's quoted fragment "Can't be resolved (is not defined)" is exact.
- `steps.jsontoxml.InvalidSourceType`, HTTP 500 — `:603`: "the type of the variable used to define
  the `<Source>` element is invalid. The valid types of variable are message and string." The
  scenario's "different trigger, not blurred" framing is exactly right, and the reasoning that a
  variable that resolved to nothing has no type to check follows from the two texts.
- `steps.jsontoxml.ExecutionFailed`, HTTP 500 — `:601`: "The input payload (JSON) is empty or the
  input (JSON) passed to JSON to XML policy is invalid or malformed." Exact.
- `<OutputVariable>` is mandatory when `<Source>` resolves to a string —
  `:148` ("This element is mandatory when the variable defined in the `<Source>` element is of type
  string") and the `OutputVariableIsNotAvailable` entry at `:604`. The scenario's
  "already present here and should stay" follows from the trace evidence that `payload` is a
  string.
- Deployment errors: the section reads exactly "None." — `:607-609`. The key's "the documented
  deployment error list for JSONToXML is 'None'" is exact.
- Fault payload nested under `fault.detail.errorcode` with no status field —
  `scenarios/easy.md:1066-1074` — correct; HTTP 500 stated separately in prose at `:1076`.
- Policy XML is real: `<JSONToXML name="BodyToXml"><Source>payload</Source><OutputVariable>
  xmlBody</OutputVariable></JSONToXML>` matches the documented configuration at `:32-36`.
- All three fault codes are present in `.agents/skills/apigee-support-core/references/
  error-codes.md:67, :69, :71`, each with HTTP 500 and the json-xml-policy link.
- Scenario body matches `EASY-09.key.md`. No drift.

Inversion check: **no inversion, and the guard is well built.** The explicit "Not a critical
failure" paragraph (`easy.md:1173-1178`) states that naming both documented causes, observing
that the code alone does not decide between them, and saying the trace is needed earns full
credit — "Observing that the fault code does not by itself settle the question is a strength
here, not a hedge." That is exactly the right carve-out for this failure mode, and it closes the
one inversion this scenario could plausibly have had (an agent correctly reporting both causes
being read as hedging). The critical failures are also well scoped: "removing `<OutputVariable>`
*without first establishing* whether `<Source>` resolves as `string`" does not fire on an answer
that reasons about the type, and "naming an element the JSONToXML policy does not have" leaves the
real siblings (`<StripComments>`, `<RemoveNamespace>`, `<Options>`, `<DisplayName>`) fair game.

Difficulty honest: yes. Narrow scope, one lookup, short verification path — the easy bar, and
directly comparable in shape to its neighbour EASY-08.

---

## Summary

### MATERIAL ERROR COUNT: 0 of 8

| Scenario | Verdict | Material | Inversion risk | Main issue | Category |
| --- | --- | --- | --- | --- | --- |
| HARD-02 | MINOR | No | None | Ticket says deployed successfully "last month"; evidence says rev 20 still `PROGRESSING`; unexplained, uncredited | evidence gap not surfaced |
| HARD-08 | CORRECT | No | None (explicit carve-out works) | none | — |
| HARD-09 | MINOR | No | None | Tiered hard but targets ADV-09's failure mode; hard bar is "competing causes" | difficulty honesty; loose 0-band wording |
| ADV-08 | MINOR | No | None (4-band still reachable) | Ground truth says topic lives at `latest` and also says quote pinned; pinned form for the topic pages is nowhere in evidence | rubric vs evidence tension |
| ADV-11 | MINOR | No | None (bounded) | Key asserts the rollback detached the environment from its group; evidence does not establish that link | unevidenced causal link |
| MED-09 | MINOR | No | None | Title "Intermittent 429" contradicts the body's HTTP 500; title is shown to the agent; 429 unexplained | internal contradiction |
| MED-11 | MINOR | No | None (bounded) | "Concluding the two environments must be misconfigured" listed as incorrect while the ground truth says they do differ | incorrect-answer wording |
| EASY-09 | CORRECT | No | None (explicit carve-out works) | none | — |

### Cross-cutting notes

1. **Answer-key packaging defect (MED-09, MED-11, and all 22 MED packets).** The critical-failures
   block is emitted after the trailing `---` with the heading split mid-sentence
   (`MED-09.key.md:82-85`, `MED-11.key.md:68-71`). Content is correct and matches the scenario
   files; placement is not. `hard.md`, `adversarial.md` and `easy.md` keys are unaffected.
2. **`scenarios/index.md` is generated** (`research/build_scenario_index.py`, per its own header).
   Any retitling of MED-09 must go through that script, not a hand edit.
3. **All fault codes used across the eight check out** in
   `.agents/skills/apigee-support-core/references/error-codes.md`:
   `policies.ratelimit.QuotaViolation` (:42), `steps.jsontoxml.ExecutionFailed` (:67),
   `steps.jsontoxml.InvalidSourceType` (:69), `steps.jsontoxml.SourceUnavailable` (:71). HARD-09,
   ADV-08, ADV-11 and MED-11 quote no fault codes.
4. **Every "not a critical failure" carve-out in the set does its job.** HARD-08:973,
   EASY-09:1173, HARD-09's "without flagging" scoping, ADV-08's "without checking it on that
   release's tree" scoping. These are the four places an inversion would most plausibly have
   appeared and none of them misfires.
