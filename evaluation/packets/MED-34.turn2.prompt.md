You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-34: A key value map read returns nothing, and the policy reports no error

The customer has replied with more information.

## Diagnostic Evidence
Listing the KVM at the API scope returns the map with entries. Listing it at organization
scope returns 404. The trace shows `apigee.countryCode` resolving to a value, for example
`IN`, while the map contains keys named `IN` only in the API-scoped map, and the
organization-scoped policy is reading from a namespace where nothing was ever written.

Separately, in the second variant of this report the map and the scope are both correct,
and the defect is:

```xml
<Key><Parameter ref="k1"></Parameter></Key>   <!-- resolves flow variable k1, then looks up its VALUE as a key name -->
<Key><Parameter>k1</Parameter></Key>           <!-- uses the literal string "k1" as the key name -->
```

The reference states that `ref` means "the name of a variable whose value contains the
exact name of the key you want to create, get, or delete", and that the attribute is
"Required if no literal value is given between the opening and closing tags."
