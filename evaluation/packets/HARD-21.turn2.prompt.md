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

The customer has replied with more information.

## Diagnostic Evidence
Run the version check on each Router node, individually:

```bash
/opt/apigee/apigee-service/bin/apigee-service edge-router version
/opt/nginx/sbin/nginx -V
```

The first reports Apigee 4.53.01 on all six nodes, which is true and useless for this question.
The second is the one that differs, and it has to be run per node because there is no
cluster-level view of it.

The per-node count of 400s correlates exactly with the per-node NGINX version. The team has been
routing test requests through each Router's health endpoint to isolate them:

```bash
curl -v http://routerIP:15999/v1/servers/self/reachable
```

which returns HTTP 200 when the Router is reachable, and can be used as a per-node probe while
the real request is replayed against each Router individually.
