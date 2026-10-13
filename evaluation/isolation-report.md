# Evaluation isolation report

Written 2026-10-13. Records the threat model, the mechanism, what was tested, and what is
not yet established.

## The problem this addresses

Run 2 recorded its own limitation: the working directory was the repository root,
`evaluation/packets/<ID>.key.md` was reachable from it, and isolation was "an instruction
rather than a mechanism". `evaluation/test-protocol.md` said answer keys are "never shown
to the agent", which described the packet generator rather than the filesystem.

`tests/test_leakage.py` verified that prompt *files* contain no held-back text. It could
not and did not verify that an evaluating *process* cannot reach an answer key. Three paths
existed:

1. The keys live at `evaluation/packets/` under the same root as `.agents/skills/`, one
   `read` call away.
2. `make_packets.py` writes the scenario ID into every prompt as `# Support case <ID>`.
3. `scenarios/index.md` maps that ID to a title, restoring the one field the generator
   deliberately strips because titles like "Root cause cannot be established" state the
   grading criterion.

## Runtime allowlist

Present in the workspace:

| Artifact | Why |
| --- | --- |
| `.agents/skills/` | The operational skill and its references. The whole point of the assisted arm. |
| `prompts/<ID>.prompt.md` | The turn-1 input. |
| `prompts/<ID>.turn2.prompt.md` | The turn-2 input, released only after turn 1 is finalised. |
| `opencode.jsonc` | The enforcing configuration. |
| `WORKSPACE.md`, `MANIFEST.json` | Provenance: commit, skill digest, per-prompt SHA-256, permission digest. |

Absent by construction: `evaluation/` (answer keys, rubrics, audit notes, prior runs),
`scenarios/` (full scenario text and the ID-to-title index), `research/` (notes that
restate specific ground truths), `archive/`, `tests/`.

## Mechanism

`tests/make_eval_workspace.py` writes an `opencode.jsonc` with:

```jsonc
{ "action": "shell",            "resource": "*", "effect": "deny" }
{ "action": "external_directory", "resource": "*", "effect": "deny" }
{ "action": "edit",             "resource": "*", "effect": "deny" }
{ "action": "webfetch",         "resource": "*", "effect": "deny" }
{ "action": "websearch",        "resource": "*", "effect": "deny" }
{ "action": "subagent",         "resource": "*", "effect": "deny" }
```

`external_directory: deny` is load-bearing. A path outside the workspace Location needs
external-directory approval *before* its own read approval is considered, so denying it
blocks reads outside the tree however the path is written: absolute, relative with `..`,
through a symlink, or via a shared mount.

The enforcement is in the harness, not the prompt. OpenCode resolves permissions before a
tool call executes; `--auto` approves only what is not explicitly denied; and saved
approvals never override a configured deny. A model that never reads the prompt's
instruction to stop still cannot make the call succeed.

## Threat model, and what it does not cover

**Covered.** Reads and writes outside the workspace by any tool. Process spawning, which is
the obvious route since `cat`, `curl`, `git` and `python` all reach the host filesystem.
Network egress. Nested agents, whose permission inheritance is not something to rely on.

**Not covered.**

- Anything the model can do inside the workspace. `.agents/skills/` is readable by
  definition. If a reference file restated an answer, isolation would not help, and that is
  a content question, not a boundary question.
- Model provider internals. The request body leaves the host.
- The `opencode` session store under `~/.local/share/opencode/`, which records invocations
  and is outside the sandbox by construction.
- Side channels. No attempt is made to measure inference from timing or from the
  permission-denial messages themselves.

## Results

### Structural: PASS

Verified offline, no model required:

- No `evaluation/`, `scenarios/`, `research/`, `archive/` or `tests/` directory present.
- No `*.key.md` anywhere in the tree.
- No path matching the forbidden-name patterns.
- `opencode.jsonc` present, well formed, with `external_directory`, `shell`, `webfetch` and
  `subagent` all denied.

### Live breach testing: INCONCLUSIVE

