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

The customer has replied with more information.

## Diagnostic Evidence
```terminal
kubectl get certificate apigee-ca -n cert-manager -o yaml
```

On the failing cluster, `spec.privateKey.rotationPolicy` is unset, so cert-manager applies its
current default. On the healthy cluster it is explicitly `Never`, because the hybrid chart sets it
on fresh installs. Both clusters run cert-manager at or above 1.18.
