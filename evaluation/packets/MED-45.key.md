# MED-45 answer key, do not show to the agent

## Ground-Truth Resolution
In Apigee version 1-17-0-apigee-1, a Netty upgrade to 4.1.129.Final introduced a regression. This
can cause API proxy calls to fail with a `400` status code and the error message `The URI contain
illegal characters`. It is tracked externally as netty/netty#16020.

The register quotes the string as `The URI contain illegal characters`, without the `s`. An agent
that silently corrects the grammar will fail an exact-match evaluation, so the string should be
quoted as it stands.

This is a bug, not a limitation, and it is fixed in the immediately following release. The
misdiagnosis risk is what makes it a medium scenario rather than a trivia question: a 400 with a
message about illegal URI characters points the engineer at the request, and the request is the
one thing that did not change. Chasing base paths, target URLs and header encoding is
well-reasoned and entirely wasted.

## Correct Remediation
Upgrade the org to Apigee 1-17-0-apigee-2. No proxy change is required and none should be made.

## Verification
Confirm successful calls on a sample of the previously failing requests, then confirm the
unaffected traffic did not change behaviour, since the fix is in the shared runtime.

## Common Incorrect Answers
Asking the customer to URL-encode a path segment. The URIs are valid and the platform broke.

Recommending a change to base paths or target endpoints. Any change here is a real client-visible
regression introduced while chasing a platform defect.

Recommending quoting the error as `The URI contains illegal characters`. It is the grammatical
form that does not appear.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Advises URL encoding | Identifies a runtime regression | Names the Netty 4.1.129.Final upgrade and 1-17-0-apigee-2 |
| Diagnostic method | Audits base paths | Checks the version | Checks the version against the single affected release |
| Error handling | Paraphrases the string | Quotes it correctly | Quotes `The URI contain illegal characters` verbatim and recognises it as client-side framing |
| Quality of next step | Changes proxy URLs | Recommends an upgrade | Recommends upgrading to 1-17-0-apigee-2 with no proxy change |

## References
- Known issues register (entry 480997525):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Upstream issue: <https://github.com/netty/netty/issues/16020>

## Critical failures
recommending a proxy or URL change; telling the customer their request is malformed.
