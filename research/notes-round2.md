# Research round 2 — real failure reports and hybrid operations

Session date: 2026-10-11. All cloud.google.com URLs below were fetched with
`research/fetch.sh`, which prints the real HTTP status and rejects soft 404s (HTTP 200 with
body "The equivalent page does not exist in Apigee"). All GitHub URLs were fetched through the
GitHub REST API via `gh api` (authenticated) and the full issue bodies and comment threads were
read, not just search snippets. Fetched page bodies are in `research/pages/`, issue threads in
`research/issues/`.

Tools written this session:

- `research/gh-issue.sh OWNER/REPO NUMBER [name]` — dumps issue + all comments to
  `research/issues/<name>.txt`. New; verify with `./gh-issue.sh` before citing.

---

## PART 1 — REAL-WORLD FAILURE REPORTS

## 1A. Official known-issues register (evidence level (a))

Source: <https://cloud.google.com/apigee/docs/release/known-issues> — observed **HTTP 200,
85178 bytes**. The page carries issue IDs, affected versions, status (FIXED/OPEN), verbatim error
strings and workarounds. This is the highest-quality public failure corpus for Apigee because it
is vendor-maintained and version-pinned. 92 entries were extracted. The ones that make good
support cases are below.

### F-01. Issue 543171828 — runtime logs silently stop after an upgrade

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: Apigee hybrid. Affects "hybrid 1.14.7, hybrid 1.15.7, and hybrid 1.16.8".
- Status on page: **FIXED in hybrid 1.16.9**.
- Problem, verbatim: **"The `apigee-logger` DaemonSet is not scheduled on any node, so Apigee
  runtime logs stop reaching Cloud Logging."**
- Detection command, verbatim: "After you install or upgrade to an affected version,
  `kubectl get daemonset apigee-logger -n apigee` reports a desired count of `0` and no logger
  pods are created."
- Root cause, verbatim: "The `apigee-telemetry` chart has always shipped a default
  `logger.nodeSelector` of `apigee.cloud.google.com/apigee-logger-enabled: "true"`, which
  requires you to label the nodes that should run the logger. Releases before the affected
  versions ignored component-level node selectors, so the logger was scheduled on the Apigee node
  pools even though the nodes were not labeled. The affected releases apply component-level node
  selectors correctly, so the default now takes effect and the DaemonSet matches no nodes."
- Precondition: "Only deployments that set `logger.enabled: true` are affected."
- Workarounds, verbatim element names: clear `logger.nodeSelector` (`key: ""`, `value: ""`) in
  `overrides.yaml`, or run
  `kubectl label nodes NODE_NAME apigee.cloud.google.com/apigee-logger-enabled=true`.
- Evidence level: (a) official docs.
- Why it is a good case: the fix for one bug (correctly honouring component-level node selectors)
  created a silent regression in a *different* component. The symptom is "we have no logs",
  which reads as a logging problem, not as a scheduling problem.

### F-02. Issue 534420582 — ExtractVariables and the backend disagree about duplicate JSON keys

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: "Apigee / Apigee hybrid". **FIXED in hybrid 1.15.8**.
- Problem, verbatim: **"JSON payloads with duplicate keys may be interpreted differently by
  Apigee policies and by backend services, which can weaken content-based security checks."**
- Detail, verbatim: "The [ExtractVariables] policy uses JSONPath, which resolves duplicate JSON
  keys using *last-wins* semantics. Some backends—most notably Google Cloud APIs that accept
  proto3 JSON—instead *merge* repeated keys (for example, concatenating repeated array fields).
  If an Apigee proxy relies on ExtractVariables + JSONPath + [RaiseFault] to inspect and block
  privileged request bodies, an attacker can hide malicious content in a duplicate key that the
  Apigee policy does not see but the backend still processes."
- Workaround, verbatim: "Do not rely on ExtractVariables with JSONPath alone as a security
  boundary for backends that accept proto3 JSON. Add a JSONThreatProtection policy to the request
  flow before ExtractVariables…"
- Evidence level: (a) official docs. Security-relevant; fault codes `steps.extractvariables.*` and
  `steps.jsonthreatprotection.*` are both in the skill's error-codes file.
- Why it is a good case: "our security policy is in place and is being bypassed" and "Apigee is
  parsing the body correctly" are both wrong. The two layers use different JSON semantics.

### F-03. Issue 513032450 — `apigee-connect-agent` hangs with no detectable symptom

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: hybrid 1.16.2. **FIXED in hybrid 1.17.1**.
- Problem, verbatim: **"`apigee-connect-agent` first tether wedges on RKE2-on-GKE clusters after
  Go 1.26.3 toolchain bump."**
- The key sentence for support purposes, verbatim: "The hung connection is not detectable by the
  `apigee-connect-agent` pod. The root cause is still under investigation, but may lie in cloudNAT,
  which is used by our test clusters."
- Workaround, verbatim: "Use more than one `apigee-connect-agent` pod. The second pod will come up
  healthy, and the first pod will reset the connection after 2 hours and become healthy thereafter."
- Evidence level: (a) official docs, and the only case here where the vendor explicitly says the
  root cause is unknown.
- Why it is a good case: a control-plane link that is down with no pod-level error. A support
  agent that only reads pod status will find nothing wrong.

### F-04. Issue 515424331 — image pull fails but Helm upgrade does not

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: hybrid 1.16.3. **FIXED in hybrid 1.16.4**.
- Problem, verbatim: **"The `apigee-pull-push.sh` script fails on 1.16.3 because some images
  carried over from 1.16.2 were not retagged with the `1.16.3` tag in the
  `gcr.io/apigee-release/hybrid/` repository."**
- The discriminating sentence, verbatim: "When `apigee-pull-push.sh` (or any manual `docker pull`)
  requested an affected image at the `1.16.3` tag, the registry returned an `image not known` error
  and the script aborted. **Upgrades performed through the Apigee hybrid Helm charts were not
  affected, because the charts reference the correct image digests directly.**"
- Evidence level: (a) official docs.
- Why it is a good case: the same version number has two different upgrade behaviours depending on
  the path taken. An agent that hears "the upgrade failed" without asking *which* path will
  produce the wrong answer.

### F-05. Issue 482077193 — proxy chaining 404 that is not a routing problem

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: "hybrid 1.15.0 and later". **FIXED in 1.16.0-hotfix.1**.
- Problem, verbatim: **"Proxy chaining fails with 404 route_not_found in
  multi-organization, single-namespace configurations."**
- Cause, verbatim: "In Apigee Hybrid environments where multiple organizations share a single
  Kubernetes namespace, proxy chaining may fail intermittently with an HTTP `404 route_not_found`
  error. This occurs because the internal chaining gateways for different organizations use the
  same `ingress_name` selector, causing Envoy to inconsistently load routing rules."
- Workaround element, verbatim: `apigeeChainingGateway: name: internal-chaining-UNIQUE_SUFFIX`.
- Evidence level: (a) official docs.
- Why it is a good case: the symptom is a 404 on a chained call, which is the classic symptom of
  a wrong base path or a missing proxy deployment. Neither is true.

### F-06. Issue 482209901 — deployment never reports status in hybrid 1.16.0

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: hybrid 1.16.0. **FIXED in hybrid 1.16.0-hotfix.1**.
- Problem, verbatim: **"Proxy deployment not completing due to missing RBAC permissions in Hybrid
  v1.16.0."** Detail: "There is a known issue in 1.16.0 where Hybrid clusters may fail to report
  deployment status of proxies. This is due to a missing permission in the `apigee-manager-role`
  role."
- Workaround: "Add the permission to the `apigee-operator` helm chart template: … Add the `- watch`
  verb to the `deployments` resource, after the `- update` verb on line 584."
- Evidence level: (a) official docs.
- Why it is a good case: "deployment is stuck" is read as a runtime problem. It is a Kubernetes
  RBAC verb missing from the controller's own role.

### F-07. Issue 479872706 — MART cannot load any org entities after a 1.16 migration

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: "hybrid 1.16.0 (EKS with WIF and forward proxy)". **FIXED in hybrid 1.16.0-hotfix.1**.
- Problem, verbatim: **"Unable to load API Products, Apps, and Developers after migrating data to
  Apigee Hybrid 1.16."**
- Cause, verbatim: "environments using Workload Identity Federation (WIF) in conjunction with an
  HTTP Forward Proxy may fail to load management entities (API Products, Apps, Developers) due to
  a credential casting regression in MART."
- Workaround, verbatim keys: `ao.image.tag: "1.16.0-hotfix.1"` and `mart.image.tag:
  "1.16.0-hotfix.1"`.
- Evidence level: (a) official docs.
- Why it is a good case: "no API products load in the UI" reads as data loss or a bad import. It is
  a MART image regression gated on two specific features being on together.

Related and distinct: issue **479040521**, "**`apigee-operator-guardrails-sa` not created on AKS/EKS
with Federated Workload Identity.**", hybrid 1.16.0, fixed in 1.16.0-hotfix.1, workaround is to
patch `apigee-operator/templates/apigee-operator-guardrails-sa.yaml` to add
`(.Values.gcp.federatedWorkloadIdentity.enabled)` to the initial `if`.

### F-08. Issue 471125841 — a deployed timeout change that is not honoured

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: "hybrid 1.14.x,hybrid 1.15.x". **FIXED in hybrid 1.16.x**.
- Problem, verbatim: **"When a new API proxy revision is created and deployed with an updated
  `io.timeout.millis` value, the new value might not be consistently honored."**
- Detail, verbatim: "The updated value of `io.timeout.millis` is intermittently not honored for
  API requests. This happens when multiple servers are used under `<LoadBalancer>` in the
  TargetEndpoint."
- Workaround, verbatim: "After API proxy deployment, restart the apigee-runtime pods one by one so
  that the change is propagated correctly."
- Evidence level: (a) official docs.
- Why it is a good case: "my timeout change did not apply" is read as a deployment failure. The
  deployment succeeded; the runtime pods did not all pick up the value. It is also *conditional on
  LoadBalancer*, which nothing in the ticket would suggest.

Companion issue **246774745**, "**Value of `io.timeout.millis` is not honored when used with
multiple dynamic targets.**" — "If a proxy sets two or more `io.timeout.millis` values in two or
more flows using the same target host, only one `io.timeout.millis` value is honored."

### F-09. Issue 465834046 — cert-manager upgrade silently arms a CA key rotation that will cause an outage

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: "hybrid 1.14.3, hybrid 1.15.1, and hybrid 1.16.0 and later **for upgrades**".
  **FIXED in hybrid 1.14.3, 1.15.1, and 1.16.0 for fresh installs.**
- Problem, verbatim: **"cert-manager versions 1.18+ changed the default for the private key
  rotation policy from `Never` to `Always`. If the private key for `apigee-ca` is rotated it will
  impact traffic."**
- The scoping sentence that makes it a support trap, verbatim: "**Note:** This only applies to
  upgraded Apigee hybrid clusters. The certificates in fresh installs of the hybrid versions
  1.14.3+, 1.15.1+, and 1.16.0. already have the rotation policy set to `Never`."
- Trigger, verbatim: "Newer versions of cert-manager (v1.18+) now automatically rotate the private
  keys. When this key is rotated for the `apigee-ca` certificate, it will cause an outage."
- Workaround: do not upgrade cert-manager past 1.17.x, or patch
  `kubectl patch Certificate -n cert-manager --type=json -p='[{"op": "replace", "path":
  "/spec/privateKey/rotationPolicy", "value": "Never"}]' apigee-ca` **before** upgrading.
  Verify with `kubectl get certificate apigee-ca -n cert-manager -o yaml`.
- Evidence level: (a) official docs.
- Why it is a good case: two clusters on the *same hybrid version* behave differently based on
  whether they were upgraded or installed fresh. The outage is deferred and unpredictable, so it
  will present as an unrelated incident weeks later.

### F-10. Issue 480997525 — `The URI contain illegal characters` caused by a Netty upgrade

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: "Apigee 1-17-0-apigee-1". **FIXED in Apigee 1-17-0-apigee-2**.
- Problem, verbatim: **"Proxy calls fail with `The URI contain illegal characters` error after Netty
  upgrade."** Detail: "In Apigee version 1-17-0-apigee-1, a Netty upgrade to 4.1.129.Final
  introduced a regression. This can cause API proxy calls to fail with a `400` status code and the
  error message `The URI contain illegal characters`. This issue is tracked externally in
  netty/netty#16020."
- Evidence level: (a) official docs, with an upstream third-party tracker.
- Why it is a good case: a 400 with a message about the URI reads as a client encoding bug. Every
  layer above Netty is behaving correctly.

### F-11. Issue 458417250 — OAuth failures caused by a duplicated `authorization` header

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: "Apigee 1-16-0-apigee-4". **FIXED in Apigee 1-16-0-apigee-6**.
- Problem, verbatim: **"Message Processor returns 500 error with `"Duplicate Header
  "authorization""`."** Detail: "When multiple authorization headers are present in a request, the
  Apigee ingress gateway doesn't concatenate them into a single header. This results in the
  Message Processor returning a `500` error with a `"Duplicate Header "authorization""` message."
- Stated workaround, verbatim: "If multiple authorization headers are present in the request,
  concatenate them into a single header. For example: `curl -s https://my-hostname.net/mocktarget/echo
  -H 'authorization: a, b'`"
- Evidence level: (a) official docs.
- Why it is a good case: an OAuth-looking 500 is read as a token problem. It is an HTTP framing
  problem in the ingress. Note the documented workaround is itself a trap — it satisfies the
  ingress while producing a nonsense token.

### F-12. Issue 433759657 — Java callout breaks after a platform fix, on the customer's code

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: Apigee. **FIXED in 1-16-0-apigee-3 or later** (platform side).
- Error string, verbatim: `{"fault":{"faultstring":"Failed to execute JavaCallout.
  org/apache/commons/lang/StringUtils","detail":{"errorcode":"steps.javacallout.ExecutionError"}}}`
- Cause, verbatim: "This error occurs when a Java Callout policy incorrectly depends on libraries
  intended for Apigee's internal use instead of providing its own dependencies."
- The label "FIXED" applies to the platform, but the page says **"Action required:"** — "developers
  must ensure that all Java Callouts are self-contained and utilize their own dedicated libraries,
  avoiding any reliance on Apigee's internal class path."
- Evidence level: (a) official docs.
- Why it is a good case: the register says FIXED, so a support agent may tell the customer their
  version is patched, while their proxy still fails until they change the bundle.

