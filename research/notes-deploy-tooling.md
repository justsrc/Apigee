# Deployment, revisions, CI/CD, Management API, and CLI tooling

Scope: deployment lifecycle, revisions, the Management API, gcloud, proxy import/export,
bundle structure, validation tooling, YAML vs XML, products/developers/apps/credentials,
environment groups and instances.

Every URL in section 1 was fetched through `fetch.sh` / `fetch-url.sh` and its HTTP status
and extracted byte count are recorded. Nothing in this file is cited from memory.

---

## 1. VERIFIED PAGES

Status and bytes are the recorded output of the fetch scripts. `200-STUB` means devsite
returned HTTP 200 but served a "page does not exist" placeholder; that is treated as not found.

### gcloud CLI reference (prefix `https://cloud.google.com/sdk/gcloud/reference/apigee`)

| Title | URL | HTTP status | bytes |
| ------- | ----- | ------------- | ------- |
| gcloud apigee | /apigee | 200 | 2488 |
| gcloud apigee apis | /apis | 200 | 2775 |
| gcloud apigee apis deploy | /apis/deploy | 200 | 6327 |
| gcloud apigee apis describe | /apis/describe | 200 | 4117 |
| gcloud apigee apis import | /apis/import | 200 | 9248 |
| gcloud apigee apis list | /apis/list | 200 | 5026 |
| gcloud apigee apis undeploy | /apis/undeploy | 200 | 4768 |
| gcloud apigee applications | /applications | 200 | 1828 |
| gcloud apigee applications describe | /applications/describe | 200 | 3780 |
| gcloud apigee applications list | /applications/list | 200 | 5855 |
| gcloud apigee deployments | /deployments | 200 | 2073 |
| gcloud apigee deployments describe | /deployments/describe | 200 | 5234 |
| gcloud apigee deployments list | /deployments/list | 200 | 7809 |
| gcloud apigee developers | /developers | 200 | 1955 |
| gcloud apigee developers describe | /developers/describe | 200 | 3709 |
| gcloud apigee developers list | /developers/list | 200 | 4940 |
| gcloud apigee environments | /environments | 200 | 1506 |
| gcloud apigee environments list | /environments/list | 200 | 4931 |
| gcloud apigee organizations | /organizations | 200 | 1938 |
| gcloud apigee organizations list | /organizations/list | 200 | 4674 |
| gcloud apigee products | /products | 200 | 3432 |
| gcloud apigee products create | /products/create | 200 | 13574 |
| gcloud apigee products delete | /products/delete | 200 | 3517 |
| gcloud apigee products describe | /products/describe | 200 | 3713 |
| gcloud apigee products list | /products/list | 200 | 4884 |
| gcloud apigee products update | /products/update | 200 | 15399 |

All of the above share the prefix `https://cloud.google.com/sdk/gcloud/reference`.

### alpha / beta variants

| Title | URL | HTTP status | bytes |
| ------- | ----- | ------------- | ------- |
| gcloud alpha apigee | <https://cloud.google.com/sdk/gcloud/reference/alpha/apigee> | 200 | 3166 |
| gcloud alpha apigee apis | .../alpha/apigee/apis | 200 | 3281 |
| gcloud alpha apigee deployments describe | .../alpha/apigee/deployments/describe | 200 | 5522 |
| gcloud beta apigee | .../beta/apigee | 200 | 2967 |
| gcloud beta apigee apis | .../beta/apigee/apis | 200 | 3086 |
| gcloud beta apigee archives | .../beta/apigee/archives | 200 | 2641 |
| gcloud beta apigee environments | .../beta/apigee/environments | 200 | 1768 |
| gcloud beta apigee environments describe | .../beta/apigee/environments/describe | 200 | 3677 |
| gcloud beta apigee operations | .../beta/apigee/operations | 200 | 1288 |

### Apigee documentation (prefix `https://cloud.google.com/apigee/docs`)

| Title | URL (after prefix) | HTTP status | bytes |
| ------- | -------------------- | ------------- | ------- |
| Getting started using gcloud with Apigee | api-platform/get-started/gcloud-get-started | 200 | 5117 |
| Deployment overview | api-platform/deploy/ui-deploy-overview | 200 | 14351 |
| Deploying an API proxy (UI/API/gcloud) | api-platform/deploy/ui-deploy-new | 200 | 13243 |
| Undeploying an API proxy | api-platform/deploy/ui-undeploy | 200 | 4929 |
| Deploying and managing archives in an environment | api-platform/deploy/manage-archive-deployments | 200 | 28497 |
| About environments and environment groups | api-platform/fundamentals/environments-overview | 200 | 22460 |
| Working with environments | api-platform/fundamentals/environments-working-with | 200 | 14118 |
| Working with environment groups | api-platform/fundamentals/environmentgroups-working-with | 200 | 16344 |
| Configuring a proxy with YAML | api-platform/fundamentals/configure-proxy-with-yaml | 200 | 6771 |
| Create an API proxy from a YAML template | api-platform/fundamentals/configure-proxy-with-yaml-example | 200 | 20243 |
| Downloading and uploading a proxy bundle | api-platform/fundamentals/download-api-proxies | 200 | 5891 |
| API development lifecycle | api-platform/fundamentals/api-development-lifecycle | 200 | 8408 |
| Understanding APIs and API proxies | api-platform/fundamentals/understanding-apis-and-api-proxies | 200 | 6662 |
| Basic characteristics of API proxies | api-platform/fundamentals/structure-api-proxies | 200 | 5192 |
| API proxy configuration reference | api-platform/reference/api-proxy-configuration-reference | 200 | 69358 |
| API proxy YAML configuration reference | api-platform/reference/api-proxy-yaml-configuration-reference | 200 | 13263 |
| Instances | api-platform/system-administration/instances | 200 | 18305 |
| Creating an API product | api-platform/publish/create-api-products | 200 | 33638 |
| Creating an API proxy | api-platform/get-started/create-proxy | 200 | 4120 |
| Deploying an API proxy (get started) | api-platform/get-started/deploy-proxy | 200 | 2941 |
| Testing an API proxy | api-platform/get-started/test-proxy | 200 | 5126 |
| Local development overview | api-platform/local-development/overview | 200 | 2943 |
| Cloud Code Apigee command reference | api-platform/local-development/vscode/command-reference | 200 | 3105 |
| Manage the Apigee Emulator | api-platform/local-development/vscode/manage-apigee-emulator | 200 | 16674 |

