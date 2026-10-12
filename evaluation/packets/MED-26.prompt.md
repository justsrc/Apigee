You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-26: A deployment fails with a Java callout error, and the build tool corrupted the artifact

## Initial Support Ticket
> Our Maven deploy fails. The UI says the revision is deployed but traffic cannot flow. Support
> told us it is a Java callout instantiation failure and said they cannot look further because the
> deployment plugin is open source. Uploading the same jar by hand works every time. Where do we
> look?

## Initial Evidence
Three messages for one deployment. The UI shows `Error in deployment for environment dev. The
revision is deployed, but traffic cannot flow`. Maven reports `Deployment failed: Bundle did not
activate within the expected time. Please check deployment status manually before trying again`.
The deployments API, queried directly, reports `steps.javacallout.JavaCalloutInstantiationFailed`.
