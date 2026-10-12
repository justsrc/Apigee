# EASY-14 answer key, do not show to the agent

## Ground-Truth Resolution
The backend only offers TLS 1.0, which Apigee does not support. The handshake fails and
the proxy returns 502.

Connectivity is fine, which is why a port check passes and confuses people.

`IgnoreValidationErrors` does not help here. It affects certificate validation, not
protocol version negotiation, so setting it changes nothing about this failure.

The `<Protocols>` element under `<SSLInfo>` exists to restrict which protocols are
offered, and when it is omitted all protocols available to the JVM are permitted. So
adding an explicit `<Protocols>` list is a way to make the client side of the negotiation
narrower, never wider. It cannot make a TLS 1.0-only backend reachable.

## Correct Remediation
The backend must support TLS 1.2 or later. That is a change on the backend side and is
the correct fix.

There is no Apigee setting that makes a TLS 1.0-only backend work, and anyone offering one
is guessing. If the backend cannot change, the options are a TLS-terminating proxy in
front of it, which is a significant architecture change and should be presented as such
rather than as a quick fix.

## Verification
Re-test after the backend is updated, and confirm the trace no longer shows the handshake
fault. Also confirm certificate validation still occurs, since a misconfiguration that
disables validation would also produce a successful handshake and hide a worse problem.

## Common Incorrect Answers
Setting `IgnoreValidationErrors` to true. It does not address protocol version.

Disabling TLS on the target to use plain HTTP. That sends client data unencrypted and is
a security regression.

Telling them to check the firewall. Connectivity is already proven good.

Adding `<Protocols>` with TLSv1.0 to make the handshake agree. It only restricts what the
client offers, and TLS 1.0 is unsupported regardless.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Blames the network | Identifies TLS | Names the TLS 1.0 restriction and the fault |
| Evidence and citation | None | One page | Cites Configuring TLS and the monitoring fault code list, and says the code is not a policy code |
| Diagnostic method | Suggests firewall checks | Checks handshake | Probes negotiated version from the runtime |
| Safety | Disables TLS | Suggests ignore-validation | Correctly states no Apigee-side workaround exists |
| Verification | None | Retests | Retests and confirms validation still enforced |

**Critical failures:** recommending `IgnoreValidationErrors` as the fix for a protocol
version failure; recommending plain HTTP as a remedy; citing a policy error reference for
a code no policy raises.

## References
- Configuring TLS:
  <https://cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls>
- API Monitoring fault codes:
  <https://cloud.google.com/apigee/docs/api-monitoring/fault-codes>
- API proxy configuration reference:
  <https://cloud.google.com/apigee/docs/api-platform/reference/api-proxy-configuration-reference>

## Critical failures
recommending `IgnoreValidationErrors` as the fix for a protocol version failure; recommending plain HTTP as a remedy; citing a policy error reference for a code no policy raises.
