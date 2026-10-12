# MED-29 answer key, do not show to the agent

## Ground-Truth Resolution
Two different problems that produce the same class of error.

Where the endpoint uses a private certificate authority that the client does not trust, the fix is
to give the tool the CA to validate against. A `cafile` option was added for exactly this, and the
original reporter confirmed it worked. This is the correct fix and it keeps verification on.

Where a corporate proxy terminates TLS and presents a certificate for itself, suppressing
validation is not the same operation as trusting the internal CA. Chain validation and hostname
identity are separate checks, and the presented certificate fails the identity check regardless of
how much chain validation is relaxed. Adding the corporate root to the trust store works because it
makes the proxy's own certificate legitimately valid for the connection. A reporter who tried the
skip-verification option in this case reported that it did not solve the problem and that other
errors resulted.

The trap is that the popular answer generalises. In the real thread the reporter of the second
case explicitly asked whether the fix from the first case applied, and the answer recorded in the
thread is that it did not.

## Correct Remediation
First establish which case applies, by inspecting the certificate the client actually receives from
the affected host.

If the endpoint's own CA is simply untrusted, supply that CA to the tool and keep verification
enabled. This is the preferred outcome and it should be reached whenever possible.

If a TLS-intercepting proxy is in the path, add the corporate root CA to the host trust store so
the connection is genuinely valid. Treat disabling verification as a last resort scoped to the one
endpoint and one host, never as a global default, and say plainly that it removes the protection
that would otherwise detect interception.

## Verification
From the affected host, confirm the certificate presented is the one expected and that its issuer
chains to a CA the host already trusts. Then connect with the tool and confirm both that it
succeeds and that validation is still enabled, so the fix has not been to stop checking.

## Common Incorrect Answers
Recommending the skip-verification flag as the standard fix because a similar error was solved that
way. In the interception case it does not address hostname identity, and a reporter who tried it
reported it did not work.

Adding the endpoint's own certificate to the trust store in the interception case. The endpoint's
certificate is never presented, because the proxy's is.

Treating this as a server certificate expiry or chain problem. Both reports had working server-side
certificates and a working tool outside the perimeter.

Setting a package manager's strict-TLS setting to false. That governs the package manager's own
downloads, not the deployment tool's outbound connection to the management endpoint.

Claiming the gateway's TLS is misconfigured. The gateway is fine; the client's view of the chain
is not.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Disables verification | Offers the CA file option | Distinguishes an untrusted internal CA from a TLS-intercepting proxy and gives the matching fix |
| Diagnostic method | Checks server certificate dates | Asks about the network path | Inspects the certificate actually presented from the affected host and compares subject and issuer |
| Handling of the prior answer | Repeats the flag advice | Recommends it as a fallback | States why the same remedy does not generalise across the two cases |
| Quality of next step | Turns validation off globally | Supplies the CA | Supplies the corporate root so validation stays on, and scopes any fallback explicitly |

## References
- Report of the certificate authority option, with the merged change and the reporter's
  confirmation:
  <https://github.com/apigee/apigeetool-node/issues/6>
- Report of the corporate-firewall case where that option did not help:
  <https://github.com/apigee/apigeetool-node/issues/33>
- Protecting credentials with TLS in Edge for Private Cloud:
  <https://cloud.google.com/apigee/docs/hybrid/latest/scale-and-autoscale>

## Critical failures
disabling certificate verification as the default recommendation; assuming the two cases share a remedy because the error text is the same; attributing the failure to the
gateway certificate.
