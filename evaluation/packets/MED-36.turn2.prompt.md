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

The customer has replied with more information.

## Diagnostic Evidence
```javascript
// in the JavaScript policy resource
var response = httpClient.send('https://myproject-eval.apigee.net/proxyA/resource');
response.waitForComplete();
context.log("done");   // sometimes never reached
```

And the organisation record showing the free trial / evaluation tier. The current
JavaScript policy reference states for the `timeLimit` attribute: "Specifies the maximum
time (in milliseconds) a script can execute... **Note: For free trial accounts, execution
time is limited to 200 ms.**" The attribute is marked **Required**.
