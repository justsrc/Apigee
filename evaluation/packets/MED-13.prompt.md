You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-13

## Initial Support Ticket
> We get a JavaScript policy failure roughly once an hour. It says `ScriptExecutionFailed`
> but the script is trivial and works most of the time. What is it failing on?

## Initial Evidence
A JavaScript policy doing a small amount of work. Roughly one failure per hour, always at
peak. The fault string is not included in what the team pasted.
