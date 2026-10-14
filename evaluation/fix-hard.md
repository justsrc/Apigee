# Fix report: scenarios/hard.md

Single file changed: `scenarios/hard.md`. No network used. Every fact below was verified
against `research/pages/` (407 cached documents). Scenario IDs, section structure and
difficulty are unchanged; all five fixes remove wrong claims without softening the
diagnostic work.

## FIX 1 — HARD-07, the ground truth was close to inverted

### What was wrong

The scenario asserted "There is no in-place update" and scored a correct answer as a
critical failure twice, in the rubric and in the **Critical failures** line. The cached
pages say otherwise:

- `pages/keystore-aliases.txt:171-172` — the aliases collection documents an `update`
  method: "Updates the certificate in an alias."
- `pages/reference_apis_apigee_rest_v1_organizations.environments.keystores.aliases_update.txt`
  — `PUT https://apigee.googleapis.com/v1/{name=organizations/*/environments/*/keystores/*/aliases/*}`,
  body is a PEM- or DER-encoded X.509 `HttpBody`, required query parameter
  `ignoreExpiryValidation`, IAM permission `apigee.keystorealiases.update`.
- `pages/api-platform_system-administration_options-configuring-tls.txt:218,225` — the
  method table lists two methods literally named "In-place update": Method 2a (Delete &
  Recreate) and Method 2b (Truststore upload).

So the old scenario punished the correct answer and let a wrong one pass.

### What is actually true, and the scenario now built on it

Three distinct things were being conflated:

1. An alias-level `update` that replaces the certificate in an alias. Real, documented,
   on a real endpoint.
2. Two TLS-page methods named "In-place update": delete and recreate the store under the
   same name (fails requests during the window), and, for truststores only, upload a new
   certificate to the existing truststore. Both require a Message Processor restart
   because Message Processors cache directly specified stores.
3. The Note at line 169 of the TLS page: "You cannot update an existing keystore or
   truststore to add a new certificate. You must create a new keystore/truststore when
   updating a certificate." That is a claim about *adding a certificate*, and it does not
   mention the alias-level method.

Items 1 and 3 sit in tension on their face. The scenario now treats that as the hard
part rather than papering over it: the agent is expected to name the tension, ask the
configuration question that actually decides the path (`ref://` reference versus direct
store name, keystore versus truststore), and mark "does the alias update take effect
immediately for a directly specified store" as unresolved pending a test in `test`.

The new trap runs the other way from the old one: declaring that in-place update does
not exist is now a critical failure, because two methods carry that exact name and the
API documents the call. Inventing an endpoint (`PATCH`, a certificate sub-resource)
remains a critical failure, since the real method is `PUT` on the alias resource.

The reference-versus-direct-name distinction, the alias-name preservation rule, the
Message Processor restart cost and "do not delete the old store" all survive, because
they are all still in the TLS page (method table rows 1 and 2, and the warning at line
126).

## FIX 2 — HARD-03, invented XML elements

`<ClientCertStore>` and `<ClientCertAlias>` appear nowhere in the 407 cached documents
(`grep -rc ClientCertStore pages/` returns no file). The documented `SSLInfo` children
(`pages/api-platform_reference_api-proxy-configuration-reference.txt:765-830`, plus the
documented `ref://` example at line 981) are `Enabled`, `Enforce`, `TrustStore`,
`ClientAuthEnabled`, `KeyStore`, `KeyAlias`, `IgnoreValidationErrors`, `Ciphers`. The
snippet now uses only elements that exist, in the documented shape:

```xml
<SSLInfo>
  <Enabled>true</Enabled>
  <ClientAuthEnabled>true</ClientAuthEnabled>
  <KeyStore>ref://orders-keystore</KeyStore>
  <KeyAlias>orders-client</KeyAlias>
  <TrustStore>ref://orders-trust</TrustStore>
</SSLInfo>
```

The claim that a reference points at a store rather than an alias is verified, line 972:
"You can only use a reference to the keystore and truststore; you cannot use a reference
to the alias. When you change the reference to a keystore, ensure that the alias name of
the cert is the same as in the old keystore." The resolved `ResourceReference` is shown
with the documented `name` / `Refers` / `ResourceType` shape.

This made the scenario harder rather than easier. The old "two findings" were one finding
and a restatement. Now they are two independent faults, each sufficient to break
southbound on its own:

- the reference still resolves to `orders-keystore-v1`, so the proxy presents the old
  client certificate, which is why the backend rejects it (a consequence, not a second
  fault in the backend);
- `<KeyAlias>` is a literal, not a reference, and the new store's only alias is
  `orders-client-v2`, so repointing the reference alone moves the failure to
  `security.util.KeyAliasNotFound` rather than fixing it.

The discriminator between the two is the fault code in the body, which is why the initial
evidence now carries one (`messaging.adaptors.http.flow.SslHandshakeFailed`, from
`pages/mon_fault-codes.txt:77`) and the ground truth names the second code.

## FIX 3 — HARD-05, a control that does not exist

