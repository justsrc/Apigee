# MED-26 answer key, do not show to the agent

## Ground-Truth Resolution
The gateway is fine and the bundle layout is fine. The build is rewriting the binary. A resource
filter applied to a directory containing a jar treats the jar as text, substitutes placeholders,
and writes it back. The result is a well-formed zip containing a corrupted class, so the runtime
loads the jar, finds the entry, and fails to instantiate the class.

The diagnostic detail is the disagreement between paths. If a manual UI upload of the same jar
works, the gateway, the policy, the class name and the keystore are all exonerated. That leaves
one variable, the bytes. And if the bytes differ between the pipeline artifact and the uploaded
one, nothing in Apigee can explain a difference that exists before the upload.

This is worth separating from the original poster's conclusion. The original report states that
the problem "is pointing to the problem in Maven deployment plugin", and Apigee support declined
further investigation on exactly that basis. A second reporter found the cause in their own POM and
said so honestly: they had `<filtering>true</filtering>` on a directory that included the jar, and
disabling filtering fixed it, while noting it was unlikely to be the original poster's exact issue.

## Correct Remediation
Exclude binary resources from filtering. Scope resource filtering to the directories that
actually contain text templates, or turn it off and do substitutions explicitly. Then rebuild and
redeploy.

Keep binary artifacts out of any text-processing step, including token replacement, property
interpolation and archive repacking that rewrites entries.

## Verification
Rebuild and verify the class magic bytes in the packaged jar before deploying. Confirm the
deployment reaches a state other than ERROR, and confirm the callout executes by exercising the
path that runs it, since a deployment can succeed with a policy that never runs.

## Common Incorrect Answers
Retrying the deployment. The activation timeout message invites this and it cannot succeed; it only
produces more failed revisions.

Upgrading the deployment Maven plugin, which is what the original report and the support response
both pointed at. The artifact was already corrupted before the plugin ever saw it.

Assuming the class name, the jar path or the policy XML is wrong because the error names a class.
The documented cause of this error is already a missing or unreadable class file, so pointing at
the class name restates the error rather than testing it. `ResourceDoesNotExist` is a different
error and refers to the `<ResourceURL>` element, not to the class.

Rebuilding the jar by hand or uploading it through the UI and declaring victory. That works once
and leaves the pipeline broken, so the next deploy fails again.

Assuming the deployment plugin is at fault because support said so. Check the artifact before
accepting the boundary; the defect was in the reporter's build configuration.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Retries the deployment | Blames the plugin | Identifies binary corruption during packaging and names filtering as the mechanism |
| Diagnostic method | Trusts the timeout message | Compares manual upload to pipeline | Inspects the packaged jar bytes and the class magic |
| Handling of support's boundary | Accepts the escalation | Still escalates | Checks the artifact before accepting the boundary, and explains why the gateway is exonerated |
| Quality of next step | Uploads by hand | Upgrades the plugin | Scopes filtering to text resources and rebuilds, then verifies the bytes |

## References
- Real report, with the identical symptom reported by a second user and the filtering cause:
  <https://github.com/apigee/apigee-deploy-maven-plugin/issues/155>
- JavaCallout policy reference and its error conditions:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/java-callout-policy>
- Fault code index, `JavaCalloutInstantiationFailed`:
  `.agents/skills/apigee-support-core/references/error-codes.md`

## Critical failures
recommending a retry loop; concluding that the open source deployment plugin is at fault without inspecting the packaged artifact; editing the policy XML or the class name in
response to an instantiation failure.
