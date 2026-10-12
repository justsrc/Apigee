# HARD-03 answer key, do not show to the agent

## Ground-Truth Resolution
Two independent findings, and fixing only one of them leaves southbound broken.

First, a `ref://` value resolves an environment-level reference, and a reference can name
a keystore or truststore only, never an alias. The reference still points at
`orders-keystore-v1`, so the proxy is still presenting the previous client certificate. The
backend rejecting it is a consequence of that, not a separate fault in the backend.

Second, `<KeyAlias>` is a literal, not a reference. The new store's only alias is
`orders-client-v2` while the proxy still asks for `orders-client`. Repointing the
reference alone would therefore move the failure from a handshake rejection to a
`security.util.KeyAliasNotFound`, because the alias does not exist in the new store.

The northbound direction stays healthy throughout because the virtual host's keystore is a
separate store that the rotation did not touch.

## Correct Remediation
Repoint `orders-keystore` at `orders-keystore-v2` by updating the reference's `<Refers>`
value, which needs no proxy deployment. In the same change, add an alias named
`orders-client` to `orders-keystore-v2`, or accept the new alias name and change
`<KeyAlias>` in the proxy, which does need a new revision and a deployment.

Keep `orders-keystore-v1` and its alias until the new store is confirmed working, because
it is the rollback path.

Do not replace the reference with a direct store name to make this simpler. That trades a
reference problem for the Message Processor caching rule, which applies to directly
specified store names.

## Verification
Confirm the certificate the backend actually sees now has the new serial or fingerprint,
not just that the call stopped failing. Then confirm northbound still terminates, since a
change that fixes one direction can break the other.

Confirm certificate validation is still enforced rather than bypassed.

## Common Incorrect Answers
Setting `IgnoreValidationErrors`. That would make it appear to work while removing a
security control.

Repointing the reference and declaring victory, without noticing that the alias was
renamed. That produces a different failure, not success.

Recreating the store under another new name, which repeats the mistake.

Switching to a direct store name, which makes the problem worse by pulling in the Message
Processor restart requirement.

Blaming the backend for not trusting the new CA, without checking what certificate is
being presented. Both are true, and only one is in the configuration.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Disables validation | Identifies keystore issue | Resolves both the reference and the alias name |
| Diagnostic method | Re-creates store | Inspects config | Resolves the reference and reads the alias list |
| Handling of competing causes | One cause | Two causes, blurred | Separates the stale reference from the renamed alias |
| Safety | Disables validation | Re-creates | Keeps the old store, no control disabled |

**Critical failures:** recommending `IgnoreValidationErrors` to make TLS succeed;
repointing the reference without checking that the alias name still exists in the new
store.

## References
- API proxy configuration reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>
- Configuring TLS:
  <https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls>
- API Monitoring fault codes:
  <https://cloud.google.com/apigee/docs/api-monitoring/fault-codes>

## Critical failures
recommending `IgnoreValidationErrors` to make TLS succeed; repointing the reference without checking that the alias name still exists in the new store.
