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
> We get a JavaScript policy failure roughly once an hour. Every time it is the same
> `ScriptExecutionFailed`. Two different policies are involved and both look fine. What is
> it failing on?

## Initial Evidence
Two JavaScript policies doing small amounts of work: one parses a JSON body, the other
reads a query parameter list. Roughly one failure per hour, always at peak. Their log
export captures only the `errorcode` column, so "the same error" in their report means the
code, not the full `faultstring` field, which is not recorded at all.
