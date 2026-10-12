# Apigee known-issues register — expanded coverage sweep

Source of record: `https://cloud.google.com/apigee/docs/release/known-issues`
(the "This section lists known issues for Apigee components" register, reachable from
Apigee release notes).

**Register re-fetched live on 2026-10-12 and byte-compared against the local cache.**
`pages/ki-live-20261012.txt` is identical to the pre-existing
`pages/apigee-known-issues.txt` (85178 bytes). The cache was current, so this pass
adds no new entries to the register itself — it harvests the 98 entries that four
earlier passes did not touch.

- **Register entries read in this pass: 102** (all of them, parsed by
  `research/parse_knownissues.py` into `research/ki-entries.json`).
- **Previously used: 4** — 465834046, 479872706, 543171828, 471125841.
- **Newly harvested: 98.**
- Open: 31. Fixed: 71.
- By product, using my own grouping of the register's Affects column (**derived, not the
  register's own filter chips**, which are finer: API hub, Monetization, Archive deployments,
  UI, Documentation, Connectors and so on each appear as their own chip):
  Apigee 34, Apigee hybrid (+Apigee) 62, UI 2, All products 1, Apigee in VS Code 1,
  Integrated portal 1, Apigee Emulator 1.
- Of the 102, I classify **15 as LIMITATION** (documented design behaviour), **4 as
  LIMITATION-with-alarming-symptom**, and **83 as BUG**. The LIMITATIONs are the valuable
  ones for evaluation, because the correct answer is "this is how it is designed" rather than
  "wait for a patch".

### Register traps found while working this

1. **The page header lies about scope.** It reads "*This page applies to **Apigee**
   and **Apigee hybrid***" and offers a link to Edge for Private Cloud docs — but the
   table contains no Private Cloud rows. Every `Edge for Private Cloud` row in this
   table would be a fabrication; there are none. OPDK known issues live in the release
   notes on `docs.apigee.com`, not here.
2. **The status cell is a bare colour span.** `<span style="color:#ec407a">OPEN</span>`
   for OPEN and `<span style="color:#008000">FIXED</span> in <version>` for FIXED, so a
   naive "first line after the affects column" parse silently swallows the FIXED-IN
   version. See `research/parse_knownissues.py`, which detects status by the colour span
   instead.
3. **Filter chips are not table headers.** The row of product/status chips
   (`Apigee 1-10 hybrid 1.16 FIXED OPEN …`) is rendered inline in the body and contains
   bare version numbers. Nothing in the register is addressable by filter in a stable
   URL; there is one table and it must be read whole.
4. **`pandoc` flattens the table and drops nothing, but it also does not keep rows
   aligned.** Row boundaries are only recoverable because issue IDs are the sole

### Two genuine defects in the register HTML itself

Found while cross-checking the flattened page against the raw HTML. Both silently lose
issues for any automated reader, and neither is announced anywhere.

- **Entry 421402073 is missing its closing `</td>`.** The affects cell is emitted as
  `<td>Apigee in VS Code` with no terminator, so a regex that pairs `<td>` with `</td>`
  swallows that cell and the next one and the row arrives with three cells instead of four.
  Fixed by splitting cells on open-tag positions rather than pairing them.
- **The page is not well-nested.** 133 `<tr>` opens against 131 `</tr>` closes, and
  several description cells contain a nested `<table>`. A LIFO stack therefore mispairs
  rows and drops issue **282997216** entirely. Verified that the ID-to-description mapping
  is still correct for all 101 entries the HTML parser does recover, by diffing every
  description against the flattened-text parse (all 55 differences are markdown-link
  rendering only, no content divergence).

Both of these are why `research/parse_knownissues.py` works from the flattened text, where
issue IDs are the sole nine-digit lines on the page and row boundaries are unambiguous.

---

## Table of every entry read (all 102)

Verbatim from the register unless marked otherwise. BUG vs LIMITATION is my classification
and is the judgement that matters most: a LIMITATION is documented design behaviour where the
correct answer is "this is working as designed", which makes a far better evaluation scenario
than a bug whose correct answer is "upgrade".

- **BUG** (83): a defect that was fixed, or is fixable.
- **LIMITATION** (15): documented behaviour. The correct answer is to explain the design.
- **LIMITATION+symptom** (4): a real limit that also produces an alarming error message, so
  it gets misdiagnosed as a defect.

