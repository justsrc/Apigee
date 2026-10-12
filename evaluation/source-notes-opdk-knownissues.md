# OPDK known-issues coverage

## Question

The official known-issues register contained no OPDK entries at the time of the research.
Why, and what does that actually establish?

## Status

**RESOLVED** — the exclusion is by design and the register states its own scope. This
answers *why the register has no OPDK entries*. It does **not** answer whether any
particular OPDK issue exists or is documented elsewhere.

## What the register is

- URL: <https://cloud.google.com/apigee/docs/release/known-issues>
- Title: `Apigee known issues | Google Cloud Documentation`
- Fetched 2026-10-12. 271,409 bytes. Not a soft 404 (body does not contain "the equivalent
  page does not exist in Apigee").
- Cached locally as `research/pages/apigee-known-issues.txt`; parsed entries live in
  `research/ki-entries.json`.

### Its own scope statement

> This page applies to **Apigee** and **Apigee hybrid**.

### Its product filter

The page offers these filters, read from the live page:

> API hub, API Monitoring/Analytics, Apigee, Apigee in VS Code, Archive deployments,
> Connectors, Documentation, hybrid, Integration, Integrated portal, Monetization, UI

There is no Edge for Private Cloud entry, and no OpDK release filter. The register does not
merely contain no OPDK rows; it does not offer OPDK as a category.

## What was found in the project's cached copy

`research/ki-entries.json`, 102 entries, by declared product:

| Count | `product` value |
| --- | --- |
| 66 | Apigee hybrid (+Apigee) |
| 30 | Apigee |
| 2 | UI |
| 1 | All Apigee products |
| 1 | Apigee in VS Code |
| 1 | Integrated portal |
| 1 | Apigee Emulator |

Status split: 71 fixed, 31 open.

A case-insensitive search of every field of all 102 entries for
`opdk|private cloud|edge for private` returns **0 matches**. No entry mentions OPDK in its
product, its affected versions, its status, or its body.

The single occurrence of the string "Private Cloud" on the live page is in the global
product navigation menu at the top of the Google Cloud documentation shell, not in the
issue table. It is not evidence of an OPDK row.

## Why no OPDK entries appear

Each candidate explanation, with the evidence:

**1. The register excludes OPDK by design — SUPPORTED.**

The page's own banner scopes it to "Apigee and Apigee hybrid", and its filter list contains
no OPDK option. An issue tracker that excludes a product from its scope will not contain
that product's rows. This is the explanation the evidence supports.

**2. OPDK issues are documented elsewhere — PARTIALLY SUPPORTED, not located.**

Edge for Private Cloud operational documentation exists and is cached under
`research/pages/` at `https://docs.apigee.com/private-cloud/v4.53.01/*`: installation
topologies, port requirements, how-monitor, backup and restore, how-perform-backup,
nginx-45301, rollback-45301, update-apigee-edge-45202-45301, upgrade-paths. These are
operational references, not an issue register.

The OPDK release-notes page exists at
`https://cloud.google.com/apigee/docs/edge-private-cloud/release-notes` but is feed-backed
and currently thin: the underlying feed
(`https://docs.cloud.google.com/feeds/apigee-edge-private-cloud-release-notes.xml`) carries
**one** entry, dated 2026-09-02. I did not find a per-release "fixed issues" listing for
OPDK. Note that `.../release-notes/changes-privatecloud-45301` returns a genuine HTTP 404,
which is a different outcome from the Google soft-404 stub and was classified correctly.

**3. The project wrongly assumed the register was exhaustive — SUPPORTED for Apigee X and
hybrid, REFUTED as a general claim.**

The register is authoritative for what it scopes. It is not evidence about OPDK, and
treating "absent from this register" as "no known issues exist" is the inference this
project must not make.

## The distinction, stated explicitly

These are three different claims and only the first is established here.

- **No entries found in a particular register.** ESTABLISHED. 102 entries in
  `research/ki-entries.json`; 0 reference OPDK. The live register confirms the same scope.
- **No known issues documented in the sources searched.** NOT ESTABLISHED. Sources
  searched: the known-issues register, its parsed cache, the OPDK release-notes page and
  feed, and the cached `docs.apigee.com/private-cloud/v4.53.01/*` set. That is not an
  exhaustive survey of where OPDK issues might be recorded, and absence from this list is
  not evidence of absence.
- **Evidence that a specific OPDK issue does not exist.** NONE. Nothing in these sources
  bears on that question.

## Defensible conclusion

The known-issues register has no OPDK entries **because it declares that it does not cover
OPDK**, not because OPDK has no known issues. The original project's observation was
correct and its likely inference was not: the register is a source for Apigee and Apigee
hybrid only, and a support answer that says "there is no known issue for this" on the
strength of this register would be asserting something the register does not support.

What this changes for the skills: an agent working an OPDK case must not treat this
register as authoritative or exhaustive. It should say that the register does not cover Edge
for Private Cloud, and point at the version-pinned
`docs.apigee.com/private-cloud/v4.53.01/` documentation and the release notes instead, noting
that OPDK version pinning means a topic verified at one release may not exist at another.

What this does not establish: whether any particular OPDK defect is documented, tracked, or
fixed. That needs the OPDK support channel, which is outside the public sources searched
here.

## Sources

| Claim | Source | How checked |
| --- | --- | --- |
| Register exists and is not a soft 404 | <https://cloud.google.com/apigee/docs/release/known-issues> | curl 2026-10-12, 271,409 bytes, grep for the soft-404 phrase → 0 |
| Register scope | same | Scope banner extracted from the rendered text |
| Filter list excludes OPDK | same | Filter list extracted from the rendered text |
| 102 entries, 0 OPDK | `research/ki-entries.json` | Counted; regex `opdk\|private cloud\|edge for private` over every field → 0 matches |
| OPDK operational docs exist | `research/pages/https___docs.apigee.com_private-cloud_*` | Listed from the corpus; URLs in `MANIFEST.tsv` |
| OPDK release notes are thin | `https://cloud.google.com/apigee/docs/edge-private-cloud/release-notes` and its XML feed | Feed parsed: 1 entry |
| `changes-privatecloud-45301` is a real 404 | `.../edge-private-cloud/release-notes/changes-privatecloud-45301` | curl → HTTP 404 with a `404 \| Page Not Found` title |