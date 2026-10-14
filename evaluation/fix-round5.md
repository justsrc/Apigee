# Round 5 fixes: MED-09, EASY-09, MED-11

Three content defects in `scenarios/medium.md` and `scenarios/easy.md`. All verification was
done against the 285-page local cache in `research/pages/`. No network access was used.

---

## MED-09 (MATERIAL) — the answer key recommended elements that do not exist

### Verification

```text
grep -oE '<(DisplayName|Identifier|MessageWeight|Rate|UseEffectiveCount|SpikeArrest)[ />]' \
  pages/api-platform_reference_policies_spike-arrest-policy.txt | sort -u
```

Returns `DisplayName`, `Identifier`, `MessageWeight`, `Rate`, `UseEffectiveCount`,
`SpikeArrest`. The page's own child-element line reads:

```text
| Child Elements | <Identifier> <MessageWeight> <Rate> (Required) <UseEffectiveCount> |
```

Neither `rateLimit` nor `timeWindow` appears anywhere in the corpus:

```text
grep -rn "timeWindow\|rateLimit" pages/ | head -20   ->  (no output)
```

Confirmed. The old key told the respondent to "add SpikeArrest with a low `rateLimit` and
a short `timeWindow`", which is not writable XML.

### The documented form of the rate

From the `<Rate>` element section:

> Valid rate values (either defined as a variable value or in the body of the element) must
> conform to the following format:
>
> - `int``ps` (number of requests per second, smoothed into intervals of milliseconds)
> - `int``pm` (number of requests per minute, smoothed into intervals of seconds)
>
> The value of `int` must be a positive, non-zero integer.

`Default Value: n/a`, `Required?: Required`, `Type: Integer`. The page's own worked examples
are `<Rate>5ps</Rate>`, `<Rate>12pm</Rate>`, `<Rate>30ps</Rate>`, `<Rate>42pm</Rate>`, and
the syntax line is `<Rate ref="flow_variable">rate[pm|ps]</Rate>`.

### What changed

The remediation now states the real child list, shows `<Rate>30ps</Rate>` in a working
policy, and explains that the `ps`/`pm` suffix **is** the window control, which is the
concept the old text was reaching for under the invented attribute name.

Two further corrections came out of the same page while rewriting:

1. The old text said "check the documented defaults for both before choosing values". That
   is not answerable for `<Rate>`, which is Required with a default of `n/a`. A respondent
   following that instruction would go looking for a default that does not exist. Replaced
   with an explicit "do not quote a documented default for `<Rate>`".
2. `<UseEffectiveCount>` now gets deliberate treatment, because the page is emphatic that
   its documented default is `false` while also saying Apigee organizations should set it to
   `true` and that rate smoothing is not supported for them.

Added from the comparing Quota/SpikeArrest page, which is already cited in References:

- Quota "Don't use it to: Protect your API proxy's target backend from traffic spikes."
- "SpikeArrest should always be attached before the Quota policy in the ProxyEndpoint
  Request PreFlow", so bursts are shed before consuming long-term allowance.

### Rubric and incorrect-answers changes

The element names are now load-bearing, so they are graded rather than assumed:

- New rubric row **Policy configuration**: 0 = "Invents elements or quotes a default
  `<Rate>`", 4 = "Uses `<Rate>` with a `ps`/`pm` value and sets `<UseEffectiveCount>`
  deliberately".
- New incorrect answer: naming `rateLimit` or `timeWindow` as SpikeArrest elements.
- New critical failure: writing a `rateLimit` or `timeWindow` element into a SpikeArrest
  policy. This is the defect the answer key itself contained, so it now has to be one.

Checked that no 2- or 4-mark cell restates a critical failure. The 4-mark cell demands the
correct elements; the critical failure names the invented ones. No overlap.

---

## EASY-09 (MINOR, inversion risk) — the fault code contradicted its own evidence

### Verification

```text
grep -n -B4 -A12 "SourceUnavailable\|InvalidSourceType" \
  pages/api-platform_reference_policies_json-xml-policy.txt
```

The two documented causes, quoted from the same table:

- `steps.jsontoxml.InvalidSourceType` — "This error occurs if the type of the variable used
  to define the `<Source>` element is invalid. The valid types of variable are `message`
  and `string`."
- `steps.jsontoxml.SourceUnavailable` — "This error occurs if the message variable specified
  in the `<Source>` element of the JSON to XML policy is either: Out of scope (not available
  in the specific flow where the policy is being executed) or **Can't be resolved (is not
  defined)**"

Confirmed the inversion. The scenario's cause was a variable that does not exist, which is
`SourceUnavailable`'s second documented trigger verbatim. The scenario handed over
`InvalidSourceType` and asked the agent to distinguish it from `SourceUnavailable`, so the
scenario was demanding the agent reject the code the scenario itself supplied.

A second defect surfaced in the same pass: the old policy read
`<Source>request.body.payload</Source>`, and the old ground truth claimed that name "is not
a variable that exists". That is true (`grep -rn "request\.body\." pages/` returns nothing,
and the variables reference documents `request.content` as the payload), but it made the
fault unconditional. A variable that never exists would fail every request, while the ticket
says the endpoint "returns 500 for some requests but works for most".

### Decision: re-picked the fault code

Chose re-picking over rewriting the distinction. The code the scenario hands over should be
the code the evidence supports; making the evidence support `InvalidSourceType` would have
required inventing a mechanism the reference does not describe, since the documented cause is
a type check on a variable that resolved.

