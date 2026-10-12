You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case EASY-14

## Initial Support Ticket
> One of our backends started returning 502 for every request. Nothing changed in Apigee.
> The backend team says nothing changed on their side either. We can reach the host on
> port 443 from the runtime.

## Initial Evidence
502 on all requests to one proxy. The target endpoint config:

```xml
<SSLInfo>
  <Enabled>true</Enabled>
</SSLInfo>
```

The backend advertises TLS 1.0 as its highest supported version.
