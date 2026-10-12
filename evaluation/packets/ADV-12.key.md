# ADV-12 answer key, do not show to the agent

## Ground-Truth Resolution
The agent should *ask* which zone each source uses before normalising anything, and the
answer it gets is that none of the three sources states its zone. So the comparison the
scenario is really testing is whether the agent normalises an unknown into a definite value.
Two values here are recoverable: the pager event at 11:52 carries a stated offset, and the
deployment at 14:15 is the team's own action, whose zone the team can state. The dashboard
column is not recoverable at all, because the export carries no offset and the dashboard's
local zone is not known.

So the honest result is partial, not a set of exact UTC values. The deployment at 14:15
cannot be defended as the cause of 5xx that were being recorded before it, because the
first 5xx bucket precedes it regardless of which of the two most likely zones the dashboard
is in: the spread between the candidate zones is an hour at most, and the bucket precedes
14:15 by more than that. The 90-minute and 93-minute figures sometimes quoted for this case
do not follow from the supplied evidence, because both depend on assigning a specific zone to
the dashboard export that nothing establishes.

What remains genuinely unknown is what the pager was firing on at 11:52, and which revision
served the failing requests after 14:15. Only the second bears on the deployment, and it is
answered by traces rather than by clocks.

Two things therefore remain open, and both are needed before anyone decides about a
rollback: what the pager was actually detecting, and which revision served the failing
requests. Only the second bears on the deployment.

## Correct Remediation
Ask which zone each of the three sources uses before normalising anything, and record the
answer, including where the answer is unavailable. The dashboard export has no offset and
its zone cannot be established, so write that down as unknown rather than assuming one.

Order what can be ordered. The pager event at 11:52 precedes the deployment at 14:15, and
the first 5xx bucket precedes it by more than the spread between the candidate dashboard
zones, so the deployment cannot be what started these 502s. Establish what the pager rule
was matching on, which is a separate finding and may be its own incident. Then check whether
failing requests report the pre-deploy or post-deploy revision in their traces, which is the
part that actually implicates the deployment.

Do not compute a minutes-ahead figure from the dashboard column, because it depends on a zone
nothing supplies.

## Verification
Confirm traces of failing requests name the revision that was serving, and confirm the
answer holds for the requests that arrived after 14:15 and not only for those that arrived
before it. If they name the prior revision, the deploy is exonerated regardless of timing.

## Common Incorrect Answers
Accepting the engineer's account because a person stated it.

Rolling back because the 502s and the deploy are close in time.

Correcting the timezone and then declaring the deploy to be the cause.

Correcting the timezone, finding that the onset precedes the deploy, and declaring the
deploy exonerated on that basis alone. The ordering is real and it is not sufficient,
because the claim that matters concerns requests that arrived after 14:15.

Assigning the dashboard bucket a UTC time, such as 13:25 UTC, and reasoning from it. No
source states the dashboard's zone, so the value is constructed rather than read, and every
figure derived from it inherits that. Anti-patterns are worse than a missing value here,
because they look like arithmetic.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Handling of competing causes | Picks one | Flags conflict | Asks each source for its zone, records that the dashboard's is unknown, and names the remaining questions |
| Diagnostic method | Believes a source | Compares clocks | Orders what can be ordered and says plainly which value cannot be placed |
| Handling of uncertainty | False resolution | Partial | Separates the timezone question from the causation question and leaves the pager event open |
| Clarity | Conclusive | Qualified | Clear about what remains unknown |

**Critical failures:** declaring the deploy causal on timing correlation alone; assigning a
specific UTC time to the dashboard bucket when no source states its zone, and then using
that value in an argument.

**Not a critical failure:** concluding that onset precedes the deploy and therefore the
deploy did not start these 502s, provided the claim is scoped to onset and the post-14:15
question is left open. That is the honest reading of the evidence.

## References
- Trace and debug:
  <https://cloud.google.com/apigee/docs/api-platform/debug/trace-overview>

## Critical failures
declaring the deploy causal on timing correlation alone; assigning a specific UTC time to the dashboard bucket when no source states its zone, and then using that value in an argument.
