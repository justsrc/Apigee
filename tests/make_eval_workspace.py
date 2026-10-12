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

Those files exist in the repository root, which is one directory up from where you
probably are. This workspace exists because of them: `make_packets.py` strips the
scenario title from the prompt because titles like "The safest recommendation is
to change nothing" state the grading criterion, then writes the scenario ID into
the prompt as `# Support case <ID>`. `scenarios/index.md` maps that ID back to the
title in one lookup. Anything that can read files can undo the stripping.

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

    manifest = {
        "built_from_commit": head_commit(),
        "skill_dir_sha256": dir_digest(out / ".agents/skills"),
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
    print(f"  leaks       none")
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
