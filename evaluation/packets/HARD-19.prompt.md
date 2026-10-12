You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case HARD-19

## Initial Support Ticket
> After last night's Router and Message Processor upgrade, about 4% of requests to our payments
> API fail. Everything else on that proxy is fine. The failing requests are new since the upgrade
> and nothing in the proxy bundle changed. Please advise.

## Initial Evidence
From the Message Processor trace of a failing request:

```json
{"fault": {"detail": {"errorcode": "steps.javacallout.ExecutionError"}}}
```

and from the Message Processor log:

```
org.bouncycastle.openssl.PEMException: unable to convert key pair: no such provider: BC
	at org.bouncycastle.openssl.jcajce.JcaPEMKeyConverter.getPrivateKey(Unknown Source)
	at com.google.apigee.util.KeyUtil.decodePrivateKey(KeyUtil.java:87)
	at com.google.apigee.callouts.RsaBase.getPrivateKey(RsaBase.java:143)
	at com.google.apigee.callouts.RsaCrypto.execute(RsaCrypto.java:271)
	at com.apigee.steps.javacallout.JavaCalloutStepDefinition$ClassLoadWrappedExecution.execute(JavaCalloutStepDefinition.java:235)
...
Caused by: java.security.NoSuchProviderException: no such provider: BC
	at sun.security.jca.GetInstance.getInstance(GetInstance.java:206)
	at java.security.KeyFactory.getInstance(KeyFactory.java:211)
	at org.bouncycastle.jcajce.util.NamedJcaJceHelper.createKeyFactory(Unknown Source)
	... 21 more
```

The policy:

```xml
<JavaCallout>
  <Properties>
    <Property name="action">decrypt</Property>
    <Property name="decode-source">base64url</Property>
    <Property name="private-key">{rsa_private_key}</Property>
    <Property name="utf8-decode-result">true</Property>
  </Properties>
  <ClassName>com.google.apigee.callouts.RsaCrypto</ClassName>
  <ResourceURL>java://apigee-callout-rsa-crypto-20230118.jar</ResourceURL>
</JavaCallout>
```

The callout jar was built years ago and uploaded once. It has never been rebuilt.
