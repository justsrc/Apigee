# Maintaining this project

Every command below was run and its behaviour observed while repairing the project. Where a
command has side effects, those are stated. Where a command is only as good as its
assumptions, those are stated too.

## The loop

```bash
python3 tests/check_repo.py --strict     # structure, generated freshness, origin classes
./tests/check_urls.sh                    # classify every cited URL (needs network)
python3 tests/fault_probe.py             # prove the checkers still detect defects
python3 tests/test_leakage.py            # prove no answer key reaches a prompt
python3 tests/release_gate.py            # all of the above, machine-readable verdict
```

`check_repo.py` is fast and offline. Run it after every edit. The others are slower; run them
before committing anything that touches a checker, a generator, or a packet.

`release_gate.py --skip-urls` runs offline and records the live URL criterion as BLOCKED
rather than passing it. That is the correct way to run it without a network.

---

## Adding or updating a scenario

1. **Find the code first.** Search `references/error-codes.md`. If it is absent, the page may
   not have been fetched. Do not write a fault code from memory. If you cannot verify it,
   say so in the scenario rather than including it.

   ```bash
   grep -n 'your.code' .agents/skills/apigee-support-core/references/error-codes.md
   grep -rl 'your.code' research/pages/
   ```

   Read the second result. The index is generated and a code documented on several pages
   appears once, attributed to whichever page sorted first, so the index tells you where to
   look, not what is true.

2. **Write the ticket** as a person would, without the cause in it.

3. **Set `Origin:`** to a value that starts with `reported real-world`, `documented`, or
   contains `synthetic`. `check_repo.py` parses the leading keyword and fails on anything
   else. The adversarial and regression suites may not be labelled real-world; they are
   constructed evaluations and counting them as incident reports inflated the library's
   apparent provenance by 21 scenarios.

4. **Fill every required section.** `check_repo.py` lists what is missing.

5. **Write scenario-specific critical-failure conditions.** A generic list copied into every
   scenario is worse than none, because it teaches a grader to rubber-stamp.

6. **Generate the packets:**

   ```bash
   python3 tests/make_packets.py <ID> --turn 1
   python3 tests/make_packets.py <ID> --turn 2
   ```

   This writes three files into `evaluation/packets/`. Running with `--all` rewrites every
   scenario's packets, which is correct after editing any scenario file but makes a large
   diff.

7. **Check:**

   ```bash
   python3 tests/check_repo.py --strict
   python3 tests/test_leakage.py
   ```

Editing a scenario without regenerating its packets is caught: `check_repo.py` compares
mtimes and reports stale answer keys by name.

### Verifying a scenario's provenance

For a real-world case, confirm the original report exists and says what the scenario claims:

```bash
grep -rn 'your-source-id' research/notes-rw-*.md research/issues/ research/so/
python3 tests/check_urls.py scenarios/<file>.md
```

If the source cannot be reached, record that rather than asserting the provenance. Several
scenarios in this library already carry an explicit "unverified" note for this reason, and
that is the correct outcome.

## Verifying a scenario's provenance after a docs change

Fault codes move between pages. The cheap check:

```bash
grep -rl '<fault.code>' research/pages/     # which pages document it today
```

If the code now appears on more pages than `references/error-codes.md` shows, regenerate it
and read the conflict section before quoting a single HTTP status.

## Adding a documentation reference

```bash
./research/fetch.sh <doc-path>             # fetches into research/pages/ and records in MANIFEST.tsv
python3 research/repair_manifest.py --dry-run   # confirm every page resolves
python3 research/repair_manifest.py             # write provenance back to MANIFEST.tsv
python3 research/build_doc_index.py            # regenerate the documentation index
./tests/check_urls.sh
```

`fetch.sh` detects soft 404s. `repair_manifest.py` exists because the filename encoding is
lossy: a page cached under a name that is not its slug gets a derived URL that 404s, and 185
of 294 pages were in exactly that state. The provenance column distinguishes `recorded` from
`guess` from `corrected` from `UNRESOLVED`. If you cannot confirm a page's real URL, it
belongs in `UNRESOLVED` with a reason, not in a plausible-looking guess.

## Rechecking a URL

```bash
python3 tests/check_urls.py                       # whole corpus
python3 tests/check_urls.py scenarios README.md   # specific paths
python3 tests/check_urls.py --json                # machine-readable
python3 tests/check_urls.py --fixtures            # offline, no network
```

Read the status, not just the exit code. `SOFT_404` is a page that returns 200 with Google's
"the equivalent page does not exist in Apigee" body. `CONTENT_MISMATCH` is a real page that
is not the document you cited. `ACCESS_RESTRICTED` is a bot-blocking host, which is not
evidence the citation is broken. `TRANSIENT_FAILURE` and `UNVERIFIED` are retried
automatically; if one survives, it is not a defect in the citation.

