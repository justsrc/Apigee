# MED-28 answer key, do not show to the agent

## Ground-Truth Resolution
The provisioning leg and the verification leg do not use the same TLS configuration. The client
that performs verification is built with a transport that only sets the skip-verification option;
it never loads the client certificate and key into the TLS configuration, so no client certificate
is presented on the verification requests. On a gateway configured to require mutual TLS, a
request without a client certificate is rejected, and the rejection surfaces as a 400 rather than
the 401 or 500 the tool knows how to interpret.

Two conclusions follow, and the second is the one that catches people. First, the environment is
not broken and the resources were created; the 400s are from the tool checking its own work.
Second, whether this matters depends entirely on runtime type. On hybrid the command succeeds
despite the 400s, so an operator can see a clean run that verified nothing. On SaaS and Edge for
Private Cloud the same run fails, so the same environment produces a different operational
outcome.

The report is also useful as an example of what not to do with a claim. It contains a version
template that the reporter never filled in, no maintainer has replied, and the thread has zero
comments. The structural claim checks out against the source, but nothing about it has been
confirmed by anyone with authority over the tool.

## Correct Remediation
Verify by hand, from outside the tool, with the client certificate presented, so the question of
whether the environment is correct is answered independently of the tool's own check.

Treat a verification failure on hybrid as a warning to investigate, not as a success, because the
tool does not fail the run. If the tool's verification is not presenting the client certificate,
treat every successful hybrid provision as unverified until an out-of-band check confirms it.

## Verification
From a host outside the provisioning container, call the verification endpoints with the client
certificate, key and CA supplied, and confirm the responses are the tolerated 401 or 500 rather
than a 400. On hybrid, record that the tool's exit status is not evidence of verification.

## Common Incorrect Answers
Re-running the provision command. The resources were created successfully; repeating it changes
nothing and risks creating duplicates.

Telling the operator to check deployment status of the proxy. The proxy deployed. The failure came
from a verification call the tool made after the deployment finished.

Rotating or re-importing the client certificate or truststore. External calls with the same
certificate succeed, so the material is fine.

Reading a successful hybrid provision as proof that verification passed. On hybrid the tool does not
return verification errors, so a clean exit code carries no verification information.

Installing the client certificate system-wide to work around it. The gap is that the tool's own HTTP
client is not configured with it.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Re-runs provisioning | Identifies it as a verification failure | Identifies the missing client certificate on the verification leg and says provisioning succeeded |
| Diagnostic method | Rotates certificates | Compares with external calls | Notes that 401 and 500 are tolerated and 400 is not, and reads the path in the tool |
| Product handling | Gives one answer | Notices runtime differences | States that hybrid returns success despite the failures and SaaS and OPDK do not |
| Quality of next step | Re-provisions | Upgrades the tool | Verifies out of band with the client certificate and treats hybrid success as unverified |

## References
- Real report, with the code location and the two verification endpoints:
  <https://github.com/apigee/apigee-remote-service-cli/issues/261>
- Provisioning a tenant with Edge for Private Cloud:
  <https://cloud.google.com/apigee/docs/hybrid/latest/upgrade>
- Hybrid architecture and gateway components:
  <https://cloud.google.com/apigee/docs/hybrid/latest/config-prop-ref>

## Critical failures
telling the operator the provision failed and to retry; treating a successful hybrid provision as verified; rotating valid certificate material because the tool's own
client is misconfigured.