### F-13. Issue 415061771 — scary controller errors that are explicitly harmless

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Status: **OPEN** (not fixed, and not meant to be).
- Message, verbatim: **"Object has been modified"** — full text: "Hybrid customers could observe
  the recurring "object has been modified; please apply your changes to the latest version and try
  again." messages in controller logs. These messages are a harmless side-effect of Apigee and
  Apigee Hybrid built-in safety mechanisms and do not indicate any risk… These errors mean that
  two sub-controllers tried to update their internal "specs" at the same time… Because these are
  purely internal administrative updates and do not change how APIs actually process traffic, the
  services should remain stable and completely unaffected."
- Evidence level: (a) official docs.
- Why it is a good case: an OPEN issue whose entire content is "ignore this". Correct triage is to
  say so immediately and stop investigating.

### F-14. Issue 207719377 — two SpikeArrest policies produce 502, not 429

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: Apigee. **FIXED in Apigee 1-11-0-apigee-1**.
- Problem, verbatim: **"If there is more than one SpikeArrest policy in a bundle, `502` errors will
  occur."** Workaround, verbatim: "Avoid using more than one SpikeArrest policy in the proxy to
  prevent the issue."
- Evidence level: (a) official docs.
- Why it is a good case: a rate-limiting failure presenting as `502` rather than `429`/`403`. An
  agent matching status codes will conclude the backend is broken.

Related, still relevant behaviourally: issue **209097822**, "**Dynamic updates to rate in spike
arrest may not reflect immediately**" — "For a particular key, if there is continuous traffic, the
key may not be rate limited at the updated rate. If there is five minutes of no traffic for a
particular key, the rate will be reflected." Workaround: "Redeploy the proxy with a new reference
variable if the rate has to take effect immediately. Or use two conditional spike arrests with
different flow variables to adjust the rate."

### F-15. Issue 300660653 — a deployment that should have been rejected, was not

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: Apigee. Status: **FIXED** (the missing validation was added).
- Problem, verbatim: **"An error should be, but is not, returned when deploying proxies with the
  same path to multiple environments that are attached to the same instance and environment
  group"** — "Deploying proxies with the same path to multiple environments that are attached to
  the same instance and environment group is not allowed and should return a warning message about
  a base path conflict. Instead, no error is shown and the deployments appear to succeed."
- Workaround, verbatim: "When deploying and after deployment, verify that there are not base path
  conflicts with deployed proxies and correct as needed."
- Evidence level: (a) official docs.
- Why it is a good case: the canonical "deployment reported success but does not take effect"
  shape, and the documented remedy is *verification*, not redeploying.

### F-16. Issue 260324159 — hybrid deployments taking 20 to 30 minutes

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: "Apigee 1-9-0-apigee-16". Status: **FIXED**.
- Problem, verbatim: **"API proxy and shared flow deployments taking up to 30 minutes."** Detail:
  "API proxies and shared flows could take around 20 to 30 minutes to deploy in the runtime plane
  in certain circumstances due to a 'socket closed' error in synchronizer."
- Evidence level: (a) official docs.
- Why it matters: a slow Synchronizer path makes every "did my deploy land?" question ambiguous.

### F-17. Issue 247540503 — KVM lookup fails under high throughput

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: "hybrid 1.7.0 and later / hybrid 1.8.0 and later". Status: **FIXED**.
- Problem, verbatim: **"A race condition with encryption key lookup can cause KVM lookup
  failures."** Detail, verbatim: "In certain circumstances at very high throughput a race
  condition with encryption key lookup can cause KVM lookup failures."
- Evidence level: (a) official docs.
- Why it matters: intermittent KVM failure is almost always read as a propagation or cache
  problem. This is a documented concurrency defect instead.

### F-18. Issue 205666368 — hybrid does not validate the target certificate by default

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: "hybrid 1.10.2, hybrid 1.10.3". **FIXED in Apigee 1-10-0-apigee-6 and Hybrid
  1.10.3-hotfix.1.**
- Problem, verbatim: **"Apigee hybrid does not validate the target certificate by default."**
- Evidence level: (a) official docs.
- Why it matters: a hybrid client reporting "we do TLS with the backend" has, by default on these
  versions, not been validating anything.

### F-19. Issue 364872027 — PEM formatting error in JWT/JWS policies

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: "Apigee / Apigee hybrid", "versions 1.13 and higher". Status: **FIXED**.
- Problem, verbatim: **"PEM parsing error in JWT/JWS policies due to non-standard format"** —
  "any deviations in the required PEM format of keys used in Apigee JWS or JWT policies may result
  in a parsing error. For example, placing any character other an a newline (`/n`) immediately
  before the `"-----END"` line (post-encapsulation boundary) is not allowed and will result in an
  error." Remedy: "no characters other than a newline, such as trailing spaces or slashes,
  immediately precede the post-encapsulation boundary." Reference: IETF RFC 7468.
- Evidence level: (a) official docs.
- Why it matters: a trailing space on a PEM line reads as a key problem, not a byte-encoding
  problem.

### F-20. Issue 484366184 — ingress manager crash loop caused by Gateway API v1.4

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: "hybrid 1.14.x, hybrid 1.15.x". **FIXED in hybrid 1.16.0.** Note: "Apigee Hybrid 1.16
  is not affected by this issue."
- Problem, verbatim: **"Apigee Hybrid versions 1.14 and 1.15 encounter a crash loop in the
  `apigee-ingressgateway-manager` when Kubernetes Gateway API v1.4.0 or newer is utilized."**
- Workaround, verbatim command:
  `kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.3.0/standard-install.yaml`
- Evidence level: (a) official docs.
- Why it matters: the crash is in Apigee's component but caused by an independently upgraded
  cluster add-on.

### F-21. Issue 146222881 — HTTP/2 `Invalid HTTP Header` between Istio and the message processor

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: "hybrid 1.3.0 and later". Status: **FIXED**.
- Problem, verbatim: **"Invalid HTTP Header error"** — "The Istio ingress switches all incoming
  target responses to the HTTP2 protocol. Because the hybrid message processor only supports
  HTTP1, you may see the following error when an API proxy is called: `http2 error: Invalid HTTP
  header field was received: frame type: 1, stream: 1,` ` name: [:authority], value:
  [domain_name]`"
- Remedies, verbatim: "Modify the target service to omit the Host header in the response." /
  "Remove the Host header using the AssignMessage policy in your API proxy if necessary."
- Evidence level: (a) official docs.

### F-22. Issue 490308770 — authenticated forward proxy produces malformed URLs in Helm templates

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: "hybrid 1.12.x, hybrid 1.15.x, hybrid 1.16.0". **FIXED in 1.16.0-hotfix.1 and 1.15.2**.
- Problem, verbatim: **"Authenticated HTTP proxy configurations fail due to malformed URL strings
  in Helm templates."** Detail: "Apigee Hybrid Helm charts generate malformed `http_proxy` and
  `https_proxy` strings. The templates incorrectly inject double-quotes into the middle of the
  URL, causing components like the guardrail validation pods to crash with a `net/url: invalid
  userinfo` error."
- Evidence level: (a) official docs.

### F-23. Issue 391140293 — scaling ingress pods causes 503

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: "Apigee / Apigee hybrid". Status: **FIXED**.
- Problem, verbatim: **"Scaling of Istio ingress pods can cause a `503` error."** Detail: "Scaling
  of the Istio ingress pods can occasionally cause a `503` error. If a `503` error occurs, logs
  for the load balancer display the following message: `statusDetails:
  backend_connection_closed_before_data_sent_to_client`." Workaround: "Manually scale the Istio
  ingress pods."
- Evidence level: (a) official docs.

### F-24. Issue 242213234 — "no connections available" from the Apigee Connect agent

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: Apigee. Status: **FIXED**.
- Error string, verbatim: "Products were not loaded successfully. Error: no connections available
  from the Apigee connect agent(s)."
- Cause, verbatim: "The problem occurs after enabling VPC service control in the Google Cloud
  project and adding `iamcredentials.googleapis.com` as one of the restricted services in the
  service perimeter."
- Evidence level: (a) official docs.
- Why it matters: the message names the Apigee Connect agent, which is the right component, but
  the operator will fix the agent; the perimeter is the problem.

### F-25. Issue 451841788 — hybrid chart demands Monetization config when Monetization is off

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: "hybrid 1.14.3 and hybrid 1.15.1". Status: **FIXED**.
- Error string, verbatim: `Error: UPGRADE FAILED: execution error at
  (apigee-org/templates/mint-task-scheduler-gsa-secret.yaml:12:63): mintTaskScheduler.serviceAccountPath
  is required!`
- Workaround: "Remove the `apigee-org/templates/mint-task-scheduler-gsa-secret.yaml` and
  `apitee-org/templates/mint-task-scheduler-sa.yaml` files." (the second path is reproduced with
  the vendor's own typo `apitee-org`).
- Evidence level: (a) official docs.

### F-26. Issue 301458133 — "the revision is immutable" on a previously deployed proxy

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: Apigee. Status: **FIXED**.
- Problem, verbatim: "Some proxy deployment attempts return an error that the revision is
  immutable." Workaround, verbatim: "Click the dropdown arrow next to the **Save** button and
  select **Save as new revision**."
- Evidence level: (a) official docs.

### F-27. Issue 416634326 — third-party CRDs break the ingress gateway manager

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Title, verbatim: "Presence of `istio.io` Custom Resource Definitions (CRDs) in an Apigee hybrid
  cluster may cause failure in `apigee-ingressgateway-manager` pods."
- Evidence level: (a) official docs. (Body was not extracted in detail in this pass — see the
  fetched page before quoting specifics.)

### F-28. Issue 329304975 — a hard basepath ceiling per environment

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: Apigee. Status: **FIXED**.
- Verbatim: "Apigee is enforcing a temporary limit of 1000 basepaths per environment to avoid
  potential failures when deploying API proxy revisions."
- Evidence level: (a) official docs.

### F-29. Issue 401746333 — Nimbus JOSE + JWT in a Java callout

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Platform: "Apigee / hybrid 1.12.4 / hybrid 1.13.3 / hybrid 1.14.1". Status: **FIXED**.
- Verbatim: "The Nimbus JOSE + JWT library may cause a `java.lang.ClassCircularityError` when using
  a JavaCallout policy." Instruction: "do not upgrade to hybrid 1.12.4, hybrid 1.13.3,
  hybrid 1.14.1."
- Evidence level: (a) official docs.

## 1B. GitHub — real developer-reported cases

Repo ownership was verified via the GitHub API before citing. `apigee` resolves as
**owner_type=Organization**; `apigee/api-platform-samples` has 509 stars and
`GoogleCloudPlatform/apigee-samples` exists as a separate org-owned repo. Four candidate repos
were checked and **do not exist** (HTTP 404): `apigee/apigee-edge-auth-request`,
`apigee/api-platform-docs`, `apigee/apigee-scripts`, `apigee/apigee-goog-auth-request`. Nothing
below rests on those names.

Note on author associations as they appear in the API `author_association` field:
`COLLABORATOR` = committed to the repo, `CONTRIBUTOR` = has contributed (opened a PR or issue),
`NONE` = unaffiliated. `MEMBER` would be the org itself.

### G-01. apigee/api-platform-samples#7 — OAuth "missing parameter" errors that were a deployment basepath problem

- URL: <https://github.com/apigee/api-platform-samples/issues/7>
- Repo: `apigee/api-platform-samples`, owner `apigee`, **owner_type=Organization**.
- Platform: not stated in the thread; the sample is an Edge-era OAuth sample. Written 2013.
- Reported errors, verbatim:
  - `Error :"Required param : grant_type"` / `Error :"Invalid redirect_uri"`
  - `{ErrorCode : "invalid_request", Error :"The request is missing a required parameter : response_type"}`
  - `{ErrorCode : "invalid_request", Error :"The request is missing a required parameter : client_id"}`
  - `{ErrorCode : "invalid_request", Error :"Invalid redirection uri http://joe.app/login?scope=READ&state=foobar&code=n9BZ8TiX"}`
- The wrong first explanation, verbatim, from contributor `baskaran-md`: "Can you try adding the
  following query param to the request?: response_type=code". The reporter correctly rejected it:
  "It's a request for access token and not authorisation code. According to documentation,
  response_type and client_id are involved in getting an authorisation code..."
- The actual cause, verbatim, from the same contributor: "There is a notion of deployment basepath
  apart from the proxy basepath which is provided in the proxy. You cannot set that deployment
  basepath from the UI. However, if its not set, it defaults to '/' . There seems to some problem
  around that in UI. Just un-deploying your proxy and deploying again through API made it to work."
- Intermediate maintainer statement, verbatim: "Checked the deployments. It was not deployed
  properly. Fixed it."
- **Resolution status: (iv) fix CONFIRMED WORKING by reporter.** Reporter: "It works for me now."
  Then closed, `state_reason: completed`.
- Still applies today: yes as a *diagnostic shape* (a token-endpoint request being routed to the
  authorize endpoint, or an OAuth error that is really a routing/deployment problem). I could not
  verify from this session whether Apigee still has a separate "deployment basepath" concept
  exposed in the UI; the thread is from 2013 and the terminology has since been reworked. Treat the
  specific UI claim as historical.
- Evidence level: (b) maintainer statement, plus (c) reporter-confirmed.
- Why it is the best OAuth case in this set: a four-message error cascade that every instinct reads
  as "the client is calling the wrong endpoint", where the actual defect was a deployment record.

### G-02. apigee/apigee-deploy-maven-plugin#213 — "deployment failed" that is really "not activated yet"

- URL: <https://github.com/apigee/apigee-deploy-maven-plugin/issues/213>
- Repo: `apigee/apigee-deploy-maven-plugin`, owner `apigee`, **owner_type=Organization**.
- Reported by `vctrainings08` (`author_association: NONE`), 2023-05-30. Closed 2023-08-31.
- Title, verbatim: "Bundle activation issue for 1.x version if deployment takes more than 10 seconds"
- Error string, verbatim: `throw new MojoExecutionException("Deployment failed: Bundle did not
  activate within expected time. Please check deployment status manually before trying again");`
  plus log lines `Waiting to assert bundle activation.....` and `Deployment failed to activate`.
- The reporter's own diagnosis, verbatim: "Plugin completely depends on Thread sleep time and if
  deployment doesn't complete within 10 seconds then exception is coming." The hardcoded code,
  verbatim from the issue body: `Thread.sleep(10L);`
- Maintainer `ssvaidyanathan` (`author_association: COLLABORATOR`) contradicts it, verbatim: "Yes,
  the delay is included only to upload the bundle but not for checking the deployment." and
  "That Thread.sleep(10) is only when the state in the deployment response is not equal to
  "deployed", then the plugin makes another call to get the deployment details. And in that call,
  if the deployed revision is not set, then it fails with that error as the proxy deployment is
  not activated".
