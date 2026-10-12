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
The full fault strings from two failing requests read:

```
Execution of ParseJSONResponse failed with error: Javascript runtime error: "TypeError: Cannot read property "length" from undefined. (ParseJSONResponse.js:7)"
```

```
Execution of ReadItemList failed with error: Javascript runtime error: "TypeError: Cannot read property "length" from undefined. (ReadItemList.js:11)"
```

The code is identical and so is the inner description. What differs is the policy name and
the source line, which is what says which script to open. On the requests that fail, the
client either sends a body that is an empty array or omits the `items` query parameter. The
first script parses `response.content` with `JSON.parse` and then reads `body[0].length`;
the second reads `request.queryparam.items` and then `.length` on it.
