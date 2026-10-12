You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# EASY-05: JavaScript policy blocked by a security violation

The customer has replied with more information.

## Diagnostic Evidence
Rewriting the second line as:

```javascript
context.setVariable("token", token);
```

now succeeds, which confirms the first line is fine and the helper call is what was
blocked.
