You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# HARD-18: The last data center is already converted

The customer has replied with more information.

## Diagnostic Evidence
`/opt/apigee/apigee-cassandra/bin/nodetool status`, on any Cassandra node:

```
Datacenter: dc-1
================
Status=Up/Down |/ State=Normal/Leaving/Joining/Moving

-- Address Load Tokens Owns (effective) Host ID Rack

UN DC-1-IP1 456.41 KiB 1 100.0% 78fc4ddd-2ed9-4a8c-98a2-63a38c2f1920 ra-1
UN DC-1-IP2 870.93 KiB 1 100.0% 160db01a-64ab-43a7-b9ea-3b7f8f66d52b ra-1
UN DC-1-IP3 824.08 KiB 1 100.0% 21d61543-d59e-403a-bfe7f664baa6 ra-1
Datacenter: dc-2
================
Status=Up/Down |/ State=Normal/Leaving/Joining/Moving

-- Address Load Tokens Owns (effective) Host ID Rack

UN DC-2-IP1 802.08 KiB 1 100.0% 583e0576-336d-4ce7-9729-2ae74e0abde2 ra-1
UN DC-2-IP2 844.4 KiB 1 100.0% fef794d5-f4c2-4a4e-bb05-9adaeb4aea4b ra-1
UN DC-2-IP3 878.12 KiB 1 100.0% 3894b3d9-1f5a-444d-83db-7b1e338bbfc9 ra-1
```

Every node `UN` in both data centers. Nothing is joining, moving or leaving. There is no ring
inconsistency to repair and no node to bring up before continuing.

The Postgres side, on the master:

```bash
/opt/apigee/apigee-service/bin/apigee-service apigee-postgresql postgres-check-master
```

reports that it is the master, and the query timing shows every analytics query running one to
two orders of magnitude slower than it did before the Postgres step.
