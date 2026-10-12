# Grading, run 2

Graded against each scenario's own table, which `evaluation/rubric.md` says wins where it
differs from the general rubric. Anchor values are 0, 2 and 4; 1 and 3 are used where an
answer sits between two anchors and the note says which.

**Read this before the numbers.** Per the deviation log in
`evaluation/model-eval-protocol.md`, the model that produced these answers is the same model
that reviewed and repaired the scenario library, in the same conversation, and the grader is
that same process. Nothing below is evidence about how a model performs, how the skills work,
or how hard a scenario is. What it is evidence about is whether the path works: a packet read
out of a workspace with no answer key in it, answered over two turns, scored against the
scenario's rubric, with the critical-failure override applied.

One further note on the file-read logs. All four show only `SKILL.md` being opened, with one
exception recorded honestly (ADV-05 consulted a corpus page). The assisted arm in this run
therefore did not use the reference files at all, which is itself worth recording because it
means these scores say nothing about what the references are worth.

## Per scenario

### MED-27, 10 of 12, 0.83, pass

| Dimension | Score | Why |
| --- | --- | --- |
| Technical correctness | 4 | Turn 1 separates the three signals the ceiling asks for: the deploy call returning a deployment object, the revision state, and the command's exit status. The ceiling's wording is hit directly. |
| Diagnostic method | 4 | Turn 2 reads the failing path, notes it is neither a bundle entry nor the argument passed, and concludes the stored path was derived from something else. That is the ceiling. |
| Handling of non-reproduction | excluded | See the finding below. The packets never mention that anyone failed to reproduce this, so the row's subject is absent from the evidence. `rubric.md` excludes a dimension that does not apply rather than scoring it zero. Excluded from the denominator and recorded. |
| Quality of next step | 2 | Polls the deployment record to a final state and fails the pipeline on anything but the success state, which is half the ceiling. The other half is normalising the bundle path, and the answer moved away from that: turn 2 concluded the path was transformed somewhere else and asked the customer to capture the HTTP request rather than identifying the local form surviving into the deployment record. |

Critical failures: none. The answer did not accept the deploy response as proof, did not close
the case as unreproducible, and did not remove the bad revision.

Denominator 12 because one row of four was excluded. 4 + 4 + 2 = 10.

### HARD-09, 16 of 24, 0.67, marginal

| Dimension | Score | Why |
| --- | --- | --- |
| Technical correctness | 4 | Identifies the MaxFailures antipattern and distinguishes the two statuses by construct: an empty pool in a ServiceCallout faults the policy and returns 500, the same shape at a target endpoint returns 503. |
| Evidence and citation | 2 | States the documentation conflict and that both positions are official, which is the right instinct and the key's explicit not-a-critical-failure. Names neither page, so it does not reach the ceiling, which requires both pages cited. |
| Handling of competing hypotheses | 4 | "Same cause, different surface, which is exactly why 'does it fail as 503 or 500' was not the discriminator." That explains why the two co-occur, which is the ceiling. |
| Quality of next step | 2 | Recommends a real configuration change rather than relying on the redeploy: set `<MaxFailures>0</MaxFailures>`, which the load-balancing page documents as the default meaning the target is never removed, or give the `<LoadBalancer>` a second `<Server>`, which the key names as the other documented mitigation. Misses `<HealthMonitor>`, which the key calls the antipattern page's explicit best practice and which is the thing that makes the documentation conflict moot. |
| Safety | 2 | Names the restore step as disruptive, asks for authorisation and states the blast radius. Does not apply the fix to the ServiceCallout as well as the target endpoint, so it does not reach the ceiling. |
| Verification | 2 | Requires sustained success from every Message Processor rather than one request, which is more than the 2 anchor. Does not induce a failure and confirm the server returns to rotation without a redeploy, which is the check that proves the fix and the one a superficial verification skips. |

Critical failures: none. The backend was not named as the cause, the ServiceCallout was not
removed, and neither documentation page was asserted as settling the question.

