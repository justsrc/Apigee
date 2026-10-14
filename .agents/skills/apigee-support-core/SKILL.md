---
name: apigee-support-core
description: Triage and diagnose an Apigee support case from intake to a sourced answer. Use for any Apigee problem report involving policies, deployments, OAuth or JWT, TLS, caching, quotas, routing, hybrid runtime, Edge for Private Cloud, or Management API behaviour. Establishes the product and version first, keeps a hypothesis ledger, separates runtime from deployment errors, and requires every consequential claim to name a source.
---

# Apigee support core

This is the workflow. It runs before any specialised skill and decides which one, if
any, should take over. Read it for a case even when the symptom looks narrow, because
most wrong answers in this product come from applying an instruction to the wrong
product.

## The failure this skill exists to prevent

Apigee has three products that share a proxy runtime and almost nothing else operational.
Apigee X is Google-managed end to end. Hybrid runs the control plane in Google Cloud
and the runtime in a Kubernetes cluster you operate. Edge for Private Cloud runs
entirely on your own hardware with its own install tree, its own service commands and
its own release process.

The runtime behaves similarly across all three, which is exactly why the mistake is so
easy. A `nodetool` command that is obviously nonsense on Apigee X produces a confident,
plausible, completely wrong answer when handed to an OPDK operator, and the person asking
will often act on it.

So the first thing you do is find out what they are running. Not as a formality. Before
any other step.

## Step 1: pin the product

Ask for the product name and the version or release string. If the ticket omits them,
ask before prescribing anything. A question costs one turn. A wrong product assumption
costs an outage.

Look for these tells:

- Mention of `apigee-service`, `apigee-all`, `/opt/apigee`, Cassandra, ZooKeeper,
  OpenLDAP, `update.sh`, or a "data center" of nodes means Edge for Private Cloud.
- Mention of a Kubernetes cluster, Istio, a runtime pod, `apigee-runtime`, or a
  Google Cloud project holding the management plane means hybrid.
- Anything else, especially a Cloud Run or GKE-hosted proxy URL and a Management API
  call, means Apigee X.

When the product is genuinely ambiguous, state the assumption you are proceeding under
and say what would change if it is wrong. Do not silently pick one.

Pin the version too. Hybrid and OPDK both move, and both have removed things. A
procedure from the wrong release is not a close approximation, it is wrong.

## Step 2: intake, but only what the problem needs

Ask for the fields the symptom needs, not a questionnaire. A routing question does not
need a deployment history and an auth question does not need a topology diagram.

Always worth having: the product and version from step 1, what changed and when, the
exact error text including the `errorcode` field rather than the prose, the request that
triggers it, and whether it affects every request or some of them.

Then pick by symptom class:

- **Deploy rejected or proxy will not start.** The revision number being deployed, the
  full deployment error text, and the policy XML of the policy the error names.
- **Requests failing at runtime.** A full trace from API Monitoring rather than the
  dashboard screenshot, including the step timings and the `errorcode` in the response.
- **Auth failure.** The exact status and body, whether it fails for all clients or
  some, and which flow the token was obtained on. Never ask for the token itself.
- **Latency or timeout.** The target's own response time measured from outside Apigee,
  so you can separate gateway time from upstream time.
- **Something works in one environment but not another.** Both revision numbers and
  whatever differs between the two environments.

Tell people how to redact. Ask them to strip authorization headers, `client_secret`
values, keystore passwords, private keys and anything else that is a secret, and to keep
the structure of the value so the shape stays visible. A redacted trace that keeps the
length and prefix of a token is usually enough to diagnose.

## Step 3: classify runtime error against deployment error

This split matters more than it looks, because the two produce different symptoms and
different fixes.

A **deployment error** means the proxy revision was rejected. The error names an
invalid configuration and it has an error name rather than a fault code. The old
revision keeps serving. Nothing ever reached the runtime.

A **runtime error** means the revision deployed and then failed while handling a
request. You get a fault code in the response, and the response also carries
`errorcode`.

If someone is seeing requests fail, it is a runtime error. If someone cannot deploy, it
is a deployment error. Do not spend time on the wrong one.

When you read an error, trap the machine-readable part. Apigee's own guidance is to
match on `errorcode` and never on `faultstring`, because the text can change between
releases. If you match on prose you will break on the next upgrade, and you will also
fail to match anything at all right now.

## Step 4: run the loop

Do these in order. Do not skip to proposing a fix because one explanation felt obvious.

1. Restate the observed problem in one sentence, in terms of what was seen, not what you
   think it means.
2. Separate what is established from what is assumed. Write both down.
3. Run the discriminating test that separates your two or three live hypotheses.
4. Interpret the result and say what it rules out as well as what it supports.
5. Update the ledger.
6. Decide whether you need more evidence or whether you can answer.
7. If you propose a change, state how you will verify it worked.

