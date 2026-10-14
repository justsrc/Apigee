# Apigee security notes: auth, authorization, tokens, TLS

Research date: 2026-10-11. Every URL in the VERIFIED PAGES table was fetched through
`research/fetch.sh` and returned the recorded HTTP status. Nothing below cites a URL
that was not checked. Facts are labelled **documented** (stated on a fetched page),
**hypothesis** (my inference), or **unverified**.

Two structural notes about the docs, both confirmed by reading the fetched pages:

- The policy error reference index (`api-platform/reference/policies/error-code-reference`)
  is a pointer page, as the recipe says. Real fault codes are on each policy page.
- **`fetch.sh` silently truncates some pages.** Its awk starts at the first markdown
  `^# `. Pages whose first code block contains a shell comment (`# comment`) or that
  simply lack an H1 lose their opening. `root-ca-rotation` lost its entire first half
  and `tls-vars` lost its title through this. I re-extracted `root-ca-rotation` with an
  explicit heading match. Any page under ~2 KB should be treated as suspect, not short.

---

## 1. VERIFIED PAGES

Title | URL | HTTP status | bytes

OAuthV2 policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy> | 200 | 111518
VerifyJWT policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jwt-policy> | 200 | 12298
AccessControl policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/access-control-policy> | 200 | 28723
BasicAuthentication policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/basic-authentication-policy> | 200 | 19643
DecodeJWT policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/decode-jwt-policy> | 200 | 14776
GenerateJWT policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/generate-jwt-policy> | 200 | 10621
VerifyJWS policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jws-policy> | 200 | 34463
VerifyIAM policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-iam-policy> | 200 | 9337
HMAC policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/hmac-policy> | 200 | 25352
VerifyAPIKey policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-api-key-policy> | 200 | 34333
CORS policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/cors-policy> | 200 | 7231
JWS and JWT policies overview | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/jwt-policies-overview> | 200 | 29427
OAuth HTTP error response reference | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauth-http-status-code-reference> | 200 | 13043
OAuth home | <https://cloud.google.com/apigee/docs/api-platform/security/oauth/oauth-home> | 200 | 6469
OAuth introduction | <https://cloud.google.com/apigee/docs/api-platform/security/oauth/oauth-introduction> | 200 | 17686
Get OAuth 2.0 tokens (access-tokens) | <https://cloud.google.com/apigee/docs/api-platform/security/oauth/access-tokens> | 200 | 36232
Configuring OAuth endpoints and policies | <https://cloud.google.com/apigee/docs/api-platform/security/oauth/configuring-oauth-endpoints-and-policies> | 200 | 3752
Customizing access tokens | <https://cloud.google.com/apigee/docs/api-platform/security/oauth/customizing-access-tokens> | 200 | 6752
Working with OAuth2 scopes | <https://cloud.google.com/apigee/docs/api-platform/security/oauth/working-scopes> | 200 | 17470
Approving and revoking access tokens | <https://cloud.google.com/apigee/docs/api-platform/security/oauth/validating-and-invalidating-access-tokens> | 200 | 9979
Enable retrieval and revocation of access tokens | <https://cloud.google.com/apigee/docs/api-platform/security/oauth/enable-retrieval-and-revocation-oauth-20-access-tokens-end-user-id-app-id-or-both> | 200 | 6549
Use a third-party OAuth system | <https://cloud.google.com/apigee/docs/api-platform/security/oauth/use-third-party-oauth-system> | 200 | 14036
Using access tokens | <https://cloud.google.com/apigee/docs/api-platform/security/oauth/using-access-tokens> | 200 | 5135
Using JWT OAuth token operations | <https://cloud.google.com/apigee/docs/api-platform/security/oauth/using-jwt-oauth> | 200 | 16546
Advanced OAuth 2.0 topics | <https://cloud.google.com/apigee/docs/api-platform/security/oauth/advanced-oauth-20-topics> | 200 | 4052
Implementing the password grant type | <https://cloud.google.com/apigee/docs/api-platform/security/oauth/implementing-password-grant-type> | 200 | 8843
OAuth 2.0 client credentials grant type | <https://cloud.google.com/apigee/docs/api-platform/security/oauth/oauth-20-client-credentials-grant-type> | 200 | 10444
OAuthV2 policy authorization code grant type | <https://cloud.google.com/apigee/docs/api-platform/security/oauth/oauth-v2-policy-authorization-code-grant-type> | 200 | 13512
Understanding the default OAuth 2.0 configuration | <https://cloud.google.com/apigee/docs/api-platform/security/oauth/understanding-default-oauth-20-configuration> | 200 | 5816
Hashing access tokens | <https://cloud.google.com/apigee/docs/api-platform/security/oauth/hashing-tokens> | 200 | 812
Sending an access token | <https://cloud.google.com/apigee/docs/api-platform/security/oauth/sending-access-token> | 200 | 1751
Obtaining developer keys | <https://cloud.google.com/apigee/docs/api-platform/security/oauth/obtaining-developer-keys> | 200 | 4413
Revoking and approving consumer keys | <https://cloud.google.com/apigee/docs/api-platform/security/oauth/revoking-and-approving-consumer-ids> | 200 | 7191
GetOAuthV2Info policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/get-oauth-v2-info-policy> | 200 | 24001
SetOAuthV2Info policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/set-oauth-v2-info-policy> | 200 | 12836
DeleteOAuthV2Info policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/delete-oauth-v2-info> | 200 | 11213
RevokeOAuthV2 policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/revoke-oauth-v2-policy> | 200 | 16159
GenerateJWS policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/generate-jws-policy> | 200 | 33103
DecodeJWS policy | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/decode-jws-policy> | 200 | 14936
Encryption keys | <https://cloud.google.com/apigee/docs/api-platform/security/encryption-keys> | 200 | 1200
IAM overview | <https://cloud.google.com/apigee/docs/api-platform/security/iam/iam-overview> | 200 | 15481
Google auth overview | <https://cloud.google.com/apigee/docs/api-platform/security/google-auth/overview> | 200 | 23171
API keys | <https://cloud.google.com/apigee/docs/api-platform/security/api-keys> | 200 | 6076
API security | <https://cloud.google.com/apigee/docs/api-platform/security/api-security> | 200 | 2067
Last mile security | <https://cloud.google.com/apigee/docs/api-platform/security/last-mile-security> | 200 | 4286
Options for configuring TLS | <https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls> | 200 | 14840
About the Apigee root CA certificate and rotation | <https://cloud.google.com/apigee/docs/api-platform/security/root-ca-rotation> | 200 | 16385
TLS flow variables | <https://cloud.google.com/apigee/docs/api-platform/security/tls-vars> | 200 | 4184
API proxy configuration reference | <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference> | 200 | 69358
Endpoint properties reference | <https://cloud.google.com/apigee/docs/api-platform/reference/endpoint-properties-reference> | 200 | 19899
Policy error code reference (index) | <https://cloud.google.com/apigee/docs/api-platform/reference/policies/error-code-reference> | 200 | 1564
What you need to know about policy errors | <https://cloud.google.com/apigee/docs/api-platform/fundamentals/what-you-need-know-about-policy-errors> | 200 | 8728
Basic auth runtime errors | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/runtime/basic-authentication-runtime-errors> | 200 | 14616
Basic auth deployment errors | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/deployment/basic-authentication-deployment-errors> | 200 | 12279
DecodeJWT runtime errors | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/runtime/decode-JWT-runtime-errors> | 200 | 6937
DecodeJWT deployment errors | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/deployment/decode-JWT-deployment-errors> | 200 | 2945
Troubleshooting playbooks index | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/introduction> | 200 | 29162
Playbook: ingress mTLS CA cert expired | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/ca-cert-expiry> | 200 | 8375
Playbook: ingress mTLS CA cert invalid | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/ca-cert-invalid> | 200 | 9390
Playbook: ingress cert expired | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/ingress-cert-expiry> | 200 | 8253
Playbook: ingress cert mismatch | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/ingress-cert-mismatch> | 200 | 6137
Playbook: connection resets during TLS handshake (hybrid) | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/hybrid/connection-resets-during-tls-handshake> | 200 | 11816
Playbook: API calls failing with TLS errors (ingressgateway) | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/ingressgateway/api-calls-failing-tls-errors> | 200 | 10702
Playbook: Cassandra TLS certificate verification failure | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/cassandra/cassandra-tls-certificate-verification-failure> | 200 | 15882
Playbook: Apigee serving cert not found or expired | <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/deployment/apigee-serving-cert-not-found-or-expired> | 200 | 253
Keystore resource (REST) | <https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.environments.keystores> | 200 | 3205
Alias resource (REST) | <https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.environments.keystores.aliases> | 200 | 6022
keystores.aliases.create (REST) | <https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.environments.keystores.aliases/create> | 200 | 5451
keystores.aliases.update (REST) | <https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.environments.keystores.aliases/update> | 200 | 3916
keystores.aliases.delete (REST) | <https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.environments.keystores.aliases/delete> | 200 | 2472
Configuring TLS and mTLS on the Istio ingress (hybrid latest) | <https://cloud.google.com/apigee/docs/hybrid/latest/ingress-tls> | 200 | 12405
Configuring TLS and mTLS on the Istio ingress (hybrid v1.17) | <https://cloud.google.com/apigee/docs/hybrid/v1.17/ingress-tls> | 200 | 12405
Hybrid config property reference | <https://cloud.google.com/apigee/docs/hybrid/latest/config-prop-ref> | 200 | 479971
Controlling access to your APIs by registering apps | <https://cloud.google.com/apigee/docs/api-platform/publish/creating-apps-surface-your-api> | 200 | 20890
Compare Apigee products | <https://cloud.google.com/apigee/docs/api-platform/get-started/compare-apigee-products> | 200 | 11304

