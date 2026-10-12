# MED-11 answer key, do not show to the agent

## Not A Critical Failure
finding, not a wrong answer. It becomes wrong only when it is turned into a claim that
both environments are broken, or that the difference alone proves a misconfiguration,
which is the opposite of what the evidence supports.

## Ground-Truth Resolution
The environments differ in a map entry that lives outside the bundle, so deploying the same
artifact to both produces different behavior. The bundle is not the variable.

The direction matters, and getting it backwards is the whole bug. `prod` is the failing
environment and `prod` is the one missing the key. A well-formed value cannot cause an
unresolved variable; a missing one does. `<Get>` documents itself as retrieving the value
for the key specified and assigning it to the `assignTo` variable, so with no entry for
`orders.timeout` in the production map, that variable is never assigned and the downstream
script reads nothing. In `test` the same policy retrieves `30` and the request succeeds.

The `<Scope>environment</Scope>` setting is why this is possible at all: entries are scoped
to an environment, so the two environments can hold different maps without anything being
mis-deployed. An identical bundle is not an identical environment.

This is the general shape of most "works in one environment" tickets: the proxy config is
deployed identically and something environment-scoped is not.

## Correct Remediation
Decide what production is supposed to do, because "add the key" and "stop depending on the
key" are both defensible and they are different changes. The first is to populate the map
entry in `prod` through a documented, repeatable mechanism rather than by hand, so the
value is visible in source control and survives the next deployment.

The second is often better: a default in the policy that handles a missing variable makes
the proxy behave the same in both environments whether or not the key is present, and it
removes a per-environment value that has to be kept in sync. Choose one deliberately
rather than letting the difference persist unnoticed.

If the map entry is left environment-scoped and missing, record that as a known difference
rather than an accident.

## Verification
Confirm the same request behaves identically in both environments. Then diff environment
configuration deliberately and record what differs, because there are usually more
differences than the one that broke.

## Common Incorrect Answers
Redeploying the production revision. The bundle is already identical.

Copying the `test` map into `prod` by hand. That fixes today and drifts tomorrow.

Reading the well-formed `30` as the problem because it is a string rather than an integer.
A value that is present and well-formed cannot leave a variable unresolved. The failing
environment is the one with no key at all.

Concluding that the environments must be identical, and therefore that one of them has
been mis-deployed. Nothing in the evidence says they are identical, and the whole
question is whether environment-scoped configuration is the variable.

Blaming the target or the runtime for a difference that is between two control-plane
configurations, neither of which is in the bundle.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Redeploys | Suspects env config | Identifies the missing map entry in the failing environment |
| Diagnostic method | Compares bundles | Compares env config | Diffs environment-scoped configuration and checks which key is absent |
| Quality of next step | Manual copy | Sets the value | Moves it into a managed configuration path or gives the policy a default |
| Verification | None | Retests | Retests and records remaining differences |

## References
- Key-value maps:
  <https://cloud.google.com/apigee/docs/api-platform/cache/key-value-maps>
- Environments overview:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/environments-overview>

## Critical failures
recommending repeated manual map edits as the durable fix; blaming the `30` value in `test` for the production failure.
