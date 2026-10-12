# MED-42 answer key, do not show to the agent

## Ground-Truth Resolution
Two limitations are in play, both documented and both now closed.

First, attempting to deploy more than 800 proxies to an environment group fails with an error, and
the register adds the detail that actually matters: the limit at which an error is returned is
lower than 800 when the base paths are longer than 15 characters. Proxy count is therefore
necessary but not sufficient. Base path length is the second factor, and it is invisible in the
error the customer receives, which reports only that an error occurred.

Second, there is a limit of 1000 base paths per environment. The register is explicit that this
counts base paths and not revisions: "If your API proxies or revisions contain more than one
base path, the total number of base paths per environment must not exceed 1000." A revision
carrying four base paths consumes four slots.

Both are limitations described as a deliberate protective measure. The 1000-basepath limit is
introduced in the register as a temporary limit "to avoid potential failures when deploying API
proxy revisions". The word temporary should be quoted rather than promised.

The two groups on the same org are both compliant with the numbers a support engineer would
naturally check, which is why the ticket exists.

## Correct Remediation
Shorten base paths on the failing group if the owning teams can tolerate the client-visible
change, or split the group. Either reduces the effective proxy count against the length-adjusted
ceiling. Separately, count total base paths per environment rather than counting revisions,
since that is what the environment-level limit measures.

## Verification
Deploy successfully to the failing group, then repeat the count across every environment in the
org, because the environment ceiling is per environment and a group split does not reset it.

## Common Incorrect Answers
Comparing only the proxy count between the two groups. Both are 604 and the counts are not the
discriminator.

Raising a quota, ticket or support request. These are documented design limits, not a
capacity entitlement that can be negotiated.

Recounting revisions instead of base paths. A revision with several base paths consumes several
slots against the 1000 ceiling.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Diagnostic method | Compares proxy counts only | Notices base path length | Identifies both the 15-character factor and the per-environment 1000 base path limit |
| Technical correctness | Says the org is full | Names the 800 proxy limit | Explains the length-adjusted threshold and base path counting |
| Cross-group reasoning | Assumes shared org means shared limit | Notes the groups differ | Uses base path length as the discriminator between the two groups |
| Quality of next step | Opens a quota request | Advises shortening paths | Splits the group or shortens paths, and recounts per environment |

## References
- Known issues register (entries 301845257 and 329304975):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Environment groups:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/environmentgroups-working-with>

## Critical failures
ruling the issue out after confirming both groups are under 800 proxies; counting revisions instead of base paths.