| Issue ID | Product | Affects (component / version) | Status | Kind | Symptom or design statement (verbatim) | Resolution / workaround | Used? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 543171828 | Apigee hybrid (+Apigee) | hybrid 1.14.7, hybrid 1.15.7, and hybrid 1.16.8 | FIXED in hybrid 1.16.9; closed | **BUG** | The apigee-logger DaemonSet is not scheduled on any node, so Apigee runtime logs stop reaching Cloud Logging. | workaround published; FIXED in hybrid 1.16.9 | used |
| 534420582 | Apigee hybrid (+Apigee) | Apigee; Apigee hybrid | FIXED in hybrid 1.15.8; closed | **BUG** | JSON payloads with duplicate keys may be interpreted differently by Apigee policies and by backend services, which can weaken content-based security checks. | workaround published; FIXED in hybrid 1.15.8 | NEW |
| 523085517 | UI | UI | OPEN; OPEN | **BUG** | The Apigee debug trace view can flicker or render slowly for large debug sessions. | none published; issue still OPEN | NEW |
| 515424331 | Apigee hybrid (+Apigee) | hybrid 1.16.3 | FIXED in hybrid 1.16.4; closed | **BUG** | The apigee-pull-push.sh script fails on 1.16.3 because some images carried over from 1.16.2 were not retagged with the 1.16.3 tag in the gcr.io/apigee-release/hybrid/ repository. | workaround published; FIXED in hybrid 1.16.4 | NEW |
| 513032450 | Apigee hybrid (+Apigee) | hybrid 1.16.2 | FIXED in hybrid 1.17.1; closed | **BUG** | apigee-connect-agent first tether wedges on RKE2-on-GKE clusters after Go 1.26.3 toolchain bump. | workaround published; FIXED in hybrid 1.17.1 | NEW |
| 512866352 | Apigee hybrid (+Apigee) | hybrid 1.16.2 | FIXED in hybrid 1.16.3; closed | **BUG** | External secret stores (such as HashiCorp Vault) do not work with the apigee-redis image due to a glibc version mismatch. | workaround published; FIXED in hybrid 1.16.3 | NEW |
| 499322601 | Apigee hybrid (+Apigee) | hybrid 1.16.0-hotfix.1,; hybrid 1.15.2,; hybrid 1.14.4 | FIXED in hybrid 1.16.2; closed | **LIMITATION** | Apigee will not support a forward proxy which has the Basic Auth credential enforced. | FIXED in hybrid 1.16.2; no workaround published | NEW |
| 496552286 | Apigee | Apigee | OPEN; OPEN | **BUG** | Deployment fails for MCP Discovery Proxies in regions with capacity limitations. | none published; issue still OPEN | NEW |
| 495305258 | Apigee | Apigee (Marketplace Solution) | OPEN; OPEN | **BUG** | Deployment disruption for Apigee Drupal Portal via Cloud Marketplace | none published; issue still OPEN | NEW |
| 490308770 | Apigee hybrid (+Apigee) | hybrid 1.12.x, hybrid 1.15.x, hybrid 1.16.0 | FIXED in 1.16.0-hotfix.1 and 1.15.2; closed | **BUG** | Authenticated HTTP proxy configurations fail due to malformed URL strings in Helm templates. | workaround published; FIXED in 1.16.0-hotfix.1 and 1.15.2 | NEW |
| 484366184 | Apigee hybrid (+Apigee) | hybrid 1.14.x, hybrid 1.15.x | FIXED in hybrid 1.16.0; closed | **BUG** | Apigee Hybrid versions 1.14 and 1.15 encounter a crash loop in the apigee-ingressgateway-manager when Kubernetes Gateway API v1.4.0 or newer is utilized. | workaround published; FIXED in hybrid 1.16.0 | NEW |
| 482209901 | Apigee hybrid (+Apigee) | hybrid 1.16.0 | FIXED in hybrid 1.16.0-hotfix.1; closed | **BUG** | Proxy deployment not completing due to missing RBAC permissions in Hybrid v1.16.0. | workaround published; FIXED in hybrid 1.16.0-hotfix.1 | NEW |
| 482077193 | Apigee hybrid (+Apigee) | hybrid 1.15.0 and later | FIXED in 1.16.0-hotfix.1; closed | **BUG** | Proxy chaining fails with 404 route_not_found in multi-organization, single-namespace configurations. | workaround published; FIXED in 1.16.0-hotfix.1 | NEW |
| 480997525 | Apigee | Apigee 1-17-0-apigee-1 | FIXED in Apigee 1-17-0-apigee-2; closed | **BUG** | Proxy calls fail with The URI contain illegal characters error after Netty upgrade. | FIXED in Apigee 1-17-0-apigee-2; no workaround published | NEW |
| 479872706 | Apigee hybrid (+Apigee) | hybrid 1.16.0 (EKS with WIF and forward proxy) | FIXED in hybrid 1.16.0-hotfix.1; closed | **BUG** | Unable to load API Products, Apps, and Developers after migrating data to Apigee Hybrid 1.16. | workaround published; FIXED in hybrid 1.16.0-hotfix.1 | used |
| 479040521 | Apigee hybrid (+Apigee) | hybrid 1.16.0 | FIXED in hybrid 1.16.0-hotfix.1; closed | **BUG** | apigee-operator-guardrails-sa not created on AKS/EKS with Federated Workload Identity. | workaround published; FIXED in hybrid 1.16.0-hotfix.1 | NEW |
| 471125841 | Apigee hybrid (+Apigee) | hybrid 1.14.x,hybrid 1.15.x | FIXED in hybrid 1.16.x; closed | **BUG** | When a new API proxy revision is created and deployed with an updated io.timeout.millis value, the new value might not be consistently honored. | workaround published; FIXED in hybrid 1.16.x | used |
| 465834046 | Apigee hybrid (+Apigee) | hybrid 1.14.3, hybrid 1.15.1, and hybrid 1.16.0 and later for upgrades | FIXED in hybrid 1.14.3, hybrid 1.15.1, and hybrid 1.16.0 for fresh installs; closed | **BUG** | cert-manager versions 1.18+ changed the default for the private key rotation policy from Never to Always. If the private key for apigee-ca is rotated it will impact traffic | workaround published; FIXED in hybrid 1.14.3, hybrid 1.15.1, and hybrid 1.16.0 for fresh… | used |
| 462685598 | UI | UI | OPEN; OPEN | **BUG** | The Apigee UI currently does not offer the option for provisioning Apigee orgs with a Google-owned and Google-managed encryption key. | none published; issue still OPEN | NEW |
| 460431753 | Apigee hybrid (+Apigee) | Apigee, Apigee hybrid | OPEN; OPEN | **BUG** | Apigee Model Armor policies are not supported with WebSockets. | none published; issue still OPEN | NEW |
| 458417250 | Apigee | Apigee 1-16-0-apigee-4 | FIXED in Apigee 1-16-0-apigee-6; closed | **BUG** | Message Processor returns 500 error with "Duplicate Header "authorization"". | workaround published; FIXED in Apigee 1-16-0-apigee-6 | NEW |
| 451841788 | Apigee hybrid (+Apigee) | hybrid 1.14.3 and hybrid 1.15.1 | FIXED; closed | **BUG** | Apigee hybrid requires the mintTaskScheduler.serviceAccountPath property even when Monetization is not enabled. | workaround published; FIXED | NEW |
| 451375397 | Apigee hybrid (+Apigee) | hybrid 1.14.3 | FIXED in hybrid 1.15.1; closed | **BUG** | The apigee-pull-push.sh script can return a No such image error message, for example: | workaround published; FIXED in hybrid 1.15.1 | NEW |
| 449012244 | Apigee | Apigee | OPEN; OPEN | **BUG** | Use separate target endpoint definitions for SSE (server sent-event) targets. Mixing SSE and non-SSE target endpoints together might result in inconsistent behavior such as empty response.content flow variable… | none published; issue still OPEN | NEW |
| 445936920 | Apigee | Apigee 1-16-0-apigee-2 and later | OPEN; OPEN | **BUG** | Previously undetected DNS configuration problems might now cause DNS errors. Apigee removed the automatic DNS fallback functionality that was in 1-16-0-apigee-2. This removal eliminates the platform's resilien… | none published; issue still OPEN | NEW |
| 438850078 | Apigee | Apigee | OPEN; OPEN | **BUG** | An infinite recursion occurs within the OASValidation policy when a backend response contains a discriminator type that is the same as the parent schema. This problem can lead to a StackOverflowError. | none published; issue still OPEN | NEW |
| 433759657 | Apigee | Apigee | FIXED in 1-16-0-apigee-3 or later; closed | **BUG** | Following the upgrade to 1-16-0-apigee-3, some Apigee organizations may encounter HTTP 500 errors stemming from a java.lang.NoClassDefFoundError within a Java Callout policy. The error appears similar to the f… | FIXED in 1-16-0-apigee-3 or later; no workaround published | NEW |
| 432315283 | Apigee | Apigee | OPEN; OPEN | **BUG** | When updating a keystore or truststore without creating a new keystore or truststore, runtime updates may fail and cause the following intermittent error: | none published; issue still OPEN | NEW |
| 422757662 | Apigee hybrid (+Apigee) | Apigee 1-15-0-apigee-5; hybrid 1.15.0 | FIXED in Apigee 1-15-0-apigee-7 and Apigee 1-15-0-apigee-8; closed | **BUG** | x-b3 headers not available when DistributedTrace is disabled | FIXED in Apigee 1-15-0-apigee-7 and Apigee 1-15-0-apigee-8; no workaround published | NEW |
| 421402073 | Apigee in VS Code | Apigee in VS Code | OPEN; OPEN | **LIMITATION** | Google Authentication in policies is not supported in Apigee in Visual Studio Code (VS Code) | none published; issue still OPEN | NEW |
| 421190799 | Apigee | Apigee | FIXED in Apigee 1-15-0-apigee-7; closed | **LIMITATION** | The Apigee Extension Processor does not support more than 100kb of data processing as part of request and response body events. | FIXED in Apigee 1-15-0-apigee-7; no workaround published | NEW |
| 420985360 | Integrated portal | Integrated portal | OPEN; OPEN | **LIMITATION+symptom** | SmartDocs | none published; issue still OPEN | NEW |
| 419856132 | Apigee hybrid (+Apigee) | hybrid 1.14.2 and newer | FIXED in hybrid 1.14.3 and hybrid 1.15.0; closed | **BUG** | If gateway.networking.k8s.io/v1 is installed in your cluster,apigee-ingressgateway-manager may fail to upgrade. | workaround published; FIXED in hybrid 1.14.3 and hybrid 1.15.0 | NEW |
| 418274570 | Apigee hybrid (+Apigee) | hybrid 1.16.0 | FIXED; closed | **BUG** | Hybrid release notes page not updated with 1.16.0-hotfix.1 information. | FIXED; no workaround published | NEW |
| 416634326 | Apigee hybrid (+Apigee) | hybrid 1.14.2 and later | FIXED in hybrid 1.14.3 and hybrid 1.15.1; closed | **BUG** | Presence of istio.io Custom Resource Definitions (CRDs) in an Apigee hybrid cluster may cause failure in apigee-ingressgateway-manager pods. | workaround published; FIXED in hybrid 1.14.3 and hybrid 1.15.1 | NEW |
| 415061771 | Apigee hybrid (+Apigee) | Apigee; Apigee hybrid | OPEN; OPEN | **BUG** | Controller Error Message "Object has been modified" | none published; issue still OPEN | NEW |
| 414499328 | Apigee hybrid (+Apigee) | hybrid 1.14.1 | FIXED in hybrid 1.14.3 and hybrid 1.15.0; closed | **BUG** | ApigeeTelemetry can become stuck in creating state. | workaround published; FIXED in hybrid 1.14.3 and hybrid 1.15.0 | NEW |
| 412740465 | Apigee hybrid (+Apigee) | hybrid 1.14.0 and later | FIXED in hybrid 1.14.3 and hybrid 1.15.1; closed | **BUG** | Starting with Apigee hybrid version 1.14.0, automatic addition of Zipkin trace headers (x-b3-*) has been removed. | FIXED in hybrid 1.14.3 and hybrid 1.15.1; no workaround published | NEW |
| 405936071 | Apigee hybrid (+Apigee) | hybrid 1.15.0 | FIXED in hybrid 1.15.1; closed | **BUG** | When metrics.serviceAccountRef or metrics.serviceAccountSecretProviderClass is specified in the overrides.yaml file, the telemetry role will target the wrong service account. | workaround published; FIXED in hybrid 1.15.1 | NEW |
| 402739748 | Apigee | Apigee | OPEN; OPEN | **LIMITATION+symptom** | APIproducts are limited to 50 paths. If you add additional paths, an error message is displayed: Operation group limit of 51 exceeded in Operation Config | none published; issue still OPEN | NEW |
| 401746333 | Apigee hybrid (+Apigee) | Apigee; hybrid 1.12.4; hybrid 1.13.3; hybrid 1.14.1 | FIXED; closed | **BUG** | The Nimbus JOSE + JWT library may cause a java.lang.ClassCircularityError when using a JavaCallout policy . | FIXED; no workaround published | NEW |
| 401624396 | Apigee hybrid (+Apigee) | hybrid 1.13.x; hybrid 1.14.x | OPEN; OPEN | **BUG** | The Apigee restore job fails while restoring GCP or HYBRID Cloud Providers backups taken from a multi-region setup. This issue does not affect CSI restore. | none published; issue still OPEN | NEW |
| 397693324 | Apigee hybrid (+Apigee) | hybrid 1.14.0; hybrid 1.14.1 | FIXED in hybrid 1.14.2; closed | **BUG** | ESS and non-ESS Multi-region Cassandra credential rotation will fail in every region except the first. | workaround published; FIXED in hybrid 1.14.2 | NEW |
| 392135466 | Apigee hybrid (+Apigee) | hybrid 1.14.0 | OPEN; OPEN | **LIMITATION** | Proxy chaining with mTLS is not supported when using Enhanced per-environment proxy limits | none published; issue still OPEN | NEW |
| 391861216 | Apigee hybrid (+Apigee) | hybrid 1.13.x; hybrid 1.14.x | FIXED in hybrid 1.13.3 and hybrid 1.14.1; closed | **BUG** | Restarting Cassandra pods on a Hybrid cluster that has been restored using the GCP or HYBRID Cloud Providers will cause the pods to go into the CrashLoopBackoff state. This issue does not affect CSI restore. | workaround published; FIXED in hybrid 1.13.3 and hybrid 1.14.1 | NEW |
| 391140293 | Apigee hybrid (+Apigee) | Apigee; Apigee hybrid | FIXED; closed | **BUG** | Scaling of Istio ingress pods can cause a 503 error. | workaround published; FIXED | NEW |
| 388608440 | Apigee hybrid (+Apigee) | hybrid 1.11.x; hybrid 1.12.x | FIXED in hybrid 1.12.4 and later; closed | **BUG** | The Apigee backup job doesn't clean up the Cassandra intermediate snapshots. | FIXED in hybrid 1.12.4 and later; no workaround published | NEW |
| 384937220 | Apigee hybrid (+Apigee) | hybrid 1.14.0 | FIXED; closed | **BUG** | Helm release creation may fail when there are multiple virtual hosts. | workaround published; FIXED | NEW |
| 383372330 | Apigee Emulator | Apigee Emulator versions 1.13.0 up to but not including 1.15.1 | FIXED in Apigee Emulator versions 1.15.1 and later; closed | **BUG** | All proxy deployments fail locally with error messages including Error parsing deployment report as JSON: | FIXED in Apigee Emulator versions 1.15.1 and later; no workaround published | NEW |
| 383334511 | Apigee | Apigee | OPEN; OPEN | **LIMITATION** | KVM entry created with unexpected name | none published; issue still OPEN | NEW |
| 382565315 | Apigee hybrid (+Apigee) | hybrid 1.13.0,; hybrid 1.13.1,; hybrid 1.13.2,; hybrid 1.14.0 | FIXED in hybrid 1.13.3 and hybrid 1.14.1; closed | **BUG** | LogTimer usage in SecurityPolicy can cause a memory leak. | FIXED in hybrid 1.13.3 and hybrid 1.14.1; no workaround published | NEW |
| 378686709 | Apigee hybrid (+Apigee) | Apigee; Apigee hybrid | FIXED in Apigee (support call required); closed | **BUG** | FIXED in hybrid 1.14.3 and hybrid 1.15.1 (procedure required) | FIXED in Apigee (support call required); no workaround published | NEW |
| 373722434 | Apigee hybrid (+Apigee) | hybrid 1.13.x | FIXED in hybrid 1.13.2 and later; closed | **BUG** | The Apigee backup job is unable to upload to Cloud Storage buckets with retention policies. | workaround published; FIXED in hybrid 1.13.2 and later | NEW |
| 368155212 | Apigee hybrid (+Apigee) | hybrid 1.14.0; hybrid 1.14.1 | FIXED in hybrid 1.14.2; closed | **BUG** | ESS and non-ESS Cassandra credential rotation does not work in organizations with Enhanced Proxy Limits. | FIXED in hybrid 1.14.2; no workaround published | NEW |
| 364872027 | Apigee hybrid (+Apigee) | Apigee; Apigee hybrid | FIXED; closed | **BUG** | PEM parsing error in JWT/JWS policies due to non-standard format | FIXED; no workaround published | NEW |
| 355714868 | Apigee hybrid (+Apigee) | Monetization; Apigee hybrid | FIXED in hybrid 1.14.3, hybrid 1.15.1, hybrid 1.16.0; closed | **BUG** | Recurring, setup, and top-up fee data not captured or billed *for hybrid organizations* | FIXED in hybrid 1.14.3, hybrid 1.15.1, hybrid 1.16.0; no workaround published | NEW |
| 341157011 | Apigee | Apigee | FIXED; closed | **BUG** | Specs generated with Gemini Code Assist in Cloud Code that also include non-ASCII UTF-8 characters are not parsed correctly when uploaded to API hub. | FIXED; no workaround published | NEW |
| 341099433 | Apigee hybrid (+Apigee) | Apigee hybrid | OPEN; OPEN | **LIMITATION** | The apigee-logger component does not support Workload Identity Federation. | none published; issue still OPEN | NEW |
| 338285095 | Apigee | Apigee | FIXED; closed | **LIMITATION** | Apps associated with an AppGroup do not appear in the Apps list in the Apigee UI. As a result, users cannot access the app's App Detail page in the console. Using search in the console with a partial app name… | workaround published; FIXED | NEW |
| 333791378 | Apigee hybrid (+Apigee) | hybrid 1.12.0 | OPEN; OPEN | **LIMITATION** | Cassandra backup and restore features not supported by Helm migration tool | none published; issue still OPEN | NEW |
| 329304975 | Apigee | Apigee | FIXED; closed | **LIMITATION** | Limit on number of basepaths per environment | FIXED; no workaround published | NEW |
| 315820718 | Apigee | Apigee | FIXED; closed | **BUG** | With gRPC proxy requests, gRPC trailers are removed from the response | FIXED; no workaround published | NEW |
| 310384001 | Apigee hybrid (+Apigee) | hybrid 1.11.0 | OPEN; OPEN | **BUG** | Cert validation failures may return a 502 instead of a 503 error response when users add the tag true in the target block for default validation of TLS target endpoint certificates. | none published; issue still OPEN | NEW |
| 310191899 | Apigee hybrid (+Apigee) | Apigee; Apigee hybrid | OPEN; OPEN | **BUG** | Timeouts when deploying API proxies and shared flows | none published; issue still OPEN | NEW |
| 301845257 | Apigee | Apigee | FIXED; closed | **BUG** | Attempting to deploy more than 800 proxies to an environment group fails with an error. The limit on which an error is returned is lower than 800 when the basepaths are longer than 15 characters. | FIXED; no workaround published | NEW |
| 301458133 | Apigee | Apigee | FIXED; closed | **BUG** | Some proxy deployment attempts return an error that the revision is immutable | workaround published; FIXED | NEW |
| 300660653 | Apigee | Apigee | FIXED; closed | **BUG** | An error should be, but is not, returned when deploying proxies with the same path to multiple environments that are attached to the same instance and environment group | workaround published; FIXED | NEW |
| 297012500 | Apigee hybrid (+Apigee) | Apigee; hybrid 1.8.0 and later | OPEN; OPEN | **BUG** | Deployment Issues with OAS Validation while using circular reference. | none published; issue still OPEN | NEW |
| 295929616 | Apigee hybrid (+Apigee) | hybrid 1.10.0 and later | FIXED in hybrid 1.10.3; closed | **BUG** | Installing Apigee hybrid 1.10 on OpenShift (OSE) can fail with out-of-memory errors. | FIXED in hybrid 1.10.3; no workaround published | NEW |
| 292558790 | Apigee hybrid (+Apigee) | Apigee; hybrid 1.8.0 and later | OPEN; OPEN | **BUG** | OASValidation policy fails with Unable to parse JSON error. | none published; issue still OPEN | NEW |
| 292118812 | Apigee hybrid (+Apigee) | hybrid 1.10.1 | FIXED; closed | **BUG** | apigee-udca may not honor the http proxy settings. | FIXED; no workaround published | NEW |
| 291294211 | Apigee | Apigee | OPEN; OPEN | **BUG** | Error using Custom Reports and Stats APIs when selecting by fee type for installations using Monetization. | none published; issue still OPEN | NEW |
| 289583112 | Apigee | Apigee | OPEN; OPEN | **LIMITATION** | OASValidation policy does not work with global security requirements in OpenAPI specifications | none published; issue still OPEN | NEW |
| 289254725 | Apigee hybrid (+Apigee) | Apigee; Apigee 1-10-0-apigee-3; hybrid 1.8.8; hybrid 1.9.3 | FIXED in Apigee 1-10-0-apigee-5; closed | **BUG** | FIXED in hybrid | FIXED in Apigee 1-10-0-apigee-5; no workaround published | NEW |
| 287922301 | Apigee | Apigee | OPEN; OPEN | **LIMITATION** | Inaccuracies in Monetization rates around volume-band thresholds | none published; issue still OPEN | NEW |
| 284500460 | Apigee | Apigee; Apigee 1-10-0-apigee-1 | FIXED; closed | **BUG** | Increase in latency for Message Logging policy when used with Cloud Logging. | FIXED; no workaround published | NEW |
| 282997216 | Apigee hybrid (+Apigee) | hybrid 1.8.0 and later; hybrid 1.9.0 and later | OPEN; OPEN | **BUG** | Special characters not allowed in Cassandra Jolokia password | none published; issue still OPEN | NEW |
| 270574696 | Apigee | Apigee | FIXED; closed | **LIMITATION** | Apigee does not support Cloud External Key Manager. | FIXED; no workaround published | NEW |
| 270371160 | Apigee hybrid (+Apigee) | hybrid 1.9.0 and later | FIXED; closed | **LIMITATION** | Apigee Ingress gateway supports TLS1.2+ protocol/ciphers only | FIXED; no workaround published | NEW |
| 269139342 | Apigee hybrid (+Apigee) | hybrid 1.7.0 and later | FIXED; closed | **BUG** | apigeectl getOrg does not follow HTTP_PROXY settings in overrides.yaml | FIXED; no workaround published | NEW |
| 268104619 | Apigee hybrid (+Apigee) | Apigee; Apigee hybrid | OPEN; OPEN | **BUG** | In the OASValidation policy, when you specify an array type in header, the MP will throw an error, even if the input is valid. | none published; issue still OPEN | NEW |
| 266452840 | Apigee hybrid (+Apigee) | Apigee; hybrid 1.7.0 and later; hybrid 1.8.0 and later; hybrid 1.9.0 and later | FIXED; closed | **BUG** | Web sockets not working with Anthos Service Mesh 1.15.3 in Apigee X and Apigee Hybrid | FIXED; no workaround published | NEW |
| 260772383 | Apigee hybrid (+Apigee) | hybrid 1.8.0 and later | OPEN; OPEN | **BUG** | Socket bind error on the AKS platform | none published; issue still OPEN | NEW |
| 260324159 | Apigee | Apigee 1-9-0-apigee-16 | FIXED; closed | **BUG** | API proxy and shared flow deployments taking up to 30 minutes. | FIXED; no workaround published | NEW |
| 258699204 | Apigee hybrid (+Apigee) | hybrid 1.8.0 and later | FIXED; closed | **BUG** | The default memory requests and limits for metrics pods have inadvertently changed in 1.8.x. | FIXED; no workaround published | NEW |
| 247540503 | Apigee hybrid (+Apigee) | hybrid 1.7.0 and later; hybrid 1.8.0 and later | FIXED; closed | **BUG** | A race condition with encryption key lookup can cause KVM lookup failures. | FIXED; no workaround published | NEW |
| 246774745 | Apigee | Apigee | FIXED; closed | **BUG** | Value of io.timeout.millis is not honored when used with multiple dynamic targets. | FIXED; no workaround published | NEW |
| 245664917 | Apigee hybrid (+Apigee) | hybrid 1.8.x | FIXED; closed | **LIMITATION+symptom** | Apigee hybrid upgrade error can be ignored | FIXED; no workaround published | NEW |
| 242213234 | Apigee | Apigee | FIXED; closed | **BUG** | API product fails to load with a "no connections available" error | workaround published; FIXED | NEW |
| 241786534 | Apigee hybrid (+Apigee) | hybrid 1.8.0 and later | FIXED; closed | **BUG** | MART sometimes unable to connect to FluentD. | FIXED; no workaround published | NEW |
| 221305498 | Apigee | Apigee | OPEN; OPEN | **BUG** | API Monitoring may display fault code of '(not set)'. | none published; issue still OPEN | NEW |
| 214447386 | All Apigee products | All | OPEN; OPEN | **LIMITATION+symptom** | The message "config not modified" is displayed in Apigee API Data Access audit logs as an Error. | none published; issue still OPEN | NEW |
| 209097822 | Apigee hybrid (+Apigee) | hybrid 1.5.0 and later; Apigee | FIXED; closed | **BUG** | Dynamic updates to rate in spike arrest may not reflect immediately | workaround published; FIXED | NEW |
| 207762842 | Apigee hybrid (+Apigee) | hybrid 1.5.0 and later | FIXED; closed | **BUG** | Logs not shipped to Cloud Logging by apigee-logger. | FIXED; no workaround published | NEW |
| 207719377 | Apigee | Apigee | FIXED in Apigee 1-11-0-apigee-1; closed | **BUG** | If there is more than one SpikeArrest policy in a bundle, 502 errors will occur. | workaround published; FIXED in Apigee 1-11-0-apigee-1 | NEW |
| 205666368 | Apigee hybrid (+Apigee) | Apigee; hybrid 1.10.2; hybrid 1.10.3 | FIXED in Apigee 1-10-0-apigee-6 and; closed | **LIMITATION** | Apigee hybrid does not validate the target certificate by default. | FIXED in Apigee 1-10-0-apigee-6 and; no workaround published | NEW |
| 205629443 | Apigee | Apigee | FIXED; closed | **BUG** | If ServiceCallout is fire and forget (no tag), a race condition can occur if there is another policy that occurs after it. | workaround published; FIXED | NEW |
| 203778087 | Apigee hybrid (+Apigee) | hybrid 1.5.3 and later | OPEN; OPEN | **BUG** | apigee-stackdriver-logging-agent currently runs as root. | none published; issue still OPEN | NEW |
| 191815997 | Apigee hybrid (+Apigee) | hybrid 1.6.0 and later | FIXED; closed | **BUG** | If a hybrid customer configures a forward proxy for the API proxy, Google token will not work unless it has direct access to *.googleapis.com. | FIXED; no workaround published | NEW |
| 191002224 | Apigee hybrid (+Apigee) | hybrid 1.5.0 and later | FIXED; closed | **BUG** | Changing an email address fails while using the PUT /organizations/{org_name}/developers/{developer_email} API. | FIXED; no workaround published | NEW |
| 184555974 | Apigee hybrid (+Apigee) | hybrid 1.5.0 and later | FIXED; closed | **LIMITATION** | The apigee-logger Fluentd can't parse logs in the OpenShift cluster. | workaround published; FIXED | NEW |
| 146222881 | Apigee hybrid (+Apigee) | hybrid 1.3.0 and later | FIXED; closed | **BUG** | Invalid HTTP Header error | FIXED; no workaround published | NEW |

