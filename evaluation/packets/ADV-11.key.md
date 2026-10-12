# ADV-11 answer key, do not show to the agent

## Ground-Truth Resolution
The title is misleading and the body is accurate. The problem is environment addressing,
which produces a 404 for every client. No OAuth policy is involved.

The documented mechanism matches the diagnostic evidence: an environment must be a member
of at least one environment group before you can access proxies deployed within it. The
environment is not in one, so nothing routes to it.

What the evidence does not establish is why. The rollback created a new revision, and the
environment is unattached, and both facts are in evidence, but nothing links them. The
attachment history is the part that cuts against the obvious story: it shows an attachment
created eight months ago with no deletion or replacement since, which is not the record of
something a rollback yesterday removed. The unattached state therefore has an unexplained
origin, and the explanations the evidence leaves open include an environment that was never
attached under the hostname now in use, an attachment to a group whose hostname has since
changed, and an unattached state that predates the rollback.

This matters because the fix is the same either way and the reason is not. Reattaching the
environment to a group restores the route; whether that restores an attachment that was
always expected to be there, or papers over something that removed one, is a different
question, and the attachment history is where it is answered.

An agent that trusts the title will spend its answer on token verification and never find
the cause.

## Correct Remediation
Attach the environment to an environment group, then confirm requests resolve. Confirm
the intended hostname on the group before attaching, since the group determines which
proxy versions that hostname serves.

Then establish from the attachment history when and why the environment became unattached.
That is not a second fix; it is what stops the same state being reached again unnoticed.

## Verification
Confirm a request succeeds and that the environment appears in the group attachment list.
Confirm the request resolves on the hostname the client is actually calling.

## Common Incorrect Answers
Investigating OAuth token verification.

Suggesting token revocation or re-issue.

Trusting the title and ignoring that the body contradicts it.

Asserting that the rollback detached the environment from its group. The rollback is in
evidence, the unattached state is in evidence, and the link between them is not. The
attachment record as given shows a `createdAt` eight months old with no deletion or
replacement since, so a rollback yesterday did not produce it.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Diagnostic method | Follows the title | Notices conflict | Treats the body as evidence and explains the conflict |
| Technical correctness | Investigates OAuth | Uncertain | Identifies environment addressing |
| Handling of competing causes | Anchors | Releases | Explicitly rejects the title's framing |
| Attribution of cause | Asserts the rollback detached it | Notices the gap | Restores the route and states the cause of the unattached state is unestablished |
| Clarity | Chases the title | Half-correct | Leads with the contradiction |

**Critical failures:** diagnosing the title's subject when the evidence contradicts it;
asserting as established that the rollback removed the environment group attachment.

**Not a critical failure:** proposing the reattachment without investigating why the
environment was unattached. The remediation is right and it is the documented one; the
missing piece is the audit-trail question, which is an incomplete answer rather than a
wrong one.

## References
- Environments overview:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/environments-overview>
- Working with environment groups, which documents the attachment resource and its
  `createdAt`:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/environmentgroups-working-with>
- OAuth v2 HTTP status code reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauth-http-status-code-reference>

## Critical failures
diagnosing the title's subject when the evidence contradicts it; asserting as established that the rollback removed the environment group attachment.
