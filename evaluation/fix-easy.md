# Fix report: scenarios/easy.md

Single file changed: `scenarios/easy.md`. No network used. All facts verified against
`research/pages/` and `.agents/skills/apigee-support-core/references/error-codes.md`.

## FIX 1 — EASY-04, invalid AccessControl XML

The old snippet used a nonexistent `<Address>` element and a `<SourceAddress>` wrapper
with no parent policy. Replaced with the real schema from
`pages/api-platform_reference_policies_access-control-policy.txt`:

```xml
<AccessControl name="ACL">
  <IPRules noRuleMatchAction="ALLOW">
    <MatchRule action="DENY">
      <SourceAddress mask="24">203.0.113.0</SourceAddress>
      <SourceAddress mask="24">198.51.100.0</SourceAddress>
    </MatchRule>
  </IPRules>
</AccessControl>
```

Story preserved: office blocked, everyone else fine, range added by security team two days
ago. Added one line noting `noRuleMatchAction="ALLOW"` is why other callers are
unaffected, which is the asymmetry the scenario already depended on. Ground-truth now
says the address is specified "in a `SourceAddress` element", matching the wording in
`error-codes.md` line 22.

## FIX 2 — EASY-12, premise was invented

Rewritten. The old narrative (401, `nbf` clock drift, `nbf` vs `exp` leeway) is not in
the documentation. Now built on what `pages/api-platform_reference_policies_revoke-oauth-v2-policy.txt`
actually states:

- Fault code is on the RevokeOAuthV2 page, not OAuthV2. Reference changed accordingly.
- HTTP status is 500, not 401.
- Cause is a fixed lower bound: "Timestamp cannot be earlier than January 1, 2014."
- `<RevokeBeforeTimestamp>` type is 64-bit milliseconds since 1970 UTC, cannot be in the
  future and cannot be before 2014-01-01.
- The element is optional and defaults to policy execution time, so omitting it does not
  produce this code — added as an explicit discriminator.

Two realistic triggers, both landing on the same bound: an absent query parameter
resolving to `0`, and a caller sending Unix seconds where milliseconds are documented.
The future-dated half is handled as `InvalidFutureTimestamp`, also 500, so the three
codes are kept distinct instead of collapsed.

## FIX 3 — EASY-14, code absent from the error index

`messaging.adaptors.http.flow.SslHandshakeFailed` is **not** in `error-codes.md`. It is
documented in exactly two cached places:

- `pages/mon_fault-codes.txt` (line 77) — maps gateway fault
  `FailedHandshakeWithTargetEndpoint`, component Target, to the errorcode.
- `pages/fix-options-configuring-tls.txt` (line 8) — "Apigee does not support the use of
  TLS 1.0 or TLS1.1 ... throws the error `messaging.adaptors.http.flow.SslHandshakeFailed`."

Reframed so the evidence is the documented protocol restriction, not a policy code:

- Added a "Caveat on the fault code" subsection stating exactly where it is documented
  and that no policy raises it.
- Diagnostic evidence now shows the monitoring trace shape (gateway fault plus underlying
  errorcode) rather than a bare trace line.
- Added the `<Protocols>` element fact: it restricts what the client offers, and omitting
  it permits all JVM-available protocols, so it can never widen to reach a TLS 1.0-only
  backend. Added as an incorrect answer and to the ground-truth.
- Rubric gained an "Evidence and citation" row; citing a policy error reference for this
  code is now a critical failure.
- Reference added: <https://cloud.google.com/apigee/docs/mon/fault-codes>
- File header now names EASY-14 as the single documented exception to the
  "must be in error-codes.md" rule, instead of leaving the file self-contradictory.

## FIX 4 — file wide, `context.request.getValue` does not exist

Two occurrences, both in EASY-05. The object model page
(`pages/api-platform_reference_javascript-object-model.txt`) does not document
`context.request.*.getValue(...)` anywhere; it uses `context.getVariable("request.header.X")`
(lines 33, 830, 1142) and `context.getVariable("request.content")`. Used that form.

