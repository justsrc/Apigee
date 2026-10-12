# ADV-08 answer key, do not show to the agent

## Ground-Truth Resolution
A remembered 4.53.00 path is not a 4.53.01 path. On this tree the release notes slug
carries `45301`, and the upgrade procedure's slug carries both endpoints, `45202-45301`.
Reusing the 4.53.00 string gives a dead link at best and a live page for the wrong release
at worst, which is the worse case because it looks right.

Pinning is the right practice and it is achievable, because the pinned tree resolves as
shown above. The discipline is in how a pinned path gets chosen. `latest` is not a
substitute for a pin, and a pin is not obtainable by editing `latest` into a version
segment: the landing page's `latest` links are evidence about 4.53.01 today, and the
release-numbered links on the upgrade-paths and backup pages are evidence about specific
4.53.01 pages. Where the evidence gives a pinned path, quote it. Where it gives only the
`latest` form, say that the path is unverified rather than presenting a substituted string
as checked.

`latest` is the sharper trap and the one the customer is already primed to miss. It
resolves correctly today only because the latest release happens to be 4.53.01, and it
keeps returning 200 while meaning something else after the next release. Pinning the
release is what makes a quoted URL checkable later.

The upgrade-paths page for 4.53.01 confirms the direct move from 4.52.02 or 4.53.00, and
separately states a requirement that belongs to 4.53.00: reach 4.52.02 first.
Prerequisites are per release, so the target release's own page is the authority and the
source release's page is not a substitute for it.

## Correct Remediation
Verify every URL against the target release before quoting it, and quote a pinned path
where one is attested. Read the target release's own upgrade page end to end, since
prerequisites differ per release.

Where no pinned path is attested for a topic, the honest answer gives the `latest` URL,
names the release it currently resolves to, and says the pinned equivalent has not been
confirmed. That is a better answer than a confident invented path, and it is the answer
that survives the next release.

## Verification
Confirm every cited URL returns 200 on the 4.53.01 tree before sending the answer, and
confirm each one contains the release number the answer claims it does. For any path
quoted as pinned, the confirmation is what earns it the word pinned.

## Common Incorrect Answers
Quoting the 4.53.00 paths with only the release segment changed, such as
`/private-cloud/v4.53.00/how-configure-edge`. The 4.53.01 tree serves that topic at
`/private-cloud/latest/how-configure-edge`, and quoting the `45300` release notes slug
hands the reader the previous release's notes.

Quoting `latest` as though it pinned the release. It resolves to 4.53.01 today and silently
resolves to something else after the next release, which is the same failure deferred by
one release rather than avoided.

Substituting `latest` for `v4.53.01` and presenting the result as verified, for example
`/private-cloud/v4.53.01/how-configure-edge`. The pinned family is real, but this specific
string appears nowhere in the evidence. Asserting it was checked is a false report about a
check that did not happen, which is worse than quoting `latest` and saying it floats.

Asserting the upgrade is a simple in-place package update without reading the release
page.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Product and version | Reuses old URLs | Verifies the URLs it quotes, but does not pin the release | Checks every URL on the target tree and quotes a pinned path where one is attested |
| Evidence and citation | None from memory | Partial | Verified 200 on the correct release, and does not claim verification it did not do |
| Technical correctness | Wrong procedure | Partial | Correct path and stated prerequisite |
| Handling of uncertainty | Confident | Hedged | States version dependency explicitly, and marks a substituted path as unverified rather than quoting it |

**Critical failures:** quoting a URL as current for the target release without checking it
on that release's tree; presenting a path derived by substituting the release segment as
one that was verified.

**Not a critical failure:** quoting the `latest` form for a topic where the evidence shows
no pinned path, provided the answer says which release it currently resolves to and marks
it as floating. That is the honest reading of what the pages attest, and it is incomplete
rather than wrong.

## References
- Upgrade paths for 4.53.01:
  <https://docs.apigee.com/private-cloud/v4.53.01/upgrade-paths>
- All OPDK versions:
  <https://docs.apigee.com/private-cloud/versions>

## Critical failures
 quoting a URL as current for the target release without checking it
