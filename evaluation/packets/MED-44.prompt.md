You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-44: Headers that were removed, then put back, and are still pinned

## Initial Support Ticket
> Our backend stopped receiving `x-b3` correlation headers last month. We did not change
> anything on the backend. Distributed Trace is switched off in our org, which I assumed meant
> nothing trace related was sent. Help me find what changed.

## Initial Evidence
`x-b3` headers are absent at the target. Distributed Trace is disabled in the org. No proxy
policy has been edited. The org was last upgraded recently.
