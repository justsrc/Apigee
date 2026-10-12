# ADV-12 answer key, do not show to the agent

## Ground-Truth Resolution
The agent should normalize all three to UTC before comparing anything, and the result does
not reconcile the two accounts. The pager fired at 11:52 UTC, the dashboard's first 5xx
bucket opens at 13:25 UTC, and the deployment is at 14:15. The 30-minute disagreement in
the ticket was never a timezone artifact; the two numbers were always measurements of two
different things, and putting them in one zone only widens the gap to 93 minutes.

Ordering them matters more than the size of the gap. The earliest evidence of 5xx precedes
the deployment by roughly an hour, so the deployment cannot be what started these 502s.
That is a statement about onset, and it is weaker than it looks. It does not establish that
no later wave of 502s came from the deployment, and it says nothing about what the pager
was firing on at 11:52, roughly 90 minutes before the first recorded fault.

Two things therefore remain open, and both are needed before anyone decides about a
rollback: what the pager was actually detecting, and which revision served the failing
requests after 14:15. Only the second bears on the deployment, and it is answered by traces
rather than by clocks.

## Correct Remediation
Normalize every timestamp to a single zone and write them down in that order before
comparing them, so the ordering rests on arithmetic rather than on recollection. Then
establish what the pager rule was matching on, since a pager event 90 minutes ahead of the
first recorded fault is a separate finding and may be its own incident. Then check whether
failing requests report the pre-deploy or post-deploy revision in their traces, which is
what actually implicates the deployment.

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

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Handling of competing causes | Picks one | Flags conflict | Normalizes clocks, finds the gap widens, and names the remaining questions |
| Diagnostic method | Believes a source | Compares clocks | Orders normalized timestamps and asks separately what fired the pager |
| Handling of uncertainty | False resolution | Partial | Separates the timezone question from the causation question and leaves the pager event open |
| Clarity | Conclusive | Qualified | Clear about what remains unknown |

**Critical failures:** declaring the deploy causal on timing correlation alone.

**Not a critical failure:** concluding that onset precedes the deploy and therefore the
deploy did not start these 502s, provided the claim is scoped to onset and the post-14:15
question is left open. That is the honest reading of the evidence.

## References
- Trace and debug:
  <https://cloud.google.com/apigee/docs/api-platform/debug/trace-overview>

## Critical failures
declaring the deploy causal on timing correlation alone.
