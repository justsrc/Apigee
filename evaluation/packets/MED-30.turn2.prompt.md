You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-30: The token endpoint is correct and the client is sending a malformed header

The customer has replied with more information.

## Diagnostic Evidence
```terminal
curl -s -X POST "$TOKEN_URL" -d grant_type=client_credentials -u "$CLIENT:$SECRET" | jq .token_type
# "BearerToken"

curl -s -X POST "$TOKEN_URL" -d grant_type=client_credentials -u "$CLIENT:$SECRET" \
  | jq '{expires_in_type: (.expires_in|type), refresh_type: (.refresh_token_expires_in|type)}'
# expires_in_type: "string"
# refresh_type: "string"
```

Both facts matter. The token type is non-compliant, and the lifetime values are serialised as
quoted strings rather than numbers.
