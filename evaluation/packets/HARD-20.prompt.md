You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case HARD-20

## Initial Support Ticket
> We have an intermittent but reproducible problem. A client creates a resource through the API
> and gets a 201. Its very next request, reading that resource back, about one time in five
> returns "not found". The client then retries the GET and it is there. This started roughly when
> we expanded to two availability zones six weeks ago. No proxy was redeployed. Please advise.

## Initial Evidence
Read-after-write misses on a low-latency client that reuses its connection. The rate is
consistent at roughly 20% and is independent of which client is calling. No proxy revisions
changed. One region, two availability zones, three Cassandra nodes per zone, six Message
Processors behind the load balancer.

Failing responses carry no Apigee fault at all. They are ordinary business 404 bodies produced by
the proxy's own lookup, which is itself the first diagnostic fact: this did not fail at a
Message Processor, it failed at the logic the proxy is running.
