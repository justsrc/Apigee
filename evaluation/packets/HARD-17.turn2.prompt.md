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

The customer has replied with more information.

## Diagnostic Evidence
Cassandra JMX authentication is enabled, confirmed in
`/opt/apigee/customer/application/cassandra.properties`:

```
conf_cassandra-env_com.sun.management.jmxremote.authenticate=true
```

`CASS_JMX_USERNAME` and `CASS_JMX_PASSWORD` are set in the operator's interactive shell but are
not present in the environment the `update.sh` / `apigee-service` process is launched from -
which is not the same thing, because a login shell sources
`/opt/apigee/customer/application/jmx_auth.sh` and a service invocation from a cron job or a
different operator's session does not.

Running the failing command with the credentials inline succeeds:

```
$ CASS_JMX_USERNAME=ADMIN CASS_JMX_PASSWORD=PASSWORD \
  /opt/apigee/apigee-service/bin/apigee-service apigee-cassandra ring
```

which is the documented self-test:

> Run the following apigee-service command. If it runs without error, your configurations are
> correct.
>
> apigee-service apigee-cassandra ring

A second detail from the source case is preserved here because it changes how the operator reads
the output: `update.sh` reported that the script had exited with status code 1 while the
underlying error was safe to disregard. A non-zero exit from `update.sh` does not by itself mean
the node failed.
