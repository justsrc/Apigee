---
name: apigee-opdk-troubleshooter
description: Diagnose Apigee Edge for Private Cloud (OPDK) faults such as components that will not start, failed deployments, lost org or environment sync, and gateway 5xx responses. Uses apigee-service, apigee-all, and nodetool. Read the docs for the customer's release version and the Apigee X error references before proposing a fix.
---

# Apigee OPDK troubleshooter

## When to reach for this

Use it when someone reports one of these on an on-premises Apigee Edge install:

- A component will not start, or `apigee-service <component> status` fails.
- The gateway returns 5xx, or the Router stops routing.
- A deployment fails, or orgs and environments stop syncing.
- Cassandra ring trouble, ZooKeeper quorum loss, Postgres replication lag, LDAP errors.

## Read the docs before diagnosing

Pin every link below to the release the customer is running. The version sits in the URL, and the content changes between releases, so a procedure from the wrong version is worse than none.

- [Edge for Private Cloud home](https://docs.apigee.com/private-cloud)
- [All Edge for Private Cloud versions](https://docs.apigee.com/private-cloud/versions)
- [Port requirements](https://docs.apigee.com/private-cloud/v4.53.01/port-requirements)
- [Installation topologies](https://docs.apigee.com/private-cloud/v4.53.01/installation-topologies)
- [Start, stop, restart, and check status](https://docs.apigee.com/private-cloud/v4.53.01/starting-stopping-and-restarting-apigee-edge)
- [Backup and restore](https://docs.apigee.com/private-cloud/v4.53.01/backup-and-restore)
- [How to back up](https://docs.apigee.com/private-cloud/v4.53.01/how-perform-backup)
- [Log files and rotation](https://docs.apigee.com/private-cloud/v4.53.01/enable-log-rotation)
- [Drain a Router or Message Processor](https://docs.apigee.com/private-cloud/v4.53.01/enablingdisabling-server-message-processorrouter-reachability)
- [Edge configuration file reference](https://docs.apigee.com/private-cloud/v4.53.01/edge-configuration-file-reference)
- [Test the install](https://docs.apigee.com/private-cloud/v4.53.01/test-install)
- [Edge for Private Cloud release notes](https://cloud.google.com/apigee/docs/edge-private-cloud/release-notes)

Those use v4.53.01 to keep the URLs readable. Swap in the real version, but check the
status code before you trust the result.

Most paths swap cleanly. Some carry the release in the slug as well, so a version
replacement silently produces a 404: `nginx-45301`, `rollback-45301`,
`update-apigee-edge-45202-45301`. Those rename with the release. If you get a 404, read
the target release's index rather than guessing the next variant.

Google documents policy errors and runtime behavior under Apigee X rather than the private cloud tree. Both run the same proxy runtime.

- [Apigee docs home](https://cloud.google.com/apigee/docs)
- [Policy error codes](https://cloud.google.com/apigee/docs/api-platform/reference/policies/error-code-reference)
- [API Monitoring fault codes](https://cloud.google.com/apigee/docs/api-monitoring/fault-codes)

If you cannot pin a fix to one of those pages, say so and open a case instead of guessing.

- [Apigee support portal](https://apigee.com/about/support/portal/)
- [Apigee community forum](https://discuss.google.dev/c/google-cloud/cloud-apigee/104)

## Triage order

Work from the data stores outward. A Router that cannot reach a Message Processor and a Management Server that cannot reach that same Message Processor produce identical 5xx responses, so establish which link is down before reading proxy logs.

**1. Get the release and the node roles.** Run `apigee-service <component> version` on any node to learn the installed release, and map each host to its role. One node per role behaves very differently from several Message Processors behind a load balancer.

**2. Find which processes are down.**

```bash
/opt/apigee/apigee-service/bin/apigee-all status
/opt/apigee/apigee-service/bin/apigee-service edge-management-server status
```

`apigee-all` reports only the components configured on the node you run it on, so run it everywhere instead of trusting one host.

**3. Read the logs for the failing component.** Paths follow the component name.

```bash
ls -lt /opt/apigee/var/log/edge-message-processor/logs/
tail -n 200 /opt/apigee/var/log/edge-message-processor/logs/system.log
```

The `logs/` subdirectory holds `system.log`, `events.log`, `configurations.log`, `transactions.log`, and `startupruntimeerrors.log` for the Message Processor. Every `edge-*` component uses the same layout under `/opt/apigee/var/log/<component>/`, plus a console log at `/opt/apigee/var/log/<component>/<component>.log`. The `apigee-*` stores (Cassandra, ZooKeeper, OpenLDAP, Postgres, Qpid, SSO) log elsewhere, so get their paths from the [log files and rotation](https://docs.apigee.com/private-cloud/v4.53.01/enable-log-rotation) page.

**4. Check the links the failing component depends on.** Most outages are one closed port. The subset that causes the most confusion, snapshotted from the v4.53.01 port requirements. Confirm against your version's page:

| Port | What it carries |
| --- | --- |
| 8080 | Management API on the Management Server. Router, Message Processor, UI, Postgres, SSO, and Qpid all depend on it. Most lost sync traces here. |
| 2181 | ZooKeeper client port, plus 2888 and 3888 between ZooKeeper nodes |
| 7000, 9042 | Cassandra inter-node traffic and CQL |
| 8082 | Management Server to Message Processor |
| 4528 | Distributed cache and management calls, plus Router to Message Processor |
| 8443 | Router to Message Processor when TLS is enabled |
| 4527 | Router management and distributed cache |
| 15999 | Router health check, used by the load balancer |
| 5432 | Qpid and Management Server to Postgres, with 8084 for Postgres management |
| 10389 | Management Server to OpenLDAP |

**5. Check the stores before blaming the runtime.**

```bash
/opt/apigee/apigee-cassandra/bin/nodetool status
/opt/apigee/apigee-cassandra/bin/nodetool ring
```

An `UN` in the status column means that node is down, not that the ring is inconsistent. Find out why the node went down before you repair anything. `nodetool repair` puts heavy load on every node it touches, so run it against one node at a time and never across a whole data center at once.

For ZooKeeper, confirm the ensemble still has quorum before restarting anything. Restarting nodes in the wrong order breaks quorum. For Postgres, establish which node is master before you touch a master/standby pair.

**6. Look for config overrides.** A `.properties` file under `/opt/apigee/customer/application/` overrides the component defaults under `/opt/apigee/etc/`. Those overrides survive upgrades, which is why a stale one so often breaks a component right after a version bump.

**7. Verify the fix the way you found the problem.** Re-run `apigee-all status` on every node, re-run `nodetool status`, and send a real request through the Router. Checking the one node you repaired tells you nothing about the cluster.

## Things that bite

- Never edit files under `/opt/apigee/edge-<component>/` in place. Overrides go in `/opt/apigee/customer/application/`, and the next RPM update discards direct edits.
- Start and stop order is not arbitrary. Data stores come up first and the Router comes up last. The [start, stop, and status page](https://docs.apigee.com/private-cloud/v4.53.01/starting-stopping-and-restarting-apigee-edge) has the exact order. On a node running several components, `apigee-all restart` gets it right and a hand-rolled loop of `apigee-service` calls usually does not.
- Drain a Router or Message Processor before you restart it. The [reachability toggle](https://docs.apigee.com/private-cloud/v4.53.01/enablingdisabling-server-message-processorrouter-reachability) takes it out of the load balancer without dropping in-flight requests, and port 15999 confirms the change.
- Cassandra and PostgreSQL have to be running to be backed up. Everything else should be stopped first. A crashed store cannot be backed up, so fix it before you take a safety copy.
- Property edits need a component restart to take effect, and restarting a live Router means a drain first.
