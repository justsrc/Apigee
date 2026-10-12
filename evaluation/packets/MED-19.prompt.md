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

## Initial Support Ticket
> We upgraded hybrid to 1.16.8 yesterday and we now have no Apigee runtime logs at all. Cloud
> Logging shows nothing from our message processors. Please escalate, we are blind.

## Initial Evidence
API traffic is normal and proxies serve correctly. Since the upgrade, no hybrid runtime log lines
appear in Logs Explorer. The prior release produced logs without configuration changes.