Step 3 is the one that gets skipped, and skipping it is how a confident wrong answer
gets written. If you cannot name the test that would tell your hypotheses apart, you do
not have two hypotheses, you have one guess and a guess.

## The hypothesis ledger

For anything past trivial, keep this in your working notes and show the interesting rows
in the answer.

| Hypothesis | Supporting | Contradicting | Missing | Test | Result | Status |
| --- | --- | --- | --- | --- | --- | --- |

Use these statuses and use them literally:

- **Confirmed.** A test that only this hypothesis predicts passed. Nothing else survives.
- **Strongly supported.** Evidence fits and alternatives are contradicted, but no single
  decisive test has run.
- **Plausible, unverified.** Reasonable, fits what you have, not yet tested.
- **Disfavoured.** Something contradicts it, though it is not eliminated.
- **Ruled out.** A specific test failed it.
- **Cannot assess.** The information to judge it does not exist yet.

"Symptom stopped after we changed X" is not confirmation. It is mitigation with an
unidentified cause, and something else on the same day may have caused the stop. Say so.

## Sources

Priority, highest first: the version-appropriate official documentation; release notes
and compatibility references; implementation code and tests; something you reproduced
yourself; an issue with a demonstrated fix; an independent explanation with its evidence
shown; an unverified community claim.

This is a preference, not a law. A reproducible experiment that contradicts the
documentation is more informative than the documentation, and you should report that as a
documentation defect rather than quietly working around it.

When sources disagree, compare versions, dates and products before choosing. Do not
pick the one that supports what you already concluded.

Cite the specific page for anything consequential. "According to Google documentation"
is not a citation. A policy reference page for the exact policy and element is. Cite
policy facts to the policy page, not to a general troubleshooting index.

Verify a URL before you cite it. In this project, `research/fetch.sh` does that and
records the status. Guessed URLs in this documentation set fail often enough to matter.
If you cannot verify a URL, link the nearest verified parent page and say the specific
page is unverified.

## Acting on the system

Sort every proposed action before recommending it:

- **Read only.** Look at logs, query the Management API, list deployments.
- **Local.** Reproduce on a scratch revision or a local bundle.
- **Reversible.** A config change you can undo in one step.
- **Disruptive.** Restarts, drains, redeploys, anything that moves traffic.
- **Destructive or sensitive.** Deleting resources, replacing certificates, changing
  credentials, touching production routing.

Do not run or recommend a disruptive or destructive action against production without
explicit authorization, and say plainly what the blast radius is. A fix that works but
takes the API down is not a fix.

Prefer read-only diagnosis. Most tickets resolve on evidence, not on changes.

## Writing the answer

Order matters. Someone reads the first two lines and decides whether to keep going.

Lead with the assessment and its confidence. Then the evidence, quoted exactly rather
than paraphrased. Then what to do. Then how to confirm it worked. Then what you could
not determine.

Skip sections that would be empty. A one-line question deserves one line back, not ten
numbered headings. Reserve the full structure for an incident.

When the cause is not established, say that in the first paragraph, name the two or three
things still in play, and give the single next test that would separate them. An
honest "not yet, here is the test" is worth more than a confident story, and it is the
answer that stops someone from breaking production on a guess.

Never end with a root cause you did not establish.

## When to hand it off

Stop and escalate, saying what you need, when any of these hold:

- The evidence you need requires access you do not have and the user has not been asked
  for it.
- Evidence contradicts itself and no available test resolves it.
- The behaviour looks like a product defect rather than a configuration problem.
- The only remaining paths are destructive and nobody has authorized them.
- The case spans a product boundary you cannot verify, such as a hybrid runtime fault
  that is really in a customer-managed ingress.

Name the specific artifact you need, not "more information". "The full trace for one
failing request from API Monitoring, with the `errorcode` field" is actionable. "More
logs" makes people send everything.

## Reference files

Load these on demand. They are not loaded with this skill, and none of them is a
substitute for opening the primary page before you assert something consequential.

| File | Use it for |
| --- | --- |
| `references/error-codes.md` | Matching a fault code or `errorcode` to the policy that owns it |
| `references/products.md` | Telling the products apart, and where an answer must branch |
| `references/security.md` | OAuth, JWT, API keys, and TLS behaviour and limits |
| `references/hybrid.md` | Hybrid runtime, sync, key-value maps, logging, upgrades |
| `references/policy-mechanics.md` | Targets, timeouts, deployment, variables, and conditions |
| `references/sources.md` | Verified URLs, how to check one, and how to find more |

Intake and action safety stay in this file rather than becoming lookups, because what to
ask and how risky a suggested action is depends on the case in front of you.

Specialised skills take over from here once the product and area are known:

- `apigee-opdk-troubleshooter` for Edge for Private Cloud runtime faults.
- `apigee-opdk-upgrader` for Edge for Private Cloud upgrades and rollbacks.
