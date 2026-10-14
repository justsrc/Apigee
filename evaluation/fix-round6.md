# Round 6 fixes: MED-09, MED-11, ADV-08, ADV-11, HARD-02, HARD-09

Six defects where a scenario contradicted itself: a title that disagreed with its own
evidence, a key that asserted what its evidence ruled out, and a case filed under a
difficulty label it did not meet. All verification was done against the local cache in
`research/pages/` and `research/scratch-pages/`. **No network access was used.**

Files edited: `scenarios/medium.md`, `scenarios/hard.md`, `scenarios/adversarial.md`.
`scenarios/index.md` was not hand-edited. See the note at the end.

---

## MED-09 — the title contradicted the evidence

### Verification

The title said "Intermittent 429". The evidence in the scenario says HTTP 500 with
`policies.ratelimit.QuotaViolation`. Both halves of the reviewer's point check out, and
they come from two different documents:

```text
grep -n "QuotaViolation" scratch-pages/rev-quota-policy.txt
1868:| `policies.ratelimit.QuotaViolation` | `500` | The quota limit was exceeded. | N/A |

grep -n "SpikeArrestViolation" pages/api-platform_reference_policies_spike-arrest-policy.txt
681:`policies.ratelimit.SpikeArrestViolation`
```

with the SpikeArrest status on the following line:

```text
665:`500`   (FailedToResolveSpikeArrestRate)
673:`500`   (InvalidMessageWeight)
681:`429`   (SpikeArrestViolation)
745:The current HTTP status code for exceeding a rate limit set by a Quota or SpikeArrest
    policy is 429 (Too Many Requests).
```

So `429` is SpikeArrest's runtime status, and the scenario's proxy has no SpikeArrest
policy. The title named a fault code the scenario never produces.

The finding is subtler than it first looks, which is why the title could not simply be
changed to 429. The **Quota** page documents *both* statuses, on the same page:

```text
grep -n "429" scratch-pages/rev-quota-policy.txt
1931:**Note:** When the rate of incoming requests exceeds the thresholds set by Quota or
     SpikeArrest policy, the system returns an HTTP status code` 429 Too Many Requests`.
```

and the comparison table lists `429` as the Quota status as well:

```text
grep -n "429" scratch-pages/rev-comparing-quota-spike.txt
68:<td>429</td>   (Quota)
69:<td>429</td>   (SpikeArrest)
```

So changing the evidence to 429 would have been defensible, and would have made the
scenario collide with HARD-13, which already handles exactly this tension and already
explains it correctly: *"The Quota policy error table does map
`policies.ratelimit.QuotaViolation` to a 500, but that is the status of the fault the
policy throws, which reaches a caller only if it propagates unhandled."*

### Fix

Retitled to match the evidence, and added the documentation tension as a **finding**
rather than leaving it as a trap:

- Title: `MED-09. Bursts are rejected by a Quota policy that is enforcing correctly`.
- Metadata now names the evaluation objective explicitly: the fault code is
  `QuotaViolation`, so the answer must not promote it to a spike problem.
- Expected investigation explains that both statuses are documented, and that a 429
  would not change the diagnosis but would change what the team is looking at.
- Ground truth states that `QuotaViolation` is Quota's error and `SpikeArrestViolation`
  is SpikeArrest's, and that this proxy has no SpikeArrest policy.
- New incorrect answer: describing the rejections as spike rejections because the
  traffic is bursty.
- **Not a critical failure:** raising the 500-versus-429 question. This is the reviewer's
  explicit requirement — a respondent who spots the mismatch before the retitle must not
  be penalised. An answer that keeps the diagnosis intact and asks how the Quota fault is
  being surfaced is the correct answer; stopping there is incomplete, not wrong.

Checked: a correct, honest answer trips none of the listed critical failures.

---

## MED-11 — the key and the incorrect-answers list contradicted each other

### Verification

Ground truth: *"The environments differ in a map entry that lives outside the bundle."*
Incorrect answer listed: *"Concluding the two environments must be misconfigured. One
difference is a fact, not a defect, until you know it was unintended."*

The first says they differ. The second fails a respondent for saying so.

### Fix

The intended wrong answer was the inverse of the finding: treating an identical bundle as
proof of identical environments, and therefore hunting for the difference in the bundle
or the request rather than in environment-scoped configuration.

