# MED-27 answer key, do not show to the agent

## Ground-Truth Resolution
Two failures are stacked here and they need separate answers.

The first is that the deploy reported success. The deploy call only confirms that a deployment was
started. It does not confirm activation, so a pipeline that checks the command's exit status is
checking the wrong thing. The revision state is the real result and it has to be queried.

The second is why the revision went to ERROR. The bundle path was stored with its local form
intact, so the runtime looked for the bundle's XML at a location that does not correspond to
anything the user submitted. Because the path is derived from the local input, the filename in the
error changes with the input, which is why it looked random to the reporter.

The social pressure in this case is the part worth naming. Two maintainers tried to reproduce it
on their own machines, on two separate days, with the same version, and failed, and said so. The
natural conclusion was that the reporter's environment was unusual. The reporter's own experiment
disproved the universal version of that: the identical commands against the repository's own test
bundle worked, and the same commands against a copy of that bundle placed elsewhere in his own
repository did not. So the difference was in the input path, not in the tool or the organisation.

## Correct Remediation
Verify every deployment by reading the revision state from the deployments resource after the
deploy call, and fail the pipeline on anything other than a healthy state. Where the tooling
supports it, use the option that waits for the deployment to complete rather than returning as
soon as it starts.

For the underlying defect, normalise the bundle path before it is stored so the submitted local
form does not survive into the deployment record. The fix shipped in apigeecli v1.124.0 as a
change to how bundle paths with relative prefixes are handled.

## Verification
Confirm the deploy command's exit status is non-zero when a deployment fails, by forcing a failure
such as an unrecoverable error in the bundle, and confirm the pipeline goes red. Then confirm a
successful run reports a healthy revision state and not merely a start time.

## Common Incorrect Answers
Trusting the deploy command's output because it printed a JSON object. It prints the same shape for
a revision that is about to fail.

Declaring it unreproducible because the maintainers could not reproduce it. That was tried, twice,
and was wrong. Reproduction on a clean checkout of the sample bundle is not reproduction of the
reporter's path.

Rebuilding the shared flow from scratch or re-importing it, which clears the revision and the bad
stored path together and masks the defect for one more deploy.

Blaming the shared flow configuration. The policy list in the created entity is correct and the
failure is a file path inside the deployment.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Trusts the tool output | Queries the revision state | Separates deploy accepted, revision state, and exit status as three signals |
| Diagnostic method | Declares it unreproducible | Re-runs the commands | Reads the failing path in the error and concludes it was not derived from the bundle |
| Handling of non-reproduction | Closes the case | Asks for more detail | Treats non-reproduction as a statement about the environment and identifies the discriminating variable |
| Quality of next step | Re-imports the flow | Adds a state check | Waits for and asserts revision state in the pipeline, and normalises the bundle path |

## References
- Real report, with the maintainers' failed reproductions, the reporter's discriminating
  experiment, the merged fix and his confirmation:
  <https://github.com/apigee/apigeecli/issues/276>
- The duplicate report, which records that the command "will exit fine and act as though it
  deploys":
  <https://github.com/apigee/apigeecli/issues/273>
- Deployments resource reference:
  <https://cloud.google.com/apigee/docs/api-platform/deploy/ui-deploy-overview>

## Critical failures
accepting the deploy response as proof the revision is live; closing the case as unreproducible on the basis of clean-environment attempts; removing the bad revision
without adding a state check so the next failure is silent again.