### Management API reference (prefix `https://cloud.google.com/apigee/docs`)

| Title | URL (after prefix) | HTTP status | bytes |
| ------- | -------------------- | ------------- | ------- |
| Apigee API REST reference index | reference/apis/apigee/rest | 200 | 186374 |
| Method: ...revisions.deployments.deploy | reference/apis/apigee/rest/v1/organizations.environments.apis.revisions.deployments/deploy | 200 | 6290 |
| Method: ...revisions.deployments.undeploy | .../organizations.environments.apis.revisions.deployments/undeploy | 200 | 4149 |
| Method: ...revisions.deployments.get | .../organizations.environments.apis.revisions.deployments/get | 200 | 2925 |
| Method: ...deployments.generateDeployChangeReport | .../organizations.environments.apis.revisions.deployments/generateDeployChangeReport | 200 | 4140 |
| Method: organizations.apis.revisions.deployments.list | .../organizations.apis.revisions.deployments/list | 200 | 2851 |
| Method: organizations.apis.revisions.list | .../organizations.apis.revisions/list | 200 | 2458 |
| Method: organizations.apis.create | .../organizations.apis/create | 200 | 5782 |
| Method: organizations.apis.revisions.updateApiProxyRevision | .../organizations.apis.revisions/updateApiProxyRevision | 200 | 3960 |
| Method: organizations.apiproducts.create | .../organizations.apiproducts/create | 200 | 4151 |
| Method: organizations.developers.create | .../organizations.developers/create | 200 | 2895 |
| Method: organizations.developers.apps.create | .../organizations.developers.apps/create | 200 | 2980 |
| Resource: DeveloperAppKey | .../organizations.developers.apps.keys.create | 200 | 6076 |
| Method: ...keys.create.create | .../organizations.developers.apps.keys.create/create | 200 | 3952 |
| Method: organizations.apps.list | .../organizations.apps/list | 200 | 8906 |
| Method: organizations.envgroups.create | .../organizations.envgroups/create | 200 | 3224 |
| Method: organizations.envgroups.attachments.create | .../organizations.envgroups.attachments/create | 200 | 2717 |
| Method: organizations.instances.list | .../organizations.instances/list | 200 | 5062 |
| Method: organizations.instances.attachments.create | .../organizations.instances.attachments/create | 200 | 2436 |

All `...` above mean `https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/`.

---

## 2. CONFIRMED COMMANDS AND FLAGS

Everything in this section was read off a fetched page. If a flag is not listed here, I did
not see it and am not claiming it exists.

### 2.1 The `apigee` command group, as actually listed

From `https://cloud.google.com/sdk/gcloud/reference/apigee` — `GROUP` is one of exactly seven:

    apis          Manage Apigee API proxies.
    applications  Manage third-party applications which call Apigee API proxies.
    deployments   Manage deployments of Apigee API proxies in runtime environments.
    developers    Manage Apigee developers.
    environments  Manage Apigee environments.
    organizations Manage Apigee organizations.
    products      Manage Apigee API products.

There is **no `gcloud apigee keys` group** in GA. There is no `gcloud apigee revisions` group.
Not documented — do not invent either.

### 2.2 Subcommands, discovered from each group's own link tree

| Command | Source URL |
| --------- | ----------- |
| `gcloud apigee apis deploy` | /sdk/gcloud/reference/apigee/apis/deploy |
| `gcloud apigee apis describe` | /sdk/gcloud/reference/apigee/apis/describe |
| `gcloud apigee apis import` | /sdk/gcloud/reference/apigee/apis/import |
| `gcloud apigee apis list` | /sdk/gcloud/reference/apigee/apis/list |
| `gcloud apigee apis undeploy` | /sdk/gcloud/reference/apigee/apis/undeploy |
| `gcloud apigee applications describe` | /sdk/gcloud/reference/apigee/applications/describe |
| `gcloud apigee applications list` | /sdk/gcloud/reference/apigee/applications/list |
| `gcloud apigee deployments describe` | /sdk/gcloud/reference/apigee/deployments/describe |
| `gcloud apigee deployments list` | /sdk/gcloud/reference/apigee/deployments/list |
| `gcloud apigee developers describe` | /sdk/gcloud/reference/apigee/developers/describe |
| `gcloud apigee developers list` | /sdk/gcloud/reference/apigee/developers/list |
| `gcloud apigee environments list` | /sdk/gcloud/reference/apigee/environments/list |
| `gcloud apigee organizations list` | /sdk/gcloud/reference/apigee/organizations/list |
| `gcloud apigee products create` | /sdk/gcloud/reference/apigee/products/create |
| `gcloud apigee products delete` | /sdk/gcloud/reference/apigee/products/delete |
| `gcloud apigee products describe` | /sdk/gcloud/reference/apigee/products/describe |
| `gcloud apigee products list` | /sdk/gcloud/reference/apigee/products/list |
| `gcloud apigee products update` | /sdk/gcloud/reference/apigee/products/update |

Asymmetry worth knowing: **only `products` has `create`/`update`/`delete`.** `developers`,
`applications`, `environments`, `organizations` and `apis` are read-and-deploy only in GA
(`apis` gains `import`). Developer/app/key lifecycle in GA has **no create or delete
subcommand** — that work is done through the Management API or the UI. This is a real gap and
an easy place to invent a `gcloud apigee developers create` that does not exist in GA.

**GA vs alpha/beta extras** (verified on the alpha/beta index pages):
`gcloud beta apigee apis delete` exists (and `alpha`), but **not in GA**.
beta/alpha groups add `archives` (delete, deploy, describe, list, update) and `operations`
(describe, list). beta/alpha `environments` adds `describe` (flag `--organization`).

### 2.3 `gcloud apigee apis deploy` — the deploy command

Source: `https://cloud.google.com/sdk/gcloud/reference/apigee/apis/deploy`

