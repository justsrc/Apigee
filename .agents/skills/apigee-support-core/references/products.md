# Products and where an answer must branch

Apigee X, Apigee hybrid, and Apigee Edge for Private Cloud share a proxy runtime and
almost nothing else operational. Full research in
`research/notes-product-differences.md`.

## Identify the product before prescribing anything

The single best discriminator is the Management API base URL, because it answers in one
question:

- `apigee.googleapis.com` means Apigee X or Apigee hybrid.
- `api.enterprise.apigee.com` means Apigee Edge.
- `http://<host>:8080/v1/o/<org>` means Edge for Private Cloud.

Other tells:

| Signal | Product |
| --- | --- |
| `apigee-service`, `apigee-all`, `/opt/apigee`, `update.sh` | Edge for Private Cloud |
| Cassandra, ZooKeeper, OpenLDAP, "data center" of nodes | Edge for Private Cloud |
| Kubernetes, Istio, runtime pod, `apigee-runtime` | Hybrid |
| Google Cloud project holding the management plane | Hybrid |
| Cloud Run or GKE proxy URL, no runtime under your control | Apigee X |

Ask if it is missing. One question costs a turn. A wrong product assumption costs an
outage, and the person asking will usually act on your answer.

## The comparison page moved

`/api-platform/get-started/compare-apigee-products` is now titled "Apigee technical
feature overview". It compares **X and hybrid only** and contains **no unsupported
feature or unsupported API list**. It used to carry that list.

The Edge to X comparison now lives at
<https://docs.apigee.com/migration-to-x/compare-apigee-edge-to-apigee-x>, which carries a
"Google does not plan to support" list and an unsupported-APIs table.

If you remember the old page having a removal list, you are remembering a page that has
been rewritten. Re-read it rather than citing your memory.

## Feature differences worth checking before you answer

**Instance attachment is Apigee X only.** The Management API reference for
`organizations.instances.attachments` and `organizations.instances` carries a note that
it is not supported for Apigee hybrid.

**Environment groups exist on X and hybrid, and not on Edge.** The hybrid install
instructions include creating one. For Edge, the evidence is documentation-level absence:
the environments overview page on `docs.apigee.com` returns 404 and the navigation tree
carries no environment group topic. That is strongly supported, not documented, so say so
rather than asserting it flatly.

**VerifyIAM is not supported on hybrid.** Stated on the policy page.

**`tls.client.*` flow variables and ingress mTLS are hybrid only.** `tls.cipher`,
`tls.protocol`, `tls.server.name` and `tls.session.id` apply to both.

**Root CA rotation is Apigee X only.** The page says it applies to Apigee but not to
Apigee hybrid.

**KeyValueMap `PUT` refreshes cache on one node only.** Expect write-visibility lag
before a value appears everywhere.

## Traps that cost time

`cloud.google.com/apigee/docs/hybrid/upgrade` returns **HTTP 200 and is a stub** reading
"The equivalent page does not exist in the selected hybrid version." The real page is
`/hybrid/latest/upgrade`.

On `docs.apigee.com`, the version segment is mandatory. `/private-cloud/port-requirements`
returns 404; `/private-cloud/v4.53.01/port-requirements` returns 200.

Edge for Private Cloud release slugs carry the version number. `nginx-45301` and
`rollback-45301` are real pages; `nginx-45300` under `v4.53.01/` is a 404. Check the status
after swapping versions.

`v4.54.00` returns 404, so **v4.53.01 is the latest Edge for Private Cloud release** as
verified on 2026-10-11.

## Hybrid operations

Runtime, sync, key-value maps, logging defaults and upgrade behaviour are in
`references/hybrid.md`. Read it before prescribing anything on hybrid, because a
successful deployment call there is one of at least four separate steps.

## What was not verified

Per-component Edge for Private Cloud log paths, `nodetool` behaviour, Edge key-value map
and UI parity, and Edge TLS and target server workflow details were not verified in this
project. The two Edge skills cover those areas from their own documented references, and
this file does not add claims about them.

Nothing in this project is verified for Edge for Private Cloud from the
`cloud.google.com` policy pages. Those pages carry an "Apigee and Apigee hybrid" banner,
so they do not describe Edge. Do not quote them as Edge behaviour.