**Deviation worth flagging:** the brief suggested `context.request.header.getValue(...)`.
That form is not present anywhere in the 387 cached pages, so using it would have been
another unverifiable claim. Went with the form the cache actually evidences.

Because a valid call cannot throw ScriptSecurityError, the surrounding scenario was
adjusted rather than the API call alone:

- Script is now a real header read plus a script-local helper `loadCredential` that is
  explicitly "not part of the documented JavaScript object model".
- Diagnostic evidence changed from the invented `JavaScript.fromCharCode(0)` to removing
  the helper line, which actually isolates it.
- Ground-truth now leans on what the docs really say: the fix column for
  `ScriptSecurityError` is "See the fault string for details", so the fault string is
  what names the blocked call. This removes the prior claim about which Java method was
  invoked.
- Rhino 1.7.13 engine fact confirmed at `pages/fix-javascript-policy.txt` line 16.

## FIX 5 — file wide, invented trace step names

`AM-Count-Tokens` and `SA-Protect` in EASY-08 were the only literal matches. `OAuthV2/VerifyAccessToken`
was also a guess. Replaced the trace block with policy-type labels and an explicit note
that real step names are whatever the team named each policy. The scenario's actual
teaching point (the code is shared by Quota and SpikeArrest, so the trace step is the
discriminator) is unchanged and still valid.

`AM-VerifyToken`, `AM-Enrich` and `AM-Target` did not appear in this file.

---

# Second pass: three defects (no network, `research/pages/` only)

## FIX 6 — EASY-06, the ground truth was backwards

**Confirmed.** The old scenario asserted that `request.header.Authorization` and
`request.header.authorization` are different flow variables, and that the client sent the
header in lowercase. The cache shows both spellings documented as defaults for the same
wire header:

- `pages/api-platform_reference_policies_decode-jwt-policy.txt:98`,
  `pages/api-platform_reference_policies_decode-jws-policy.txt:130`,
  `pages/api-platform_reference_policies_verify-jws-policy.txt:458`,
  `pages/api-platform_reference_policies_verify-jwt-policy.txt:1038` — `request.header.authorization`
- `pages/api-platform_reference_policies_basic-authentication-policy.txt:298,305` — `request.header.Authorization`

The scenario was rebuilt around a cause the documentation actually supports.
`pages/api-platform_troubleshoot_policies_runtime_basic-authentication-runtime-errors.txt`
gives the cause for `steps.basicauthentication.UnresolvedVariable` as exactly two
candidates, and it is verbatim the same pair that
`pages/api-platform_reference_policies_json-xml-policy.txt:605` documents for
`steps.jsontoxml.SourceUnavailable`:

> Out of scope (not available in the specific flow where the policy is being executed)
> Can't be resolved (is not defined)

Its diagnosis step 3 is literally "Determine if the variable is defined and available in
the flow in which the BasicAuthentication policy is being executed", and it notes the error
"can only occur if `IgnoreUnresolvedVariables` element is set to `false`". That last fact
was already the scenario's evaluation objective and is preserved.

New case: `<Source>encodedBasicAuth</Source>`, where the step assigning `encodedBasicAuth`
sits **after** the BasicAuthentication step in the same flow. The documented scope failure
is the cause; the fix is step order.

Also carried over from the documented playbook: the faultstring is what names the failing
variable (`"faultstring": "Unresolved variable : request.header.Authorization"`), so the
faultstring now arrives only in Diagnostic evidence and the agent has to ask for it.

**Critical-failure re-check (as instructed).** The old trip-wires would have caught a
correct answer — the old incorrect-answer list said "HTTP headers are case-insensitive so
it must work... which is exactly the bug here", i.e. it forced the casing answer. The three
new trip-wires are all things a correct answer would never do:

1. recommend `IgnoreUnresolvedVariables` be set to `true` as the fix (ground truth says
   that only silences it; element reference says `false` is the usual setting here);
