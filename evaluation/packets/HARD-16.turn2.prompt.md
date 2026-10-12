You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# HARD-16: The Management Server will not start, and it started fine three weeks ago

The customer has replied with more information.

## Diagnostic Evidence
The Management Server node can reach all three Cassandra nodes:

```
$ /opt/apigee/apigee-cassandra/bin/nodetool status
Datacenter: dc-1
================
Status=Up/Down |/ State=Normal/Leaving/Joining/Moving

-- Address Load Tokens Owns (effective) Host ID Rack

UN 10.0.0.5 4.58 MiB 1 100.0% c6c130e0-59cf-420e-a315-41d0f9ec51d7 ra-1
UN 10.0.0.6 4.7 MiB 1 100.0% ac456a98-4136-49fb-818f-b2a71fb9575a ra-1
UN 10.0.0.7 4.67 MiB 1 100.0% 78958ae1-3c36-4309-b16b-fbd43446b5a0 ra-1
```

Every node `UN`, single data center, no `describecluster` divergence. So the ring is fine and the
Management Server's own JMX path to Cassandra works. What does not work is the CQL native
transport from the Management Server to 9042.

Port 9042 is documented for exactly this, and 8080 is what the Management Server itself serves:

| Port | What it carries |
| --- | --- |
| 8080 | Management API on the Management Server. Router, Message Processor, UI, Postgres, SSO, and Qpid all depend on it. |
| 9042 | Cassandra inter-node traffic and CQL, used by Router, Message Processor and Management Server. |
| 7000 | Cassandra inter-node communications, Cassandra to other Cassandra nodes only. |
| 9160 | Not described anywhere in the v4.53.01 port tables. It appears only in the page's port filter list. |

After the 9042 path is opened, the Management Server starts and then fails again, differently:

```
INFO c.d.driver.core.Cluster - Cluster$Manager.init() : New Cassandra host /10.0.0.5:9042 added
INFO c.d.driver.core.Cluster - Cluster$Manager.init() : New Cassandra host /10.0.0.7:9042 added
INFO c.d.driver.core.Cluster - Cluster$Manager.init() : New Cassandra host /10.0.0.6:9042 added
ERROR KERNEL.DEPLOYMENT - ServiceDeployer.startService() : ServiceDeployer.deploy() : Got a life cycle exception
while starting service [IdentityZoneService, Keyspace 'identityzone' does not exist] : {}
com.datastax.driver.core.exceptions.InvalidQueryException: Keyspace 'identityzone' does not exist
```

The cluster had no `identityzone` keyspace. This was not caused by the firewall fix. It was
caused by the firewall having been closed during the upgrade window, when the Management Server
setup step was supposed to create the schema, and it persisted after connectivity returned.