---

## Prose detail: the ten most scenario-worthy entries

### 1. 300660653 — the deploy that should have failed and did not

> **An error should be, but is not, returned when deploying proxies with the same path to
> multiple environments that are attached to the same instance and environment group**
>
> Deploying proxies with the same path to multiple environments that are attached to the same
> instance and environment group is not allowed and should return a warning message about a
> base path conflict. Instead, no error is shown and the deployments appear to succeed.
>
> **Workaround:** When deploying and after deployment, verify that there are not base path
> conflicts with deployed proxies and correct as needed.

Apigee. Status FIXED, no fixed-in version given. This is the register's cleanest example of
the category that punishes a confident support engineer. Every signal a deploy produces is
green: the Management API returns success, the revision shows as deployed, the environment
group lists it. The one thing the platform refuses to do is tell you that you have created an
ambiguity that it will later resolve by picking one of the two winners, and the loser 404s.

This is a **BUG** in the sense of "the warning was missing", but the *conflict itself* is a
**LIMITATION**: the design does not permit two proxies claiming the same path in one
environment group, and it does not prevent it. The correct answer to a customer is not "upgrade"
so much as "you are relying on an invariant that Apigee neither enforces nor reports". A support
agent that sees two green deploys and moves on has been actively misled.

Worth noting what the register does *not* say: it does not give a fault code, because there is
no error to give a code for. Searching the error index for this will find nothing.