---

## 2. CONFIRMED TECHNICAL FACTS

Each fact below is **documented** unless marked otherwise. Source URL given for each.

### OAuth 2.0 / OAuthV2

- **documented** — "OAuth tokens are cached for three minutes (180 seconds); therefore, a revoked token may still succeed for up to three minutes, until its cache limit expires." Applies to `InvalidateToken`. <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy> and <https://cloud.google.com/apigee/docs/api-platform/security/oauth/validating-and-invalidating-access-tokens>
- **documented** — "Only OAuth 2.0 Bearer Tokens are supported. Other types of tokens such as Message Authentication Code (MAC) tokens are not supported." for `VerifyAccessToken`. <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>
- **documented** — Default token source for `VerifyAccessToken` is the `Authorization` header with the `Bearer` prefix stripped. Override with `<AccessToken>`; that override also suppresses prefix matching unless `<AccessTokenPrefix>` is set. <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>
- **documented** — Authorization code grant needs four separate OAuthV2 policies: authorization code generation, access code generation, access code validation, refresh token generation. <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>
- **documented** — A `GenerateAccessToken` policy on the **response** flow fails with 401 unless an `Authorization` request header carrying `Basic base64(client_id:client_secret)` is set by an earlier policy. <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>
- **documented** — Warning: "`VerifyAPIKey` and `OAuthV2` policies may experience increased p90+ latencies under specific conditions. This behavior is typically observed when the Queries Per Second (QPS) rate is very low (single-digit rate) and Message Processors (MPs) are over-provisioned. The elevated latency in these scenarios is primarily attributed to inefficient cache utilization." <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>
- **documented** — With `GenerateAccessToken`, "the `token_type` property in the token response may be non-compliant" with OAuth 2.0 specs. <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>
- **documented** — Known bug: "There is currently a bug where unsupported grant type errors are not thrown correctly. If an unsupported grant type error occurs, the proxy does not enter the Error Flow, as expected." (`steps.oauth.v2.UnSupportedGrantType`). <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>
- **documented** — Fault rules must catch both `invalid_client` and `InvalidClientIdentifier`; these are the same condition split on the value of `<GenerateResponse>`. <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>
- **documented** — `<ExpiresIn>` and `<RefreshTokenExpiresIn>` accept positive integers, in milliseconds. <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>
- **documented** — Policy `name` attribute "cannot exceed 255 characters"; `async` attribute is deprecated. <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>
- **documented** — The `oauth-http-status-code-reference` page carries an explicit deprecation banner: "**This topic is deprecated.** The error names and HTTP response codes associated with the OAuthV2 policies are described in each policy's reference documentation". Its `keymanagement.service.*` codes still differ from the `steps.oauth.v2.*` codes on the OAuthV2 page for the same conditions (see section 4). <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauth-http-status-code-reference>

### JWT / JWS

