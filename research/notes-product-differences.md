# Product differences: Apigee X vs Apigee hybrid vs Edge for Private Cloud (OPDK)

Research date: 2026-10-11. All statuses observed via `research/fetch.sh` or bare `curl -sL -o /dev/null -w '%{http_code}'`.

**OPDK version used for all deep-page citations below: `v4.53.01`** (latest confirmed). The version-in-URL pattern was verified across six releases (see section 1).

Evidence labels follow `RESEARCH-RECIPE.md`: **documented** (stated on a fetched page), **observed** (executed/reproduced), **reported**, **hypothesis**.

---

## 1. VERIFIED PAGES

Format: Title | URL | HTTP status | bytes of extracted body

| Title | URL | Status | Bytes |
| --- | --- | --- | --- |
| Apigee technical feature overview (was "Compare Apigee products") | https://cloud.google.com/apigee/docs/api-platform/get-started/compare-apigee-products | 200 | 11304 |
| What is Apigee hybrid? | https://cloud.google.com/apigee/docs/hybrid/what-is-hybrid | 200 | 11551 |
| Apigee hybrid — upgrade stub (see section 5) | https://cloud.google.com/apigee/docs/hybrid/upgrade | 200 (STUB) | 0 |
| Upgrading Apigee hybrid | https://cloud.google.com/apigee/docs/hybrid/latest/upgrade | 200 | 78108 |
| Installing Apigee hybrid: before you begin | https://cloud.google.com/apigee/docs/hybrid/latest/install-before-begin | 200 | 10254 |
| Installing Apigee hybrid: the big picture | https://cloud.google.com/apigee/docs/hybrid/latest/big-picture | 200 | 11502 |
| Apigee hybrid: supported platforms and versions | https://cloud.google.com/apigee/docs/hybrid/supported-platforms | 200 | 58518 |
| Apigee hybrid: ports | https://cloud.google.com/apigee/docs/hybrid/latest/ports | 200 | 19075 |
| Apigee hybrid: admin overview | https://cloud.google.com/apigee/docs/hybrid/latest/administer-overview | 200 | 10379 |
| Apigee hybrid: service configuration overview | https://cloud.google.com/apigee/docs/hybrid/latest/service-config | 200 | 17774 |
| Apigee hybrid: project/org setup overview (precog) | https://cloud.google.com/apigee/docs/hybrid/latest/precog-overview | 200 | 9743 |
| Apigee hybrid: runtime logs | https://cloud.google.com/apigee/docs/hybrid/latest/runtime-logs | 200 | 11976 |
| Apigee hybrid: logging | https://cloud.google.com/apigee/docs/hybrid/latest/logging | 200 | 8562 |
| Apigee hybrid: creating an environment | https://cloud.google.com/apigee/docs/hybrid/latest/environment-create | 200 | 11768 |
| Apigee hybrid: about environments | https://cloud.google.com/apigee/docs/hybrid/latest/environments-about | 200 | 14278 |
| Apigee hybrid: metrics collection | https://cloud.google.com/apigee/docs/hybrid/latest/metrics-collection | 200 | (fetched, 200) |
| Apigee hybrid: data collection overview | https://cloud.google.com/apigee/docs/hybrid/latest/data-collection-overview | 200 | (fetched, 200) |
| Apigee hybrid: configuration properties reference | https://cloud.google.com/apigee/docs/hybrid/latest/config-prop-ref | 200 | 479971 |
| Apigee hybrid release notes | https://cloud.google.com/apigee/docs/hybrid/release-notes | 200 | 819438 |
| About environments and environment groups | https://cloud.google.com/apigee/docs/api-platform/fundamentals/environments-overview | 200 | 22460 |
| Edge for Private Cloud release notes (post-Sep-2026) | https://cloud.google.com/apigee/docs/edge-private-cloud/release-notes | 200 | 3571 |
| Apigee Edge for Private Cloud release notes (45301) | https://docs.apigee.com/release/notes/45301-edge-private-cloud-release-notes | 200 | 9971 |
| Apigee Edge release notes archive (pre-Sep-2026) | https://docs.apigee.com/release/notes/apigee-release-notes | 200 | (status only) |
| Known issues with Edge / Edge for Private Cloud | https://docs.apigee.com/release/known-issues | 200 | 25961 |
| **Compare Apigee Edge to Apigee X** (the real feature-difference page) | https://docs.apigee.com/migration-to-x/compare-apigee-edge-to-apigee-x | 200 | 26454 |
| What is Apigee Edge? | https://docs.apigee.com/api-platform/get-started/what-apigee-edge | 200 | 16042 |
| Edge for Private Cloud index (unversioned root) | https://docs.apigee.com/private-cloud/ | 200 | 10606 |
| Edge for Private Cloud overview v4.53.01 | https://docs.apigee.com/private-cloud/v4.53.01/overview | 200 | 9627 |
| OPDK port requirements v4.53.01 | https://docs.apigee.com/private-cloud/v4.53.01/port-requirements | 200 | 17382 |
| OPDK installation requirements v4.53.01 | https://docs.apigee.com/private-cloud/v4.53.01/installation-requirements | 200 | 26392 |
| OPDK installation topologies v4.53.01 | https://docs.apigee.com/private-cloud/v4.53.01/installation-topologies | 200 | 13251 |
| OPDK upgrade paths v4.53.01 | https://docs.apigee.com/private-cloud/v4.53.01/upgrade-paths | 200 | 581 |
| OPDK starting/stopping/restarting v4.53.01 | https://docs.apigee.com/private-cloud/v4.53.01/starting-stopping-and-restarting-apigee-edge | 200 | 3797 |
| OPDK after the install v4.53.01 | https://docs.apigee.com/private-cloud/v4.53.01/after-the-install | 200 | 7971 |
| OPDK how to configure Edge v4.53.01 | https://docs.apigee.com/private-cloud/v4.53.01/how-configure-edge | 200 | (fetched, 200) |
| OPDK test the install v4.53.01 | https://docs.apigee.com/private-cloud/v4.53.01/test-install | 200 | 4429 |
| OPDK Edge configuration file reference v4.53.01 | https://docs.apigee.com/private-cloud/v4.53.01/edge-configuration-file-reference | 200 | (fetched, 200) |
| Edge org structure | https://docs.apigee.com/api-platform/fundamentals/apigee-edge-organization-structure | 200 | 10135 |
| Edge deploy via Management API | https://docs.apigee.com/api-platform/deploy/deploy-api-proxies-using-management-api | 200 | 3048 |
| Edge service requests | https://docs.apigee.com/api-platform/system-administration/service-requests | 200 | 1842 |
| Apigee REST: organizations.instances.attachments/create | https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.instances.attachments/create | 200 | 2436 |
| Apigee REST: organizations.instances.attachments/list | https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.instances.attachments/list | 200 | 5296 |
| Apigee REST: organizations.instances/list | https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.instances/list | 200 | 5062 |
| Apigee REST: organizations.envgroups | https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.envgroups | 200 | 4811 |

