You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case ADV-12

The customer has replied with more information.

## Diagnostic Evidence
None of the three sources states its timezone, and none of them says what it measured.
The pager record attached to the engineer's note carries an offset in its raw timestamp:

```json
{"fired_at": "2026-03-04T13:52:48+02:00", "received_at": "2026-03-04T14:00:11+02:00"}
```

The dashboard export carries no offset at all, and declares only its bucket granularity:

```text
bucket_granularity_minutes: 5
last_bucket_without_5xx:   2026-03-04 13:25
first_bucket_with_5xx:     2026-03-04 13:30
```

The release pipeline recorded one timestamp for the deployment and nothing about it:

```text
deployed_at: 2026-03-04 14:15
```