Synopsis, verbatim from the page:

    gcloud apigee apis deploy [[REVISION] --api=API --environment=ENVIRONMENT
        --organization=ORGANIZATION] [--override]

* `REVISION` — optional positional. A positive revision number, or the special value `latest`.
  Default is `latest` when unspecified.
* `--api=API` — API proxy to be deployed.
* `--environment=ENVIRONMENT` — environment to deploy into.
* `--organization=ORGANIZATION` — org of proxy and environment; defaults to the Cloud Platform
  project's associated organization.
* `--override` — "Force the deployment of the new revision, overriding any currently deployed
  revision that would conflict with it." Page states: with `--override` the existing revision
  **remains deployed until the new revision is fully deployed** (zero downtime). Without it,
  the command **fails** unless conflicting proxies are un-deployed first.

Verbatim examples on that page:

    gcloud apigee apis deploy --environment=test --api=demo
    gcloud apigee apis deploy 3 --organization=my-org --environment=test --api=demo --override
    gcloud apigee apis deploy 3 --organization=my-org --environment=test --api=demo --format=json

Note there is **no `--service-account` flag** on the GA `gcloud apigee apis deploy` page,
even though the underlying Management API deploy call accepts a `serviceAccount` query
parameter and the UI offers an optional service account. If a case involves running a proxy as
a service account, the CLI path is not documented on the GA page. Unverified whether a
beta/alpha variant adds the flag; I did not fetch the beta `apis/deploy` page.

### 2.4 `gcloud apigee apis undeploy`

Source: `https://cloud.google.com/sdk/gcloud/reference/apigee/apis/undeploy`

    gcloud apigee apis undeploy [[REVISION] --api=API --environment=ENVIRONMENT
        --organization=ORGANIZATION]

No `--override` flag on this command. Examples on the page:

    gcloud apigee apis undeploy --environment=test --api=my-api
    gcloud apigee apis undeploy 3 --organization=test-org --environment=test --api=my-api

### 2.5 `gcloud apigee apis import` — import, and the YAML entry point

Source: `https://cloud.google.com/sdk/gcloud/reference/apigee/apis/import`

    gcloud apigee apis import (API : --organization=ORGANIZATION)
        (--from-bundle=BUNDLE_PATH | --from-template=TEMPLATE_PATH)

* Exactly one of `--from-bundle` / `--from-template` is required.
* `--from-bundle` — "The ZIP file must contain the API proxy configuration under an
  `apiproxy/` directory."
* `--from-template` — Apigee Feature Template YAML. Compiled locally into a bundle before
  upload. Referenced feature files must sit in the same directory as the template.
* `API` positional is required (can be an FQN such as `organizations/my-org/apis/helloworld`).

Verbatim examples:

    gcloud apigee apis import helloworld --from-bundle=./helloworld.zip
    gcloud apigee apis import helloworld --from-template=./helloworld.yaml
    gcloud apigee apis import helloworld --organization=my-org --from-template=./helloworld.yaml
    gcloud apigee apis import organizations/my-org/apis/helloworld --from-bundle=./helloworld.zip

Page states import **never overwrites**: "If an API proxy with the given name already exists,
a new revision is created; otherwise, a new API proxy is created." And under "After importing":
"Each import creates a new API proxy revision rather than overwriting an existing one. Deploy
the new revision to an environment with `gcloud apigee apis deploy`."

Prerequisites section names the permission role `roles/apigee.apiAdmin`.

**There is no `gcloud apigee apis export`.** Export is not a gcloud command in GA; it is the
UI action "More revision actions > Export revision n" plus the API `organizations.apis.revisions/get`.

### 2.6 `gcloud apigee apis describe`

Source: `https://cloud.google.com/sdk/gcloud/reference/apigee/apis/describe`

    gcloud apigee apis describe (API : --organization=ORGANIZATION) [--verbose]

`--verbose` — "Include proxy revision info in the description."

### 2.7 `gcloud apigee deployments describe` / `list`

Sources: `/sdk/gcloud/reference/apigee/deployments/describe` and `.../deployments/list`

    gcloud apigee deployments describe [[REVISION] --api=API --environment=ENVIRONMENT
        --organization=ORGANIZATION]

    gcloud apigee deployments list [--api=API --environment=ENVIRONMENT
        --organization=ORGANIZATION --revision=REVISION] [--filter=EXPRESSION] [--limit=LIMIT]
        [--page-size=PAGE_SIZE] [--sort-by=[FIELD,...]] [--uri]

`deployments describe` supports a `--revision` attribute (listed in the group attribute table on
the list page). `deployments list` description: "lists deployments of API proxies, optionally
filtered by environment, proxy name, proxy revision, or a combination of these."

### 2.8 `gcloud apigee products create` / `update` — the API product surface

