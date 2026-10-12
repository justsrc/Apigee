You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-17

## Initial Support Ticket
> Our CI deploys shared flows and proxies with the Apigee deploy Maven plugin. Intermittently the
> build fails with `Deployment failed: Bundle did not activate within expected time. Please check
> deployment status manually before trying again`. We want the plugin's hardcoded 10 second wait to
> be made configurable. Can you confirm that is the bug?

## Initial Evidence
`apigee.override.delay` is set to 30 in the POM. Direct calls to the Management API import and
deploy succeed. Deployments that take longer than the plugin's internal check interval fail; faster
ones pass. Nothing else in the pipeline fails.
