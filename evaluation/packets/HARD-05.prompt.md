You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# HARD-05: Intermittent 502s across a mixed revision fleet

## Initial Support Ticket
> Since the 09:00 deploy we see maybe 5% 502s. Functional tests pass. It seems random,
> which is the worst part. We rolled back an hour ago and it is still happening.

## Initial Evidence
A deployment of revision 22 went out at 09:00. Roughly 5% of requests return 502. A
rollback was performed at 10:00. The rate is unchanged. The environment group is
`prod-group` and its hostname is `api.example.com`.
