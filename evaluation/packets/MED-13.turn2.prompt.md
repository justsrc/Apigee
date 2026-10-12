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

The customer has replied with more information.

## Diagnostic Evidence
The full fault string reads:

```
Execution of ParseJSONResponse failed with error: Javascript runtime error: "TypeError: Cannot read property "length" from undefined. (ParseJSONResponse.js:7)"
```

The error description on its own does not say which of the two policies failed. It is the
policy name and the source line inside the same fault string that discriminate: this one
is `ParseJSONResponse` at line 7, not the query-parameter policy. On the requests that
fail, the client sends a body that is an empty array, and the script reads
`response.content[0].length`.
