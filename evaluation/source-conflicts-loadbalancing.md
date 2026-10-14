# Source conflict: load-balanced target return to rotation

## Question

For a target server removed from rotation because the `<MaxFailures>` threshold in a
`<LoadBalancer>` was reached, with **no** `<HealthMonitor>` configured: does Apigee return the
target to rotation automatically (and on what schedule), or does it stay out of rotation until
the API proxy is redeployed?

Two official pages assert opposite answers. This record fixes what each one says, verbatim, and
tests whether the difference can be scoped away.

## Status

DOCUMENTATION_CONFLICT

## Sources

### Load balancing across backend servers

- URL: <https://cloud.google.com/apigee/docs/api-platform/deploy/load-balancing-across-backend-servers> (per research/pages/MANIFEST.tsv, entry `api-platform_deploy_load-balancing-across-backend-servers`)
- Local cache: research/pages/api-platform_deploy_load-balancing-across-backend-servers.txt (byte-identical duplicate: research/pages/lb-verify.txt, md5 01e14fef95a3246328503735df6e6f36)
- Line: 350 (related: 342, 344, 537, 539, 589)
- Product/deployment model: "This page applies to **Apigee** and **Apigee hybrid**." (cache line 1); Edge mirror also published at docs.apigee.com (see third source)
- Statement type: configured behaviour (MaxFailures > 0, health monitor absent)
- Verbatim quote:
  > "Alternatively, if you configure MaxFailures \> 0 and you do not configure a health monitor, Apigee will automatically take the target server out of rotation when the first failure is detected. Apigee will check the health of the target server every five minutes and return it to the rotation when it responds normally."
  > (The `\>` is literal in the cache file, a pandoc escape artifact. Fetched live 2026-10-12: sentence still renders; page footer "Last updated 2026-10-09 UTC".)

### Antipattern: Load Balance with a single target server with MaxFailures set to a non-zero value

- URL: <https://cloud.google.com/apigee/docs/api-platform/antipatterns/load-balancing-maxfailures> (per research/pages/MANIFEST.tsv)
- Local cache: research/pages/api-platform_antipatterns_load-balancing-maxfailures.txt
- Line: 98 (related: 53, 73, 96, 104, 106, 113, 146)
- Product/deployment model: "This page applies to **Apigee** and **Apigee hybrid**." (cache line 1); cache line 3 links the Edge mirror at docs.apigee.com/api-platform/antipatterns/load-balancing-maxfailures. No version-scoped statement anywhere on the page.
- Statement type: failure condition (single `<Server>` + non-zero MaxFailures, health monitor absent)
- Verbatim quote:
  > "Even if the TargetServer "target1" gets back to its normal state and is capable of sending successful responses, the requests to the API Proxy will continue to return 503 errors. This is because Apigee does not automatically put the TargetServer back in rotation even after the target is up and running again. To address this issue, ***the API Proxy must be redeployed*** for Apigee to put the TargetServer back into rotation."
  > (Fetched live 2026-10-12: sentence still renders, with "Apigee" in place; page footer "Last updated 2026-10-09 UTC".)

No `#` heading exists in either cached file (`grep -n '^# '` on both returns nothing), so titles
are taken from the live page H1/`<title>` (fetched 2026-10-12), corroborated for the antipatterns
page by the docs-nav title in research/pages/api-platform_troubleshoot_playbooks_504-target-read-timeout.txt:1960
("Load Balance with a single target server with MaxFailures set to a non-zero value").

### Load balancing across backend servers (Apigee Edge mirror)

- URL: <https://docs.apigee.com/api-platform/deploy/load-balancing-across-backend-servers> (fetched live 2026-10-12; no local cache, no MANIFEST.tsv entry)
- Local cache: none
- Line: n/a — live HTML fetch 2026-10-12, not a line-numbered cache file
- Product/deployment model: Edge (public/private cloud) docs tree, unversioned current page; page footer "Last updated 2026-10-09 UTC" (fetched 2026-10-12)
- Statement type: two statements on one page — one configured behaviour, one failure condition
- Verbatim quotes:
  > "Alternatively, if you configure MaxFailures > 0 and you do not configure a health monitor, Apigee will automatically take the target server out of rotation when the first failure is detected. Apigee will check the health of the target server every five minutes and return it to the rotation when it responds normally."
  > "The failing TargetServer is then taken out of rotation until you redeploy the proxy."
  > (Both render as visible body text on this page, fetched 2026-10-12. Neither sentence is qualified by the number of `<Server>` entries.)

### Antipattern (Apigee Edge mirror)

- URL: <https://docs.apigee.com/api-platform/antipatterns/load-balancing-maxfailures> (fetched live 2026-10-12)
- Local cache: none
- Line: n/a — live HTML fetch 2026-10-12
- Product/deployment model: Edge docs tree
- Statement type: failure condition
- Verbatim quote:
  > "Even if the TargetServer "target1" gets back to its normal state and is capable of sending successful responses, the requests to the API Proxy will continue to return 503 errors. This is because Edge does not automatically put the TargetServer back in rotation even after the target is up and running again. To address this issue, the API Proxy must be redeployed for Edge to put the TargetServer back into rotation."
  > (Same claim as the cloud.google.com antipatterns page, with "Edge" substituted for "Apigee".)

### Endpoint properties reference — checked, makes no claim

research/pages/api-platform_reference_endpoint-properties-reference.txt: `grep -i maxfailures` returns
nothing. Its only `<LoadBalancer>` mentions concern timeout and retries, not rotation
(lines 68, 70). Live fetch 2026-10-12 also shows no `<MaxFailures>` occurrence. It is not a party
to the conflict.

