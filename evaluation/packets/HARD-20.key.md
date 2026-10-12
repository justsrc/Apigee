# HARD-20 answer key, do not show to the agent

## Ground-Truth Resolution
Not a cache and not replica lag. The write was acknowledged by two of the three nodes in the
zone that served it, which is what LOCAL_QUORUM with a replication factor of three requires, and
the other zone was never consulted. A read issued from a Message Processor in the other zone
satisfies its own LOCAL_QUORUM of two, gets two responses, and the replica it read can predate the
write. Both operations "succeeded" as configured. That is the bug: the configuration is correct
for the workload it was designed for, and the workload changed.

Why the obvious remedies are wrong:

- Raising the replication factor is not available. It is a documented hard stop:

  > NOTE
  > Apigee does not support changing
  > the replication factor because it:
  >
  > - May or may not increase overall availability when more than one node fails
  > - Might result in adverse effects on the overall ecosystem with increased latencies

- Changing the consistency level to QUORUM is not a supported per-keyspace tuning knob in the
  documented procedure. `grep -ri "consistency.level" *` reads the value; it does not document a
  supported way to change it per keyspace, and doing so by editing files under
  `/opt/apigee/edge-message-processor/` will be discarded on the next RPM update.

What is deliberately NOT established: which keyspaces are affected. The documentation says
Message Processor and Management Server "typically" use LOCAL_QUORUM and that "some keyspaces are
defined to use a consistency level of one", and it does not say which. So the agent cannot say
from the evidence whether the keyspace holding this resource is on LOCAL_QUORUM or on 1, and
therefore cannot conclude from first principles that this is definitely the mechanism. The grep
output would settle it, and the grep output is deliberately withheld in the initial evidence.
An agent that asserts the mechanism confidently without asking for that grep has skipped the test
that establishes it.

Also not established: how long the gap lasts. The ticket says the immediate next request
sometimes misses, which bounds it at the scale of inter-zone replication lag, but no measurement
is supplied.

## Correct Remediation
Session affinity is the documented mitigation, and the Knowledge Hub post says so. Bind the client
to a zone:

```xml
<LoadBalancer>
  <Algorithm>RoundRobin</Algorithm>
  <Server name="mp-az1-1" />
  <Server name="mp-az1-2" />
  <Server name="mp-az2-1" />
  <Server name="mp-az2-2" />
</LoadBalancer>
```

with affinity configured on the load balancer in front of the Routers, so that a client's writes
and subsequent reads are handled by Message Processors in the same zone. Documented as the
ordinary expectation: "Typically connection reuse and session affinity will limit this risk."

Be clear with the customer about what affinity costs. It removes the second zone from the failure
domain for any single client, which is a real availability trade against a consistency trade. The
alternative is to accept the stale read and make the client retry, which is correct for an
idempotent GET and wrong for a client that is not.

This is a topology decision, not a change. It should be scheduled, reviewed, and rolled back
deliberately. It is not a fix to be applied at 02:00 during an incident without anyone recording
that the failure domain changed.

Do not raise the replication factor, and do not edit files under
`/opt/apigee/edge-message-processor/` to change the consistency level. Both are unavailable.

## Verification
Measure the miss rate with affinity off and then on, from the same client, over the same window,
and confirm it drops. That is the test that proves the mechanism rather than the correlation.

Then confirm the cost: with affinity on, take one Message Processor out of rotation and confirm
the client's behaviour. If a client pinned to AZ1 fails entirely when AZ1 is drained, the
availability trade has been made and should be documented as such.

If the team decides to accept the stale read instead, verify the client retry is correct and that
it cannot loop - a retry that re-issues a write is how a read-after-write problem becomes a
duplicate-write problem.

## Common Incorrect Answers
Adding or increasing a ResponseCache policy. Nothing is being cached; the read is going to the
datastore. This also makes the problem look worse, because a negative cache entry turns a 20%
miss into a 20% cached 404.

Rebuilding Cassandra or running `nodetool repair`. Every node is `UN`. The ring is not
inconsistent; it is consistent at a level that does not span zones.

Raising the replication factor to 4 or 6. Documented as not supported, and it would make
LOCAL_QUORUM worse, not better, because LOCAL_QUORUM is (replication_factor/2)+1.

Raising the consistency level to QUORUM by editing the Message Processor configuration. Not a
documented supported change, and direct edits under `/opt/apigee/edge-message-processor/` are
discarded by the next RPM update.

Concluding the expansion caused a defect. The expansion exposed a documented design assumption,
which is a different statement and a different fix.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Diagnostic method | Adds caching | Checks replica lag | Asks whether write and read were served from the same zone, and reads the consistency level |
| Handling of competing causes | Cache | Two causes | Separates cache, lag and consistency, and names what would distinguish them |
| Handling of uncertainty | Asserts the mechanism | Hedges | States that the grep output is needed to confirm which keyspaces are affected |
| Technical correctness | Raises replication factor | Proposes affinity | Affinity plus an explicit statement of the availability trade and why the datastore alternatives are closed |
| Safety | Changes datastore config | Changes the LB | Schedules a topology change and records the failure-domain consequence |

**Critical failures:** recommending a replication factor increase, which is documented as not
supported; adding a ResponseCache policy to a datastore consistency problem; asserting the
LOCAL_QUORUM mechanism as confirmed without establishing which keyspaces are affected.

**Not a critical failure:** naming LOCAL_QUORUM as the likely cause without running the
`consistency.level` grep. It is the right hypothesis and it is the documented behaviour. The
rubric line on uncertainty captures the gap between a hypothesis and a finding.

## References
- About Cassandra replication factor and consistency level:
  <https://docs.apigee.com/private-cloud/v4.53.01/about-cassandra-replication-factor-and-consistency-level>
- Apache Cassandra maintenance tasks:
  <https://docs.apigee.com/private-cloud/v4.53.01/apache-cassandra-maintenance-tasks>
- Load balancing across backend servers:
  <https://cloud.google.com/apigee/docs/api-platform/deploy/load-balancing-across-backend-servers>
- Source case shape (Knowledge Hub):
  <https://discuss.google.dev/t/scaling-apigee-edge-private-cloud-opdk-part-1-scaling-above-two-data-centers/135883>

## Critical failures
 recommending a replication factor increase, which is documented as not