Source: `https://cloud.google.com/sdk/gcloud/reference/apigee/products/create`

    gcloud apigee products create [INTERNAL_NAME : --organization=ORGANIZATION]
        [--attributes=[NAME=VALUE,...]] [--description=DESCRIPTION]
        [--display-name=DISPLAY_NAME] [--manual-approval] [--oauth-scopes=[SCOPE,...]]
        [--all-environments | --environments=ENVIRONMENT,[ENVIRONMENT,...]]
        [--all-proxies | --apis=[API,...] --resources=RESOURCE#[RESOURCE...]]
        [--internal-access | --private-access | --public-access]
        [--quota=QUOTA --quota-interval=QUOTA_INTERVAL --quota-unit=QUOTA_UNIT]

Source: `https://cloud.google.com/sdk/gcloud/reference/apigee/products/update`

    gcloud apigee products update (PRODUCT : --organization=ORGANIZATION)
        [--display-name=SET_DISPLAYNAME]
        [--all-apis | --add-api=[API,...] --remove-api=[API,...]]
        [--all-environments | --add-environment=[ENVIRONMENT,...]
         --remove-environment=[ENVIRONMENT,...]]
        [--all-resources | --add-resource=RESOURCE#... --remove-resource=RESOURCE#...]
        [--automatic-approval | --manual-approval]
        [--clear-attributes | --add-attribute=[NAME=VALUE,...] --remove-attribute=[NAME,...]]
        [--clear-description | --description=SET_DESCRIPTION]
        [--clear-oauth-scopes | --add-oauth-scope=[OAUTH-SCOPE,...]
         --remove-oauth-scope=[OAUTH-SCOPE,...]]
        [--clear-quota | --quota=QUOTA --quota-interval=QUOTA_INTERVAL --quota-unit=QUOTA_UNIT]
        [--internal-access | --private-access | --public-access]

Note the three-way `--internal-access | --private-access | --public-access` choice: the product
access level is mutually exclusive, matching the UI "Access" field.

### 2.9 Common list flags

Every GA `list` command I fetched (`apis`, `applications`, `deployments`, `developers`,
`environments`, `organizations`, `products`) carries the same set: `--filter`, `--limit`,
`--page-size`, `--sort-by`, `--uri`, and most carry `--organization`. `applications list` adds
`--developer`.

### 2.10 Commands quoted in prose docs that are NOT on the GA reference pages

Flagged deliberately, because the docs and the GA reference disagree:

* `https://cloud.google.com/apigee/docs/api-platform/deploy/ui-deploy-overview` shows
  `gcloud alpha apigee deployments describe --api=$API --environment=$ENV` and links to
  `/sdk/gcloud/reference/alpha/apigee/deployments/describe` (verified 200). The GA
  `gcloud apigee deployments describe` also exists and is the stable form.
* `https://cloud.google.com/apigee/docs/api-platform/get-started/gcloud-get-started` uses
  `gcloud components install beta` to reach `gcloud beta apigee`, and says beta is what
  deploys and manages archives.
* `https://cloud.google.com/apigee/docs/api-platform/deploy/ui-deploy-new` shows
  `gcloud apigee apis deploy $REV --api=$API --environment=$ENV`.
* `https://cloud.google.com/apigee/docs/api-platform/fundamentals/configure-proxy-with-yaml`
  diagrams `gcloud apigee apis import --from-template` then `gcloud apigee apis deploy`.

### 2.11 gcloud-wide flags (listed on the apis/deploy page, apply to all)

`--access-token-file`, `--account`, `--billing-project`, `--configuration`, `--flags-file`,
`--flatten`, `--format`, `--help`, `--impersonate-service-account`, `--log-http`, `--project`,
`--quiet`, `--trace-token`, `--user-output-enabled`, `--verbosity`.

### 2.12 VS Code / Cloud Code commands (not gcloud)

Source: `https://cloud.google.com/apigee/docs/api-platform/local-development/vscode/command-reference`

Cloud Code Command Palette entries: `Cloud Code: Create Apigee environment`,
`Cloud Code: Create Apigee proxy bundle`, `Cloud Code: Create Apigee shared flow bundle`,
`Cloud Code: Create Apigee test bundle`, `Cloud Code: Create Apigee workspace`,
`Cloud Code - Apigee: Focus on Emulators View`, `Cloud Code: Import Apigee proxy bundle`,
`Cloud Code: Import Apigee shared flow bundle`, `Cloud Code: Open Apigee workspace`,
`Cloud Code: Refresh Apigee Emulator view`, `Cloud Code: Refresh Apigee workspace view`,
`View: Show Cloud Code - Apigee`.

---

## 3. MANAGEMENT API PATHS

Base: `https://apigee.googleapis.com/v1/`. All templated HTTP requests below are verbatim from
the fetched method pages, which note "The URL uses gRPC Transcoding syntax." OAuth scope on
all of these: `https://www.googleapis.com/auth/cloud-platform`.

### 3.1 The deploy endpoint (the one the task named)

Source: `https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.environments.apis.revisions.deployments/deploy`

    POST https://apigee.googleapis.com/v1/{name=organizations/*/environments/*/apis/*/revisions/*}/deployments

* Method id: `organizations.environments.apis.revisions.deployments.deploy`
  (gRPC `google.cloud.apigee.v1.DeploymentService.DeployApiProxy`)
* Path parameter `name`, required, format `organizations/{org}/environments/{env}/apis/{api}/revisions/{rev}`
* **Request body must be empty.** Verbatim: "The request body must be empty."
* Query parameters:
  * `override` (boolean) — "Set `override` to `true` to replace other deployed revisions. By
    default, `override` is `false` and the deployment is rejected if other revisions of the
    API proxy are deployed in the environment."
  * `sequencedRollout` (boolean) — rolls routing changes out in a safe order; only needed when
    a deployment captures traffic from another environment under a shared environment group,
    or when a base path removal reroutes traffic.
  * `serviceAccount` (string) — format `{ACCOUNT_ID}@{PROJECT}.iam.gserviceaccount.com`;
    requires `iam.serviceAccounts.actAs`.
* Response body: a `Deployment` resource.
* IAM permissions required, verbatim from the page:
  * `apigee.deployments.create` on `organizations/{org}/environments/{env}`
  * `apigee.proxyrevisions.deploy` on `organizations/{org}/apis/{api}/revisions/{rev}`

### 3.2 Deployment read/undeploy/report

| Method | HTTP request | Source |
| -------- | -------------- | -------- |
| undeploy | `DELETE https://apigee.googleapis.com/v1/{name=organizations/*/environments/*/apis/*/revisions/*}/deployments` | .../revisions.deployments/undeploy |
| get | `GET https://apigee.googleapis.com/v1/{name=organizations/*/environments/*/apis/*/revisions/*}/deployments` | .../revisions.deployments/get |
| generateDeployChangeReport | `POST https://apigee.googleapis.com/v1/{name=organizations/*/environments/*/apis/*/revisions/*}/deployments:generateDeployChangeReport` | .../revisions.deployments/generateDeployChangeReport |
| list revisions of an API | `GET https://apigee.googleapis.com/v1/{parent=organizations/*/apis/*}/revisions` | organizations.apis.revisions/list |
| list deployments of a revision (all envs) | `GET https://apigee.googleapis.com/v1/{parent=organizations/*/apis/*/revisions/*}/deployments` | organizations.apis.revisions.deployments/list |

Note the colon form `.../deployments:generateDeployChangeReport` — this is a custom verb on the
same resource path, not a subpath. Listing deployments for an *environment* has no dedicated
method; the docs use `GET /v1/organizations/$ORG/deployments`
(`organizations.environments.deployments/list`). The curl for that call is on the fetched
`ui-deploy-new` page; I did not fetch the `organizations.environments.deployments/list` method
page itself, so treat the method name as index-confirmed only.

### 3.3 Import / export / revisions

| Method | HTTP request | Source |
| -------- | -------------- | -------- |
| Create an API proxy **and a new revision** | `POST https://apigee.googleapis.com/v1/{parent=organizations/*}/apis` | organizations.apis/create |
| Update an existing API proxy revision | `POST https://apigee.googleapis.com/v1/{name=organizations/*/apis/*/revisions/*}` | organizations.apis.revisions/updateApiProxyRevision |
| Get (export) a revision bundle | see note | organizations.apis.revisions/get (linked from download-api-proxies) |

`organizations.apis/create` detail, verbatim:

* "Creates an API proxy. The API proxy created will not be accessible at runtime until it is
  deployed to an environment."
* To import a zip bundle: set `name` query param to the proxy name, set `action=import`, set
  `Content-Type: multipart/form-data`, and pass the zip as the `file` form field.
* **Validation:** "To validate the API proxy configuration bundle only without importing it,
  set the `action` query parameter to `validate`." And: "Invalid API proxy configurations are
  rejected, and a list of validation errors is returned to the client."
* Query params: `name` (chars restricted to `A-Za-z0-9._-`), `action` (`import` | `validate`),
  `validate` (boolean, **ignored**, "Maintained for compatibility with Apigee Edge API"), and
  `space` (optional; only respected when creating a new proxy, has no effect on a new revision
  of an existing proxy).
* Request body is an `HttpBody`; response is an `ApiProxyRevision`.
* IAM: `apigee.proxies.create` on `organizations/{org}`.

### 3.4 Products, developers, apps, credentials

The resource collection is **`apiproducts`, not `products`** — `organizations.products/create`
returns 404 (section 5).

| Method | HTTP request | Source |
| -------- | -------------- | -------- |
| Create API product | `POST https://apigee.googleapis.com/v1/{parent=organizations/*}/apiproducts` | organizations.apiproducts/create |
| Create developer | `POST https://apigee.googleapis.com/v1/{parent=organizations/*}/developers` | organizations.developers/create |
| Create developer app | `POST https://apigee.googleapis.com/v1/{parent=organizations/*/developers/*}/apps` | organizations.developers.apps/create |
| Create consumer key/secret | `POST https://apigee.googleapis.com/v1/{parent=organizations/*/developers/*/apps/*}/keys/create` | organizations.developers.apps.keys.create/create |
| List apps | `GET https://apigee.googleapis.com/v1/{parent=organizations/*}/apps` | organizations.apps/list |

`DeveloperAppKey` fields (from the resource page `organizations.developers.apps.keys.create`):
`apiProducts` (array), `attributes[]` (Attribute), `consumerKey`, `consumerSecret`, `expiresAt`,
`issuedAt`, `scopes[]`, `status` (`approved` | `revoked`), `expiresInSeconds`.

Two important verbatim notes from that page:

* "**Do not specify the list of API products when creating a consumer key and secret for a
  developer app.** Instead, use the `keys.updateDeveloperAppKey` API to make the association
  after the consumer key and secret are created."
* `expiresInSeconds` is input only; `-1` (the default) means the key never expires, and the
  expiration **cannot be updated after it is set**.

The method index also lists (names only, not fetched, so treat as unverified shapes):
`organizations.developers.apps.keys.apiproducts/delete` and
`organizations.developers.apps.keys.apiproducts/updateDeveloperAppKeyApiProduct` — these, not
an `.../add` or `.../remove` (both 404).

### 3.5 Environment groups and instances

| Method | HTTP request | Source |
| -------- | -------------- | -------- |
| Create env group | `POST https://apigee.googleapis.com/v1/{parent=organizations/*}/envgroups` | organizations.envgroups/create |
| Attach env to group | `POST https://apigee.googleapis.com/v1/{parent=organizations/*/envgroups/*}/attachments` | organizations.envgroups.attachments/create |
| List instances | `GET https://apigee.googleapis.com/v1/{parent=organizations/*}/instances` | organizations.instances/list |
| Attach environment to instance | `POST https://apigee.googleapis.com/v1/{parent=organizations/*/instances/*}/attachments` | organizations.instances.attachments/create |

Verbatim curls from the environment groups doc:

    curl -i $TOKEN -X POST \
      https://apigee.googleapis.com/v1/organizations/ORG_NAME/envgroups?name=new-group-name

    curl -H "Authorization: Bearer $TOKEN" -X POST
      "https://apigee.googleapis.com/v1/organizations/my-org/envgroups/test-group/attachments"
      -d '{ "name": "my-attachment", "environment": "test" }'

Env group name rules, verbatim: "you must use only lower case letters, numbers, and hyphens
(`a-z`, `A-Z`, and `-`). You cannot use upper case letters or any special characters other than
hyphens. You must also start the name with a lower case letter." (The doc's own parenthesised
letter ranges contradict its sentence — quoting it rather than silently correcting it.)

### 3.6 Full method-name inventory for the areas in scope

Extracted from the link tree of `https://cloud.google.com/apigee/docs/reference/apis/apigee/rest`
(361 method pages total). Useful for confirming a method exists before citing it:

    organizations.apis                          create delete get list move patch
    organizations.apis.revisions                delete get list updateApiProxyRevision
    organizations.apis.revisions.deployments    list
    organizations.environments.apis.revisions.deployments
                                               deploy undeploy get generateDeployChangeReport
                                               generateUndeployChangeReport
    organizations.environments.deployments      get list getIamPolicy setIamPolicy
                                               testIamPermissions
    organizations.environments.archiveDeployments
                                               create delete get list patch
                                               generateDownloadUrl generateUploadUrl
    organizations.environments.sharedflows.revisions.deployments  deploy undeploy get
    organizations.apiproducts                   create delete get list update move
    organizations.developers                    create delete get list update setDeveloperStatus
    organizations.developers.apps               create delete get list update
    organizations.developers.apps.keys          create delete get replaceDeveloperAppKey
                                               updateDeveloperAppKey
    organizations.developers.apps.keys.apiproducts
                                               delete updateDeveloperAppKeyApiProduct
    organizations.developers.subscriptions      create expire get list
    organizations.developers.balance            adjust credit
    organizations.envgroups                     create delete get list patch
    organizations.envgroups.attachments         create delete get list
    organizations.instances                     create delete get list patch
    organizations.instances.attachments         create delete get list
    organizations.environments                  create delete get list update modifyEnvironment
                                               updateEnvironment
    organizations.environments.keyvaluemaps     create delete get list update
    organizations.environments.targetservers    create delete get list update

---

## 4. DEPLOYMENT LIFECYCLE

Sources: `api-platform/deploy/ui-deploy-overview`, `api-platform/deploy/ui-deploy-new`,
`organizations.apis/create`, `organizations.environments.apis.revisions.deployments/deploy`,
`gcloud apigee/apis/deploy`, `gcloud apigee/apis/import`,
`api-platform/fundamentals/environments-overview`.

### Step 1 — Create a revision (import or create)

A proxy revision comes into being one of two ways. Both always create a **new revision**; there
is no in-place edit path.

* **Management API:** `POST /v1/{parent=organizations/*}/apis` with `name` set. Verbatim: "If
  the API proxy does not exist, it will be created. If the API proxy exists, then a new revision
  is created." Request body is an `HttpBody`; for a zip bundle use `action=import`,
  `Content-Type: multipart/form-data`, and the `file` form field.
* **gcloud:** `gcloud apigee apis import <API> --from-bundle=<zip>` or
  `--from-template=<yaml>`. Verbatim: "Each import creates a new API proxy revision rather than
  overwriting an existing one."

### Step 2 — The revision is not live

Verbatim from `organizations.apis/create`: "The API proxy created will not be accessible at
runtime until it is deployed to an environment." From the deploy method page: "You cannot
invoke an API proxy until it has been deployed to an environment."

### Step 3 — Deploy

* API: `POST /v1/{name=organizations/*/environments/*/apis/*/revisions/*}/deployments`, empty
  body, `override=true` if another revision is already deployed.
* gcloud: `gcloud apigee apis deploy [REVISION] --api=API --environment=ENVIRONMENT
  [--organization=ORG] [--override]`.

Conflict rule, verbatim from `gcloud apigee apis deploy`: "By default, the API proxy's base path
must not already be in use by a deployed proxy in the target environment... If unset,
`gcloud apigee apis deploy` will fail unless all conflicting API proxies are first undeployed."

### Step 4 — Zero-downtime, eventually consistent

Verbatim from the deploy method page: "All successful API proxy deployments to Apigee are
zero-downtime deployments." From the deployment overview, the order is:

1. Revision 1 of `/hello` is deployed and handling traffic.
2. Revision 2 of `/hello` is deployed.
3. Revision 2 is deployed to the Message Processors in the runtime plane.
4. Revision 1 is undeployed.

And verbatim: "If the deployment of Revision 2 *fails* for any reason, the previous version,
Revision 1 is still undeployed. In this case, you can re-deploy the previous revision to
restore it."

Consistency model, verbatim: "In Apigee, MPs act independently of one another and any given MP
can be in a different state than the other MPs (such as active or disabled). This is known as
an *eventually consistent* deployment model for API proxies."

Deployment is **not instant**: "It takes time for the API proxy to be synchronized across all
MPs in the runtime plane." Hence a separate status step.

### Step 5 — Confirm it is live

* `GET /v1/organizations/$ORG/environments/$ENV/apis/$API/revisions/$REV/deployments` returns a
  `Deployment` with a `pods[]` array and a top-level `"state": "READY"`.
* `gcloud apigee deployments describe --api=... --environment=...`
* UI status icons, verbatim from the overview: gray dot = not deployed to the environment;
  green = no errors or warnings; **yellow triangle = "some routing did not update due to base
  path conflicts"**; red box = "there was an error deploying the API proxy."

The yellow-triangle state is the single most useful diagnostic for a base-path collision, and
it is a *partial success*, not a failure.

### Step 6 — Undeploy

`DELETE` on the same resource path, or `gcloud apigee apis undeploy`.

### Revisions are immutable

Verbatim, stated on three separate pages: "After you deploy an API proxy, the revision is
read-only. You cannot change an API proxy revision...; the only way to *change* a revision is to
create a new revision and deploy it." Also: "You cannot make incremental changes to an API
proxy revision and redeploy that same revision to Apigee." And: "MPs can deploy a proxy bundle
only in its entirety."

Practical consequence for a support case: a user reporting "my edit didn't take" has almost
certainly edited a deployed revision rather than creating a new one.

### Environments

Verbatim from `environments-overview`: "An Apigee *environment* is a software environment,
within an organization, for creating and deploying API proxies. You must deploy an API proxy to
an environment before it can be accessed."

Deployment types in an environment (verbatim table):

| Type | Description |
| --- | --- |
| Proxy | Develop and test API proxies in development environments, then deploy to integration test and production. |
| Archive | Develop and test programmable API proxies using Apigee in VS Code. |

Archive deployment enables local development. Enabling it **locks out a set of actions**;
attempts fail with `FAILED_PRECONDITION`. Verbatim list: cannot view/confirm/manage Archive
deployments in the UI or use the Debug UI; cannot create, update, or delete resource files or
target servers via UI, API, or gcloud; Google Authentication using Service Accounts is not
supported. KVMs and TLS keystores remain manageable.

Billing unit, verbatim: "A **proxy deployment unit** is defined as one API proxy or shared flow
revision deployment, per environment, per instance (region)." So one proxy deployed to one
environment spanning two instances counts as two PDUs.

Environment types (PAYG): Base, Intermediate, Comprehensive. Subscription plans are always
Comprehensive.

### Environment groups

Verbatim from `environments-overview`: "An *environment group* (sometimes called an *envgroup*
in the Apigee API) is the basic mechanism for defining the way requests are routed to individual
environments. You define hostnames on your environment groups (not on individual environments)."
And, critically: "An environment must be a member of at least one environment group before you
can access proxies deployed within it."

