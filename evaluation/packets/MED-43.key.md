# MED-43 answer key, do not show to the agent

## Ground-Truth Resolution
The use of wildcards in Apigee proxy base paths may conflict with other explicit base paths,
resulting in a `404`. In this case, calls to the explicit base path resolve successfully while
calls to `Proxy-2` may return a `404`, if the wildcard path is evaluated as `/a/v1/c`.

The important part is what the register says next: the issue is fixed in Apigee and in hybrid
1.14.3 and later, however the fix is **not enabled by default**. Enabling the use of wildcards
in base paths requires a support request for Apigee orgs, and a documented procedure for hybrid
orgs.

So the customer's premise is exactly wrong in the most confident possible way. They checked the
version, the version says fixed, and the fix has not been switched on for their org. An agent
that treats "fixed in 1.14.3" as "therefore not our problem" closes the case wrongly, and an
agent that recommends only an upgrade has already been given the upgrade.

Note the asymmetry that makes this hard to spot from the outside: an agent that establishes "the
environment group is serving traffic" has proved nothing, because a sibling proxy in the same
environment is serving fine.

## Correct Remediation
For an Apigee org, contact Apigee support to request that the wildcard base path fix be enabled.
For a hybrid org, follow the documented procedure for 1.14.3 or 1.15.1. Until then, remove the
wildcard and use explicit base paths, which is the only configuration guaranteed to be unambiguous.

## Verification
Call the wildcard path and confirm it resolves. Then confirm the explicit path still resolves,
because the fix changes conflict resolution between them rather than in isolation.

## Common Incorrect Answers
Recommending another upgrade. The customer is already on a version that contains the fix.

Concluding the environment group or the deployment is at fault. Other proxies on the same group
serve traffic, including a sibling on the same prefix.

Removing the conflicting explicit base path without asking. That is a client-visible breaking
change for whichever team owns it.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Recommends an upgrade | Identifies wildcard and explicit base path conflict | Names the `/a/v1/c` collision and the opt-in nature of the fix |
| Diagnostic method | Checks the group | Compares the two base paths | Uses the working-versus-failing asymmetry within one environment |
| Version handling | Reads "fixed" as resolved | Notices opt-in wording | States that hybrid 1.14.3 contains a fix that is disabled by default |
| Quality of next step | Upgrades again | Deletes the explicit path | Requests enablement for Apigee, follows the procedure for hybrid |

## References
- Known issues register (entry 378686709):
  <https://cloud.google.com/apigee/docs/release/known-issues>
- Upgrading Apigee hybrid: <https://cloud.google.com/apigee/docs/hybrid/v1.17/upgrade>

## Critical failures
telling the customer to upgrade when they are already on a fixed version; concluding the environment group is at fault because other proxies on it serve traffic.
