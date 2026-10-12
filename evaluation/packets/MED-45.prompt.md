You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-45

## Initial Support Ticket
> Since the weekend upgrade roughly 40% of our API calls fail with `The URI contain illegal
> characters`. We looked at our base paths and our target URLs and they are all valid. We have
> not changed any URLs. Can you tell us which URL is malformed?

## Initial Evidence
Requests fail with status 400 and the message `The URI contain illegal characters`. Base paths,
target endpoints and request encoding are unchanged and valid. The failures started on a version
bump, with no proxy change.