That last sentence is the answer to a very common support question: a proxy deployed
successfully and reporting READY still 404s at the URL, because the environment was never
attached to an env group, so no hostname routes to it.

### Multi-environment-group hazard

Verbatim from `ui-deploy-new`: "Deploying a proxy in more than one environment in the same
environment group may lead to undefined behavior." The mitigation is the
`generateDeployChangeReport` call, which "warns you if a base path in the proxy you want to
deploy will not receive traffic due to an existing deployment that is already using that base
path." The `sequencedRollout` query parameter on deploy exists for this class of problem.

### Hybrid differences, verbatim

* Environment groups: "**Apigee hybrid users:** Every environment group you create with an
  attached environment must be included in all override files where the environment is used."
* Instances: "You can view hybrid instances in the UI, but they are read-only. To create or
  manage hybrid instances, you must use the `helm` command-line tool."
* Deployment validation: "Apigee hybrid validates the dependencies between shared flows and API
  proxies at deployment time. For example, if the Flow Callout policy in an API proxy references
  a shared flow that either doesn't exist or isn't deployed, the API proxy deployment fails."
  (From the deploy method page.) This is a hybrid-specific **deployment error** mode that does
  not exist on Apigee X.
* Deployment usage: "If your organization is Apigee hybrid-enabled, only a sub-set of these usage
  metrics are displayed."

