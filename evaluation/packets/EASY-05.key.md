# EASY-05 answer key, do not show to the agent

## Ground-Truth Resolution
`loadCredential` is not part of the documented JavaScript object model. It is a helper
that reaches for something the sandbox refuses, and Apigee throws
`steps.javascript.ScriptSecurityError` when a security error occurs during execution. It
is the runtime refusing a restricted call, not a defect in the policy.

The documented fix column for this code sends you to the fault string for details, so the
fault string, not the code alone, is what names the blocked call. An agent that stops at
the code will guess at the cause; one that asks for the fault string will not.

Nothing changed in the script because nothing needed to. The behavior is the documented
sandbox behavior, and the script was relying on a call that should not have been
available.

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
