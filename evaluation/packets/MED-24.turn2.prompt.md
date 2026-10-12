You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-24

The customer has replied with more information.

## Diagnostic Evidence
```terminal
apigeelint --version          # v2.76.0
# same bundle on the previous linter
apigeelint --version          # v2.75.0 -> clean
```

The official policy reference lists `UseEffectiveCount` among the supported child elements and
documents `true` as a supported value, and notes that organizations should set it to `true` even
though `false` is the default. The actual documented restriction is narrower than the lint
message: it concerns the value `false` on any organization, and `UseEffectiveCount` on hybrid
organizations running production workloads.