### 2. 402739748 — a hard limit that reports itself in someone else's language

> APIproducts are limited to 50 paths. If you add additional paths, an error message is
> displayed: `Operation group limit of 51 exceeded in Operation Config`
>
> **Workaround:** Use wildcard patterns to combine resource paths and operations as described in
> Configuring resource paths.
>
> **Workaround:** Create multiple API Products. This workaround has been verified and is viable
> for those who add a lot of API Proxies to an API Product. The App that is associated with your
> API Products would need to be updated to include the new one, but credentials and
> client-side request details have been proven to not need changing.

Apigee. Status **OPEN**. The 51 in the message is the tell: the limit is 50, and the error
reports the first value that breaches it. "Operation group limit of 51 exceeded in Operation
Config" is not an Apigee error code and will not appear in any Apigee fault-code index; it is
an internal-operation-config limit surfacing through the save path, so the operator has no
`{"fault":{"detail":{"errorcode":...}}}` payload to grep for.

Two failure modes stack here. First, it is a **LIMITATION** — 50 paths per API product is the
design, and creating more API products is the intended answer, not a hack. Second, it is a
save-time error that a support engineer will attribute to the *proxy* rather than to the
*product*, because the customer was editing an API product and the message names "Operation
Config". The second workaround's reassurance is the most useful sentence on the page: the App
must be updated to reference the new product, but **credentials and client-side request details
do not change**. That is exactly what a support engineer needs in order to tell a customer their
clients are safe, and it is stated nowhere else.

### 3. 301845257 — a documented limit whose threshold is a function of something else

> Attempting to deploy more than 800 proxies to an environment group fails with an error. The
> limit on which an error is returned is lower than 800 when the basepaths are longer than 15
> characters.

Apigee. Status FIXED. One sentence, and it is a textbook two-factor cause: the number of proxies
is necessary but not sufficient. Basepath *length* is the second factor, and it is invisible
from the API response, which reports only that an error occurred.

Read alongside **329304975** ("Limit on number of basepaths per environment", FIXED, Apigee),
which states a 1000-basepath-per-environment ceiling that counts *total basepaths*, not
revisions, so a revision carrying several basepaths consumes several slots — the register is
explicit: "If your API proxies or revisions contain more than one basepath, the total number of
basepaths per environment must not exceed 1000."

