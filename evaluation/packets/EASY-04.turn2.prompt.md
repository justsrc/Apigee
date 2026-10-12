You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case EASY-04

The customer has replied with more information.

## Diagnostic Evidence
The AccessControl policy contains:

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

`noRuleMatchAction="ALLOW"` is why every caller outside those two ranges is unaffected.
The office egress address is 203.0.113.47, inside the 203.0.113.0/24 block. A change
record shows the range was added two days ago by a security team hardening a blocklist.