### Version-in-URL pattern verification (observed)

**OPDK.** `docs.apigee.com/private-cloud/<version>/<page>` confirmed working across releases. Same two pages checked at six versions:

| Version | `/port-requirements` | `/installation-requirements` |
| --- | --- | --- |
| v4.50.00 | 200 | 200 |
| v4.51.00 | 200 | 200 |
| v4.52.00 | 200 | 200 |
| v4.52.02 | 200 | 200 |
| v4.53.00 | 200 | 200 |
| v4.53.01 | 200 | 200 |

- `https://docs.apigee.com/private-cloud/` → 200 (unversioned root works).
- `https://docs.apigee.com/private-cloud/latest/` → 200 (alias works).
- `https://docs.apigee.com/private-cloud/v4.54.00/` → **404**. v4.53.01 is the newest release published.
- **The version segment is mandatory.** `https://docs.apigee.com/private-cloud/port-requirements` → **404**.
- Version list observed in the v4.53.01 nav: v4.51.00, v4.52.00, v4.52.01, v4.52.02, v4.53.00, v4.53.01 (plus older 4.16–4.19 links).

**Hybrid.** Version is `latest` or explicit `v1.x`: `https://cloud.google.com/apigee/docs/hybrid/latest/<page>` → 200. Latest = **v1.17**. Observed dropdown: supported = v1.14–v1.17; unsupported/EOL = v1.1–v1.13.
**Trap:** `https://cloud.google.com/apigee/docs/hybrid/upgrade` (no version) returns **HTTP 200 but is a stub** reading "The equivalent page does not exist in the selected hybrid version." The recipe's fetch.sh has been updated to detect this marker and report `200-STUB`. Never cite a bare `hybrid/<page>` URL.

---

## 2. CONFIRMED TECHNICAL FACTS

### 2.1 The two comparison pages are not the same, and the X-hosted one was rewritten

- `cloud.google.com/.../compare-apigee-products` is now titled **"Apigee technical feature overview"** and compares **only Apigee X and Apigee hybrid**. It carries the banner "This page applies to Apigee and Apigee hybrid" and links out to Edge docs for anything else. **It contains no longer any "unsupported features" or "unsupported APIs" list.** (documented)
- The Edge-to-X feature removal list now lives at `docs.apigee.com/migration-to-x/compare-apigee-edge-to-apigee-x`. That page is the citable source for what Edge lost in X. (documented)
- Same page, three hosting rows (observed verbatim): Apigee Edge for Public Cloud = Apigee's cloud / Apigee; Apigee Edge for Private Cloud = customer's private data center / **Customer**; Apigee X = Google Cloud / Apigee; Apigee hybrid = both / Apigee manages management plane, customer manages runtime plane.