So: **environment groups and instances both exist for hybrid**, and the envgroups page carries
the "applies to Apigee and Apigee hybrid" banner. They are not X-only. The honest nuance is that
for instances, hybrid rows are read-only in the UI and managed with `helm`.

### Bundle structure

From `api-platform/reference/api-proxy-configuration-reference`:

The zip's top-level directory **must be `/apiproxy`**. Verbatim from `download-api-proxies`:
"The top-level directory in the zip file must be `/apiproxy`." Directly under `apiproxy` sit
`policies/`, `proxies/`, `resources/`, `targets/`, and the base config XML
(the example uses `weatherapi.xml`). The page's contents table:

| Component | Meaning |
| ----------- | --------- |
| Base configuration | Primary configuration settings; e.g. `/apiproxy/weatherapi.xml`. Name must be unique within the organization. |
| ProxyEndpoint | Inbound HTTP connection, request/response flows, policy attachments (`/proxies`). |
| TargetEndpoint | Outbound HTTP connection to the backend, request/response flows, policy attachments (`/targets`). |
| Flows | ProxyEndpoint and TargetEndpoint request/response pipelines. |
| Policies | XML files conforming to the Apigee policy schemas (`/policies`). |
| Resources | Scripts, JAR files, XSLT referenced by policies (`/resources`). |