The old scenario had "the environment group contains a traffic split" and "the traffic
split still sends a share to revision 22". Environment groups carry hostnames, not
weights: `pages/api-platform_fundamentals_environments-overview.txt:14-22,225-227` and
the "Multiple environments in a single environment group" section, which states that
"hostnames are defined on the environment group level: they do not route to a specific
environment." And a deployment replaces the prior revision inside its environment:
`pages/api-platform_deploy_ui-deploy-overview.txt:33-40` ("Revision 2 is deployed to the
Message Processors... Revision 1 is undeployed").

Rebuilt on mechanisms that exist, keeping the teaching point: the symptom correlates with
the serving revision, not the client.

- Two environments, `prod` and `prod-b`, are both members of `prod-group` and both serve
  `api.example.com` on the same base path. That is what puts two revisions on one URL.
- The 10:00 rollback moved `prod` only, which is why the rate did not move.
- The uncertainty is preserved and sharpened: a stable mixed fleet (two environments) and
  an unpropagated deployment look identical in a trace, because deployments are
  eventually consistent across Message Processors and a deployment stays `PROGRESSING`
  until the runtime has loaded it (`pages/api-platform_deploy_ui-deploy-overview.txt:19`,
  `RuntimeState` in `pages/rev-env-deployments-res.txt:267-300`). The per-environment
  deployment list is the test that separates them, which is why assuming one environment
  is a critical failure.

Metadata updated: secondary topics now "environment groups, routing, revision
management" instead of the load-balancing claim.

## FIX 4 — HARD-11, contradictory mechanism

Element names verified in
`pages/api-platform_reference_endpoint-properties-reference.txt`: `io.timeout.millis`
(line 78, default 55000) and `api.timeout` (line 295). The old note also claimed 504 can
come from "the target read/write timeouts" as a third setting; there is no such separate
setting in the X property reference, so that phrase is gone.

The ServiceCallout correction was right and is kept, but it contradicted the scenario's
own mechanism. `pages/api-platform_reference_policies_service-callout-policy.txt:519,531`:
"If the ServiceCallout hits a timeout, an HTTP 500 is returned, the policy fails, and the
API proxy goes into an error state", with a documented default of 55000 ms. A callout can
therefore never be the cause of a 504.

Main mechanism rebuilt on a real 504-producing setting, using the documented precedence:
the ProxyEndpoint carries `<Property name="api.timeout">10000</Property>`. The Message
Processor sets `api.timeout` to the lesser of the Ingress timeout (300 s, not
configurable) and the proxy-level value, then clamps `io.timeout.millis` to
`api.timeout` minus elapsed time before connecting. So the team's 30 s target setting is
the *larger* of the two numbers and was never the constraint. The ServiceCallout survives
as a red herring that the status code eliminates rather than as the answer.

Also used and verified: `api.timeout` cannot be set with a variable and must be shorter
than the standard Message Processor timeout of 300 seconds, so changing it is a proxy
change needing a new revision and deployment. Fault codes `flow.APITimedOut` and
`messaging.adaptors.http.flow.GatewayTimeout` both come from `pages/mon_fault-codes.txt`
(lines 69 and 78) and are named as the discriminator for "did every 504 share this
cause", which is left open.

## FIX 5 — HARD-14, one wrong store name left

The restore trio was already correct and is unchanged. The ticket, initial evidence and
diagnostic evidence all say OpenLDAP, ZooKeeper and Cassandra, which matches
`pages/https___docs.apigee.com_private-cloud_v4.53.01_backup-and-restore.txt:31,41`
("organizations are in LDAP, ZooKeeper and Cassandra"; "When you restore one of
ZooKeeper, Cassandra or LDAP nodes it is recommended to restore all three nodes in order
to achieve consistency").

One factual slip remained: the ground truth said "The state is inconsistent because
Postgres was moved backwards alone", while the ticket says OpenLDAP was restored. Fixed
to OpenLDAP, and the documented guidance is now quoted as the source of the
restore-together rule. PostgreSQL is in the backup set per the same page, but it is not
part of the consistency trio, so the scenario does not imply otherwise.

## Also changed

The file header claimed every fault code in the file "lives in
`.agents/skills/apigee-support-core/references/error-codes.md`". That index is
policy-level only; the gateway codes added here (`SslHandshakeFailed`,
`KeyAliasNotFound`, `GatewayTimeout`, `APITimedOut`, `UnexpectedEOFAtTarget`) come from
`pages/mon_fault-codes.txt`. The header now says both things accurately. No other file
was touched.

All three JSON error payloads use the required shape
`{"fault": {"detail": {"errorcode": "..."}}}` with no invented `faultstring` text; where
the faultstring matters, the prose says so instead of quoting a made-up string.

## Verification

- `python3 tests/check_repo.py` → PASS, 13 passed, 0 failed, 0 warnings.
- All 15 scenarios still present, IDs stable, one of each required section per scenario
  (checked with a per-scenario heading count).
- All three JSON payloads parse and already match the canonical fault shape.
- Note for whoever owns `tests/fix_error_shape.py`: its `--dry` counter now reports
  "hard.md: would fix 3 payload(s)" even though none need fixing. The counter increments
  on `new_block != m.group(0)`, and `convert()` returns the inner block while the match
  includes the ```json fences, so an already-correct block is always counted. The file
  skipped entirely before because it had no `"errorcode"` string. Pre-existing bug in
  that script, not a payload problem.
