You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-39

The customer has replied with more information.

## Diagnostic Evidence
```terminal
kubectl get services -n istio-system
NAME                   TYPE           CLUSTER-IP    EXTERNAL-IP   PORT(S)                                                     AGE
istio-ingressgateway   LoadBalancer   10.198.5.104  <pending>     15020:31927/TCP,12h                                         80:31381/TCP,443:31391/TCP,...
```

```terminal
kubectl get jobs -n istio-system
```

`EXTERNAL-IP` is `<pending>`, which is the finding. The documented causes for a Service
stuck in pending are, verbatim, "Jobs in erroneous/pending state in istio-system namespace"
and "Incorrect IP address range assigned to external load balancer" as configured in
`istio-operator.yaml`.
