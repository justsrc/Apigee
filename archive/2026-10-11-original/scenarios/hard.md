# Hard scenarios

These cases resemble escalation tickets. They mix symptoms, multiple regions, upgrade state, and rollback risk. A useful answer should state assumptions, request exact evidence, and avoid unsafe recovery commands.

1. **A two-data-center upgrade is split across Cassandra versions.** `dc-1` is on Cassandra 4.0.13, `dc-2` is still on Cassandra 3.11, and the customer reports intermittent management failures. The last `update.sh -c cs` failed on one node. How do we assess cluster health, identify the supported recovery boundary, and decide whether rollback is still possible?

2. **Upgrade failure after the last Cassandra data center changed.** All data centers completed the Cassandra step, but Management Server upgrade failed halfway through. The customer wants to restore the old RPMs and restart everything. What makes this rollback decision different from a failure before the last data center conversion?

3. **A Router fleet returns 503 during a rolling upgrade.** There are six Routers across two regions, but the load balancer keeps sending traffic to drained nodes because port 15999 still reports healthy. At the same time, one Message Processor is down. How should we restore traffic safely without upgrading two runtime nodes at once?

4. **Organization synchronization stopped after a network policy rollout.** Management Servers can reach Cassandra and ZooKeeper locally, but one region cannot synchronize organizations or environments. Router traffic remains healthy. Which exact inter-component ports and logs should be correlated before changing data?

5. **Cassandra repair is proposed during an active incident.** One data center has a `DN` node, elevated read latency, and a growing repair backlog. The customer wants `nodetool repair -full` on every node immediately. What evidence is needed to determine whether the node should be recovered, replaced, or repaired, and how should the operational risk be explained?

6. **Postgres master and standby disagree after a power event.** Both nodes appear online, but each reports itself as master in different local checks. Analytics writes are inconsistent and the customer asks for a forced promotion. What must be established before selecting a single master or restoring from backup?

7. **SSO migration lost the active signing key.** After moving to 4.53.00, login redirects loop. The old SSO files were deleted after a PKCS12 keystore was created, but the alias name is unknown. Which logs, keystore facts, and backup artifacts should be collected before attempting key replacement?

8. **A failed upgrade left mixed component releases.** `apigee-all status` shows Cassandra and ZooKeeper on the target version, while Management Server and Message Processor remain on the source version. Some APIs work, but deployments fail. How should we map the exact component state and use the release rollback procedure without guessing?

9. **A proxy deploys but fails only under load after upgrade.** Functional tests pass through one Router, but production traffic produces intermittent 502 and 504 responses. The fleet includes old and new runtime nodes, and only one region shows the fault. How should we compare node versions, reachability, ports, logs, and load-balancer membership?

10. **A restore was performed from partial backups.** The team restored Postgres but not ZooKeeper or Cassandra, then found that organizations and environments do not match the management database. What consistency problem does this create, and what evidence is needed to choose a coordinated restore instead of more isolated restores?

11. **The upgrade window overlaps certificate and DNS changes.** During a planned move from 4.52.02 to 4.53.00, the team also changed Router certificates and DNS records. Afterward, only TLS clients in one region fail. How should the incident be decomposed so upgrade, certificate, and routing causes are tested separately?

12. **A custom override breaks only one Message Processor.** The node starts, joins the load balancer, and then drops requests with Java out-of-memory errors. Its peer has no errors. The override directory contains several locally edited files with no change record. How should we identify the responsible setting, drain the node, and validate a correction without editing installed files?

13. **A maintenance restart risks losing ZooKeeper quorum.** The customer has three ZooKeeper nodes, one already unavailable, and asks to restart a second node to apply a property change. Management traffic is degraded but not down. What quorum facts must be confirmed, and what is the safest sequence for recovery and change?

14. **The target release requires an earlier post-upgrade action.** The customer cannot prove that `post_upgrade` and `drop_old_tables` ran during the previous upgrade, and the target release changes Cassandra behavior. They want to proceed because all services are currently green. What evidence and release documentation should gate the plan?

15. **A full outage combines store, runtime, and upgrade symptoms.** After a host kernel update, Cassandra reports one `DN` node, ZooKeeper loses quorum, Management Server will not start, and the load balancer marks every Router unhealthy. The customer has a recent full backup but no topology diagram. What information should be gathered first, in what order should dependencies be recovered, and which actions must wait until quorum and store health are established?
