# Confirmed: the evidence is gone. Here is what to change.

**That is the end of the diagnosis.** Retention windows have passed and there is no trace, no
log and no per-request record left to work from. I am not going to name a cause, and neither
should anyone else who offers one.

There is one thing you can still compute, and it is worth doing before you close the ticket:
re-run the aggregation grouped by API, revision, status code and hour over the same two weeks.
It will tell you whether the 200 were one thing or several and whether they line up with a
deploy. That is a real result and it is usually enough to decide whether this is worth
reopening later.

## What to change, in the order I would do it

1. **Get an `errorcode` out of every future failure.** This is the highest-value change on the
   list and it costs one policy. A `RaiseFault` or an AssignMessage after the point of failure,
   or a fault rule that logs, so that each failure carries the stable code rather than only a
   prose `faultstring`. Group on `errorcode`, never on `faultstring`: the prose changes between
   releases, so grouping on it breaks and gives you a number you cannot act on. With codes
   logged, the next occurrence answers the question "is this the same 200" in one query.

2. **Alert on the rate, with a denominator.** You found this because a person was looking. An
   alert on an abnormal failure rate for that API gives you the timestamp, and the timestamp is
   the one thing you cannot reconstruct today. Define the denominator now: 200 out of 40
   million is noise and 200 out of 400 is an outage, and you need to know which before you
   choose a threshold.

3. **Trace the APIs that failed, for a bounded window.** Continuous tracing is expensive, so do
   it as a deliberate short-term measure: sample at a low rate, or trace continuously for one
   named API and revision during the hours you expect trouble, then turn it off. Set a calendar
   reminder, because a sampling change left on for a month is a bill nobody expects.

4. **Send Message Processor logs somewhere with its own retention.** Runtime logs are separate
   from API Monitoring traces and they rotated too, which is why you lost both. Shipping them
   off the pod, or raising their retention, is what stops the next occurrence from ending in
   this conversation.

5. **Extend the API Monitoring retention if the cost is acceptable.** Check what your current
   window actually is before assuming it is the platform default, then decide deliberately
   whether two weeks is the right number for how fast you want to be able to investigate.

## What I would not do

I would not reconstruct the incident from the count. It is tempting to look at which APIs have
the highest failure counts and call the worst one the cause, and on a 200-failure sample across
two weeks that is a guess with a chart attached.

## How you will know the change worked

The test is the next occurrence. When the alert fires, you want three things you do not have
today: the `errorcode`, a trace of at least one failing request, and the timestamp. If a repeat
incident produces those three, the change worked, and you can send me the trace and get an
answer in one turn instead of none.

## What I could not determine

What the 200 failures were, and whether the next batch is the same problem. Both are now
dependent on the changes above rather than on anything I can retrieve.