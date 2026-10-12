You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-38: OAuth rejects a valid-looking token because no API product matched

The customer has replied with more information.

## Diagnostic Evidence
```
GET /v1/o/{org}/apiproducts            -> product list
GET /v1/o/{org}/developers/{dev}/apps/{app}   -> app.productBundle
GET /v1/o/{org}/apiproducts/{prod}/resources -> proxy + path list
GET /v1/o/{org}/apiproducts/{prod}/operations -> resource paths and operations
```

The trace shows the OAuth policy succeeds and the failure occurs on the resource match,
not on token validation. The app is associated with product **A**, the proxy is exposed
through product **B**, and the product the app holds does not include the request path.
