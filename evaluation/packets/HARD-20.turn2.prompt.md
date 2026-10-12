You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case HARD-20

The customer has replied with more information.

## Diagnostic Evidence
`nodetool status` is clean on all six nodes, every node `UN`, no leaving or joining nodes. The
ring is healthy and the replication is complete.

The consistency level configured on the Message Processor:

```
$ cd /opt/apigee/edge-message-processor/conf
$ grep -ri "consistency.level" *
```

which returns the configured value for each keyspace. The documentation's explanation of what
that value means is the whole answer:

> The Cassandra consistency level is defined as the minimum number of Cassandra nodes that must
> acknowledge a read or write operation before the operation can be considered successful.
> Different consistency levels can be assigned to different Edge keyspaces.

> When connecting to Cassandra for read and write operations, Message Processor and Management
> Server nodes typically use the Cassandra value of LOCAL_QUORUM to
> specify the consistency level for a keyspace. However, some keyspaces are defined to use a
> consistency level of one.

> The calculation of the value of LOCAL_QUORUM for a data center is:
>
> LOCAL_QUORUM = (replication_factor/2) + 1

> With LOCAL_QUORUM = 2, at least two of the three Cassandra nodes in the data
> center must respond to a read/write operation for the operation to succeed.

> By specifying the consistency level as LOCAL_QUORUM , Edge avoids the latency
> required by validating operations across multiple data centers.

And the operational consequence, from the Knowledge Hub post:

> Cassandra treats each DC as a separate DC whether they happen to be close geographically or not.
> Replication across DCs is slower than in-DC writes. Apigee configures Cassandra with a
> LOCAL_QUORUM consistency level to optimize write speeds and data security with the assumption
> that traffic from a client typically stays within a DC. If load balancing across AZs, there is a
> risk that data written in AZ1 may not be available in AZ2 when a fast following second call from
> a client comes in. Typically connection reuse and session affinity will limit this risk.

The miss rate correlates with the load balancer placing the write and the read on Message
Processors in different zones. Requests where both land in the same zone never miss.
