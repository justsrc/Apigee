# Real-world Apigee engineering problems found on GitHub

Discovery pass: 2026-10-12. Purpose: seed an evaluation scenario library with cases whose
obvious first explanation is wrong.

Method: GitHub REST API (`gh api`, authenticated as a user). Every repo below was confirmed
`owner.type == "Organization"` via `GET /repos/{owner}/{repo}`. Issue bodies and full comment
threads were fetched, not read from search snippets.

Resolution status vocabulary used throughout, four distinct claims:
- CLOSED: issue state is closed. NOT a fix.
- PROPOSED: a fix suggested in a comment. NOT a fix.
- MERGED: a linked PR was merged. The strongest claim available on GitHub.
- CONFIRMED: the original reporter or another user said the fix worked.

Evidence levels: (a) official documentation, (b) maintainer statement, (c) reporter-confirmed
workaround, (d) unverified community claim.

---

## Case 1. apigeelint PO035 rejects a Quota policy that the runtime accepts

- URL: https://github.com/apigee/apigeelint/issues/443
- Repo: apigee/apigeelint, owner_type = Organization (confirmed via API)
- Problem: lint plugin PO035 treated `SyncIntervalInSeconds` and `SyncMessageCount` as
  mutually exclusive inside `<AsynchronousConfiguration>`, so a bundle that runs correctly on
  the gateway was rejected by the linter. Reporter (DinoChiesa, COLLABORATOR) verbatim:
  "The documentation for AsynchonousConfiguration states that people can use EITHER the
  SyncIntervalInSeconds or the SyncMessageCount. And that they are mutually exclusive. The doc
  does not state what happens if a configuration uses both." ... "I think it is valid to use both
  elements. And when you do, it means: 'Sync every N messages, or... M seconds, whichever comes
  first.'"
- Why the obvious first explanation is wrong: the lint failure looks exactly like a
  configuration error, so the instinct is to fix the bundle. The bundle is correct.
- Environment: apigeelint plugin PO035; any version containing the pre-#445 behaviour.
- Evidence for claimed cause: maintainer (COLLABORATOR) reading the runtime semantics, plus the
  official Quota policy reference. Evidence level (b), corroborated by (a).
- Resolution: MERGED. PR https://github.com/apigee/apigeelint/pull/445 "fix: PO035 allows both of
  Sync{IntervalInSeconds, MessageCount}", merged=true, merged_at 2024-05-16T17:31:09Z. Issue
  closed as completed. NOT reporter-confirmed on a live proxy.
- Still applies today: the fix merged in 2024-05; apigeelint has released since (latest tag
  v2.85.1, 2026-07-03), so current apigeelint should not raise it. The underlying documentation
  ambiguity about mutual exclusivity is the thing to re-check, not the plugin.

## Case 2. apigeelint crashes on a Quota policy attached to a FaultRule

- URL: https://github.com/apigee/apigeelint/issues/527
- Repo: apigee/apigeelint, owner_type = Organization
- Problem: linter plugin crashed instead of linting. Verbatim error string from the issue:
  `plugin error: PO023-quotaPolicyReuseCheck.js TypeError: step.getParent(...).getPhase is not a function`
  with stack `at getFlowKey (/usr/local/lib/node_modules/apigeelint/lib/package/plugins/PO023-quotaPolicyReuseCheck.js:92:45)`
  `at onPolicy (/usr/local/lib/node_modules/apigeelint/lib/package/plugins/PO023-quotaPolicyReuseCheck.js:43:19)`
- Why the obvious first explanation is wrong: a `TypeError` inside apigeelint reads as a broken
  install or a bad node version. It is neither. The fault is a null path in the plugin: a policy
  attached to a `<FaultRule>` has a different parent chain than a policy on the normal
  `<Step>`, and `getPhase` is not defined on it.
- Environment: apigeelint, plugin PO023. Opened 2025-06-01.
- Evidence for claimed cause: maintainer statement. Evidence level (b).
- Resolution: MERGED. PR https://github.com/apigee/apigeelint/pull/528 "fix: correct PO023
  handling of Quota in FaultRule", merged=true, merged_at 2025-06-02T16:43:37Z. Issue closed
  2025-06-02. No reporter confirmation.
- Still applies today: fixed in a version released after June 2025; verify the installed
  apigeelint version before repeating this diagnosis.

## Case 3. apigeetool fails TLS with UNABLE_TO_VERIFY_LEAF_SIGNATURE against an on-prem endpoint

- URL: https://github.com/apigee/apigeetool-node/issues/6
- Repo: apigee/apigeetool-node, owner_type = Organization. "apigeetool" implementation in
  Node.js for managing Apigee Edge apps and proxies.
- Problem: apigeetool cannot talk to a private/on-prem Apigee SSL endpoint. Verbatim error:
  `Error: UNABLE_TO_VERIFY_LEAF_SIGNATURE` with stack `at SecurePair.<anonymous> (tls.js:1380:32)`
  `at SecurePair.emit (events.js:92:17)` `at SecurePair.maybeInitFinished (tls.js:979:10)`.
  Reporter: "We have our own instance of Apigee and when trying to use our SSL endpoint (base URL)
  with apigeetool, I get: ... There should be a way, how to specify the certificate used for
  validation of the endpoint certificate."
- Environment: Apigee Edge for Private Cloud, apigeetool-node, 2014-12-04, Node `tls.js` line
  numbers indicate a very old Node runtime.
- Why the obvious first explanation is wrong: the instinct is that the gateway cert is expired
  or self-signed and should be replaced. The defect is in the client: apigeetool had no way to
  supply a CA, and no way to skip verification.
- Evidence for claimed cause: maintainer statement. gbrail (apigee) replied: "That's a good use
  case -- thanks! ... We could add a flag that lets you pass in a CA certificate as a PEM file ...
  Or, we could add a flag to disable certificate validation, like the '-k' flag to 'curl.'"
  Evidence level (b).
- Resolution: MERGED and CONFIRMED. PR https://github.com/apigee/apigeetool-node/pull/7 "added
  'cafile' and 'insecure' command line options for handling SSL connections", merged=true,
  merged_at 2015-02-26. Reporter confirmed: ivan-novakov, 2016-01-05: "I think, this problem has
  been resolved in #7 . At least it works for me :." Issue remains OPEN (state_reason None).
  This is the strongest of the four claims on the same issue: merged AND confirmed working,
  yet the issue was never closed.
- Still applies today: no. `cafile` and `insecure` are present in the tool (repo still actively
  pushed, 2026-08-07). The CLOSED-vs-CONFIRMED gap is the reusable lesson.

## Case 4. Same TLS symptom, different cause: corporate TLS-intercepting proxy, and the popular fix does not work

- URL: https://github.com/apigee/apigeetool-node/issues/33
- Repo: apigee/apigeetool-node, owner_type = Organization
- Problem: verbatim error `Error: unable to verify the first certificate`. Reporter states the
  discriminator plainly: "As long as I'm outside the firewall, apigeetool works properly."
  Tried and failed: `npm config set registry="http://registry.npmjs.org/"` and
  `npm config set strict-ssl false`. Then: "I've also tried to use the `-k` option to turn off ssl
  checking, and it still doesn't work - I get other errors. So, the bottom line is that I need
  to use apigeetool outside my corporate firewall to make it work."
- Corroborating third report, stewartmatheson 2016-07-17: "This is similar to the issue I'm
  having. Apigeetool does not seem to respect the ignore certificate check. In my case the
  corporate proxy will return a different certificate to what apigeetool is expecting. Setting
  `npm config set strict-ssl false` should resolve the issue however in apigeetool's case this
  does not seem to be happening."
- Why this is the best case in the set: Case 3 and Case 4 present nearly the same symptom
  (TLS verify failure on connect) but the obvious explanation for each is different, and the
  obvious FIX for Case 3 is documented by the reporter as failing for Case 4. An agent that
  learned "UNABLE_TO_VERIFY_LEAF_SIGNATURE -> use -k" from Case 3 gives the wrong answer here.
  The real discriminator is the presence of a TLS-intercepting middlebox: the client sees a
  certificate that is valid for the proxy, not for the host it asked for, so the hostname does
  not match even after verification is relaxed. `-k` suppresses chain validation, not
  hostname/identity mismatch in every node version, and it does not repair the missing
  corporate root CA in the OS trust store.
- Environment: Edge for Private Cloud deployment behind a corporate firewall, 2015-12-31.
- Evidence for claimed cause: reporter-confirmed on the boundary condition only (works outside
  the firewall, fails inside) — evidence level (c) for the boundary, (d) for the "corporate
  proxy returns a different certificate" mechanism, which is an inference by a second user.
- Resolution: PROPOSED only, and explicitly not confirmed. tmarrs: "I'm wondering if the
  solution for .../issues/6 fixes this too" -> ivan-novakov's confirm applies to #6 only.
  tmarrs: "I tried the `insecure` option and it didn't solve
  https://github.com/apigee/apigeetool-node/issues/33". Issue is still OPEN today.
- Still applies today: the node-version-specific mechanics may have changed, but the trap
  stands: `strict-ssl` is an npm setting and does not govern apigeetool's own outbound TLS,
  and "turn off certificate checking" is not the same operation as "trust our internal CA".

## Case 5. apigee-remote-service-cli provisions over mTLS, then fails its own verification with 400

- URL: https://github.com/apigee/apigee-remote-service-cli/issues/261
- Repo: apigee/apigee-remote-service-cli, owner_type = Organization
- Problem: verbatim, reporter: "the proxy resources are successfully created over mTLS, but the
  subsequent verification steps fail with HTTP 400. The verification logic appears to ignore the
  provided mTLS certificates, sending requests without the client certificate." Repro in the
  report: "Provision an Apigee environment requiring mTLS by running apigee-remote-service-cli
  provision with --tls-cert, --tls-key, and --tls-ca. - Observe that the proxy creation and KVM
  setup succeed. - Notice that the automatic verification attempts to call /remote-service and
  /remote-token endpoints, returning 400 errors because the client certificate is not
  presented."
