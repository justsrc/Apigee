You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-03

## Initial Support Ticket
> Our orders backend has two nodes. When one of them starts returning 500, load balancing
> keeps sending it about half the traffic and those requests keep failing. When one node is
> stopped outright, every other request gets noticeably slower before it succeeds. Load
> balancing is configured. Why is it not protecting us?

## Initial Evidence
Two target servers configured under a `<LoadBalancer>`. Requests routed to a node that
returns 500 fail. When a node is stopped entirely, those requests eventually succeed via
the other node, but only after a failed connection attempt.
