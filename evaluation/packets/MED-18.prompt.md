You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-18: Every API product, app and developer fails to load after a hybrid upgrade

## Initial Support Ticket
> We upgraded our hybrid install to 1.16.0 over the weekend. Since then the UI and API cannot load
> API Products, developer apps or developers at all. Nothing was deleted. Proxy traffic is
> unaffected. Is our data gone?

## Initial Evidence
The UI reports a failure to load org entities. Proxy traffic and deployed revisions work. The
runtime pods are running. Management API calls that read proxies succeed; calls that read org
entities fail. The installation is on EKS.
