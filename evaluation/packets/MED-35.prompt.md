You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-35: 502 Bad Gateway at exactly two minutes, with the backend reporting success four minutes later

## Initial Support Ticket
> We have an Apigee proxy in front of a Node.js 12 / Express backend. If a request takes
> longer than two minutes the client gets a 502 Bad Gateway, always at the two minute mark.
> The backend logs a 200 about four minutes later, so it is completing the work after the
> client has already given up. The backend logs nothing at the moment the client errors.
>
> The fault body is:
>
> ```json
> {"fault":{"faultstring":"Unexpected EOF at target",
>   "detail":{"errorcode":"messaging.adaptors.http.flow.UnexpectedEOFAtTarget"}}}
> ```
>
> We have already raised the Node request timeout to ten minutes and added keep-alive on
> the backend. Neither changed anything. Please tell us why Apigee is throwing the error
> when the backend is not.

## Initial Evidence
HTTP 502, fault code `messaging.adaptors.http.flow.UnexpectedEOFAtTarget`, fault string
"Unexpected EOF at target". The failure is at a fixed 120 seconds from request start. The
backend receives the request, does not respond for four minutes, and has no log entry at
the two minute mark. The customer has already changed backend-side keep-alive and Node
timeouts.

The fault code is verified in `research/pages/mon_fault-codes.txt` line 81. It is
deliberately **not** in `.agents/skills/apigee-support-core/references/error-codes.md`,
because that index covers policy fault codes and this one is raised by the HTTP target
adaptor, not by a policy. An agent that cannot say that distinction has not read the
evidence properly.