- Independent code check I performed (not a reporter claim): in `cmd/provision/provision.go`,
  `createAuthorizedClient` builds the shared `http.Client` and only ever sets
  `TLSClientConfig: &tls.Config{InsecureSkipVerify: true}` under
  `config.Tenant.TLS.AllowUnverifiedSSLCert`. It never calls `tls.LoadX509KeyPair` and never
  populates `tls.Config.Certificates`. `verifyRemoteServiceProxy` then reuses that same client
  for `GET /certs`, `GET /products`, `POST /verifyApiKey`, `POST /quotas`. So the structural
  claim checks out: no client certificate is presented on the verify leg.
- Two details that make this a much better scenario than the report itself:
  1. `verifyRemoteServiceProxy` deliberately tolerates 401 and 500:
     `if res.StatusCode != http.StatusUnauthorized && res.StatusCode != http.StatusInternalServerError`
     — "401 or 500 is ok, either the secret is not there or we didn't use a valid api key".
     So a 400 is not a generic failure; it means the request arrived and was rejected on
     grounds the tool never expected.
  2. The failure does NOT fail the command on hybrid. `provision.go` ends with
     `if !p.IsGCPManaged || p.isCloud() { return verifyErrors }` and `isCloud()` is
     `IsGCPManaged && runtimeType == "CLOUD"`. On hybrid (GCP-managed, not CLOUD) the
     expression is false, so the 400s are printed as a warning and the command exits
     successful. On SaaS and OPDK, `IsGCPManaged` is false and the verifyErrors ARE returned.
  Same tool, same 400, two different operational outcomes depending on runtime type.
- Environment: apigee-remote-service-cli, issue opened 2025-01-09. The issue's "Platform"
  section is a blank template, so the reporter did not state the version.
- Evidence for claimed cause: reporter claim plus my own read of the source. Evidence level (d):
  no maintainer has responded and nothing is confirmed.
- Resolution: NONE. Issue state OPEN, state_reason None, **zero comments** as of 2026-10-12.
  This is the weakest claim class and must be labelled as such.
- Still applies today: the source still shows the behaviour, so yes, unless a change landed
  after this read. Verify against the running version before asserting it.

## Case 6. Maven says deployment failed, the UI says "revision is deployed", the real cause is a corrupted jar

- URL: https://github.com/apigee/apigee-deploy-maven-plugin/issues/155
- Repo: apigee/apigee-deploy-maven-plugin, owner_type = Organization
- Problem: three different failure messages for one deployment. Verbatim from the reporter:
  - Edge UI: `"Error in deployment for environment dev. The revision is deployed, but traffic cannot flow"`
  - Maven: `"Deployment failed: Bundle did not activate within the expected time. Please check deployment status manually before trying again "`
  - From Apigee support to the reporter: `"steps.javacallout.JavaCalloutInstantiationFailed"`
  - Reporter: "If we _manually upload the JAR file(1) from UI, the same deployment works fine. Hence
    it is pointing to the problem in Maven deployment plugin."
- Why the obvious first explanation is wrong: two wrong answers are sitting right there. (i) "The
  bundle activated late, just retry the deployment" — the message invites exactly this and it is
  wrong, the bundle will never activate. (ii) The reporter's own conclusion, "it is pointing to
  the problem in Maven deployment plugin", which the original issue text itself asserts and which
  is also wrong. Apigee support bounced it with "APIGEE support can't investigate further as it
  is an open-source maven plugin issue", so the tool vendor really was the only place left to look,
  and even there the answer was in the user's own POM.
- Actual cause, from a second reporter in the same thread (rad264, 2021-06-10): "I had the same
  or a very similar issue. Deployed with the plugin, the Maven command finished no problem, but in
  the Edge UI it said it failed to deploy with the same message. Called the management API to get
  more info and saw the same error: 'steps.javacallout.JavaCalloutInstantiationFailed'. If I
  updated the jar manually through the Edge UI, it deployed successfully. In my case, it was
  because I had enabled filtering for the maven-resources-plugin (`<filtering>true</filtering>`)
  on the entire apiproxy folder, which included the jar. I guess it must have tried to filter the
  jar contents, and corrupted it, because once I disabled filtering, it deployed successfully."
- Fault-code check: `JavaCalloutInstantiationFailed` is in the local index with message
  `Failed to instantiate the JavaCallout Class [classname]`
  (.agents/skills/apigee-support-core/references/error-codes.md line 243). The prefix
  `steps.javacallout.` is the standard policy-fault prefix. Valid.
- Why the symptom is a Java callout and not a TLS or deployment error: the class file inside
  the jar has been rewritten as text, so the JVM cannot load the class. "Instantiation failed"
  means the class was found but could not be constructed; a text-corrupted class file produces
  this, and so does a genuinely wrong class name. The discriminator is that a UI upload of the
  same artifact works, which rules the artifact out only if the uploaded file is byte-identical.
  A maven-resources filter means it is not.
- Evidence for the claimed cause: (c) reporter-confirmed workaround, but for the SECOND
  reporter's case, not the original poster's. rad264 is explicit: "It's unlikely this was the OP's
  exact issue". So the mechanism is (c); the claim that it explains issue #155 is (d).
- Resolution for the original issue: NONE. Still OPEN, 2 comments, no maintainer statement.
  Maintainer ssvaidyanathan (COLLABORATOR) replied "The above info is not enough to investigate"
  and asked for `mvn -X`. Evidence level (b) only for "not enough info".
- Still applies today: yes. `<filtering>true</filtering>` over a directory containing a binary
  jar is a build defect that no Apigee version change fixes. Note also the reporter's own
  closing advice, which is the durable part: "Make sure nothing is potentially altering the jar
  in any way when copying or packaging the bundle!"

## Case 7. "Path /x conflicts with existing deployment path" — the maintainer's first diagnosis was also wrong

- URL: https://github.com/apigee/apigeetool-node/issues/57
- Repo: apigee/apigeetool-node, owner_type = Organization
- Problem: verbatim, reporter: "My CI tool just updated the npm package to 0.6.4 and now my
  deployments are broken because of the message > 'Error: Path /myproxy conflicts with existing
  deployment path for revision 13 of the APIProxy authorization in foo-organization'." Also:
  "When I reverted back to 0.6.3 the deploy worked again, so there is something wrong with the
  version matching."
- Why this matters as a scenario: the maintainer's first answer is a good example of a
  plausible-but-unverified explanation. mukundha (CONTRIBUTOR) replied: "the basepath conflict
  issue look different. If its the same proxy, then `deployproxy` would override the previous
  revisions. But if the basepath conflict happens across proxies, then it would fail with the
  above error you mentioned. I tried the former case, it seemed to work - but i can look into it
  again - can you confirm?" He explicitly separates two mechanisms that produce the same string
  and asks the reporter which one applies. That is the diagnostic question, and it is not the
  one the version number suggests.
- Note the message text itself is misleading: "APIProxy authorization" is the name of a
  DIFFERENT proxy in the same org, not the proxy being deployed. The obvious reading is that the
  tool deployed the wrong proxy. It did not; the base path was already claimed by another proxy.
- Evidence for the claimed cause: maintainer statement, evidence level (b), and explicitly
  provisional ("it seemed to work", "can you confirm?").
- Resolution: PROPOSED, not confirmed. mukundha: "we just published v0.6.6 to npm, with these
  https://github.com/apigee/apigeetool-node/pull/60 — let me know if it fixes your issue". The
  reporter never answered. Issue is still OPEN.
- Still applies today: apigeetool-node is actively maintained (pushed 2026-08-07) and 0.6.6 is
  many releases behind; treat the current tool as fixed and the reporting as unverified.

## Case 8. `kvms export --org=$ORG` exports proxy KVMs only, and the help text says otherwise

