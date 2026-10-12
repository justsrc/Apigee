You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-27

## Initial Support Ticket
> Our shared flow deploys. The command prints the deploy response and returns success. The revision
> shows as ERROR in the UI with "Failed to load file". We only see it because someone checked.
> Nothing in our pipeline would catch this.

## Initial Evidence
The create succeeds. The deploy command prints a response containing an environment name, a proxy
name, a revision number and a start time, and the pipeline continues. A direct query of the
deployments resource for that revision returns a state of ERROR with a per-instance error naming a
file inside the shared flows directory that does not exist in the bundle. The failure only occurs
when the bundle path given to the create step begins with a dot-slash prefix.
