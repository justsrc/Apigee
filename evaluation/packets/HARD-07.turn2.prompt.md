You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case HARD-07

The customer has replied with more information.

## Diagnostic Evidence
The target endpoint names the store directly, with no `ref://` prefix. The keystore
aliases API documents an `update` method: `PUT` to
`organizations/{org}/environments/{env}/keystores/{keystore}/aliases/{alias}`, described
as "Updates the certificate in an alias", taking a PEM- or DER-encoded X.509 body,
requiring the `ignoreExpiryValidation` query parameter and the
`apigee.keystorealiases.update` IAM permission.

The same documentation set also says, as a Note: "You cannot update an existing keystore
or truststore to add a new certificate. You must create a new keystore/truststore when
updating a certificate." It also lists two rotation methods named "In-place update":
delete and recreate the store with the same name, and, for truststores only, upload a new
certificate directly to the existing truststore. Both are marked as requiring a Message
Processor restart, because Message Processors cache directly specified stores.
