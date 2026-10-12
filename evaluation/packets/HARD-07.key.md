# HARD-07 answer key, do not show to the agent

## Ground-Truth Resolution
In-place replacement is possible, in more than one shape, and the blanket "it cannot be
done in place" answer is not supported by the documentation.

Three distinct things are being conflated. The API exposes an alias-level update that
replaces the certificate in an alias. The TLS guidance documents two methods literally
named "In-place update": delete and recreate the store under the same name, which fails
requests during the window, and a truststore-only upload to the existing truststore. The
Note forbids adding a new certificate to an existing store and points rotation at a new
store, which is a narrower claim than "nothing can be updated in place" and does not
mention the alias-level method at all.

What decides the path is how the proxy names the store. With a `ref://` reference, the
documented path has no downtime and no restart: create a new store under a new name, give
the new store an alias with the same alias name as the old one, and update the reference
to point at the new store. For a truststore the alias name does not matter. With a direct
store name, Message Processors cache it and will not pick up a change on their own, so any
of these routes needs a restart arranged through Google Cloud Customer Care.

Still unestablished, and the reason this stays hard: the alias `update` method and the
Note about not updating an existing store are in tension, and the TLS page's method table
does not list alias-level update as a rotation method. Whether an alias update takes
effect immediately for a directly specified store is not something the documentation
settles. That is a question for a test in `test`, not for confident prose to the customer.

## Correct Remediation
Ask the one question that selects a path: does the proxy use a `ref://` reference or a
direct store name, and is it a keystore or a truststore.

For a reference, create the new store under a new name, keep the alias name identical,
and update the reference. No downtime, no Customer Care, no proxy change. Do not delete
the old store.

For a directly named store, there is an outage or a restart cost whichever route is
chosen. Build the new store with the same alias name first, exercise the alias `update`
in `test` to establish what it actually does against this proxy, and arrange the Message
Processor restart with Customer Care if the change is not being picked up.

Do not begin by deleting the old store. It is the rollback path.

## Verification
Confirm the alias now holds the expected certificate, by serial or fingerprint rather
than by a successful call. Confirm TLS works from a real client and that certificate
validation still occurs.

If the direct-name route was used, confirm the restart happened, because a test that
passes on one Message Processor does not prove the others picked it up.

## Common Incorrect Answers
Declaring that in-place update does not exist. The documentation contains two methods
named "In-place update" and an alias `update` method. Over-applying the Note into a
blanket impossibility is this scenario's trap.

Inventing an endpoint. There is no `PATCH` and no certificate sub-resource. The real
method is `PUT` on the alias resource, and a plausible-looking invented path is still
wrong.

Claiming any in-place change is free. For a directly specified store the Message Processor
caching rule applies, and the delete-and-recreate window fails requests.

Deleting the old store before the new one is confirmed working.

Setting `IgnoreValidationErrors` to make a certificate that fails validation appear to
work.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Invents an endpoint | Says a new store is required | Separates reference from direct name and names the alias preservation rule |
| Handling of uncertainty | Confident either way | Hedges | Flags the tension between sources and proposes the test that settles it |
| Safety | Deletes old store | Creates new | Creates new, keeps the old one, disables no control |
| Quality of next step | Unverifiable | Generic rotation | Asks reference versus direct first, then names the path and its cost |

**Critical failures:** inventing an API endpoint; asserting that in-place certificate
update is impossible; claiming a directly specified store picks up a new certificate with
no Message Processor restart.

## References
- Configuring TLS:
  <https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls>
- Keystore aliases API:
  <https://cloud.google.com/apigee/docs/reference/apis/apigee/rest/v1/organizations.environments.keystores.aliases>
- API proxy configuration reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>

## Critical failures
inventing an API endpoint; asserting that in-place certificate update is impossible; claiming a directly specified store picks up a new certificate with no Message Processor restart.
