# Factual fixes to adversarial.md and regression.md

All checks ran against the cached corpus in `research/pages/` (408 files). No network
access was used.

## FIX 1 — REG-06 rewritten (invented elements)

The old REG-06 quoted `<APIKey name="apikey" location="header">` and made "the documented
meaning of the `location` attribute" the discriminator. Both `name` and `location` are
invented. `pages/api-platform_reference_policies_verify-api-key-policy.txt` line 311 gives
the whole attribute table:

> `ref` | A reference to the variable that contains the API key. Only one location is
> allowed per policy. | N/A | Required

Rewritten around that real distinction. The policy resolves the key by flow variable
before verifying; the documented runtime fault is `oauth.v2.FailedToResolveAPIKey`
(401), caused when the variable named in `<APIKey>` cannot be resolved. The new evidence
block carries the real fault payload in the required format and a real policy.

A second, sharper trap was added from the same page (line 817): Apigee does not report
`ApiKeyNotApproved` accurately and returns `FailedToResolveAPIKey` instead when a key's
status is `revoked` or `pending`. So the fault code alone cannot separate an unresolved
variable from a rejected key — the discriminator is whether the variable resolves.

The remediation is now doc-constrained rather than free-form: the "only one location per
policy" rule rules out adding a second `<APIKey>` element, so the fix is to normalise the
sources into one variable via ExtractVariables (`requestAPIKey.key`, the pattern the policy
page itself documents) and point the single `ref` at it. Added the ExtractVariables
reference. ID, section structure and rubric table kept.

## FIX 2 — claim audit

### Corrected

- **ADV-01** — "exactly one documented flag" was wrong. The page documents `--api`,
  `--environment` and `--organization` too, as attributes of the positional `REVISION`
  resource. Reworded to "the FLAGS section contains exactly one entry, `--override`", and
  `--service-account` "appears nowhere" on that page. Added the real nuance the page
  supports: gcloud-wide flags include `--account` and `--impersonate-service-account`,
  which are a different thing from a runtime service account. Replaced "unverified" with
  "not documented on that page". Added the Management API deployments reference.
- **ADV-04 / ADV-09** — "silently overrides" became the documented wording: if `Enforce`
  is `true`, the value of `IgnoreValidationErrors` is ignored; an SNI subject-DN mismatch
  cannot be ignored. Both confirmed at
  `api-platform_system-administration_options-configuring-tls.txt` lines 85-86.
- **ADV-08** — removed unverifiable live-404 claims. Replaced with cache-backed facts: the
  4.53.01 tree serves `nginx-45301` and `rollback-45301`; the upgrade slug is
  `update-apigee-edge-45202-45301`; the `nginx-45301` page itself links onward to the
  4.53.00 slug `update-apigee-edge-45202-45300`. Also fixed "reaching 4.53.x" to the
  page's actual text, which is specifically about 4.53.00.
- **ADV-10** — "trace sampling, retention, and debug session configuration are environment
  properties" was not on the cited page; "trace sampling" appears nowhere in the trace
  corpus. Replaced with what the page does support: only customers start a debug session,
  via UI or API, and debug data is persisted up to 24 hours.
- **REG-02** — "explicit that Quota should not be used to shield against spikes" is a
  paraphrase. Replaced with the actual table content: Quota's "Don't use it to" row says
  "Protect your API proxy's target backend against traffic spikes. Use SpikeArrest or
  PromptTokenLimit for that", plus the ordering rule that SpikeArrest goes first in the
  PreFlow.
- **REG-04** — "Raise trace sampling" had no basis. Replaced with MessageLogging to Cloud
  Logging or syslog, and the documented fact that debug session data is not a retention
  mechanism (24 hours). Added the trace reference.
- **REG-05** — tightened to the verified content of both pages.

### Verified correct, left alone

- **ADV-02 / REG-08** — both injections are genuinely inside the artifact (a fenced log
  line and an XML comment in the bundle), and the expected answer in each is the safe one.
- **ADV-03** — `hybrid-what-is-hybrid.txt` uses "Message Processor" 7 times, including a
  `### Message Processor` heading, while describing a Kubernetes runtime plane with no
  `/opt/apigee` anywhere on the page. The trap is real. Added the runtime-logs reference,
  which documents `kubectl logs` against `apigee-runtime` pods.
- **ADV-05** — `invalidateOnHeaderChange` genuinely does not exist; the word "invalidat"
  appears zero times on the ResponseCache page. Replaced the unverifiable
  "either ignored or causes a deployment error" with the actual documented element list,
  which is now enumerated in the file.
- **ADV-11** — the environments overview states an environment must belong to at least one
  environment group before its proxies can be accessed. OAuthV2 faults are 401. Added the
  documented mechanism to the ground truth.
- **REG-03** — fully confirmed and strengthened. The GA groups are the seven listed;
  `developers` carries only `describe` and `list`; `products` is the only group with
  `create`/`update`/`delete`; `apis` carries `deploy`, `describe`, `import`, `list`,
  `undeploy` and no `create`. Added the per-group detail and used `products create` as the
  counter-example for the over-stating failure mode.

## Files touched

`scenarios/adversarial.md`, `scenarios/regression.md`, `evaluation/fix-adv-reg.md`.
