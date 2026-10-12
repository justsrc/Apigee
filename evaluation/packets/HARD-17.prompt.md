You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# HARD-17: The password is right, the error says it is wrong

## Initial Support Ticket
> We are about halfway through the 4.53.01 upgrade and it has stopped. Cassandra will not stop,
  so we cannot continue to the management servers. We have JMX authentication enabled on
  Cassandra. Please advise, we have a maintenance window closing.

## Initial Evidence
```
$ sudo /opt/apigee/apigee-service/bin/apigee-service apigee-cassandra restart
Checking the status of Cassandra before shutdown
Disabling binary...
nodetool: Failed to connect to 'localhost:7199' - FailedLoginException: 'Invalid username or password'.
Unable to disable binary. Disabling gossip...
nodetool: Failed to connect to 'localhost:7199' - FailedLoginException: 'Invalid username or password'.
Unable to disable gossip. Draining...
nodetool: Failed to connect to 'localhost:7199' - FailedLoginException: 'Invalid username or password'.

Could not drain.done
```

The reporter has also supplied the fact that falsifies the obvious explanation:

```
$ sudo /opt/apigee/apigee-cassandra/bin/nodetool -u cassadmin -pw password status

Datacenter: dc-1
================
Status=Up/Down |/ State=Normal/Leaving/Joining/Moving

-- Address Load Tokens Owns (effective) Host ID Rack

UN 10.0.0.1 4.58 MiB 1 100.0% c6c130e0-59cf-420e-a315-41d0f9ec51d7 ra-1
```

The same credentials, the same host, the same port, the same shell. It works.
