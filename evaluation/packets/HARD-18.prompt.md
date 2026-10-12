You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case HARD-18

## Initial Support Ticket
> We finished upgrading the second data center's Cassandra this morning. Since then the Analytics
> queries through the Management API have been extremely slow and our reporting team is blocked.
> We would like to roll the whole thing back to 4.52.02. How do we do that? Please be quick, we
> have a board meeting.

## Initial Evidence
`/opt/apigee/apigee-cassandra/bin/nodetool describecluster`, run from any node:

```
Schema versions :
2eadcd74-0245-309a-9992-3625afa70038 : [ DC-1-IP1, DC-1-IP2, DC-1-IP3 ]
129dc15e-198e-3c11-b64c-701044a3a1ad : [ DC-2-IP1, DC-2-IP2, DC-2-IP3 ]
   ...

Stats for all nodes :

Live : 6
Joining : 0
Moving : 0
Leaving : 0
Unreachable : 0

Data Centers :
dc-1 #Nodes: 3 #Down: 0
dc-2 #Nodes: 3 #Down: 0

Database versions :
4.0.13 : [ DC-1-IP1:7000, DC-1-IP2:7000, DC-1-IP3:7000 ]
4.0.18 : [ DC-2-IP1:7000, DC-2-IP2:7000, DC-2-IP3:7000 ]
```

Every node is up. No node is joining, moving or leaving. Both data centers are on Cassandra 4.
That is Checkpoint 2.

The slowness is in Postgres query performance after the major Postgres upgrade, not in Cassandra.
`nodetool status` is clean on all six nodes.