## Evidence collected

- The pages agree on the default: "**The MaxFailures default is 0.** This means that Apigee always tries to connect to the target for each request and never removes the target server from the rotation." (research/pages/api-platform_deploy_load-balancing-across-backend-servers.txt:342; antipatterns cache line 146; LB cache lines 539, 589). No conflict at the default.
- The pages agree that a `<HealthMonitor>` restores the target without a redeploy (LB cache lines 344, 537; antipatterns cache line 113, "...there is no need to redeploy the proxy"). No conflict when health monitoring is enabled.
- The conflict is confined to the `<MaxFailures>` > 0 with no health monitor case, where LB cache line 350 says the target returns to rotation automatically after a five-minute health re-check and antipatterns cache line 98 says it does not and requires a redeploy.
- Both statements are current, not one stale page and one fresh page: both pages fetched live 2026-10-12 render their claim, and both footers read "Last updated 2026-10-09 UTC".
- Product scope is identical, so an Edge-vs-Apigee/hybrid split does not explain it: both cached pages state "This page applies to **Apigee** and **Apigee hybrid**." (load-balancing cache line 1; antipatterns cache line 1). The Edge mirrors assert the same two claims.
- The field is the same, so a `<MaxFailures>`-vs-TargetServer-config split does not explain it: `<MaxFailures>` is a child of `<LoadBalancer>` under `<HTTPTargetConnection>` in both pages (antipatterns cache lines 53, 67; LB cache lines 329, 587, 613). The TargetServer JSON config on the LB page (cache lines 34-41) has no MaxFailures field at all.
- Target type is not the difference either: both pages cover TargetEndpoint and ServiceCallout (antipatterns cache lines 5-12, 100; LB cache line 221).
- Decisive against the server-count explanation: the Edge mirror of the load-balancing page renders both sentences on the same page, and its "taken out of rotation until you redeploy the proxy" sentence carries no server-count qualifier (fetched 2026-10-12).
- Corroborating editorial signal: on cloud.google.com the same "until you redeploy" paragraph still exists but is wrapped in an HTML comment, so it does not render; the rendered page keeps only the five-minute sentence (fetched 2026-10-12; the passage sits between `<!--` and `-->` in the page source).
- The load-balancing page is internally inconsistent about removal timing, independent of the conflict: line 350 says removal happens "when the first failure is detected", while lines 310-316 say the target is removed after the configured number of failures and line 342 restates the threshold.

## Possible explanations

- Different server counts in the `<LoadBalancer>`. The antipatterns page is scoped to one `<Server>` (cache lines 77, 79, 96, 104); the load-balancing page's five-minute sentence is not scoped by server count, and its examples all use two servers (cache lines 300-301, 327-328). No cached or fetched page states that server count changes recovery behaviour, and the Edge mirror's unscoped "until you redeploy" sentence argues against it. Recorded, not asserted.
- One page was edited and the other not. Both footers read "Last updated 2026-10-09 UTC" (fetched 2026-10-12), and the commented-out paragraph on cloud.google.com shows the contradiction was known at edit time rather than left behind by an older page. Supported as an editorial observation only; no page states which behaviour was changed.
- A version or product split. No version-scoped statement appears near either claim (both cached pages line 1 only). No evidence for a version-dependent reading.
- A runtime mechanism (for example, the re-check running but the rotation state not being rebuilt, or differing between a balancer with a failover peer and one without). Plausible, but no source describes it. Not asserted.

## Defensible conclusion

What the sources DO establish:

- Two official pages, both current as of 2026-10-12, both stated to apply to Apigee and Apigee hybrid, describe the same field in the same configuration and give opposite answers: load balancing cache line 350 (automatic return, five-minute health re-check) versus antipatterns cache line 98 (no automatic return, redeploy required).
- The Edge mirrors repeat both claims, and the Edge load-balancing page carries both claims simultaneously in visible text.
- With `<MaxFailures>` at its default of 0, or with a `<HealthMonitor>` configured, the pages agree and no conflict exists.

What they do NOT establish:

- Which behaviour the runtime actually exhibits for `<MaxFailures>` > 0 with no health monitor. No source names a mechanism, a version scope, or a server-count rule that would scope one claim out.
- Whether the commented-out paragraph on cloud.google.com reflects a decision, a draft, or an abandoned edit.

The available sources do not establish a definitive answer on whether an unmonitored failed target returns to rotation. The conflict is genuine and is not an artifact of different products, different fields, or stale pages.

## Tests or additional sources needed

- Direct test, single server: one `<Server>` + `<MaxFailures>5</MaxFailures>`, no `<HealthMonitor>`. Fail the backend, generate five failures, confirm 503s, restore the backend, then watch continuously for more than five minutes before concluding, and compare against a redeploy. This is the only test that separates the two claims.
- Direct test, two servers (plus a fallback if configured): the configuration the load-balancing page's claim appears to describe, to check whether server count changes recovery.
- Additional sources: Apigee or Edge release notes mentioning load-balancer health re-check or rotation recovery; the community tutorial linked at antipatterns cache line 151; the runtime load-balancing implementation (five-minute interval) if any source for it can be cited.

## Resolution status

DOCUMENTATION_CONFLICT — two current official pages, same product scope and same `<MaxFailures>` field, assert opposite recovery behaviour for `<MaxFailures>` > 0 with no `<HealthMonitor>`, and nothing in either page scopes the other out.