- **documented** — `<Algorithm>` means signed JWT; `<Algorithms>` (plural) means encrypted JWT. Signed verification takes `<SecretKey>` (HS*) or `<PublicKey>` (RS*, ES*, PS*). Encrypted verification takes `<PrivateKey>`, `<SecretKey>`, `<PasswordKey>`, or `<DirectKey>`. <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jwt-policy>
- **documented** — "If the policy configuration provides a certificate as the source of the public key, the runtime does not check the trust chain of the certificate and does not check the expiry of the certificate. The public key contained within the certificate is treated as valid and trusted." <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jwt-policy>
- **documented** — HMAC minimum key lengths: "HS256: 32 bytes minimum key length; HS384: 48 bytes minimum key length; HS512: 64 bytes minimum key length". <https://cloud.google.com/apigee/docs/api-platform/reference/policies/jwt-policies-overview>
- **documented** — "There are no size requirements on the keys" for RSA (RS*); RSASSA-PSS (PS*) has "The format, mechanism, and size limits of the key is the same as for the RS* algorithms." <https://cloud.google.com/apigee/docs/api-platform/reference/policies/jwt-policies-overview>
- **documented** — ECDSA curve mapping: ES256=P-256 (secp256r1/prime256v1), ES384=P-384 (secp384r1), ES512=P-521 (secp521r1). <https://cloud.google.com/apigee/docs/api-platform/reference/policies/jwt-policies-overview>
- **documented** — Supported JWS/JWT signature algorithms are exactly: `RS256, RS384, RS512, PS256, PS384, PS512, ES256, ES384, ES512, HS256, HS384, HS512`. Any other value fails deployment with `InvalidAlgorithm`. <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jws-policy>
- **documented** — Supported JWT *encryption* algorithms: `dir`, `RSA-OAEP-256`, `A128KW`, `A192KW`, `A256KW`, `A128GCMKW`, `A192GCMKW`, `A256GCMKW`, `PBES2-HS256+A128KW`, `PBES2-HS384+A192KW`, `PBES2-HS512+A256KW`, `ECDH-ES`, `ECDH-ES+A128KW`, `ECDH-ES+A192KW`, `ECDH-ES+A256KW`. <https://cloud.google.com/apigee/docs/api-platform/reference/policies/jwt-policies-overview>
- **documented** — JWKS source: `<PublicKey><JWKS uri="..."/></PublicKey>`, `uriRef="var"` (variable holding the URI), or `ref="var"` (variable holding the JWKS document). <https://cloud.google.com/apigee/docs/api-platform/reference/policies/jwt-policies-overview>
- **documented** — JWKS resolution sequence: (1) reject if token `alg` does not match policy `<Algorithm>`; (2) fetch key list from the JWKS endpoint or internal cache; (3) **"If the inbound JWT does not include a key ID (kid) in the header, then the mapping of kid to verification-key is not possible, and Apigee will throw a fault."**; (4) throw a fault if no JWK matches the `kid`; (5) throw a fault if the JWK algorithm does not match; (6) verify signature. <https://cloud.google.com/apigee/docs/api-platform/reference/policies/jwt-policies-overview>
- **documented** — Security warning on `uriRef`: "As the proxy designer, you are responsible for insuring that you do not configure your verification policies to trust unvetted URIs." <https://cloud.google.com/apigee/docs/api-platform/reference/policies/jwt-policies-overview>
- **documented** — JWKS elements that "should always be present": `kty` (RSA or EC) and `kid`. Optional: `alg`, `use` ("sig" / "enc"). <https://cloud.google.com/apigee/docs/api-platform/reference/policies/jwt-policies-overview>
- **documented** — "If you use a ServiceCallout to retrieve the JWKS, it's a good practice to cache the JWKS to avoid executing the ServiceCallout on every request." <https://cloud.google.com/apigee/docs/api-platform/reference/policies/jwt-policies-overview>
- **documented** — OAuthV2 JWT access token fault names use the prefix `oauth.v2.` (not `steps.oauth.v2.`): e.g. `oauth.v2.InvalidJWTSignature`, `oauth.v2.JWTAlgorithmMismatch`. All are HTTP 401. <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>
- **documented** — `oauth.v2.InvalidTypeInJWTHeader`: "Occurs when the JWT's type is not `at+Jwt`". <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>
- **documented** — JWS/JWT deployment error `InvalidVariableNameForKey`: "The flow variable name specified in the `ref` attribute of the child element `<Value>` of the `<PrivateKey>`, `<PublicKey>` or `<SecretKey>` elements does not contain the `private` prefix." <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>

### API keys

- **documented** — `<APIKey ref="...">` — "Only one location is allowed per policy." <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-api-key-policy>
- **documented** — "Currently, Apigee does not report the `ApiKeyNotApproved` error accurately. Instead, if a key is not approved (its status is set to `revoked` or `pending`), you will get the `FailedToResolveAPIKey` error instead." <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-api-key-policy>
- **documented** — Best practice: "It's a good practice to pass the API key in a header or form parameter rather than in a query parameter." <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-api-key-policy>
- **documented** — Developer App key status note (from the REST reference surfaced on the policy page): "All keys start out with status=approved, even if status=revoked is passed when the key is created." <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-api-key-policy> (links to organizations.developers.apps.keys.create)

### AccessControl

- **documented** — `<IPRules noRuleMatchAction="ALLOW|DENY">` — valid values ALLOW or DENY, **default ALLOW**, presence Required. `<MatchRule action="ALLOW|DENY">` — default ALLOW, Required. <https://cloud.google.com/apigee/docs/api-platform/reference/policies/access-control-policy>
- **documented** — "The mask values in the following IPv4 samples identify which of the four octets (8, 16, 24, 32 bits) the match rule considers when allowing or denying access. The default value is 32." <https://cloud.google.com/apigee/docs/api-platform/reference/policies/access-control-policy>
- **documented** — `<ValidateBasedOn>`: "Currently it is necessary to set the element `<IgnoreTrueClientIPHeader>` to true in order for multiple IP addresses to be evaluated." The page also recommends `client.resolved.ip` instead. <https://cloud.google.com/apigee/docs/api-platform/reference/policies/access-control-policy>
- **documented** — Runtime faults: `accesscontrol.IPDeniedAccess`, `accesscontrol.InvalidIPAddressInVariable`. No policy-specific deployment errors are listed. <https://cloud.google.com/apigee/docs/api-platform/reference/policies/access-control-policy>

### BasicAuthentication

- **documented** — Operations are exactly `Encode` and `Decode`. Encode Base64-encodes username+password from variables; Decode extracts them from a `Basic <Base64>` string. <https://cloud.google.com/apigee/docs/api-platform/reference/policies/basic-authentication-policy>
- **documented** — Both runtime faults are HTTP **500**, not 401: `steps.basicauthentication.InvalidBasicAuthenticationSource`, `steps.basicauthentication.UnresolvedVariable`. <https://cloud.google.com/apigee/docs/api-platform/reference/policies/basic-authentication-policy>
- **documented** — `UnresolvedVariable` "can only occur if `IgnoreUnresolvedVariables` is false". Deployment errors: `UserNameRequired`, `PasswordRequired`, `AssignToRequired`, `SourceRequired`. <https://cloud.google.com/apigee/docs/api-platform/reference/policies/basic-authentication-policy>

### HMAC

