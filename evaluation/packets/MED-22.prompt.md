You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-22

## Initial Support Ticket
> We upgraded cert-manager on our hybrid clusters last week as part of routine maintenance. No
  issues since. We are seeing intermittent connection failures between hybrid runtime components on
  one cluster but not the other. Both are the same hybrid version. Where do we start?

## Initial Evidence
Two hybrid clusters, same hybrid version, same changes. One has intermittent component connection
failures; the other does not. Both were upgraded rather than installed fresh.
