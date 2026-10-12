You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-34

## Initial Support Ticket
> We store a lookup table in a key value map and read it in the request flow. The variable we
> assign is always empty and the policy produces no error at all. The trace shows the step
> completing.
>
> We created the map through the management API using the API-scoped URL
> `/v1/o/{org}/apis/{api}/keyvaluemaps`, named `countrymap`. Our policy is:
>
> ```xml
> <KeyValueMapOperations async="false" continueOnError="false" enabled="true"
>   mapIdentifier="countrymap" name="keyvaluemapoperations-2">
>   <Get assignTo="my.country" index="1">
>     <Key><Parameter ref="apigee.countryCode"></Parameter></Key>
>   </Get>
>   <Scope>organization</Scope>
> </KeyValueMapOperations>
> ```
>
> One thing we noticed: if we add an `<InitialEntries>` block the same policy works. We are
> assuming that proves the map exists. Does it?

## Initial Evidence
The variable is empty on every request. No fault is raised; the policy step completes
normally. The map was created at API scope; the policy declares `<Scope>organization</Scope>`.
The `<Key><Parameter>` element carries a `ref` attribute. `index="1"` is a 1-based index
into a multi-valued key.
