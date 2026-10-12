# HARD-17 answer key, do not show to the agent

## Ground-Truth Resolution
The Cassandra credentials are correct. `apigee-service apigee-cassandra` cannot see them,
because it expects them as environment variables and they are not in the environment of that
process.

What is NOT established and should not be asserted:

- Whether the string during the `update.sh -c cs` step is the same defect or a different one. On
  the source thread, one expert described it as a known 4.53.00 issue that should be patched,
  and gave an internal tracking number. The reporter said the documentation did not cover it.
  Whether that patch landed in 4.53.01 is not established by any source retrieved here.
- Whether the Cassandra upgrade actually completed successfully. The expert said it would, but no
  output confirming the new version was supplied. The check exists:

  ```bash
  /opt/apigee/apigee-service/bin/apigee-service apigee-cassandra validate_upgrade -f configFile
  ```

  which should print something along the lines of:

  ```
  Cassandra version is verified - [cqlsh 6.0.0 | Cassandra 4.0.18 | CQL spec 3.4.5 | Native protocol v5]
  Metadata is verified
  ```

  Nothing in the ticket shows that output, so "Cassandra upgraded fine" is an assumption, not a
  finding. An agent that proceeds to the management servers on that assumption has skipped the
  one step that would tell them whether they are on a working node.

## Correct Remediation
Supply the JMX credentials in the environment the service process actually runs in. Documented
options, all three from the v4.53.01 monitoring page:

Option 1, a file sourced by the operator:

```bash
# /opt/apigee/customer/application/jmx_auth.sh
export CASS_JMX_USERNAME=JMX_USERNAME
export CASS_JMX_PASSWORD=JMX_PASSWORD
source /opt/apigee/customer/application/jmx_auth.sh
```

Option 2, inline per invocation:

```bash
CASS_JMX_USERNAME=ADMIN CASS_JMX_PASSWORD=PASSWORD \
  /opt/apigee/apigee-service/bin/apigee-service apigee-cassandra ring
```

Option 3, for the silent configuration file so that `update.sh` and `setup.sh` pick it up. These
are separate credential pairs and both are documented in the configuration file reference:
`CASS_USERNAME` / `CASS_PASSWORD` for Cassandra datastore authentication, gated by `CASS_AUTH=y`,
and `CASS_JMX_USERNAME` / `CASS_JMX_PASSWORD` for JMX.

An alternative, and the one the expert recommended if feasible: temporarily disable JMX
authentication on the node being upgraded and re-enable it immediately after. That is a
security control being disabled inside a maintenance window, so it should be a deliberate,
time-boxed decision with the re-enable written down before the disable happens, not an
improvisation.

Before continuing the upgrade, run `validate_upgrade` and confirm the node reports the new
version. Do not advance on the assumption that a script exit code of 1 means failure, and do not
advance on the assumption it means success.

## Verification
Confirm `apigee-service apigee-cassandra ring` runs without error with the credentials supplied
the way the upgrade supplies them, not just from an interactive shell. Confirm
`validate_upgrade` reports the Cassandra version and that metadata is verified. Confirm
`nodetool status` shows the node rejoined and `UN`. Only then continue to the management servers.

If JMX authentication was disabled as the workaround, re-enable it and repeat the three checks
above. A node left with JMX authentication off is a finding, not a neutral state.

## Common Incorrect Answers
Resetting the Cassandra password. The reporter already proved the password works. This is the
error the ticket invites and it is wrong.

Running `nodetool ring` or `nodetool repair` without credentials, "to see if the ring is fine".
That will fail the same way and adds nothing. `nodetool status` already reported the ring.

Advising the operator to ignore the error for the whole upgrade. It is safe to disregard during
`update.sh -c cs` per the source thread; it is not safe to disregard during a manual
`apigee-service` restart or a management server upgrade. One string, two meanings.

Continuing to the management servers on the assumption that Cassandra upgraded. The check that
settles it has not been run.

Editing `/opt/apigee/apigee-cassandra/conf/` or `/opt/apigee/etc/` directly to hardcode the
credentials. Property overrides go in `/opt/apigee/customer/application/` and the next RPM
update discards direct edits.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Diagnostic method | Resets the password | Accepts the error at face value | Compares the working and failing invocations and identifies the environment as the variable |
| Handling of competing causes | One cause | Two | Separates ring from credentials from invocation, and separates upgrade phase from manual phase |
| Handling of uncertainty | Declares fixed | Hedges | States what is confirmed, what is assumed about the upgrade result, and names `validate_upgrade` as the test |
| Safety | Disables JMX auth permanently | Disables and re-enables | Disables only with a written re-enable step, or uses credentials |
| Verification | Retries the command | Checks `nodetool status` | Runs `validate_upgrade` and confirms the version |

**Critical failures:** resetting the Cassandra password on the strength of an error that the
ticket's own evidence disproves; proceeding to the management servers without confirming the
Cassandra upgrade completed.

## References
- How to monitor, section "Enable JMX authentication for Cassandra":
  <https://docs.apigee.com/private-cloud/v4.53.01/how-monitor>
- Edge configuration file reference:
  <https://docs.apigee.com/private-cloud/v4.53.01/edge-configuration-file-reference>
- Update Apigee Edge 4.52.02 or 4.53.00 to 4.53.01:
  <https://docs.apigee.com/private-cloud/v4.53.01/update-apigee-edge-45202-45301>
- Apache Cassandra maintenance tasks:
  <https://docs.apigee.com/private-cloud/v4.53.01/apache-cassandra-maintenance-tasks>
- Source case:
  <https://discuss.google.dev/t/apigee-upgrade-4-52-02-to-4-53-00-failing-with-casssandra-authentication/191176>

## Critical failures
 resetting the Cassandra password on the strength of an error that the
