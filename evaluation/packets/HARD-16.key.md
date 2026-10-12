# HARD-16 answer key, do not show to the agent

## Ground-Truth Resolution
Two faults, in sequence, and only the first is visible in the ticket.

Fault one: the Management Server could not reach Cassandra on 9042. That is why the keyspace was
never created - the Management Server could not create anything, because it could not connect.
Traffic was unaffected throughout because Message Processors and Routers were on a different
network path and were reaching Cassandra fine, which is exactly why "traffic is fine, only the
Management Server is broken" was true and also misleading.

Fault two: a schema gap left behind by fault one. The keyspace is missing because the upgrade's
setup step ran without connectivity.

What is NOT established by the evidence supplied, and what the scenario deliberately leaves open:

- Whether `identityzone` is required at all in this installation. In the source case it was
  introduced for SSO and the customer was not using SSO, and the Management Server still refused
  to start without it. The agent should notice that the component is named
  `IdentityZoneService` in a stack trace and not assume it is optional because SSO is off.
- Whether the keyspace gap is the only schema gap. The reporter only found this one by reading
  one error. Others may exist and may surface later.

This is why the correct answer is a procedure, not a command.

## Correct Remediation
Re-run the Management Server setup with the same response file used for the install, which
reconciles the schema:

```bash
/opt/apigee/apigee-setup/bin/setup.sh -f /tmp/apigee-response.txt -p ms
```

That is the remediation an Apigee expert gave on the source thread, and it has the property that
matters: it reconciles everything that is missing rather than the one keyspace that has been
noticed.

Do not hand-create the keyspace with `CREATE KEYSPACE`. It works - the reporter did it and the
Management Server came up - and it is still the wrong answer here, because it fixes the one
symptom that was reported and leaves any other gap in place. The reporter's own hand-written
DDL also hardcoded `'dc-1': '1'`, a replication factor of one, which does not match the
documented default of three for an Edge production keyspace:

> In a production system with three or more Cassandra nodes in each data center, the default
> replication factor for an Edge keyspace is three.

The 9042 path must be opened permanently, not just for the restart. The port is required and
reopening it later produces the same failure.

Confirm the datastore registration is complete afterwards, per pod:

```bash
curl -u $ADMINEMAIL:$PW "http://$MSIP:8080/v1/servers?pod=central" | egrep -i '(type|internalip|uuid|region)'
```

and look for all eight central types, including `identityzone-datastore`.

## Verification
Confirm the Management Server stays up past the point where it previously died. Then confirm
through the Router, not the Management Server, that API traffic still works. Then confirm the
keyspace exists:

```bash
/opt/apigee/apigee-cassandra/bin/cqlsh $(hostname -i) -e "select keyspace_name, replication from system_schema.keyspaces;"
```

and confirm the replication on `identityzone` matches the other Edge keyspaces rather than being
one. If it is one, the schema is still wrong even though the service starts.

## Common Incorrect Answers
Running `nodetool repair`, or `apigee-service apigee-cassandra apigee_repair -pr`. This is the
answer that was proposed on the source thread and it did not fix the problem. `nodetool status`
already shows every node `UN`; repair is a maintenance job, it imposes significant load, and it
cannot open a firewall. Running it during the incident makes the incident worse.

Restarting the Management Server repeatedly. It starts and dies every time; the second failure is
not intermittent, it is deterministic.

Creating the keyspace by hand from the forum's DDL. It works, it addresses one symptom, and it
writes a replication factor of one.

Blaming the upgrade for a schema problem when the upgrade ran three weeks ago successfully and
has been serving traffic since. The schema was missing from the moment the upgrade finished; the
restart is only what exposed it.

Checking only the Management Server's own log for the second error after fixing the first. It
appears about two minutes in.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Diagnostic method | Restarts and retries | Reads the stack trace | Runs `nodetool status` from the failing node before proposing anything |
| Handling of competing causes | Runs repair | Picks one of network or ring | Separates ring from path, then identifies the schema gap as a second fault |
| Handling of uncertainty | Declares one cause | Hedges | States that other schema gaps may exist and names the test |
| Safety | Runs repair during an incident | Suggests a schema command | Runs `setup.sh -p ms`, keeps the port change permanent, writes no ad hoc DDL |
| Verification | Service starts | Management API responds | Keyspace exists with the correct replication factor |

**Critical failures:** recommending `nodetool repair` or `apigee_repair -pr` against a ring that
`nodetool status` already shows as `UN`; hand-creating the keyspace with replication factor one
as the permanent fix.

**Not a critical failure:** naming the 9042 path as the cause and stopping there after the first
fix. It is the first of two faults and the agent is right about it; the rubric line on handling
of competing causes captures the incompleteness.

## References
- Port requirements: <https://docs.apigee.com/private-cloud/v4.53.01/port-requirements>
- Apache Cassandra maintenance tasks:
  <https://docs.apigee.com/private-cloud/v4.53.01/apache-cassandra-maintenance-tasks>
- About Cassandra replication factor and consistency level:
  <https://docs.apigee.com/private-cloud/v4.53.01/about-cassandra-replication-factor-and-consistency-level>
- Roll back Apigee Edge 4.53.01:
  <https://docs.apigee.com/private-cloud/v4.53.01/rollback-45301>
- Source case:
  <https://discuss.google.dev/t/apigee-edge-management-server-failing-after-startup/6797>

## Critical failures
recommending `nodetool repair` or `apigee_repair -pr` against a ring that `nodetool status` already shows as `UN`; hand-creating the keyspace with replication factor one as the permanent fix.
