You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# ADV-12: Contradictory evidence requiring a decision

## Initial Support Ticket
> The on-call engineer says the 502s started at 14:00. The dashboard says they started at
> 13:30. We need to know which is right before we decide whether to roll back the 14:15
> deploy.

## Initial Evidence
Two accounts of the same failure's onset, differing by 30 minutes. A deployment is recorded
at 14:15, after both stated onsets. None of the three sources says what timezone it is
using, and the two accounts do not agree on what they are measuring.
