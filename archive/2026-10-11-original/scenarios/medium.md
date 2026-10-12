# Medium scenarios

These tickets include partial evidence, more than one affected component, or a topology detail. Ask for the missing facts, then give a bounded diagnostic sequence.

1. **Five-minute 502 bursts after a firewall change.** Two Routers and four Message Processors span two data centers. Since a firewall rule update, requests fail for about five minutes every hour. Router logs show intermittent connection failures to Message Processors. How would you separate a port problem from a load-balancer health-check problem?

2. **A deployment succeeds in one region only.** A proxy deploys in region `dc-1` but remains pending in `dc-2`. Management Server logs mention synchronization timeouts. What node roles, ports, and store health should we compare across regions?

3. **Cassandra shows a mixed status.** Two nodes are `UN`, one is `UJ`, and one is `DN` after a host reboot. The customer wants to run `nodetool repair` across the cluster. What should we verify first, and how should repair be scoped if it is later justified?

4. **A rolling restart lost ZooKeeper quorum.** An operator restarted two of three ZooKeeper nodes at once. Management and runtime components now flap between healthy and unhealthy. How should we restore quorum without making the outage worse?

5. **Postgres failover left analytics stale.** The former master is down, the standby is serving, but analytics dashboards stopped updating. Which services and replication state should be checked before attempting failback?

6. **Upgrade stopped during the Cassandra step.** `update.sh -c cs -f configFile` completed on two nodes and failed on the third with a package dependency error. The customer asks whether to continue with Management Server nodes. What version, node, backup, and cluster checks determine the safe next step?

7. **The SSO service will not start after an upgrade.** The customer upgraded to 4.53.00 and the SSO logs report a missing keystore alias. The old certificate and key are still present as separate files. What migration detail should be verified before restarting SSO repeatedly?

8. **A runtime node has stale customer overrides.** After an upgrade, one Message Processor uses an old JVM setting while its peers use the new default. The setting is under `/opt/apigee/customer/application/`. How should we identify the active override and decide whether it should be removed or updated?

9. **Traffic drops during maintenance.** The load balancer drains Routers, but requests still reach a Message Processor being upgraded. Which reachability controls and health endpoints should be checked, and how do we keep another processor available?

10. **A 5xx began after certificate rotation.** TLS traffic fails at the Router, while plain HTTP works. The certificate was replaced on the load balancer and on the Router. What logs, ports, and certificate details should be compared?

11. **The UI is healthy but the Management API is slow.** Requests take 30 seconds and sometimes time out. Cassandra is `UN`, Postgres is healthy, and the Router serves traffic normally. Which dependency path should be tested next?

12. **A new environment does not sync.** The organization exists, but the new environment is absent from one Message Processor and present on another. What evidence would distinguish Management Server synchronization trouble from a Message Processor connectivity issue?

13. **A backup is incomplete before a maintenance window.** Cassandra and Postgres backups succeeded, but ZooKeeper backup failed because the service was not stopped. The window starts in two hours. What can be safely retried, and what should the rollback plan record?

14. **An OS upgrade and OPDK upgrade are being combined.** The customer runs 4.52.02 on an older supported OS and wants to upgrade the OS and Apigee in one outage. How should the work be split, and what compatibility pages must be checked?

15. **A patch jump may be unsupported.** The customer wants to move from 4.51.00 directly to 4.53.00 because both installers are available. What must be checked in the target release upgrade path before any node is changed?
