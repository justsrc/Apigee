# Authentication, tokens and TLS

Verified facts with their source URLs. Full research, including what could not be
verified, is in `research/notes-security.md`.

Match on the `errorcode` from the response body, never on the `faultstring` prose.
Google states the prose can change between releases.

## OAuth 2.0

The OAuthV2 policy takes an `<Operation>`. There are exactly eleven, and guessing an
operation name is a common failure because several read plausibly.

Opaque token operations: `GenerateAccessToken`, `GenerateAccessTokenImplicitGrant`,
`GenerateAuthorizationCode`, `RefreshAccessToken`, `VerifyAccessToken`, `InvalidateToken`,
`ValidateToken`.

JWT operations: `GenerateJWTAccessToken`, `GenerateJWTAccessTokenImplicitGrant`,
`VerifyJWTAccessToken`, `RefreshJWTAccessToken`.

Fault names on the OAuthV2 page use the prefix `steps.oauth.v2.`, for example
`steps.oauth.v2.InvalidClient`. The JWT access token faults use a shorter `oauth.v2.`
prefix, for example `oauth.v2.InvalidJWTSignature`. Do not assume a prefix. Read the
actual `errorcode`.

Three things that generate most OAuth tickets:

**Revocation is not immediate.** Tokens are cached for three minutes, so a revoked token
can still succeed for up to three minutes. A report of "I revoked it and it still works"
is usually this, not a failed revocation. Wait out the cache before concluding.

**Status codes vary by policy, not by the logic.** The same bad access token returns 401
from `VerifyAccessToken` but 404 from `GetOAuthV2Info` or `SetOAuthV2Info`. An expired
token returns 401 from `VerifyAccessToken` and 500 from the info policies. Match the
status to the operation that produced it.

**The authorization code grant needs four policies**, not one. Generating the code,
generating the access token, validating the code, and generating the refresh token are
separate OAuthV2 policies. A partially wired flow fails at whichever one is missing.

The default token source for `VerifyAccessToken` is the `Authorization` header with the
`Bearer` prefix stripped. Overriding with `<AccessToken>` also switches off prefix
matching unless `<AccessTokenPrefix>` is set, so a token that starts working only when
the prefix is removed usually means the override is in play.

Only OAuth 2.0 Bearer tokens are supported. MAC tokens are not.

Source: <https://cloud.google.com/apigee/docs/api-platform/reference/policies/oauthv2-policy>

## JWT and JWS

`<Algorithm>` (singular) means a signed JWT. `<Algorithms>` (plural) means an encrypted
one. Confusing the two is a frequent deployment failure and the error message does not
always make it obvious.

Supported signature algorithms are exactly `RS256, RS384, RS512, PS256, PS384, PS512,
ES256, ES384, ES512, HS256, HS384, HS512`. Anything else fails at deployment with
`InvalidAlgorithm`.

HMAC minimum key lengths: HS256 32 bytes, HS384 48 bytes, HS512 64 bytes.

**JWKS requires a `kid`.** If the inbound JWT has no key ID in the header, Apigee throws a
fault because it cannot map `kid` to a verification key. A missing `kid` after an
identity provider upgrade is a common real failure, and the token looks structurally fine.

**Supplying a certificate as the public key skips trust-chain and expiry checks.** The
public key inside is treated as valid and trusted. Worth telling people when they ask why
their revoked signing certificate still validates.

`InvalidVariableNameForKey` at deployment means the flow variable name used in a `ref`
attribute does not contain the `private` prefix. The prefix is required by the
configuration, not by the person reading it.

VerifyIAM is documented as unavailable on Apigee hybrid. It must be the first policy in
the request flow, typical latency is 10 to 50 ms, and it accepts at most 1,500 role
bindings per policy.

Sources:
<https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-jwt-policy>,
<https://cloud.google.com/apigee/docs/api-platform/reference/policies/jwt-policies-overview>

## TLS

TLS 1.0 and 1.1 are not supported. A target endpoint configured with them fails with
`messaging.adaptors.http.flow.SslHandshakeFailed`, which looks like a network fault and
is not one. Hybrid also blocks TLS 1.0 southbound.

**Mutual TLS needs the `clientAuth` extended key usage on the client certificate.**
Without it, mTLS fails in both directions, client to Apigee and Apigee to backend. Public
CAs are discontinuing the usage, so an mTLS integration that breaks after a CA renewal
usually broke because the renewed certificate stopped carrying it. Check the EKU before
anything else.

`IgnoreValidationErrors` does not rescue an SNI DN mismatch. The connection still fails.

`Enforce=true` silently wins over `IgnoreValidationErrors` when both are set. If someone
set both expecting the lenient one to apply, that is the bug.

An `https://` target URL overrides `<Enabled>false</Enabled>` and the rest of the
`<SSLInfo>` block is ignored. The reverse holds for `http://`. This makes a target that
"should not be using TLS" quietly use it.

TLS variable substitution works only in a target endpoint. Using it in message logging or
anywhere else causes validation failures. The `tls.client.*` variables and ingress mTLS
are hybrid only, while `tls.cipher`, `tls.protocol`, `tls.server.name` and
`tls.session.id` apply to both products.

Certificate rotation cannot be done in place. You cannot add a certificate to an existing
keystore or truststore, so rotation means creating a new store. Alias names must be
preserved across that swap when references are used, because a reference points at the
store, not at an alias. Direct-name stores need a Message Processor restart through
Google Cloud Customer Care, with temporary service degradation, which makes it a planned
change rather than something to attempt during an incident.

Sources:
<https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls>,
<https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>

## Known documentation gaps

The VerifyJWT policy page is truncated upstream and ends mid-table with no element
reference and no error reference. `steps.jwt.*` fault codes do not appear in published
documentation anywhere this project could verify. Treat a `steps.jwt.*` code as
unverified rather than quoting it confidently.

There is no Apigee X prose page for creating keystores, truststores or aliases. The
authoritative content is the Management API reference. The richer prose on
`docs.apigee.com` is Apigee Edge, which is a different product, so do not transfer its
instructions to Apigee X.