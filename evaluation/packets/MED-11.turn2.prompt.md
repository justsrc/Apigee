You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-11

The customer has replied with more information.

## Diagnostic Evidence
A key-value map lookup differs, and the difference is an absent key rather than a
differing value: `prod` has no `orders.timeout` key at all, while `test` has it set to
`30`. The policy is the same in both environments:

```xml
<KeyValueMapOperations name="GetOrdersTimeout" mapIdentifier="orders-config">
  <Get assignTo="private.orders.timeout" index="1">
    <Key>
      <Parameter>orders.timeout</Parameter>
    </Key>
  </Get>
  <Scope>environment</Scope>
</KeyValueMapOperations>
```

A JavaScript policy reads `private.orders.timeout` and sets the target request timeout from
it. In `test` the lookup returns `30` and the timeout is set. In `prod` there is nothing to
retrieve, so nothing is assigned to the `assignTo` variable, and the script is left holding
no timeout value, which is what produces the 500.