- Decisive diagnostic, verbatim from the reporter: "Yes Management API works well directly but it
  took around 30 secs to deploy where as deployment through plugin is failing with activation
  issue."
- **Resolution status: (i) issue CLOSED — and closed without a fix.** Final maintainer comment,
  verbatim: "Closing due to inactivity". No configuration change was merged, and the maintainer's
  own position was that the environment, not the plugin, was slow: "We have many many customers
  using this plugin and no one has reported this issue. So am wondering if your setup is really slow
  and thats causing this issue."
- Still applies today: unverified. I did not check whether the hardcoded `Thread.sleep(10L)` is
  still present in the 1.x branch. Do not assert it either way without checking.
- Evidence level: (b) maintainer statement.
- Why it matters: this is the cleanest public example of "the deployment call succeeded, the
  activation check is a separate question, and conflating them produces a false 'deployment
  failed' ticket". It also shows that "resolved" would be a lie here.

### G-03. apigee/apigeetool-node#70 — a bundle that deploys by hand but not by tool

- URL: <https://github.com/apigee/apigeetool-node/issues/70>
- Repo: `apigee/apigeetool-node`, owner `apigee`, **owner_type=Organization**. Opened 2017-04-25,
  closed 2018-06-04.
- Title, verbatim: "Deployment fails when a keystore or target server is added in the service callout policy"
- The triggering configuration, verbatim from the issue body:

  ```xml
  <HTTPTargetConnection>
    <URL>https://myURL.com</URL>
    <SSLInfo>
        <Enabled>true</Enabled>
        <ClientAuthEnabled>true</ClientAuthEnabled>
        <KeyStore>openiam_tls_keystore</KeyStore>
        <KeyAlias>openiam_tls_client_cert</KeyAlias>
    </SSLInfo>
  </HTTPTargetConnection>
  ```

- Error string, verbatim:

  ```text
  "{\n  \"code\" : \"beans.OtherValidationError\",\n  \"message\" : \"Unexpected Validation Error null\",\n  \"contexts\" : [ ]\n}"
  ```

- Decisive fact, verbatim from the reporter: "When I create a zip of the same proxy bundle and
  upload it to management UI then it deploys fine."
- Maintainer `noahdietz` (`author_association: COLLABORATOR`), verbatim: "I've found the root cause.
  It is an issue in the Apigee Management Server API, which means the issue cannot be completely
  fixed from Apigee tool."
- Reporter-confirmed workaround, verbatim from `Michael-McD`: "In the interim we're using the
  Apigee management API which does work:
  `curl -X POST --header "Authorization: Basic *******=" -F "file=@apiproxy.zip"
  "https://api.enterprise.apigee.com/v1/organizations/our-org/apis?action=import&name=oauth&validate=true"`"
- Same root cause also hit shared flows: "We're trying to integrate our Apigee Proxies into our CI
  and have just discovered the same issue in attempting to deploy "Shared Flows" that reference a
  LoadBalancer."
- **Resolution status: fix RELEASED, then issue CLOSED.** Maintainer 2018-06-04, verbatim: "The
  fix for this was released. I will close this issue." No reporter confirmation after that comment
  — so this is "fix merged/released" with the workaround independently confirmed, *not*
  reporter-confirmed-fixed.
- Still applies today: the specific Management Server validation defect is fixed and should not
  recur. The general lesson (the same bundle can take two different API paths with different
  acceptance behaviour) still applies.
- Evidence level: (b) maintainer statement for the cause, (c) reporter-confirmed for the
  workaround.

### G-04. apigee/apigeelint#154 — the maintainer was wrong, the reporter proved it, the fix merged

- URL: <https://github.com/apigee/apigeelint/issues/154>
- Repo: `apigee/apigeelint`, owner `apigee`, **owner_type=Organization**.
- Reporter claim, verbatim: "Rule PO008 is requesting developers to use a file name for their
  policies that matches the policy's display name. This is inconsistent to Apigee's default
  behavior when exporting code." and "So whenever you are up- and downloading code via the
  Management UI, you would end up in the need to modify the file names over and over again."
- Maintainer `DinoChiesa` (`author_association: COLLABORATOR`) rejected it outright, verbatim:
  "my observations do not align with that. In my experience, Apigee does not modify the policy
  filename and does not explicitly modify the displayname." and "If you think Apigee itself is
  changing either the policy name or the displayname automatically, then... I think that is a bug
  in Apigee (and probably a serious one)."
- The reporter then supplied the evidence. Maintainer's revised position, verbatim: "Thanks
  karsten-wagner, for weighing in. I wasn't aware of that subtlety."
- **Resolution status: (iii) fix MERGED, and (iv) CONFIRMED by reporter.**
  - PR <https://github.com/apigee/apigeelint/pull/191> — verified via API: `merged=true`,
    `merged_at=2020-09-28T16:59:37Z`, title "Rationalize policy name attribute, and policy
    DisplayName".
  - Reporter closing comment, verbatim: "Changes have been merged quite a while ago... Not sure if
    I should, but for hygiene closing this issue."
- Still applies today: the underlying Apigee behaviour (on export, the bundle filename follows the
  `name=` attribute, not `<DisplayName>`) is what the merged PR codifies, so yes.
- Evidence level: (b) maintainer statement, corrected by (c) reporter-confirmed evidence.

### G-05. apigee/apigeelint#526 — a linter that warns in both directions, because it cannot see the TargetServer

- URL: <https://github.com/apigee/apigeelint/issues/526>
- Repo: `apigee/apigeelint`, owner `apigee`, **owner_type=Organization**. Opened 2025-05-25,
  closed 2025-06-04.
- The contradiction, verbatim from user `kacperillo`: "And then I get another warning: '**When
  using a LoadBalancer, the SSLInfo should be configured in the TargetServer, not under
  HTTPTargetConnection**', which is in contradiction to the first one. So in each situation there
  is a warning."
  - Warning 1 (TD012): "TargetEndpoint HTTPTargetConnection should have exactly one SSLInfo"
  - Warning 2 (TD006): "When using a LoadBalancer, the SSLInfo should be configured in the
    TargetServer, not under HTTPTargetConnection"
- Root cause, verbatim from `DinoChiesa`: "the plugin isn't checking that. It's checking the
  proxy. (TargetEndpoint). And it has no way to check the referred TargetServer - in other words it
  has no way to check that SSLInfo is configured in the TargetServer, per the recommendation. The
  design of the plugin is sort of broken - it assumes that if there is an SSLInfo under
  HTTPTargetConnection, then it is NOT present in the TargetServer. But that is not a valid
  assumption."
- The second defect (TD015), verbatim from the reporter: "if I set it to Zero, then it complains to
  be a positive integer. But Apigee best practice document says … 'If there's some constraint such
  that only one TargetServer and if the HealthMonitor is not used, then don't specify MaxFailures
  in the LoadBalancer configuration.'" (that quote is from
  <https://cloud.google.com/apigee/docs/api-platform/antipatterns/load-balancing-maxfailures>,
  verified 200.)
- **Resolution status: (iii) fix MERGED.** Maintainer closing comment, verbatim: "Fixed in
  v2.67.0". No reporter follow-up, so *not* reporter-confirmed.
- Still applies today: v2.67.0 shipped in June 2025; current apigeelint is later. The *root cause*
  is permanent and worth carrying: apigeelint analyses the proxy bundle, and TargetServers live
  outside it, in the environment's target-server configuration.
- Evidence level: (b) maintainer statement.

### G-06. apigee/apigeecli#473 — "malformed request syntax" hiding a FAILED_PRECONDITION

- URL: <https://github.com/apigee/apigeecli/issues/473>
- Repo: `apigee/apigeecli`, owner `apigee`, **owner_type=Organization**. Opened 2024-05-28.
- Real API error, verbatim:

  ```text
  "message": "generic::failed_precondition: revision organizations/djfong-autopush-ngsaas/apis/apiproduct-operations-oauth2/revisions/3 is currently deployed in default-dev",
  "status": "FAILED_PRECONDITION",
  ```

  with `"code": 400` and a `DebugInfo` detail repeating the string three times.
- What the user actually saw on the terminal, verbatim: `Error: Bad Request - malformed request
  syntax` followed by the full `apigeecli apis delete` usage block.
- Reproduce command, verbatim: `apigeecli apis delete --name apiproduct-operations-oauth2 --org
  djfong-autopush-ngsaas --token ... --disable-check --api staging`
- Maintainer `kurtkanaskie` (`author_association: COLLABORATOR`) named the real cause, verbatim: "The
  reason being you cannot delete a deployed proxy, it must be un-deployed first, as per the API"
  (citing <https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.apis/delete>).
  Steps given: `apigeecli apis listdeploy --name=proxy-name --org=$ORG`, then
  `apigeecli apis undeploy --name=proxy-name --rev=11 --org=$ORG --env=dev --safeundeploy=false`,
  then delete.
- Maintainer on *why* the message was wrong, verbatim: "I understand, but that's the same error
  message from the Apigee API." and, later, "Agree" to the point that printing usage after a
  failed API call is inappropriate.
- **Resolution status: (ii) fix PROPOSED in comments only, as far as this session verified.** The
  maintainer named the code location — `internal/apiclient/httpclient.go` `getErrorMessage` — and
  said "perhaps that should be embellished to include preconditions", and separately "Agree".
  Contributor `srinandan` (`author_association: CONTRIBUTOR`) added "I have a method to silence
  usage if the error is returned **after** the parameters have been validated." No merged PR was
  confirmed in this session. The issue is closed, `state_reason: completed`.
- Still applies today: **unverified.** I did not read past the thread's last comment.
- Evidence level: (b) maintainer statement for the real cause; the tooling defect itself is (b)
  proposed only.

### G-07. apigee/apigeelint#501 — an undocumented requirement shipped by a code-cleanup PR

- URL: <https://github.com/apigee/apigeelint/issues/501>
- Repo: `apigee/apigeelint`, owner `apigee`, **owner_type=Organization**.
- Title, verbatim: "#494 added new undocumented required `EX-` plugin prefix"
- Maintainer `DinoChiesa` admits it, verbatim: "Hmmm... You're right. I hadn't thought people would
  need to use a different prefix." and "Your view is valid that if this is the restriction, we
  should have documented it."
- The trade-off the maintainer names, verbatim: "Requiring ALL external plugins to have a name like
  EX000 implicitly avoids name clashes. I am not sure if there would be any problem if there was an
  external plugin with the same name as a bundled plugin."
- Resolution taken: keep the restriction, document it. Verbatim: "we are thinking that we might want
  to just keep it simple and document the EX prefix as a restriction." then "Fixed in #503 ."
- **Resolution status: (iii) fix MERGED (documentation only) and (iv) CONFIRMED by reporter.**
  - PR <https://github.com/apigee/apigeelint/pull/503> — verified: `merged=true`,
    `merged_at=2025-03-14T17:02:21Z`, title "docs: clarify the requirement for naming of External
    Plugins".
  - Reporter, verbatim: "I spoke to the team and we can handle this update, so no worries."
- The introducing PR is <https://github.com/apigee/apigeelint/pull/494> — verified:
  `merged=true`, `merged_at=2024-12-19T17:07:04Z`, title "chore: code cleanup. add new test for
  PO039."
- Still applies today: yes; the EX- prefix is still required.
- Evidence level: (b) maintainer statement, (c) reporter-confirmed.
- Why it belongs here: a pure code cleanup changed a user-visible contract. "Refactor with no
  behaviour change" is false often enough that a support skill should assume otherwise.

### G-08. apigee/apigeetool-node#6 — self-signed management endpoint, and an `insecure` flag that is not the same bug

- URL: <https://github.com/apigee/apigeetool-node/issues/6>
- Repo: `apigee/apigeetool-node`, owner `apigee`, **owner_type=Organization**. Opened 2014-12-04.
  **Still OPEN as of this session.**
- Error, verbatim:

  ```text
  Error: UNABLE_TO_VERIFY_LEAF_SIGNATURE
      at SecurePair.<anonymous> (tls.js:1380:32)
      ...
  ```

- `gbrail` (`author_association: NONE`, signed "greg brail | apigee <https://apigee.com>") proposed
  two options, verbatim: "We could add a flag that lets you pass in a CA certificate as a PEM file"
  or "we could add a flag to disable certificate validation, like the "-k" flag to "curl.""
- The reporter rejected the second, verbatim: "I think, that disabling the validation is not a
  good approach, although there might be cases when you don't have other choice."
- **Resolution status: split.** PR-linked fix: reporter states "I think, this problem has been
  resolved in #7 . At least it works for me :)" → that is **(iv) reporter-confirmed** for this
  issue's specific symptom. But the issue is still open, and the last comment shows the insecure
  flag does not cover the neighbouring case: "I tried the `insecure` option and it didn't solve
  <https://github.com/apigee/apigeetool-node/issues/33>" — that other issue is titled "Error: unable
  to verify the first certificate", i.e. an incomplete chain, which is a different defect from an
  untrusted root.
- Evidence level: (c) reporter-confirmed, for the CA-file option only.
- Why it belongs here: a single "TLS verification failed" bucket contains at least three different
  root causes (untrusted root, incomplete chain, hostname mismatch) and the insecure flag covers
  only some of them.

### G-09. apigee/apigee-api-catalog-drupal#46 — an OAuth policy defect that was never fixed, only documented around

- URL: <https://github.com/apigee/apigee-api-catalog-drupal/issues/46>
- Repo: `apigee/apigee-api-catalog-drupal`, owner `apigee`, **owner_type=Organization**.
  Opened 2019-10-01. **Still OPEN as of this session.**
- Title, verbatim: "Refer workaround to users impacted by Apigee OAuth policy returning incorrect OAuth2.0 token_type"
- Problem, verbatim: "Apigee OAuth 2.0 Policy returns a non compliant token type causing downstream
  applications like SmartDocs and Swagger UI to send "Authorization" header prefixed with
  BearerToken."
- Maintainer `cnovak` (`author_association: COLLABORATOR`) redirected rather than fixed, verbatim:
  "The documentation about this issue is now explained on the Edge OAuthV2 Policy page, Non-RFC-compliant
  behavior section". Final comment, verbatim: "doc bug b/141752334 is now fixed."
- **Resolution status: documentation workaround only, no code fix.** This is (ii) "fix PROPOSED in a
  comment" at best — a doc link and a third-party reference proxy. The behaviour it describes was
  not fixed in the runtime.
- Still applies today: the OAuthV2 policy page
  (<https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>, verified
  200 this session) does carry a non-RFC-compliance note; I did not read that section in this
  session, so treat the current wording as unverified.
- Evidence level: (b) maintainer statement.
- Why it belongs here: "downstream tools send the wrong Authorization scheme" is universally
  diagnosed as a downstream bug. Here it originates in the gateway's own token response.

