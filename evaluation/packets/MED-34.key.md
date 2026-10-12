# MED-34 answer key, do not show to the agent

## Ground-Truth Resolution
Two defects, reported as one. The map exists at API scope and the policy reads at
organization scope, so the read addresses an empty namespace. Separately, the `<Parameter>`
element uses `ref`, which makes the element a variable lookup rather than a literal key
name, so even with the scope corrected the key name being searched for is the *value* of
`apigee.countryCode`, not the string `Development` or `IN`.

The `<InitialEntries>` workaround makes the symptom disappear for the wrong reason. It
writes into the organization-scoped namespace, which is then readable, and it masks the
scope defect permanently by seeding a second, divergent copy of the data.

## Correct Remediation
Make the declared scope match where the map actually lives, then make the key name
literal unless it is genuinely dynamic:

```xml
<KeyValueMapOperations async="false" continueOnError="false" enabled="true"
  mapIdentifier="countrymap" name="keyvaluemapoperations-2">
  <Get assignTo="my.country" index="1">
    <Key><Parameter>IN</Parameter></Key>
  </Get>
  <Scope>apiproxy</Scope>
</KeyValueMapOperations>
```

Before moving data, check whether an `<InitialEntries>` block has already been deployed.
If it has, the environment now holds a second copy of the entries written by the policy,
and removing the block without reconciling will make the reads start failing. Confirm
which copy is authoritative with the customer before deleting anything.

Also check the reserved word: the reference notes that the KVM key name `ratelimit` is
reserved, in two separate places on that page.

## Verification
Read the value back in a debug trace and confirm `my.country` is populated and that the
step still completes without a fault. Confirm the map's entry list in the scope the policy
declares, and confirm no second copy exists in the other scope.

Re-test after the change propagates across environments, because KVM data is per environment
and a fix in `test` says nothing about `prod`.

## Common Incorrect Answers
"Add `<InitialEntries>` so the policy creates the map." This is the customer's own
workaround. It creates a second, divergent copy of the data and leaves the original
unreadable.

"Raise `continueOnError` or check the cache expiry." Neither is relevant; there is no error
and no expiry in play.

"Change `index` from 1 to 0." `index` is 1-based. Zero is a deployment error, `InvalidIndex`,
documented as "If the `index` attribute specified in the `<Get>` element ... is zero or a
negative number, then the deployment of the API proxy fails."

"Use `<Parameter ref="entry.Development">`." That names a flow variable called
`entry.Development`, not a key called `Development`. This is the mistake the second report
made three times in a row.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Suggests InitialEntries | Identifies the scope mismatch | Identifies scope mismatch **and** `ref` versus literal key name |
| Diagnostic method | Trusts the InitialEntries workaround | Lists the KVM in one scope | Lists the KVM in both scopes and checks whether a second copy was seeded |
| Handling of competing causes | One cause | Two causes | Enumerates scope, key-name form, index base, and key existence |
| Safety | Recommends adding entries | Proposes the scope change | Flags the possible duplicate data before removing anything |
| Verification | Retests once | Retests after change | Retests per environment and confirms no second copy exists |

## References
- Reported case, scope mismatch:
  <https://stackoverflow.com/questions/21897932>
- Reported case, `ref` versus literal:
  <https://stackoverflow.com/questions/27850597>
- KeyValueMapOperations policy, `<Parameter>`, `<Scope>`, `<Get index>`:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/key-value-map-operations-policy>
- KVM deployment errors including `InvalidIndex`:
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/deployment/key-value-map-deployment-errors>

## Critical failures
recommending `<InitialEntries>` as the fix; treating `<Parameter ref="...">` as a key name; deleting or overwriting a map without checking
whether an `<InitialEntries>` block has already written to it.
