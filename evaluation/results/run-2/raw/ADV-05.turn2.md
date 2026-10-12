# Confirmed: the element does not exist, and there is an InvalidateCache policy

**That settles it.** `<invalidateOnHeaderChange>` is not a ResponseCache element, and the
policy page does not talk about invalidation at all. What you have is a configuration that
cannot do what it looks like it does, which means the staleness you are seeing was never being
addressed by it.

The last sentence of your evidence is the useful one: **cache invalidation is handled by a
separate InvalidateCache policy.** That is the answer to your question, and it is a different
policy from the one you have been configuring.

I gave you three levers on the last turn and two of them are still right. What I did not have
was the policy that does the thing you actually asked for, and you have now supplied it.

## What to do

1. **Remove `<invalidateOnHeaderChange>` from the policy.** Leaving an element the schema does
   not define in place is how this will happen again, and if your deployment did accept it
   silently then you have a false sense of configuration you no longer have.
2. **Decide between the InvalidateCache policy and key separation, not both blindly.**
   - If your header means "this value must never see a cached entry again" (a user, a tenant, a
     permission change), put the header in `<CacheKey>` as a `<KeyFragment ref="...">`. A request
     carrying a new value cannot read the old entry, and it never needed invalidating.
   - If something outside the request needs to drop an entry now (an admin action, a deploy, a
     data correction), that is what the InvalidateCache policy is for. It is driven by an entry
     you name, so you have to know which entry. Read its reference for your version before you
     script it; I have not opened that page in this session and I am not going to describe its
     elements from memory.
3. **Set `<ExpirySettings><TimeoutInSeconds>` to bound staleness regardless.** This is the
   cheap mitigation and it is worth having while you work out which of the two above you need.
   Test it outside production first.

## One thing to check about your current behaviour

If the element was rejected at deploy time and you have been deploying with `continueOnError`,
or if a tool wrote the file without the runtime ever validating it, then the policy you think
you are running may not be the policy that is running. Send me the revision's deployment state
and the effective policy XML, and I will confirm you are getting what you expect before you
build anything on top of it.

## How to confirm

After the change, send two requests to the same resource: one with the header value you expect
to be current and one with the previous value, and check you get the behaviour you intended for
each. With key separation, the old value keeps serving its own entry until it expires, and that
surprise is worth designing for now rather than discovering later.

## What I still could not determine

Whether the element was rejected or ignored at deploy time, which needs the deployment record,
and what your header represents, which decides whether you want InvalidateCache at all or just
a better cache key.