You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# HARD-21: Half the routers are rejecting a request the other half accepts

## Initial Support Ticket
> We finished the 4.53.01 upgrade last week across all six nodes and everything has been fine
> since. Yesterday we began moving our edge nginx to the version your documentation recommends
> and now roughly one request in eight comes back as a 400. It is always the same client. The
> other 96 proxies are completely unaffected. We have not changed the proxy. Please advise.

## Initial Evidence
```
HTTP/1.1 400 Bad Request
```

The response body differs between nodes, and this is the only detail in the ticket that matters:

- Requests that reach a Router running NGINX 1.26.x get a 400 with an Nginx-generated body.
- Requests that reach a Router still on NGINX 1.20.x get a 400 with an Apigee Message Processor
  fault body:

```json
{"fault": {"detail": {"errorcode": "messaging.adaptors.http.flow.BadRequest"}}}
```

Six Routers, all on Edge for Private Cloud 4.53.01:

```bash
/opt/apigee/apigee-service/bin/apigee-service edge-router version
```

reports 4.53.01 on every node. So `apigee-service` says the cluster is consistent and it is not,
because NGINX is not part of that version.
