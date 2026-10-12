# OPDK known-issues coverage

## Question

"The official known-issues register contained no OPDK entries at the time of the research." Why?
Because the register excludes OPDK, because OPDK issues are published elsewhere, because the
research searched the wrong source, or because OPDK has no documented known issues? And which of
(a) no entries found in a particular register, (b) no known issues documented in the sources
searched, (c) evidence that a specific issue does not exist, does the evidence support?

## What the register is

There are **two** official known-issues registers, on two hosts. The reported issue names only
one, and it is the one the project's known-issues passes actually read.

**Register 1 — the one the project used.** `https://cloud.google.com/apigee/docs/release/known-issues`
Title (live fetch 2026-10-12): "Apigee known issues | Google Cloud Documentation". Coverage
statement, verbatim from `research/pages/apigee-known-issues.txt:1`:
> "*This page applies to **Apigee** and **Apigee hybrid**.*"
(Live render on 2026-10-12, without the emphasis: "This page applies to Apigee and Apigee hybrid.")
Scope sentence, `research/pages/apigee-known-issues.txt:5`:
> "This section lists known issues for Apigee components. For a list of bugs, new features, and
> other release information, see the release notes"

**It does state which products it covers — Apigee and Apigee hybrid — and makes no claim to cover
Edge for Private Cloud.** Consistent with that: its product filter chips are "API hub, API
Monitoring/Analytics, Apigee, Apigee in VS Code, Archive deployments, Connectors, Documentation,
hybrid, Integration, Integrated portal, Monetization, UI", and its version chips are "Apigee 1-10,
Apigee 1-9, hybrid 1.16 … hybrid 1.3" — no Private Cloud option anywhere
(`research/pages/apigee-known-issues.txt:7`; live fetch 2026-10-12). It carries an Edge redirect
banner (`:3`): "If you are using Apigee Edge for Public or Private Cloud, click this link to view
Apigee Edge documentation."

**Register 2 — the OPDK one, which this project's known-issues passes never fetched.**
`https://docs.apigee.com/release/known-issues`. Title (live fetch 2026-10-12): "Known issues with
Apigee | Apigee Edge | Apigee Docs"; footer "Last updated 2026-10-09 UTC". Coverage statement,
verbatim (live fetch 2026-10-12):
> "The following sections describe the known issues with Apigee Edge and Edge for Private Cloud.
> In most cases, the issues listed will be fixed in a future release."
It has an H2 section "Known issues with Edge for Private Cloud" introduced by "The following
sections describe the known issues with Edge for Private Cloud." It is linked from the left nav of
docs.apigee.com pages as "All known issues" → `/release/known-issues`, and from the OPDK 4.53.01
release notes as "Known issues with Edge for Private Cloud" → `/release/known-issues#private-cloud`
(both verified on `https://docs.apigee.com/release/notes/45301-edge-private-cloud-release-notes`,
fetched 2026-10-12).

So "the official known-issues register" is ambiguous: register 1 does not cover OPDK, register 2
does.

## What was found

- **102 entries** in the cached copy: `research/ki-entries.json`, parsed by
  `research/parse_knownissues.py` from `research/pages/apigee-known-issues.txt` (85,178 bytes);
  `research/ki-scored.json` holds the same 102.
- **Zero are OPDK.** By product: Apigee hybrid (+Apigee) 66, Apigee 30, UI 2, All Apigee
  products 1, Apigee in VS Code 1, Integrated portal 1, Apigee Emulator 1
  (`research/ki-entries.json`; same grouping at `research/notes-rw-knownissues.md:13-22`).
- The only entry containing the string "private" is **465834046**, about "the private key rotation
  policy" (cert-manager) — not Private Cloud (`research/ki-entries.json`; row at
  `research/notes-rw-knownissues.md:99`).
- The absence is reproducible: `research/pages/ki-live-20261012.txt` is byte-identical to
  `research/pages/apigee-known-issues.txt` (md5 `1a86830cc77b81950ce781cfe9d2ca1e`), and a live
  re-fetch of register 1 on 2026-10-12 still returned 102 nine-digit IDs and no Private Cloud
  rows. Matches `research/notes-rw-opdk.md:1984`, which records "zero matches for 'private cloud',
  'OPDK', or 'Edge for Private'".
- **The project has no cached copy of register 2 at all.** No file in `research/pages/` contains
  its distinctive strings ("Known issues with Edge for Private Cloud", `CVE-2026-42945`, `BCFIPS`),
  and `research/pages/MANIFEST.tsv` records only the cloud.google.com URL under known issues
  (rows `apigee-known-issues`, `known-issues-v`, `ki-live-20261012`, all 85,178 bytes).
- One project file does record register 2 as reachable:
  `research/notes-product-differences.md:40` — "Known issues with Edge / Edge for Private Cloud |
  https://docs.apigee.com/release/known-issues | 200 | 25961" — and `:216` cites its EOL pop-up
  entry as "documented under known issues".

## Why no OPDK entries appear