- **documented** — `<Algorithm>` valid values: `SHA-1`, `SHA-224`, `SHA-256`, `SHA-384`, `SHA-512`, and `MD-5`. "The policy configuration accepts algorithm names without distinguishing case, and with or without the dash between the letters and numbers. For example, `SHA256` and `SHA-256` and `sha256` are equivalent." Element is Required. <https://cloud.google.com/apigee/docs/api-platform/reference/policies/hmac-policy>
- **documented** — Security note on that page: "SHA-1 and MD-5 are included here for completeness, but Google recommends that people do not use these hashes." <https://cloud.google.com/apigee/docs/api-platform/reference/policies/hmac-policy>
- **documented** — Default encoding of `<SecretKey>` is UTF-8; default encoding of `<Output>` is base64. Whitespace in `<Message>` "is significant". All five HMAC runtime faults are HTTP **401**: `steps.hmac.UnresolvedVariable`, `steps.hmac.HmacVerificationFailed`, `steps.hmac.HmacCalculationFailed`, `steps.hmac.EmptySecretKey`, `steps.hmac.EmptyVerificationValue`. <https://cloud.google.com/apigee/docs/api-platform/reference/policies/hmac-policy>

### VerifyIAM

- **documented** — **"This policy is not available with Apigee hybrid at this time."** The page header also says "*This page applies to **Apigee**, but not to **Apigee hybrid***." <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-iam-policy>
- **documented** — Only two elements exist: `<DisplayName>` and `<CredentialSource>`. "If omitted, policy execution assumes the value is in the authorization header and in the standard format 'Bearer xyz'." When read from the reference, "a direct value is expected. For example, 'Bearer' should not be present as the prefix." <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-iam-policy>
- **documented** — "This policy does not return any policy-specific deployment errors." <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-iam-policy>
- **documented** — Latency: "Typically, policy execution with VerifyIAM takes between 10 and 50 milliseconds... in the `asia-east2` region specifically, average latency can rise to 50 ms, and some calls could take around 100 ms to complete." <https://cloud.google.com/apigee/docs/api-platform/security/iam/iam-overview>
- **documented** — "VerifyIAM should be the first policy in the request flow, after only traffic management policies." "IAM-based access control supports a maximum of 1,500 role bindings within a single policy." <https://cloud.google.com/apigee/docs/api-platform/security/iam/iam-overview>
- **documented** — "IAM conditions are not supported on the deployment resource, and can't be used to control invoke access." <https://cloud.google.com/apigee/docs/api-platform/security/iam/iam-overview>

### CORS

- **documented** — "The `AllowOrigins` field is a required policy element and the default should not be set to allow all (`*`)." Setting `Access-Control-Allow-Origin: *` "effectively disables the same-origin protection." <https://cloud.google.com/apigee/docs/api-platform/reference/policies/cors-policy>
- **documented** — Deployment errors: `InvalidMaxAge`, `MissingAllowOrigins`, `InvalidHTTPMethods`, `AllowHeadersSizeTooLarge`, `ExposeHeadersSizeTooLarge`. <https://cloud.google.com/apigee/docs/api-platform/reference/policies/cors-policy>

### TLS

- **documented** — "**Unsupported TLS versions:** Apigee does not support the use of TLS 1.0 or TLS1.1. If you use these protocols in your target endpoint configuration, the Apigee target endpoint throws the error `messaging.adaptors.http.flow.SslHandshakeFailed`." <https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls>
- **documented** — "**Note:** TLS 1.0 is not supported for Apigee Hybrid for southbound connections." <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>
- **documented** — "Apigee uses TLS exclusively" despite legacy `SSL` naming in elements and UI. <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>
- **documented** — **mTLS EKU restriction:** "Public Certificate Authorities (CAs) are discontinuing the inclusion of the `clientAuth` Extended Key Usage (EKU) in latest publicly-trusted SSL/TLS certificates. This industry-wide change affects Apigee mutual TLS (mTLS) configurations... Apigee requires the `clientAuth` EKU to be present in client certificates for mTLS handshakes. Without this EKU, mTLS connections will fail for both northbound (client to Apigee) and southbound (Apigee to backend) traffic." <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>
- **documented** — `<Enforce>true</Enforce>` fails connections for "targets with invalid certs, expired certs, self-signed certs, certs with a hostname mismatch, and certs with an untrusted root. A failure code of `4xx` or `5xx` is returned." If `<Enforce>` is true, `<IgnoreValidationErrors>` is ignored. <https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls>
- **documented** — SNI hostname mismatch cannot be ignored: "If the backend system uses SNI and returns a cert with a subject Distinguished Name (DN) that does not match the hostname, there is no way to ignore the error and the connection fails." <https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls>
- **documented** — `<Enabled>` default depends on URL: true for `https`, false for `http`. And from the config reference: if `<URL>` begins with `https://`, SSL is used even if `<Enabled>` is false and the whole `<SSLInfo>` block is ignored; conversely `http://` ignores `<Enabled>true</Enabled>`. <https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls> and <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>
- **documented** — "**Warning:** Apigee strongly recommends that you always use references to the keystore and truststore... If you upload a new certificate that does not use a reference but instead specifies the keystore name directly, the runtime Message Processors will **not** automatically detect the change. To resolve this, you must contact Google Cloud Support to restart your Message Processors, which may cause temporary service degradation." <https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls>
- **documented** — "**Note:** You cannot update an existing keystore or truststore to add a new certificate. You must create a new keystore/truststore when updating a certificate." <https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls>
- **documented** — Reference update requires creating a new keystore with a **new name** and an alias with the **same name as the old alias**; for a truststore create a new truststore with a new name and the alias name does not matter. <https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls>
- **documented** — "**Note:** If a cert is part of a chain, then you must either create a single file containing all the certs and upload that file to a single alias, or upload all certs in the chain separately to the truststore using a different alias for each cert." <https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls>
- **documented** — "**Note:** You can only use a reference to the keystore and truststore; you cannot use a reference to the alias. When you change the reference to a keystore, ensure that the alias name of the cert is the same as in the old keystore." <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>
- **documented** — "**Note:** Variable replacement of TLS/SSL values can only be used for a target endpoint. Any attempt to use variables in any other context, such as message logging, will cause validation failures." <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>
- **documented** — `<SSLInfo.Enforce>` can override `<Enforce>` at the environment level via a feature flag. <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>
- **documented** — TLS flow variables: `tls.cipher`, `tls.protocol`, `tls.server.name`, `tls.session.id`. Two-way TLS adds `tls.client.s.dn`, `tls.client.i.dn`, `tls.client.raw.cert`, `tls.client.cert.serial`, `tls.client.cert.fingerprint`. "**Note:** Enabling mTLS only applies to Apigee hybrid." <https://cloud.google.com/apigee/docs/api-platform/security/tls-vars>
- **documented** — Hybrid ingress mTLS config (K8s secret form): `virtualhosts[].tlsMode: MUTUAL`, `sslSecret`, optional `minTLSProtocolVersion` / `maxTLSProtocolVersion`. The alternative form uses `caCertPath`, `sslCertPath`, `sslKeyPath`. "Either `sslCertPath`/`sslKeyPath` or `sslSecret` is required." <https://cloud.google.com/apigee/docs/hybrid/latest/ingress-tls> and <https://cloud.google.com/apigee/docs/hybrid/latest/config-prop-ref>
- **documented** — Apigee root CA: "Each Apigee organization has a Google-managed root CA certificate... The Apigee root CA certificate has a long but finite validity period (typically 10 years)." Rotation is Google-controlled and happens in four stages (~1 year before expiry publish, ~60 days leaf cutover, ~30 days old withdrawn, at original expiry complete). <https://cloud.google.com/apigee/docs/api-platform/security/root-ca-rotation>
- **documented** — Root CA field: `caCertificates[]` (array) returns both current and new during rotation. "The deprecated `caCertificate` (singular) field returns only one certificate and does not surface the upcoming certificate during a rotation." <https://cloud.google.com/apigee/docs/api-platform/security/root-ca-rotation>
- **documented** — Post-cutover client error text: "`x509: certificate signed by unknown authority` or `SSL_ERROR_BAD_CERT_DOMAIN`". <https://cloud.google.com/apigee/docs/api-platform/security/root-ca-rotation>
- **documented** — Action is required only for clients that connect **directly** to the Apigee runtime (Internal routing TLS Option 2, or direct TCP to the instance ingress IP). A customer-managed LB that terminates TLS requires no action. <https://cloud.google.com/apigee/docs/api-platform/security/root-ca-rotation>
- **documented** — The root CA rotation page header says "*This page applies to **Apigee**, but not to **Apigee hybrid***." <https://cloud.google.com/apigee/docs/api-platform/security/root-ca-rotation>

