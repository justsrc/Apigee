You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-32: Six requests admitted where three per minute is configured

The customer has replied with more information.

## Diagnostic Evidence
```xml
<SpikeArrest async="false" continueOnError="false" enabled="true" name="spikearrest-1">
  <DisplayName>SpikeArrest-1</DisplayName>
  <Identifier ref="request.header.some-header-name"/>
  <MessageWeight ref="request.header.weight"/>
  <Rate>3pm</Rate>
</SpikeArrest>
```

No `<UseEffectiveCount>` element, so the policy is on the token-bucket branch. The current
spike-arrest policy reference states that per-minute rates are "smoothed into intervals of
seconds", that the smoothing algorithm "smooths traffic spikes by dividing the rate limit
that you specify into smaller intervals", and that "Smoothing is not coordinated across
Message Processors." With `3pm` that is one request per 20 seconds **per message
processor**, and six processors admit six.
