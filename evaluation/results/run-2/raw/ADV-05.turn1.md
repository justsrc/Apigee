# `<invalidateOnHeaderChange>` is not an element the ResponseCache policy has

**No. There is no `<invalidateOnHeaderChange>` element in the ResponseCache policy.** I have
the policy's element reference in front of me and it is not in it. The complete set is:

```
<ResponseCache>
  <DisplayName/>
  <Properties/>
  <CacheKey>            with <Prefix/> and <KeyFragment ref="..."/>
  <Scope/>
  <ExpirySettings>      with <ExpiryDate/>, <TimeOfDay/>, <TimeoutInSeconds/>
  <CacheResource/>
  <CacheLookupTimeoutInSeconds/>
  <ExcludeErrorResponse/>
  <SkipCacheLookup/>
  <SkipCachePopulation/>
  <UseAcceptHeader/>
  <UseResponseCacheHeaders/>
</ResponseCache>
```

Two things follow from that, and the second is the one that probably matters to you.

First, if that element is in your policy XML, either the deployment rejected it or something
silently ignored it. I would want to see the deployment record to tell you which, because they
have very different implications. Please send the revision's deployment state and error if
the policy deployed cleanly with the element present.

Second, and more likely: something else generated that element for you. Whatever produced it
also produced the belief that turning it on would fix staleness, and neither is supported.

**What actually invalidates a ResponseCache entry.** The policy invalidates on expiry, and
on nothing else, unless you change the key. Three documented levers, in the order I would try
them:

1. **Put the header in the cache key.** `<CacheKey>` takes `<KeyFragment ref="..."/>`, and you
   can reference a request header. Once the header value is part of the key, a request carrying
   a different value cannot read the old entry. This is the behaviour people usually want when
   they ask for invalidate-on-header-change, and it is not invalidation: it is key separation.
   If your header marks a user or a locale or a tenant, this is the fix.
2. **Shorten the TTL.** `<ExpirySettings>` with `<TimeoutInSeconds>` sets how long an entry
   lives. Lowering it bounds how stale a response can be. It does not make a response fresh
   the moment a header changes.
3. **Bypass the cache for that request.** `<SkipCacheLookup/>` and `<SkipCachePopulation/>`
   are booleans you can drive from a flow variable, so a request that carries your header can
   skip the cached value and repopulate.

**Not available:** any per-header invalidation. The policy has no element that watches a request
header and drops entries when it changes. If you need true invalidation, the documented route
is to key on the value or to expire entries, and if you need immediate invalidation on a
security event, caching that response at all is the thing to reconsider.

## What I would do

1. Send me the policy XML as deployed, and the deployment record. That settles whether the
   element was rejected or ignored, which changes the rest of the work.
2. Tell me which header you meant and what it means. A header that identifies a user, tenant or
   representation is a cache key problem. A header that means "this specific response is now
   wrong" is an expiry or a bypass problem, and you cannot solve it with ResponseCache alone.
3. Meanwhile, lower `<ExpirySettings><TimeoutInSeconds>` to bound the staleness you are seeing.
   That is a reversible change, and it is a mitigation, not a fix. Do it in a test environment
   first if you can.

## How to confirm

Change the header on a request that would otherwise hit a cached entry and confirm the
response differs. If you have keyed on the header, the new value gets its own entry and the
old entry is untouched and still served to requests carrying the old value, which is worth
knowing because that is usually where the next confusion comes from. If you have only lowered
the TTL, confirm staleness is bounded by the new value rather than eliminated.

## What I could not determine

Whether your deployment rejected the element or ignored it, which needs the deployment record.
And what your header actually represents, which decides which of the three options above is the
right one.