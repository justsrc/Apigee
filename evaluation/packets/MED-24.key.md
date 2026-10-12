# MED-24 answer key, do not show to the agent

## Ground-Truth Resolution
This is a regression in the linter, not a configuration error and not a product-version problem.
The lint message says the element is not allowed in the product. The documentation says the
element is allowed, `true` is a supported value, and is in fact the recommended one, and that the
restriction applies to the value `false` and to a specific hybrid production case. The message
overstates the rule, and an agent that trusts the message over the reference will delete a setting
the documentation tells you to keep.

The discriminating evidence is temporal, not textual. Nothing in the proxy changed and the
findings appeared on a linter release. That alone is enough to move the investigation to the tool.

## Correct Remediation
Upgrade the linter. The fix was released as v2.77.1 and confirmed working by the reporter in the
real case. Do not remove `UseEffectiveCount`, and do not change the rate.

If the linter cannot be upgraded immediately, exclude PO042 for the affected proxies rather than
editing bundles that are working. Read the element's value before concluding anything: `true` is
the supported and recommended setting, and it is `false` that the documentation rules out.

## Verification
Re-run the linter at v2.77.1 or later and confirm PO042 no longer fires on these policies. Then
confirm the rate limiting behaviour is unchanged at runtime, because the point of not editing the
bundle is that the bundle was never wrong.

## Common Incorrect Answers
Removing `UseEffectiveCount` because the lint message says it is not allowed. The documentation
recommends setting it to `true`, and removing it silently changes the algorithm from an effective
count to a smoothing algorithm.

Recommending an Apigee gateway upgrade or a product change. The gateway never changed and the
policies were already deployed and working.

Assuming the message is accurate about the product. Compare it with the policy reference before
acting on the element name.

Ignoring the version clue entirely and editing bundles until lint passes. That converts a tooling
regression into a set of permanent, unnecessary, behaviour-changing proxy edits.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Removes the element | Identifies a linter regression | Identifies the linter as the cause and cites the documented restriction on the value false |
| Diagnostic method | Edits the bundle | Asks what changed | Establishes the linter version boundary and that no proxy changed |
| Use of documentation | Repeats the lint message | Says the docs disagree | States what the reference actually restricts and why the message overstates it |
| Quality of next step | Removes the element | Upgrades the linter | Upgrades the linter, or excludes PO042 without editing working bundles |

## References
- Real report, with the v2.77.1 release and the reporter's confirmation:
  <https://github.com/apigee/apigeelint/issues/590>
- SpikeArrest policy reference, including the `UseEffectiveCount` element and its restriction:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy>
- Comparing Quota and SpikeArrest policies:
  <https://cloud.google.com/apigee/docs/api-platform/develop/comparing-quota-and-spike-arrest-policies>

## Critical failures
removing `UseEffectiveCount` from a working policy; proposing a gateway or product change when nothing on the gateway changed; repeating the lint message as if it were the
documented restriction.
