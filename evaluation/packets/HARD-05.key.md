# HARD-05 answer key, do not show to the agent

## Ground-Truth Resolution
Revision 22 fails and revision 21 succeeds, so the differentiator is the serving revision,
not the client and not the payload. That is why the failure looks random.

The fleet is mixed because hostnames are defined on the environment group and route to any
environment in that group, and because a deployment replaces the prior revision within the
environment it targets. Two environments sharing one hostname is what puts revision 21 and
revision 22 on the same base path. The rollback moved `prod` only, so `prod-b` kept serving
revision 22 and the rate did not move.

What the trace evidence does not settle on its own: an in-flight deployment produces the
same signature, because deployments are eventually consistent across Message Processors
and a deployment stays in a progressing state until the runtime has loaded it. A mixed
fleet and an unpropagated deployment are indistinguishable from the trace alone. The
per-environment deployment list is what separates them, which is why one environment must
not be assumed.

## Correct Remediation
Bring `prod-b` back to revision 21, which is the command that was rejected:

```bash
gcloud apigee apis deploy 21 --environment=prod-b --api=reports --override
```

The flag is not incidental, and naming the reason is the whole point of this remediation. By
default a proxy's base path must not already be in use by a deployed proxy in the target
environment, and revision 22 currently holds `api.example.com` on `prod-b`. `--override` is
what permits Apigee to undeploy the conflicting proxy as part of deploying revision 21.

This is the general trap in rollbacks: the revision you deploy to undo something is by
definition not the newest revision on the base path, so the plain form of the command is
the form most likely to be refused. An agent that runs the deploy without the flag, sees it
rejected, and reports the rollback as blocked has mistaken the guard for the fault.

Confirm afterwards, per environment, that revision 21 is the only revision serving.

Reproduce revision 22's failure in `test` before any further rollout. If the hostname has
to be off the failing environment to stop the bleeding, that is a valid temporary move,
but it changes who can be deployed to and should be recorded as one.

## Verification
Confirm traces show only revision 21 serving, and confirm it per environment rather than
in aggregate, since aggregate is exactly what hid this. Confirm 502s stop. Then reproduce
revision 22's failure in `test` before rolling forward again.

## Common Incorrect Answers
Concluding the rollback failed because the symptom persisted. The rollback succeeded as a
revision operation in `prod` and never reached the environment that was failing.

Assuming random distribution means a flaky network.

Assuming one environment can serve two revisions at once. A deployment replaces the prior
revision, so a stable mixed fleet means more than one environment is serving the hostname.

Blaming the load balancer without checking which revision served each request.

Reading the rejected rollback as a further failure of the rollback, rather than as the
base path guard doing its job.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Diagnostic method | Calls it random | Checks traces | Correlates failures with serving revision, then enumerates environments |
| Handling of competing causes | Rollback failed | Network theory | Separates mixed fleet from unpropagated deployment and names the test |
| Technical correctness | Random cause | Flaky infra | Identifies revision 22 and the second environment as the differentiator |
| Quality of next step | Redeploy | Re-check the rollback | Moves the second environment with `--override`, explains the base path conflict, and reproduces in test |

**Critical failures:** declaring the symptom random without correlating with the serving
revision; concluding the rollback failed without checking which environments it reached.

**Not a critical failure:** proposing the deploy with `--override` but without explaining
the base path conflict. That is a partial answer, not a wrong one.

## References
- Environments overview:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/environments-overview>
- Deploy an API proxy revision:
  <https://cloud.google.com/apigee/docs/api-platform/deploy/ui-deploy-overview>
- `gcloud apigee apis deploy` and `--override`:
  <https://cloud.google.com/sdk/gcloud/reference/apigee/apis/deploy>
- Trace and debug:
  <https://cloud.google.com/apigee/docs/api-platform/debug/trace-overview>
- API Monitoring fault codes:
  <https://cloud.google.com/apigee/docs/api-monitoring/fault-codes>

## Critical failures
declaring the symptom random without correlating with the serving revision; concluding the rollback failed without checking which environments it reached.
