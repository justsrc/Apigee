You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case HARD-14

## Initial Support Ticket
> We restored OpenLDAP from last night's backup. Now some environments exist and others do
> not, and the UI shows orgs that cannot be deployed to. Should we restore the other stores
> too?

## Initial Evidence
OpenLDAP was restored from backup. ZooKeeper and Cassandra were not. Environments are
missing on some Message Processors.
