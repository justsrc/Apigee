# Apigee hybrid operations

Verified facts for the product where the control plane runs in Google Cloud and the
runtime runs in a Kubernetes cluster you operate. Full research, including the "could not
verify" list, is in `research/notes-round2.md`.

Apigee hybrid documentation uses Edge for Private Cloud vocabulary in places, including
"Message Processor". That trips up agents that assume the wording implies OPDK. Identify
the product from the topology, not the nouns.

## A successful deployment call proves very little

There are at least four separable questions, and the Management API cannot answer all of
them:

1. The revision was saved.
2. The Synchronizer pulled the contract.
3. The Message Processor applied it.
4. The Watcher reported status.

So "the deployment returned success" is step one of four. A ticket saying a deployment did
not work on hybrid cannot be closed by checking the Management API alone.

The discriminator for step three is a log line in the runtime pod:

```
Switched to newer version 750 from version null
```

Related lines from the same service show an attempt in progress and a load of the latest
contract version. No `Switched to newer version` line means the contract was never
applied, whatever the API said.

## Missing setSyncAuthorization fails silently

If `setSyncAuthorization` was never called for an organization, the Synchronizer has no
permission to pull artifacts and nothing ever syns. There is no obvious error at any
layer.

The documented call is:

```
POST https://apigee.googleapis.com/v1/organizations/YOUR_ORG_NAME:setSyncAuthorization
     -d '{"identities":["serviceAccount:SYNCHRONIZER_MANAGER_SERVICE_ACCOUNT_NAME"]}'
```

The documented requirement is that the service account added holds the **Apigee
Synchronizer Manager** role. The API accepts an identity that lacks the role, so grant
first and confirm, or you will have called it successfully and synced nothing.

Check this before suspecting a network or runtime problem.

Related permission failure: deployments status goes missing when the manager role lacks
`watch` on deployments.

## Key value maps behave differently from Apigee X

The contract carries key value map **names**, not entries. The entries live in Cassandra
behind MART. So the statement "the key-value map propagates with the deployment" is wrong
for hybrid, and a map that looks correct in the contract can still resolve to nothing at
runtime.

There is a documented lookup race at high throughput, which is worth knowing before
chasing a concurrency bug in a policy.

## There is no documented hybrid trace CLI

Traces come from the UI. Do not invent a `kubectl` or gcloud trace command; none is
documented.

## Logging defaults differ by platform

On by default on GKE and GKE on-premises, off by default on AKS via `logger.enabled`. "We
have no logs" is a configuration question before it is a bug question.

Logs and metrics are documented as **lossy**. Analytics and deployment status are not.

Ingress access logs are not in the Apigee log stream. They are in Cloud Service Mesh.

A known issue has runtime logs stopping silently on hybrid: a bug fix that began honouring
component-level node selectors activated a latent default `logger.nodeSelector`, leaving
the runtime healthy but the log daemonset scaled to zero. `kubectl get daemonset
apigee-logger` showing a desired count of 0 with healthy runtime pods is that signature.

## Message processor error codes

They start with `runtime.sync.`. A documented example is
`runtime.sync.ContractLoadFailedMessage: Error loading spec file`.

Two documented errors mean the Cassandra keyspaces were never provisioned:
`Keyspace cache_<orgname>_hybrid does not exist` and `Encryption key does not exist for
organization <org> and type KmsKey`.

## Two-factor causes

**MART credential regression** is gated on workload identity federation **and** a forward
proxy **together**. Checking either one alone rules it out wrongly, which is a trap when
the two configurations arrived at different times.

**cert-manager 1.18 and later** flips `rotationPolicy` to `Always`. Clusters that were
upgraded are affected; fresh installs are not. Same hybrid version, different behaviour,
which makes it look like an intermittent problem when it is neither.

## Architecture guidance that differs from Apigee X

Running one environment per application is documented as an antipattern on hybrid, for
three reasons that do not apply on X: boot time, coupled scaling, and noisy neighbour.

## Upgrades

No version skipping. Mixed versions break Cassandra backup and restore. Version 1.17
triggers a rolling restart of all deployments, so budget for that rather than treating it
as a surprise.

## Known gaps

No Stack Overflow or community cases were verified in this project. The Stack Exchange API
returned stale cached payloads for every query, so nothing from there is cited rather than
citing something unchecked.

Not verified: whether a specific sleep-based delay in the Maven deploy plugin still exists
today, and the current state of a few third-party CLI issues.