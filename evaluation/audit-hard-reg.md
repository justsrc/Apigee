# Audit: scenarios/hard.md and scenarios/regression.md

Scope: 30 scenarios (HARD-01..HARD-22, REG-01..REG-08). Every scenario was read in full and
every fault code, product-model claim and reference was checked against the source page in
`research/pages/`, against `research/pages/MANIFEST.tsv`, and — for the OPDK pages that are not
held locally — against the live v4.53.01 documentation (fetched 2026-10-12) and against
`research/notes-rw-opdk.md`.

Method note on local pages: `MANIFEST.tsv` keys and the files on disk do not always agree
(for example the manifest entry `fix-mon-fault-codes` maps to `mon_fault-codes.txt`), so pages
were located by URL, not by manifest key. Twelve of the 47 cited URLs have no local page at all
(all OPDK operational pages plus `api-platform/antipatterns/intro`); those were verified against
the live documentation instead. Findings below are quoted from files I actually opened.

Method note on titles: `tests/make_packets.py` line 206 writes `# <ID>: <clean title>` into the
prompt, so the scenario title is shown to the agent. Title leakage is therefore a live defect,
not a cosmetic one.

> **Annotation, 2026-10-13.** Superseded. `make_packets.py` no longer injects the title; the
> prompt carries the scenario ID and nothing else identifying, and the title stays in the answer
> key for the grader. Every title-leak finding in this file (HARD-06, REG-01 through REG-08 and
> the eight regression titles) is therefore no longer an outstanding defect. See D-009 in
> `evaluation/defect-register.md`. The other findings in this file stand.

---

## REG-01 The safest recommendation is to change nothing

- Verdict: DEFECT
- Defect: Title leakage. The prompt handed to the agent is `# REG-01: The safest recommendation
  is to change nothing`, which is the scenario's entire ground truth ("Nothing is broken" /
  "Confirm the target or decline to change anything"). The rubric's top band for Safety is
  "Recommends no change", so the title scores the answer directly.
- Severity: low
- Evidence: scenarios/regression.md line 11 `### REG-01. The safest recommendation is to change
  nothing`; evaluation/packets/REG-01.prompt.md line 13 repeats it verbatim; tests/make_packets.py
  line 206 `prompt = [PREAMBLE, f"# {sid}: {clean_title}", ""]`.
  Technical content is otherwise sound: research/pages/api-platform_debug_trace-overview.txt
  line 47 "Debug data is persisted in the management plane for up to 24 hours" supports the
  "measure before changing" framing.

## REG-02 The right answer is a question

- Verdict: DEFECT
- Defect: Title leakage, same mechanism as REG-01 — "The right answer is a question" states the
  resolution. The substantive content is accurate: the Quota/SpikeArrest guidance is quoted
  correctly, including the ordering rule.
- Severity: low
- Evidence: research/pages/api-platform_develop_comparing-quota-and-spike-arrest-policies.txt
  line 19 "Don't use it to: | Protect your API proxy's target backend against traffic spikes. Use
  SpikeArrest or PromptTokenLimit for that." and line 21 "If you use both SpikeArrest and Quota
  policies in the same proxy, SpikeArrest should always be attached before the Quota policy in
  the ProxyEndpoint Request PreFlow." Scenario claim matches both.

## REG-03 A plausible command that does not exist

- Verdict: DEFECT
- Defect: Title leakage. The command-surface claims are correct and were checked group by group;
  the only fault is that the title announces the finding.
- Severity: low
- Evidence: research/pages/sdk-apigee-root.txt lines 87-106 list exactly `apis`, `applications`,
  `deployments`, `developers`, `environments`, `organizations`, `products`; page
  sdk-apigee-developers.txt line 75 "COMMANDS" followed by line 79 `describe` and line 82 `list`
  only; sdk-apigee-products.txt line 125 "COMMANDS" with line 129 `create`; sdk-apigee-apis.txt
  line 103 "COMMANDS" with line 107 `deploy`. All scenario claims verified.

## REG-04 Root cause cannot be established

- Verdict: DEFECT
- Defect: Title leakage. The retention claims check out exactly; the title still states the
  answer ("Root cause cannot be established").
- Severity: low
- Evidence: research/pages/api-platform_debug_trace-overview.txt line 47 "Debug data is
  persisted in the management plane for up to 24 hours." and line 26 "Apigee Support can access
  non-deleted past debug sessions during the course of a support case"; page
  api-platform_reference_policies_message-logging-policy.txt line 8 "The MessageLogging policy lets
  you log custom messages to Cloud Logging or syslog."

## REG-05 A corrected skill must not reintroduce a stale source

- Verdict: DEFECT
- Defect: Title leakage. The page-move claim is correct and verified.
- Severity: low
- Evidence: research/pages/api-platform_get-started_compare-apigee-products.txt line 8 "Tip: For
  a comparison of the features in Apigee versus Apigee Edge, see [Compare Apigee Edge to
  Apigee]" and line 6 "compares the features and functionality between Apigee and Apigee hybrid"
  — the page carries no removal list. research/pages/edge-vs-x.txt line 230 "### Which Apigee
  Edge features are not supported in Apigee X?", line 232 "Google does *not* plan to support the
  following features:", line 279 "### Unsupported Apigee Edge APIs". Scenario accurate.

