# Sources and how to verify them

The full index of fetched pages is `research/official-documentation-index.md`. This file
is the short version plus the method.

## Verify before citing

Guessed URLs fail often enough here to matter. During setup, 22 of the first 39
plausible-looking paths returned 404. `basic-auth-policy` does not exist, the page is
`basic-authentication-policy`. `debug-runtime-errors` does not exist at all.

```bash
cd research
./fetch.sh <doc-path>     # prints status, saves clean Markdown to pages/
```

Check the status before citing. Do not cite a link you inferred from a naming pattern.

## Soft 404s return HTTP 200

`cloud.google.com` answers 200 for paths that do not exist, with a body reading "The
equivalent page does not exist in Apigee". Eight such pages were found in one sweep and
would otherwise have been indexed as live.

A 200 response is therefore not evidence that a page has content. `fetch.sh` checks the
body for this marker and treats a match as a 404.

## Find URLs instead of guessing

Any fetched page carries the real link tree.

```bash
grep -oE '/apigee/docs/[a-zA-Z0-9/._-]+' pages/<file>.txt | sort -u
```

Good seeds: `api-platform/reference/policies/error-code-reference` for the policy list,
`api-platform/get-started/compare-apigee-products` for product differences.

## Two hosts, two rules

`cloud.google.com/apigee/docs/...` holds Apigee, Apigee hybrid, and Edge for Private Cloud
release notes.

`docs.apigee.com/private-cloud/...` holds Edge for Private Cloud operational docs, with
the release in the path. Two consequences:

Most paths swap cleanly between releases. Slugs that carry the version number do not.
`nginx-45301` and `rollback-45301` exist; `nginx-45300` under `v4.53.01/` is a 404. When
you swap versions, check the status.

The prose on `docs.apigee.com` is about Apigee Edge, a different product. Rich TLS and
keystore material lives there. Do not transfer those instructions to Apigee X without
checking.

## Load-bearing pages

Reach for these first. All verified 200.

| Need | Page |
| --- | --- |
| Which product supports what | `/api-platform/get-started/compare-apigee-products` |
| Policy elements and errors | `/api-platform/reference/policies/<policy-name>-policy` |
| Fault handling model | `/api-platform/fundamentals/fault-handling` |
| Policy error model | `/api-platform/fundamentals/what-you-need-know-about-policy-errors` |
| Proxy configuration | `/api-platform/reference/api-proxy-configuration-reference` |
| Flow variables | `/api-platform/reference/variables-reference` |
| Conditions | `/api-platform/reference/conditions-reference` |
| OAuthV2 | `/api-platform/reference/policies/oauthv2-policy` |
| JWT policies | `/api-platform/reference/policies/jwt-policies-overview` |
| TLS | `/api-platform/system-administration/options-configuring-tls` |
| Hybrid | `/hybrid/what-is-hybrid` |
| OPDK versions | `https://docs.apigee.com/private-cloud/versions` |
| OPDK upgrade paths | `https://docs.apigee.com/private-cloud/v4.53.01/upgrade-paths` |

The policy error reference page is a pointer, not a table. It carries no fault codes and
sends you to the individual policy pages, where the real `## Error reference` sections
live. `research/build_error_index.py` extracts all of them into
`references/error-codes.md`.

## Evidence levels

Label claims so the reader knows how much weight to put on them.

**Documented** states on a page you opened, at a URL you checked.

**Observed** something you reproduced or executed yourself.

**Reported** a community claim you read but did not reproduce.

**Hypothesis** your own inference. Label it as one.

Do not promote a hypothesis to documented. When evidence conflicts, say so and give the
test that would resolve it rather than choosing the source that agrees with your first
guess.