- Replaced with: concluding the environments must be identical and one was mis-deployed,
  plus blaming the target or runtime for a difference between two control-plane
  configurations.
- Added **Not a critical failure:** stating that the two environments differ. That is the
  finding. It becomes wrong only when turned into a claim that *both* are broken.

Checked: the existing critical failures are about manual map edits and blaming the `30`,
neither of which a correct answer does.

---

## ADV-08 — internal contradiction about `latest` versus pinned paths

### Verification

The old key said the topic "lives at `/private-cloud/latest/...`" while the remediation
said to "quote the pinned form rather than `latest`". The reviewer asked whether the
pinned form is evidenced. Checked the scratch cache, which retains hrefs the `.txt`
normalization drops:

```text
grep -o 'href="[^"]*"' scratch-pages/rev-opdk-versions.txt | grep v4.53
/private-cloud/v4.53.00/how-configure-edge      <- 4.53.00 pinned, attested
grep -n "latest" scratch-pages/rev-opdk-versions.txt
10:- [Edge for Private Cloud overview](/private-cloud/latest/overview)
12:- [Configuration](/private-cloud/latest/how-configure-edge)
```

The landing page uses `latest` for 4.53.01 and `v4.53.00` for the previous release. **No
`/private-cloud/v4.53.01/how-configure-edge` appears anywhere.** But the pinned 4.53.01
tree is real and attested elsewhere:

```text
grep -o 'href="[^"]*"' scratch-pages/rev-opdk-update-apigee-edge-45202-45301.txt
/private-cloud/v4.53.01/install-and-configure-edge-sso#commonconfig
grep -n "private-cloud/v4.53.01" scratch-pages/rev-opdk-how-perform-backup.txt
[Backup and restore](/private-cloud/v4.53.01/backup-and-restore)
```

So the old key asserted a pinned form for a page that the evidence does not attest, while
the scenario simultaneously told the respondent that only the `latest` form was correct.

### Fix

Resolved by separating two things the old text conflated — *pinning is achievable* and
*any particular pinned string is attested*:

- Diagnostic evidence now states the pinned tree demonstrably resolves
  (`update-apigee-edge-45202-45301`, `backup-and-restore`), **and** that the landing page
  never shows `/private-cloud/v4.53.01/how-configure-edge`, so that string is an inference
  from the family rather than something the pages attest.
- Ground truth: "A pinned path is correct because someone confirmed it, not because the
  shape is predictable."
- Remediation: where a pinned path is attested, quote it; where only `latest` is attested,
  give the `latest` URL, name the release it currently resolves to, and say the pinned
  equivalent is unverified.
- New incorrect answer: substituting `latest` for `v4.53.01` and presenting the result as
  verified — a false report about a check that did not happen.
- Rubric row reworded from "quotes pinned paths" to "quotes a pinned path where one is
  attested", plus a citation row that penalises claiming verification not performed.
- **Not a critical failure:** quoting `latest` for a topic with no attested pinned path,
  provided the answer names the release it resolves to and marks it floating.

Everything the key asserts is now verifiable from the pages.

---

## ADV-11 — unsupported causal claim in the ground truth

### Verification

The key asserted that a rollback "left the environment unattached". Turn-2 evidence said
only two things: the rollback created a new revision, and the environment is not a member
of any group. Nothing connected them. A rollback is a revision operation inside an
environment; the environments overview is explicit that group membership is separate:

```text
grep -n "environment group" pages/api-platform_fundamentals_environments-overview.txt
16:An environment must be a member of at least one environment group before you can
   access proxies deployed within it.
```

### Fix

Two options were available: add evidence supporting the claim, or remove it and re-derive.
The evidence route would have meant inventing a mechanism in which a rollback detaches an
environment group — unsupported and, as written, the claim was the thing least defensible
in the key. So the claim was removed and the resolution re-derived from what is evidenced.