- URL: https://github.com/apigee/apigeecli/issues/540
- Repo: apigee/apigeecli, owner_type = Organization. Reporter kurtkanaskie, COLLABORATOR.
- Problem: the tool's own help text, quoted verbatim from the issue: `export      Export all KV Map
  entries for all KV Maps`, with only `-o, --org string  Apigee organization name` and
  `-r, --region`. Reporter: "The command implies it exports all KVMs ... How do I export org
  level KVMs using `apigeecli kvms export`?"
- Why the obvious first explanation is wrong: the natural operational conclusion is "our org
  KVMs were never deployed" or "org KVMs were lost in a migration". Nothing was lost. The
  export never looked at org-scoped KVMs.
- Cause, located in source by a collaborator (kurtkanaskie): `internal/cmd/kvm/expkvm.go`
  line 54, verbatim:
  ```go
  		// return all kvm entries from all proxies
  		if env == "" && proxyName == "" {
  			return kvm.ExportAllEntries()
  		}
  ```
  With no `--env` and no `--proxy`, `ExportAllEntries()` is proxy-scoped, so
  `kvms export --org=$ORG` means "every KVM in every proxy", not "every KVM".
- The useful second-order finding: a second collaborator (srinandan) states the scope rule
  explicitly — "You can export all org scoped kvms or proxy kvms for a proxy or env kvms for a
  specific environment. But nothing to export all KVMs." And kurtkanaskie shows that simply
  deleting the block is not a complete fix, because it would then break the proxy case:
  "But then there's no way to export all proxy KVMs unless we use something like
  `kvms export --org=$ORG --proxy=*` and change to use
  `if env == "" && proxyName == "*" { return kvm.ExportAllEntries() }` which works."
  Three KVM scopes (org, environment, proxy) share one command whose default means only one of
  them.
- Evidence for the claimed cause: maintainer statement with a file and line reference, evidence
  level (b). Strongest of the four statuses.
- Resolution: MERGED. Commit `dd7b9e17` "bug: enable exporting org scoped kvms #540 (#541)"
  in apigee/apigeecli, authored 2024-09-17T03:22:39Z, the same second the issue closed
  (state_reason completed, closed_at 2024-09-17T03:22:40Z). Issue events show
  `closed srinandan 2024-09-17T03:22:40Z`. Closed one day after opening.
- Still applies today: fixed 2024-09-17, and apigeecli has been released since (pushed
  2026-07-28). The SCOPE MODEL, not the bug, is what still applies: in Apigee a KVM name is
  scoped to org, environment or proxy, and `--org` alone does not imply org scope.

## Case 9. Shared flow deployment fails silently with `"state":"error"` and partialResults

- URL: https://github.com/apigee/apigeetool-node/issues/151
- Repo: apigee/apigeetool-node, owner_type = Organization. Reporter jhonnymertz, NONE.
- Problem: a deploy that partially fails is reported as success by the SDK. Verbatim, the
  failing response:
  ```json
  [{"name":"shared-flow-name","environment":"dev","revision":47,"state":"error","basePath":"N/A","partialResults":[{"pod":{"name":"rde1dmp010-1","region":"eu-central-1"},"status":"deployed","type":["message-processor"],"uUID":"1be899cb-3228-4239-baeb-713ac2b5fad4"},{"pod":{"name":"rea1dmp010-1","region":"us-east-1"},"status":"deployed","type":["message-processor"],"uUID":"d7ffaa10-16da-4bc3-a2e8-5512f37bc33d"}, ... ]}]
  ```
  versus the success shape:
  ```json
  [{"name":"shared-flow-name","environment":"dev","revision":48,"state":"deployed","basePath":"N/A","uris":[]}]
  ```
  Reporter: "sometimes the deploy of shared flows fail and the javascript command does not result
  on errors nor trigger exceptions. It may be due to some network issue or something on apigee
  side that `partially` deploys the shared flow, so I'm not able to reproduce it." And: "apigeetool
  sdk does not trigger the exception, it proceeds to the `then` ... handleError(err) // not reached
  when the error mentioned happens..."
- Why the obvious first explanation is wrong: two of them. "The network dropped during deploy"
  explains nothing about why the SDK said success, and it invites retries that create more
  partial revisions. The real defect is that HTTP-level success is being read as
  deployment-level success.
- The precise trap: the response IS an error and it is HTTP 200. The signal is inside the body —
  `"state":"error"` alongside a `partialResults` array in which individual pods report
  `"status":"deployed"`. Note the pod names: `rde1dmp010-1` and `rea1dmp010-1` are runtime
  router / message processor data plane nodes, and they are spread over `eu-central-1` and
  `us-east-1`. A deployment that reports per-pod detail at all is already a hybrid/Apigee X
  managed-runtime response, not Edge for Private Cloud.
- Reporter's own interim mitigation, quoted: "Of course, I can verify the content of the `result`
  and check the `state` field of the deployment (which indeed I'm doing right now). But, I'd like
  to confirm if it is expected behavior". So the workaround exists and is (c) reporter-confirmed
  in the weak sense of "I am using it".
- Evidence for the claimed cause of the partial deployment itself: NONE. The reporter says
  explicitly they could not reproduce it. Anyone asserting a cause for the partial deployment is
  inventing one. Evidence level for the root cause: (d) at best; for the silent-success
  behaviour, (c).
- Resolution: NONE. Issue still OPEN. One comment, and it is another user asking the reporter a
  question: "you got any solution?" (maheshdhummi, NONE, 2019-11-19). No maintainer has
  engaged in seven years.
- Still applies today: the general rule — a 200 from the deployments API is not a successful
  deployment; read `state` and `partialResults` — is durable. Whether apigeetool-node still has
  the behaviour has not been checked.

## Case 10. apigeelint BN003 false positive: PopulateCache in one proxy, LookupCache in another, and the maintainer decided not to fix it

- URL: https://github.com/apigee/apigeelint/issues/480
- Repo: apigee/apigeelint, owner_type = Organization. Reporter ssvaidyanathan, COLLABORATOR.
- Problem: plugin BN003 requires a `<PopulateCache>` for every `<LookupCache>` found in the bundle
  being linted, and errors when the PopulateCache is not in that bundle. Verbatim: "The logic for
  BN003 might not be right. The plugin basically checks for a key from LookupCache policy matches
  with the PopulateCache policy. It fails if the PopulateCache policy is not part of the bundle.
  This is a common use case where I could have the logic to populate the cache in one proxy and
  have the lookup in another.. Similarly I could have populating cache in one SharedFlow and the
  retrieval in another sharedflow.. This should not flag as an error..."
- Why the obvious first explanation is wrong: this lint failure is, correctly, a real runtime
  hazard — and the agent's natural first move, "add a PopulateCache to this bundle", can create a
  second real bug. The default `<Scope>` is `Exclusive`, and the official documentation is
  explicit that this makes the key proxy-local. Quoted from the cached official page
  (research/pages/api-platform_reference_policies_lookup-cache-policy.txt, line 249):
  "Exclusive | Default. This is the most specific, and therefore presents minimal risk of namespace
  collisions within a given cache. Prefix is one of two forms: If the policy is attached to the
  ProxyEndpoint flow, prefix is of the form ApiProxyName_ProxyEndpointName . If the policy is
  attached at TargetEndpoint , prefix is of the form ApiProxyName_TargetName . Cache key
  prepended in the form orgName__envName__applicationName__proxyNameITargetName". And line 244:
  "Global | Cache key is shared across all API proxies deployed in the environment. Cache key is
  prepended in the form orgName __ envName __."
  So: a PopulateCache in proxy A and a LookupCache in proxy B only share a cache key if Scope is
  `Global` (or a `<Prefix>` is set, since line 238 says "A `<Prefix>` element overrides any
  `<Scope>` element"). With the default, they can never meet. The linter is detecting a genuine
  defect in most cases, which is exactly why it is hard to simply switch it off.
- The genuinely undocumented part, and the reason the maintainers stalled: the scope values
  `Application`, `Proxy` and `Target` all resolve to the PROXY, not the shared flow. Line 246:
  "Application | API proxy name is used as the prefix." So two different shared flows attached to
  the same proxy CAN share keys under those scopes. That is not written down anywhere in the
  policy reference.
- Maintainer asked exactly the right question and never got an answer. Verbatim, DinoChiesa
  (COLLABORATOR) 2024-10-18: "Do you know, What happens if the PopulateCache is done within one
  Shared flow, and the LookupCache is done from within another shared flow, and if the
  [Scope](...) for the policies is _anything other than Global_ ? Does it work? If the Scope is
  "Application" does it use the shared flow name? or the proxy name? Do you know? What about the
  other cases?" No answer appears in the thread.
- Final disposition, verbatim, DinoChiesa 2026-04-12: "Ya, I am of the mind to just leave it alone.
  People can disable it in their .apigeelintrc file or on the command line. It's not useful in a
  sufficiently complex environment." And mldelaney94 (CONTRIBUTOR) 2026-03-24: "I created an
  external plugin for my company that just scans all apigeex repos for the existence of a newly
  referenced sharedflow or proxy, allowing us to disable this plugin altogether. That is probably
  just where this rule will go and should be the recommended path for users who find it giving
  false negatives once their setup becomes at a certain level of complexity."
- Evidence level: (b) maintainer statement for the decision not to fix; (a) official documentation
  for the Scope semantics; the "false negative" framing in the community comment is technically a
  misnomer — the plugin is producing a false POSITIVE (it flags valid bundles), which is worth
  noting because the contributor who proposes the workaround calls it the other way round.
- Resolution: CLOSED-BY-DECISION is wrong — the issue is still OPEN (state_reason None) as of
  2026-10-12. There is no fix and none is planned. This is a permanent known false positive.
- Still applies today: YES, and deliberately. Any scenario built on BN003 must accept that
  disabling the rule is the sanctioned answer, not "fix the bundle".

## Case 11. Quota CountOnly/EnforceOnly pairing rule proposed, then withdrawn because the maintainers' own topology violates it

- URL: https://github.com/apigee/apigeelint/issues/475
- Repo: apigee/apigeelint, owner_type = Organization. Reporter DinoChiesa, COLLABORATOR.
- Problem: a proposed new lint rule. Verbatim: "It should be the case that if there is an
  EnforceOnly Quota policy, we should also have a CountOnly policy attached. @ssvaidyanathan
  @kurtkanaskie WDYT? Are there cases where it makes sense to violate this? For example, a
  CountOnly policy in a FlowHook-attached sharedflow, and an EnforceOnly policy directly attached
  in the proxy?"
- Why this is worth keeping even though nothing shipped: the rule was proposed by a maintainer,
  the two people asked to review it both said the rule is wrong for a real topology, and it was
  closed without a commit. The maintainers' own answer, verbatim, kurtkanaskie: "I've always used
  them in pairs. EnforceOnly doesn't increment the count so it's not useful on its own. I suppose
  they could be in different shared flows (e.g. PreFlow flow hook and PostFlow flow hook)."
  ssvaidyanathan: "Yes - thats how its been used, if they want it in two different sharedflows.
  Sometimes in request vs response flows as well".
  So the proposed rule was correct at the level of "same bundle" and wrong at the level of
  "same request path", which is where linting actually operates.
- The underlying runtime fact, quoted by a maintainer: "EnforceOnly doesn't increment the count".
  This is the mechanism behind a whole family of confusing Quota symptoms: an EnforceOnly policy
  enforces and does not count, so if you only deploy EnforceOnly you get enforcement with no
  analytics, and if you split CountOnly into one shared flow and EnforceOnly into another, you get
  both — but only if both actually execute on the same request path.
- Evidence level: (b) maintainer statement, twice, from two collaborators.
- Resolution: CLOSED, state_reason completed, closed 2024-12-26T22:13:17Z by DinoChiesa. I checked
  the commit log for apigee/apigeelint after 2024-09-27 for a Quota/PO023/PO0xx commit and found
  none implementing this. The issue events show only `mentioned` x2, `subscribed` x2 and `closed`.
  So "closed completed" here means "decided not to do it", and no rule was added. This is the
  clearest example in the whole set of CLOSED being mistaken for FIXED.
- Still applies today: the rule does not exist. The flow-hook split of CountOnly and EnforceOnly
  is a sanctioned pattern, not a lint violation.

## Case 12. Two apigeelint rules that cannot both be satisfied: TD006 vs TD012, plus a rule that fights the official anti-pattern page

- URL: https://github.com/apigee/apigeelint/issues/526
- Repo: apigee/apigeelint, owner_type = Organization. Reporter PratMoha, NONE (an outside user).
- Problem, part 1 — the unsatisfiable pair. Verbatim from a second reporter, kacperillo, who hit
  it independently: "I get the linting warning: 'TargetEndpoint HTTPTargetConnection should have
  exactly one SSLInfo'. So I added SSLInfo to the configuration ... And then I get another warning:
  'When using a LoadBalancer, the SSLInfo should be configured in the TargetServer, not under
  HTTPTargetConnection', which is in contradiction to the first one. So in each situation there is a
  warning." There is no bundle that satisfies both. Rule TD012 fires when HTTPTargetConnection has
  no SSLInfo; rule TD006 fires when it does.
- Problem, part 2 — a rule that contradicts the official anti-pattern guidance. TD015 "Missing
  MaxFailures element within LoadBalancer" fires on a single-server LoadBalancer. The reporter
  quotes the official page back at the maintainers:
  "If there's some constraint such that only one TargetServer and if the HealthMonitor is not used,
  then don't specify MaxFailures in the LoadBalancer configuration. The default value of MaxFailures
  is 0. This means that Apigee always tries to connect to the target for each request and never
  removes the target server from the rotation."
  and: "I have only one server specified in LoadBalancer and the apigeelint requires MaxFailures to
  be included, however the Google documentation defines it as antipatern: 'Having single
  TargetServer in a LoadBalancer configuration of the TargetEndpoint or Service Callout policy with
  MaxFailures set to a non-zero value is not recommended as it can have adverse implications.'"
  So complying produces a different warning: set MaxFailures to 0 and TD015 complains it must be a
  positive integer.
- Why the obvious first explanation is wrong, and this is the durable insight: the instinct is
  "the linter is wrong, add SSLInfo to the bundle". Maintainer DinoChiesa (COLLABORATOR) states
  the structural reason, verbatim: "For 'When using a LoadBalancer, the SSLInfo should be configured
  in the TargetServer, not under HTTPTargetConnection': this warning is issued by plugin TD006. In
  fact this is the only thing TD006 does. ... But the plugin isn't checking that. It's checking the
  proxy. (TargetEndpoint). And it has no way to check the referred TargetServer - in other words it
  has no way to check that SSLInfo is configured in the TargetServer, per the recommendation. The
  design of the plugin is sort of broken - it assumes that if there is an SSLInfo under
  HTTPTargetConnection, then it is NOT present in the TargetServer. But that is not a valid
  assumption."
  apigeelint lints a bundle. TargetServers are org-level entities and are NOT in the bundle. The
  linter therefore cannot verify the advice it is giving. The rules were not merely miscalibrated;
  they were asking a question the tool structurally cannot answer.
- The third-party disagreement, which makes this better than a plain bug: PratMoha reports the
  same TD012 warning is ALSO produced by Advanced API Security "even when the same is defined in the
  target server". Advanced API Security CAN see TargetServers. So the linter with less information
  and the scanner with more information produce the same wrong warning. DinoChiesa, verbatim:
  "That seems like a bug in Adv API Sec. We don't have control over that. I suggest you connect
  with Google support and file a bug. Adv API Sec **IS** able to see the TargetServers". Treat the
  Adv API Sec half as (d) unverified from this source.
- Maintainer's own plan, verbatim, 2025-06-03: "1. Demote TD006 to an External Plugin. 2. Modify
  TD012 to fire if and only if there is no LoadBalancer 3. Modify TD015 so that it does not
  complain about a missing MaxFailures if there is a single server." ssvaidyanathan amended item 2
  to "checks only if there is a URL configured (https)" and approved item 3: "Yes - lets warn only
  if there are more than one server". He voted to KEEP TD006 as a built-in rather than demote it.
- Evidence level: (b) maintainer statement, plus (a) official documentation for the MaxFailures
  anti-pattern page.
- Resolution: MERGED and RELEASED. ssvaidyanathan, 2025-06-04: "Fixed in v2.67.0". Release tag
  v2.67.0 published 2025-06-04T00:42:43Z; commit e42588a5 "v2.67.0" authored 2025-06-04T00:40:05Z.
  Issue CLOSED 2025-06-04T00:43:12Z, state_reason completed. Reporter never re-tested.
- Verified still applies today: NO, and I confirmed by reading the current plugin source rather
  than trusting the release note.
  - `TD006-target-LoadBalancer-SslInfo.js` message is now "Configure SSLInfo in the TargetServer,
    even if SSLInfo is also present under HTTPTargetConnection", and it is still `enabled: true`,
    so it was NOT demoted to an external plugin as proposed. The contradiction is gone because the
    message now tolerates both.
  - `TD012-targetSslInfo-exactly-one-SSLInfo.js` now gates on `if (urls.length == 1)`, so it no
    longer fires when a LoadBalancer is used.
  - `TD015-target-LB-no-MaxFailures.js` now contains `if (maxFailuresElts.length == 0) { if
    (serverElts.length != 1) {`, so the single-server case is exempt.
  The lesson survives: a lint warning about a TargetServer cannot be resolved from inside the
  bundle.

## Case 13. Build passes, deployment says "Sharedflow deployment failed with status: ERROR", exit code is 0

- URL: https://github.com/apigee/apigeecli/issues/644
- Repo: apigee/apigeecli, owner_type = Organization. Reporter ascopes, CONTRIBUTOR.
- Problem: verbatim terminal transcript from the issue:
  ```
  ➜ code git:(task/test) >>> apigeecli sharedflows deploy --org my-org --account  ~/.gcloud/my-key.json --env my-env --name sharedflow-x-powered-by --rev 12 --ovr --wait
  {
          "environment": "my-env",
          "apiProxy": "sharedflow-x-powered-by",
          "revision": "12",
          "deployStartTime": "1740661465612"
  }

  Checking deployment status in 10 seconds
  Sharedflow deployment failed with status:  ERROR
  ➜ code git:(task/test) >>> echo $?
  0
  ```
  Reporter: "If the `apigeecli sharedflows deploy` command fails, we still get an exit status of 0.
  This means we are unable to fail our builds if sharedflow deployments fail. The equivalent
  command for `apigeecli apis deploy` _does_ fail with a non-zero exit code, which means the
  process of deploying sharedflows and apiproxies does not appear to work consistently."
- Why the obvious first explanation is wrong: the tool PRINTED the failure in plain English and
  then exited 0. Two wrong conclusions follow from that shape. (i) "The pipeline is fine, the tool
  told us it failed, humans will see it" — no, the pipeline sees nothing. (ii) "It is a shared
  flow specific quirk, only shared flows are affected" — also wrong, the reporter's own comparison
  shows `apis deploy` already behaved correctly, so the defect is in one sharedflow code path, not
  in shared flows as a concept. The tell is the asymmetry, and the right instinct is to ask why
  the same class of failure is handled differently in two commands of the same tool.
- Evidence for the claimed cause: maintainer statement, verbatim, kurtkanaskie (COLLABORATOR)
  2025-03-03: "I think I see the issue, the sharedflows Wait function is not setting err correctly
  when it fails." This is a code-reading diagnosis, not a guess about the environment.
- The maintainer then did the thing that makes this case unusually strong: reproduced it before
  fixing it. Verbatim, 2025-03-24: "@ascopes I was able to reproduce by forcing a JS syntax error."
  A JS syntax error inside the bundle makes the runtime reject the bundle, which is how you force a
  deployment to go to ERROR state on demand.
- Resolution: the strongest chain in this whole set. MERGED ("A fix has been merged into main",
  kurtkanaskie 2025-03-25), RELEASED ("Released in v2.10.1", ssvaidyanathan 2025-03-26; tag
  v2.10.1 published 2025-03-26T16:47:22Z), and CONFIRMED by the original reporter
  (ascopes, 2025-03-26T16:37:14Z: "Thanks for the quick fix!"). Issue CLOSED 2025-03-26T16:52:02Z,
  state_reason completed. Note the 29 days between report and fix, and that the confirmation came
  from the reporter before the close, which is the correct order.
- Still applies today: no, fixed in v2.10.1 (2025-03). The durable rule is that a deployment tool's
  exit status must be checked, because "did it deploy" and "did the tool succeed" are different
  questions, and `state` in the deployments response is a third.

## Case 14. Maven fails with an error whose message is literally `null`, caused by a feature that cannot work in the wrapper

- URL: https://github.com/apigee/devrel/issues/533
- Repo: apigee/devrel, owner_type = Organization. Reporter vitor-a-pinto-alb, NONE.
- Problem: verbatim, `[ERROR] Failed to execute goal io.apigee.build-tools.enterprise4g:apigee-edge-maven-plugin:2.3.1:configure (configure-bundle-step) on project apigee-deployer: null: MojoExecutionException -> [Help 1]`.
  Reporter: "If config.json (supported by apigee-deploy-maven-plugin) is present, using sackmesser
  to deploy the proxy with `sackmesser deploy --googleapi -d <path to proxy> -t $(gcloud auth
  print-access-token) -e $ENV -o $ORG` Fails with the error ... If I remove config.json everything
  works just fine."
- Why the obvious first explanation is wrong: the error text contains the word "null" where the
  message should be. That reads like a broken or mismatched plugin version, and the obvious moves
  are to upgrade apigee-edge-maven-plugin or to suspect the proxy bundle. Neither helps, because
  the cause is a structural mismatch between two tools. It is also not a network or auth problem,
  which the `null` message might otherwise suggest.
- Evidence for the claimed cause: maintainer statement, verbatim, danistrebel (COLLABORATOR)
  2022-05-03: "Apigee Sackmesser's intention was to remove the need for writing a manifest and the
  complexity that comes with Maven. So far this has worked out nicely but it breaks a few features
  that are dependent on some maven constructs. The config.json is one of them because it depends
  on a match of the key in the config.json and the profile used. Because the pom.xml is auto
  generated the profile functionality is not used." Evidence level (b).
- The decisive diagnostic detail, which rules out the plugin-version theory: the same config.json
  deployed with the maven plugin directly WORKS. Reporter: "if I try to use maven plugin to deploy
  the proxy with the config.json on the zip file, with works fine." Same artifact, same config,
  same org, different wrapper, different result. The only variable is the auto-generated pom.
  The maintainer's first reply had also suspected a version mismatch, verbatim: "can you confirm
  you're using the config.json you linked? Because the linked file is the Apigee Edge config.json
  file and some of the resources might not be 100% compatible with the X/hybrid API you target with
  `--googleapi`" — a hypothesis the reporter's follow-up disproved.
- Resolution: NONE, and a design decision was never made. The maintainer listed three options and
  the thread ends on "I am not yet convinced this is a great idea so any input is very welcome".
  Issue still OPEN as of 2026-10-12, ~4.5 years after filing. Evidence level (d) for the current
  behaviour; nothing confirms it was ever fixed.
- Still applies today: the generalisable form holds for any wrapper that auto-generates a build
  file — Maven profile-scoped configuration cannot survive that. Whether sackmesser still behaves
  this way has not been re-verified.

## Case 15. A linter upgrade breaks every SpikeArrest policy, and the fix is to upgrade the linter again

- URL: https://github.com/apigee/apigeelint/issues/590
- Repo: apigee/apigeelint, owner_type = Organization. Reporter guycall, NONE.
- Problem: verbatim error string from the issue,
  `PO042 The element <UseEffectiveCount> is not allowed here in profile=apigee`
  against this policy, which the reporter quotes verbatim:
  ```xml
  <SpikeArrest name="SA-ThrottleOnSomething">
    <Rate ref="somevariable">10ps</Rate>
    <UseEffectiveCount>true</UseEffectiveCount>
  </SpikeArrest>
  ```
  Reporter: "Upgrading from v2.75.0 to v2.76.0 has introduced a new linting error in our project ...
  This occurs in all our Spike Arrest policies. From a look at the docs our usage is correct and also
  these policies are deployed and appear to be working as expected."
- Why the obvious first explanation is wrong: a lint failure names an element and a profile, so
  the natural read is "the element is not allowed in this product" and the natural remedies are
  remove the element, or check the org's product version. Both are wrong, and the reporter's own
  evidence already refutes them: the policies were already deployed and working before the linter
  complained, and the complaint appeared on a linter upgrade, not on a gateway change. The version
  that matters is the linter's, not the proxy's.
- The official documentation is also more specific than the lint message, and the difference is
  the whole point. From the cached official SpikeArrest page
  (research/pages/api-platform_reference_policies_spike-arrest-policy.txt):
  - line 52 lists the child elements as `<Identifier> <MessageWeight> <Rate> (Required)
    <UseEffectiveCount>`, so the element is documented and allowed.
  - line 589 onwards documents `true` as a supported value, and line 600 notes "Although the
    default value is `false`, Apigee organizations should set this element to `true`."
  - line 462 carries the actual restriction, verbatim: "**Note:** The use of
    [`<UseEffectiveCount>`] with a value or `false` is not supported for *any* Apigee
    organizations or for Apigee hybrid organizations running production workloads."
  So the documented constraint is about the VALUE `false` and about hybrid production workloads.
  It is not "the element is not allowed here". An agent that trusts the lint text over the
  policy reference will tell the customer to delete a setting the documentation explicitly
  recommends.
- Evidence for the claimed cause: maintainer statement, verbatim, ssvaidyanathan (COLLABORATOR)
  2026-01-08T00:16:57Z: "@guycall - thanks for reporting. A fix is pushed.. Will release it
  shortly". No root-cause explanation of why PO042 regressed is given in the thread.
- Resolution: the full chain, and it is fast. MERGED ("A fix is pushed"), RELEASED
  (ssvaidyanathan 2026-01-08T00:21:14Z "Released a patch v2.77.1"; tag v2.77.1 published
  2026-01-08T00:22:04Z), and CONFIRMED by the original reporter within two minutes of the
  release (guycall, 2026-01-08T00:24:23Z: "Fixed! Thanks"). Issue CLOSED 2026-01-08T00:24:23Z.
  For the record: v2.76.0 was published 2026-01-05T18:21:02Z, so the window of exposure was
  roughly 60 hours.
- Still applies today: no, from apigeelint v2.77.1 onward. The durable lesson is that an
  apigeelint version change can introduce or remove findings with no gateway change at all, so
  "the lint started failing" is a statement about the linter until proven otherwise.

## Case 16. Hybrid install fails with `error: You must be logged in to the server (Unauthorized)` from a kubectl wait

- URL: https://github.com/apigee/apigee-hybrid-install/issues/30
- Repo: apigee/apigee-hybrid-install, owner_type = Organization. Reporter DinoChiesa, NONE.
- Problem: verbatim log, and the timestamps are the diagnostic content:
  ```
  2022-12-09T20:38:14.187368 apigee-hybrid-setup.sh: Running: '/usr/bin/kubectl wait apigeedatastore/default apigeeredis/default apigeeenvironment/intrinsic-beam-11622-eval apigeeorganization/intrinsic-beam-11622 apigeetelemetry/apigee-telemetry -n apigee --for=jsonpath=.status.state=running --timeout=15m'
  error: You must be logged in to the server (Unauthorized)
  error: You must be logged in to the server (Unauthorized)
  2022-12-09T20:47:40.545270 apigee-hybrid-setup.sh: FAILED.
  ```
  Reporter: "At line 416, the script `apigee-hybrid-install/tools/apigee-hybrid-setup.sh` performs a
  `kubectl wait`. In my experience this thing can wait a good long time. It has a timeout of 15
  minutes ... But I have seen the credentials expire during this wait, causing an unexpected
  failure". And the confirming experiment: "If I refresh the credentials with `gcloud container
  clusters get-credentials ${CLUSTER_NAME} --project ${GCP_PROJECT_ID} --region ${CLUSTER_REGION}`
  ...then I can perform kubectl operations again."
- Why the obvious first explanation is wrong: "You must be logged in to the server (Unauthorized)"
  from a `kubectl wait` reads as "the cluster is unreachable", "the install put resources in the
  wrong namespace", or "run the script with the right project". Those send you looking at
  resources. The resources are fine; the message arrived 9 minutes 26 seconds after the wait
  started, which is long after authentication succeeded and inside a command the reporter says can
  legitimately run for 15 minutes. The timestamp is the evidence and nobody quoted it at first.
- Note also what the error does NOT say. This is not a Kubernetes RBAC denial (that would name a
  resource and a verb) and not a context problem (that would fail immediately, not after nine
  minutes). It is an authentication failure that appeared partway through a long-running command.
- Evidence for the claimed cause: reporter-confirmed workaround, evidence level (c): the refresh
  command was run and kubectl worked afterwards. But the reporter immediately qualified his own
  report: "Now that I look further, the symptom I am reporting here may be due to a problem on my
  side - in my .bashrc file I force a specific project, which is probably the wrong thing to do. It
  may be causing the timeout I reported." So the reporter withdrew the causal claim in the thread.
- Maintainer response, verbatim, blackrookgeek (CONTRIBUTOR) 2022-12-12: "You are correct that the
  Wait time may need to be adjusted. I have seen it take longer than 15 mins to complete setup. The
  Creds issue is separate from the wait issue. I'm not aware of any connection between the two."
  So even the maintainer did not accept the causal claim. Evidence level (b) for "this is a known
  separate issue", and explicitly not for a root cause.
- Resolution: PROPOSED only. The reporter supplied a patch (insert
  `gcloud container clusters get-credentials ...` before the `kubectl wait`). No maintainer merged
  it, and the issue is still OPEN as of 2026-10-12. Note the suggested patch is itself dubious:
  refreshing credentials once before a 15-minute wait does not fix a credential that expires
  DURING the wait, which is the symptom as reported.
- Still applies today: gcloud access tokens are short-lived and a `kubectl wait` with
  `--timeout=15m` can outlive them, so the failure mode is durable. Whether the script was changed
  has not been re-checked. This is an (d)-level case and must be labelled that way; the value is in
  the reasoning, not in the claimed fix.

## Case 17. Edge Microgateway quota plugin: "the local-mode check is reversed", issue closed, claim unverified

- URL: https://github.com/apigee/microgateway-plugins/issues/86
- Repo: apigee/microgateway-plugins, owner_type = Organization. Reporter heckler, NONE.
- Problem: a pure code-reading claim, quoted verbatim: "Looking at the quota plugin, the check for
  local mode appears reversed: https://github.com/apigee/microgateway-plugins/blob/master/quota/index.js#L61-L65
  For the 'if' test clause to match the debug message it should be reversed:
  `!process.env.EDGEMICRO_LOCAL` or `process.env.EDGEMICRO_LOCAL != \"1\"`".
- Why the obvious first explanation is wrong, and why this case is worth keeping despite being
  thin: the report has NO symptom. No customer report, no error string, no reproduction. The
  argument is entirely "the condition does not match the string in the adjacent debug line". That
  makes it very easy for an agent to pattern-match it onto a completely unrelated quota problem it
  is later shown — "local mode is skipping the quota plugin" — and to apply the same "fix" to a
  production issue where the maintainers established the opposite fact (Case 11: Edge Micro
  quota behaviour differs by runtime). The guard against that is to notice that this issue proves
  a code-reading habit, not a runtime behaviour.
- Evidence for the claimed cause: contributor statement, verbatim, srinandan (CONTRIBUTOR)
  2018-10-16: "yes, i have a PR to fix this. i will publish this version soon." Evidence level (b),
  and note it is a promise to publish, not a merged PR.
- Resolution: PROPOSED, and the resolution record is poor enough to be instructive. Two months
  later dschniebel asks: "This issue should be closed or am I wrong?" and the issue author
  replies "yes, this should be closed." The issue is CLOSED 2018-12-15T22:36:11Z,
  state_reason completed. No merged PR is referenced anywhere in the thread.
- Verified against current source, which is why this is still worth recording: the plugin today
  (apigee/microgateway-plugins, pushed 2026-03-31) reads
  ```js
  onrequest: function(req, res, next) {
      if ( process.env.EDGEMICRO_LOCAL !== undefined ) {
          debug("MG running in local mode. Skipping Quota");
          next();
      } else {
          middleware(req, res, next);
      }
  },
  ```
  The commit history for `quota/index.js` shows no December 2018 fix; the entries jump from
  2019-06-28 onward. So the specific correction the reporter asked for was NOT applied: the code
  still tests `!== undefined` rather than truthiness or `!= "1"`. If `EDGEMICRO_LOCAL` is set to
  `"0"` or `"false"`, quota is still skipped. Eight years on, the claimed fix is absent and the
  issue is closed. This is the cleanest CLOSED-is-not-FIXED example in the set.
- Still applies today: yes for the residual bug, no for the closure.

## Case 18. Shared flow deploy reports success, then the revision goes to ERROR with `repository.FailedToLoadFile` — and three maintainers could not reproduce it

- URL: https://github.com/apigee/apigeecli/issues/276 (the companion issue
  https://github.com/apigee/apigeecli/issues/273 was closed as a duplicate of this one)
- Repo: apigee/apigeecli, owner_type = Organization. Reporter cygnus8595, NONE.
- Problem: verbatim, from the issue:
  ```sh
  apigeecli sharedflows create -n $SF_NAME -f $SF_PATH -t $GCLOUD_TOKEN -o $APIGEE_ORG
  ```
  with `$SF_PATH="./fromscratch/sharedflowbundle"` succeeds. The subsequent
  `apigeecli sharedflows deploy -n $SF_NAME -e $APIGEE_ENV -t $GCLOUD_TOKEN -o $APIGEE_ORG -r -v $REV`
  succeeds. Then:
  ```
  Status: instance "us-east1" reported error repository.FailedToLoadFile: "Failed to load file : /sharedflows/fromscratch.xml"
  ```
  And in full deployments-response form, quoted from the thread:
  ```json
  {
          "environment": "mobility-dev",
          "apiProxy": "sf-test2",
          "revision": "3",
          "deployStartTime": "1692821476473",
          "state": "ERROR",
          "errors": [
                  {
                          "code": 2,
                          "message": "instance \"us-east1\" reported error repository.FailedToLoadFile: \"Failed to load file : /sharedflows/test.xml\""
                  }
          ],
          "instances": [
                  {
                          "instance": "us-east1"
                  }
          ]
  }
  ```
  With `$SF_PATH="fromscratch/sharedflowbundle"` (no `./`) the same flow deploys cleanly.
  The reporter also notes the filename in the error changes between runs, verbatim: "once
  deployed, there's an error where it can't find the base xml file. Sometimes it has the name
  wrong, too. But only when using `./` notation. It's odd and random and really annoying me!! :)"
- Why the obvious first explanation is wrong, and there are three of them:
  1. "The bundle is missing its XML." It is not. `create` returned `"sharedFlows": ["default"]`
     and the file is present in the zip.
  2. "The CLI failed." It did not. The reporter identifies the exact weakness, verbatim: "deploy
     shows success on apigeecli (because it just checks for the deploy starting)". That is the
     same failure mode as Case 13, and it is why `"state": "ERROR"` has to be read from the
     deployments response rather than inferred from the command's exit status.
  3. "Not reproducible, therefore user error." Three apigee maintainers tested this and could NOT
     reproduce it, twice, on different days, on their own machines with the same version.
     ssvaidyanathan 2023-08-28T21:50:30Z: "Both @srinandan and I are not able to replicate the
     issue. Its working from our laptops and we use the same version". So the usual escape
     hatch was taken and it was wrong.
- The evidence that settles it is in the error string itself and nobody quoted it for a month.
  The failing path is `/sharedflows/test.xml` — note the LEADING SLASH and the absence of the
  local directory prefix `./sharedflows/test/test_flow/sharedflowbundle/`. The runtime is looking
  for a path that is neither a real bundle entry nor the path the user typed. Combined with the
  filename changing between runs, the only consistent explanation is that the stored bundle path
  was derived from the local filesystem path rather than from the bundle's own contents. That is
  a string-handling bug, and it explains every observation including the `./`-dependence, the
  randomness, and why the maintainers' clean reproductions passed.
- Evidence for the claimed cause: the reporter's own discriminating observation, quoted above
  (c) that it happens only with `./`, and his A/B test that removing `./` fixes it. The cause
  itself was never explained by a maintainer in words; it is visible in the fix.
- The resolution record is the best in the set because it shows what "fixed" actually means here.
  First attempt, MERGED and insufficient: PR #279 "bug: additional valdation for sf #276",
  merged=true, merged_at 2023-08-23T19:25:52Z, referencing commit ab2cb236. The issue stayed open
  another four weeks and the maintainers kept failing to reproduce it. That PR added validation,
  not a path fix.
  Actual fix, MERGED: commit `bug: fixes bundle errors with relative paths #294 (#299)`, authored
  2023-09-20T16:41:01Z, one second before the issue closed (closed_at 2023-09-20T16:41:02Z). The
  commit title names the cause the thread never did: relative paths.
  CONFIRMED: ssvaidyanathan released a beta, v1.124.0-beta, and cygnus8595 replied
  2023-09-20T20:31:32Z with a successful `./sharedflows/from-scratch/sharedflowbundle` create and
  deploy and a screenshot: "I downloaded the latest version and it works ... Thanks!"
  RELEASED: ssvaidyanathan 2023-09-20T21:23:46Z: "Great news! We will release the version in a
  few days as we consolidate other fixes".
  Note the order: beta -> reporter confirmation -> general release. That is the correct order and
  it is worth copying into a rubric.
- The same-day companion commit closes the loop on the exit-status problem from Case 13:
  `feat: adds wait option for sf deploys #300 (#301)`, 2023-09-20T17:46:26Z. The `--wait` flag
  exists because the default path checks only that the deploy STARTED.
- Still applies today: fixed from v1.124.0. The durable lesson is twofold: read `state` and
  `errors[]` from the deployments response, and treat "three maintainers cannot reproduce" as a
  statement about your reproduction environment, not about the reporter.

## Case 19. OAuthV2 returns `"token_type": "BearerToken"` and downstream clients send a broken Authorization header

- URL: https://github.com/apigee/apigee-api-catalog-drupal/issues/46
- Repo: apigee/apigee-api-catalog-drupal, owner_type = Organization. Reporter arunz6161, NONE.
- Problem: verbatim: "As described on the following community post, Apigee OAuth 2.0 Policy returns
  a non compliant token type causing downstream applications like SmartDocs and Swagger UI to send
  \"Authorization\" header prefixed with BearerToken."
- Why the obvious first explanation is wrong: the symptom appears at the CLIENT, as a 401 from
  something downstream, or as a broken Swagger UI. Nothing points at the token endpoint. And the
  reported behaviour looks like a gateway defect, so the instinct is to file a bug and wait. It
  is neither a bug nor a fix-me-up ticket: it is the documented default, and the whole thing is
  resolved with one element in one policy.
- The official documentation is unambiguous, quoted from the cached page
  research/pages/api-platform_reference_policies_oauthv2-policy.txt line 928:
  | Element | Value is false or absent | Value is true |
  | "token_type" property in valid token response | A non-compliant token_type value.
  { ... "token_type": "BearerToken", ... } | A compliant token_type value.
  { ... "token_type": "Bearer", ... } |
  and line 936: "**Default** | `false`: By default, the policy will exhibit certain
  non-RFC-compliant behaviors as described above."
  The fix is `<RFCCompliantRequestResponse>true</RFCCompliantRequestResponse>` (element documented
  at line 917-919).
  Three other rows of that same table matter and are usually missed: `Cache-Control` is absent by
  default and becomes `no-store` plus `Pragma: no-cache` when true; `expires_in` and
  `refresh_token_expires_in` are QUOTED STRINGS by default and become numbers when true; and an
  expired-refresh-token error is `{"ErrorCode": "InvalidRequest", "Error": "Refresh Token
  expired"}` by default versus `{"error": "invalid_grant", "error_description": "refresh token
  expired"}` when true. Switching the element on changes error shapes, not just one field, so it
  is a behaviour change for every client of that token endpoint.
- Evidence level (a) official documentation. The issue itself is evidence level (d) — it is a
  pointer to a community post, and the drupal maintainers' comments are about SmartDocs, not
  about the gateway.
- The documentation history is the interesting part and is why the issue is worth keeping. The
  behaviour was correct-but-undocumented. cnovak (COLLABORATOR) 2019-11-06: "The documentation
  about this issue is now explained on the Edge OAuthV2 Policy page, Non-RFC-compliant behavior
  section." The doc bug was b/141752334, opened by the reporter, and only closed on 2020-12-08:
  "doc bug b/141752334 is now fixed." Roughly 14 months between "documentation updated" and the
  underlying doc bug actually closed.
- Resolution: CONFIRMED WORKING by the maintainer, and it is a documentation resolution, not a
  code change. cnovak 2020-04-23: "Here is an [example of a RFC compliant Apigee OAuth proxy]
  for anyone looking for a solution." The apigeecli-side SmartDocs fix was a separate track:
  "This feature will be in the next release of SmartDocs Drupal Angular application."
  The issue is still OPEN — which is correct, because the drupal workaround is not a gateway fix.
- Still applies today: the non-compliant default still applies unless
  RFCCompliantRequestResponse is set. The ErrorCode/Error vs error/error_description shape
  difference is the one most likely to catch an integrator out today.

## Case 20. Quota policy lint error caused by attaching the same quota to mutually exclusive flows

- URL: https://github.com/apigee/apigeelint/issues/168
- Repo: apigee/apigeelint, owner_type = Organization. Reporter karsten-wagner, NONE.
- Problem: rule PO023 flags a proxy that attaches the same Quota policy more than once.
  Verbatim: "I have a setup with three different proxy sections/files, each using the same quota
  in 5 mutually exclusive flows. The rule simply counts all of them (so 15 in total) and raises an
  error that it's attached more than once. Neither three different scopes, nor the mutually
  exclusive flow setup has been considered - so this creates a false positive."
- Why the obvious first explanation is wrong: the lint message is literally "the same quota is used
  more than once", which sounds like a genuine double-counting defect that would inflate the
  quota. An agent that believes the message will tell the customer to remove the duplicates, which
  would BREAK a correct design: the flows are mutually exclusive at runtime, so each request
  consumes exactly one counter. The message describes the bundle's static structure, not runtime
  counting. Compare with the official Quota versus SpikeArrest guidance, which is explicit that
  the two policies serve different purposes and that SpikeArrest "Smoothing is not coordinated
  across Message Processors".
- The reporter extended the case himself, and the extension is the part that generalises: the
  same false positive appears across mutually exclusive TARGETS. Verbatim, 2021-08-05: "Recently
  it turns out this behavior also applies when multiple targets exist. We are using the same quota
  policy in two different targets within the same proxy and the rule complains the quota is used
  twice... Similar to flows, targets are mutually exclusive in the routing, hence apigeelint should
  not consider the quota to be used twice."
- Evidence level: (b) maintainer statement for the fix, plus (a) official documentation for why
  mutual exclusion is the point.
- Resolution: the cleanest full chain in the set, and it took a long time. MERGED and RELEASED:
  ssvaidyanathan (COLLABORATOR) 2023-03-11T00:43:57Z, "Released v2.36.0 with a fix for this. Can
  you please try it out? It looks for the policy and checks if its across flows or across
  ProxyEndpoint or TargetEndpoint. If its within the same flow, it checks if the Condition tag is
  same." That description is a precise statement of the correct algorithm, and note the last
  clause: within one flow, two attachments with DIFFERENT `<Condition>` are also fine.
  CONFIRMED by both reporters three days later: karsten-wagner, "I can confirm it works now as
  expected. Thanks for the fix!" and samcrutt9900, "I can also confirm it is now working as
  expected."
  Issue CLOSED 2023-03-11T00:38:01Z, state_reason completed. Reported 2020-07-17, so the gap
  from report to fix is 2 years 8 months.
- Note the connection to Case 2: PO023 is the same plugin that crashed outright on a Quota policy
  attached to a FaultRule in 2025. That crash was fixed in PR #528; the flow/target awareness
  described above was added later. Both were needed before the rule was usable.
- Still applies today: no, from v2.36.0. The durable rule is that a static count of policy
  attachments says nothing about runtime counting; mutual exclusion lives in the Condition and in
  the routing.

## Case 21. A linter fix shipped, failed to fix the report, shipped again, and the reporter diagnosed the second defect himself

- URL: https://github.com/apigee/apigeelint/issues/551
- Repo: apigee/apigeelint, owner_type = Organization. Reporter dangrasso, NONE.
- Problem: verbatim error string,
  ```
  error CC005 : Invalid Condition - cannot parse
  ```
  triggered by a perfectly ordinary condition:
  ```xml
  <Condition>notValidJson == true</Condition>
  ```
  Reporter: "This is likely a regression due to the fix in
  https://github.com/apigee/apigeelint/pull/544/files#diff-...R483. Would an option be to
  explicitly replace only `not(` and `not ` but not everything starting with `not`?"
  Note the tell: the variable is NAMED `notValidJson`. The linter is treating the leading `not` in
  an identifier as the `NOT` operator. The bundle is fine. The version ladder the reporter
  measured is the key evidence: `2.67.0 Pass`, `2.68.0 Fail`, `2.69.0 Fail`.
- Why the obvious first explanation is wrong: "Invalid Condition - cannot parse" says the
  condition is malformed, so the instinct is to rewrite the condition. The condition parses
  correctly at runtime; it is already deployed and working. The regression is in the tool, and it
  arrived with a release, so the version that matters is apigeelint's.
- Why the obvious fix was wrong too, which is the reason this case is worth keeping: the
  maintainer's first correction fixed the example and not the class of bug. dangrasso, verbatim:
  "It actually doesn't work. I don't understand why this time ... I tried your new regex directly
  on my condition and as expected it doesn't replace the `not` this time. But still CC005 is marked
  as failed for that condition block."
  He then found the residual himself, with a file, a line number and a regex, verbatim: "I see
  that this replacement still happens a few lines above:
  https://github.com/DinoChiesa/apigeelint/blob/bc113b92f6f39ae7868f27f8b6f4480c32898514/lib/package/TruthTable.js#L484
  The * quantifier will match on 0 or more occurrences of the space, so any condition starting with
  a variable starting with not... will be affected. You probably want to match only on `^ *NOT +` to
  ensure there is a space after the not."
  The first fix addressed one call site; the pattern existed at more than one.
- Evidence level: (b) maintainer statements; the reporter's diagnosis is (c) in the precise sense
  that it identified a specific construct, was accepted by the maintainer ("Yes, thanks for the
  diagnosis"), and the follow-up release was cut the same day.
- Resolution: MERGED and RELEASED TWICE, and this is the point. v2.69.0 (released 2025-06-23,
  announced by ssvaidyanathan "v2.69.0 is released") did NOT fix it, and the reporter said so
  publicly. v2.69.1 was released 2025-06-27 with "released as v2.69.1". Issue CLOSED
  2025-06-27T15:18:24Z, state_reason completed.
  NOT CONFIRMED: the last comment is DinoChiesa at 2025-06-27T17:18:18Z, "How 'bout now , Dan?
  Works?" — asked 2 hours AFTER the issue was closed, and the reporter never answered. So the
  strongest defensible claim is MERGED AND RELEASED, not CONFIRMED. Anyone asserting "v2.69.1
  fixed it" is going one step beyond the record.
- Still applies today: mostly no, and CC005 itself has been rewritten. The plugin is now
  `CC005-unterminatedStrings.js` with the message "Conditions should not include strings that are
  unterminated.", which is a different rule from the 2025 "Invalid Condition - cannot parse". So
  the specific error string no longer appears.
- My own source-level follow-up, recorded because it is a live observation and NOT a
  maintainer-confirmed finding (evidence level (d), my own verification): the leading-NOT
  normalization in today's `lib/package/TruthTable.js` reads
  ```js
  expression = expression.replace(new RegExp("^ *NOT\b", "i"), " ! "); // leading NOT
  ```
  In JavaScript, `\b` inside a double-quoted string literal is the BACKSPACE escape, not a regex
  word boundary. I extracted that exact line from the current source and evaluated it under Node:
  `new RegExp("^ *NOT\b", "i").test("NOT (a == b)")` returns false, while
  `new RegExp("^ *NOT\\b", "i").test("NOT (a == b)")` returns true. The same run confirmed the
  intended behaviour of the corrected regex on the reported input,
  `.test("notValidJson == true")` returning false. As written, that line never matches, so the
  leading-`NOT` normalization is inert today. I did not run apigeelint end to end and I am NOT
  claiming this produces a user-visible lint failure; CC005 has been replaced and other code paths
  may normalize conditions. Flagging it as a discrepancy to verify, not as a confirmed defect.

---

## Fault code validation

Every Apigee fault code quoted above was checked against
`.agents/skills/apigee-support-core/references/error-codes.md`:

| String quoted | Where from | In the index? |
| --- | --- | --- |
| `steps.javacallout.JavaCalloutInstantiationFailed` | apigee-deploy-maven-plugin#155, quoted from the reporter relaying Apigee support | YES. Index line 243 carries `JavaCalloutInstantiationFailed`, message `Failed to instantiate the JavaCallout Class [classname]`. The `steps.javacallout.` prefix is the standard policy-fault prefix, consistent with existing usage in scenarios/medium.md |
| `policies.ratelimit.SpikeArrestViolation` (429) and `policies.ratelimit.QuotaViolation` (500) | used only in the comparing Quota/SpikeArrest discussion | YES, index lines 43 and 42. Not quoted as observed strings, only as the documented codes behind the guidance |
| `error CC005 : Invalid Condition - cannot parse` | apigeelint#551 | NOT an Apigee fault code. It is a lint tool message, correctly excluded from the fault index |

Two strings quoted above are real and verbatim but are NOT in the fault index, because the index
covers policy fault codes and deployment errors raised by policy validation. Both are recorded
here and neither was used as a fault code in a scenario:

- `repository.FailedToLoadFile` / `Failed to load file : /sharedflows/test.xml` (Case 18). This
  is a runtime deployment error string produced by the Apigee X message processor instances, seen
  in the deployments response `errors[]` array with `"code": 2`. Verified in the primary source
  only. Not present in `research/pages/` either.
- `config.json ... null: MojoExecutionException` (Case 14). A Maven plugin message whose detail
  is literally `null`. Not an Apigee string at all.

---

## Summary table

| # | Case | Repo | Resolution | Evidence |
| --- | --- | --- | --- | --- |
| 1 | PO035 rejects Quota async config the runtime accepts | apigeelint#443 | MERGED (PR #445) | b, a |
| 2 | PO023 crashes on Quota in a FaultRule | apigeelint#527 | MERGED (PR #528) | b |
| 3 | UNABLE_TO_VERIFY_LEAF_SIGNATURE, no CA option | apigeetool-node#6 | MERGED + CONFIRMED, issue still open | b, c |
| 4 | unable to verify the first certificate behind a corporate proxy | apigeetool-node#33 | PROPOSED and explicitly failed, open | c for boundary, d for mechanism |
| 5 | mTLS provision succeeds, verification 400s | apigee-remote-service-cli#261 | NONE, open, 0 comments | d (source verified by me) |
| 6 | JavaCalloutInstantiationFailed from a filtered jar | apigee-deploy-maven-plugin#155 | NONE, open | c for mechanism, d for this reporter |
| 7 | Basepath conflict, maintainer's first theory also wrong | apigeetool-node#57 | PROPOSED (v0.6.6), open | b |
| 8 | kvms export only covers proxy scope | apigeecli#540 | MERGED (commit dd7b9e17) | b |
| 9 | Shared flow partial deploy read as success | apigeetool-node#151 | NONE, open, no maintainer in 7 yrs | d for cause, c for mitigation |
| 10 | BN003 demands a cross-proxy PopulateCache | apigeelint#480 | OPEN, fix declined on purpose | b, a |
| 11 | Quota CountOnly/EnforceOnly pairing rule withdrawn | apigeelint#475 | CLOSED, no rule shipped | b |
| 12 | TD006 and TD012 cannot both be satisfied | apigeelint#526 | MERGED + RELEASED v2.67.0, verified in source | b, a |
| 13 | Shared flow deploy fails, exit code 0 | apigeecli#644 | MERGED + RELEASED v2.10.1 + CONFIRMED | b, c |
| 14 | Maven error message is literally `null` | devrel#533 | NONE, open, design undecided | b for mechanism |
| 15 | PO042 false positive on UseEffectiveCount | apigeelint#590 | MERGED + RELEASED v2.77.1 + CONFIRMED | a, b |
| 16 | kubectl wait Unauthorized mid-install | apigee-hybrid-install#30 | PROPOSED only, cause withdrawn by reporter | c, b |
| 17 | Quota plugin local-mode check reversed | microgateway-plugins#86 | CLOSED by the reporter, claimed fix absent from source | b |
| 18 | Deploy reports success, revision ERROR | apigeecli#276 | MERGED + RELEASED v1.124.0 + CONFIRMED | c, b |
| 19 | token_type BearerToken breaks downstream clients | apigee-api-catalog-drupal#46 | CONFIRMED, documented, issue open | a |
| 20 | PO023 counts mutually exclusive flows | apigeelint#168 | MERGED + RELEASED v2.36.0 + CONFIRMED x2 | b, a |
| 21 | CC005 regression, first fix incomplete | apigeelint#551 | MERGED + RELEASED v2.69.1, NOT confirmed | b |

---

## PROPOSED SCENARIOS

Eight scenarios, MED-23 through MED-30, appended to `scenarios/medium.md` in the file's existing
section structure. They are written in the same file rather than here; this section is the index
into them.

- **MED-23** A linter rule demands a cache populate that would break the cache it is protecting.
  Source: apigee/apigeelint#480. Open, maintainer declined to fix. Tests whether the agent reads
  cache key scope or just silences the rule.
- **MED-24** A linter release breaks every working rate limit policy in the estate. Source:
  apigee/apigeelint#590. Fixed in v2.77.1, reporter confirmed. Tests whether the agent checks the
  linter version before editing a bundle, and whether it trusts a lint message over the policy
  reference.
- **MED-25** The linter says a quota is used twice, and the quota is used once per request. Source:
  apigee/apigeelint#168. Fixed in v2.36.0, two reporters confirmed. Tests the difference between
  static attachment counting and runtime counting, including conditions and target endpoints.
- **MED-26** A deployment fails with a Java callout error, and the build tool corrupted the
  artifact. Source: apigee/apigee-deploy-maven-plugin#155. Still open. Uses
  `steps.javacallout.JavaCalloutInstantiationFailed`, verified in the index. Tests whether the
  agent inspects the artifact instead of accepting the support boundary or retrying.
- **MED-27** The deployment tool says it succeeded, and the revision is in ERROR. Source:
  apigee/apigeecli#276, fixed and confirmed. Deliberately avoids the unindexed
  `repository.FailedToLoadFile` string as a fault code and instead teaches the three-signal
  distinction. Tests whether the agent treats "maintainers could not reproduce it" as a conclusion.
- **MED-28** Provisioning over mutual TLS succeeds, then the tool fails its own verification.
  Source: apigee/apigee-remote-service-cli#261. Open, unconfirmed, source-verified. Tests product
  and runtime handling, because the same 400 fails the command on SaaS and OPDK and is a warning on
  hybrid.
- **MED-29** The same TLS error, two different causes, and the accepted fix works for one of them.
  Source: apigee/apigeetool-node#6 and #33. Tests whether the agent carries an answer from one
  case into the other, which is the highest-value trap in the whole set.
- **MED-30** The token endpoint is correct and the client is sending a malformed header. Source:
  apigee/apigee-api-catalog-drupal#46, corroborated by the official OAuthV2 policy reference.
  Tests whether the agent looks at what the token endpoint returned rather than at the 401
  downstream, and whether it audits all four response fields that compliance changes.

Scenarios already present and NOT duplicated: MED-21 already covers apigeelint#526 and MED-17
already covers apigee-deploy-maven-plugin#213, so Case 12 and Case 6 were reworked into different
angles rather than repeated. MED-09 already covers the SpikeArrest effective-count configuration,
so MED-24 is built on the linter regression rather than the configuration.

### Coverage against the requested topic list

| Requested topic | Covered by |
| --- | --- |
| OAuthV2 policy failures and exact error strings | MED-30, plus MED-16 which already existed |
| Quota counting more than expected, SpikeArrest, the Quota/SpikeArrest confusion | MED-25, MED-24; MED-09 and HARD-08 already existed |
| Response cache stale or wrong content, cache key problems | MED-23; MED-04 already existed |
| TLS, keystore, certificate, mTLS | MED-28, MED-29; MED-08 and HARD-03 already existed |
| Deployments reporting success but not taking effect | MED-27, MED-26; MED-17 already existed |
| Shared flow and flow hook resolution failures | MED-27 (shared flow bundle path). Flow-hook specific resolution failures did not yield a case with verbatim errors and this was the weakest area of the public record; MED-25 records the CountOnly/EnforceOnly-across-flow-hooks pattern instead |
| KeyValueMap and target server resolution | Partial. Case 8 (apigeecli#540, KVM export scope) and Case 12 (target server, already MED-21). No hybrid-specific KVM resolution failure with a verbatim error was found in the public record |
| Management API and gcloud automation failures | MED-27, Case 16 (`kubectl wait` Unauthorized). No gcloud flag or output-format change case was found; the public GitHub record for that lives in issue trackers outside the apigee organisation |
| Hybrid runtime, Kubernetes, Istio | MED-28, Case 16. No Istio-specific runtime problem with a verbatim error surfaced publicly |
| Latency regressions and timeouts | Weakest area. Only the Java callout instantiation timeout message (MED-26) and the Quota anti-pattern guidance were found. Nothing was found in the public record strong enough to build a latency scenario from |
| apigeelint false positives conflicting with runtime | MED-23, MED-24, MED-25. Best-covered area by a wide margin |
| Linter/validator disagreement, bundle vs UI, YAML vs XML | MED-24 (linter vs deployed reality), MED-27 (CLI output vs UI state) |
| A popular community answer that turned out wrong | MED-29 by construction; also Case 14, where Apigee support redirected the reporter to the wrong component |

### What did not turn up, stated plainly

No public case in the apigee GitHub organization was found for: Istio-specific hybrid runtime
failures with a verbatim error; gcloud CLI flag or output-format changes breaking Apigee
automation; latency regressions with an attributable cause; or hybrid KeyValueMap resolution
failures. The repos that would be expected to carry those (apigee-internal/microgateway is
internal, and the gcloud surface is covered by Google Cloud SDK trackers rather than the apigee
organisation) either are not public or did not contain qualifying reports. Fabricating them would
have been the wrong move.
