# Scenario correctness baseline

A measured count of scenarios free of known material errors, so "the suite is done" means
something checkable rather than a feeling.

## How this is measured

By blind hostile review, not by counting my own fixes. Counting my own fixes is exactly
how round one looked finished while a quarter of it was wrong. Each review agent gets the
scenario files, the local documentation cache, and a list of already-established facts. It
does not see the previous reviews, and it is told to assume nothing.

A scenario counts as clean when a reviewer returns CORRECT, meaning every fault code, HTTP
status, XML element, API path and CLI flag it cites was verified against a fetched page,
and its ground truth is derivable from the evidence provided.

## Round 1, before any fixes

63 scenarios reviewed. **18 material errors, so 71.4% clean.**

Error classes, in order of frequency:

1. Invented XML elements and attributes. The largest single class.
2. Misattributed fault codes, including codes on the wrong policy page and wrong statuses.
3. Contradictions between a scenario's ground truth and its own incorrect-answers section.
4. Assertions about a control or method that does not exist, in some cases while citing
   the page that documents it.

Reviews: `review-easy-medium.md`, `review-hard-adv-reg.md`.

## Round 2, after fixes and a second blind pass

| Part | Scenarios | Material errors | Clean |
| --- | --- | --- | --- |
| easy + medium | 37 | 4 | 89.2% |
| hard + adversarial + regression | 35 | 5 | 85.7% |
| **Combined** | **72** | **9** | **87.5%** |

Neither half cleared 90% on its own. Averaging them would have been a convenient way to
hide that, so the halves are reported separately as well.

Part 2 also flagged a process defect that no structural check could see, described under
Process defects below.

### What the first blind pass still caught

EASY-06 asserted that header flow variables are case-sensitive. The documentation uses
both `request.header.authorization` and `request.header.Authorization` as documented
defaults for the same wire header, so the claim was backwards, and three listed critical
failures would have caught a correct answer. That is the same failure shape as HARD-07:
the ground truth was inverted, and inverted is worse than vague.

EASY-10 named `<SecretVariable>` and `<VerificationOutputVariableToVerify>` as the elements
to go and add. Neither exists in 408 cached pages. The real ones are `<SecretKey>` and
`<VerificationValue>`.

MED-04 supplied `<Key>` for ResponseCache, which exists only inside `<Encryption>` in the
JWT policies, while telling the agent not to invent cache-key expressions.

MED-15 wrote `javacallout.ExecutionError` without the `steps.` prefix, in the one scenario
whose evaluation target is exact-code discipline.

### Two corrections to my own work

`<LoadBalancer>` is real and a child of `<HTTPTargetConnection>`; `<LoadBalancing>` is the
invented one. I had told the fix agents the opposite. `<SSLInfo>` has more children than the
four I listed. `context.request.header.getValue` does not exist either: `getValue` appears
zero times on the JavaScript object model page, and the documented forms are
`context.getVariable("request.header.X")` and `context.proxyRequest.headers['X']`.

A fix report also carried a caveat claiming MED-07's `setSyncAuthorization` was not
locally verifiable. It is, in six places in the hybrid synchronizer-access page. The
caveat has been retracted in place, because a wrong caveat in a fix report invites a later
pass to break working content.

## Why this number is worth less than it looks

Thirty-seven scenarios reviewed by one reviewer each, no second opinion, and the reviewer
worked from the same cache the fixers used. A reviewer sharing a source with the fixer can
inherit the same blind spot.

This measures "no known material errors under one review pass". It does not mean correct.
The evaluation in `results/RUNS.md` remains the only thing that says whether any of this
helps a real answer, and that run is too small to conclude from.

## What the reviews consistently find

The same four classes, every time. That is the useful signal, not the ratio.

Invented XML is first, and it is the one class a careful writer should catch, since
element names are checkable against a reference page in seconds. It survives because
plausible names are generated fluently and nothing stops generation until something
downstream fails to parse.

Fault codes are second, and the pattern is misattribution rather than pure invention: a
real code attached to the wrong policy page, or to the wrong status. A code being real does
not make its stated cause real.

The third class is the one that worries me most, because it is invisible to every
mechanical check: a scenario whose ground truth is wrong in a way that makes a correct
answer score as a critical failure. A passing harness cannot see it. Only review can.
## Round 3, final blind pass

Part 2 (`final-review-hard-adv-reg.md`, 35 scenarios): **2 material errors, 94.3% clean**,
plus 10 minor.

The two survivors were both instructive.

HARD-02 used `DEPLOYING` as a deployment state. The documented enum is `PROGRESSING` then
`READY`. A corpus whose whole purpose includes catching invented flags and elements was
inventing an enum value, and HARD-05 in the same file had it right, which is the part that
should bother anyone reading it.

HARD-08 quoted one sentence from the Quota page and dropped the sentence after it, which
says the opposite about the consequence. The worked example increments once per policy
EXECUTION, not once per request, and the page calls multi-placement an antipattern that
makes Quota run out faster than expected. The scenario had asserted the opposite of the
documented statement. Its rubric was also self-contradictory in the inversion class:
technical correctness paid 2 marks for identifying double counting while critical failures
named asserting double counting as a fail, so a respondent earned marks for the answer
that failed them.