### Keystores, truststores, aliases

- **documented** — Keystore name must match `[\w[:space:].-]{1,255}`. Alias name must match `[\w\s-.]{1,255}`. <https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.environments.keystores> and <https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.environments.keystores.aliases/create>
- **documented** — `aliases.create` `format` query parameter, exact valid values: `selfsignedcert`, `keycertfile`, or `pkcs12`. For `keycertfile`, `Content-Type: multipart/form-data` with `keyFile`, `certFile`, and `password`; **"If uploading to a truststore, omit `keyFile`."** For `pkcs12`, the file goes in the `file` field. For `selfsignedcert`, `Content-Type: application/json` with `CertificateGenerationSpec`. <https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.environments.keystores.aliases/create>
- **documented** — `aliases.create` also has `ignoreExpiryValidation` and `ignoreNewlineValidation` booleans. "If set to `true`, no error is thrown when the file contains a certificate chain with no newline between each certificate. Defaults to `false`." IAM permission required: `apigee.keystorealiases.create`. <https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.environments.keystores.aliases/create>
- **documented** — Alias methods available: `create`, `csr` (PKCS #10 Certificate Signing Request), `delete`, `get`, `getCertificate` (PEM form), `list`, `update`. <https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.environments.keystores.aliases>

---

## 3. OAUTH OPERATION VALUES

The exact allowed `<Operation>` values for the OAuthV2 policy, as listed under
`## <Operation> element`, **Valid values**.

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>

Opaque-token operations (7):

| Value | Documented meaning |
| --- | --- |
| `GenerateAccessToken` | Generates an access token. |
| `GenerateAccessTokenImplicitGrant` | Generates an access token for the implicit grant type. |
| `GenerateAuthorizationCode` | Generates an auth code. Used with the authorization code grant type. |
| `RefreshAccessToken` | Exchange a refresh token for a new access token. |
| `VerifyAccessToken` | Verifies that an access token sent in a request is valid. |
| `InvalidateToken` | Revokes an access token. Carries the 3-minute cache warning. |
| `ValidateToken` | Reinstates or "approves" an access token that was previously revoked. |

Additional JWT access token operations (4):

| Value | Documented meaning |
| --- | --- |
| `GenerateJWTAccessToken` | Generates an access token with a signed JWT. |
| `GenerateJWTAccessTokenImplicitGrant` | Generates an access token with a signed JWT for the implicit grant type. |
| `VerifyJWTAccessToken` | Verifies a signed JWT access token. |
| `RefreshJWTAccessToken` | Exchange a refresh token for a new JWT access token. |

Total: **11 allowed values.**

Defaulting behaviour, quoted: "If `<Operation>` is not specified, Apigee looks at the
list of `<SupportedGrantTypes>`. Only operations on those grant types will be
successful... If neither `<Operation>` nor `<SupportedGrantTypes>` are specified, the
default grant type is authorization_code. That is, authorization_code grant type
requests will succeed, but all others will fail."

Other policy Operation values, for contrast (different policies, do not mix up):

- BasicAuthentication: `Encode`, `Decode` — <https://cloud.google.com/apigee/docs/api-platform/reference/policies/basic-authentication-policy>
- AccessControl, HMAC, VerifyAPIKey, VerifyJWT, VerifyJWS, AccessControl have **no**
  `<Operation>` element. VerifyIAM has none either; its only elements are `<DisplayName>`
  and `<CredentialSource>`.

---

## 4. AUTH FAILURE DIAGNOSTIC TABLE

Match on the `errorcode` field, never on `faultstring` — stated on the policy pages
("the best practice is to trap the `errorcode` part of the error response. Do not rely
on the text in the `faultstring`, because it could change.")

### OAuthV2 runtime faults

Source for all rows: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>

| Fault code | HTTP | Cause | Thrown by |
| --- | --- | --- | --- |
| `steps.oauth.v2.access_token_expired` | 401 | Access token is expired. | VerifyAccessToken, InvalidateToken |
| `steps.oauth.v2.access_token_not_approved` | 401 | Access token was revoked. | VerifyAccessToken |
| `steps.oauth.v2.apiproduct_doesnot_exist` | 401 | Requested API product not in any product associated with the token. | VerifyAccessToken |
| `steps.oauth.v2.FailedToResolveAccessToken` | 500 | Variable named in `<AccessToken>` could not be resolved. | GenerateAccessToken |
| `steps.oauth.v2.FailedToResolveAuthorizationCode` | 500 | Variable named in `<Code>` could not be resolved. | GenerateAuthorizationCode |
| `steps.oauth.v2.FailedToResolveClientId` | 500 | Variable named in `<ClientId>` could not be resolved. | GenerateAccessToken, GenerateAuthorizationCode, GenerateAccessTokenImplicitGrant, RefreshAccessToken |
| `steps.oauth.v2.FailedToResolveRefreshToken` | 500 | Variable named in `<RefreshToken>` could not be resolved. | RefreshAccessToken |
| `steps.oauth.v2.FailedToResolveToken` | 500 | Variable named in `<Tokens>` could not be resolved. | ValidateToken, InvalidateToken |
| `steps.oauth.v2.InsufficientScope` | 403 | Token scope does not match the policy's scope. | VerifyAccessToken |
| `steps.oauth.v2.invalid_client` | 401 | Client ID invalid **with `<GenerateResponse>true</GenerateResponse>`**. | GenerateAccessToken, RefreshAccessToken |
| `steps.oauth.v2.InvalidRequest` | 400 | Multiple kinds of missing/incorrect request parameters. | Generate*/ Refresh* |
| `steps.oauth.v2.InvalidAccessToken` | 401 | Authorization header lacks the required `Bearer` word. | VerifyAccessToken |
| `steps.oauth.v2.InvalidAPICallAsNoApiProductMatchFound` | 401 | Executing proxy/operation is not in the token's Product. | VerifyAccessToken |
| `steps.oauth.v2.InvalidClientIdentifier` | 500 | Client ID invalid **with `<GenerateResponse>false</GenerateResponse>`**. | GenerateAccessToken, RefreshAccessToken |
| `steps.oauth.v2.InvalidParameter` | 500 | "The policy must specify either an access token or an authorization code, but not both." | GenerateAuthorizationCode, GenerateAccessTokenImplicitGrant |
| `steps.oauth.v2.InvalidTokenType` | 500 | `<Tokens>/<Token>` needs a type (e.g. `refreshtoken`); wrong type passed. | ValidateToken, InvalidateToken |
| `steps.oauth.v2.MissingParameter` | 500 | Response type is `token` but no grant types specified. | GenerateAuthorizationCode, GenerateAccessTokenImplicitGrant |
| `steps.oauth.v2.UnSupportedGrantType` | 500 | Grant type not in `<SupportedGrantTypes>`. **Known bug: the proxy does not enter the Error Flow.** | Generate*/ Refresh* |

### OAuthV2 JWT runtime faults (all 401)

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>

| Fault code | Cause |
| --- | --- |
| `oauth.v2.JWTSigningFailed` | Policy could not sign the JWT. (GenerateJWTAccessToken) |
| `oauth.v2.InvalidValueForJWTAlgorithm` | Algorithm absent from token or unsupported. |
| `oauth.v2.InsufficientKeyLength` | Key shorter than the minimum for HS384 or HS512. |
| `oauth.v2.JWTAlgorithmMismatch` | Generate algorithm ≠ Verify algorithm. "The algorithms specified must match." |
| `oauth.v2.JWTDecodingFailed` | JWT possibly corrupted. |
| `oauth.v2.MissingMandatoryClaimsInJWT` | Required claims absent. |
| `oauth.v2.InvalidJWTSignature` | Signature could not be verified or is invalid. |
| `oauth.v2.InvalidTypeInJWTHeader` | JWT type is not `at+Jwt`. |

For JWT **generation and refresh** flows, the policy page defers to RFC 6749 §5.2 Error
Response rather than listing codes.

### OAuthV2 deployment errors (error name, not fault code)

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>

`InvalidValueForExpiresIn`, `InvalidValueForRefreshTokenExpiresIn`, `InvalidGrantType`,
`ExpiresInNotApplicableForOperation`, `RefreshTokenExpiresInNotApplicableForOperation`,
`GrantTypesNotApplicableForOperation`, `OperationRequired`, `InvalidOperation`,
`TokenValueRequired`.
JWT-specific: `InvalidValueForAlgorithm`, `MissingKeyConfiguration`,
`EmptyValueElementForKeyConfiguration`, `InvalidKeyConfiguration`,
`EmptyRefAttributeForKeyconfiguration`, `InvalidVariableNameForKey`.

### VerifyAPIKey

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-api-key-policy>

| Fault code | HTTP | Cause |
| --- | --- | --- |
| `keymanagement.service.consumer_key_missing_api_product_association` | 400 | App credential has no API product association. |
| `keymanagement.service.DeveloperStatusNotActive` | 401 | Developer who created the app is inactive. |
| `keymanagement.service.invalid_client-app_not_approved` | 401 | Developer App is revoked. |
| `oauth.v2.FailedToResolveAPIKey` | 401 | Variable named in `<APIKey>` does not exist. Also returned instead of `ApiKeyNotApproved` for revoked/pending keys. |
| `oauth.v2.InvalidApiKey` | 401 | Key not found in the database — e.g. the key was regenerated. |
| `oauth.v2.InvalidApiKeyForGivenResource` | 401 | Key is valid but not an approved key for this proxy's Product. |

Deployment error: `SpecifyValueOrRefApiKey`.

### VerifyJWS (all 401)

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jws-policy>

| Fault code | Cause |
| --- | --- |
| `steps.jws.AlgorithmInTokenNotPresentInConfiguration` | Verify policy has multiple algorithms; token's alg not among them. |
| `steps.jws.AlgorithmMismatch` | Generate alg ≠ Verify alg. |
| `steps.jws.ContentIsNotDetached` | `<DetachedContent>` set but JWS has no detached payload. |
| `steps.jws.FailedToDecode` | JWS possibly corrupted. |
| `steps.jws.InsufficientKeyLength` | Key shorter than 32 bytes for HS256. |
| `steps.jws.InvalidClaim` | Missing claim/claim mismatch, or missing header/header mismatch. |
| `steps.jws.InvalidCurve` | Key curve invalid for the ECDSA algorithm. |
| `steps.jws.InvalidJsonFormat` | Invalid JSON in the JWS header. |
| `steps.jws.InvalidJws` | **JWS signature verification fails.** |
| `steps.jws.InvalidPayload` | JWS payload invalid. |
| `steps.jws.InvalidSignature` | `<DetachedContent>` omitted but JWS has a detached payload. |
| `steps.jws.KeyIdMissing` | Policy uses JWKS but the JWS header has no `kid`. |
| `steps.jws.KeyParsingFailed` | Public key could not be parsed. |
| `steps.jws.MissingPayload` | JWS payload missing. |
| `steps.jws.NoAlgorithmFoundInHeader` | JWS omits the algorithm header. |
| `steps.jws.NoMatchingPublicKey` | Policy uses JWKS and the `kid` is not listed in the JWKS. |
| `steps.jws.UnhandledCriticalHeader` | A header in the `crit` header is not listed in `<KnownHeaders>`. |
| `steps.jws.UnknownException` | Unknown exception. |
| `steps.jws.WrongKeyType` | e.g. RSA key for an ECDSA algorithm, or a curve key for RSA. |

Fault variable: `jws.<policy_name>.failed` — "All JWS policies set the same variable".

### VerifyIAM

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-iam-policy>

| Fault code | HTTP | Cause |
| --- | --- | --- |
| `steps.verifyiam.CredentialSourceRefUnresolved` | 400 | Flow variable in CredentialSource could not be resolved. |
| `steps.verifyiam.CredentialValueNotProvided` | 400 | Credential not found, including in the default Authorization header location. |
| `steps.verifyiam.Forbidden` | 403 | Lacks permissions/scopes, or other related issue. |
| `steps.verifyiam.Unauthorized` | 401 | Credential invalid or expired. |
| `steps.verifyiam.MiscellaneousAuthorizationConfigurationError` | 500 | Issue with the auth request to IAM. |
| `steps.verifyiam.UnexpectedAuthorizationInfrastructureError` | 500 | Internal error. |

Fault variable: `verifyiam.<policy_name>.failed`.

### BasicAuthentication

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/basic-authentication-policy>

| Fault code | HTTP | Cause |
| --- | --- | --- |
| `steps.basicauthentication.InvalidBasicAuthenticationSource` | 500 | Base64 string invalid, or header malformed (e.g. does not start with `Basic`). |
| `steps.basicauthentication.UnresolvedVariable` | 500 | Required source variables absent; only when `IgnoreUnresolvedVariables` is false. |

### HMAC (all 401)

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/hmac-policy>

`steps.hmac.UnresolvedVariable`, `steps.hmac.HmacVerificationFailed`,
`steps.hmac.HmacCalculationFailed`, `steps.hmac.EmptySecretKey`,
`steps.hmac.EmptyVerificationValue`.

Deployment errors: `steps.hmac.MissingConfigurationElement`,
`steps.hmac.InvalidValueForElement`, `steps.hmac.InvalidSecretInConfig`,
`steps.hmac.InvalidVariableName`.

### AccessControl

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/access-control-policy>

`accesscontrol.IPDeniedAccess`, `accesscontrol.InvalidIPAddressInVariable`.
No policy-specific deployment errors listed.

### Other OAuth info policies

Sources: the respective policy pages under `/apigee/docs/api-platform/reference/policies/`.

- GetOAuthV2Info — `steps.oauth.v2.access_token_expired`, `authorization_code_expired`, `invalid_access_token`, `invalid_client-invalid_client_id`, `invalid_refresh_token`, `invalid_request-authorization_code_invalid`, `InvalidAPICallAsNoApiProductMatchFound`, `refresh_token_expired`.
- SetOAuthV2Info — `steps.oauth.v2.access_token_expired`, `invalid_access_token`, `InvalidAPICallAsNoApiProductMatchFound`.
- DeleteOAuthV2Info — `steps.oauth.v2.invalid_access_token`, `invalid_request-authorization_code_invalid`, `InvalidAPICallAsNoApiProductMatchFound`.
- RevokeOAuthV2 — `steps.oauth.v2.InvalidFutureTimestamp`, `InvalidEarlyTimestamp`, `InvalidTimestamp`, `EmptyAppAndEndUserId`.

### Status codes on the deprecated HTTP reference page

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauth-http-status-code-reference>

This page is **deprecated** but is the only place the raw `keymanagement.service.*`
wire codes and their statuses are listed. Notable and easy to mis-apply:

| Symptom | Status | `errorcode` |
| --- | --- | --- |
| Invalid access token (Verify) | 401 | `keymanagement.service.invalid_access_token` |
| Invalid access token (GetOAuthV2Info / SetOAuthV2Info) | **404** | `keymanagement.service.invalid_access_token` |
| Expired access token | 401 (Verify) / **500** (Get/Set OAuthV2Info) | `keymanagement.service.access_token_expired` |
| Access token revoked | 401 | `keymanagement.service.access_token_not_approved` |
| Insufficient scope | 403 | `steps.oauth.v2.InsufficientScope` |
| Missing Bearer prefix | 401 | `oauth.v2.InvalidAccessToken` |
| Invalid resource | 401 | `keymanagement.service.apiresource_doesnot_exist` |
| No API product match | 401 | `keymanagement.service.InvalidAPICallAsNoApiProductMatchFound` |
| DeleteOAuthV2Info failure | 404 | varies by token vs auth code |

**Caution — documented inconsistency.** For the same logical conditions, the OAuthV2
policy page documents the `steps.oauth.v2.*` form while this deprecated page documents
`keymanagement.service.*`. Both are on verified URLs. I did not execute either, so
**hypothesis**: the deprecated page reflects legacy/Edge naming and the policy page
reflects current naming, and a real trace will show one or the other depending on the
flow. Do not assume the prefix; read the actual `errorcode` from the response.

---

## 5. TLS RESTRICTIONS AND GOTCHAS

1. **TLS 1.0 and 1.1 are unsupported.** Target endpoints configured with them fail with
   `messaging.adaptors.http.flow.SslHandshakeFailed`. Hybrid southbound also blocks TLS 1.0.
   <https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls>,
   <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>
2. **mTLS requires the `clientAuth` EKU on client certificates.** Public CAs are dropping
   it. Without it, mTLS fails in **both** directions (northbound client→Apigee and
   southbound Apigee→backend). This is the single most likely cause of a "suddenly broken
   mTLS after a CA renewal".
   <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>
3. **SNI DN mismatch cannot be worked around.** `IgnoreValidationErrors` will not help;
   the connection fails. <https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls>
4. **`Enforce=true` silently overrides `IgnoreValidationErrors`.** Setting both is a
   contradiction that resolves in favour of `Enforce`.
   <https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls>
5. **An `https://` URL overrides `<Enabled>false</Enabled>`** and causes the whole
   `<SSLInfo>` block to be ignored. Likewise `http://` ignores `<Enabled>true</Enabled>`.
   <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>
6. **You cannot add a cert to an existing keystore or truststore.** Cert rotation means
   creating a new store. Direct-name (non-reference) stores additionally require a
   Message Processor restart via Google Cloud Customer Care, with temporary service
   degradation. <https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls>
7. **Alias names must be preserved across a keystore swap** when using references; a
   reference cannot point at an alias, only at the keystore/truststore. Truststore alias
   names do not matter. <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>
8. **Chain certs need either one concatenated file per alias, or one alias per cert.** A
   single file must have the leaf first, then the chain in order to the CA, with a blank
   line between certs. <https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls>
9. **Truststore upload via `keycertfile` must omit `keyFile`.** Sending a key to a
   truststore is the wrong shape. <https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.environments.keystores.aliases/create>
10. **Cert chains with no newline between certificates are rejected by default.** Use
    `ignoreNewlineValidation=true` on alias create.
    <https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.environments.keystores.aliases/create>
11. **TLS/SSL variable substitution is target-endpoint only.** Using it anywhere else,
    including message logging, causes validation failures.
    <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>
12. **`tls.client.*` flow variables and ingress mTLS are Apigee hybrid only.** `tls.cipher`,
    `tls.protocol`, `tls.server.name`, `tls.session.id` apply to both.
    <https://cloud.google.com/apigee/docs/api-platform/security/tls-vars>
13. **Root CA rotation is Apigee X only** ("applies to Apigee, but not to Apigee hybrid"),
    and only bites clients connecting directly to the runtime. Clients behind a
    customer-managed terminating load balancer are unaffected.
    <https://cloud.google.com/apigee/docs/api-platform/security/root-ca-rotation>
14. **`caCertificate` (singular) is deprecated** and will not show the upcoming root CA
    during rotation. Read `caCertificates[]`.
    <https://cloud.google.com/apigee/docs/api-platform/security/root-ca-rotation>
15. **VerifyIAM does not exist on hybrid.** Any hybrid IAM-auth design is blocked.
    <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-iam-policy>
16. **Alias create accepts only `selfsignedcert`, `keycertfile`, `pkcs12`.** No `keycertjar`
    in the current REST reference. (The Edge apidocs site mentions `keycertjar`; that is
    an Edge-only page I did not verify as an Apigee X URL.)
    <https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.environments.keystores.aliases/create>

### Hybrid TLS operational signals (ApigeeIssue reasons)

Sources: the four playbook pages listed in section 1, all 200.

| Reason string | Meaning | Playbook |
| --- | --- | --- |
| `AIS_INGRESS_MTLS_CA_CERT_EXPIREY` | Ingress mTLS CA expired or expiring within 14 days | ca-cert-expiry |
| `AIS_INGRESS_MTLS_CA_CERT_INVALID` | Ingress mTLS CA cert invalid | ca-cert-invalid |
| `AIS_INGRESS_CERT_EXPIREY` | Ingress serving cert expired | ingress-cert-expiry |
| `AIS_INGRESS_CERT_MISMATCH` | Ingress private key and cert do not match | ingress-cert-mismatch |

Inspect with `kubectl -n apigee get apigeeissues` and `kubectl -n apigee describe apigeeissue <NAME>`.
`ApigeeRouteConfig` name format is `<org>-<virtualhost name>`.

Client-visible TLS failure signatures (documented):
`ECONNRESET`, `Connection reset by peer`, `SSL_ERROR_SYSCALL`,
`curl: (35)`, `x509: certificate signed by unknown authority`, `SSL_ERROR_BAD_CERT_DOMAIN`.

---

## 6. 404 / NOT FOUND

URLs tried that returned **404** (recorded, do not cite):

- <https://cloud.google.com/apigee/docs/api-platform/system-administration/configuring-ssl>
  (that is an Apigee **Edge** path, on `docs.apigee.com`, not cloud.google.com)
- <https://cloud.google.com/apigee/docs/api-platform/security/keystores>
- <https://cloud.google.com/apigee/docs/api-platform/system-administration/keystores>
- <https://cloud.google.com/apigee/docs/api-platform/develop/endpoint-attachments>
- <https://cloud.google.com/apigee/docs/api-platform/deploy/endpoint-attachment-configuration>
- <https://cloud.google.com/apigee/docs/api-platform/develop/target-endpoint-configuration>
- <https://cloud.google.com/apigee/docs/api-platform/publish/creating-and-publishing-api-products>
- <https://cloud.google.com/apigee/docs/api-platform/security/tls>
- <https://cloud.google.com/apigee/docs/api-platform/system-administration/tls>
- <https://cloud.google.com/apigee/docs/sitemap.xml> (404; no sitemap available, so the
  link tree must be mined from page HTML instead)

Not 404 but also not usable content — these return **200** and are stub pages:

- <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/runtime/hmac-runtime-errors>
  — 200, 1192 bytes, body reads "## The equivalent page does not exist in Apigee."
- <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/runtime/verify-JWT-runtime-errors>
  — 200, 1192 bytes, same stub. Note the capitalisation in the path (`verify-JWT`).
- <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/deployment/apigee-serving-cert-not-found-or-expired>
  — 200, 253 bytes, effectively empty.
- <https://cloud.google.com/apigee/docs/api-platform/security/encryption-keys> — 200,
  1200 bytes; title and body were lost to the `fetch.sh` awk. Treat as unverified
  content; the URL itself is real.
- <https://cloud.google.com/apigee/docs/api-platform/security/tls-vars> — 200 but the
  title line was lost to the same awk. Content below the title is intact and was read.
- <https://cloud.google.com/apigee/docs/api-platform/security/oauth/hashing-tokens> —
  200, 812 bytes. Likely another stub; I did not confirm its body.

### Known gaps — things I could NOT verify

- **No dedicated Apigee X prose page for creating keystores/truststores/aliases exists
  at a URL I could find.** The nav sidebar (2445 links, extracted from live HTML) contains
  no keystore topic page under `api-platform`. The authoritative content on cloud.google.com
  is the **REST API reference** (`organizations.environments.keystores*`), which I did
  verify. The richer prose versions ("Creating keystores and truststores using the Edge
  management API", "Update a TLS certificate for the Cloud") live on `docs.apigee.com`
  and describe **Apigee Edge**, a different product — do not apply them to Apigee X
  without saying so. I did not fetch those URLs.
- **`basic-auth-policy` does not exist**; the page is `basic-authentication-policy`.
  Consistent with the recipe's warning.
- The `VerifyJWT` policy page is **truncated upstream**: it ends mid-table after the word
  "Algorithm" with no element reference and no `## Error reference` section. This is a
  Google documentation defect, not an extraction problem. Anyone needing VerifyJWT element
  details or fault codes must use the VerifyJWS page, which carries the `steps.jws.*`
  codes. **Unverified** whether VerifyJWT emits `steps.jwt.*` codes that appear nowhere in
  the published docs.
- TLS **pass-through** (TLS origination vs passthrough on virtual hosts) is **not covered
  by any Apigee X page I verified**. `api-platform/system-administration/options-configuring-tls`
  is explicitly scoped: "This section shows how to configure TLS for traffic from a proxy
  to a target." Northbound virtual-host TLS termination is referenced only obliquely via
  the root-CA rotation page. I found no verified page documenting `<VirtualHost>` TLS
  elements for Apigee X.
- I did not verify any **CORS** wire-level status behaviour beyond the deployment errors.
- I did not verify the `<ExpiresIn>` / token lifetime **minimum** or maximum values, only
  that they must be positive integers in milliseconds.