Round trip (verbatim shell from `download-api-proxies`):

    mkdir myappdir
    unzip ./my-app_app_rev3_2019_04_20.zip -d myappdir
    zip my-new-proxy.zip -r .

"There are no special requirements for the zip file name. For example, you do not need to
increment the revision number or specify the date in the file name."

Export is "More revision actions > Export revision n" in the UI, or the API
`organizations.apis.revisions/get`. Import of the zip back is the UI action
"More revision actions > Import revision", or the API `organizations.apis.revisions/updateApiProxyRevision`
("Update an existing API proxy revision").

### Validation tooling

I probed for a dedicated proxy linter and **could not find one**. These all returned 404:
`api-platform/reference/api-proxy-linter`, `api-platform/test/api-proxy-linter`,
`api-platform/get-started/api-proxy-linter`, `api-platform/develop/maven-plugin`. None appears
anywhere in the 426-entry api-platform navigation tree I extracted.

What validation *does* exist, all **documented**:

1. **Server-side at upload.** `organizations.apis/create` with `action=validate` validates a
   bundle without importing it. And on every import: "Invalid API proxy configurations are
   rejected, and a list of validation errors is returned to the client." The `validate` boolean
   query param is explicitly a no-op kept for Edge compatibility — all uploads validate anyway.
2. **YAML schema is strict.** Verbatim from `api-proxy-yaml-configuration-reference`: "The
   schema is strict. Unknown fields cause an error when you import the file." Only `gateway:
   apigee` and `schemaVersion: 1.0.0` are supported.
3. **Deployment-time dependency checking on hybrid only** (see above).
4. **The Apigee Emulator** for local test execution, driven from VS Code / Cloud Code
   (`api-platform/local-development/vscode/manage-apigee-emulator`).

If a case asks "how do I lint my proxy in CI", the honest documented answer is the Emulator plus
`action=validate`; do not assert that a Google-provided linter exists.

### YAML (Apigee Feature Templates) vs classic XML bundle

Two real doc URLs, both verified:

* Conceptual: `https://cloud.google.com/apigee/docs/api-platform/fundamentals/configure-proxy-with-yaml`
* Walkthrough: `.../fundamentals/configure-proxy-with-yaml-example`
* Field reference: `https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-yaml-configuration-reference`

Classic XML bundle: `https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference`
(zip of XML under `apiproxy/`, imported with `--from-bundle`).

What YAML is, verbatim: "You can define an Apigee API proxy in YAML and deploy it with the
Google Cloud CLI, as an alternative to authoring the traditional XML proxy bundle. You describe
a proxy's endpoints, routes, policies, and backend targets in YAML files called *Apigee Feature
Templates*, and Apigee compiles them into a standard API proxy bundle for you."

Because it compiles to a normal bundle: "the result is an ordinary Apigee API proxy bundle, a
proxy that you build this way runs on the same Apigee runtime, with the same policies and
behavior as a proxy that you build in the Apigee UI or from an XML bundle."

Three document types by `type` field:

| Document type | `type` | Purpose |
| ---- | ---- | ---- |
| Template | `template` | The entry point that you deploy. Composes features; defines endpoints and routes. |
| Feature | `feature` | Reusable unit of configuration; holds the policies and resources. |
| Proxy | `proxy` | Fully resolved proxy the CLI produces; can also be imported directly. |

Minimal template verbatim:

    gateway: apigee
    schemaVersion: 1.0.0
    name: HelloWorld-v1
    type: template
    description: API proxy for HelloWorld-v1
    features:
    - proxy-apigeemock.yaml
    - response-helloworld.yaml

