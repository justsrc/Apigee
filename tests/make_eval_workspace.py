#!/usr/bin/env python3
"""Build the directory an evaluating model is actually allowed to see.

Why this exists. `tests/test_leakage.py` proves the packet *text* is clean: no
held-back heading, no ground-truth sentence from the scenario's own file, no
title rendered as a markdown heading. That is worth having and it is not the
whole risk.

The repository puts three answers within one `Read` of the prompt:

  evaluation/packets/<ID>.key.md   the ground truth, remediation and rubric
  scenarios/<suite>.md             every scenario in full, ground truth included
  scenarios/index.md               a table mapping each scenario ID to its title

`make_packets.py` strips the scenario title from the prompt on purpose, with a
comment explaining that titles like "The safest recommendation is to change
nothing" or "Root cause cannot be established" state the grading criterion. It
then writes the ID into the prompt anyway (`# Support case MED-13`), and
`scenarios/index.md` hands the title straight back. Restoring a dropped title
through a lookup table is the same leak the dropping was for.

No tool in this repository stops an agent from reading those files, because the
skill and the answer keys sit under one root and that root is the natural working
directory for any platform that discovers `.agents/skills/`. The protocol says
"never shown to the agent" (`evaluation/test-protocol.md`), which describes the
generator, not the filesystem.

So: build the tree. Copy `.agents/skills/` and the prompt packets for the
requested scenarios into a fresh directory and write nothing else. An agent
pointed at that directory cannot reach an answer key because the answer keys are
not in it. `tests/test_leakage.py` asserts exactly that.

Usage:
    python3 tests/make_eval_workspace.py --out /tmp/run-a
    python3 tests/make_eval_workspace.py --out /tmp/run-a --scenario MED-13 --scenario HARD-22
    python3 tests/make_eval_workspace.py --out /tmp/run-a --with-corpus   # cache research pages too

What lands in the workspace:

    .agents/skills/            the skills, references and all, unmodified
    prompts/<ID>.prompt.md     turn-1 prompt
    prompts/<ID>.turn2.prompt.md turn-2 prompt
    WORKSPACE.md               what this directory is and what it deliberately lacks

What never lands, and why:

    evaluation/                answer keys, grader rubrics, audit notes
    scenarios/                 full scenario text and the ID-to-title index
    research/                  notes that restate specific ground truths
    tests/, archive/           tooling and the original material
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".agents/skills"
PACKETS = ROOT / "evaluation/packets"
SCENARIOS = ROOT / "scenarios"
CORPUS = ROOT / "research/pages"

# Names whose presence in an agent workspace means the isolation failed. Matched
# case-insensitively against every path relative to the workspace root.
FORBIDDEN = ("key.md", "scenarios/", "evaluation/", "audit", "defect-register",
             "review", "grading", "packets/", "notes-", "rubric")

# The permission rules that make the isolation real rather than advisory.
#
# Run 2's deviation log recorded that its working directory was the repository root and
# the answer key was reachable from it, with isolation "an instruction rather than a
# mechanism". These rules are the mechanism. OpenCode evaluates them in the harness before
# a tool call executes, and a configured deny is not overridable: `--auto` only
# auto-approves permissions that are not explicitly denied, and saved approvals "never
# override a configured deny".
#
# The load-bearing rule is `external_directory`. A path outside the workspace Location needs
# external-directory approval before its own read approval is even considered, so denying
# it blocks every read outside this directory regardless of how the path was written:
# absolute, relative with `..`, through a symlink, or via a shared mount.
#
# Verified against a live model on 2026-10-13: `nemotron-3-ultra-550b-a55b` attempted to
# read an out-of-workspace canary and received `Permission denied: external_directory`.
PERMISSIONS = [
    # No process spawning. Shell is the obvious route out: cat, curl, git and python can
    # all reach anything on the host filesystem.
    {"action": "shell", "resource": "*", "effect": "deny"},
    # The boundary itself.
    {"action": "external_directory", "resource": "*", "effect": "deny"},
    # Read-only inside the workspace.
    {"action": "edit", "resource": "*", "effect": "deny"},
    # No network, so no fetching an answer from the documentation the answers cite.
    {"action": "webfetch", "resource": "*", "effect": "deny"},
    {"action": "websearch", "resource": "*", "effect": "deny"},
    # No nested agents, which would not inherit these rules predictably.
    {"action": "subagent", "resource": "*", "effect": "deny"},
]

BANNER = """# Evaluation workspace

This directory was built by `tests/make_eval_workspace.py`. It is the only tree an
evaluating model should be pointed at.

Present on purpose:

  `.agents/skills/`   the skills and their reference files, unmodified
  `prompts/`         the generated turn-1 and turn-2 prompts
  `MANIFEST.json`    scenario list, packet checksums, and the commit this was built from