If a citation genuinely fails, record it in `research/notes-known-404.txt` rather than
silently deleting it. That file is the argument against guessing URLs, and it only stays
useful if failures keep going into it.

## Regenerating derived artifacts

All four are generated. Do not edit their output.

```bash
python3 research/build_error_index.py       # -> references/error-codes.md
python3 research/build_scenario_index.py    # -> scenarios/index.md
python3 research/build_doc_index.py         # -> research/official-documentation-index.md
python3 tests/make_packets.py --all --turn 1
python3 tests/make_packets.py --all --turn 2
```

`check_repo.py` regenerates the first two in memory and diffs them against what is committed,
so a stale or hand-edited generated file fails the check with the missing codes named. If a
generated file looks wrong, fix the generator or the source page and regenerate. Editing the
output makes the freshness check fail, which is the intended outcome.

## Recording a defect

Add an entry to `evaluation/defect-register.md` with: ID, severity, affected files, the
evidence of failure, a reproduction procedure a reader can paste, the likely cause, the
correction, and the regression test that now detects it.

Then add that regression test:

- **A checker or generator defect** goes in `tests/fault_probe.py`. Each probe copies the
  repository to a throwaway directory, breaks one thing, runs the checker, and asserts the
  checker noticed. If a probe reports a false pass, that is a live defect in the checker.
- **A URL-classification defect** goes in the `FIXTURES` list in `tests/check_urls.py`. These
  run offline and need no network.
- **A content or ground-truth defect** cannot be checked mechanically. It is recorded in
  `evaluation/audit-*.md` with the source page and line that contradicts it.

A defect is closed when a test fails without the fix and passes with it. Changing the file is
not the evidence.

## Resolving a documentation conflict

Do not pick the more convenient page. Create or extend a record under `evaluation/`:

- Both statements, verbatim, with file and line or URL and fetch date.
- The product and version each applies to, quoted from the page rather than assumed.
- Whether the statement is default behaviour, configured behaviour, or a failure condition.
- Candidate explanations, each marked supported or not.
- A status: `RESOLVED`, `VERSION_DEPENDENT`, `CONFIGURATION_DEPENDENT`,
  `DOCUMENTATION_CONFLICT`, or `INSUFFICIENT_EVIDENCE`.

If it cannot be resolved, say so and keep both statements. Two current official pages
disagreeing about load-balanced target rotation is recorded in
`evaluation/source-conflicts-loadbalancing.md` precisely because it was not resolved.

## Evaluating a model

Packets are in `evaluation/packets/`. Give the agent **only** the turn-1 prompt, then the
turn-2 prompt after it has answered. Score with the scenario's own rubric table where it
exists, and with `evaluation/rubric.md` otherwise.

Record per run: scenario ID, skill version or content hash, model and version, the prompt
actually sent, the raw response, per-dimension scores, critical failures found, the final
disposition, the timestamp, and anything blocked.

Keep the raw response. A score without it cannot be re-examined, and grader disagreement
almost always lives in the response text.

Store each run in its own directory. Never overwrite the only copy of a previous run;
generate summaries from the retained evidence instead.

## Comparing two skill versions

Hold model, settings, prompts, evidence and scoring rubric constant. Change one thing. If you
change more than one, the result does not attribute to the skills.

```bash
git rev-parse HEAD                    # record the skill version being tested
```

With a single grader, say so. Add the objective checks (`check_repo.py`, `fault_probe.py`,
`test_leakage.py`) alongside, and report agreement with them rather than treating them as a
second opinion on the same axis. Do not claim statistical significance without an appropriate
analysis and enough data for it.

The one existing A/B run covers 7 scenarios with one grader. It is a smoke test and cannot
support a general effectiveness claim.

## Archiving a deprecated skill or reference

Move it to `archive/<date>-original/<kind>/` with the original path preserved, and record in
`evaluation/defect-register.md` why it was retired. Do not delete: an archived file that is
never loaded is provenance, and `check_repo.py` warns when an active file references an
archived path.

Retired tooling goes in `research/tooling-superseded/` with a row in the README there saying
what replaced it and why. Do not reintroduce anything in that directory.

## Requalifying after a significant change

```bash
python3 tests/release_gate.py
```

A change to a skill, a scenario, a checker, a generator or the rubric is significant.
Read the gate's output rather than its exit code: `BLOCKED` means the check could not run
here, and `UNVERIFIED` means no machine can settle it. Neither is a pass.

A passing gate means the defined checks were executed and behaved as required. It is not a
claim of universal correctness across all Apigee configurations and future incidents.