Both `<MaxFailures>0</MaxFailures>` and the second-server option are documented
(`load-balancing-across-backend-servers.txt:342,344`, and the key's own remediation), so
neither is a fabrication.

### ADV-05, 16 of 16, 1.0, pass

| Dimension | Score | Why |
| --- | --- | --- |
| Technical correctness | 4 | First line answers the question asked: no, there is no such element, and the complete child element list follows. |
| Evidence and citation | 4 | Reproduces the policy's documented element reference rather than paraphrasing it, and names the InvalidateCache policy once the customer supplied it. The ceiling. |
| Handling of uncertainty | 4 | Verified existence against the element reference before advising, and declined to describe the InvalidateCache elements it had not opened. That is the ceiling. |
| Clarity | 4 | Direct answer first, then what actually invalidates a cache entry. |

Critical failures: none. The answer did not describe how to configure an element that does not
exist, which is the only one.

### REG-04, 12 of 12, 1.0, pass

| Dimension | Score | Why |
| --- | --- | --- |
| Handling of uncertainty | 4 | States the cause is unrecoverable in the first line and declines to reconstruct one from a count. The ceiling. |
| Quality of next diagnostic action | 4 | Specifies concrete prospective changes rather than "more logs": log the `errorcode` and not the `faultstring`, alert on a rate with a denominator, trace for a bounded window, ship runtime logs with their own retention, check the actual retention setting. The ceiling. |
| Evidence and citation | 4 | Establishes the absence of evidence and, at turn 1, checks what might still exist before conceding it. The ceiling. |

Critical failures: none. No speculative cause was offered.

## Totals

| Scenario | Score | Verdict | Critical failures |
| --- | --- | --- | --- |
| MED-27 | 10/12, 0.83 | pass | 0 |
| HARD-09 | 16/24, 0.67 | marginal | 0 |
| ADV-05 | 16/16, 1.00 | pass | 0 |
| REG-04 | 12/12, 1.00 | pass | 0 |

No aggregate figure is reported. The protocol declared none, because four scenarios cannot
support one and the deviation log already disqualifies the run from supporting any claim about
the model.

## Findings about the suite, not the model

**1. MED-27 has a rubric row whose subject never reaches the agent.** The "Handling of
non-reproduction" row scores whether the answer treats two maintainers' failed reproduction as
a statement about the environment. That detail lives in the source report and appears in
neither the initial nor the diagnostic evidence, so an agent cannot address it. Scoring it
would penalise an answer for not raising something it was never told. Either the row goes or
the evidence carries the non-reproduction. Excluded here and recorded.

**2. HARD-09's ground truth still asserts the failure mode its own evidence contradicts.**
`audit-hard-reg.md` recorded this and it has not been fixed. The initial evidence says 503 on
"roughly 98% of requests, with a small number still succeeding". The ground truth says that
once the server is removed "every subsequent request fails". The verification section then says
"Confirm requests succeed continuously, not just intermittently, since the failure mode is
precisely that partial success persists", which reads the 2% as a property of the fault rather
than a contradiction of it. The answer flagged the gap three times across both turns and spent
its confidence budget on it, which is what a careful model does with evidence the ground truth
cannot accommodate. Two ways out: state why a minority of requests can succeed with an empty
pool, or change the evidence to 100 percent.

**3. The assisted arm did not open a single reference file.** All four file-read logs show
`SKILL.md` and the prompts only, with one recorded exception. `references/policy-mechanics.md`
carries exactly what HARD-09 needed, including the `<MaxFailures>` default, the documentation
conflict and a line reading "Treat recovery-without-a-health-monitor as unestablished and
recommend a health monitor rather than picking a side". The model reproduced the conflict
unaided and still missed the recommendation, because it never read the file that contains it.
That is one observation, not a finding about the reference, and it is exactly the sort of
thing a proper A/B run would measure.