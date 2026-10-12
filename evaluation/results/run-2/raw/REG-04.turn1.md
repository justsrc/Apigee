# About 200 failures, two weeks, no retained evidence

**Short answer: no, not about these 200.** What you have is a count. A count cannot be
diagnosed, and I am not going to reconstruct a cause from it. There is no honest answer here
beyond what to do about the next batch, which is worth doing.

**Product.** Your wording is consistent with Apigee X or hybrid through API Monitoring. Tell me
which, and the version, because the retention and export controls differ.

## What you still have

Before concluding the evidence is gone, check these four. People routinely have more than they
think:

1. **The aggregation query's dimensions.** If the metric you counted grouped by API, revision or
   status code, the shape of the failures is still there even though the traces are not. The
   query is cheap to re-run and it may show that all 200 were one API and one status, which
   would narrow this a long way.
2. **Analytics.** If the dashboard is on, the same events live there with a longer retention
   window than the trace store.
3. **Runtime logs.** Message Processor logs are separate from API Monitoring traces and are
   still rotating unless something purged them. A grep for the error text across the window
   may recover both the occurrences and their frequency.
4. **Cloud Audit Logs.** Deployments, proxy changes and organization-level changes in the
   period will tell you whether anything changed, which is the other half of the question.

If any of those exist, send them and I will work from them.

## What to change so the next batch is answerable

This is the part I would actually spend your time on.

1. **Turn on trace sampling for the APIs that failed, temporarily.** Continuous full tracing is
   expensive, so the honest version is: sample at a low rate, or trace continuously for the
   specific API and revision that was failing, and turn it back off afterwards. Without at
   least some traces, every future incident of this kind ends here too.
2. **Log the `errorcode`, not the `faultstring`.** This is the one piece of advice that pays
   for itself immediately. The `faultstring` is prose that changes between releases, so matching
   or grouping on it breaks and tells you nothing you can act on. The `errorcode` is stable and
   is what you would group on to tell whether the next 200 failures are the same 200.
3. **Set an alert on the failure count itself.** You found these because someone was looking.
   An alert on a rate that is abnormal for that API gets you the timestamp to correlate with,
   which is the one thing you cannot reconstruct now.
4. **Decide what "200 failures" has to mean.** Right now it is not actionable at all, because
   nobody defined the denominator. 200 out of 40 million requests is noise; 200 out of 400 is
   an outage. Whichever it is, the ratio is the number you need and it is still computable from
   the metric you already have.

## If you need this answered now

It cannot be, and anyone who gives you a confident root cause for 200 failures with no trace,
no log and no per-request record is guessing. What you can get today is the shape: re-run the
aggregation grouped by API, revision and status, and by hour. That tells you whether it was
one thing or several, and whether it correlates with a deploy. That is a real result, and it is
usually enough to decide whether to keep digging.

## What I could not determine

What the failures were. Nothing in a count can tell me that, and the only way to find out is to
make the next ones observable.