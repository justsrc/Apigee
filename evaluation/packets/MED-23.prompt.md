You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-23

## Initial Support Ticket
> Our lint build started failing after a release of the linter. It now reports a LookupCache
> policy with no matching PopulateCache in the bundle. We know why it says that, but we cannot
> add what it wants: our writes happen in a different proxy than our reads. If we silence the
> rule, are we shipping a real bug? Tell us what to do.

## Initial Evidence
Two API proxies in the same organization. Proxy A attaches a `<PopulateCache>` policy. Proxy B
attaches a `<LookupCache>` policy. Neither bundle contains the other's policy, and neither policy
sets `<Scope>` or `<Prefix>`. The linter reports the LookupCache in proxy B.