Both are **LIMITATIONS** ("Apigee is enforcing a *temporary* limit of 1000 basepaths per
environment to avoid potential failures when deploying API proxy revisions"). The word
"temporary" is doing a lot of work and an agent should quote it rather than promise permanence.
Together they give a scenario where a customer at 610 proxies with 20-character basepaths
cannot deploy, while a colleague at the same 610 proxies with short basepaths can, and neither
count is wrong.

### 4. 310384001 — the wrong status code sends support to the wrong component

> Cert validation failures may return a 502 instead of a 503 error response when users add the
> tag `<Enforce>true</Enforce>` in the target `<SSLInfo>` block for default validation of TLS
> target endpoint certificates.

hybrid 1.11.0. Status **OPEN**. This is the register's best "confidently blame the wrong
component" entry. The customer adds `<Enforce>true</Enforce>` precisely because they *want*
certificate validation. They get a **502 Bad Gateway** — the code that means "upstream returned
something unusable" — where the documented meaning is a target certificate that failed
validation.

A 502 reads as "the target is down or the gateway cannot reach it". An engineer will check
target health, L7 routing, and the gateway, and will find all of them fine, because nothing is
down. The cause is the target's certificate, and the status code actively conceals that. The
conjunction matters too: the wrong code appears when `<Enforce>true</Enforce>` is set in the
target `<SSLInfo>` block. Default validation is not being bypassed; the customer has asked for
it and is being told the wrong thing about the result. **LIMITATION**, still open, so the
correct answer is not "wait for a fix" but "read the code as a certificate problem".

### 5. 445936920 — hardening that removes the cushion under a latent misconfiguration

> Previously undetected DNS configuration problems might now cause DNS errors. Apigee removed
> the automatic DNS fallback functionality that was in 1-16-0-apigee-2. This removal eliminates
> the platform's resiliency to DNS misconfigurations and might now result in DNS errors.
>
> Find related errors by checking the runtime logs for DNS resolution errors.

Apigee 1-16-0-apigee-2 and later. Status **OPEN**. The affected range *includes* the version the
text says the fallback was in, which reads oddly until you notice the sentence is describing
what was removed from it. Nothing was broken. A fallback that silently recovered from bad DNS
configuration was deleted, and a configuration that was always wrong is now visible.

This is the purest "a fix introduced a regression" shape available in the register, and it is
classified as a **LIMITATION** rather than a bug precisely because nothing regressed: resiliency
was removed on purpose and the misconfiguration it was masking was always there. The scenario
value is the *timeline*. The cluster has been running since before the change, worked fine,
then stopped working on a version bump, and the customer is certain they changed nothing —
because they did not. The diagnostic move is to check runtime logs for DNS resolution errors,
which the register names explicitly.

### 6. 480997525 — a transitive dependency upgrade surfaces as a client error

> **Proxy calls fail with `The URI contain illegal characters` error after Netty upgrade.**
>
> In Apigee version 1-17-0-apigee-1, a Netty upgrade to 4.1.129.Final introduced a regression.
> This can cause API proxy calls to fail with a `400` status code and the error message `The URI
> contain illegal characters`. This issue is tracked externally in
> [netty/netty#16020](https://github.com/netty/netty/issues/16020).

Apigee 1-17-0-apigee-1 only. Status FIXED in Apigee 1-17-0-apigee-2. Note the grammar in the
error string, "contain" rather than "contains" — it is quoted exactly as the register quotes it
and any agent that paraphrases it into correct English will fail a verbatim match.

The misdiagnosis risk is severe and specific: a **400** with a message about illegal URI
characters points straight at the request. The customer will inspect their basepath, their
target URL, their headers, and their encoding — all of which are unchanged and correct. The
actual change is a Netty version bump inside the proxy runtime. **BUG**, single version, fixed
in the very next release, so the correct answer is "upgrade to 1-17-0-apigee-2", but reaching it
requires knowing the version is the discriminator rather than the request.

### 7. 422757662 — a change that broke a relied-upon default, then had to be put back

> In the Apigee 1-15-0-apigee-5 and hybrid 1.15.0 releases, Apigee stopped sending `x-b3`
> headers to target endpoints when Distributed Trace is disabled. However, some Apigee
> installations were relying on `x-b3` headers being sent regardless of whether Distributed
> Trace was enabled or disabled. Therefore this change has been reverted starting in Apigee
> 1-15-0-apigee-7.
>
> **Note:** In case you are experiencing this issue please reach out to Apigee to revert this
> change for now in your Apigee Org.
>
> **Caution:** Apigee does not recommend using `x-b3` headers when Distributed Trace is disabled.
> This will guard against future changes to this behavior.

Apigee 1-15-0-apigee-5; hybrid 1.15.0. FIXED (reverted) in Apigee 1-15-0-apigee-7 and the
matching Apigee release. Three properties make this the best version-gated entry in the
register:

- **Version-gated and non-monotonic.** Present in -5 and -6, absent again from -7. "Fixed in"
  is not a one-way door, and an agent that reasons "it was fixed in -7, so -6 must have it" is
  right and an agent that reasons "this release is newer so it includes the fix" is also right,
  for opposite reasons.
- **Fix-enabled is not default-enabled.** "please reach out to Apigee to revert this change for
  now in your Apigee Org" means the org is pinned to a behaviour the platform no longer
  recommends. Version alone cannot tell you whether your org is pinned. That is exactly the
  fresh-install-versus-upgraded split the register encodes elsewhere, applied per org.
- **A latent default in use.** Nobody configured these headers. They were injected because
  something had once depended on them.

The trailing **Caution** is the part a scenario should test for: the correct advice is to stop
depending on the headers, because the reversion is a reprieve, not a guarantee.

### 8. 378686709 — the fix exists, is off, and 404s until you ask for it

> The use of wildcards (`*`) in Apigee proxy basepaths may conflict with other explicit
> basepaths, resulting in a `404` error. For example, use of the following basepaths for two
> proxies deployed in the same environment may result in a `404` error when calling `Proxy-2`:
>
> ```
> Proxy-1: /a/v1/b
> Proxy-2: /a/*/c
> ```
>
> In this case, calls to the explicit base path will resolve successfully, but calls to the
> `Proxy-2` may return a `404`, if the wildcard path is evaluated as `/a/v1/c`.
>
> **Fixed:** This issue is fixed in Apigee and in hybrid 1.14.3 and later. However, the fix is
> not enabled by default. If you wish to enable the use of wildcards in basepaths:
>
> - Customers with Apigee orgs should reach out to Apigee support to enable the fix if needed.
> - Customers with Apigee hybrid orgs shoul…

Apigee and Apigee hybrid. Status "FIXED in Apigee (support call required)", fixed in hybrid
1.14.3 and 1.15.1 with a procedure. The register truncates the hybrid remediation mid-sentence
at the bottom of the page; that truncation is in the source.

The routing consequence is the good part and it is asymmetric in a way that is very hard to
intuit: `/a/v1/b` resolves and `/a/*/c` 404s. One proxy in the environment works perfectly while
its sibling fails, from the same deployment, on the same path prefix. Any agent that
establishes "the environment group is serving traffic" has proved nothing. And because the fix
is **not enabled by default**, upgrading to a version ≥ 1.14.3 does not fix it — a support
engineer who checks the version, sees it fixed, and stops has been wrong twice.

### 9. 289583112 — a security control that is silently not applied

> **OASValidation policy does not work with global security requirements in OpenAPI
> specifications**
>
> If the OASValidation policy specifies an `<OASResource>` with security requirements set at a
> *global* level, the security requirements are not enforced.
>
> **Workaround:** To ensure enforcement, all security requirements must be set at the
> *operation* level in the OpenAPI specification passed in the `<OASResource>` element of the
> OASValidation policy.

Apigee. Status **OPEN**. A **LIMITATION**, and the highest-stakes one in the register. Nothing
errors. The policy is attached, it validates, it passes requests. The security requirements in
the spec are simply not being checked. The customer's evidence that validation "works" is the
strongest possible false positive: a green checkmark from the very control that is failing to
act.

The discriminator is *where in the spec* the requirement lives, not whether it exists. An agent
that confirms "the OASValidation policy is deployed and the spec has security requirements" has
confirmed both halves and drawn the wrong conclusion, because the conjunction must hold with
requirements at operation level. Close relatives worth keeping in the same cluster of knowledge:
**268104619** (array-typed headers throw in the Message Processor even when the input is valid),
**292558790** (`Unable to parse JSON`, and `Unable to parse JSON - Unrecognized token` when a
path parameter uses a `$ref` schema), **297012500** (circular references in OpenAPI 3.0.0 cause
infinite recursion and the deploy fails), **438850078** (a discriminator whose type equals the
parent schema drives the policy into `StackOverflowError`), and **289254725** (YAML OpenAPI with
a floating-point number such as `example: 2.345` can fail the deploy). Five open OASValidation
entries, all still open, all with different triggers.

### 10. 146222881 — HTTP/2 on the response path, blamed on the target

> **Invalid HTTP Header error**
>
> Invalid HTTP Header error: The Istio ingress switches all incoming target responses to the
> HTTP2 protocol. Because the hybrid message processor only supports HTTP1, you may see the
> following error when an API proxy is called:
>
> `http2 error: Invalid HTTP header field was received: frame type: 1, stream: 1,`
>
> ` name: [:authority], value: [domain_name]`
>
> If you see this error, you can take either of the following actions to correct the problem:
>
> - Modify the target service to omit the Host header in the response.
> - Remove the Host header using the AssignMessage policy in your API proxy if necessary.

hybrid 1.3.0 and later. Status FIXED. The error text names a *received* header field and an
`:authority` pseudo-header, which sends an engineer looking at the request the client sent. The
`name: [:authority], value: [domain_name]` fragment is the target echoing its own Host header
back in a response, and it is illegal in HTTP/2 where `:authority` is request-only.

Three components are involved — Istio ingress, the message processor, and the target — and the
register's own root cause sentence splits the blame across all three. The ingress upgrades the
response protocol to HTTP/2; the message processor only speaks HTTP/1; the target emits a header
that is only legal under HTTP/1. Remove any one of the three conditions and there is no error.
This is the purest two-factor case in the register: it is genuinely conjunctive, and the two
documented remediations sit at opposite ends of the chain (fix the target, or fix it in the
proxy with AssignMessage). A **BUG** that is fixed at the platform level, so the durable answer
for a hybrid customer on a current version is "this should not happen; if it does, the target is
still emitting a Host header".

---

## Also worth harvesting (one line each, all verified from the register)

- **287922301** (Apigee + hybrid, **OPEN**). Monetization volume-band thresholds: "Due to
  current design, inaccurate monetization rates may be assessed for transactions that occur near
  a volume-band threshold… more likely to occur when many transactions for a given developer and
  rate plan combination occur within a 30 second window… **has no known workaround**." The only
  register entry that states outright that no workaround exists. Silent *wrong billing* in both
  directions — over-reports on decreasing banded rates, under-reports on increasing ones.
- **432315283** (Apigee, **OPEN**). Keystore/truststore update fails **intermittently** because
  the update "may fail on one runtime pod but succeed on other pods". Verified payload:
  `{"fault":{"faultstring":"SSL Handshake failed sun.security.provider.certpath.SunCertPathBuilderException: unable to find valid certification path to requested target","detail":{"errorcode":"messaging.adaptors.http.flow.SslHandshakeFailed"}}}`. An intermittent TLS error that is a *partially applied config change*, so retries "fix" it and destroy the evidence.
- **449012244** (Apigee, **OPEN**). Mixing SSE and non-SSE target endpoint definitions "might
  result in inconsistent behavior such as empty `response.content` flow variables." Silent,
  intermittent, and points at the backend rather than at the proxy.
- **207719377** (Apigee, FIXED in 1-11-0-apigee-1). "If there is more than one SpikeArrest
  policy in a bundle, `502` errors will occur." A `502` that means "you configured SpikeArrest
  twice", not "the backend failed".
- **209097822** (hybrid + Apigee, FIXED). Dynamic SpikeArrest rate updates do not take effect
  while a key has continuous traffic; they apply only after **five minutes of no traffic** for
  that key. Time-gated, and the gate is per-key rather than global.
- **383334511** (Apigee, **OPEN**). A KeyValueMapOperations `<Put>` called from a **shared flow
  via a flow hook** with `apiproxy` scope writes the entry under the **shared flow name**
  instead of the API proxy name. Scope resolution is evaluated at the wrong level; the entry
  exists, so any check that only asks "does the KVM key exist" passes.
- **499322601** (hybrid, FIXED in 1.16.2). "Apigee will not support a forward proxy which has
  the Basic Auth credential enforced." A **LIMITATION** stated as a refusal, affecting
  1.16.0-hotfix.1, 1.15.2 and 1.14.4.
- **392135466** (hybrid 1.14.0, **OPEN**). "Proxy chaining with mTLS is not supported when using
  Enhanced per-environment proxy limits." Two features, one **LIMITATION**, no error and no
  message. Silent.
- **460431753** (Apigee + hybrid, **OPEN**). Model Armor policies — `SanitizeUserPrompt`,
  `SanitizeModelResponse` — "currently do not function as expected when used in API proxies
  handling WebSocket connections". A security policy that is present and inert.
- **205666368** (hybrid 1.10.2, 1.10.3; FIXED in Apigee 1-10-0-apigee-6 and hybrid
  1.10.3-hotfix.1). "Apigee hybrid does not validate the target certificate by default."
  Cross-reference with **310384001** above: by default you get no validation and, when you ask
  for it, the wrong status code.
- **246774745** (Apigee, FIXED). "If a proxy sets two or more `io.timeout.millis` values in two
  or more flows using the same target host, only one `io.timeout.millis` value is honored."
  Silent, and which one wins is not stated. Pairs with the already-used **471125841**.
- **315820718** (Apigee, FIXED). On gRPC target calls "the only trailer that's returned is the
  `grpc-status` trailer. All other trailers are removed from the response."
- **270574696** (Apigee, FIXED). "Apigee does not support Cloud External Key Manager." One
  sentence, no elaboration.
- **270371160** (hybrid 1.9.0 and later, FIXED). "Apigee Ingress gateway only supports TLS1.2+,
  and not earlier versions of TLS."
- **245664917** (hybrid 1.8.x, FIXED). The Cassandra schema validation job sitting in an error
  state after `apigeectl init` and a successful `check-ready` is "**a harmless condition**" and
  can be ignored. Pairs with **415061771** ("object has been modified; please apply your changes
  to the latest version and try again" — recurring controller-log noise that "do not indicate
  any risk") and **214447386** ("config not modified" in Data Access audit logs as an `Error`
  — "expected to occur every minute and does not affect your billing cost"). Three entries whose
  entire purpose is to stop someone opening a ticket.
- **214447386** (All products, **OPEN**). Quoted above; notable as the only entry whose Affects
  column reads simply "All".
- **221305498** (Apigee, **OPEN**). API Monitoring of Configurable API Proxies "may display a
  fault code of '(not set)'" for non-2xx target responses. An observability gap: the tool that is
  supposed to name the fault cannot.
- **245664917**, **246774745**, **260772383** (hybrid 1.8.0 and later, **OPEN**). On AKS:
  `envoy config listener '0.0.0.0_443' failed to bind or apply socket options: cannot bind
  '0.0.0.0:443': Permission denied`. Verified verbatim. Workaround is an `svcAnnotations`
  stanza with `service.beta.kubernetes.io/azure-load-balancer-internal: "true"` — an Azure
  annotation on an AKS install.
- **284500460** (Apigee, FIXED). "To avoid increasing latency in responses to the client, the
  Message Logging policy should be attached to the *PostClientFlow*." A latency increase blamed
  on the gateway that is really a flow-placement problem.
- **401624396** (hybrid 1.13.x/1.14.x, **OPEN**) and **391861216** (FIXED in 1.13.3/1.14.1). The
  GCP/HYBRID cloud providers behave differently from CSI: restore fails with `Unrecognized
  strategy option passed to NetworkTopologyStrategy`, and restarting Cassandra on a
  GCP/HYBRID-restored cluster gives `Cannot change the number of tokens from 512 to 256` and
  CrashLoopBackOff. Both entries say "**This issue does not affect `CSI`**", which is a
  discriminator agents will miss entirely.
- **415061771**, **310191899** (Apigee + hybrid, **OPEN**). Deployment timeouts on
  `organizations.environments.apis.revisions.deployments.deploy` and the three sibling
  endpoints under high QPS; recommended target is 1 QPS and checking deployment status first.

### Entries that are documentation-of-a-refusal rather than a fault

These are still useful, because the correct answer is "this will never work":

- **421402073** (Apigee in VS Code, **OPEN**). Google authentication in ServiceCallout and
  ExternalCallout is not supported in VS Code.
- **338285095** (Apigee, FIXED). Apps in an AppGroup are absent from the UI Apps list, and
  console search by partial app name or API key does not find them. "Apigee hybrid organizations
  are not impacted… as they use the Classic UI" — a product-difference trap.
- **420985360** (Integrated portal, **OPEN**). A single ID covering four separate portal
  limitations: SmartDocs supports OpenAPI 3.0 with an unsupported subset (e.g. `allOf`); "Try
  this API" forces `Accept: application/json` "regardless of the value set for `consumes`" and
  rejects non-string request header types; simultaneous portal edits by multiple users are
  unsupported; **deleting an API reference documentation page is irreversible** — "you'll need
  to delete and re-add the API product, and regenerate"; theme changes take up to 5 minutes;
  search is not integrated; SLO with the SAML IdP is unsupported for custom domains and the
  workaround is to leave the Sign-out URL blank.
- **184555974** carries two more Open entries merged under it: archive deployments cannot be
  viewed, confirmed or debugged in the UI at all, and **rolling back an archive deployment is
  not supported** — you must redeploy a previous version or delete the environment.
- **482077193** (hybrid 1.15.0 and later, FIXED in 1.16.0-hotfix.1). Multi-org, single-namespace
  clusters: proxy chaining fails intermittently with `404 route_not_found` because the internal
  chaining gateways for different organizations share one `ingress_name` selector and Envoy
  loads routing rules inconsistently. Intermittent, load-dependent, and fixed by making the
  `apigeeChainingGateway.name` unique per org.

---

## Register hygiene notes

- The register is **one page and one table**. The product and status chips are client-side
  filters over the same rows; there is no per-product URL.
- **No Edge for Private Cloud rows exist** despite the page header linking to OPDK docs. OPDK
  known issues live in the release notes on `docs.apigee.com`. Do not attribute an OPDK finding
  to this page.
- Several rows are **merged**: one issue ID covers multiple independent sub-issues, each with
  its own product filter and its own status line. 341099433 covers three; 420985360 covers four;
  412740465, 184555974, 241786534, 207762842 and 191815997 cover two each. A parser that assumes
  one issue per ID will silently attribute a neighbouring sub-issue's product and status to the
  wrong statement.
- **Regex-discovered issue IDs on the flattened page (102) and on the raw HTML (102) agree
  exactly.** Every fault code and log line quoted in this file was re-verified by literal
  string search against `pages/ki-live-20261012.txt`.

---

# PROPOSED SCENARIOS

Format copied from `scenarios/medium.md`. Fault codes used are restricted to those in
`.agents/skills/apigee-support-core/references/error-codes.md`. HTTP status codes, header
fragments and log lines are quoted verbatim from the official known-issues register and were
re-verified by literal string search against `research/pages/ki-live-20261012.txt`.

---

### MED-40. Two green deploys, one invisible conflict

#### Scenario metadata

- ID: MED-40
- Difficulty: medium
- Primary topic: environment groups and base paths
- Secondary topics: deployment state, routing, silent misconfiguration
- Product: Apigee
- Origin: reported real-world case (official known issue 300660653, closed as FIXED)
- Versions: checked 2026-10-12
- Evaluation objectives: every deploy signal is green. The only thing that is wrong is
  something Apigee declines to report. The correct move is to distrust the absence of an error,
  not to look for a failing deploy
- Skills expected: apigee-support-core

#### Initial support ticket

> We deployed `/v1/orders` to `prod` last month and it works. This week we deployed `/v1/orders`
> to `uat`. Both deploy calls returned success and both show as deployed. Now traffic for one of
> them 404s and we cannot tell which. Nobody can tell us which proxy is at fault. Can you check
> the deployments?

#### Initial evidence

The Management API reports both revisions deployed in their respective environments. Both
environments are attached to the same environment group. Requests to one proxy host resolve and
succeed. Requests to the other return 404. No error is logged at deploy time or since.

#### Expected investigation

The agent should resist the invitation to inspect deployments, because deployments are not the
thing that is wrong. It should notice that "which one 404s" is the actual question, and that
this is an address-resolution problem caused by two proxies claiming one base path within a
single instance and environment group.

#### Diagnostic evidence

Both environments are members of the same environment group, and both environments belong to the
same Apigee instance. Both proxies declare the identical base path `/v1/orders`. No deployment
error was ever produced because Apigee does not raise one for this case.

#### Ground-truth resolution

This is a documented limitation, not a broken deployment. Deploying proxies with the same path
to multiple environments attached to the same instance and environment group is not allowed, and
should return a warning about a base path conflict. It does not. Instead, no error is shown and
the deployments appear to succeed.

That wording is the whole lesson: the deploy genuinely succeeded, and the platform has recorded
an ambiguity it will later resolve by choosing one winner. The loser 404s. The 404 is correct
behaviour for an undefined routing situation, not a routing fault.

An agent that treats "deploy succeeded" as proof that the environment is consistent has adopted
the exact assumption the register warns against. Note also that this produces no fault code, so
there is nothing in any error-code index to grep for.

#### Correct remediation

Rename the base path on one of the two proxies so the two are distinct, and redeploy that one.
Renaming the path is a routing change that clients depend on, so it needs to be scheduled with
the owning team rather than applied as a reflex.

Going forward, verify after each deployment that no other proxy in the same environment group
claims the same base path. There is no platform warning to rely on, because there is no platform
warning.

#### Verification

Send a request to each proxy host and confirm both resolve. Then confirm no other proxy in the
group shares either base path, since a third conflict is as invisible as the first.

#### Common incorrect answers

Redeploying both proxies. Redeployment is not the defect and will reproduce the same state.

Recommending a redeploy as a "clean slate". There is nothing to clean; the conflict is in the
declared paths.

Looking for a routing or environment-group misconfiguration. The group is correctly configured
and both attachments are correct.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Redeploys | Identifies duplicate base paths | States it is an unreported base path conflict within one instance and environment group |
| Diagnostic method | Re-runs the deploys | Compares the two base paths | Confirms shared instance, shared group, and identical declared path |
| Handling of the green deploy | Trusts it | Doubts it | Explains why the absence of an error is the defect |
| Quality of next step | Restarts or redeploys | Asks the team to rename a path | Names the path change, the client impact, and the missing verification step |

#### Critical failures: recommending a redeploy as the fix; treating a successful deployment as
proof the environment is internally consistent.

Not a critical failure: not being able to say which proxy 404s. That is exactly the customer
problem, and the register gives no way to determine it.

#### References

- Known issues register (entry 300660653):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Environment groups:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/environmentgroups-working-with>

---

### MED-41. "Operation group limit of 51 exceeded in Operation Config"

#### Scenario metadata

- ID: MED-41
- Difficulty: medium
- Primary topic: API products and resource paths
- Secondary topics: hard limits, error triage, monetization of the design
- Product: Apigee
- Origin: reported real-world case (official known issue 402739748, still OPEN)
- Versions: checked 2026-10-12
- Evaluation objectives: the error message is not an Apigee fault code, names a component the
  customer is not editing, and reports 51 when the limit is 50. An agent that treats it as a
  proxy fault, or that greps an error-code index for it, will fail
- Skills expected: apigee-support-core

#### Initial support ticket

> Our team tried to add a few more paths to an existing API product in the console. The save
> failed with `Operation group limit of 51 exceeded in Operation Config`. We did not change any
> proxy. Is our proxy misconfigured?

#### Initial evidence

An API product in one environment holds 50 resource paths. Adding a 51st fails on save. No proxy
was edited, no revision was deployed, and no runtime error exists because nothing reached the
runtime.

#### Expected investigation

The agent should locate the error in the API product rather than in any proxy, and should
recognise that the string is a limit-enforcement message rather than a runtime fault. There is
no `{"fault":{"detail":{"errorcode":...}}}` payload here at all.

#### Diagnostic evidence

The API product contains 50 paths. The message reads `Operation group limit of 51 exceeded in
Operation Config`. The count of 50 matches a documented limit exactly.

#### Ground-truth resolution

API products are limited to 50 paths. This is a limitation, not a defect, and it is still OPEN
on the register, so the correct answer is not to wait for a fix.

Two details deserve attention. The message says 51 because it reports the first value that
breaches a limit of 50, so "51" is the ceiling plus one and not an off-by-one bug. And
"Operation Config" is not an Apigee component a support engineer can look up; it is an internal
operation-config limit surfacing through the save path, which is why the message names something
the customer is not editing and why it appears in no Apigee fault-code reference.

An agent that reads "Operation Config" as a proxy or deployment component will go and inspect
proxies that were never touched.

#### Correct remediation

The first published workaround is to combine resource paths and operations using wildcard
patterns, which reduces the number of separate paths without changing what clients call.

The second is to create multiple API products. The register states this has been verified as
viable, and it includes the sentence that matters most operationally: the App associated with
the API products must be updated to include the new one, but credentials and client-side
request details have been proven not to need changing. That is what allows a support engineer to
tell the customer their existing clients are unaffected.

#### Verification

Save the API product and confirm the limit error is gone. Then confirm the App now references
every product a client needs, because that is the step the workaround actually requires and the
step most likely to be forgotten.

#### Common incorrect answers

Blaming the proxy. No proxy was modified and no proxy is misconfigured.

Treating "51" as a miscount and arguing the limit is really 51. The limit is 50; the message
reports the breaching value.

Searching for `Operation group limit` in an Apigee error-code index. It is not an Apigee error
code and will not be there.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Investigates the proxy | Identifies the API product path limit | Names the 50-path limit and explains the 51 in the message |
| Diagnostic method | Greps fault codes | Reads the message | Recognises it is a limit message, not a runtime fault payload |
| Product knowledge | Suggests a new environment | Suggests wildcards | Gives both published workarounds, including splitting into multiple products |
| Client impact | Advises re-issuing credentials | Says clients still work | States the App must be updated but credentials and client-side details do not change |

#### Critical failures: attributing the failure to a proxy; telling the customer their
credentials must be re-issued.

Not a critical failure: proposing multiple API products without noting the App update. It is an
oversight rather than a wrong answer, and the register itself flags the same omission in its own
second workaround.

#### References

- Known issues register (entry 402739748):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Configuring resource paths:
  <https://cloud.google.com/apigee/docs/api-platform/publish/create-api-products#behavior-resource-path>

---

### MED-42. The proxy limit that depends on how long your base paths are

#### Scenario metadata

- ID: MED-42
- Difficulty: medium
- Primary topic: deployment scale limits
- Secondary topics: environment groups, two-factor causation, counting rules
- Product: Apigee
- Origin: reported real-world cases (official known issues 301845257 and 329304975, both closed
  as FIXED)
- Versions: checked 2026-10-12
- Evaluation objectives: two hard limits are in play, they count different things, and one of
  them has a hidden second factor. Checking only the proxy count, or only the environment
  total, rules the case out incorrectly
- Skills expected: apigee-support-core

#### Initial support ticket

> I cannot deploy to my environment group. Two of our teams on the same Apigee org can deploy
> fine with the same number of proxies. We are not over any limit that I can find. Is the org
> full?

#### Initial evidence

One environment group holds 604 deployed proxies with base paths around 22 characters long. A
second environment group on the same org holds 604 proxies with short base paths and deploys
without error. The environment totals differ as well.

#### Expected investigation

The agent should establish that there are two independent documented ceilings, in different
scopes, counting different units. The discriminator is not the proxy count.

#### Diagnostic evidence

The failing environment group's base paths exceed 15 characters. The working group does not. The
environment containing the failing group has a total base path count above 1000, counting base
paths rather than revisions.

#### Ground-truth resolution

Two limitations are in play, both documented and both now closed.

First, attempting to deploy more than 800 proxies to an environment group fails with an error, and
the register adds the detail that actually matters: the limit at which an error is returned is
lower than 800 when the base paths are longer than 15 characters. Proxy count is therefore
necessary but not sufficient. Base path length is the second factor, and it is invisible in the
error the customer receives, which reports only that an error occurred.

Second, there is a limit of 1000 base paths per environment. The register is explicit that this
counts base paths and not revisions: "If your API proxies or revisions contain more than one
base path, the total number of base paths per environment must not exceed 1000." A revision
carrying four base paths consumes four slots.

Both are limitations described as a deliberate protective measure. The 1000-basepath limit is
introduced in the register as a temporary limit "to avoid potential failures when deploying API
proxy revisions". The word temporary should be quoted rather than promised.

The two groups on the same org are both compliant with the numbers a support engineer would
naturally check, which is why the ticket exists.

#### Correct remediation

Shorten base paths on the failing group if the owning teams can tolerate the client-visible
change, or split the group. Either reduces the effective proxy count against the length-adjusted
ceiling. Separately, count total base paths per environment rather than counting revisions,
since that is what the environment-level limit measures.

#### Verification

Deploy successfully to the failing group, then repeat the count across every environment in the
org, because the environment ceiling is per environment and a group split does not reset it.

#### Common incorrect answers

Comparing only the proxy count between the two groups. Both are 604 and the counts are not the
discriminator.

Raising a quota, ticket or support request. These are documented design limits, not a
capacity entitlement that can be negotiated.

Recounting revisions instead of base paths. A revision with several base paths consumes several
slots against the 1000 ceiling.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Diagnostic method | Compares proxy counts only | Notices base path length | Identifies both the 15-character factor and the per-environment 1000 base path limit |
| Technical correctness | Says the org is full | Names the 800 proxy limit | Explains the length-adjusted threshold and base path counting |
| Cross-group reasoning | Assumes shared org means shared limit | Notes the groups differ | Uses base path length as the discriminator between the two groups |
| Quality of next step | Opens a quota request | Advises shortening paths | Splits the group or shortens paths, and recounts per environment |

#### Critical failures: ruling the issue out after confirming both groups are under 800 proxies;
counting revisions instead of base paths.

#### References

- Known issues register (entries 301845257 and 329304975):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Environment groups:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/environmentgroups-working-with>

---

### MED-43. The 404 that a version bump does not fix

#### Scenario metadata

- ID: MED-43
- Difficulty: medium
- Primary topic: base path wildcards
- Secondary topics: opt-in fixes, routing precedence, version-gated behaviour
- Product: Apigee and Apigee hybrid
- Origin: reported real-world case (official known issue 378686709, FIXED but not enabled by
  default; hybrid 1.14.3 and 1.15.1 with a procedure required)
- Versions: checked 2026-10-12
- Evaluation objectives: the fix exists and the customer is on a version that contains it, and
  it is still 404ing, because the fix is opt-in. Version alone cannot discriminate here
- Skills expected: apigee-support-core, apigee-opdk-upgrader

#### Initial support ticket

> We upgraded hybrid to 1.14.3 last week to pick up the wildcard base path fix. `/a/v1/b` works.
> `/a/*/c` still returns 404. We are on a fixed version. What is going on?

#### Initial evidence

Two proxies in the same environment: `Proxy-1` with base path `/a/v1/b`, `Proxy-2` with base path
`/a/*/c`. Requests to `Proxy-1` resolve. Requests to `Proxy-2` return 404. Both are deployed and
listed. The environment group is healthy and other proxies on it serve traffic.

#### Expected investigation

The agent should notice that one of the two proxies in the same environment, on the same path
prefix, in the same deployment, works while the other does not. That asymmetry rules out the
environment group and the deployment and points at base path conflict resolution.

#### Diagnostic evidence

The wildcard path `/a/*/c` is being evaluated as `/a/v1/c`, which collides with the explicit
`/a/v1/b` prefix.

#### Ground-truth resolution

The use of wildcards in Apigee proxy base paths may conflict with other explicit base paths,
resulting in a `404`. In this case, calls to the explicit base path resolve successfully while
calls to `Proxy-2` may return a `404`, if the wildcard path is evaluated as `/a/v1/c`.

The important part is what the register says next: the issue is fixed in Apigee and in hybrid
1.14.3 and later, however the fix is **not enabled by default**. Enabling the use of wildcards
in base paths requires a support request for Apigee orgs, and a documented procedure for hybrid
orgs.

So the customer's premise is exactly wrong in the most confident possible way. They checked the
version, the version says fixed, and the fix has not been switched on for their org. An agent
that treats "fixed in 1.14.3" as "therefore not our problem" closes the case wrongly, and an
agent that recommends only an upgrade has already been given the upgrade.

Note the asymmetry that makes this hard to spot from the outside: an agent that establishes "the
environment group is serving traffic" has proved nothing, because a sibling proxy in the same
environment is serving fine.

#### Correct remediation

For an Apigee org, contact Apigee support to request that the wildcard base path fix be enabled.
For a hybrid org, follow the documented procedure for 1.14.3 or 1.15.1. Until then, remove the
wildcard and use explicit base paths, which is the only configuration guaranteed to be unambiguous.

#### Verification

Call the wildcard path and confirm it resolves. Then confirm the explicit path still resolves,
because the fix changes conflict resolution between them rather than in isolation.

#### Common incorrect answers

Recommending another upgrade. The customer is already on a version that contains the fix.

Concluding the environment group or the deployment is at fault. Other proxies on the same group
serve traffic, including a sibling on the same prefix.

Removing the conflicting explicit base path without asking. That is a client-visible breaking
change for whichever team owns it.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Recommends an upgrade | Identifies wildcard and explicit base path conflict | Names the `/a/v1/c` collision and the opt-in nature of the fix |
| Diagnostic method | Checks the group | Compares the two base paths | Uses the working-versus-failing asymmetry within one environment |
| Version handling | Reads "fixed" as resolved | Notices opt-in wording | States that hybrid 1.14.3 contains a fix that is disabled by default |
| Quality of next step | Upgrades again | Deletes the explicit path | Requests enablement for Apigee, follows the procedure for hybrid |

#### Critical failures: telling the customer to upgrade when they are already on a fixed version;
concluding the environment group is at fault because other proxies on it serve traffic.

#### References

- Known issues register (entry 378686709):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Upgrading Apigee hybrid: <https://cloud.google.com/apigee/docs/hybrid/v1.17/upgrade>

---

### MED-44. Headers that were removed, then put back, and are still pinned

#### Scenario metadata

- ID: MED-44
- Difficulty: medium
- Primary topic: distributed trace and `x-b3` headers
- Secondary topics: version-gated behaviour, relied-upon defaults, per-org pinning
- Product: Apigee and Apigee hybrid
- Origin: reported real-world case (official known issue 422757662, reverted in Apigee
  1-15-0-apigee-7 and the matching Apigee release)
- Versions: checked 2026-10-12
- Evaluation objectives: the behaviour is non-monotonic across versions and pinned per org, so
  neither "the version" nor "the org version" is sufficient. An agent must establish both
- Skills expected: apigee-support-core

#### Initial support ticket

> Our backend stopped receiving `x-b3` correlation headers last month. We did not change
> anything on the backend. Distributed Trace is switched off in our org, which I assumed meant
> nothing trace related was sent. Help me find what changed.

#### Initial evidence

`x-b3` headers are absent at the target. Distributed Trace is disabled in the org. No proxy
policy has been edited. The org was last upgraded recently.

#### Expected investigation

The agent should notice that the assumption embedded in the ticket, that a disabled Distributed
Trace implies no `x-b3` headers, is exactly the assumption the platform once stopped making and
then partially restored. It should establish the org's version and whether the reversion has been
pinned for this org.

#### Diagnostic evidence

The org is on a release in the affected window where the headers stopped being sent when
Distributed Trace is disabled. A sibling org on the same version that was pinned to the old
behaviour still receives the headers.

#### Ground-truth resolution

In Apigee 1-15-0-apigee-5 and hybrid 1.15.0, Apigee stopped sending `x-b3` headers to target
endpoints when Distributed Trace is disabled. Some installations were relying on `x-b3` headers
being sent regardless of whether Distributed Trace was enabled or disabled. The change was
therefore reverted starting in Apigee 1-15-0-apigee-7.

Three properties make this hard to resolve by version alone.

The behaviour is **non-monotonic**. It was present, it disappeared, it came back. "Fixed in
1-15-0-apigee-7" does not mean a newer org has the new behaviour; it means the removal was
undone. An agent that assumes the present state is the newest behaviour will be wrong twice.

The fix is **not enabled by default**. The register says that anyone experiencing the issue
should reach out to Apigee to revert the change for now in their org. That is a per-org pin. Two
orgs on the same version can behave differently, and version cannot tell them apart.

The headers were a **latent default in use**. Nobody configured them. They were injected because
something depended on them once, and nothing recorded that dependency.

The register closes with a caution worth surfacing to the customer: Apigee does not recommend
relying on `x-b3` headers when Distributed Trace is disabled, because doing so will not guard
against a future change to this behaviour.

#### Correct remediation

Ask Apigee to re-pin this org to the previous behaviour, as the register directs, and
simultaneously start removing the backend's dependence on `x-b3` headers. The reversion is a
reprieve with an explicit warning attached, not a permanent answer, and a support engineer who
applies only the first half is handing the customer the same problem later.

#### Verification

Confirm the target receives `x-b3` headers again, and confirm Distributed Trace remains disabled so
the change was not achieved by turning tracing on.

#### Common incorrect answers

Enabling Distributed Trace to get headers back. That changes the customer's tracing behaviour and
costs money to fix a correlation problem.

Asserting the org must be on 1-15-0-apigee-7 or later. The org may already be, and still be
affected, because the fix is per-org opt-in.

Telling the customer the header removal was a bug they must live with. It was reverted, at their
request, on request.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Enables Distributed Trace | Identifies the `x-b3` removal window | States it was reverted and that the reversion is per-org opt-in |
| Diagnostic method | Inspects proxy policies | Checks org version | Checks org version and whether the org is pinned to old behaviour |
| Version handling | Assumes newer means current behaviour | Notices the reversion | Recognises the behaviour is non-monotonic across versions |
| Quality of next step | Turns tracing on | Requests the pin | Requests the pin and starts removing the backend dependency |

#### Critical failures: enabling Distributed Trace as the remedy; concluding that an org on a
version at or past 1-15-0-apigee-7 cannot be affected.

Not a critical failure: recommending removing the `x-b3` dependency first, without requesting the
pin. It is the better long-term advice but does not restore the customer's current behaviour.

#### References

- Known issues register (entry 422757662):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Distributed trace: <https://cloud.google.com/apigee/docs/api-platform/debug/trace-overview>

---

### MED-45. `The URI contain illegal characters` after a version bump

#### Scenario metadata

- ID: MED-45
- Difficulty: medium
- Primary topic: proxy runtime HTTP handling
- Secondary topics: transitive dependency upgrades, request-side misdiagnosis
- Product: Apigee
- Origin: reported real-world case (official known issue 480997525, FIXED in Apigee
  1-17-0-apigee-2)
- Versions: checked 2026-10-12
- Evaluation objectives: a 400 that names the URI is blamed on the request. Nothing about the
  request changed. The discriminator is the Apigee version, not the traffic
- Skills expected: apigee-support-core

#### Initial support ticket

> Since the weekend upgrade roughly 40% of our API calls fail with `The URI contain illegal
> characters`. We looked at our base paths and our target URLs and they are all valid. We have
> not changed any URLs. Can you tell us which URL is malformed?

#### Initial evidence

Requests fail with status 400 and the message `The URI contain illegal characters`. Base paths,
target endpoints and request encoding are unchanged and valid. The failures started on a version
bump, with no proxy change.

#### Expected investigation

The agent should notice that the customer has already eliminated the request side, that the error
is a 400 pointing at the URI, and that the only thing that changed is the platform version. That
combination is the signature of a runtime dependency regression rather than a bad request.

#### Diagnostic evidence

The org is on Apigee 1-17-0-apigee-1. The proxy runtime in that release carries a Netty upgrade to
4.1.129.Final.

#### Ground-truth resolution

In Apigee version 1-17-0-apigee-1, a Netty upgrade to 4.1.129.Final introduced a regression. This
can cause API proxy calls to fail with a `400` status code and the error message `The URI contain
illegal characters`. It is tracked externally as netty/netty#16020.

The register quotes the string as `The URI contain illegal characters`, without the `s`. An agent
that silently corrects the grammar will fail an exact-match evaluation, so the string should be
quoted as it stands.

This is a bug, not a limitation, and it is fixed in the immediately following release. The
misdiagnosis risk is what makes it a medium scenario rather than a trivia question: a 400 with a
message about illegal URI characters points the engineer at the request, and the request is the
one thing that did not change. Chasing base paths, target URLs and header encoding is
well-reasoned and entirely wasted.

#### Correct remediation

Upgrade the org to Apigee 1-17-0-apigee-2. No proxy change is required and none should be made.

#### Verification

Confirm successful calls on a sample of the previously failing requests, then confirm the
unaffected traffic did not change behaviour, since the fix is in the shared runtime.

#### Common incorrect answers

Asking the customer to URL-encode a path segment. The URIs are valid and the platform broke.

Recommending a change to base paths or target endpoints. Any change here is a real client-visible
regression introduced while chasing a platform defect.

Recommending quoting the error as `The URI contains illegal characters`. It is the grammatical
form that does not appear.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Advises URL encoding | Identifies a runtime regression | Names the Netty 4.1.129.Final upgrade and 1-17-0-apigee-2 |
| Diagnostic method | Audits base paths | Checks the version | Checks the version against the single affected release |
| Error handling | Paraphrases the string | Quotes it correctly | Quotes `The URI contain illegal characters` verbatim and recognises it as client-side framing |
| Quality of next step | Changes proxy URLs | Recommends an upgrade | Recommends upgrading to 1-17-0-apigee-2 with no proxy change |

#### Critical failures: recommending a proxy or URL change; telling the customer their request is
malformed.

#### References

- Known issues register (entry 480997525):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Upstream issue: <https://github.com/netty/netty/issues/16020>

---

### MED-46. The 502 that means your certificate is bad

#### Scenario metadata

- ID: MED-46
- Difficulty: medium
- Primary topic: target endpoint TLS
- Secondary topics: status code semantics, component misattribution, certificate validation
- Product: Apigee hybrid
- Origin: reported real-world case (official known issue 310384001, still OPEN)
- Versions: checked 2026-10-12
- Evaluation objectives: the customer enabled certificate enforcement and is now told 502, which
  means upstream failure and sends the investigation to the wrong component. The correct reading
  is that the target certificate failed validation
- Skills expected: apigee-support-core, apigee-opdk-troubleshooter

#### Initial support ticket

> We turned on certificate checking on our target endpoint because we wanted to stop accepting
> expired certs. Now that backend returns 502 Bad Gateway. The host is up, it answers on 443, and
> the same URL works from a browser. The gateway cannot reach it.

#### Initial evidence

The target `<SSLInfo>` block contains `<Enforce>true</Enforce>`. The target responds to `502`. The
target is reachable and healthy by every other measure. The status code is 502 rather than the
503 that would suggest a target certificate problem.

#### Expected investigation

The agent should resist reading 502 as "upstream unavailable", because the target is demonstrably
available, and should look at what the customer's change actually asked the platform to do.

#### Diagnostic evidence

The target's certificate chain does not validate against the runtime's trust store. `<Enforce>` is
set to `true` in the target `<SSLInfo>` block, which selects default validation.

#### Ground-truth resolution

Cert validation failures may return a 502 instead of a 503 error response when users add the tag
`<Enforce>true</Enforce>` in the target `<SSLInfo>` block for default validation of TLS target
endpoint certificates. This is a limitation and it is still OPEN, so the correct answer is not to
wait for a fix.

The status code is actively misleading here, which is the whole point of the entry. A 502 reads
as "the upstream returned something unusable", so an engineer checks target health, L7 routing
and gateway reachability, and finds all of them fine, because nothing is down. The cause is the
target certificate, and the code conceals it.

It is also worth being precise about what the customer did. They added `<Enforce>true</Enforce>`
*because* they wanted certificate validation. They did not weaken it. Default validation is being
enforced and the platform is reporting the result with the wrong code.

A related documented behaviour from the same register, entry 205666368, states that Apigee hybrid
does not validate the target certificate by default. Read together the two entries say that the
default is no validation, and that turning validation on produces a misleading status code.

#### Correct remediation

Fix the target's certificate chain, or add the issuing authority to the appropriate truststore.
There is no configuration change that makes a 502 become a 503, because the code is the
platform's, and the register has the issue open rather than resolved.

#### Verification

Confirm the target certificate validates against the runtime trust store, then confirm the status
code is 200 or whatever the backend genuinely returns. Do not use the status code alone as proof,
since it is known to be wrong in this case.

#### Common incorrect answers

Investigating target availability and load balancing. The target is up; that is established.

Recommitting the proxy or restarting runtime pods. Neither changes certificate validation.

Telling the customer to remove `<Enforce>true</Enforce>` to make the error go away. That silently
returns them to no certificate validation at all, which is the opposite of what they asked for.

#### Evaluation rubric

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Investigates target availability | Suspects the certificate | States 502 here means target certificate validation failed |
| Diagnostic method | Trusts the status code | Notes the code contradicts the evidence | Recognises the documented 502-instead-of-503 behaviour with `<Enforce>` set |
| Component attribution | Blames the gateway | Blames the backend broadly | Blames the target certificate chain against the runtime trust store |
| Quality of next step | Removes `<Enforce>` | Suggests restarting pods | Fixes the chain or truststore, and does not disable enforcement |

#### Critical failures: advising removal of `<Enforce>true</Enforce>` as the fix; opening a load
balancing or gateway investigation and closing it as an upstream outage.

Not a critical failure: not knowing the corresponding 503. The register gives only the observed
502, and inferring the intended 503 is a bonus rather than a requirement.

#### References

- Known issues register (entries 310384001 and 205666368):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- API calls failing with TLS errors:
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/ingressgateway/api-calls-failing-tls-errors>

---