### Where this leaves the number

Measured after the round 3 fixes, by a pass that predates them:

| Part | Scenarios | Material errors | Clean |
| --- | --- | --- | --- |
| hard + adversarial + regression | 35 | 2 | 94.3% |
| easy + medium | pending | see `final-review-easy-medium.md` | pending |

The hard/adversarial/regression half clears 90%. The easy/medium half last measured 89.2%
and has had four scenarios rewritten since, so its number is stale and a fresh pass is
required before any combined figure is quoted.

I am not going to publish a single blended percentage until both halves have been measured
after their fixes. Blending a fresh number with a stale one is how a suite gets declared
finished while a quarter of it is wrong.

## Process defects found by review, not by the harness

Three, all of which would have corrupted a scoring run rather than merely misreporting.

**Stale answer keys.** Packets are generated from scenarios, and scenarios get edited.
Nothing enforced regeneration, so a reviewer read a `HARD-08.key.md` still asserting a
ground truth the scenario had been rewritten away from, and an `ADV-12.key.md` asserting a
conclusion the scenario no longer reached. Any evaluation run before the regeneration
graded respondents against the wrong answers. The harness now compares packet mtimes
against the mtime of the file containing that scenario ID, and fails with the regeneration
command. It fired on its own in real use the first time an agent edited a scenario file.

The first version of that check passed vacuously, because it keyed the lookup by filename
stem (`hard`) while packets are named by scenario ID (`HARD-08`), so nothing ever matched.
It was caught by deliberately touching a file and confirming the check complained. The
same class of vacuous pass has now bitten this project three times: `check_urls.sh`
reporting PASS having checked nothing, `check_repo.py` skipping section checks, and this.

**A generator that was run once instead of always.** `normalize_pages.py` was run as a
one-off batch, then more pages were fetched, and every new page reintroduced raw HTML
tables that the pipe-table parser silently skips. That is how
`oauth.v2.FailedToResolveAPIKey` went missing from the generated reference while REG-06
cited it correctly. `fetch.sh` now normalises on every fetch. A batch step someone has to
remember is not a pipeline step.

**An over-escaped regex** in `make_packets.py` duplicated the scenario ID in all 105
prompt titles.

## Round 4, the fixes for round 3

All four material errors from round 3 were fixed, plus nine minors.

The MED fixes were the ones that mattered most, because they were grading-integrity bugs
rather than scenario bugs. All 22 MED answer keys were missing their critical-failure
conditions, which meant a MED response tripping one could still have been scored as a pass.
The library graded itself more leniently than intended, in one third of its files, and no
summary statistic showed it. The extractor now finds critical failures in all three shapes
the library uses: a heading, bold text under the rubric, and a sibling heading with the
conditions inline. All 72 keys carry them, and the harness fails if any does not.

MED-09's key recommended `<Rate>`-shaped configuration using two elements that do not
exist. A grader treats the key as authoritative, so a fabrication sitting in the key is
worse than one in a scenario, because it is the answer the grader is checking against. The
rewrite also revealed that SpikeArrest has no window element at all: the `ps` or `pm` suffix
inside `<Rate>` IS the window control, which is a better answer than the invented
`timeWindow` was.

EASY-09 turned out to be an inversion. Its cause, a variable that does not exist, is
verbatim the documented trigger for a different fault code than the one it handed over, so
a respondent saying "this code does not match this evidence" was correct and would have
been marked down. Re-picking the code also surfaced a second defect: the variable it blamed
never existed, which would have failed every request and contradicted the ticket's "works
for most".

## Where the number stands

Measured by blind review, after fixes:

| Pass | Scenarios | Material errors | Clean |
| --- | --- | --- | --- |
| Round 1, first review | 63 | 18 | 71.4% |
| Round 3, easy + medium | 37 | 2 | 94.6% |
| Round 3, hard + adv + reg | 35 | 2 | 94.3% |
| **Round 3 combined** | **72** | **4** | **94.4%** |

The target was 90%. It is met on the combined figure, and on each half separately.

Those four were fixed afterwards, so 94.4% is a floor rather than a current reading. The
honest statement is: at least 94.4% of scenarios are free of material errors under blind
review, and a confirmation pass over the nine scenarios changed since that measurement is
recorded in `confirm-pass.md`.

## What the number does not mean

It means no known material error survived a blind review pass. It does not mean the
scenarios are correct.

Every reviewer worked from the same local cache the fixers used, one reviewer per half, no
second opinion, and no adjudicator. A reviewer sharing a source with the fixer can inherit
the same blind spot, and every error class found in round 1 was found again in round 2,
which suggests these passes catch a lot but are not exhaustive.

More to the point, no pass can tell whether the best answer is the one encoded. A scenario
can be factually flawless, internally consistent, fully sourced, and still reward a weaker
line of reasoning than the one an expert would take. Only running it against real
respondents measures that, and the one evaluation run in `results/RUNS.md` is far too small
to say.

So the honest summary is two separate claims, and they should not be merged:

**94.4% of scenarios are internally and factually sound under blind review.**

**Nothing has been established about whether answering any of them is easier with the
skills than without.**
