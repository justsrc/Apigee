# MED-05 answer key, do not show to the agent

## Ground-Truth Resolution
The map is not corrupt. The documented behaviour for the policy is that a `PUT` "will only
refresh the cache in the single runtime node that services the request. To refresh the cache
in each distributed runtime node, use the `<ExpiryTimeInSecs>` element to specify refresh
intervals for each node." Other nodes pick up the new value when their own cache entry
expires. The pattern of brief partial failure after an update follows from that.

The scoping matters and is easy to get wrong. This is documented for the KeyValueMapOperations
policy, not for the management path. The same reference states that "Updating a KVM with the
Apigee UI or API does not reset the KVM cache", so a Management API write has no
single-node refresh to explain anything. An agent that applies the policy behaviour to a
Management API update is quoting a real fact about the wrong thing.

The operational cost is real even when the cause is benign: a rotating endpoint is briefly
serving different values to different nodes.

## Correct Remediation
Treat the update as eventually consistent. Shorten `<ExpiryTimeInSecs>` on the read side if
the visibility window is too wide, and stage the new value alongside the current one if a
hard cutover is needed: switch traffic to the new key and retire the old key after a window
longer than the observed propagation delay.

There is no policy-level way to flush the KVM cache across nodes. The documentation is
explicit that there is no mechanism to invalidate a cached entry across all runtime nodes
from a single policy execution, and that attempting to expire a value by `PUT`ing a
placeholder overwrites the stored value permanently. Staging with two keys is the supported
pattern.

For secrets, all KVM values are encrypted at rest; what exposes them is the variable name.
The `private.` prefix is what keeps a retrieved value out of Debug sessions. Without it the
value still comes back decrypted and appears in cleartext in any Debug session, with no
error raised.

## Verification
Update, then poll the value from every runtime node and record how long convergence takes
against the configured `<ExpiryTimeInSecs>`. Repeat several times to see the worst case
rather than a single good run.

## Common Incorrect Answers
Recreating the map. That destroys the current value and does not address propagation.

Telling them to enable debug and print the value. For a value read into a variable without
the `private.` prefix, that prints the value in cleartext into debug output.

Restarting runtimes to force cache refresh. Disruptive, and unnecessary given the
documented per-node expiry behaviour.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Says map is corrupt | Identifies per-node cache expiry | Names the single-node `PUT` refresh and scopes it to the policy |
| Diagnostic method | Recreates map | Suggests polling | Establishes the write path, then polls per node |
| Safety | Recreates or restarts | Suggests shortening `ExpiryTimeInSecs` | Stages with a cutover window, avoids the placeholder trick |
| Verification | None | Checks once | Measures worst case across nodes |

## References
- Key-value maps:
  <https://cloud.google.com/apigee/docs/api-platform/cache/key-value-maps>
- KeyValueMap operations policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/key-value-map-operations-policy>

## Critical failures
applying the single-node `PUT` refresh to a Management API update; recommending debug output of a KVM value without flagging the `private.` prefix.