Absent on purpose:

  `evaluation/packets/*.key.md`  the answer key for every scenario in this run
  `scenarios/`                   full scenario text, including every ground truth
  `scenarios/index.md`           the ID-to-title table
  `research/notes-*.md`          notes that restate specific scenario answers

Those files exist in the repository root, outside this tree. They are kept out of
the workspace so a model with file access has no route to them.

The stripping `make_packets.py` performs is still worth naming, because this banner is
the only place a model reads it: the title is removed from the prompt because titles
state the grading criterion, and the ID on its own does not give it back.

If you are running this workspace, do not read outside it. If your harness gives
you a working directory above it, that is the harness's bug, not a limitation of
the run.
"""


def all_scenario_ids() -> list[str]:
    out = []
    for p in sorted(SCENARIOS.glob("*.md")):
        if p.name == "index.md":
            continue
        for line in p.read_text(errors="replace").splitlines():
            if line.startswith("### ") and len(line) > 4:
                sid = line[4:].split(".")[0].strip()
                if "-" in sid and sid.split("-")[0].isalpha() and sid.split("-")[1:]:
                    if all(c.isalnum() or c == "-" for c in sid):
                        out.append(sid)
    return sorted(set(out))


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def find_leaks(root: Path) -> list[str]:
    hits = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        low = rel.lower()
        for bad in FORBIDDEN:
            if bad in low:
                hits.append(rel)
                break
    return sorted(hits)


def build(out: Path, ids: list[str], with_corpus: bool, force: bool) -> int:
    if out.exists():
        if not force:
            print(f"{out} already exists. Pass --force to replace it.", file=sys.stderr)
            return 2
        shutil.rmtree(out)

    out.mkdir(parents=True)
    shutil.copytree(SKILLS, out / ".agents/skills",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (out / "prompts").mkdir()

    copied, missing = [], []
    for sid in ids:
        for suffix in ("prompt.md", "turn2.prompt.md"):
            src = PACKETS / f"{sid}.{suffix}"
            if not src.is_file():
                missing.append(f"{sid}.{suffix}")
                continue
            shutil.copy2(src, out / "prompts" / f"{sid}.{suffix}")
            copied.append(src)

    if with_corpus:
        (out / "corpus").mkdir()
        for src in CORPUS.glob("*.txt"):
            shutil.copy2(src, out / "corpus" / src.name)

    (out / "WORKSPACE.md").write_text(BANNER, encoding="utf-8")

    # The config is what enforces the boundary. Written into the workspace so it is part of
    # the artifact whose hash goes in the manifest.
    cfg = {"$schema": "https://opencode.ai/config.json", "permissions": PERMISSIONS}
    (out / "opencode.jsonc").write_text(
        json.dumps(cfg, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "built_from_commit": head_commit(),
        "skill_dir_sha256": dir_digest(out / ".agents/skills"),
        "permission_config_sha256": sha256(out / "opencode.jsonc"),
        "permissions": PERMISSIONS,
        "scenarios": ids,
        "prompts": [{"file": p.name, "sha256": sha256(p)} for p in sorted(copied)],
        "corpus_included": with_corpus,
        "missing_packets": missing,
        "forbidden_name_patterns": list(FORBIDDEN),
    }
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n",
                                       encoding="utf-8")

    leaks = find_leaks(out)
    if leaks:
        print("REFUSING: the workspace contains answer material:", file=sys.stderr)
        for ln in leaks:
            print(f"  {ln}", file=sys.stderr)
        return 1

    print(f"workspace: {out}")
    print(f"  scenarios   {len(ids)}")
    print(f"  packets     {len(copied)}" + (f" ({len(missing)} missing)" if missing else ""))
    print(f"  corpus      {'included' if with_corpus else 'excluded'}")
    print(f"  skill sha   {manifest['skill_dir_sha256']}")
    print("  leaks       none")
    return 1 if missing else 0


def head_commit() -> str:
    import subprocess
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, timeout=30).stdout.strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def dir_digest(d: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(d.rglob("*")):
        if p.is_file():
            h.update(p.relative_to(d).as_posix().encode())
            h.update(p.read_bytes())
    return h.hexdigest()[:16]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", required=True, help="directory to build")
    ap.add_argument("--scenario", action="append", default=[],
                    help="scenario ID; repeatable. Default is all of them.")
    ap.add_argument("--with-corpus", action="store_true",
                    help="also copy research/pages, so the agent can read the cached docs")
    ap.add_argument("--force", action="store_true", help="replace an existing directory")
    args = ap.parse_args()

    ids = args.scenario or all_scenario_ids()
    return build(Path(args.out).expanduser().resolve(), ids, args.with_corpus, args.force)


if __name__ == "__main__":
    raise SystemExit(main())
