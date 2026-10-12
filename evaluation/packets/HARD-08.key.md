# HARD-08 answer key, do not show to the agent

## Ground-Truth Resolution
The counter is not double counting and it is not buggy. It counts what it is asked to
count, accurately. Three facts are being conflated and all three have to be held apart.

First, `<MessageWeight>` makes the limit an expression in weighted units rather than in
requests. That alone accounts for most of the 10,000: 5,000 x 1 + 2,000 x 2 = 9,000 units
consumed by 7,000 requests.

Second, there is one counter and not two. Apigee documents that a Quota policy referenced
in multiple places in a proxy maintains a single counter updated by all instances of the
policy. That sentence does not say one increment per request. The worked example beside it
increments once per policy execution, so a single request that traverses two placements
moves the one counter twice.

Third, and this is where the ticket's claim fails, this request path does not traverse both
placements. The PreFlow attachment is conditional, so only the 1,000 enterprise requests
are counted twice. That contributes 1,000 units, and 9,000 + 1,000 = 10,000, the configured
limit. The arithmetic rejects both shortcuts: treating every request as counted twice gives
18,000, and ignoring the second attachment entirely gives 9,000.

So the duplicate attachment is a real finding and it is not the main one. It is 1,000 of the
10,000 units. It is still worth fixing, both because the documentation calls the pattern an
antipattern and because a policy that looks as though it is enforced twice invites precisely
this question again. Removing it moves the threshold by 1,000 units for enterprise traffic
and does not return it to 7,000 requests, because MessageWeight still accounts for 9,000 of
the units.

What remains open is which unit the API product's quota is denominated in, and whether the
condition on the PreFlow attachment is deliberate or a leftover. The first is a question
for the owner of the API product, the second for whoever wrote the proxy, and the proxy
cannot settle either.

## Correct Remediation
Decide whether the limit is meant to be per request or per unit. If per request, remove
the `<MessageWeight>` binding. If per unit, restate the limit and correct the ticket,
because the current 10,000 is not 10,000 requests. Do not scale the number to match the
observation until that decision is made, because the two errors cancel for exactly one
window and then diverge.

Separately, remove the duplicate attachment or narrow it, and do that in its own revision.
Both are real cleanups and only one of them moves this threshold, so bundling them means
the verification cannot attribute the change in the counter.

Deploy to `test`, replay a known mix of weight-1 and weight-2 requests with and without
`x-tier`, and confirm the counter advances by the expected unit total before applying to
production.

## Verification
Send a known number of requests of each weight, with and without `x-tier`, and confirm the
counter increments by the weighted total per execution. Confirm the rejection threshold
lands on the configured limit expressed in the agreed unit, and confirm it separately for
an enterprise request and a non-enterprise request.

## Common Incorrect Answers
Raising the limit to 20,000. That absorbs the discrepancy for this window without deciding
which unit the limit means.

Switching to asynchronous counters. That changes freshness, not the unit of account.

Concluding the counter is buggy. It counts what it is asked to count, accurately.

Accepting the ticket's double-counting story because the policy is attached twice. The
documented behavior is a single counter updated per execution, and on this request path
only the conditional attachment runs twice, contributing 1,000 of the 10,000 units.

Counting every request twice. That gives 18,000 and does not match the counter that was
actually read.

Removing the second attachment and expecting the threshold to return to 7,000 requests.
MessageWeight still accounts for 9,000 of the units.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Raises the limit to compensate | Finds `<MessageWeight>` and states the limit is a unit count | Closes the arithmetic to 10,000 from the weight mix and the conditional second execution |
| Handling of competing explanations | Asserts double counting from the two attachments alone | Notices that weight and placement are both in play | Rejects the blanket double-counting claim, finds the condition on the second attachment, and attributes each contribution separately |
| Diagnostic method | Trusts the ticket | Reads the policy and replays one request | Replays one request of each kind, gets two different increments, and accounts for the mix |
| Quality of next step | Raises the limit | Removes the duplicate policy | Settles the unit of account first, then changes one thing and tests it |

**Critical failures:** raising the limit to compensate without settling whether the limit is
per request or per unit; asserting that the two attachments alone explain the 7,000, or
that the counter is double counting as a blanket claim.

**Not a critical failure:** naming the duplicate attachment as a contributing factor,
conditioned or not. It is a real finding and it is worth 1,000 of the units. What fails is
asserting it as the whole explanation, which is the ticket's claim and which the arithmetic
contradicts.

## References
- Quota policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
- Flow configuration reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/flow-configuration-reference>
- Introduction to antipatterns:
  <https://cloud.google.com/apigee/docs/api-platform/antipatterns/intro>

## Critical failures
 raising the limit to compensate without settling whether the limit is
