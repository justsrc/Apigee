# MED-41 answer key, do not show to the agent

## Ground-Truth Resolution
API products are limited to 50 paths. This is a limitation, not a defect, and it is still OPEN
on the register, so the correct answer is not to wait for a fix.

Two details deserve attention. The message says 51 because it reports the first value that
breaches a limit of 50, so "51" is the ceiling plus one and not an off-by-one bug. And
"Operation Config" is not an Apigee component a support engineer can look up; it is an internal
operation-config limit surfacing through the save path, which is why the message names something
the customer is not editing and why it appears in no Apigee fault-code reference.

An agent that reads "Operation Config" as a proxy or deployment component will go and inspect
proxies that were never touched.

## Correct Remediation
The first published workaround is to combine resource paths and operations using wildcard
patterns, which reduces the number of separate paths without changing what clients call.

The second is to create multiple API products. The register states this has been verified as
viable, and it includes the sentence that matters most operationally: the App associated with
the API products must be updated to include the new one, but credentials and client-side
request details have been proven not to need changing. That is what allows a support engineer to
tell the customer their existing clients are unaffected.

## Verification
Save the API product and confirm the limit error is gone. Then confirm the App now references
every product a client needs, because that is the step the workaround actually requires and the
step most likely to be forgotten.

## Common Incorrect Answers
Blaming the proxy. No proxy was modified and no proxy is misconfigured.

Treating "51" as a miscount and arguing the limit is really 51. The limit is 50; the message
reports the breaching value.

Searching for `Operation group limit` in an Apigee error-code index. It is not an Apigee error
code and will not be there.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Investigates the proxy | Identifies the API product path limit | Names the 50-path limit and explains the 51 in the message |
| Diagnostic method | Greps fault codes | Reads the message | Recognises it is a limit message, not a runtime fault payload |
| Product knowledge | Suggests a new environment | Suggests wildcards | Gives both published workarounds, including splitting into multiple products |
| Client impact | Advises re-issuing credentials | Says clients still work | States the App must be updated but credentials and client-side details do not change |

## References
- Known issues register (entry 402739748):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Configuring resource paths:
  <https://cloud.google.com/apigee/docs/api-platform/publish/create-api-products#behavior-resource-path>

## Critical failures
attributing the failure to a proxy; telling the customer their credentials must be re-issued.
Not a critical failure: proposing multiple API products without noting the App update. It is an
oversight rather than a wrong answer, and the register itself flags the same omission in its own
second workaround.