**The conversion story is one-directional.** Verbatim: the CLI (1) compiles template + features
into one proxy definition, (2) converts it to a standard bundle, (3) uploads it, "which creates
a new API proxy *revision*". And under Limitations: "**Troubleshooting uses the generated XML.**
The Apigee UI and runtime work with the generated bundle. There is no round-trip back to your
YAML source in the UI." Also, earlier on the same page: "When you troubleshoot a proxy in the
Apigee UI, you still see the generated XML configuration, not the YAML source."

So: YAML is a **source format** that compiles down to the XML bundle. There is no XML-to-YAML
converter documented. XML is still the canonical runtime format and still what you see in the UI.

Documented YAML limitations (verbatim, all real constraints that will generate support cases):

* "**Features are local files.** A template can only reference feature files that are in the same
  directory. Referencing features by URL or from a shared catalog is not supported."
* "**Parameter values use their defaults.** Features can define parameters, but parameter values
  resolve to the default defined in the feature. There is no command-line flag to override
  parameter values at import time."
* "**JSONPath parameters are not supported.** A parameter that uses a `paths` (JSONPath)
  expression causes compilation to fail."
* "**Tests are not supported.** A `tests` section is accepted by the schema but is ignored and
  not included in the generated bundle."
* "**The schema is strict.** Unknown fields cause an error. Only `gateway: apigee` and
  `schemaVersion: 1.0.0` are supported."

The "tests are ignored" limitation is worth flagging: a team moving an Apigee test bundle into a
YAML template will silently lose those tests with no error.

Common top-level fields are camelCase; `priority` (default `100`) orders feature application,
lower first. Feature policy names are auto-prefixed with the feature's `uid` (or `name`).

---

## 5. 404 / NOT FOUND

Every URL below was requested and returned HTTP 404. Several are natural guesses that a support
engineer would plausibly write, which is exactly why they are listed.

### Guessed Apigee docs paths

| URL | Status |
| ----- | -------- |
| <https://cloud.google.com/apigee/docs/api-platform/get-started/create-proxy-deployment> | 404 |
| <https://cloud.google.com/apigee/docs/api-platform/get-started/set-up-cloud-apigee> | 404 |
| <https://cloud.google.com/apigee/docs/api-platform/cicd/overview> | 404 |
| <https://cloud.google.com/apigee/docs/api-platform/cicd> | 404 |
| <https://cloud.google.com/apigee/docs/api-platform/deploy/cicd> | 404 |
| <https://cloud.google.com/apigee/docs/api-platform/develop/cicd> | 404 |
| <https://cloud.google.com/apigee/docs/api-platform/develop/maven-plugin> | 404 |
| <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-linter> | 404 |
| <https://cloud.google.com/apigee/docs/api-platform/test/api-proxy-linter> | 404 |
| <https://cloud.google.com/apigee/docs/api-platform/get-started/api-proxy-linter> | 404 |

### Guessed Management API method paths

| URL | Status | Correct path |
| ----- | -------- | -------------- |
| .../v1/organizations.products/create | 404 | `organizations.apiproducts/create` |
| .../v1/organizations.apps/create | 404 | `organizations.developers.apps/create` (apps are nested under a developer) |
| .../v1/organizations.apis.revisions/create | 404 | `organizations.apis/create` creates the revision; there is no revisions/create |
| .../v1/organizations.developers.apps.keys.apiproducts/add | 404 | `...apiproducts/updateDeveloperAppKeyApiProduct` |
| .../v1/organizations.developers.apps.keys.apiproducts/remove | 404 | `...apiproducts/delete` |
| .../v1/organizations.environments.apis.revisions.deployments/list | 404 | use `organizations.environments.deployments/list` or `organizations.apis.revisions.deployments/list` |
| .../v1/organizations.apis.revisions.deployments/generateDeployChangeReport | 404 | it lives under `organizations.environments.apis.revisions.deployments/` |

---

## 6. UNVERIFIED / GAPS — read before citing

Stated plainly rather than omitted.

1. **No CI/CD documentation page exists in the current Apigee docs.** I extracted the full
   426-entry api-platform navigation tree and searched it for cicd / ci-cd / pipeline /
   automated / jenkins / github / cloud-build: zero hits. Six plausible CI/CD URLs all returned
   404. If a case asks "what is the supported CI/CD tool", **I could not verify a Google-authored
   answer in these docs.** The documented building blocks are the Management API, `gcloud apigee`,
   bundle export/import, and `action=validate`. Any named CI/CD product or sample pipeline would
   have to come from elsewhere (community or third-party), and I did not research it.

2. **No proxy linter page exists.** See section 4 "Validation tooling".

3. **`--service-account` on `gcloud apigee apis deploy`**: unverified. The GA page lists only
   `--override`, but the Management API accepts `serviceAccount` and the UI offers it. I did not
   fetch the beta/alpha `apis/deploy` pages, so I cannot say the flag does not exist anywhere.

4. **Product/developer/app create+delete in gcloud GA**: confirmed absent from the GA index.
   I checked the index link trees for all seven groups, so this is documented absence for GA
   only. I did not enumerate every alpha/beta subcommand page (I fetched the group pages and
   the `apis`, `archives`, `operations`, `environments describe` pages only).

5. **Environment group name rules** are self-contradictory in the source: the prose says "only
   lower case letters" then parenthesises `(a-z, A-Z, and -)`, and separately says "You cannot
   use upper case letters". Quoted verbatim in section 3.5; I did not resolve the contradiction.

6. **`organizations.apis.revisions/get`** is cited by `download-api-proxies` as the export
   method but I did not fetch its page directly. The link itself came off a fetched page.

7. **Only Apigee X / hybrid was covered.** I did not verify Apigee Edge for Private Cloud
   (OPDK) equivalents of any of this; `/apigee/docs/` pages carry a banner redirecting Edge
   users to `docs.apigee.com`. Do not transfer these Management API paths to OPDK without
   checking the customer's release version.

8. **Instance/environment creation for hybrid** is managed with `helm` / `apigeectl`, which I
   did not research here (out of scope; see the `apigee-opdk-*` and hybrid skills).
