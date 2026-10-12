You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case HARD-03

The customer has replied with more information.

## Diagnostic Evidence
Inspecting the target endpoint shows:

```xml
<SSLInfo>
  <Enabled>true</Enabled>
  <ClientAuthEnabled>true</ClientAuthEnabled>
  <KeyStore>ref://orders-keystore</KeyStore>
  <KeyAlias>orders-client</KeyAlias>
  <TrustStore>ref://orders-trust</TrustStore>
</SSLInfo>
```

The environment reference resolves as:

```xml
<ResourceReference name="orders-keystore">
  <Refers>orders-keystore-v1</Refers>
  <ResourceType>KeyStore</ResourceType>
</ResourceReference>
```

The new store is `orders-keystore-v2`, and its only alias is `orders-client-v2`. The
alias was renamed during the swap. The northbound certificate is configured on the
virtual host, against a different store, and was never touched.