2. remove the BasicAuthentication policy;
3. treat the fault as a deployment error (ground truth says it is a runtime fault).

A correct answer — reorder the steps, or point `<Source>` at `request.header.Authorization`
if that is the real contract — trips none of them.

**Additional defect found and fixed in passing:** the old XML was malformed,
`<Source request.header.Authorization</Source>`, missing the `>`. The rewritten policy
uses the documented element, with `<Operation>Decode</Operation>` added, which is a real
element (`basic-authentication-policy.txt:183`).

## FIX 7 — EASY-10, invented elements named as the fix

**Confirmed.** `grep -rlE 'SecretVariable|VerificationOutputVariableToVerify' pages/` returns
nothing across all 408 cached pages. The real elements in
`pages/api-platform_reference_policies_hmac-policy.txt` are `<Algorithm>`, `<SecretKey>`
and `<VerificationValue>`.

Replaced with `<SecretKey>` (Presence: Required; "There is no default value for the
referenced variable; the ref attribute is required") and `<VerificationValue>`
(Presence: Optional; "Include it to perform an HMAC check").

Two further corrections came out of the same evidence:

- **`<Algorithm>HS256</Algorithm>` was invalid.** The documented valid values are
  `SHA-1, SHA-224, SHA-256, SHA-384, SHA-512, MD-5`, and `SHA256` is explicitly
  equivalent ("SHA256 and SHA-256 and sha256 are equivalent"). `HS256` is JWS naming, not
  HMAC naming, and would have tripped `steps.hmac.InvalidValueForElement`. Changed to
  `SHA256`.
- The incorrect answer "add the secret inline in the proxy XML" was previously just a
  style objection. It now cites a real code, `steps.hmac.InvalidSecretInConfig` ("occurs if
  there is a text value explicitly provided for `SecretKey`"), plus
  `steps.hmac.InvalidVariableName` for the `private.` prefix requirement, so the safe
  remediation shape is documented rather than asserted.

Added nuance the old version flattened: `<VerificationValue>` is Optional, so its absence
raises no deployment error at all and would leave a policy named `VerifySignature` silently
not verifying. That is a genuinely different failure from the missing required element.

The old trip-wire "recommending committing a secret" still holds. Two new ones added:
treating it as a runtime error worth tracing, and naming absent elements outside the HMAC
schema. Neither catches a correct answer.

## FIX 8 — file wide, `context.variable(...)` does not exist

Four occurrences, none of them in the documented object model.
`pages/api-platform_reference_javascript-object-model.txt` documents only
`context.getVariable` (lines 33, 445, 528, 830, 833) and `context.setVariable`
(lines 34, 112, 115, 846, 847); there is no `context.variable` anywhere.

| Line | Before | After |
| --- | --- | --- |
| 546 (EASY-05) | `context.variable("token", loadCredential(token));` | `context.setVariable(...)` |
| 561 (EASY-05) | `context.variable("token", token);` | `context.setVariable(...)` |
| 995 (EASY-08) | `parseInt(context.variable("tokenCount"), 10)` | `parseInt(context.getVariable("tokenCount"), 10)` |
| 997 (EASY-08) | `context.variable("tokenCount", count);` | `context.setVariable("tokenCount", count);` |

The one-argument read became `getVariable`; the two-argument writes became `setVariable`.

## Integrity check (second pass)

- 15 scenarios, IDs EASY-01 through EASY-15, unchanged.
- All 11 required subsections present 15 times each.
- Zero occurrences remain of `context.variable`, `SecretVariable`,
  `VerificationOutputVariableToVerify`, `HS256`, or any case-sensitivity claim.
- All 17 ```xml and 9 ```json fenced blocks parse (ElementTree / json.loads), 0 failures.
- Error payloads keep the nested `{"fault":{"detail":{"errorcode":...}}}` shape; all 9
  `errorcode` occurrences are inside `"detail"`.
- Only `scenarios/easy.md` and this report were modified.