New shape:

- Fault code is `steps.jsontoxml.SourceUnavailable`, which matches the evidence exactly.
- `<Source>payload</Source>` names a real flow variable assigned by a conditional JavaScript
  step, so failure is genuinely partial and the ticket's "some requests" is earned.
- The sibling distinction still gets taught, and now as a genuine elimination: nothing
  resolved, so there is no type to check, so `InvalidSourceType` is unreachable.
- `ExecutionFailed` was added as the third wrong turn, since the ticket's "we changed the
  upstream contract last week" is a live lure and it has a documented code of its own
  ("the input payload (JSON) is empty or the input (JSON) ... is invalid or malformed").
- The contract change is preserved as a real but unverified item, since it was a good
  secondary check in the original and there is no reason to throw it away.

The `<OutputVariable>` note was kept and made load-bearing rather than decorative. The
policy now carries `<OutputVariable>xmlBody</OutputVariable>` and the trace shows `payload`
resolving as a string, so the documented rule that it "is mandatory when the variable
defined in the `<Source>` element is of type string" applies directly. Removing it becomes
a real mistake rather than a hypothetical.

### Rubric check: is "the code does not match the evidence" scored as wrong?

Explicitly not. An added **Not a critical failure** clause says so, and the Handling of
uncertainty 4-mark cell now rewards it: "States that the code alone does not decide between
the two causes, then says which one the trace shows." Note that this is safe precisely
because the code was re-picked. Had the code stayed `InvalidSourceType`, the correct response
to the original scenario genuinely was "these do not match", and a rubric that punished that
would be punishing a correct answer.

Error payload kept nested: `{"fault":{"detail":{"errorcode":"..."}}}`, unchanged shape, only
the code value swapped. `steps.jsontoxml.SourceUnavailable` was confirmed present in
`error-codes.md` before use.

---

## MED-11 (MINOR) — the mechanism pointed the wrong way

### Verification

```text
grep -n -i -B2 -A6 "not defined\|unresolved\|private" pages/api-platform_cache_key-value-maps.txt
```

The KVM page documents the `private.` prefix as what keeps a retrieved value out of Debug
sessions, and nothing about a missing key producing a malformed value. The
KeyValueMapOperations page documents `<Get>` as "Retrieves the value for the key specified",
with the value assigned to the `assignTo` variable.

Confirmed the inversion. The scenario described `prod` holding a well-formed `30` and `test`
holding nothing, and then had `prod` fail with "a malformed value in production only". A
present, well-formed value cannot cause an unresolved variable. The absent key was in the
environment that worked.

### What changed

The direction is now flipped and the symptom follows from it:

- `prod` has no `orders.timeout` key at all; `test` has it set to `30`.
- Added the actual policy, so the mechanism is inspectable rather than asserted:
  `<Get assignTo="private.orders.timeout" index="1">` with `<Parameter>orders.timeout</Parameter>`.
- The 500 now follows: nothing to retrieve, so nothing is assigned, so the downstream script
  reads no timeout value.

The ground truth states the principle explicitly, since that is what was wrong before: "A
well-formed value cannot cause an unresolved variable; a missing one does." Also noted that
`<Scope>environment</Scope>` is why the two environments can hold different maps without
anything being mis-deployed, which is the actual lesson of the scenario and was previously
unstated.

### Remediation

Rewritten, because the old text ("Decide whether production should have the key at all. A
default in the policy that handles a missing variable may be better") was written against
the inverted evidence and read as confused once the direction changed. It now presents "add
the key" and "stop depending on the key" as two defensible and genuinely different changes,
with the defaulted-policy option argued rather than merely mentioned.

### Rubric and incorrect-answers changes

- Technical correctness 4-mark cell is now "Identifies the missing map entry in the failing
  environment", and Diagnostic method 4 adds "checks which key is absent". The old wording,
  "Identifies the map difference", is satisfied equally by noticing a differing value, which
  is the wrong observation.
- New incorrect answer: reading the well-formed `30` as the problem because it is a string
  rather than an integer.
- New critical failure: blaming the `30` value in `test` for the production failure.
- Metadata objective updated from "the answer is usually one config value" to name the
  direction requirement.

Checked the critical failure does not overlap a mark cell. The failure names the inverted
reading; the 4-mark cell requires the correct one.

---

## Structural verification after the round

- Scenario counts unchanged: medium 22, easy 15.
- All three edited scenarios re-checked for the 11 sections. The `#### Critical failures`
  line is the 10th heading in medium.md's house style and a bolded paragraph in easy.md's,
  matching the surrounding file in each case.
- Scenario IDs stable and in place: MED-09, MED-11, EASY-09.
- Every fault code appearing in the three edited scenarios checked against
  `.agents/skills/apigee-support-core/references/error-codes.md`:
  `policies.ratelimit.QuotaViolation`, `steps.jsontoxml.ExecutionFailed`,
  `steps.jsontoxml.InvalidSourceType`, `steps.jsontoxml.SourceUnavailable`. All present.
- Error payload nesting unchanged: `{"fault":{"detail":{"errorcode":"..."}}}`.
- Every element named in the rewritten answers re-checked against the cached page. No
  element appears in an answer that is absent from the policy's documented schema.
- No network access used; all greps ran against `research/pages/`.