### Could not verify / rejected

- **Stack Overflow and Google Cloud community threads: not obtained.** The Stack Exchange API in
  this environment returned stale cached payloads for every query (identical unrelated PySpark
  results for three different `q` values), and web search surfaced only generic documentation
  summaries. I did not fetch a single Stack Overflow thread, so there are **no** SO-sourced cases
  in this note. The search results that did render (e.g. the OAuth HTTP status reference page) are
  documentation, not failure reports, and are already covered by the verified doc set.
- No `apigee/…` repository was found that is *not* org-owned among those cited; the four 404s above
  are the only rejections and they are rejections for non-existence, not for community ownership.
- F-27 (416634326) and the bodies of several other register entries were listed from the register
  but not extracted in full in this pass. Treat their detail lines as unverified.

---

## PART 2 — HYBRID OPERATIONS

Seed page verified first, as instructed:
<https://cloud.google.com/apigee/docs/hybrid/latest/what-is-hybrid> — observed **HTTP 200, 11551
bytes**, saved as `pages/hybrid-what-is.txt`. Link tree extracted with
`grep -oE '/apigee/docs/[a-zA-Z0-9/._-]+' pages/hybrid-what-is.txt | sort -u` (20 paths), then
expanded iteratively across every page fetched below. The version selector on every page confirms
the current release line is **v1.17**, and `/apigee/docs/hybrid/latest/...` redirects into
`/apigee/docs/hybrid/v1.17/...` — so every operational URL below is pinned to v1.17 and the
`latest` alias is safe to cite.

Note on the seed page: the extracted body begins with a stray `# An error occurred. / Unable to
execute JavaScript.` fragment. That is the version-selector widget in the page shell, not the
article. The article content is intact from `## About the runtime plane` onward. Worth knowing
before anyone greps that file for headings.

## 2.1 Architecture and components

### "What is hybrid?" — <https://cloud.google.com/apigee/docs/hybrid/latest/what-is-hybrid> (HTTP 200, 11551 bytes)

Runtime plane components, quoted element names: **Message Processor**, **Synchronizer**,
**Cassandra**, **MART**. Management plane: **Apigee hybrid UI**, **Apigee APIs**, **Unified
Analytics Platform (UAP)**.

- Message Processors: "Hybrid Message Processors (MPs) provide API request processing and policy
  execution on the runtime plane. MPs load all of the deployed proxies, resources, target servers,
  certificates, and keystores from local storage. You configure an Apigee ingress gateway to expose
  the MPs to requests that come from outside the cluster."
- Synchronizer: "The Synchronizer periodically polls the Management Server for changes and downloads
  a new configuration whenever changes are detected. The configuration data is retrieved and stored
  locally as a JSON file on the local file system, where the Message Processors can access it."
  This JSON is called the **contract**.
- **Contract contents, verbatim list** — this is the single most useful fact in hybrid support:
  "Proxy bundles and shared flow deployments / Flow hooks / Environment information / Shared API
  resources / Target server definitions / TLS settings / Key Value Map (KVM) names / Data masks".
  Note carefully: **KVM *names*** travel in the contract, not KVM *entries*. Entries live in
  Cassandra.
- Degraded operation: "If the connection between the management and runtime plane goes down,
  services on the runtime plane continue to function."
- Cassandra stores: "Key management system (KMS) / Key Value Map (KVM) / OAuth / Management API
  for RunTime data (MART) / Monetization data / Quotas / Response cache". Deployed as a
  **StatefulSet** node pool.
- MART: "Like most hybrid services, MART is stateless: it does not persist its own state at
  runtime." and "The Management plane communicates with MART via the Apigee Connect agent… You do
  not call MART directly."
- Verified product claim to carry into answers: "Currently, the hybrid runtime plane can be
  deployed to Google Cloud or in your own data center."

### "Runtime services" — <https://cloud.google.com/apigee/docs/hybrid/v1.17/service-config> (HTTP 200, 17774 bytes)

The authoritative component table. Columns: Service / Description / Configuration Object /
Implemented As / Scope. Copied exactly:

| Service | Configuration Object | Implemented As | Scope |
| --- | --- | --- | --- |
| Apigee Connect | `connectAgent` | Deployment | Kubernetes cluster |
| Apigee Ingress Gateway | `apigeeIngressGateway`, `ingressGateways` | Deployment | Kubernetes cluster |
| Apigee Operators | `ao` | Deployment | Kubernetes cluster |
| Cassandra | `cassandra` | StatefulSet | Organization |
| Guardrails | `guardrails` | Kubernetes pod | Cluster |
| Logger | `logger` | **DaemonSet** | Cluster |
| MART | `mart` | Deployment | Organization |
| Message Processor | `runtime` | Deployment | **Environment** |
| Metrics | `metrics` | Deployment | Cluster |
| Redis | `redis` | **DaemonSet and Deployment (both)** | Cluster |
| Synchronizer | `synchronizer` | Deployment | **Environment** |
| UDCA | `udca` | Deployment | **Environment** |
| Watcher | `watcher` | Deployment | Cluster |

Three support-relevant statements, verbatim:

- Redis exists for one reason: "Redis is used for storing cluster-level rate limit counts used for
  distributed rate limiting used for SpikeArrest policies that use effectiveCount option to
  synchronize request counts across message processors." (See also F-14 — SpikeArrest with more
  than one policy in a bundle is a known 502 source.)
- Watcher is the deployment-status reporter: "Watcher periodically executes task in the runtime
  cluster such as reconfiguring Ingress routes, checking ingress status for new proxy deployments,
  fetching deployment status from Message Processors and Ingress in order to report status to
  Management Plane." **A hybrid ticket saying "deployment never completed" should include a Watcher
  check before anything else.**
- Logger is a DaemonSet, not a Deployment: "Extracts log files and sends the data to the monitoring
  application associated with your Google Cloud account (currently Cloud Operations)." This is
  exactly the component that F-01 broke.

