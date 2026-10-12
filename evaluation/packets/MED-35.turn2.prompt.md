You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-35

The customer has replied with more information.

## Diagnostic Evidence
```terminal
kubectl get svc istio-ingressgateway -n istio-system
kubectl get deploy -n apigee
```

From the TargetEndpoint definition:

```xml
<HTTPTargetConnection>
  <URL>https://backend.example.com</URL>
  <Properties>
    <Property name="keepalive.timeout.millis">30000</Property>
  </Properties>
</HTTPTargetConnection>
```

Against a backend configured with a 25 second keep-alive, and the reference documents a
default of 60000 ms for that property.
