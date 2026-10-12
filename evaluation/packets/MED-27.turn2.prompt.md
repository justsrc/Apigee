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

The customer has replied with more information.

## Diagnostic Evidence
```terminal
apigeecli sharedflows listdeploy -e "$ENV" -n "$SF" -o "$ORG" -r "$REV"
```

The response contains a state field that is not ERROR on a healthy deployment, and an errors array
on an unhealthy one. The path inside the error message begins at the root of the shared flows
directory rather than relative to the submitted bundle, and the filename in that path does not match
the bundle's own XML filename. A path that is neither a real bundle entry nor the path the user
typed means the stored path was derived from something other than the bundle contents.
