# MED-23 answer key, do not show to the agent

## Ground-Truth Resolution
The linter is not producing a false positive about the cache; it is producing an unhelpful
finding about the bundle. With the default scope, a PopulateCache in one proxy and a LookupCache
in another can never meet. So the rule is doing its job, and the customer's design is a latent
defect that the linter has now made visible.

What the linter cannot see is the case the customer actually has. Non-global scopes resolve to
the proxy, not the shared flow. Two different shared flows attached to the same proxy can share
cache keys under the `Application`, `Proxy` and `Target` scopes, and two different proxies cannot.
The documentation does not state this anywhere, and the customer is asking about exactly this
point.

The linter rule itself was raised as a false positive in the real report and the maintainers
decided not to change it. Their reasoning is the answer to "is it safe to disable this": a plugin
that requires a PopulateCache inside the same bundle cannot be correct in any environment large
enough for the populate and the lookup to live in different places, so the only honest options
are to disable the rule or to accept the finding.

## Correct Remediation
Decide the sharing model explicitly and encode it in `<Scope>` or `<Prefix>`, then disable the
rule for these proxies rather than adding a PopulateCache that writes keys nobody reads.

If reads must cross proxy boundaries, the scope has to be shared. `<Scope>Global</Scope>` shares
the key across every proxy deployed in the environment. `<Prefix>` also works and takes precedence
over `<Scope>`, so it can be used when the shared key must be explicitly named.

If reads stay inside one proxy, leave the default and disable the rule. Do not add a PopulateCache
to proxy B to satisfy the linter; that policy would run on every request in B and populate keys
that B never looks up.

## Verification
Confirm the scope on every participating policy, then confirm the runtime agrees by populating
from one proxy and reading from the other, checking that the assigned variable is populated on
the read leg. A LookupCache that finds nothing leaves the target variable unset rather than
setting it to null, so absence of the variable is the expected failure signal.

Then confirm the rule no longer fires, or that it is excluded for these proxies.

## Common Incorrect Answers
Adding a PopulateCache policy to the bundle the linter complained about. It satisfies the rule and
does not fix the cache, because the two policies still produce different keys.

Deleting the LookupCache because it has no populate. The rule says the bundle is incomplete, not
that the read is pointless.

Assuming the linter is simply broken because it is inconvenient. In the default scope the finding
is correct.

Treating `Global` as the only fix and applying it everywhere. A global scope widens the key
namespace across every proxy in the environment, and the maintainers state that its counting and
behaviour differ from the default; that is a design change, not a lint fix.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Adds a PopulateCache to silence the rule | Identifies scope as the variable | Establishes the default scope makes the keys disjoint and explains why Global or Prefix is needed |
| Diagnostic method | Turns the rule off | Reads the CacheKey element | Establishes the effective scope on both policies and the resulting key namespaces |
| Handling of the finding | Calls it a false positive | Notes the bundle is the wrong unit | Says the finding is correct for the default scope and the real defect is the unstated sharing model |
| Quality of next step | Silences the rule | Adds Scope Global | Encodes the intended scope and excludes the rule for those proxies, without adding a dead populate |

## References
- Real report, maintainer decision not to fix, and the unanswered question about non-global
  scope in shared flows:
  <https://github.com/apigee/apigeelint/issues/480>
- LookupCache policy, Scope element and acceptable values:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/lookup-cache-policy>
- Working with cache keys:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/working-cachekeys>

## Critical failures
adding a PopulateCache to satisfy the rule; recommending `Global` without establishing that cross-proxy reads are actually required; asserting the rule is a false positive
when the default scope makes the two keys genuinely disjoint.
