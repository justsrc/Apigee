---
name: apigee-opdk-upgrader
description: Plan and run Apigee Edge for Private Cloud (OPDK) upgrades with apigee-setup update.sh, including rolling upgrades on multi-node topologies and rollbacks after a failed one. Covers which version jumps are legal, prerequisites, component order, backups, and post-upgrade checks. Use when the user mentions upgrading OPDK, update.sh errors, or moving between Edge for Private Cloud versions.
---

# Apigee OPDK upgrade planner

## When to reach for this

- Moving OPDK to a new patch or minor release, for example 4.52.02 to 4.53.00.
- Planning an upgrade across a multi-node or multi-data-center topology where traffic has to stay up.
- Working out whether the installed release can reach the target release at all.
- Recovering from an upgrade that went wrong.

## Confirm the version jump is legal first

Apigee supports an upgrade only from the release named in the upgrade path for the target version. Skipping releases is unsupported, and an unsupported jump fails partway through with a cluster split across two versions.

- [All versions](https://docs.apigee.com/private-cloud/versions)
- [Upgrade compatibility matrix and end-of-life dates](https://docs.apigee.com/release/apigee-edge-release-process#upgrade-compatibility-matrix-for-edge-for-private-cloud-releases)
- [Upgrade paths for 4.53.00](https://docs.apigee.com/private-cloud/v4.53.00/upgrade-paths)
- [Upgrade from 4.52.02 to 4.53.00](https://docs.apigee.com/private-cloud/v4.53.00/update-apigee-edge-45202-45300)
- [Roll back 4.53.00](https://docs.apigee.com/private-cloud/v4.53.00/rollback-45300)
- [Backup and restore](https://docs.apigee.com/private-cloud/v4.53.00/backup-and-restore)
- [Operating system upgrade](https://docs.apigee.com/how-to-guides/os-upgrade)
- [Supported software and versions](https://docs.apigee.com/private-cloud/v4.53.00/installation-requirements)
- [Edge for Private Cloud release notes](https://cloud.google.com/apigee/docs/edge-private-cloud/release-notes)

Read the target version's own upgrade page end to end before planning anything. Prerequisites differ per release.

Put the two version numbers in the plan. "Upgrade OPDK" is not a plan. "4.52.02 to 4.53.00, one Cassandra data center at a time, 4.52.02 recoverable until the last data center is converted" is.

## Prerequisites

The 4.52.02 to 4.53.00 procedure lists these. Treat them as blocking.

- **Back up every component on every node.** Cassandra, ZooKeeper, Postgres, OpenLDAP, Qpid, SSO, Management Server, Message Processor, and Router. A partial backup is not a rollback plan. Take VM snapshots of the Cassandra nodes too if the platform allows it.
- **Keep the cluster running during the upgrade.** The procedure assumes proxy traffic keeps flowing, and a stopped cluster mid-upgrade turns a routine upgrade into a rebuild.
- **Confirm the earlier release's post-upgrade steps ran.** Going to 4.53.00 requires Cassandra 3.11.16, `LeveledCompactionStrategy`, and both `post_upgrade` and `drop_old_tables` to have run during the previous upgrade. Re-running them is safe, so do it if you cannot prove they ran.
- **Every node needs Python 3,** Cassandra nodes included.
- **Operating system upgrades run in a separate window.** Never upgrade Apigee and the OS in the same window. RHEL 7, CentOS 7, OEL 7, and Amazon Linux AMI 2 have to move to an 8.x series OS first, then upgrade Apigee. The [OS upgrade page](https://docs.apigee.com/how-to-guides/os-upgrade) covers a new parallel data center and a node-by-node rolling upgrade. Check that your target OS is supported by your current Edge version before you start.
- **SSO keys move to a keystore in 4.53.00.** IDP keys and certs that were plain files become a PKCS12 keystore. Export the existing key and cert before touching the SSO component.

Backup commands, one per component:

```bash
/opt/apigee/apigee-service/bin/apigee-service apigee-cassandra backup
/opt/apigee/apigee-service/bin/apigee-service apigee-zookeeper backup
```

Back up one Cassandra node at a time, one ZooKeeper node at a time, one Postgres node at a time. The ZooKeeper backup briefly stops ZooKeeper, which is why it cannot run alongside the others. Cassandra and PostgreSQL must be running to be backed up; stop everything else first. Files land in `/opt/apigee/backup/<component>/`. With Postgres master and standby, back up the master only.

On restore, bring back ZooKeeper, Cassandra, and OpenLDAP together. Organizations and environments created after the backup live in all three, so restoring one alone leaves you inconsistent.

## Component order

`update.sh` takes short component codes.

| Code | Component |
| --- | --- |
| `cs` | Cassandra |
| `zk` | ZooKeeper |
| `ps` | Postgres |
| `ldap` | OpenLDAP |
| `edge` | Management Server, Message Processor, Router |
| `qpid` | Qpid |
| `ui` | Classic Edge UI |
| `ue` | New Edge UI |
| `sso` | Apigee SSO |
| `all` | Everything configured on the node |

The 4.53.00 procedure goes Cassandra, then management nodes, then runtime nodes, then the rest. Within each step, one node at a time across every region.

1. **Cassandra, one node at a time and one data center at a time.** Between nodes inside a data center, wait a few minutes for the node to finish starting and join the cluster. After a whole data center, wait 30 minutes to a few hours and check that data center's health before starting the next one.

   ```bash
   /opt/apigee/apigee-setup/bin/update.sh -c cs -f configFile
   ```

2. **Validate each Cassandra node before moving on.** `validate_upgrade` confirms the Cassandra version and metadata, `post_upgrade` finishes the schema work, then rebuild the `kms` secondary indexes with `nodetool rebuild_index` under `/opt/apigee/apigee-cassandra/bin/`.

   ```bash
   /opt/apigee/apigee-service/bin/apigee-service apigee-cassandra validate_upgrade -f configFile
   /opt/apigee/apigee-service/bin/apigee-service apigee-cassandra post_upgrade
   ```

3. **Management nodes.** One at a time, across all regions.

   ```bash
   /opt/apigee/apigee-setup/bin/update.sh -c edge -f configFile
   ```

4. **Runtime nodes.** One at a time. The same `edge` code covers the Routers and Message Processors.

5. **The remaining components.** One at a time: `qpid`, then `ps`, then the UI and SSO. Follow the SSO keystore steps in the release page before updating `sso`.

## Keeping traffic up

- Drain each Router and Message Processor before upgrading it, so the load balancer stops sending traffic while you work. The [reachability toggle](https://docs.apigee.com/private-cloud/v4.53.00/enablingdisabling-server-message-processorrouter-reachability) does this without dropping in-flight requests, and port 15999 tells you when the node is out of rotation.
- Never upgrade two Message Processors at the same time. Rolling them means traffic always has somewhere to land.
- 4.53.00 moves Cassandra from 3.11 to 4.0.13, and no in-place rollback exists once that step finishes. A mixed-version Cassandra cluster has real operational limits, so keep at least one data center on 4.52.02 until you are satisfied. After the last data center converts, going back is no longer possible.
- If you want rollback without risking data loss, add a Cassandra data center before you start. Restoring from backups instead means downtime and possible data loss.
- 4.53.00 does not upgrade NGINX on the Router. After you verify the upgrade, move each router from 1.20.x to 1.26.x yourself, one node at a time with `dnf update apigee-nginx-1.26.3`. Fresh installs on 9.x OS series get 1.26.x already. Read [Nginx 1.26 changes in Apigee Edge 4.53.00](https://docs.apigee.com/private-cloud/v4.53.00/nginx-45300) before you make that change.

## After the upgrade

```bash
/opt/apigee/apigee-service/bin/apigee-all status
/opt/apigee/apigee-cassandra/bin/nodetool status
```

Run `apigee-all status` on every node, since it only reports what is installed on that host. Call a real API through the Router, not the Management Server. Load the Edge UI and confirm the org list and analytics are current. If you moved NGINX forward, confirm it with `/opt/nginx/sbin/nginx -V`.

## Considering hybrid instead

If the goal is to stop running the runtime yourself while keeping API management, Apigee hybrid is the on-premises product for that. Its management plane runs in Google Cloud and you run the runtime plane on a supported Kubernetes cluster. Plan it as its own project with its own timeline, not as a step in an OPDK upgrade.

- [What is Apigee hybrid](https://cloud.google.com/apigee/docs/hybrid/latest/what-is-hybrid)
- [Upgrading Apigee hybrid](https://cloud.google.com/apigee/docs/hybrid/latest/upgrade)
- [Apigee hybrid release notes](https://cloud.google.com/apigee/docs/apigee-hybrid-release-notes)