**C1 — register 1 is scoped by its own declaration to Apigee and Apigee hybrid.** *For:* the
applies-to line (`:1`), no Private Cloud product or version chip (`:7`), 102/102 entries in the
Apigee/hybrid families, and a separate Edge-docs banner (`:3`). *Against:* a scope line is a
declaration, not a stated reason; nothing says OPDK was deliberately excluded. Proximate
explanation, not motive.

**C2 — OPDK known issues live in register 2 on the Apigee Edge host.** *For:* live fetch
2026-10-12 of `https://docs.apigee.com/release/known-issues`, coverage statement naming "Apigee
Edge and Edge for Private Cloud", a 10-row OPDK table (next section), the release-notes link to
`/release/known-issues#private-cloud`, and `research/notes-product-differences.md:40` recording
HTTP 200 on 2026-10-11. *Against:* nothing. This is the strongest explanation, and it contradicts
`research/notes-rw-knownissues.md:33-34` and `:564`, which assert "OPDK known issues live in the
release notes on `docs.apigee.com`, not here" — incomplete, since a dedicated register exists.

**C3 — OPDK issues are published in per-release release notes instead of a register.** *For:*
`https://docs.apigee.com/release/notes/45301-edge-private-cloud-release-notes` (fetched
2026-10-12) has "Bug fixes" with issue IDs, plus "Known Issues" sections;
`research/pages/https___docs.apigee.com_private-cloud_versions.txt` links each release to its
release notes. *Against:* those pages delegate rather than list ("See Known issues with Edge for
Private Cloud for a complete list of known issues"). Half right, and the weaker half.

**C4 — the research searched the wrong source.** *For:* `research/fetch_ki.sh` defaults every
fetch to `https://cloud.google.com/apigee/docs/${path}` and no invocation records a docs.apigee.com
known-issues URL; `MANIFEST.tsv` has no row for register 2; no cached copy exists; the skills
directory references no known-issues register. *Against:* `notes-product-differences.md:40` shows
the project did fetch register 2 and record HTTP 200 — the URL was known, just never mined. A
coverage gap in the known-issues passes, not a total search failure.

**C5 — OPDK has no known issues documented.** *Against:* falsified by register 2's 10 OPDK
entries (fetched 2026-10-12). Do not assert.

**C6 — the content appeared only after the research.** *Against:* register 2's footer reads "Last
updated 2026-10-09 UTC", before the 2026-10-11 research date, and
`notes-product-differences.md:40,216` show both the page and an OPDK entry from it in use on
2026-10-11. Caveat: register 2 is not version-pinned; these counts are as of 2026-10-12.

**Skills directory:** `grep -ri 'known issue' .agents/` returns exactly one hit,
`.agents/skills/apigee-support-core/references/hybrid.md:80`, about a hybrid register entry (the
`apigee-logger` DaemonSet issue, register-1 entry 543171828). Neither OPDK skill links any
known-issues register: `.agents/skills/apigee-opdk-troubleshooter/SKILL.md:21-32` and
`.agents/skills/apigee-opdk-upgrader/SKILL.md:19-27,137` list operational pages and the OPDK
release-notes page only.

## Where OPDK issues are documented instead

**Primary source (not cached here; URL verified live 2026-10-12):**
`https://docs.apigee.com/release/known-issues` — "Known issues with Apigee". Its OPDK section's
table has a header row plus 10 entry rows:

| Area, as printed | Entry |
| --- | --- |
| Edge for Private Cloud 4.53.01 | NGINX Vulnerability Assessment (CVE-2026-42945) |
| Edge for Private Cloud 4.53.00 | 440148595: End of Life Popup Warning Displayed Excessively |
| Edge for Private Cloud 4.53.01 | Java Callouts — Bouncy Castle provider name "BC" → "BCFIPS" |
| Edge for Private Cloud 4.53.00 | Java Callouts — same, for 4.53.00 |
| Edge for Private Cloud 4.52.01 Mint update | `OutOfMemoryError: unable to create new native thread`; fixed in 4.52.01.01 |
| Apigee HTTP/2 vulnerability | CVE-2023-44487, Edge for Private Cloud router and management server |
| Postgresql upgrade when updating to version 4.52 | Fails when the number of tables exceeds 500 |
| LDAP policy | 149245401: LDAP connection pool settings for JNDI |
| High Request Processing Latency | 139051927: MP HTTPClient cache eviction above ~50 target servers |
| Multiple entries for key value maps | 157933959: "This limitation only applies to Edge for Private Cloud." |

**Secondary source (live fetch 2026-10-12):**
`https://docs.apigee.com/release/notes/45301-edge-private-cloud-release-notes` — "4.53.01 Edge for
Private Cloud release notes", with "Bug fixes" (issue IDs 166228, 391852306, …) and "Known Issues"
delegating to `/release/known-issues#private-cloud`.

**Pages cached in `research/pages/` (real URLs from `research/pages/MANIFEST.tsv`):**

| Cached file | Real URL | What it carries |
| --- | --- | --- |
| `research/pages/edge-private-cloud_release-notes.txt` | `https://cloud.google.com/apigee/docs/edge-private-cloud/release-notes` (URL at `research/official-documentation-index.md:299`; **no MANIFEST.tsv row**) | Post-Sep-2026 OPDK release notes; its "See also" links "Known issues" to `/apigee/docs/release/known-issues` — register 1, which holds no OPDK content |
| `research/pages/https___docs.apigee.com_private-cloud_versions.txt` | `https://docs.apigee.com/private-cloud/versions` (rows `rev-opdk-versions`, `https___docs.apigee.com_private-cloud_versions`) | Per-release index linking to each release's release notes |
| `research/pages/https___docs.apigee.com_private-cloud_v4.53.01_upgrade-paths.txt` | `https://docs.apigee.com/private-cloud/v4.53.01/upgrade-paths` (row `rev-opdk-upgrade-paths`) | Supported upgrade paths to 4.53.01 |
| `research/pages/https___docs.apigee.com_private-cloud_v4.53.01_backup-and-restore.txt` | `https://docs.apigee.com/private-cloud/v4.53.01/backup-and-restore` (row `rev-opdk-backup-and-restore`) | Coordinated three-store restore rules |
| `research/pages/https___docs.apigee.com_private-cloud_v4.53.01_how-perform-backup.txt` | `https://docs.apigee.com/private-cloud/v4.53.01/how-perform-backup` (row `rev-opdk-how-perform-backup`) | Component backup procedure |

Documented OPDK behaviour *changes* (not known issues) are on the versioned "Changes in" pages
cited at `research/notes-rw-opdk.md:27` and `:119`, fetched live 2026-10-12, not cached.

**Negative results worth keeping:** four candidate OPDK known-issues URLs returned genuine HTTP
404 pages (titled "404 | Page Not Found"), not soft 404s, on 2026-10-12:
`https://docs.apigee.com/private-cloud/v4.53.01/known-issues`,
`https://docs.apigee.com/private-cloud/known-issues`,
`https://cloud.google.com/apigee/docs/release/known-issues-edge-private-cloud`,
`https://cloud.google.com/apigee/docs/edge-private-cloud/known-issues`.

## Distinguish explicitly

- **No entries found in the register: TRUE, and precise.** 102 entries in the project's cached
  copy of `https://cloud.google.com/apigee/docs/release/known-issues`
  (`research/ki-entries.json`, from `research/pages/apigee-known-issues.txt`, 85,178 bytes); 0
  are OPDK. Re-confirmed against a live re-fetch on 2026-10-12 (102 nine-digit IDs, no Private
  Cloud rows). This is statement (a) and nothing more.
- **No known issues documented in the sources searched: FALSE as a general claim; narrowly true
  only of the exact sources searched.** The sources actually searched for known issues were
  register 1 (three cached copies, `research/pages/MANIFEST.tsv`) and, per
  `research/notes-rw-opdk.md:1984`, register 1 again as an explicit negative result. No cached
  copy of register 2 exists in `research/pages/`. But register 2 was reachable throughout —
  `research/notes-product-differences.md:40` records HTTP 200 on 2026-10-11, and a live fetch on
  2026-10-12 returns 10 OPDK entries — so "OPDK has no documented known issues" is falsified.
- **Evidence that a specific issue does not exist: NONE in general.** No source searched says an
  OPDK defect does not exist. What exists is (i) a register whose declared scope excludes OPDK,
  (ii) one entry stating a limitation "only applies to Edge for Private Cloud" (157933959), and
  (iii) one entry stating "Apigee Edge for Private Cloud is not affected by this vulnerability in
  its default, shipped configuration" (CVE-2026-42945) — a negative statement about one named CVE
  in one configuration. The absence of a register row is not evidence of the absence of a defect.

## Status

RESOLVED — the absence is explained by a two-register split: the register the project fetched is
declared to cover Apigee and Apigee hybrid only, and OPDK known issues live in a separate
Edge-hosted register that the project's known-issues passes never fetched.

## Defensible conclusion

Established:

- The register the project read (`research/pages/apigee-known-issues.txt`) declares itself to
  apply to "Apigee and Apigee hybrid" and contains 102 entries, none for OPDK — still true of the
  live page as of 2026-10-12.
- A second official register, `https://docs.apigee.com/release/known-issues`, states it covers
  "Apigee Edge and Edge for Private Cloud" and carries a 10-entry OPDK section, plus per-release
  OPDK release notes on docs.apigee.com. The project recorded that URL as reachable
  (`research/notes-product-differences.md:40`) but never fetched or cached it, and
  `research/notes-rw-knownissues.md:33-34` names the wrong location.
- One real discoverability defect: the post-Sep-2026 OPDK release-notes page
  (`research/pages/edge-private-cloud_release-notes.txt`) links "Known issues" to register 1,
  which holds no OPDK content, while the correct target is register 2's `#private-cloud` anchor.

Not established:

- Any reason beyond the pages' own declarations for why Google maintains two registers. No page
  states that OPDK was deliberately excluded from register 1.
- That OPDK has no known issues, or that any particular OPDK issue does not exist; no source
  searched supports either, and register 2 contradicts both.
- Stable counts: register 2 is not version-pinned (footer "Last updated 2026-10-09 UTC"), so its
  10 OPDK entries are as observed on 2026-10-12, not a permanent figure.
