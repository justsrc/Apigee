You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case HARD-16

## Initial Support Ticket
> Our Management Server will not stay up. It starts, runs for a couple of minutes, then dies.
> API traffic is completely unaffected and all our proxies are serving. We upgraded to 4.53.01
> about three weeks ago and this is the first time we have restarted the Management Server
> since. Nothing has changed in the configuration. Please advise urgently, we cannot manage
> environments.

## Initial Evidence
From the Management Server's `system.log`, at
`/opt/apigee/var/log/edge-management-server/logs/system.log` - the Message Processor path
`/opt/apigee/var/log/edge-message-processor/logs/system.log` is documented verbatim, and the log
rotation page states that similar files exist for the other `edge-*` components, naming
`edge-management-server` among them:

```
WARN DATASTORE.CASSANDRA - ConfigurationUtil.resolveLocalDataCenter() : TException while resolving datacenter for
datastoreconfig:[DataStoreConfig{name='identityzone-datastore', type=null, keyspace='identityzone', ...
org.apache.cassandra.thrift.InvalidRequestException: null
```

then, about thirty seconds later:

```
ERROR KERNEL.DEPLOYMENT - ServiceDeployer.startService() : ServiceDeployer.deploy() : Got a life cycle exception
while starting service [IdentityZoneService, All host(s) tried for query failed (tried: /10.0.0.5:9042
(com.datastax.driver.core.TransportException: [/10.0.0.5:9042] Cannot connect), /10.0.0.7:9042
(com.datastax.driver.core.TransportException: [/10.0.0.7:9042] Cannot connect), /10.0.0.6:9042
(com.datastax.driver.core.TransportException: [/10.0.0.6:9042] Cannot connect))] : {}
com.datastax.driver.core.exceptions.NoHostAvailableException:
```

All three Cassandra nodes are unreachable on 9042 from the Management Server node. The upgrade is
three weeks old. Traffic is fine.
