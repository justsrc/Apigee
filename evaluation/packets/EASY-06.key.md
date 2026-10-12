# EASY-06 answer key, do not show to the agent

## Ground-Truth Resolution
The variable named in `<Source>` is not available in the flow where the policy is being
executed, because the step that assigns it runs after the policy that reads it. The
documented diagnosis step is exactly this check: determine whether the variable is defined
and available in the flow in which the policy is being executed.

This is a runtime fault. The policy parsed and deployed fine and fails on every request at
execution time, which is why the 500 is universal rather than intermittent.

`IgnoreUnresolvedVariables` being `false` is what turned an unavailable variable into an
error instead of silently continuing. With the flag set to `true` the policy does not
throw when a variable cannot be resolved, so the same ordering bug would let requests
through with no decoded credentials instead of failing loudly.

## Correct Remediation
Put the assigning step before the policy that reads it. Step order inside the flow is the
fix, not the policy configuration:

```xml
<Flow name="partner-auth">
  <Request>
    <Step><Name>BuildBasicAuthVariable</Name></Step>
    <Step><Name>DecodeBasicAuth</Name></Step>
  </Request>
</Flow>
```

If the partner actually sends a standard header, the intermediate step is unnecessary. The
documented example for this policy points `<Source>` at the request header variable:

```xml
<BasicAuthentication name="DecodeBasicAuth">
  <Operation>Decode</Operation>
  <Source>request.header.Authorization</Source>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
</BasicAuthentication>
```

Confirm which of the two the partner contract actually implies before choosing. Do not
write either variant on a guess.

## Verification
Send a request carrying credentials and confirm the decoded username and password
variables are populated, not merely that the request returned 200, because a decode policy
with nothing to decode can still return 200. Then confirm a request without credentials
still fails, which proves the policy is checking rather than passing through.

## Common Incorrect Answers
Setting `IgnoreUnresolvedVariables` to `true`. That hides the 500 while letting requests
through with no credentials. The element reference says this setting is usually `false` for
a BasicAuthentication policy precisely because it is beneficial to throw an error when the
username or password cannot be found.

Reading it as a malformed Base64 payload, that is, a decoding problem. The faultstring
reports an unresolved variable, which is a failure to resolve the variable, not a failure
to decode its contents.

Treating it as a deployment or configuration validation failure. The policy deployed and
parsed; it fails at request time, and no revision was re-saved.

Removing the BasicAuthentication policy. That silently removes authentication for every
caller, not just the affected route.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Blames Base64 or the deployment | Identifies the unresolved variable | Names the scope cause and quotes both documented candidates |
| Diagnostic method | Guesses | Asks for the faultstring | Asks for the faultstring and checks step order in the flow |
| Evidence and citation | None | Generic | Cites the BasicAuthentication runtime error reference |
| Quality of next step | Suppresses the error | Reorders the steps | Reorders the steps and offers the header-source alternative |
| Safety | Removes the policy | Reorders without asking | Changes step order and asks which contract applies |
| Verification | None | Retests once | Confirms decoded values and confirms missing credentials still fail |

**Critical failures:** recommending `IgnoreUnresolvedVariables` be set to `true` as the
fix; removing the BasicAuthentication policy; treating the fault as a deployment error.

## References
- BasicAuthentication policy error reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/policies/basic-authentication-policy>
- BasicAuthentication runtime errors:
  <https://cloud.google.com/apigee/docs/api-platform/troubleshoot/policies/runtime/basic-authentication-runtime-errors>
- Flow variables and conditions:
  <https://cloud.google.com/apigee/docs/api-platform/fundamentals/flow-variables-and-conditions>

## Critical failures
 recommending `IgnoreUnresolvedVariables` be set to `true` as the
