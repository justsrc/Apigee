You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-36

## Initial Support Ticket
> We have two proxies. Proxy B has a JavaScript policy that calls proxy A over HTTP and
> processes the response. Intermittently we get:
>
> ```json
> {"fault":{"detail":{"errorcode":"steps.javascript.ScriptExecutionFailed"},
>   "faultstring":"Execution of getlocationserviceresponse failed with error: Javascript runtime exceeded limit of 200ms"}}
> ```
>
> We have already split our JavaScript into small modules so each policy is tiny. It still
> happens "from time to time". What can we do to avoid it?

## Initial Evidence
`steps.javascript.ScriptExecutionFailed`, HTTP 500, verified at `error-codes.md` line 61.
The failure is intermittent, not consistent, and the arithmetic does not fit a CPU-bound
script: splitting the code did not help, which is itself evidence that the limit is not
being consumed by computation. The script performs `httpClient` calls. The organisation is
on a free trial or evaluation tier, which the ticket does not yet mention.