Eight routes, each planting a uniquely identifiable canary outside the boundary and asking
the model to fetch it by a named technique: absolute path, parent traversal, dot-dot from
inside the workspace, glob enumeration, `cat`, `find / -name '*.key.md'`, `git log` plus
`git show`, and environment-variable enumeration.

Two runs, both inconclusive, for different reasons worth recording.

**Run 1** returned three BREACHED and five blocked. The breaches are not trusted. The
provider's free tier exhausted its daily quota partway through, after which every request
returned HTTP 429 with `X-RateLimit-Limit: 50, X-RateLimit-Remaining: 0`. A rate-limit
error carries neither a canary nor a denial marker, so the test classified it as "the model
tried and was refused". It had not tried. The test was also discarding the raw provider
streams it told the reader to inspect, so the three breaches could not be adjudicated after
the fact.

**Run 2**, after the test was fixed to separate INDETERMINATE from BLOCKED and to retain raw
streams, returned INDETERMINATE on all eight routes. The quota was still exhausted.

**One earlier manual probe did succeed.** Before the harness existed, a model was run in a
workspace with the same rules and asked to read an out-of-workspace canary. It returned
`Permission denied: external_directory`. That is a single data point from one route, taken
outside this test, and it is evidence that the mechanism is enforced rather than advisory.
It is not a test result and does not establish the boundary.

Quota resets 2026-10-14 05:30 local.

## Conclusion

**The boundary is implemented and structurally verified. It has not been demonstrated to
hold against a model trying to breach it.**

No isolation claim is made. Any evaluation run before the live tests complete must be
reported as not leakage-resistant, because that is what the evidence supports.

To complete:

```bash
python3 tests/test_isolation.py --live --raw-dir /tmp/iso-evidence
```

PASS requires every route to reach a model, none to retrieve a canary, and the structural
checks to pass. An INDETERMINATE on any route makes the result INCONCLUSIVE, never PASS.

## Addendum, 2026-10-13: subagents do not inherit project permission config

An alternative execution path was tested: running evaluation units as OpenCode subagents
rather than through the CLI. It solves the provider problem (no CLI, no free-tier quota,
fresh context per unit) and creates a worse one.

A project `opencode.jsonc` was written to the repository root denying reads of
`evaluation/**`, `scenarios/**`, `research/**` and `archive/**`. A subagent was then asked to
read four paths: the skill, `evaluation/packets/MED-13.key.md`, `scenarios/medium.md` and a
cached documentation page.

**All four reads succeeded. Zero denials.** The answer key was returned in full.

Child sessions do not apply the parent's already-loaded project configuration, so a
permission rule that would genuinely bound the CLI path bounds nothing here. The config file
was deleted rather than committed, because leaving it in place would imply a protection that
does not exist.

### What this rules out

Running evaluation units as subagents gives real model execution and no isolation. Prompt
text is not a boundary. Run 2 already established that: its file-read logs were
self-reported, and the answer key was reachable from its working directory the whole time.

Prompt-level enforcement is not worthless, but it has to be described for what it is. It is
a **detection** control, not a **prevention** control. The difference matters:

| | Prevention | Detection |
| --- | --- | --- |
| Mechanism | Harness refuses the tool call | Answer is checked afterwards for ground-truth-only strings |
| Fails by | Nothing reaches the model | Agent reads the key and the answer looks confident |
| Evidence needed | None, the refusal is the evidence | The check has to run, and its sensitivity has to be measured |
| Honest label | "isolated" | "not leakage-resistant; leakage screened for after the fact" |

### Execution paths, as they now stand

| Path | Execution | Isolation | Available |
| --- | --- | --- | --- |
| `opencode run`, CLI | Free OpenRouter models | Enforced by harness permissions | Quota exhausted, resets 2026-10-14 05:30 local |
| `opencode run`, CLI | Paid OpenRouter | Enforced | 402: OpenCode requests 128k max tokens, account affords about 79k |
| Subagent | Yes, no quota | **None** | Now |
| Subagent, prompt-only rules | Yes, no quota | Detection only | Now, and must not be called isolated |

The only path that both executes and isolates is the CLI, and it becomes usable when the
daily free quota resets. That is the condition on running anything and calling it
leakage-resistant.