Cassandra sub-pods, quoted: `apigee-cassandra-default` (the database),
`apigee-cassandra-user-setup` ("initializes and configures the users and roles"),
`apigee-cassandra-schema-setup` ("initializes and configures the database schema… setting up
Cassandra keyspace and table definitions"). A `CrashLoopBackOff` on the two `*-setup` pods is a
schema/credential problem, not a data problem.

## 2.2 Installation prerequisites and Kubernetes requirements

### "Prerequisites" — <https://cloud.google.com/apigee/docs/hybrid/v1.17/prerequisites> (HTTP 200, 10655 bytes)

Prerequisite table, quoted verbatim: **Google Cloud billing account**; **Google Cloud project**;
**Clock synchronization**; **Software**; **Hardware**.

- Clock synchronization, verbatim: "Apigee hybrid uses the Cassandra database, and Cassandra relies
  on Network Time Protocol (NTP) synchronization to maintain data consistency… If you plan to
  install hybrid into multiple regions, be sure they are synchronized with NTP across all regions."
- Software, verbatim: "gcloud CLI (required for command line provisioning steps)" and "After the
  gcloud CLI is installed, run `gcloud components update`", "curl (recommended)", and "If you are
  installing Apigee hybrid on EKS and you are using Kubernetes 1.24 or newer, install the
  Kubernetes CSI driver for Amazon EBS."

### "Cluster overview" (minimum configurations) — <https://cloud.google.com/apigee/docs/hybrid/v1.17/cluster-overview> (HTTP 200, 12798 bytes)

Quoted label names and minimums:

| Configuration | Stateful node pool | Stateless node pool |
| --- | --- | --- |
| Purpose | "A stateful node pool used for the Cassandra database." | "A stateless node pool used by the runtime message processor." |
| Label name | `apigee-data` | `apigee-runtime` |
| Number of nodes | "1 per zone (3 per region)" | "1 per zone (3 per region)" |
| CPU | "8 (Prod) / 4 (Non-prod)" | "8 (Prod) / 4 (Non-prod)" |
| RAM | "32 (Prod) / 16 (Non-prod)" | "32 (Prod) / 16 (Non-prod)" |
| Minimum disk IOPS | "2000 IOPS with SAN or directly attached storage. NFS is not recommended even if it can support the required IOPS." | same |

- "For **production** environments, we recommend a minimum of two clusters."
- Cassandra network, verbatim: "Cassandra requires a minimum of 1 Gbps of network bandwidth for each
  machine instance… on GKE, the minimum recommended machine type, `e2-standard-4`… The maximum or
  99th percentile latency for Cassandra should be below 100 milliseconds."
- Multi-region, verbatim: "Always use port 7001 for Cassandra. All other ports are local to the
  region."

### "Supported platforms" — <https://cloud.google.com/apigee/docs/hybrid/supported-platforms> (HTTP 200, 58518 bytes)

The version matrix is per-platform. Read from the fetched table for **hybrid 1.17 on GKE**: Kubernetes
`1.33.x`, `1.34.x`, `1.35.x`, `1.36.x`. hybrid 1.16 on GKE: `1.31.x`–`1.36.x`. hybrid 1.17 on
Anthos on-prem VMware: `1.33.x`–`1.36.x`. The version support matrix changes per release, so the
correct support answer is always "check supported-platforms for your exact hybrid version", never a
memorised number. EKS on 1.17 lists `1.30.x`–`1.36.x` on at least one platform column read.

## 2.3 Runtime pod structure

### "ApigeeDeployment services" — <https://cloud.google.com/apigee/docs/hybrid/v1.17/apigee-deployment-services> (HTTP 200, 9638 bytes)

- **ApigeeDeployment (AD)** is "a CustomResourceDefinition (CRD) used to define, update, and
  release stateless Apigee hybrid components in a Kubernetes cluster."
- "with AD all these resources are maintained as an atomic deployment unit."
- Pod, quoted: `apigee-operators` — "Creates and updates low level Kubernetes and Istio resources
  that are required to deploy and maintain the AD… validates the ApigeeDeployment configuration
  before persisting it in Kubernetes cluster."
- Command, verbatim:

  ```terminal
  kubectl get ad -n APIGEE_NAMESPACE
  ```

  Output shape, verbatim:

  ```text
  NAME                                              AGE
  apigee-mart-my_org                                4h
  apigee-runtime-my_org-my_env                      4h
  apigee-synchronizer-my_org-my_env                 4h
  ```

  The `apigee-runtime-<org>-<env>` and `apigee-synchronizer-<org>-<env>` naming convention is the
  fastest way to confirm which environment a pod serves.

### "Environments" — <https://cloud.google.com/apigee/docs/hybrid/v1.17/environments-about> (HTTP 200, 14278 bytes)

- Overrides shape, verbatim: `envs:` → `- name: test` → `serviceAccountPaths:` with keys
  `synchronizer` and `udca`.
- Routing model, verbatim: "On a request to an API proxy, the ingress compares the `Host` header of
  the incoming request to the list of host aliases to determine which virtual host handles the
  request. `curl` commands, browsers, and many other utilities automatically set the `Host` header
  with the domain of the request. If for any reason your app is not setting the `Host` header
  automatically, you must set it manually." **A hybrid 404 with no Host header set by the client is
  a client-configuration bug, and the doc says so explicitly.**
- "Note that name of the virtualhosts must be the names of the environment groups."
- Documented antipattern and why, verbatim: "**Antipattern**: Deploy all of your proxies to one
  hybrid environment." "**Best practice**: Create multiple environments and deploy a limited number
  of proxies to each one."
- Three reasons to limit proxies per environment, quoted: "Message processor boot-up time" ("There
  is a direct correlation between the amount of time a message processor (MP) takes to boot up and
  the number of proxies deployed to that MP"); "Scaling performance" ("all of the proxies in that
  environment will scale with it"); "Noisy neighbor" ("if one proxy crashes, then all of the
  proxies in the environment will be taken down while the MPs restart").
  **This is the hybrid-specific answer to "is one environment per app?" and it differs from X.**
- Cross-reference: "consider the product configuration limits described in
  [Limits](…/reference/limits#hybrid)" — hybrid has its own limits anchor.

## 2.4 Reading runtime logs and traces in hybrid

### "Using runtime logs" — <https://cloud.google.com/apigee/docs/hybrid/v1.17/runtime-logs> (HTTP 200, 11976 bytes)

- Purpose, verbatim: "Use the runtime logs to help diagnose problems with the `apigee-runtime` pods.
  Each runtime pod contains a message processor, which is responsible for processing API proxy
  traffic, executing policies, routing requests, and more."
- Command, verbatim:

  ```terminal
  kubectl logs -f -n APIGEE_NAMESPACE apigee-runtime-apigee-gcp-prod1-test-blue-hd77q
  ```

- **Contract version log lines** (the discriminator for "did my deploy land on this pod?"),
  verbatim:
  - `hybrid-runtime Apigee-Timer-9 INFO RUNTIME-SYNC-SERVICE - RuntimeSyncServiceImpl.updateToVersion() : Switched to newer version 750 from version null` → "The MP changed to a newer version of the configuration contract."
  - `… loadLatestVersionIfAvailable() : Found a newer version 750` → "The MP loaded the latest contract configuration version from `version.properties`."
  - `… updateToVersion() : Attempting to update to a newer version 750` → in progress.
  - `… updateToVersion() : Switched to newer version 751 from version 750` → applied.
- **Deployment error log lines**, verbatim:
  - `hybrid-runtime org:hybrid env:prod Apigee-Main-6 ERROR i.a.h.e.i.HermesEngineImpl - HermesEngineImpl.handleHermesException() : Keyspace cache_hybrid_hybrid does not exist` → "Keyspace `cache_<orgname>_hybrid` is not provisioned in Cassandra."
  - `hybrid-runtime org:hybrid Apigee-Timer-9 ERROR c.a.s.e.k.HybridEncryptionKeyServiceImpl - HybridEncryptionKeyServiceImpl.getEncryptionKey() : Encryption key does not exist for organization hybrid and type KmsKey` → "Keyspace `kms_<orgname>_hybrid` is not provisioned in Cassandra."
- **Message processor error codes**: "Error codes for the message processor start with
  `runtime.sync.<error-name>`." Documented example, verbatim:
  `runtime.sync.ContractLoadFailedMessage: Error loading spec file` — "**Reason**: The error could be
  caused by an invalid schema, corrupted contract specification file, or invalid contract."
  "**Remedy**: Make sure either the contract specification file is available, the file system is not
  corrupted, or the schema/contract is valid."
- **Critically**: there is **no** `trace` command documented on this page. Hybrid debug traces come
  through the Apigee UI, not through `kubectl`. Do not invent a hybrid trace CLI.

### "Logging" — <https://cloud.google.com/apigee/docs/hybrid/v1.17/logging> (HTTP 200, 8562 bytes)

- Verbatim: "Each runtime plane service writes log data to stdout/stderr, and Kubernetes writes this
  data to the host filesystem. A logs collector for hybrid runs on each hybrid node. The collector
  is a DaemonSet (replicated once and only once per node) whose job is to collect the written log
  data and export it to the Cloud Logging application."

### "View logs" — <https://cloud.google.com/apigee/docs/hybrid/v1.17/logging-view> (HTTP 200, 9769 bytes)

- Verbatim and platform-dependent, this is a support trap: "Logging is provided by default on GKE
  and GKE on-prem. On these platforms, be sure that you have disabled logging in your overrides file
  by setting `logger.enabled` to `false`. On AKS, you must explicitly enable logging by setting
  `logger.enabled` to `true` in your overrides file."
  (Note the apparent contradiction with F-01, which affects only deployments with
  `logger.enabled: true`. Reconcile by asking which platform and what `logger.enabled` is set to.)
- "Ingress logs are managed through Cloud Service Mesh. To view access logs, refer to Accessing
  logs in Cloud Logging… in the Cloud Service Mesh documentation." **Ingress access logs are not in
  the Apigee log stream on current hybrid.**
- Direct pod logs, verbatim: `kubectl logs pod_name -n namespace`, example
  `kubectl logs apigee-mp-hybrid-docs-test-blue-6fb96f5b9-2k8hp -n my-namespace`.

### "Metrics collection" — <https://cloud.google.com/apigee/docs/hybrid/v1.17/metrics-collection> (HTTP 200, 9624 bytes) and "Data collection on hybrid" — <https://cloud.google.com/apigee/docs/hybrid/v1.17/data-collection-overview> (HTTP 200, 9885 bytes)

The reliability table from data-collection-overview is the correct thing to quote when someone
treats telemetry as ground truth. Verbatim rows:

| | Logging | Metrics | Analytics/Deployment Status |
| --- | --- | --- | --- |
| Purpose | "Debugging and troubleshooting" | "Health monitoring and alerts" | "Analytics and API proxy deployment status" |
| Bounded/Unbounded | "Either (unbounded when debug is on; bounded when debug is off)" | "Bounded" | "Unbounded (may generate data on each request)" |
| Relative Speed | "ASAP" | "ASAP" | "Slow" |
| Storage Location | "Your Google Cloud Project" | "Your Google Cloud Project" | "Your Apigee account on the management plane" |
| Collection Method | "Stream" | "Stream" | "Batch" |
| Expected Reliability | "**Lossy**" | "**Lossy**" | "Non-lossy" |

So: on hybrid, logs and metrics are explicitly documented as lossy, while analytics and deployment
status are not. "The metrics say the latency went up" is weaker evidence on hybrid than it looks.

### "Synchronizer access" — <https://cloud.google.com/apigee/docs/hybrid/v1.17/synchronizer-access> (HTTP 200, 15103 bytes)

- Verbatim: "In Apigee hybrid, the Synchronizer's primary job is to poll and download the runtime
  contracts which are supplied by the management plane. Information communicated by contract
  includes API proxies, API products, caches, and virtual hosts. Synchronizer by default stores
  environment configuration data in the Cassandra database." and "One Synchronizer can support many
  Message Processors deployed in the same pod."
- Commands, verbatim:

  ```terminal
  export GOOGLE_APPLICATION_CREDENTIALS=your_sa_credentials_file.json
  gcloud auth application-default print-access-token
  export TOKEN=ya29....Ts13inj3LrqMJlztwygtM
  curl -X POST -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type:application/json" \
    "https://apigee.googleapis.com/v1/organizations/YOUR_ORG_NAME:setSyncAuthorization" \
     -d '{"identities":["serviceAccount:SYNCHRONIZER_MANAGER_SERVICE_ACCOUNT_NAME"]}'
  ```

- The role requirement, verbatim: "Be sure that the service account name that you add to this API
  has the **Apigee Synchronizer Manager** role."
- **This is a classic support trap and the doc is explicit**: if `setSyncAuthorization` was never
  called, the Synchronizer has no permission to pull artifacts and nothing will ever sync, with no
  obvious error. Check this before suspecting a network or runtime problem.

## 2.5 Common runtime failures, from the official register

See Part 1A for F-01 through F-29. The hybrid-specific cluster, in rough triage order:

1. **Control plane cannot reach the runtime** — F-24 (`no connections available from the Apigee
   connect agent(s)`, caused by a VPC Service Controls perimeter covering
   `iamcredentials.googleapis.com`), F-03 (agent tether wedges with no detectable symptom),
   missing `setSyncAuthorization` (2.4 above).
2. **Nothing deploys / deployment status missing** — F-06 (missing `watch` on `deployments` in
   `apigee-manager-role`), F-16 (Synchronizer `socket closed`, 20–30 minute deploys).
3. **Runtime pods up but behaving per-environment** — F-05 (`404 route_not_found` from a shared
   `ingress_name` selector in multi-org single-namespace), F-08 (`io.timeout.millis` not honoured
   under a `<LoadBalancer>`), F-17 (KVM lookup race at high throughput), F-14 (two SpikeArrest
   policies → 502; `effectiveCount` depends on Redis).
4. **Control-plane components crash or are missing** — F-20 (Gateway API v1.4 crash-loops
   `apigee-ingressgateway-manager` on 1.14/1.15), F-07/479040521
   (`apigee-operator-guardrails-sa` missing with Federated WIF on AKS/EKS), F-22
   (`net/url: invalid userinfo` from authenticated forward proxy), F-25
   (`mintTaskScheduler.serviceAccountPath is required!` when Monetization is off), F-21
   (HTTP/2 `Invalid HTTP Header` between Istio and the MP), F-23 (`503` while scaling ingress pods).
5. **Logs and telemetry vanish while the runtime is healthy** — F-01 (logger DaemonSet matches no
   nodes), F-05 in the runtime-logs page (`Keyspace cache_<org>_hybrid does not exist`,
   `Encryption key does not exist for organization <org> and type KmsKey`,
   `runtime.sync.ContractLoadFailedMessage: Error loading spec file`).
6. **Expected-looking alarms that are not incidents** — F-13 (`Object has been modified`),
   F-04 (`image not known` from `apigee-pull-push.sh` only; Helm upgrade was unaffected).

## 2.6 Upgrade procedure

### "Upgrade Apigee hybrid" — <https://cloud.google.com/apigee/docs/hybrid/v1.17/upgrade> (HTTP 200, 78108 bytes)

Prerequisites, verbatim:

- "If your hybrid installation is running a version older than v1.16, you must upgrade to version
  1.16 before upgrading to 1.17." (**No version skipping.** This is the analogue of the Edge for
  Private Cloud `update.sh` rule and should be checked before any upgrade ticket.)
- "Helm version v3.14.2+."
- "`kubectl`: A supported version of `kubectl` appropriate for your Kubernetes platform version."
- "cert-manager: A supported version of cert-manager."

The explicit cost warning, verbatim: "**Upgrading to Apigee hybrid version 1.17 may require
downtime.** When upgrading the Apigee controller to version 1.17.1, all Apigee deployments undergo a
rolling restart. To minimize downtime in production hybrid environments during a rolling restart,
make sure you are running at least two clusters… Divert all production traffic to a single cluster
and take the cluster you are about to upgrade offline, and then proceed with the upgrade process.
Repeat the process for each cluster."

Mixed-version constraint, verbatim: "until all remaining clusters are upgraded Cassandra backup and
restore cannot work with mixed versions. For example, a backup from Hybrid 1.16 cannot be used to
restore a Hybrid 1.17 instance."

"Management plane changes do not need to be fully suspended during an upgrade."

Other verbatim constraints:

- "**Caution:** Do not create new environments during the upgrade process."
- CRD install, verbatim: "**Note:** This is the only supported method for installing Apigee CRDs.
  Do not use `kubectl apply` without `-k`, do not omit `--server-side`."
- Namespace customisation, verbatim: "If your Apigee namespace is not `apigee`, edit the
  `apigee-operator/etc/crds/default/kustomization.yaml` file and replace the `namespace` value with
  your Apigee namespace."
- Dry run, verbatim: "Before executing any of the Helm upgrade/install commands, use the Helm
  dry-run feature by adding `--dry-run` at the end of the command."
- "This step requires elevated cluster permissions" for the operator upgrade.
- Cert-manager step exists as its own subsection because of F-09: `kubectl get certificate apigee-ca
  -n cert-manager -o yaml`, and `kubectl apply -f
  https://github.com/cert-manager/cert-manager/releases/download/v1.19.2/cert-manager.yaml`.

Chart upgrade order and exact commands (all quoted):

| # | Release name | Chart | Verification command | Expected output token |
| --- | --- | --- | --- | --- |
| 1 | `operator` | `apigee-operator/` | `kubectl -n APIGEE_NAMESPACE get deploy apigee-controller-manager` | — |
| 2 | `datastore` | `apigee-datastore/` | `kubectl -n APIGEE_NAMESPACE get apigeedatastore default` | — |
| 3 | `telemetry` | `apigee-telemetry/` | `kubectl -n APIGEE_NAMESPACE get apigeetelemetry apigee-telemetry` | — |
| 4 | `redis` | `apigee-redis/` | `kubectl -n APIGEE_NAMESPACE get apigeeredis default` | — |
| 5 | `ingress-manager` | `apigee-ingress-manager/` | `kubectl -n APIGEE_NAMESPACE get deployment apigee-ingressgateway-manager` | — |
| 6 | `ORG_NAME` | `apigee-org/` | `kubectl -n APIGEE_NAMESPACE get apigeeorg` | `running` |
| 7 | `ENV_RELEASE_NAME` | `apigee-env/` | `kubectl -n APIGEE_NAMESPACE get apigeeenv` | — |
| 8 | `ENV_GROUP_RELEASE_NAME` | `apigee-virtualhost/` | `kubectl -n APIGEE_NAMESPACE get arc` | `apigee-org1-dev-egroup-123abc  running` |

Canonical invocation, verbatim:

```text
helm upgrade ORG_NAME apigee-org/ \
  --install \
  --namespace APIGEE_NAMESPACE \
  -f OVERRIDES_FILE \
  --dry-run=server
```

(then the same without `--dry-run=server`.)

Release-name rule, verbatim and easy to get wrong: "`ENV_RELEASE_NAME` is a name used to keep track
of installation and upgrades of the `apigee-env` chart. This name must be unique from the other Helm
release names in your installation. Usually this is the same as `ENV_NAME`. However, if your
environment has the same name as your environment group, you must use different release names for the
environment and environment group, for example `dev-env-release` and `dev-envgroup-release`."

Rollback, verbatim: "To roll back to the previous version, use the older chart version to roll back
the upgrade process in the reverse order. Start with `apigee-virtualhost` and work your way back to
`apigee-operator`, and then revert the CRDs." "**Tip:** If you know the last release version, you can
use the `helm rollback` command rather than the `helm upgrade` command described below." Rollback
invocations include `--atomic`.

## 2.7 Network and ports

### "Ports" — <https://cloud.google.com/apigee/docs/hybrid/v1.17/ports> (HTTP 200, 19075 bytes)

Internal connections (Source → Destination / Port / Security / Purpose):

| Source | Destination | Port | Security | Purpose |
| --- | --- | --- | --- | --- |
| (management plane) | MART | TLS | TLS | "Requests from the management plane go through Apigee Connect. Apigee Connect initiates the connection." |
| Default Istio Ingress | Message Processor | **TCP/8443** | "TLS (Apigee-generated, self-signed cert)" | "Processes incoming API requests." |
| Message Processor | Cassandra | **TCP/9042, TCP/9142** | mTLS | "Sends data for persistence." |
| Message Processor | fluentd (analytics / logging) | **TCP/20001** | mTLS | "Streams data to the data collection pod." |
| Cassandra | Cassandra | **TCP/7001, TCP/7199** | mTLS | "Intra-node cluster communications." |
| Cassandra | Cassandra | **TCP/7001** | mTLS | "Inter-region communications." |
| Synchronizer | Cassandra | **TCP/9042, TCP/9142** | mTLS | "Sends data for persistence." |
| Prometheus (metrics) | Cassandra | **TCP/7070 (HTTPS)** | TLS | "Scrapes metrics data from various services." |
| Prometheus (metrics) | MART / Message Processor / Synchronizer | **TCP/8843 (HTTPS)** | TLS | "Scrapes metrics data from various services." |
| Prometheus (metrics) | UDCA | **TCP/7070 (HTTPS)** | TLS | "scrapes" |
| Watcher | Ingress pods | **TCP/8843** | TLS | "Polls to get deployment status." |

Note the two-way nature of the Watcher→Ingress port: a support answer that opens 8443 but not 8843
will produce a hybrid deployment-status symptom with no ingress symptom at all.

External connections (quoted destinations):

| Source | Destination | Port | Notes |
| --- | --- | --- | --- |
| Client Apps | Default Istio Ingress | TCP/* | "API requests from external apps." |
| Message Processor | Backend services | TCP/*, UDP/* | "Sends requests to customer-defined hosts." |
| Synchronizer | Apigee Services | TCP/443 | "connects to `apigee.googleapis.com`"; also "`iamcredentials.googleapis.com` for authorization" |
| UDCA (Analytics) | Apigee Services (UAP) | TCP/443 | "connects to `apigee.googleapis.com` and `storage.googleapis.com`" |
| Apigee Connect | Apigee Services | TCP/443 | "connects to `apigeeconnect.googleapis.com`" |
| Prometheus (metrics) | Google Cloud (Cloud Operations) | TCP/443 | "connects to `monitoring.googleapis.com`" |
| fluentd (logging) | Google Cloud (Cloud Operations) | TCP/443 | "connects to `logging.googleapis.com`" |
| MART | Google Cloud | TCP/443 | "connects to `iamcredentials.googleapis.com` for authorization" |
| Message Processor | Distributed Trace back end | http or https | "The back end for Distributed Trace is usually Cloud Trace or Jaeger." |

Two-way: "Apigee Connect … TCP/443 TLS … **Therefore, you do not need to configure your firewall
for inbound connectivity.**"

Firewall guidance, verbatim: "You should not allow external connections for specific IP addresses
associated with `*.googleapis.com`. The IP addresses can change since the domain currently resolves
to multiple addresses."

## 2.8 Ingress exposure and scaling

### "Expose the Apigee ingress gateway" — <https://cloud.google.com/apigee/docs/hybrid/v1.17/install-expose-apigee-ingress> (HTTP 200, 17055 bytes)

- "Create a custom Kubernetes service for each Apigee ingress gateway (recommended)" and "For
  production environments, Apigee recommends you create a custom Kubernetes service for each ingress
  gateway."
- Required pod selector labels, quoted: `app`, `ingress_name`, `org`, with `app: apigee-ingressgateway
  #required` and `type: LoadBalancer`.
- "`INGRESS_NAME` is the name of this Apigee ingress gateway. It must match the name you provided
  for `ingressGateways.name` in your `overrides.yaml` file."
- Commands, verbatim: `kubectl get svc -n APIGEE_NAMESPACE -l app=apigee-ingressgateway`,
  `kubectl apply -f SERVICE_FILENAME.yaml`, `kubectl get svc -n APIGEE_NAMESPACE SERVICE_NAME`.
- Sample output line, verbatim:
  `apigee-ingressgateway-prod-hybrid-37a39bd   LoadBalancer   192.0.2.123   233.252.0.123
  15021:32049/TCP,80:31624/TCP,443:30723/TCP   16h`
- "Disable the loadbalancer for the default Apigee ingress gateway service: 1. Update the
  `ingressGateways[].svcType` property to `ClusterIP` in your overrides file".
- Note: "This service will be deleted when the ingress deployment is deleted (when the ingress
  gateway is removed from the overrides file)."

### "Scale and autoscale runtime services" — <https://cloud.google.com/apigee/docs/hybrid/v1.17/scale-and-autoscale> (HTTP 200, 21040 bytes)

- "Cloud Service Mesh uses Horizontal Pod Autoscaling (HPAs)."
- Patching maxReplicas, verbatim: "use the `kubernetes patch` command to change the `maxReplicas`
  property for the `runtime` component" with
  `--patch "$(echo -e "spec:\n  components:\n    $COMPONENT:\n      autoScaler:\n        maxReplicas: $MAX_REPLICAS\n        minReplicas: $MIN_REPLICAS")"`.
- Important limit, verbatim: "The Kubernetes Horizontal Pod Autoscaler (HPA) API, uses the
  `hpaBehavior` field to configure the scale-up and scale-down behaviors of the target service.
  **Metrics-based scaling is not available for any other components in a hybrid deployment.**"
- A built-in troubleshooting section exists: "### HPA shows `unknown` for metrics values" with
  `kubectl describe hpa HPA_NAME`.

## 2.9 Ways hybrid differs from Apigee X that change a support answer

1. **KVM entries do not travel in the contract.** Contract carries "Key Value Map (KVM) names";
   entries live in Cassandra and are reached through MART. An answer that says "the KVM propagates
   with the deployment" is wrong for hybrid.
2. **Deploy-time behaviour has a Synchronizer and a Watcher in the path.** Deployment status is
   reported by the Watcher polling Message Processors and Ingress (2.1) and the contract is pulled
   by the Synchronizer (2.4). There are at least four separable questions: revision saved,
   Synchronizer pulled the contract, MP applied the contract (`Switched to newer version N` in the
   pod log), Watcher reported status. A "deployment didn't work" ticket on hybrid cannot be answered
   by checking the Management API alone.
3. **There is an explicit, documented permission step that must not be skipped**:
   `organizations/YOUR_ORG_NAME:setSyncAuthorization` with an **Apigee Synchronizer Manager** role.
4. **Ingress access logs are not in the Apigee log stream** — they are in Cloud Service Mesh.
5. **Logging default differs by platform**: on by default on GKE/GKE-on-prem, off by default on AKS
   (`logger.enabled`). "We have no logs" is a configuration question before it is a bug question.
6. **Logs and metrics are documented as lossy**; analytics and deployment status are not (2.4).
7. **One environment per app is an antipattern on hybrid**, with three documented reasons
   (boot time, coupled scaling, noisy neighbour) that do not exist on X (2.3).
8. **Ingress routes by the `Host` header**, so a client that does not set `Host` produces a routing
   failure rather than a proxy failure (2.3).
9. **Multiple orgs in one namespace is a supported but hazardous topology** (F-05), and the
   mitigation is a unique `apigeeChainingGateway.name`.
10. **Redis exists in hybrid specifically for SpikeArrest `effectiveCount`** (2.1). A SpikeArrest
    design that assumes per-MP counters is wrong on hybrid.
11. **No version skipping on upgrade, and mixed versions break Cassandra backup/restore** (2.6).
    Upgrading to 1.17 "may require downtime" and triggers a rolling restart of all deployments.
12. **Hybrid minimums are hardware, not just policy**: 2 clusters for production, Cassandra p99
    under 100 ms, 1 Gbps per instance, 2000 IOPS, NTP across all regions (2.2). Performance tickets
    on hybrid frequently have an infrastructure answer, not a proxy answer.
13. **Hybrid does not validate the target certificate by default** on 1.10.2/1.10.3 (F-18), and
    1.10.3-hotfix.1 changed that. State the version.

### A claim in the existing scenarios file that I could NOT verify

`scenarios/medium.md` MED-07 asserts that "Hybrid validates shared-flow dependencies at deployment
time" while "Apigee resolves the reference when the request runs", and presents that as a documented
product difference. I fetched
<https://cloud.google.com/apigee/docs/api-platform/fundamentals/shared-flows> (HTTP 200, 15185
bytes) and it does not support that claim. What it says, verbatim: "*This page applies to **Apigee**
and **Apigee hybrid**.*" and "**Deploy the shared flow** to the environment before deploying proxies
or shared flows that will consume it." One instruction, both products, no difference in *when* the
dependency is checked. The only product-scoped artefact I found is the fault code
`flow.SharedFlowNotFound`, which is a runtime fault, not a deployment error, and which the skill's
own `error-codes.md` lists. MED-07's ordering advice ("deploy the shared flow first") is sound; its
stated mechanism is not sourced. Recommend rewording before MED-07 is used for evaluation.

---

## PART 3 — MISDIAGNOSED CAUSES

The cases where the first plausible explanation is wrong. Ordered by how badly an agent trained on
the obvious answer would fail.

## M-1. "The runtime logs stopped, so the runtime must be broken" → the Logger DaemonSet matches zero nodes

F-01 / issue 543171828. The obvious reading of "no logs after our upgrade" is that the Message
Processors died, hung, or cannot write. In fact the MPs are fine and the request path is
unaffected; a **fix** to node-selector handling in the `apigee-telemetry` chart made a pre-existing
`logger.nodeSelector` default start taking effect, so the DaemonSet stopped matching nodes.
Discriminator: `kubectl get daemonset apigee-logger -n apigee` reports "a desired count of `0`".
Trajectories that go wrong:

- Escalate as a runtime outage. The API is serving traffic the whole time.
- Delete and recreate the Logger DaemonSet. The default selector returns.
- Only check "is `logger.enabled` true" and stop. The bug only affects deployments with
  `logger.enabled: true`, but the selector is the cause, not the flag.

## M-2. "The token request is missing required parameters" → the deployment's base path is wrong

G-01 / api-platform-samples#7. The error cascade
`The request is missing a required parameter : response_type` →
`... : client_id` → `Invalid redirection uri http://joe.app/login?scope=READ&state=foobar&code=n9BZ8TiX`
reads unambiguously as a malformed token request. A contributor proposed adding `response_type=code`
and `client_id`; the reporter correctly noted those belong to the *authorize* request. The real
cause, verbatim: "There is a notion of deployment basepath apart from the proxy basepath… Just
un-deploying your proxy and deploying again through API made it to work." The token request was
being served by the wrong flow because the request was not landing where it was supposed to.
This is the general shape: **an OAuth error that names a request parameter can be a routing error.**
Agent must check where the request actually landed before concluding anything about the client.

## M-3. "The Maven deploy failed, so the deployment did not happen" → the deployment succeeded and the *activation check* timed out

G-02 / apigee-deploy-maven-plugin#213. `Deployment failed: Bundle did not activate within expected
time. Please check deployment status manually before trying again` is a tool-authored message built
on `Thread.sleep(10L)`. The reporter was certain the delay setting was the cause; the maintainer
showed it was not ("the delay is included only to upload the bundle but not for checking the
deployment"), and that the check only runs when the response state is not `deployed`. The decisive
evidence was not a log at all: "Yes Management API works well directly but it took around 30 secs
to deploy." So the deployment was fine and slow, and the tool conflated "not yet loaded" with
"failed". Resolution was **closure for inactivity**, not a fix — an agent told "this is resolved"
here would be repeating a falsehood.

## M-4. "Malformed request syntax, my CLI flags are wrong" → a `FAILED_PRECONDITION` from the API

G-06 / apigeecli#473. The API returned
`"status": "FAILED_PRECONDITION", "message": "generic::failed_precondition: revision
organizations/.../revisions/3 is currently deployed in default-dev"`, and the CLI printed
`Error: Bad Request - malformed request syntax` plus its usage block. The user had to argue,
correctly, that the usage block was the problem: "in this issue, the problem is not the fact that
there was an error, but the fact that the resulting error message was misleading. misleading in the
sense that it attributes the failure to the wrong cause." Cause: you cannot delete a deployed proxy;
`apis undeploy` first. **Generalisable lesson: when a tool's error text names a different layer
than the one that failed, trust the payload, not the tool's prose.**

## M-5. "My `ExtractVariables` security check is in place, so the request was blocked" → the two layers parse duplicate JSON keys differently

F-02 / issue 534420582. ExtractVariables + JSONPath is *last-wins*; backends accepting proto3 JSON
*merge* repeated keys. So the policy never sees the content the backend acts on. Verbatim: "an
attacker can hide malicious content in a duplicate key that the Apigee policy does not see but the
backend still processes." The obvious diagnosis — "the security policy is misconfigured" or "it is a
backend bug" — is wrong in both directions. The agent must ask what the *backend's* JSON parser
does with duplicate keys, not what the policy is configured with.

## M-6. "Rate limiting is returning 502s, so the backend or the load balancer is broken" → two SpikeArrest policies in one bundle

F-14 / issue 207719377. Verbatim: "If there is more than one SpikeArrest policy in a bundle, `502`
errors will occur." A 502 has no rate-limit signature at all. Fault-code matching will not catch it
because it is not a policy fault. Second-order trap in the same area: changing a SpikeArrest rate
at runtime "may not reflect immediately" for a key under continuous traffic (issue 209097822), which
looks exactly like the limit not being enforced at all.

## M-7. "The timeout change was lost in deployment" → the deployment succeeded and the runtime pods did not pick up `io.timeout.millis`

F-08 / issue 471125841, plus 246774745. Verbatim: "The updated value of `io.timeout.millis` is
intermittently not honored for API requests. This happens when multiple servers are used under
`<LoadBalancer>` in the TargetEndpoint." Two wrong first answers: "the deployment failed" (it did
not) and "the backend is ignoring the timeout" (it is not). The condition depends on the presence of
a `<LoadBalancer>`, which nothing in the symptom suggests. Related: with multiple dynamic targets,
"only one `io.timeout.millis` value is honored" — so per-flow timeouts silently collapse to one.

## M-8. "My client is sending a malformed URI" → a Netty version regression inside Apigee

F-10 / issue 480997525. `400` with `The URI contain illegal characters`, introduced by "a Netty
upgrade to 4.1.129.Final" in `Apigee 1-17-0-apigee-1`, tracked upstream at netty/netty#16020. The
first three hypotheses a support agent reaches for — client percent-encoding, proxy config, backend
rejection — are all wrong. Version-pinned, upstream-tracked, and fixed in `1-17-0-apigee-2`.

## M-9. "Our OAuth token is being rejected" → the request carried two `authorization` headers

F-11 / issue 458417250. The ingress gateway does not concatenate multiple `authorization` headers,
so the MP returns `500` with `"Duplicate Header "authorization""`. Everything upstream of that reads
as an OAuth failure. The documented workaround on the register is itself a trap — `-H 'authorization:
a, b'` satisfies the ingress but produces a meaningless token, so "the workaround worked" and "auth
works" are different claims.

## M-10. "API Products, Apps and Developers have disappeared after the 1.16 migration" → a MART image regression, gated on WIF + forward proxy

F-07 / issue 479872706. "environments using Workload Identity Federation (WIF) in conjunction with
an HTTP Forward Proxy may fail to load management entities (API Products, Apps, Developers) due to a
credential casting regression in MART." The obvious reading is data loss or a bad import. The
gating condition is a *conjunction of two features*, so a support agent checking only "are you using
WIF?" or only "are you using a proxy?" will wrongly rule it out. Companion 479040521 in the same
release: `apigee-operator-guardrails-sa` is simply never created on AKS/EKS with Federated WIF.

## M-11. "The outage is random" → cert-manager silently armed a CA key rotation, and only on upgraded clusters

F-09 / issue 465834046. cert-manager ≥1.18 changed the default of `spec.privateKey.rotationPolicy`
from `Never` to `Always`. Fresh hybrid installs already have `Never`; **upgraded** clusters do not.
So a routine cert-manager upgrade converts a future, unpredictable CA rotation of `apigee-ca` into
an outage, on some clusters and not others at the same hybrid version. Nothing about the symptom
points at cert-manager, and the two-cluster topology means the outage may hit one cluster and not
the other. This is the single best "first explanation is wrong" case in the whole set.

## M-12. "Our deployment succeeded" → in one documented case there was never an error to return

F-15 / issue 300660653. "Deploying proxies with the same path to multiple environments that are
attached to the same instance and environment group is not allowed and should return a warning
message about a base path conflict. Instead, no error is shown and the deployments appear to
succeed." The prescribed response is post-deployment verification, not redeployment. An agent whose
default move is "the deploy succeeded so look elsewhere" would look elsewhere forever; an agent
whose default move is "redeploy" would produce a new revision and hide the conflict.

## M-13. "The controller is throwing errors, something is broken" → they are documented as harmless

F-13 / issue 415061771, status **OPEN**. `Object has been modified` is described as "a harmless
side-effect of Apigee and Apigee Hybrid built-in safety mechanisms", because "these are purely
internal administrative updates and do not change how APIs actually process traffic, the services
should remain stable and completely unaffected." The correct answer is short and the failure mode is
investigating for an hour. Note the entry is still listed, which is exactly why an agent must read
the body rather than pattern-match on "OPEN" = broken.

## M-14. "The image tag doesn't exist, so the 1.16.3 release is broken" → only the manual pull path is broken

F-04 / issue 515424331. Verbatim: "Upgrades performed through the Apigee hybrid Helm charts were not
affected, because the charts reference the correct image digests directly." Same version number, two
different upgrade behaviours. An agent that hears "the 1.16.3 upgrade failed" and concludes the
release is unusable will send a customer off a perfectly good upgrade path.

## M-15. "Apigee lints are wrong, the tool contradicts itself" → correct, and it cannot see the TargetServer

G-05 / apigeelint#526. TD012 says add `SSLInfo` to `HTTPTargetConnection`; TD006 says do not put it
there. Maintainer, verbatim: "The design of the plugin is sort of broken - it assumes that if there
is an SSLInfo under HTTPTargetConnection, then it is NOT present in the TargetServer. But that is
not a valid assumption." The structural reason: apigeelint analyses the proxy bundle, and
TargetServers are not in the bundle. So "follow the linter" and "follow the linter" give opposite
results, and the popular shorthand "always add SSLInfo to HTTPTargetConnection" is wrong whenever a
`<LoadBalancer>` with TargetServers is in play. Fixed in v2.67.0 by demoting TD006 and narrowing
TD012 to the no-LoadBalancer case.

## M-16. A maintainer was wrong and the reporter proved it

G-04 / apigeelint#154, included because it is the only case in this set where the *first answer from
the expert side* was the wrong one. The reporter claimed Apigee rewrites policy filenames on export.
`DinoChiesa` rejected it: "my observations do not align with that… I think that is a bug in Apigee
(and probably a serious one)." The reporter then demonstrated it, and the maintainer reversed:
"Thanks karsten-wagner, for weighing in. I wasn't aware of that subtlety." Fix merged as PR #191
on 2020-09-28, reporter confirmed. Evaluation value: a skill must let a specific, reproducible user
observation override a confident maintainer assertion, and must ask for the reproduction (curl
commands, upload/download round-trip) rather than dismissing the claim.

## M-17. The refusal cases

Two "obvious explanation is wrong" answers are the wrong kind of wrong and worth naming:

- **apigee-api-catalog-drupal#46 (G-09)**: "SmartDocs and Swagger UI send the wrong Authorization
  scheme, so the bug is downstream." The wrong scheme originates in Apigee's own token response. The
  official remedy is a documentation section, not a fix — so "upgrade to fix it" is wrong too.
- **apigeetool-node#6 (G-08)**: `UNABLE_TO_VERIFY_LEAF_SIGNATURE` against an on-prem endpoint. The
  `insecure` flag is treated as the universal escape hatch, and the thread itself shows it does not
  cover the neighbouring case (`unable to verify the first certificate` — an incomplete chain, not
  an untrusted root). Still open. Treat "TLS verification failed" as at least three root causes.

---

## PART 4 — PROPOSED SCENARIOS (MED-16 to MED-22)

Format copied from `scenarios/medium.md`. Every fault code below exists in
`.agents/skills/apigee-support-core/references/error-codes.md` (checked). Every URL was fetched
this session with HTTP 200.

---

### MED-16. The OAuth error names a missing parameter, but the token request never reached the token endpoint

#### Scenario metadata

- ID: MED-16
- Difficulty: medium
- Primary topic: OAuth 2.0 authorization code grant
- Secondary topics: base path routing, deployment records, fault handling
- Product: Apigee
- Origin: reported real-world case (apigee/api-platform-samples#7)
- Versions: checked 2026-10-11
- Evaluation objectives: resist treating an OAuth error string as proof of a client
  configuration defect. The agent must establish where the request actually landed before
  concluding anything about the client.
- Skills expected: apigee-support-core

#### Initial support ticket

> Our authorization code flow is broken. The token endpoint returns
> `{"ErrorCode" : "invalid_request", "Error" :"The request is missing a required parameter :
> response_type"}`. We are calling the token endpoint, not the authorize endpoint, so
> `response_type` should not apply. Please confirm our proxy is misconfigured.

#### Initial evidence

The client POSTs to the documented token path with `grant_type=authorization_code`, `code`, and
`redirect_uri`. The proxy bundle is the vendor's own OAuth sample. A second client on the same
environment succeeds with a different `redirect_uri`.

#### Expected investigation

The agent should notice that the first three errors in this class form a cascade and that the
cascade is itself the clue. The documented errors are listed in the OAuthV2 policy reference:
`The request is missing a required parameter : response_type`,
`The request is missing a required parameter : client_id`, and
`Required param : redirect_uri`. Seeing `response_type` demanded on a token request means the
request reached the wrong endpoint, not that a parameter is missing.

#### Diagnostic evidence

A trace of the failing request shows the request entering the flow whose `<Condition>` is
`proxy.pathsuffix == "/oauth/authorizationcode"`, not the `"/oauth/accesstoken"` flow. The proxy
was deployed with a deployment base path that did not match the base path in the bundle, so the
request path resolved into the wrong flow.

#### Ground-truth resolution

Nothing is wrong with the client and nothing is wrong with the OAuth policy. The token request is
being served by the authorization-code flow because of how the proxy was deployed. Every fix
proposed against the error text — adding `response_type`, adding `client_id`, "fixing"
`redirect_uri` — makes the error text change without making the flow work.

#### Correct remediation

Undeploy the proxy and redeploy it so the deployment base path matches the proxy base path in the
bundle, then confirm each flow's `<Condition>` is distinct.

Treat this as a deployment-record change, not a bundle change. Do not modify the sample policies
to satisfy the error messages.

#### Verification

Call the token endpoint with a fresh authorization code and confirm an access token is returned.
Then call the authorize endpoint and confirm it returns a code. Confirm both, because a fix that
makes one work can leave the other broken.

#### Common incorrect answers

Adding `response_type=code` to the token request. That parameter belongs to the authorize request
and this is the most commonly repeated wrong answer in this area.

Telling the client to fix its `redirect_uri`. The registered callback URL is correct.

Rewriting the OAuth policy to generate the error manually. That hides the routing defect.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Adds response_type | Suspects routing | Identifies wrong-flow dispatch from deployment base path |
| Diagnostic method | Edits client request | Reads error text | Reads error text as a routing signal and checks flow conditions |
| Handling of competing causes | Accepts the literal error | Hedges | Separates client, policy, and routing explicitly |
| Quality of next step | Changes parameters | Redeploys blindly | Redeploys with the base path matched, then verifies both flows |

#### Critical failures: recommending adding `response_type` or `client_id` to the token request

asserting the OAuth policy is misconfigured.

#### References

- OAuthV2 policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>
- Real report of this failure:
  <https://github.com/apigee/api-platform-samples/issues/7>

---

### MED-17. The deploy tool says "Deployment failed" and the Management API says the deployment worked

#### Scenario metadata

- ID: MED-17
- Difficulty: medium
- Primary topic: deployment state
- Secondary topics: tool automation, shared flows, management API
- Product: Apigee
- Origin: reported real-world case (apigee/apigee-deploy-maven-plugin#213)
- Versions: checked 2026-10-11
- Evaluation objectives: separate "the deployment was accepted" from "the revision is serving".
  This is the case where the failure message is authored by the tool, not by Apigee, and the tool's
  cause was disputed and the dispute was never resolved.
- Skills expected: apigee-support-core

#### Initial support ticket

> Our CI deploys shared flows and proxies with the Apigee deploy Maven plugin. Intermittently the
> build fails with `Deployment failed: Bundle did not activate within expected time. Please check
> deployment status manually before trying again`. We want the plugin's hardcoded 10 second wait to
> be made configurable. Can you confirm that is the bug?

#### Initial evidence

`apigee.override.delay` is set to 30 in the POM. Direct calls to the Management API import and
deploy succeed. Deployments that take longer than the plugin's internal check interval fail; faster
ones pass. Nothing else in the pipeline fails.

#### Expected investigation

The agent should establish that the message is tool-generated. The string
`Deployment failed: Bundle did not activate within expected time. Please check deployment status
manually before trying again` is thrown by the plugin, not returned by Apigee, so it is not
evidence about the state of the deployment.

The agent should then separate three questions: was the bundle accepted, is a revision deployed, and
is the deployed revision the one just uploaded.

#### Diagnostic evidence

Running the same deployment directly against the Management API succeeds and takes around 30
seconds. The plugin's log shows `Waiting to assert bundle activation.....` followed by
`Deployment failed to activate`. Querying the deployment afterwards shows the new revision present
and serving.

#### Ground-truth resolution

The deployment succeeded. The plugin waits a fixed interval, then makes a follow-up call to read
deployment state, and treats a not-yet-set deployed revision as a failure. The delay property is
not the cause; in the original thread the reporter asserted it was, and the maintainer's position
was the opposite: the delay is used for the upload, not for the activation check.

The honest answer stops there. It is not established why the deployments take 30 seconds. The
maintainer's own hypothesis was environmental slowness, and the thread was closed for inactivity
without a fix.

#### Correct remediation

Increase the tool's activation check interval, or run the deployment with a tool that polls
deployment state instead of sampling it once. Both are tooling changes and belong to the customer's
CI, not to Apigee.

Establish the real deployment time in this environment before changing anything, since that number
is the actual unknown.

#### Verification

Deploy a proxy and a shared flow, and confirm both revisions are serving. Then confirm the build
passes on the deployments that previously passed, so the change has not narrowed what deploys.

#### Common incorrect answers

Increasing `apigee.override.delay` to 60 and declaring victory. The delay is not what the check
reads. In the source thread the reporter raised exactly this and was told it would not help.

Blaming the Management API or raising a platform defect. The deployment is verifiably fine.

Treating "the tool said failed" as proof the proxy is not deployed. Check the deployment directly.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Attributes to the delay | Identifies tool-side check | Separates acceptance, revision, and serving |
| Diagnostic method | Raises the delay | Reads the log | Runs the same deploy via the Management API |
| Handling of uncertainty | Asserts a cause | Hedges | States that the 30-second deployment time is unexplained |
| Quality of next step | Increases delay | Retries | Changes the check interval or polls deployment state |

#### Critical failures: asserting the delay setting is the root cause; opening a platform defect

against Apigee for a tool-generated message.

#### References

- Real report, with the disputed diagnosis and the closure for inactivity:
  <https://github.com/apigee/apigee-deploy-maven-plugin/issues/213>
- Deploy an API proxy revision:
  <https://cloud.google.com/apigee/docs/api-platform/deploy/ui-deploy-overview>

---

### MED-18. Every API product, app and developer fails to load after a hybrid upgrade

#### Scenario metadata

- ID: MED-18
- Difficulty: medium
- Primary topic: hybrid runtime components
- Secondary topics: MART, workload identity federation, forward proxy, upgrade
- Product: hybrid
- Origin: reported real-world case (official known issue 479872706)
- Versions: checked 2026-10-11
- Evaluation objectives: the obvious reading is data loss or a failed import. The documented cause is
  a MART image regression gated on the conjunction of two optional features, so checking only one
  of them leads to a confident and wrong ruling-out.
- Skills expected: apigee-support-core, apigee-opdk-troubleshooter

#### Initial support ticket

> We upgraded our hybrid install to 1.16.0 over the weekend. Since then the UI and API cannot load
> API Products, developer apps or developers at all. Nothing was deleted. Proxy traffic is
> unaffected. Is our data gone?

#### Initial evidence

The UI reports a failure to load org entities. Proxy traffic and deployed revisions work. The
runtime pods are running. Management API calls that read proxies succeed; calls that read org
entities fail.

#### Expected investigation

The agent should establish the product and the version first, then check whether the failure is
scoped to MART rather than to the whole control plane. Everything works except the components that
reach the runtime datastore.

#### Diagnostic evidence

The MART component is on image tag `1.16.0`, not `1.16.0-hotfix.1`. The installation has both
Workload Identity Federation enabled and an HTTP forward proxy configured. A second hybrid
installation on the same `1.16.0` that uses neither combination loads entities normally.

#### Ground-truth resolution

No data is lost. The documented cause is a credential casting regression in MART, affecting
environments that use Workload Identity Federation together with an HTTP forward proxy. Both
conditions are required. The fix is to move the operator and MART images to
`1.16.0-hotfix.1`.

The trap is the conjunction. An agent that checks only "are you using WIF?" or only "do you have a
forward proxy?" will correctly observe one is absent and wrongly close the case.

#### Correct remediation

Set the `ao.image.tag` and `mart.image.tag` properties to `1.16.0-hotfix.1` in `overrides.yaml`, or
perform the documented hotfix upgrade.

Then check the neighbouring 1.16.0 defect: on AKS and EKS with Federated Workload Identity, the
Kubernetes ServiceAccount `apigee-operator-guardrails-sa` is not created, because the chart template
omits `(.Values.gcp.federatedWorkloadIdentity.enabled)` from its initial condition.

#### Verification

Confirm API Products, apps and developers load. Then confirm proxy deployment still works, because
the fix changes the operator image, not just MART.

#### Common incorrect answers

Telling the customer their data is lost, or that they must re-import. Both are wrong and alarming.

Re-importing org entities. They are in Cassandra; the import is not the problem and a re-import
risks real damage.

Checking only Workload Identity Federation, or only the forward proxy. Either alone rules the issue
out incorrectly.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Product and version | Gives Apigee X advice | Identifies hybrid | Names the 1.16.0 MART defect |
| Technical correctness | Says data lost | Suspects MART | Names the credential casting regression |
| Diagnostic method | Re-imports | Checks MART | Checks MART version and both WIF and proxy |
| Handling of uncertainty | Asserts | Hedges | States the conjunction condition explicitly |

#### Critical failures: telling a customer their data is lost; ruling the issue out by checking

only one of the two gating features.

#### References

- Known issues register (entry 479872706 and 479040521):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- MART and runtime service configuration:
  <https://cloud.google.com/apigee/docs/hybrid/v1.17/service-config>

---

### MED-19. Runtime logs stopped after a successful upgrade

#### Scenario metadata

- ID: MED-19
- Difficulty: medium
- Primary topic: hybrid logging
- Secondary topics: Kubernetes scheduling, upgrades, DaemonSets
- Product: hybrid
- Origin: reported real-world case (official known issue 543171828)
- Versions: checked 2026-10-11
- Evaluation objectives: the symptom reads as a runtime outage. The correct move is one command
  that distinguishes "runtime broken" from "log collector unscheduled". The root cause is a bug fix
  that turned into a regression, which is the counter-intuitive part.
- Skills expected: apigee-support-core, apigee-opdk-troubleshooter

#### Initial support ticket

> We upgraded hybrid to 1.16.8 yesterday and we now have no Apigee runtime logs at all. Cloud
> Logging shows nothing from our message processors. Please escalate, we are blind.

#### Initial evidence

API traffic is normal and proxies serve correctly. Since the upgrade, no hybrid runtime log lines
appear in Logs Explorer. The prior release produced logs without configuration changes.

#### Expected investigation

One command separates the two hypotheses immediately:

```terminal
kubectl get daemonset apigee-logger -n apigee
```

If the desired count is 0, the runtime is healthy and the log collector is simply not scheduled.
The agent should not start a runtime investigation.

#### Diagnostic evidence

`kubectl get daemonset apigee-logger -n apigee` reports a desired count of `0` and no logger pods
exist. The overrides file sets `logger.enabled: true`. The `apigee-telemetry` chart's default
`logger.nodeSelector` is `apigee.cloud.google.com/apigee-logger-enabled: "true"`, and no nodes carry
that label.

#### Ground-truth resolution

The runtime is fine. Earlier releases ignored component-level node selectors, so the logger was
scheduled onto the Apigee node pools despite the default selector matching nothing. The affected
release honours component-level node selectors correctly, so the long-standing default now takes
effect and the DaemonSet matches no nodes.

The counter-intuitive step is accepting that a bug fix caused this. "The upgrade made it worse" is
the correct reading here, not a contradiction.

#### Correct remediation

Either clear the default selector in `overrides.yaml`:

```yaml
logger:
  enabled: true
  nodeSelector:
    key: ""
    value: ""
```

or label the intended nodes and keep the default:

```terminal
kubectl label nodes NODE_NAME apigee.cloud.google.com/apigee-logger-enabled=true
```

Then upgrade the `apigee-telemetry` chart. The defect is fixed in hybrid 1.16.9.

#### Verification

Confirm logger pods exist and the desired count matches the labelled node count. Then confirm log
lines appear in Logs Explorer for the `Kubernetes Container` resource type.

#### Common incorrect answers

Escalating as a runtime outage. Traffic is unaffected and the runtime is healthy.

Deleting and recreating the `apigee-logger` DaemonSet. The default node selector returns and the
DaemonSet matches no nodes again.

Checking only whether `logger.enabled` is set. The flag being true is the precondition, not the
cause. Also note the platform dependency: logging is on by default on GKE and GKE on-prem, and off
by default on AKS.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Calls it a runtime outage | Suspects the logger | Identifies the node selector as the cause |
| Diagnostic method | Escalates | Inspects pods | Runs kubectl get daemonset first |
| Product and version | Generic | Names hybrid | Names the affected hybrid versions and the fix version |
| Quality of next step | Restarts pods | Deletes the DaemonSet | Clears the selector or labels nodes |

#### Critical failures: escalating as a runtime outage; recreating the DaemonSet; recommending a

runtime restart, which does not address scheduling.

#### References

- Known issues register (entry 543171828):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Logging in hybrid:
  <https://cloud.google.com/apigee/docs/hybrid/v1.17/logging>
- View logs:
  <https://cloud.google.com/apigee/docs/hybrid/v1.17/logging-view>

---

### MED-20. A deployed timeout change is not taking effect on some requests only

#### Scenario metadata

- ID: MED-20
- Difficulty: medium
- Primary topic: timeouts and LoadBalancer targets
- Secondary topics: deployment state, hybrid runtime pods, latency
- Product: hybrid
- Origin: reported real-world case (official known issues 471125841 and 246774745)
- Versions: checked 2026-10-11
- Evaluation objectives: two competing wrong answers dominate here, "the deployment failed" and "the
  backend ignores the timeout". Both are wrong. The agent must notice that the condition depends on
  the presence of a `<LoadBalancer>`, which the symptom does not reveal.
- Skills expected: apigee-support-core

#### Initial support ticket

> We raised `io.timeout.millis` from 5000 to 15000 on our search proxy and redeployed. Some
> requests still time out at 5 seconds as if the old value is in force. Others behave as expected.
> The deployment reported success.

#### Initial evidence

The TargetEndpoint uses a `<LoadBalancer>` with more than one target server. Deployment succeeded.
Behaviour is inconsistent across requests. The upstream service itself is healthy and responds
within 4 seconds.

#### Expected investigation

The agent should separate the three states that "the deploy succeeded" collapses: the revision was
saved, the runtime accepted the contract, and each Message Processor applied the new value. In
hybrid this is directly observable in the pod log via the contract version lines.

#### Diagnostic evidence

The TargetEndpoint contains a `<LoadBalancer>` with multiple servers. Runtime pod logs show the
contract version advancing. Requests that still time out at 5 seconds correlate with a Message
Processor that has not applied the new contract value.

#### Ground-truth resolution

The deployment succeeded and the revision is deployed. The documented defect is that an updated
`io.timeout.millis` value is intermittently not honoured when multiple servers are used under
`<LoadBalancer>` in the TargetEndpoint. The old value survives on some Message Processors, which is
why only some requests behave as deployed.

A separate documented defect compounds it: when two or more flows set `io.timeout.millis` for the
same target host, only one value is honoured.

#### Correct remediation

Restart the `apigee-runtime` pods one by one so the change propagates, rather than all at once, to
keep serving traffic. This is disruptive and needs authorization.

Separately, if several flows set different timeouts against the same target host, consolidate them,
because the per-flow values will collapse to one regardless.

#### Verification

Confirm requests no longer time out at the old value. Then exercise every flow that sets a timeout
for that target host, because the collapse to a single value will only show up there.

#### Common incorrect answers

Redeploying. The revision is already deployed and the redeploy changes nothing.

Raising the timeout further, or blaming the backend. The backend responds in 4 seconds.

Rolling every runtime pod at once. That turns a partial problem into a full outage.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Redeploys | Suspects propagation | Identifies LoadBalancer-conditioned timeout defect |
| Diagnostic method | Restarts everything | Reads deployment state | Checks TargetEndpoint for LoadBalancer and per-flow timeouts |
| Diagnostic method | Raises the timeout | Blames the backend | Measures the target independently |
| Quality of next step | Redeploy | Rolling restart | Rolling restart plus consolidating conflicting timeouts |

#### Critical failures: recommending a redeploy as the fix; blaming the backend for timeouts at a

value the proxy is no longer configured to use.

#### References

- Known issues register (entries 471125841 and 246774745):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- API proxy configuration reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>

---

### MED-21. The linter and the security team want opposite things

#### Scenario metadata

- ID: MED-21
- Difficulty: medium
- Primary topic: TLS configuration and load balancing
- Secondary topics: target servers, tooling, conflicting guidance
- Product: Apigee or hybrid
- Origin: reported real-world case (apigee/apigeelint#526)
- Versions: checked 2026-10-11
- Evaluation objectives: the customer has two trusted authorities giving contradictory instructions.
  The agent must identify the structural reason rather than picking a side, and must recognise that
  the tool cannot see the TargetServer at all.
- Skills expected: apigee-support-core, references/security.md

#### Initial support ticket

> Our API security scan says we must declare TLS in the target endpoint. Our bundle linter says we
  must not. We already define the TLS settings on the target server. What do we change?

#### Initial evidence

The TargetEndpoint uses a `<LoadBalancer>` referencing target servers that carry the TLS settings
in the environment's target server configuration. The linter emits
`TargetEndpoint HTTPTargetConnection should have exactly one SSLInfo` when TLS is absent from the
proxy, and `When using a LoadBalancer, the SSLInfo should be configured in the TargetServer, not
under HTTPTargetConnection` when it is present. The scan emits its requirement independently.

#### Expected investigation

The agent should notice that the two warnings are mutually exclusive, so no configuration can
satisfy both, and that this is a property of the tool's reach rather than of the customer's config.
The linter analyses the proxy bundle. Target servers are not in the bundle, so the linter cannot see
the TLS configuration and assumes its absence from the proxy means its absence everywhere.

#### Diagnostic evidence

The target server definition carries its own TLS settings. The proxy bundle contains no reference
to them, only a `<Server name="...">` inside `<LoadBalancer>`.

#### Ground-truth resolution

TLS belongs on the target server when using a `<LoadBalancer>`. The linter cannot verify this,
because TargetServers are environment configuration and are not part of the proxy it scans.

The popular shorthand "always add SSLInfo to the TargetEndpoint" is wrong for the LoadBalancer case,
and following it produces the second warning. This was reported as an apigeelint defect; the
maintainer's stated fix was to demote TD006 and to narrow TD012 to fire only when there is no
LoadBalancer, shipped in v2.67.0.

#### Correct remediation

Keep TLS on the target server. If the installed linter predates v2.67.0, suppress the TD012 rule
for that proxy rather than restructuring the TargetEndpoint.

Separately, note the related MaxFailures trap from the same discussion: a single target server with
a non-zero `MaxFailures` and no HealthMonitor causes continuous failures until the proxy is
redeployed. The antipattern guidance is explicit on this point.

#### Verification

Lint the proxy on a version at or after v2.67.0 and confirm only one of the two TLS warnings can
appear. Then confirm the connection to the target server actually negotiates TLS with the expected
certificate.

#### Common incorrect answers

Adding SSLInfo to the TargetEndpoint to satisfy the first warning. It triggers the second warning and
misleads anyone reading the config later.

Adding SSLInfo to the TargetEndpoint because the security scan demands it, without checking whether
a LoadBalancer is in use. The rule differs by case and the agent should state which case applies.

Assuming one of the two authorities is simply wrong. Both are describing a real conflict created by
a tool that cannot see the target server.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Adds SSLInfo to TargetEndpoint | Names the contradiction | Explains the tool's limited reach |
| Diagnostic method | Picks a side | Checks both configs | Checks whether TargetServers are in the bundle at all |
| Handling of competing causes | Declares one wrong | Hedges | States both rules are reachable and why |
| Quality of next step | Adds config | Suppresses the rule | Keeps TLS on the target server and cites the fixed version |

#### Critical failures: adding `SSLInfo` to `HTTPTargetConnection` without establishing whether a

`<LoadBalancer>` is in use; telling the customer one of the two authorities is simply wrong.

#### References

- Real report of the contradictory warnings:
  <https://github.com/apigee/apigeelint/issues/526>
- MaxFailures antipattern:
  <https://cloud.google.com/apigee/docs/api-platform/antipatterns/load-balancing-maxfailures>
- API proxy configuration reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>

---

### MED-22. A routine cert-manager upgrade plants a future outage

#### Scenario metadata

- ID: MED-22
- Difficulty: medium
- Primary topic: TLS and certificate lifecycle in hybrid
- Secondary topics: upgrades, multi-cluster topology, disaster recovery
- Product: hybrid
- Origin: reported real-world case (official known issue 465834046)
- Versions: checked 2026-10-11
- Evaluation objectives: nothing in the symptom points at cert-manager, and the defect is scoped to
  upgraded clusters only, so two clusters on the same hybrid version behave differently. The agent
  must think about a future outage caused by a completed, successful change.
- Skills expected: apigee-support-core, apigee-opdk-troubleshooter, references/security.md

#### Initial support ticket

> We upgraded cert-manager on our hybrid clusters last week as part of routine maintenance. No
  issues since. We are seeing intermittent connection failures between hybrid runtime components on
  one cluster but not the other. Both are the same hybrid version. Where do we start?

#### Initial evidence

Two hybrid clusters, same hybrid version, same changes. One has intermittent component connection
failures; the other does not. Both were upgraded rather than installed fresh.

#### Expected investigation

The agent should compare the two clusters rather than reason about "the version", because the
documented defect does not apply uniformly. The question to ask is not "what version is
cert-manager" but "what is the rotation policy on the `apigee-ca` certificate".

#### Diagnostic evidence

```terminal
kubectl get certificate apigee-ca -n cert-manager -o yaml
```

On the failing cluster, `spec.privateKey.rotationPolicy` is unset or set to `Always`. On the healthy
cluster it is `Never`. Both clusters run cert-manager at or above 1.18.

#### Ground-truth resolution

cert-manager 1.18 changed the default of `Certificate.Spec.PrivateKey.rotationPolicy` from `Never`
to `Always`. Fresh hybrid installs already set `Never`; upgraded clusters keep whatever the older
cert-manager default was, so the new default takes effect on them only.

From this point the cluster will rotate the `apigee-ca` private key on cert-manager's schedule. The
documented consequence is blunt: "When this key is rotated for the `apigee-ca` certificate, it will
cause an outage."

So the current symptom and the upcoming outage share a cause, and that cause is a completed
maintenance change from a week ago, not anything happening now.

#### Correct remediation

Patch the certificate to `Never` before rotating anything further, then verify:

```terminal
kubectl patch Certificate \
  -n cert-manager \
  --type=json \
  -p='[{"op": "replace", "path": "/spec/privateKey/rotationPolicy", "value": "Never"}]' \
  apigee-ca
```

Alternative, per the documentation: do not upgrade cert-manager above 1.17.x.

The order matters and the documentation warns about it: perform these steps before upgrading
cert-manager, otherwise a rotation may already be triggered.

#### Verification

Confirm `rotationPolicy: Never` on `apigee-ca` with
`kubectl get certificate apigee-ca -n cert-manager -o yaml`. Then confirm the runtime components
are healthy. Separately, verify Cassandra backup and restore across the clusters, because mixed
hybrid versions cannot share backups.

#### Common incorrect answers

Restarting the affected pods to clear the connection failures. It masks the symptom until the next
rotation and destroys the evidence.

Comparing the two clusters only by hybrid version. The documented defect separates upgraded
clusters from fresh installs at the same version, so version alone cannot discriminate.

Rebuilding the `apigee-ca` certificate from scratch. That forces a rotation immediately, which is
the outcome being avoided.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Restarts pods | Inspects certificates | Identifies the rotationPolicy default change |
| Diagnostic method | Compares hybrid versions only | Compares the two clusters | Inspects apigee-ca rotationPolicy on both |
| Product and version | Gives Apigee X advice | Identifies hybrid | Names cert-manager 1.18 default and the fresh-vs-upgraded split |
| Quality of next step | Restarts | Rebuilds the CA | Patches rotationPolicy to Never before any further change |

#### Critical failures: recommending a CA rebuild or an immediate rotation; treating identical

hybrid versions as proof that both clusters behave the same way.

#### References

- Known issues register (entry 465834046):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Upgrading Apigee hybrid (cert-manager section):
  <https://cloud.google.com/apigee/docs/hybrid/v1.17/upgrade>
- Supported platforms and versions:
  <https://cloud.google.com/apigee/docs/hybrid/supported-platforms>

---

## Scenario provenance summary

| ID | Origin | Primary source verified this session |
| --- | --- | --- |
| MED-16 | reported real-world case | <https://github.com/apigee/api-platform-samples/issues/7> |
| MED-17 | reported real-world case | <https://github.com/apigee/apigee-deploy-maven-plugin/issues/213> |
| MED-18 | reported real-world case | known issue 479872706 |
| MED-19 | reported real-world case | known issue 543171828 |
| MED-20 | reported real-world case | known issues 471125841, 246774745 |
| MED-21 | reported real-world case | <https://github.com/apigee/apigeelint/issues/526> |
| MED-22 | reported real-world case | known issue 465834046 |

No synthetic scenarios were added; the real corpus was sufficient.