### 2.2 Features Google does not plan to support in Apigee X (exact list, verbatim)

Source: https://docs.apigee.com/migration-to-x/compare-apigee-edge-to-apigee-x — section "Which Apigee Edge features are not supported in Apigee X?" (documented). The page states "Google does *not* plan to support the following features":

1. Apigee Edge Extensions
2. OpenAPI Specification store
3. APIs to search for or revoke OAuth access tokens (because tokens are hashed)
4. OAuth v1 or OAuth OAuthv1.0a policy
5. Trireme (EOL'd on 10/10/2019)
6. Headers prefixed with `X-Apigee-` are not supported in Apigee X and are stripped from requests and responses before sending to targets and clients.
7. The Apigee Edge `proxy_read_timeout` property is not supported in Apigee X.

Also on the same page (documented):
- **StatisticsCollector policy is not supported** (replaced by the new DataCapture policy).
- **MessageLogging policy does not support file logging.**
- `reasonPhrase` — Not supported.
- `[@.length-x]` in JSONPath — not supported in Apigee X; superseded by `[-x]`. Concrete behavioural example on the page: for input `$.books[@.length-1]`, Edge returns `{“name”: “B”}` and X returns `[{“name”: “B”}]`.
- **Node.js API proxies are not supported**; recommendation is to host Node.js apps as separate containers in Kubernetes.
- **SOAP services in the Build a proxy wizard: not supported** (use the wsdl2apigee open source project).
- **Organization-level resources: cannot be used.**
- Hosted targets → use Cloud Run or Cloud Functions.
- Microgateway / Apigee Adapter for Istio → use Apigee Adapter for Envoy.
- Sense → use Advanced API Security.
- Companies/developers → AppGroups.
- Northbound mTLS → supported via Google Cloud load balancers (not natively).
- Active Health Checks: supported for External MIGs, **not** supported when using Private Service Connect.
- **HTTP/1.1 header field names are lowercased when forwarded to the backend in X/hybrid; Edge preserves case.** (A classic cross-product symptom.)
- Roles: managed through Google Cloud console IAM; Google has no plans for Apigee-style fine-grained IAM roles (marked "Planned").
- CwC (Code with Config) — "Planned", i.e. not available.

### 2.3 Unsupported Apigee Edge APIs (exact list, from the same page)

Table titled "Unsupported Apigee Edge APIs (that do not have Apigee X API equivalents)":

| API category | Unsupported Edge APIs |
| --- | --- |
| API Monitoring | No APIs supported |
| API proxies | Force undeploy API proxy; Get npm dependencies; Manage npm modules |
| Audits | Use Stackdriver Logging API |
| Cached logs | No APIs supported |
| Companies | No APIs supported |
| Company apps | No APIs supported |
| Company app family | No APIs supported |
| Company app keys | No APIs supported |
| Debug sessions | Cannot stop trace sessions; cannot delete individual transactions |
| Developer app | Get count of API resources |
| Developer app family | No APIs supported |
| Extensions | No APIs supported |
| Keystore: Truststore | Test a keystore or truststore |
| LDAP | No APIs supported |
| Monetization | No APIs supported |
| OAuth V2 | No APIs supported |
| Policies | No APIs supported |
| Resource files | API proxy revision scope; Organization scope |
| Sense | No APIs supported |
| Users and user roles | Use Google IAM APIs instead |
| Virtual hosts | No APIs supported |

### 2.4 API behaviour changes Edge → X (documented, same page)

- Base domain: Edge `api.enterprise.apigee.com` → X `apigee.googleapis.com`.
- Media types: Edge `application/json` **and** `application/xml` → X `application/json` only.
- Authentication: Edge OAuth2, SAML, Basic → X OAuth2 only.
- Timestamps in keys: Edge `int64` (`"createdAt": 1234`) → X `String` (`"createdAt": "1234"`). **Silent-type-change trap for parsers.**
- `expand=false` shape: Edge returns a bare array `["helloworld","weather"]`; X returns `{"proxies":[{"name":"helloworld"},{"name":"weather"}]}`.
- Query params prefixed by underscore: Edge supported (`_optimal=true`) → X **not** supported (`optimal=true`).
- Payload properties `created_by`, `modified_by`, `self`: Edge supported → X **not** supported.
- Default values in payloads: Edge includes them → X does not.
- Error structure: Edge `{"code","message","contexts":[]}` → X `{"error":{"code","message","status","details":[...]}}`.
- Cache deletion response: Edge `200 OK` + cache details → X **`204 No Content`**.
- Cache API operations: Edge has list/create/get/update/delete/clear-all/clear; **X has list and delete only**, plus an automatic short-lived L1 cache on proxy deployment.
- Metrics APIs: `userId` omitted from Async Query List responses; `createdBy`/`lastModifiedBy` removed from Custom Report responses; no APIs for daily analytics emails.

### 2.5 Trace/debug differences (documented; the X+hybrid table is on both compare pages, the three-way table on the Edge→X page)

| Feature | Apigee Edge Cloud | Apigee X and hybrid |
| --- | --- | --- |
| Timeliness | Real time; synchronous | Slight delay; asynchronous |
| Session name/ID | Accepts session name from the user | Doesn't accept session name from the user |
| Filters | Basic (header, query parameter) | Complex filtering with AND/OR, any flow variable, same syntax as conditionals |
| Session timeout | Defines session length **and** retention; default 20 min via API, 10 min via UI | Defines **only** session length, starting when the MP receives the request; default 5 min via API, 10 min via UI; data persisted 24 hours before hybrid auto-deletes |
| Session validity | (not applicable / none) | Synchronizers may disregard the creation request if it does not start in time; **keep Synchronizer clocks in sync** |
| Trace request count | Max 20 per Message Processor | Default 10 per MP; **max 15** |
| Stop debug session | Supported | **Not supported** |
| Delete specific transactions | Supported | **Not supported** |

### 2.6 Monetization differences (documented)

Edge: rate plans attach to API product *bundles* attachable to multiple products; developers *purchase rate plans*; quotas at **API proxy** level; published rate plans can only be expired (no edit/delete); no wizard; `MonetizationLimitsCheck` blocks only **after the first call is processed**; prepaid/postpaid configurable for both developers and rate plans.
X/hybrid: rate plans attach **one-to-one to API products**; developers purchase API products; quotas at **API product** (business) level; published rate plans can be expired, edited, moved to draft, or deleted; wizard + preview tool; `MonetizationLimitsCheck` blocks **immediately**; prepaid/postpaid only for developers; monetization data captured automatically, overridable with DataCapture.

OPDK-specific (from https://docs.apigee.com/private-cloud/): **Monetization Services cannot be installed on an All-in-One (AiO) configuration**, and **Edge Gateway + Analytics are prerequisites** for Monetization Services. Monetization components are Edge Management Server + Edge Message Processor.

### 2.7 Hybrid architecture — what runs where (documented)

- Management plane (Google-hosted, Google-maintained): Apigee hybrid UI, Apigee APIs, **UAP** (Unified Analytics Platform). Reaches runtime data via **MART**.
- Runtime plane (customer Kubernetes): **Message Processor (MP)**, **Synchronizer**, **Cassandra**, **MART**.
- **MART** = Management API for Runtime data. Sits on the runtime plane, authenticates/authorizes, does business validation, reads/writes Cassandra. It is **stateless**. You do not call MART directly — the management plane reaches it through the **Apigee Connect agent** using a service account with the **Apigee Connect Agent role**. **MART does not receive proxy requests**; those go to the Runtime ingress controller and then to MPs.
- **Synchronizer** polls the management plane and stores the *contract* (proxy bundles, shared flows, flow hooks, environment info, shared resources, **target server definitions**, **TLS settings**, **KVM names**, data masks) as local JSON. **If the management plane connection drops, runtime services keep working** — this is the single most useful hybrid troubleshooting fact.
- **Cassandra** (deployed as a StatefulSet node pool) stores KMS, KVM, OAuth, MART data, monetization data, quotas, response cache. Both MART and the MPs read/write the same datastore.
- Supported platforms: Google Distributed Cloud (bare metal/VMware), AWS, Bare Metal, EKS, GKE, OpenShift, Anthos Service Mesh ingress. Latest hybrid v1.17 maps to Kubernetes 1.33.x on GKE/Anthos/EKS/RKE, 1.34.x on AKS, OpenShift 4.20.
- Hybrid ingress: **Anthos Service Mesh / Istio Ingress** hands requests to the Router/MP; keys and certs are deployed **directly to Kubernetes**.
- An **MP pod can only serve one environment** (Apigee X and hybrid).
- Hybrid metrics: **one Prometheus server per cluster** for all services (Edge contrast: **each component configured with JMX**). Current hybrid docs describe an **OpenTelemetry collector pod per node** scraping application metrics to Cloud Operations.

### 2.8 Hybrid prerequisites (documented)

Google Cloud project, billing account, `gcloud` CLI installed; enable required GCP APIs (`precog-enableapi`); create the Apigee organization (`precog-provision`); **create an environment AND an environment group** (`precog-add-environment`). Kubernetes permissions are managed via RBAC if installation is delegated. Note on VPC Service Controls: follow the VPC SC guidance before proceeding.

### 2.9 Hybrid upgrade (documented)

- Same procedure for minor (1.16 → 1.17) and patch (1.17.0 → 1.17.1) upgrades.
- **You must be on 1.16 or later to go to 1.17.** From 1.15 or older you must upgrade to 1.16 first.
- Upgrading the Apigee controller to 1.17.1 causes **all Apigee deployments to undergo a rolling restart**; **may require downtime**. To minimize it, run at least two clusters, divert production traffic to one, take the other offline, upgrade, repeat.
- Backup your `$APIGEE_HELM_CHARTS_HOME/` directory before upgrading.
- Hybrid v1.17 changes: MCP support, root CA certificate rotation (phased, no downtime), **TLS 1.3 support**, forward proxy support for AI policies, semantic cache PSC endpoint support.
- **A hybrid "upgrade" is a Helm chart upgrade, not an installer run.** Per-environment pattern: `helm upgrade ENV_RELEASE_NAME apigee-env/ --install --namespace APIGEE_NAMESPACE --set env=ENV_NAME -f OVERRIDES_FILE`. Note `ENV_RELEASE_NAME` must be **unique within the installation** — if environment and environment group share a name (e.g. both `dev`), use distinct release names like `dev-env-release` / `dev-envgroup-release`. If you see `UPGRADE FAILED: "test" has no deployed releases`, change `upgrade` to `install`.

### 2.10 OPDK upgrade paths (documented, v4.53.01 page)

- To reach **4.53.01**: upgrade directly **from 4.52.02 or 4.53.00**.
- To reach **4.53.00**: you must first be on **4.52.02**. **Direct upgrades from versions earlier than 4.52.02 are not supported.**
- Edge UI in 4.53.00+ shows an **EOL warning pop-up** (documented under known issues).

### 2.11 OPDK components and operations (documented, https://docs.apigee.com/private-cloud/)

- Gateway: Edge Management Server, Apache ZooKeeper, Apache Cassandra, Edge Router, Edge Message Processor, OpenLDAP, Edge UI (new) + Classic UI.
- Analytics: Qpid (Apache Qpid messaging + `edge-qpid-server`) and Postgres (`edge-postgres-server` + `apigee-postgresql`).
- Roles: Router terminates TLS/SSL and steers by virtual host; MP executes policies; Cassandra is the runtime data repo; ZooKeeper holds configuration and notifies servers; OpenLDAP manages system/org users and roles; Management Server is the Management API endpoint and talks to the UI.
- Service control: `/opt/apigee/apigee-service/bin/apigee-all [start|stop|restart|status]` and `apigee-service component_name [start|stop|restart|status]` (e.g. `apigee-service edge-management-server start`).
- Config: only `.properties` under `/opt/apigee/customer/application` are editable; the rest are view-only. Tokens live under `/opt/apigee/token`.
- Validation: `apigee-service apigee-validate install|setup|clean -f configFile`; creates a virtual host on the Router on **port 59001**; verify topology with `curl -u sysAdminEmail:password http://localhost:8080/v1/servers?pod=central|gateway|analytics`.
- Router nginx access log path seen in config: `/opt/apigee/var/log/edge-router/nginx/${org}~${env}.${port}_access_log`.

### 2.12 OPDK port requirements (documented, v4.53.01)

Management API **8080** on the Management Server, required for Router, MP, UI, Postgres, Apigee SSO (if enabled), Qpid. **8082** on the MP for Router→MP TLS (and for management regardless). Cassandra **7199**, Zookeeper **2181** (client) / 2888 (ensemble), Postgres **5432**, Qpid **5672** (broker) / 5636, **59001** for `apigee-validate`. All Management Servers must reach all Cassandra nodes in all data centers.

### 2.13 Environment groups and instance attachment — the precise answer

- **Environment groups: Apigee X AND hybrid. NOT Edge for Private Cloud.** (documented)
  - Applies banner: "This page applies to Apigee and hybrid" on https://cloud.google.com/apigee/docs/api-platform/fundamentals/environments-overview.
  - Hybrid requires one: install step 3 is "Create an environment group"; `precog-add-environment` and `virtualhosts` overrides reference environment group names ("the name of the virtualhosts must be the names of the environment groups").
  - `organizations.envgroups` in the Apigee REST reference carries **no** "not supported for hybrid" note (fetched and grepped).
  - Evidence of absence for Edge: `https://docs.apigee.com/api-platform/fundamentals/environments-overview` → **404**; the full 260-link Edge side nav contains **zero** links matching `envgroup` or `environment-group`; four probed envgroup-style Edge URLs all **404**. Edge documents environments as "either test or prod" (`apigee-edge-organization-structure`). This is consistent with environment groups being absent from Edge, but note the honest limit: absence of documentation is not a positive statement that the API fails. Label: **documented for X+hybrid; strongly supported (documentation-level) for Edge.**
  - Semantics: an environment **must be a member of at least one environment group** before its proxies are reachable. Hostnames live on the environment group, not on the environment.
- **Instance attachment: Apigee X ONLY. Explicitly "Not supported for Apigee hybrid."** (documented — verbatim note on `organizations.instances.attachments/create`, `.../list`, and `organizations.instances/list`)
  - Do not tell a hybrid customer to attach a runtime instance to an environment. In hybrid the equivalent is a Helm release per environment in the overrides file plus the Synchronizer contract.
  - Hybrid has its own unrelated `instanceID` override property (≤63 chars, must be identical for all orgs in one Kubernetes cluster; each region needs its own cluster).

---

## 3. PRODUCT BRANCHING TABLE

Every cell is either sourced inline or says **not verified**. "—" means the topic does not apply to that product.

| Topic | Apigee X | Apigee hybrid | Edge for Private Cloud |
| --- | --- | --- | --- |
| **Deployment** | Asynchronous; deployment status based on last runtime-plane check-in [compare]. Supports Proxy and Archive deployment types; Archive blocks UI resource/target-server edits and returns `FAILED_PRECONDITION` [environments-overview] | Asynchronous, same check-in semantics [compare]. Adding an environment is 2-step: create env in management plane, then add `envs[]` entry to overrides and `helm upgrade`/`install` per environment [environment-create] | Management API `/v1/o/$org/e/$env/apis/$api/revisions/1/deployments` POST for deploy, DELETE for undeploy [edge-deploy-mgmtapi]. Force-undeploy API is listed unsupported in X/hybrid [edge-vs-x] |
| **Key-value maps** | Encrypted, environment-scoped; **cannot add/update/view entries in the UI** — use keyvaluemaps.entries API or KeyValueMapOperations policy; use `private.` attribute with GET to hide values in a Trace session [compare] | Same X semantics [compare]. KVM **names** come down via Synchronizer; KVM data stored in Cassandra and served by MART [what-is-hybrid] | KVM exists in Edge; per-org/per-app/env scopes documented separately. Exact UI/API capability parity vs X: **not verified** on the pages fetched |
| **Target servers** | Supported; target server definitions distributed to runtime [what-is-hybrid] | Supported; definitions are part of the Synchronizer contract, stored locally [what-is-hybrid] | Supported (Edge); load-balancing across backend servers page exists on the Edge host (200). Parity details: **not verified** |
| **TLS** | Northbound mTLS via Google Cloud load balancers, not natively; each instance exposes HTTPS with a self-signed cert whose CA can be downloaded by querying the org [compare, edge-vs-x] | Ingress through Anthos Service Mesh; **keys and certs deployed directly to Kubernetes**; TLS 1.3 added in v1.17; root CA rotation supported [compare, upgrade] | Router terminates TLS/SSL and steers by vhost; MP TLS configurable (port 8082); creating-virtual-host page exists on Edge host (200). Exact cert workflow: **not verified** |
| **Analytics** | UAP in the management plane; Async Query List omits `userId`; custom reports omit `createdBy`/`lastModifiedBy`; no API for daily analytics emails [compare] | Runtime-plane data-collection pod uses **fluentd + UDCA** to feed **UAP** in the management plane [compare]. Analytics/deployment-status rows confirmed in data-collection-overview | **Qpid + Postgres** analytics, entirely on-premises [compare, private-cloud index]. Edge has a *Daily analytics emails* API that X lacks [edge-vs-x] |
| **Debugging** | Async trace; **max 15 requests per MP (default 10)**; cannot stop a trace session; cannot delete individual transactions [compare, edge-vs-x] | Same as X [compare]. Synchronizer clock skew can cause a session creation request to be discarded; trace data auto-deleted after 24 hours [compare]. Runtime logs via `kubectl logs -f -n APIGEE_NAMESPACE apigee-runtime-...` [runtime-logs] | Real-time synchronous trace; accepts user session name; **max 20 requests per MP**; can stop sessions and delete individual transactions [edge-vs-x]. Has `nodetool` — **not verified from a fetched page in this research round** |
| **Environment groups** | Supported; an environment must belong to ≥1 envgroup; hostnames defined on the group [environments-overview] | Supported and **required** by the install flow; virtualhost names must equal environment group names [install-before-begin, environments-about] | **Not documented.** environments-overview → 404; zero envgroup links in the 260-link Edge nav; 4 probed URLs → 404. Edge documents envs as test/prod only [edge-org-structure]. Strongly supported as absent |
| **Instance attachment** | Supported: `organizations.instances.attachments` create/list/get/delete, `organizations.instances` CRUD | **Explicitly "Not supported for Apigee hybrid"** (verbatim on three method pages). Use per-environment Helm releases + Synchronizer instead [x-instance-attach-*] | No `instances` resources in Edge. **not verified** as an explicit Edge statement |
| **Admin API** | Base domain `apigee.googleapis.com`; OAuth2 only; JSON only; String timestamps; `{"error":{code,message,status,details}}`; cache delete returns 204; cache API list+delete only [edge-vs-x] | Same X API surface, reached via Management Server → **MART** → Cassandra [what-is-hybrid, edge-vs-x] | Base domain `api.enterprise.apigee.com`; OAuth2/**SAML**/Basic; JSON **and XML**; int64 timestamps; `{"code","message","contexts"}`; cache delete returns 200 with details; full cache CRUD [edge-vs-x]. Local verification endpoint `http://localhost:8080/v1/servers?pod=...` [test-install]. `apigee-validate` UI on 59001 |
| **Upgrade procedure** | Not a customer procedure — Google-managed; customers deploy proxy revisions, not the platform | Helm chart upgrade. Must be on ≥1.16 to reach 1.17. Controller upgrade triggers **rolling restart of all deployments, may require downtime**; run ≥2 clusters and go one at a time; back up `$APIGEE_HELM_CHARTS_HOME/` first [upgrade] | Installer-driven via `update.sh`/apigee-setup and `apigee-service`. To 4.53.01: from **4.52.02 or 4.53.00** only. To 4.53.00: must be on **4.52.02**; earlier direct upgrades unsupported [upgrade-paths]. Edge UI shows EOL pop-up on 4.53.00+ [known-issues] |
| **Log locations** | Not verified in this round (no customer runtime) | `kubectl logs` on `apigee-runtime-*` pods in APIGEE_NAMESPACE [runtime-logs]; logging/metrics pages exist (200). Prometheus per cluster [compare] | Component logs under the Edge install tree, e.g. `/opt/apigee/var/log/edge-router/nginx/${org}~${env}.${port}_access_log` [how-configure]; `edge-message-processor system.log` referenced in known issues. Full per-component log path list: **not verified** in this round |

---

## 4. HOW TO IDENTIFY THE PRODUCT

The skill's existing "tells" list in `apigee-support-core` is sound. What this research adds, each sourced:

**Decisive, ask-for-this-first, single highest-value question:** "Which product and which version/release string?" Concretely:
- Ask for the **Management API base URL they are calling.** It resolves the product in one answer (documented):
  - `apigee.googleapis.com` → Apigee X **or** hybrid (then go to step 2).
  - `api.enterprise.apigee.com` → Apigee Edge (public **or** private — then go to step 3).
  - `http://<host>:8080/v1/o/...` on an internal host → **Edge for Private Cloud** (the OPDK test-install page uses exactly this form with `localhost:8080`).
- Ask for the **version/release string** and match it to the right doc tree: hybrid `1.17.1`; OPDK `4.53.01`. A procedure from the wrong release is wrong, not approximately right.

**Step 2 — X vs hybrid** (both use `apigee.googleapis.com`):
- Is there a **Kubernetes cluster** the customer operates? Any mention of `apigee-runtime` pods, a runtime plane, Istio/Anthos Service Mesh ingress, Prometheus per cluster, UDCA, or a **Synchronizer** → hybrid.
- Do they run `helm upgrade` against `apigee-org` / `apigee-env` charts, or maintain an `overrides.yaml` with `instanceID`/`org`/`envs[]` → hybrid.
- Do they have a **Google Cloud project holding the management plane** plus a separate data center runtime → hybrid.
- Is it a single fully Google-managed offering with no runtime of their own → **X**.

**Step 3 — Edge for Private Cloud** (tells, each anchored to a fetched page):
- `apigee-service`, `apigee-all`, `update.sh`, `/opt/apigee` install tree → OPDK (documented: starting-stopping page, how-configure page).
- ZooKeeper, OpenLDAP, Qpid, Postgres, `apigee-monit` → OPDK (documented: private-cloud index, how-configure component table).
- "All-in-One" / AiO topology, or a named **data center / POD** arrangement, or "pod=central/gateway/analytics" → OPDK (documented: installation-topologies, test-install).
- Note **Monetization cannot be installed on AiO** — an AiO install with monetization is a contradiction worth asking about (documented).

**Fast discriminator if they will only paste a URL or an error:**
- `*.apigee.net` proxy hostname is an **Edge public cloud** convention, not X/hybrid.
- `reasonPhrase`, `created_by`/`modified_by`/`self`, `application/xml`, or int64 timestamps in a response → **Edge**, because X explicitly dropped all of these (documented, edge-vs-x).
- An error saying trace/deployment status is **delayed or stale** → X or hybrid (async check-in), not Edge.

---

## 5. 404 / NOT FOUND

| URL | Status | Note |
| --- | --- | --- |
| https://cloud.google.com/apigee/docs/hybrid/upgrade | **200 but STUB** | Not a 404 — returns 200 with "The equivalent page does not exist in the selected hybrid version." Worse than a 404 for tooling. Use `/hybrid/latest/upgrade`. fetch.sh now reports `200-STUB`. |
| https://cloud.google.com/apigee/docs/hybrid/upgrade (as supplied) | — | The seed URL given for this task is unversioned and is a stub. Superseded by `/hybrid/latest/upgrade`. |
| https://docs.apigee.com/private-cloud/port-requirements | 404 | Version segment is mandatory on the OPDK host. |
| https://docs.apigee.com/private-cloud/v4.54.00/ | 404 | No such release. v4.53.01 is latest. |
| https://docs.apigee.com/private-cloud/v4.53.00/install-prerequisites | 404 | Page is named `installation-requirements`. |
| https://docs.apigee.com/private-cloud/v4.53.00/nonexistent-page-xyz | 404 | Control test — confirms real 404s do occur on this host. |
| https://docs.apigee.com/api-platform/fundamentals/environments-overview | 404 | Environment groups page does not exist for Edge. |
| https://docs.apigee.com/api-platform/fundamentals/environment-groups | 404 | ditto |
| https://docs.apigee.com/api-platform/deploy/understanding-environment-groups | 404 | ditto |
| https://docs.apigee.com/api-platform/reference/environment-groups | 404 | ditto |
| https://docs.apigee.com/api-platform/get-started/environment-groups | 404 | ditto |
| https://cloud.google.com/apigee/docs/api-platform/reference/apis/apigee/rest/v1/organizations.instances | 404 | Wrong tree. Correct tree is `/apigee/docs/reference/apis/apigee/rest/v1/...` (no `api-platform`). |
| https://cloud.google.com/apigee/docs/api-platform/reference/apis/apigee/rest/v1/organizations.instances.attachments | 404 | ditto |
| https://cloud.google.com/apigee/docs/api-platform/reference/apis/apigee/rest/v1/organizations.instances.attachments/list | 404 | ditto (correct URL returns 200) |

**Transient anomaly, not reproducible (observed):** an early `curl` of `https://docs.apigee.com/private-cloud/v4.53.00/port-requirements` reported a redirect to the version root. Two subsequent checks (`curl -sIL` and `curl -sL`) both returned a clean **200** with no redirect. Treat the 200 as authoritative; the earlier reading was not reproducible.

---

## 6. RESEARCH-HARNESS FINDINGS (relevant to the rest of the project)

1. **pandoc 3.8 silently truncates large devsite pages.** Running it on the full ~840 KB HTML of `compare-apigee-products` exits 0 and emits only ~4 KB, dropping everything after the first table header. The old `fetch.sh` therefore produced a **1,679-byte** extraction of a page whose real content is ~11 KB — it looked like the page simply had no table. Any citation built on that file would have been wrong. `fetch.sh` now trims to `<div class="devsite-article-body">` before conversion (18 KB input → 11 KB correct output).
2. **devsite serves HTTP 200 for nonexistent versioned pages.** The body text "The equivalent page does not exist in the selected hybrid version" is a reliable stub marker; `fetch.sh` detects it and prints `200-STUB` and exits non-zero. Status codes alone are not sufficient evidence that a page exists.
3. **Some pages put the H1 outside `devsite-article-body`.** The awk H1-trim then produced an empty file. `fetch.sh` falls back to the full converted body when the trimmed result is empty.
4. The pre-existing `api-platform_reference_policies_quota-policy.txt` was fetched with the buggy script and was almost certainly truncated; it has been re-fetched (now 84 KB). Other pages fetched before this fix may need re-fetching — worth a sweep.

## 7. GAPS — explicitly not verified

- Full per-component OPDK log path list. Only the Router nginx access-log path and a reference to `edge-message-processor system.log` were seen.
- `nodetool` behaviour and its exact role in OPDK troubleshooting — no fetched page confirmed it in this round. Do not assert it from this file.
- X-side "log locations": N/A by design but no positive source collected.
- Edge KVM capability parity vs X (can Edge view/edit KVM entries in the UI?) — unverified.
- Edge target-server and TLS-certificate workflows — pages exist (200) but were not read in depth.
- Environment groups in Edge: the evidence is documentation-level absence (404s, nav). No page was found that says "environment groups are not supported in Edge for Private Cloud" in so many words. Do not upgrade this claim beyond "strongly supported" without a positive source.
- OPDK release/support status beyond 4.53.01, and whether the EOL pop-up implies 4.53.x is itself EOL.
