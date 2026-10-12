You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-19: Runtime logs stopped after a successful upgrade

The customer has replied with more information.

## Diagnostic Evidence
`kubectl get daemonset apigee-logger -n apigee` reports a desired count of `0` and no logger pods
exist. The overrides file sets `logger.enabled: true`. The `apigee-telemetry` chart's default
`logger.nodeSelector` is `apigee.cloud.google.com/apigee-logger-enabled: "true"`, and no nodes carry
that label.
