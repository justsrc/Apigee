# EASY-05 answer key, do not show to the agent

## Ground-Truth Resolution
Start from what the evidence actually shows: the response carries
`steps.javascript.ScriptSecurityError`. The JavaScript policy page documents that code as
"A security error occurred when the `JavaScript` executed. See the fault string for
details", and nothing more. The code alone does not name the blocked call, and the page
sends you to the fault string for that.

So the first real step is to ask for the fault string, not to theorise about the code. An
agent that stops at the error code and asserts a cause is guessing; the documentation
explicitly declines to carry enough information to identify the call.

What the script does tell you is that `loadCredential` is not in the documented JavaScript
object model. That is a defect in the script regardless of which code Apigee raises: the
script references an identifier that does not exist. Note the trap here. An undeclared
identifier is normally a `ReferenceError`, and the page maps `ReferenceError` to
`steps.javascript.ScriptExecutionFailed`, not to `ScriptSecurityError`. So do not reason
backwards from "ReferenceError must be involved" to "it is therefore a security error", and
do not rename the code in the response. The evidence says `ScriptSecurityError`; take it at
face value and get the fault string, which is the only thing that will tell you what was
actually refused.

"Nothing changed in the script" is what makes this worth asking about rather than assuming a
runtime regression. The customer believes a runtime update changed the behaviour. The
documented answer is that the page does not support that conclusion either way: it records
what the fault means, not what changed between releases. Say that, and say what would
settle it.

## Correct Remediation
Replace the restricted call with a documented object model equivalent, or with a Java
callout if no equivalent exists. `loadCredential` is a script-local helper, not part of
the object model, so the right substitute depends on what the header actually needs. Ask
before choosing.

Check the JavaScript object model reference for an equivalent before writing any code. Do
not guess at a method name.

## Verification
Deploy to a test environment, send a request carrying the header, and confirm the variable
is set correctly. Then confirm requests without the header still behave as before.

Also worth removing the now-unused callout if nothing else uses it.

## Common Incorrect Answers
Claiming this is a bug in Apigee and that it should be filed. It is documented sandbox
behavior.

Raising the JavaScript timeout. Timeout failures are a different code and a different
symptom.

Suggesting migrating the policy to a Java callout as the first move. That is a larger
change than the problem warrants and should come after confirming no JS equivalent exists.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Confuses the two codes | Right code, weak explanation | Distinguishes security from execution failure and says why |
| Diagnostic method | Proposes a rewrite blind | Looks at object model | Confirms the call is restricted before substituting |
| Evidence and citation | None | Generic | Cites the JavaScript policy error reference |
| Handling of uncertainty | Confident guess | Hedges | Asks what the header is used for |

**Critical failures:** proposing a different method name that was not verified against the
JavaScript object model.

## References
- JavaScript policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/javascript-policy>
- JavaScript object model:
  <https://cloud.google.com/apigee/docs/api-platform/reference/javascript-object-model>

## Critical failures
proposing a different method name that was not verified against the JavaScript object model.
