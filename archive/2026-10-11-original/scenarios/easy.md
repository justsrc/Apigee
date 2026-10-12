# Easy scenarios

Use these as short, single-symptom prompts. They should exercise the first-pass diagnosis or upgrade checks without requiring a large amount of context.

1. **Message Processor will not start.** We restarted `edge-message-processor`, but `apigee-service edge-message-processor status` still reports it as stopped. The node is running OPDK 4.53.00. What should we collect and check first?

2. **Router returns 503 after a reboot.** The load balancer marks one Router unhealthy after a planned restart, while the other Router still serves traffic. How do we verify the Router is ready before putting it back in rotation?

3. **Management API returns 500.** Calls to the Management API started returning HTTP 500 after a configuration change. Which component status and log files should we inspect?

4. **One Cassandra node is down.** `nodetool status` shows one node as `DN` and the remaining nodes as `UN`. What is the safe first response, and what should we avoid doing immediately?

5. **Organizations are missing from the UI.** The Edge UI loads, but the organization list is empty. The runtime still serves existing APIs. What dependencies and logs should we check?

6. **A proxy deployment fails.** A deployment to the `test` environment fails with a generic error in the UI. What information should we gather before retrying the deployment?

7. **A policy reports an invalid configuration.** A newly deployed proxy returns a policy fault, but the same policy worked in another environment. Where should we look for the documented policy error and what release information matters?

8. **The Router cannot reach a Message Processor.** Traffic to one API returns 502, while another API works. Which ports and health checks should we verify?

9. **ZooKeeper reports a connection error.** Several components log connection failures to ZooKeeper after a network firewall change. Which ports and quorum checks are relevant?

10. **Postgres replication is lagging.** The standby is several hours behind the master, and analytics data is delayed. What should we establish before restarting either database node?

11. **LDAP authentication fails.** Users receive login failures in the Edge UI, but API traffic is normal. Which component and port should be checked first?

12. **A property change had no effect.** We edited a component configuration file, restarted the process, and saw no change. Where should OPDK overrides live, and how can we confirm which file wins?

13. **A component restart caused dropped requests.** An operator restarted a live Router directly and users saw connection resets. What should the normal restart procedure do differently?

14. **A backup command failed.** The team tried to back up Cassandra while the database service was unhealthy. What precondition does the backup require, and what should be fixed first?

15. **The target release is unclear.** A customer asks to upgrade from 4.52.02 to "the latest OPDK" and wants a command immediately. What release and compatibility details must be confirmed before proposing a plan?