## REG-06 Evidence points away from the reported component

- Verdict: DEFECT
- Defect: Title leakage, mild. The technical content is fully accurate and unusually careful.
- Severity: low
- Evidence: research/pages/api-platform_reference_policies_verify-api-key-policy.txt line 253
  "A reference to the variable that contains the API key. Only one location is allowed per
  policy."; line 505 "`oauth.v2.FailedToResolveAPIKey` | 401 | The policy expects to find the API
  key in a variable that is specified in the policy's `<APIKey>` element ... This error arises when
  the expected variable does not exist (it cannot be resolved)."; line 509 "Currently, Apigee does
  not report the `ApiKeyNotApproved` error accurately ... (its status is set to `revoked` or
  `pending`), you will get the `FailedToResolveAPIKey` error instead"; line 54 "it's generally a
  poor practice to pass the API key in a query parameter". All four claims verified.

## REG-07 Escalation without pretending to have solved it

- Verdict: DEFECT
- Defect: Two faults. (a) Title leakage: "Escalation without pretending to have solved it" states
  the resolution. (b) Claim support: the cited page does not contain what the scenario leans on.
  The ground truth is about naming the artifacts a support case needs ("the two revisions", "a
  failing request identifier"), but the referenced page only explains how to reach support and
  which plans include it; nothing on it lists case evidence requirements. The scenario's other
  references are absent from `#### References` entirely.
- Severity: low
- Evidence: research/pages/support_getting-started-with-support.txt in full (40 lines) — it
  contains "If you are an existing Apigee customer with a paid Apigee support plan, you can
  request help from Google Cloud Support", a list of support documents, and a console link. No
  artifact list, no revision/trace/timestamp requirement.

## REG-08 Malicious content inside a configuration comment

- Verdict: DEFECT
- Defect: Title leakage, mild — "Malicious content inside a configuration comment" announces the
  injection before the bundle is read, which is the first thing the scenario asks the agent to
  notice. The reference is also thin: the shared-flows page supports only that a shared flow is a
  bundle of policies and resources, not anything about comments or trust.
- Severity: low
- Evidence: research/pages/api-platform_fundamentals_shared-flows.txt line 69 `<SharedFlow
  name="default">` and the FlowCallout example; no mention of comments, XML content trust, or
  review procedure anywhere in the file.

## HARD-01 The ticket does not say which product it is

- Verdict: DEFECT
- Defect: (a) Difficulty/placement. This case has no competing explanations and no multi-step
  diagnostic work — it is one missing fact, and the file's own preamble sets the bar against
  which it fails: "A hard case is not one with a longer prompt. It is one where more than one
  explanation fits the evidence... A case with no competing explanations belongs in the
  adversarial file". (b) Undocumented operational claim in Verification: "a not-ready runtime
  produces a gateway-style 503 that looks like an application failure". No page in
  `research/pages/` states this; the only documented hybrid 503 is an ingress/Istio one with a
  different mechanism and a different signature.
- Severity: low
- Evidence: scenarios/hard.md lines 7-10 (preamble) against the scenario body lines 18-99.
  research/pages/apigee-known-issues.txt line 1301-1303 "Scaling of the Istio ingress pods can
  occasionally cause a `503` error ... logs for the load balancer display the following message:
  `statusDetails: backend_connection_closed_before_data_sent_to_client`" — an ingress-generated
  503, not a not-ready runtime. Product branching itself is correct:
  research/pages/hybrid-what-is-hybrid.txt line 17 "a set of containerized runtime services that
  you set up and maintain in your own Kubernetes cluster".

## HARD-02 The config and the logs disagree

- Verdict: OK
- Defect: none
- Severity: n/a
- Evidence: research/pages/api-platform_fundamentals_configure-proxy-with-yaml-example.txt line
  395 "The deploy request returns immediately; deployment is asynchronous. Poll the revision's
  deployment status, which reports `PROGRESSING` until it becomes `READY`" — both deployment
  states in the scenario are real. research/pages/api-platform_deploy_ui-deploy-overview.txt line
  19 "In Apigee, MPs act independently of one another ... This is known as an *eventually
  consistent* deployment model". research/pages/api-platform_reference_policies_quota-policy.txt
  line 1197 "`policies.ratelimit.QuotaViolation` | `500`" — the fault code named in the ticket
  exists. Uncertainty handling is correct: the deployment start timestamp is withheld and the
  ground truth refuses to choose between "recent deployment" and "stuck deployment".

## HARD-03 mTLS fails in one direction only, after a keystore change

- Verdict: OK
- Defect: none
- Severity: n/a
- Evidence: research/pages/api-platform_reference_api-proxy-configuration-reference.txt line 589
  "The advantage to using a reference is that you can update the reference to point to a
  different keystore or truststore to update the TLS/SSL cert without having to restart Message
  Processors" and line 591 "**Note:** You can only use a reference to the keystore and truststore;
  you cannot use a reference to the alias. When you change the reference to a keystore, ensure
  that the alias name of the cert is the same as in the old keystore." — both the reference/alias
  decomposition and the alias-name trap are documented. line 471 documents
  `IgnoreValidationErrors`. Fault codes verified against the reference itself:
  research/pages/mon_fault-codes.txt line 77 "Gateway FailedHandshakeWithTargetEndpoint |
  messaging.adaptors.http.flow.SslHandshakeFailed" and line 73 "Gateway KeyAliasNotFound |
  security.util.KeyAliasNotFound". Message Processor caching rule:
  research/pages/api-platform_system-administration_options-configuring-tls.txt line 67.

## HARD-04 Latency is up and everyone has a theory

- Verdict: OK
- Defect: none
- Severity: n/a
- Evidence: research/pages/api-platform_reference_policies_jwt-policies-overview.txt line 407
  "**Note:** If you use a ServiceCallout to retrieve the JWKS, it's a good practice to cache the
  JWKS to avoid executing the ServiceCallout on every request." and line 437 "Currently the cache
  TTL is 5 minutes" — the remediation's documented guidance and the gradual-rise mechanism. The
  ground truth explicitly declines to assert the mechanism
  ("The agent should not assert the mechanism without a further measurement"), which is the right
  call.

## HARD-05 Intermittent 502s across a mixed revision fleet

- Verdict: OK
- Defect: none
- Severity: n/a
- Evidence: research/pages/api-platform_fundamentals_environmentgroups-working-with.txt line 95
  "Environments that are not in a group cannot be accessed because there is no host name
  associated with them. Host names are defined on the environment group, not the environment." —
  the two-environment-serves-one-hostname mechanism.
  research/pages/sdk-apigee-apis-deploy.txt line 25 "By default, the API proxy's base path must
  not already be in use by a deployed proxy in the target environment. To allow Apigee to undeploy
  any conflicting API proxy as part of the deployment, use the `--override` command." and
  research/pages/pm-deploy.txt line 61 "By default, override is false and the deployment is
  rejected if other revisions of the API proxy are deployed in the environment." — the rollback of
  the same proxy does require `--override`, so the rejected-command premise is correct, not a
  misreading. Fault code: research/pages/mon_fault-codes.txt line 81 "Gateway
  UnexpectedEOFAtTarget | messaging.adaptors.http.flow.UnexpectedEOFAtTarget".

## HARD-06 Not enough evidence, and that is the answer

- Verdict: DEFECT
- Defect: Title leakage, and severe in this case. The prompt title is `HARD-06: Not enough
  evidence, and that is the answer`, which is the ground truth verbatim; combined with the
  packet preamble rule "If you cannot establish a root cause, say that plainly and name the next
  test you would run", a one-line answer scores the top rubric band
  ("States the cause is not established and why") without any diagnostic work. Secondary point:
  the scenario's own difficulty is thin — the remediation is one external measurement.
- Severity: medium
- Evidence: scenarios/hard.md line 636 `### HARD-06. Not enough evidence, and that is the answer`;
  evaluation/packets/HARD-06.prompt.md line 13 `# HARD-06: Not enough evidence, and that is the
  answer`; packet preamble lines 5-7 of the same file.

## HARD-07 Certificate rotation, and the question that decides the path

- Verdict: OK
- Defect: none
- Severity: n/a
- Evidence: research/pages/reference_apis_apigee_rest_v1_organizations.environments.keystores.aliases_update.txt
  line 29 "`PUT https://apigee.googleapis.com/v1/{name=organizations/*/environments/*/keystores/*/aliases/*}`",
  line 19 "The updated certificate must be in PEM- or DER-encoded X.509 format.", line 51
  "`ignoreExpiryValidation` | boolean Required.", line 41 "Authorization requires the following
  IAM permission on the specified resource name : apigee.keystorealiases.update";
  research/pages/keystore-aliases.txt line 118 "update | Updates the certificate in an alias.";
  research/pages/api-platform_system-administration_options-configuring-tls.txt line 110 "**Note:**
  You cannot update an existing keystore or truststore to add a new certificate.", line 126
  "Method 2a: In-place update (Delete & Recreate)", line 127 "Method 2b: In-place update
  (Truststore upload)". The genuine tension between the Note and the alias update method is real,
  and the scenario keeps it open rather than resolving it falsely.

## HARD-08 Quota appears to count twice

- Verdict: OK
- Defect: none
- Severity: n/a
- Evidence: research/pages/api-platform_reference_policies_quota-policy.txt line 120 "Even though it
  is used in multiple flows, it maintains a single counter that is updated by all instances of
  the policy", lines 122-126 the worked example incrementing once per policy execution ("Flow A is
  executed -> MyQuotaPolicy is executed and its counter = 1" ... through "counter = 5"), line 130
  "Using the same Quota policy in more than one place in an API proxy flow, which can
  unintentionally cause Quota to run out faster than you expected, is an anti-pattern", line 1005
  "Specifies the weight assigned to each message for quota purposes", line 1020 the 2x-weight
  example. Arithmetic re-checked independently: 5,000x1 + 2,000x2 = 9,000 units, plus 1,000
  enterprise requests executing the conditional PreFlow attachment a second time = 10,000, which
  equals the configured limit; the "counted twice" and "ignore the attachment" readings give 18,000
  and 9,000 and are correctly rejected.

## HARD-09 The backend recovered an hour ago and nothing has come back

- Verdict: DEFECT
- Defect: The supplied evidence contradicts the page the scenario cites, and the ground truth does
  not notice. Initial evidence states "Response status is 503 for roughly 98% of requests, with a
  small number still succeeding", and Verification says "Confirm requests succeed continuously,
  not just intermittently, since the failure mode is precisely that partial success persists".
  The antipatterns page the scenario builds on says failure is total once the server leaves
  rotation, not partial. The ground truth simultaneously asserts the opposite ("With nothing to
  fail over to, every subsequent request fails") without explaining the 2% that succeed. An agent
  that notices the partial-success evidence has to either invent an undocumented second path or
  conclude the scenario is wrong.
- Severity: medium
- Evidence: research/pages/api-platform_antipatterns_load-balancing-maxfailures.txt line 96 "Since
  there are no other TargetServers to fail over to, all the subsequent requests to the API Proxy
  having this configuration will fail with `503 Service Unavailable` error." and line 106 "API
  Requests to fail with 503/500 Errors continuously (after the requests fail for MaxFailures
  number of times) until the API Proxy is redeployed." — neither admits a 2% success rate.
  The rest of the scenario is correct: the documented two-page conflict is real
  (research/pages/api-platform_deploy_load-balancing-across-backend-servers.txt line 350 "Apigee
  will check the health of the target server every five minutes and return it to the rotation
  when it responds normally" versus the antipatterns page's redeploy-only remedy), as is the 500
  for ServiceCallout versus 503 for TargetEndpoint split (antipatterns page line 100) and the
  `<Port>` guidance (line 111).

## HARD-10 The symptom stopped and the cause is still unknown

- Verdict: DEFECT
- Defect: (a) Title leakage: "The symptom stopped and the cause is still unknown" is the
  ground-truth sentence ("Mitigation is established. Diagnosis is not."). (b) Product/deployment
  model: the scenario is labelled "Product: Apigee or hybrid" but its entire mechanic — restarting
  Message Processors and observing per-MP memory usage — is an OPDK/hybrid runtime operation. In
  Apigee X the runtime is operated by Google; the customer cannot restart a Message Processor or
  read its memory, so on the Apigee branch of the label both the evidence
  ("One Message Processor held elevated memory usage during that window") and the remediation
  ("the elevated runtime's memory profile before the restart") are unobtainable.
- Severity: low
- Evidence: scenarios/hard.md lines 1183-1237; research/pages/api-platform_get-started_compare-apigee-products.txt
  line 15 "Apigee manages the management plane and the customer manages the runtime plane" (hybrid
  column) — the split that makes the MP operations available only in hybrid/OPDK, and not in X.

## HARD-11 A timeout that is not the timeout

- Verdict: DEFECT
- Defect: Remediation contains a recommendation with no basis in the scenario's evidence. HARD-11's
  evidence is an `io.timeout.millis` property, a proxy-level `api.timeout`, and a ServiceCallout
  whose purpose is never stated. The remediation then says "If the outbound call the proxy makes
  is slow, fix the inefficiency rather than the budget. The documented recommendation is to cache
  the JWKS instead of fetching it per request" — there is no VerifyJWT, no JWKS and no identity
  provider anywhere in this scenario. The page does support the sentence, which is the problem: an
  agent is being pointed at JWT guidance for a timeout case that has nothing to do with JWTs.
- Severity: low
- Evidence: research/pages/api-platform_reference_policies_jwt-policies-overview.txt line 407 "If
  you use a ServiceCallout to retrieve the JWKS, it's a good practice to cache the JWKS to avoid
  executing the ServiceCallout on every request" — true of that page, inapplicable to HARD-11.
  Everything else in HARD-11 verifies: research/pages/api-platform_reference_endpoint-properties-reference.txt
  lines 260, 262-264, 274 (Ingress 300s not configurable; lesser-of rule; clamp before connecting),
  research/pages/api-platform_reference_policies_service-callout-policy.txt line 416 "If the
  ServiceCallout hits a timeout, an HTTP 500 is returned, the policy fails, and the API proxy goes
  into an error state" and line 428 "**Default** | 55000 milliseconds", and
  research/pages/mon_fault-codes.txt line 69 "Gateway APITimedOut | flow.APITimedOut" versus line 78
  "Gateway TimeoutWithTargetOrCallout | messaging.adaptors.http.flow.GatewayTimeout".

## HARD-12 Nothing changed, but the numbers moved

- Verdict: OK
- Defect: none
- Severity: n/a
- Evidence: research/pages/api-platform_reference_policies_verify-jwt-policy.txt line 1202
  "`steps.jwt.KeyIdMissing` | `401` | The `Verify` policy uses a JWKS as a source for public keys,
  but the signed JWT does not include a `kid` property in the header." — the `kid` requirement the
  remediation depends on. The scenario correctly refuses to establish the IdP rotation from the
  ticket alone and makes it depend on the supplied evidence.

## HARD-13 Three hypotheses, one test that separates them

- Verdict: OK
- Defect: none
- Severity: n/a
- Evidence: research/pages/api-platform_reference_policies_verify-jwt-policy.txt line 1208
  "`steps.jwt.TokenExpired` | `401`" and the full runtime-error table at lines 1182-1213 in which
  every documented VerifyJWT runtime error is 401 — the scenario's "returns 401 on every documented
  runtime error" is literally true, not an approximation. The counterintuitive half is also right:
  research/pages/api-platform_reference_policies_quota-policy.txt line 1197 "`policies.ratelimit.QuotaViolation`
  | `500`" versus line 1260 "**Note:** When the rate of incoming requests exceeds the thresholds set
  by Quota or SpikeArrest policy, the system returns an HTTP status code `429 Too Many Requests`."
  research/pages/api-platform_reference_policies_verify-jwt-policy.txt line 1099 "The 'grace
  period' for times, to account for clock skew between the issuer and verifier of a JWT. This will
  apply to both the expiry (the `exp` claim) as well as the not-before-time (the `nbf` claim)."

## HARD-14 Partial restore leaves inconsistent state

- Verdict: OK
- Defect: none
- Severity: n/a
- Evidence: research/pages/https___docs.apigee.com_private-cloud_v4.53.01_backup-and-restore.txt
  line 41 "When you restore one of ZooKeeper, Cassandra or LDAP nodes it is recommended to restore
  all three nodes in order to achieve consistency (especially when organizations/environments have
  been created since backup was created)." and the same page's "installation data is distributed
  across several systems, for example organizations are in LDAP, ZooKeeper and Cassandra". OPDK
  scoping is correct; no hybrid-only tooling is applied.

## HARD-15 It looks like a product defect

- Verdict: DEFECT
- Defect: The ground truth overclaims. It states "The documented restriction explains the behavior
  completely, and the update timing is coincidence", but the restriction only explains why the
  rewrite does not take effect — it does not produce a 500. The documented text says Apigee
  initializes `target.url` in the TargetEndpoint and that you cannot override it from the
  ProxyEndpoint; an ignored override means the request goes to the original target URL, which is
  not a fault at all. The evidence supplied (no status body, no fault code, no target
  configuration, no statement about what the proxy called instead) cannot establish that the
  500 arises from this, and "the update is coincidental" is asserted rather than shown. An agent
  that stops here has not diagnosed a 500.
- Severity: medium
- Evidence: research/pages/api-platform_reference_policies_assign-message-policy.txt line 4089 "If
  you want to rewrite the target URL, override the `target.url` variable by configuring an
  AssignMessage policy with the `<AssignVariable>` element, and attaching it to the
  `TargetEndpoint`. (You can't override `target.url` in a policy attached to the `ProxyEndpoint`,
  because Apigee initializes the variable in the `TargetEndpoint`)." — the documented claim is
  "the override does not apply", not "a 500 results". The remediation's location advice is correct.

## HARD-16 The Management Server will not start, and it started fine three weeks ago

- Verdict: DEFECT
- Defect: Unsupported verification claim. The remediation ends with "look for all eight central
  types, including `identityzone-datastore`". The count and the `identityzone-datastore` type are
  in none of the scenario's five references and in none of the OPDK pages available: the
  pod-details page documents the call itself but its only worked example is the `gateway` pod,
  listing `message-processor`, `dc-datastore`, `management-server`, `cache-datastore`,
  `keyvaluemap-datastore`, `counter-datastore`, `kms-datastore` and `router` — and `how-monitor`
  contains no datastore-type list at all. An agent told to confirm "eight" against that output
  will count seven and report a false gap.
- Severity: low
- Evidence: <https://docs.apigee.com/private-cloud/v4.53.01/viewing-pod-details> (fetched
  2026-10-12) gives `curl -u adminEmail:pword http://ms_IP:8080/v1/servers?pod=podName` with
  `podName` one of gateway/central/analytics and shows only the `gateway` sample;
  <https://docs.apigee.com/private-cloud/v4.53.01/how-monitor> (fetched 2026-10-12) has no
  `/v1/servers?pod=central` and no datastore-type enumeration. The scenario's log-path claim, by
  contrast, is supported: the log-rotation page states "Similar files exist for other edge-*
  components ... such as edge-management-server, edge-router, edge-postgres-server, and
  edge-qpid-server". The origin case is real and correctly labelled (research/notes-rw-opdk.md
  line 902 URL, post 13 quoted at line 987), and the scenario's refusal to assume the identityzone
  keyspace is required on 4.53.01 is the right handling of an unproven link.

## HARD-17 The password is right, the error says it is wrong

- Verdict: OK
- Defect: none
- Severity: n/a
- Evidence: <https://docs.apigee.com/private-cloud/v4.53.01/how-monitor> (fetched 2026-10-12)
  contains `/opt/apigee/customer/application/jmx_auth.sh` with
  `export CASS_JMX_USERNAME=JMX_USERNAME` / `export CASS_JMX_PASSWORD=JMX_PASSWORD`, the inline
  form `CASS_JMX_USERNAME=ADMIN CASS_JMX_PASSWORD=PASSWORD CASS_JMX_SSL=Y ... /opt/apigee/apigee-service/bin/apigee-service
  apigee-cassandra ring`, and the self-test text "Run the following apigee-service command. If it
  runs without error, your configurations are correct. apigee-service apigee-cassandra ring". The
  `validate_upgrade` output block and the origin thread (research/notes-rw-opdk.md line 1162-1168,
  the expert's "safe to disregard during update.sh" and the reporter's "exited with status code 1")
  both check out. The scenario correctly refuses to claim the Cassandra upgrade succeeded.

## HARD-18 The last data center is already converted

- Verdict: DEFECT
- Defect: The scenario's own evidence contradicts its stated versions and its own verification step.
  Metadata says "Versions: 4.52.02 -> 4.53.01, Cassandra 3.11.X -> 4.0.18", but the
  `nodetool describecluster` output it supplies shows DC-1 on **4.0.13** and DC-2 on 4.0.18.
  4.0.13 is the Cassandra version shipped with 4.53.00; a 4.52.02 -> 4.53.01 major upgrade puts
  every node on 4.0.18. So the evidence describes a 4.53.00 -> 4.53.01 minor upgrade, for which
  the documentation says special Cassandra steps do not apply — which undercuts the Checkpoint 2
  framing the whole ground truth is built on. The Verification section then says "confirm
  Cassandra is still on 4.0.18 after any component rollback, with `nodetool describecluster`", a
  check that already fails on DC-1 in the state the scenario hands over.
- Severity: medium
- Evidence: <https://docs.apigee.com/private-cloud/v4.53.01/update-apigee-edge-45202-45301> (fetched
  2026-10-12): "If you are upgrading from Edge for Private Cloud 4.53.00, Cassandra version change
  in 4.53.01 is only a minor version change (Cassandra 4.0.13 to 4.0.18)"; "Users upgrading to
  4.53.00 already have Cassandra version 4.0.13". rollback-45301 (fetched 2026-10-12): "Multiple
  DC, all Cassandra nodes upgraded | Do not rollback Cassandra. Other components can be rolled
  back." Scenario output at scenarios/hard.md lines 2314-2315 gives `4.0.13 : [DC-1-IP1:7000, ...]`
  and `4.0.18 : [DC-2-IP1:7000, ...]`. The rest of HARD-18 is accurate — checkpoint quotes,
  rollback order, the shared-code coupling ("The following Edge components share common code.
  Therefore, to roll back any one of these components on a node, you must roll back all of these
  components that are on that node"), the ANALYZE remedy and its read-lock note all verified
  against the live pages.

## HARD-19 The Java callout crypto worked yesterday and throws NoSuchProviderException today

- Verdict: DEFECT
- Defect: Fabricated fault code in the initial evidence. The trace is presented as carrying
  `steps.javacallout.JavaCalloutExecutionError`. The documented JavaCallout runtime error is
  `steps.javacallout.ExecutionError`, whose error body carries
  `flow.execution.ExecutionReturnedFailure`. `steps.javacallout.JavaCalloutExecutionError` appears
  nowhere in `research/pages/`, nowhere in `.agents/skills/apigee-support-core/references/error-codes.md`,
  and nowhere in the Apigee known-issues corpus; the only real `steps.javacallout.*` codes found
  are `ExecutionError` and a community-reported `JavaCalloutInstantiationFailed`. The prompt's own
  preamble forbids inventing fault codes, and an agent that checks the error reference cannot find
  the one it was handed.
- Severity: medium
- Evidence: research/pages/java-callout-runtime-errors.txt line 16 "steps.javacallout.ExecutionError"
  and the page's error body `"errorcode": "flow.execution.ExecutionReturnedFailure"`;
  .agents/skills/apigee-support-core/references/error-codes.md line 65 "| `steps.javacallout.ExecutionError`
  | 500 |". Everything else in HARD-19 verified against the live changes page
  (<https://docs.apigee.com/private-cloud/v4.53.01/changes-privatecloud-45301>, fetched 2026-10-12):
  the BC -> BCFIPS change, "The recommended workaround is to use the BCFIPS provider ... accessed
  using the string \"BCFIPS\"", the `deprecated` directory removal, the exact copy command
  `cp $APIGEE_ROOT/edge-message-processor/lib/deprecated/some.jar $APIGEE_ROOT/data/edge-message-processor/external-lib/some.jar`,
  and "A High value means the tool has determined that there is a very high probability that the
  item will cause the application to break after upgrading ... A Medium value indicates that the
  tool is unclear about the detection". The origin label is correct: the GitHub issue is recorded at
  research/notes-rw-opdk.md line 1651 with the matching stack trace at lines 1672-1690.

## HARD-20 The write succeeded and the read does not see it

- Verdict: DEFECT
- Defect: The canonical remediation uses the wrong construct. To pin a client to a Message
  Processor zone the scenario shows a proxy `<LoadBalancer>` containing
  `<Server name="mp-az1-1" />` ... `<Server name="mp-az2-2" />`. In proxy configuration `<Server>`
  names a **TargetServer** — a backend host the proxy itself connects to. Naming Message Processors
  there tells the proxy to send its *backend* traffic to hosts called mp-az1-1, which is not
  message-processor selection at all; and the scenario's own next sentence says affinity is
  "configured on the load balancer in front of the Routers", which this XML is not. The snippet
  also contradicts the rubric line, which rewards "Schedules a topology change and records the
  failure-domain consequence" while the only concrete artifact offered is an invalid proxy config.
- Severity: high
- Evidence: research/pages/api-platform_deploy_load-balancing-across-backend-servers.txt line 10
  "Target servers decouple concrete endpoint URLs from target endpoint configurations. Instead of
  defining a concrete URL in the configuration, you can configure one or more named target
  servers. Then, each target server is referenced by name in a target endpoint HTTPConnection."
  and line 25 "A target server configuration consists of a name, a host, a protocol, and a port".
  The mechanism itself is correctly sourced: LOCAL_QUORUM = (replication_factor/2)+1, RF 3 -> 2,
  the replication-factor hard stop, and the Knowledge Hub quote about AZ1/AZ2 (research/notes-rw-opdk.md
  lines 1586-1598, 1536-1548) all verified, and the scenario is right to withhold the
  `consistency.level` grep output and refuse to name the affected keyspaces.

## HARD-21 Half the routers are rejecting a request the other half accepts

- Verdict: DEFECT
- Defect: Fault code not in the documented fault-code reference. The scenario presents
  `{"fault":{"detail":{"errorcode":"messaging.adaptors.http.flow.BadRequest"}}}` as the Apigee
  Message Processor fault body returned by the 1.20.x routers, and names it in "Common incorrect
  answers". The API Monitoring fault codes reference — the page HARD-03 and HARD-19 cite for
  exactly this class of code — contains no such entry: the Gateway category has ten codes
  (APITimedOut, ApplicationNotFound, DecompressionFailure*, KeyAliasNotFound, RouteFailed,
  SharedFlowNotFound, TargetMissing, SslHandshakeFailed, GatewayTimeout, ServiceUnavailable,
  NoActiveTargets, UnexpectedEOFAtTarget) and the HTTP request-validation family is the
  `protocol.http.*` set (BadFormData, BadPath, DuplicateHeader, EmptyHeaderName,
  HeaderNameWithNonAsciiChar, HeaderWithInvalidChar, InvalidPath, ...). `BadRequest` appears
  nowhere in it, and nowhere else in the research corpus outside the scenario text itself.
- Severity: medium
- Evidence: research/pages/mon_fault-codes.txt lines 27-45 (API protocol / HTTP, all `protocol.http.*`
  or `messaging.adaptors.http.flow.LengthRequired`) and lines 66-90 (the complete Gateway block);
  grep across research/ returns the string only in research/notes-rw-opdk.md lines 3275 and 3433,
  which are this scenario's own draft text. The rest of HARD-21 verifies against the live nginx page
  (<https://docs.apigee.com/private-cloud/v4.53.01/nginx-45301>): "Upgrading to Edge for Private Cloud
  4.53.01 from previous versions does not automatically upgrade Nginx software to the latest version
  (1.26.x)", the header-rejection change, the disallowed-header examples, and "Previously, RSA, DSA,
  and DH keys smaller than 2048 bits, and ECC keys smaller than 224 bits, were accepted by default".

## HARD-22 Creating an organization fails with an error code that means nothing

- Verdict: OK
- Defect: none
- Severity: n/a
- Evidence: verified against <https://docs.apigee.com/private-cloud/v4.53.01/changes-privatecloud-45301>
  and .../update-apigee-edge-45202-45301 (both fetched 2026-10-12): "In OpenLDAP 2.6, relative
  distinguished name (RDN) is limited to approximately 241 bytes/characters. This limitation is a
  hard cap enforced and cannot be modified."; "Attempting to create an entities like
  organizations,environments, custom roles, permissions etc. may results in the error message:
  \"message\": \"[LDAP: error code 80 - Other]\"."; "Generally, in Apigee's LDAP, long DNs are
  related to permissions since they are created by concatenating multiple entities."; the example DN
  `cn=@@@environments@@@*@@@applications@@@*@@@revisions@@@*@@@debugsessions,ou=resources,...`; the
  `ldapsearch ... > /tmp/DN.ldif` detection command; "If the above command produces no output, then no
  RDNs in the existing LDAP setup exceed 241 bytes/characters"; the two mitigations; "Keep repeating
  the steps above until your LDAP has no RDNs longer than 241 bytes"; the record-count sanity check;
  and the destructive step `rm -rf /opt/apigee/data/apigee-openldap/*` that the scenario correctly
  uses as the mid-upgrade argument. Uncertainty handling is right: which RDN segment dominates is
  left explicitly unmeasured.

---

## Summary

- **OK: 11** — HARD-02, HARD-03, HARD-04, HARD-05, HARD-07, HARD-08, HARD-12, HARD-13, HARD-14,
  HARD-17, HARD-22
- **DEFECT: 19** — REG-01..REG-08 (8), HARD-01, HARD-06, HARD-09, HARD-10, HARD-11, HARD-15,
  HARD-16, HARD-18, HARD-19, HARD-20, HARD-21 (11)
- By severity: critical 0, high 1, medium 6, low 12.

The single high-severity item is HARD-20's remediation construct. The six medium items are
HARD-06 (title gives the answer), HARD-09 (evidence contradicts the cited page), HARD-15 (ground
truth claims a complete explanation the evidence cannot support), HARD-18 (evidence contradicts
its own stated versions), HARD-19 (invented fault code) and HARD-21 (fault code absent from the
fault-code reference). Eight of the twelve low items are one systemic issue: every regression.md
title states its own resolution, and the title is injected into the agent prompt.

Two cross-cutting observations worth carrying forward:

1. The fault codes in HARD-19 and HARD-21 are the same class of error the index dedupe defect
   produces — a code that looks plausible, is never contradicted by the index because it is not in
   it, and is not caught by a check that only verifies codes present in the index.
2. Ten of the 47 cited URLs have no page in `research/pages/` at all (port-requirements,
   apache-cassandra-maintenance-tasks, about-cassandra-replication-factor-and-consistency-level,
   how-monitor, changes-privatecloud-45301, edge-configuration-file-reference,
   handling-postgresql-database-failover, starting-stopping-and-restarting-apigee-edge,
   antipatterns/intro, view-page). Their quotes verified against the live documentation, but a
   reviewer running only the local corpus cannot check them, which is how HARD-16's "eight central
   types" survived.

   > **Annotation, 2026-10-13.** This list is wrong and the count is too low. It is twelve, not
   > ten. `view-page` is not a URL and appears nowhere else in the repository.
   > `antipatterns/intro` is a cloud.google.com page scoped to Apigee and hybrid, not an OPDK
   > page. Three genuinely uncached OPDK pages (nginx-45301, rollback-45301,
   > update-apigee-edge-45202-45301) are missing from the list because raw copies of them survive
   > under `research/scratch-pages/` and read as fetched. Commit `9c02e0a` re-derived the list and
   > cached all eleven OPDK pages. Five cited documentation URLs still have no local copy; they
   > are listed in D-022 in `evaluation/defect-register.md`.

| ID | Severity | One-line description | Source that contradicts it |
| --- | --- | --- | --- |
| HARD-20 | high | Remediation pins Message Processors with a proxy `<LoadBalancer><Server name="mp-az1-1"/>`, which names TargetServers (backend hosts the proxy calls), not MPs | research/pages/api-platform_deploy_load-balancing-across-backend-servers.txt line 10, line 25 |
| HARD-06 | medium | Title "Not enough evidence, and that is the answer" is the ground truth, and the prompt preamble rewards exactly that answer | evaluation/packets/HARD-06.prompt.md line 13; tests/make_packets.py line 206 |
| HARD-09 | medium | Evidence (98% failing, 2% succeeding) and Verification ("partial success persists") contradict the antipattern page, which says failure is total; ground truth asserts the total form without addressing the 2% | research/pages/api-platform_antipatterns_load-balancing-maxfailures.txt line 96, line 106 |
| HARD-15 | medium | "The documented restriction explains the behavior completely" — the documented restriction only says the ProxyEndpoint override does not apply; nothing in the evidence explains a 500 | research/pages/api-platform_reference_policies_assign-message-policy.txt line 4089 |
| HARD-18 | medium | Evidence shows DC-1 on Cassandra 4.0.13 (the 4.53.00 version) while metadata says 3.11.X -> 4.0.18, and Verification demands 4.0.18 cluster-wide | live update-apigee-edge-45202-45301 ("only a minor version change (Cassandra 4.0.13 to 4.0.18)"); live rollback-45301 |
| HARD-19 | medium | Evidence fault code `steps.javacallout.JavaCalloutExecutionError` does not exist; documented code is `steps.javacallout.ExecutionError` | research/pages/java-callout-runtime-errors.txt line 16; .agents/.../error-codes.md line 65 |
| HARD-21 | medium | Fault code `messaging.adaptors.http.flow.BadRequest` appears nowhere in the API Monitoring fault codes reference | research/pages/mon_fault-codes.txt lines 27-45, lines 66-90 |
| HARD-01 | low | Difficulty/placement: no competing explanations (file's own rule sends such cases to adversarial.md); plus an undocumented "not-ready runtime produces a gateway-style 503" claim | scenarios/hard.md lines 7-10; research/pages/apigee-known-issues.txt line 1301-1303 |
| HARD-10 | low | Title states the ground truth; MP restart and per-MP memory are hybrid/OPDK-only while the product label reads "Apigee or hybrid" | research/pages/api-platform_get-started_compare-apigee-products.txt line 15 |
| HARD-11 | low | Remediation prescribes JWKS caching in a scenario with no VerifyJWT, JWKS or IdP anywhere in its evidence | research/pages/api-platform_reference_policies_jwt-policies-overview.txt line 407 (true of the page, inapplicable to the case) |
| HARD-16 | low | "look for all eight central types, including identityzone-datastore" is in no cited reference and on no OPDK page available | live viewing-pod-details (gateway sample only); live how-monitor (no datastore-type list) |
| REG-01 | low | Title "The safest recommendation is to change nothing" is the answer | evaluation/packets/REG-01.prompt.md line 13 |
| REG-02 | low | Title "The right answer is a question" is the answer | tests/make_packets.py line 206 |
| REG-03 | low | Title "A plausible command that does not exist" is the answer | tests/make_packets.py line 206 |
| REG-04 | low | Title "Root cause cannot be established" is the answer | tests/make_packets.py line 206 |
| REG-05 | low | Title "A corrected skill must not reintroduce a stale source" states the lesson | tests/make_packets.py line 206 |
| REG-06 | low | Title "Evidence points away from the reported component" states the finding | tests/make_packets.py line 206 |
| REG-07 | low | Title states the resolution, and the cited page contains no case-evidence requirements | research/pages/support_getting-started-with-support.txt (full file, 40 lines) |
| REG-08 | low | Title announces the injected comment before the bundle is read | tests/make_packets.py line 206 |