- Turn-2 evidence now adds the **attachment history**, grounded in the documented
  `createdAt` field on the EnvironmentGroupAttachment resource
  (`pages/api-platform_fundamentals_environmentgroups-working-with.txt:151` — "the
  response contains details about the new attachment, including the timestamp at which it
  was created"). The record shows `createdAt` eight months old with no deletion or
  replacement since, which is evidence *against* the rollback having removed it.
- Ground truth keeps the finding the case is built on — environment addressing, 404 to all
  clients, no OAuth involved — and separates it from the unexplained *origin* of the
  unattached state, with the open candidates named.
- The fix and the cause are distinguished: reattachment restores the route either way, but
  whether it restores an expected attachment or papers over a removal is a different
  question answered by the attachment history.
- New incorrect answer: asserting the rollback detached the environment.
- New rubric row, *Attribution of cause*, plus a critical failure for asserting the
  detachment as established.
- **Not a critical failure:** proposing the reattachment without investigating why the
  environment was unattached.

---

## HARD-02 — unsurfaced contradiction

### Verification

The ticket claimed the change "was deployed successfully" last month. The diagnostic
evidence showed revision 20 still `PROGRESSING` with revision 19 `READY` and serving.
Nothing in the case acknowledged the gap, and nothing in the rubric rewarded spotting it.

### Fix

Surfaced deliberately as a second, independent contradiction. This makes the case harder
rather than easier, which is the correct direction for a hard file.

- Evaluation objectives now say there are two contradictions and that only one is obvious.
- Expected investigation names the ticket as the source of the second.
- Diagnostic evidence notes the deployment record's start timestamp is not supplied, which
  is what keeps the two accounts apart instead of resolving them.
- Ground truth makes the consequence explicit: a deployment progressing for a month is
  stuck and "wait for `READY`" would be **wrong**; a recent deployment makes waiting
  right. Opposite recommendations, and the evidence does not distinguish them.
- Remediation now branches on that check rather than unconditionally advising "wait".
- Two new incorrect answers: adopting "deployed successfully" as established, and advising
  a wait without checking when the deployment started.
- Rubric's *Handling of competing causes* now reads "Names **both** contradictions";
  *Diagnostic method* gained the start-time check; *Quality of next step* now branches.
- New critical failure for accepting the ticket's success claim.
- **Not a critical failure:** noticing that a month-old deployment cannot still be
  progressing and raising it. That is correct and the case is built on it. What fails is
  noticing it and then advising as though the ticket were right.

---

## HARD-09 — difficulty mislabelled; moved to adversarial as ADV-13

### Verification

`scenarios/index.md` defines hard as *"Competing causes, and in some cases deliberately
insufficient evidence."* HARD-09 had one cause (the requested change weakens a control),
no competing hypothesis, and nothing a respondent could discriminate between. Its own
rubric had a row headed *Handling of competing causes* whose cells were "Concedes /
Suggests deferral / Offers an immediately actionable safe path" — that is a safety row
wearing a diagnosis row's label. The same failure mode is already covered by ADV-09
(unsafe remediation proposed with good intentions) and ADV-02.

### Fix

Moved rather than rewritten. Adding competing hypotheses would have meant inventing a
diagnostic puzzle the case does not contain; the honest options were to move it or leave a
false label in place.

- Removed from `hard.md`; added to `adversarial.md` as **ADV-13**.
- **No other ID was renumbered.** hard.md now runs HARD-01…HARD-08, HARD-10…HARD-15.
  The gap is intentional and is documented in the file header, which now reads
  "Fourteen cases" and explains where the case went and why the label did not fit.
- Metadata gained the `Failure mode targeted` field the adversarial file uses, and Origin
  is now `adversarial, synthetic` per that file's convention.
- The misleading rubric row was renamed to *Handling of the schedule*, which is what it
  actually measured.
- Added **Not a critical failure:** recommending the narrow origin without mentioning the
  policy owner's review — process, not configuration.

---

## Housekeeping

**Error payloads.** All `errorcode` bodies remain nested and unchanged. Verified across
all three files; no payload was added, removed, or restructured.

**11-section structure.** Verified programmatically. All 14 hard.md and all 13
adversarial.md cases carry exactly the 11 required `####` sections. medium.md cases carry
the 11 plus a `#### Critical failures:` heading, which is that file's existing convention
used by all 22 cases; the two `Not a critical failure` headings added here follow the same
convention.

**`scenarios/index.md`.** Not hand-edited. Note for the record: while verifying that the
ID set was still parseable I invoked `build_scenario_index.py` without its `--dry-run`
flag, so the file was rewritten by the generator rather than by me. Its content is
whatever the generator produces from the three edited files — 72 scenarios, MED-09 with
the new title, no HARD-09 row, an ADV-13 row — so the regeneration the task anticipated
has simply already happened. No hand-written content was introduced or lost.
