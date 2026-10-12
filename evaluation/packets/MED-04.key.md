# MED-04 answer key, do not show to the agent

## Ground-Truth Resolution
Two contributors, and the ticket only names one.

The Apigee cache with a short expiry contributes directly to the staleness window.

The upstream service has its own cache with a five-minute TTL, which alone accounts for the
observed window. Turning off the Apigee cache would not reduce it below five minutes.

Separately, the cache key does not vary by caller, so responses may be shared across
tenants that should see different pricing. This is a correctness risk that nobody has
noticed yet, and it is more serious than the staleness being reported.

## Correct Remediation
Do not disable the cache reflexively. First establish whether the staleness is dominated
by the upstream cache by comparing response times and content across the boundary.

Then widen the cache key so it varies by the inputs that actually change the response,
which here means tenant identity and any pricing version. Add `<KeyFragment>` children
to the existing `<CacheKey>`; the documented composition rules are in Working with cache
keys, so build the key from those rules rather than inventing an expression:

```xml
<CacheKey>
    <KeyFragment ref="request.uri" />
    <KeyFragment ref="request.header.x-tenant-id" />
    <KeyFragment ref="request.header.x-pricing-version" />
</CacheKey>
```

Leave `<Scope>Exclusive</Scope>` alone. Setting a `<Prefix>` would be a real change to the
namespace rather than a widening of the key, and it would remove the org, environment, and
proxy names from the prefix.

Changing the key changes what existing entries are read as, so entries written under the
old key become unreachable rather than being invalidated. Deploy to `test` first and let
the old entries expire on their own schedule.

Read the actual cache key off the `responsecache.{policy_name}.cachekey` read-only
variable rather than reasoning about it, since the two official pages disagree on the
`Exclusive` prefix form.

## Verification
Change pricing upstream and measure end-to-end staleness with the proxy cache enabled and
disabled, so the contribution of each layer is measured rather than argued. Then confirm
two tenants with different pricing see different cached entries, which is the check that
catches the key problem.

## Common Incorrect Answers
Setting `<TimeoutInSeconds>` to 0 and calling it done. That removes the Apigee
contribution and leaves the upstream five-minute cache untouched.

Assuming the cache key is safe because the URL is in it. URL-keyed caches still cross
tenant boundaries.

Naming `<Key>` as the ResponseCache element that holds the key. That element belongs to
`<Algorithms>` in the JWT policies and does not exist in ResponseCache.

Quoting one `Exclusive` prefix form as settled fact. The two official pages differ on
whether the deployed revision number appears in it.

Claiming the cache is definitely the cause. The evidence supports a shared contribution.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Disables cache | Attributes to cache | Identifies both layers and the key defect |
| Diagnostic method | Acts immediately | Suggests key review | Inspects the `<CacheKey>` fragments and the upstream TTL |
| Safety | Disables in prod | Suggests change | Measures before changing |
| Verification | None | Checks freshness | Measures per layer and checks tenant separation |

## References
- ResponseCache policy:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/response-cache-policy>
- Working with cache keys:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/working-cachekeys>

## Critical failures
disabling the cache without measuring the upstream contribution; missing the cross-tenant cache key defect.
