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
import functools
import hashlib
import json
import re
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
    """Return paths inside ``root`` that carry held-back answer material.

    Two complementary checks, name-based first then content-based, because names
    alone are trivially evaded: a key copied to ``secret.md`` or ``payload.txt``
    never matches a forbidden *name*.

    (1) Forbidden path-name patterns (case-insensitive), kept from the
        original implementation.

    (2) Content signatures: answer-key section headings and held-back blocks copied
        from the scenario source. Scan every regular file; the specific exclusion
        lists are documented in ``_content_leaks``.
    """
    hits: set[str] = set()
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        low = rel.lower()
        for bad in FORBIDDEN:
            if bad in low:
                hits.add(rel)
                break

    # Content check supplements the names above.
    for rel in _content_leaks(root):
        hits.add(rel)

    return sorted(hits)


# Headings that only an answer key carries. A prompt is built from the ticket and the
# evidence, a skill from the documentation, a corpus page from the page it was fetched
# from: none of them contains any of these, so their presence anywhere in the workspace is
# a leak. Checked on every file.
UNIQUE_KEY_HEADINGS = frozenset({
    "ground truth resolution",
    "correct remediation",
    "common incorrect answers",
    "evaluation rubric",
})

# Headings that DO occur legitimately. "References" and "Verification" are ordinary
# documentation headings, so they are only held against files that are not trusted
# builder output; see _eligible_for_block_scan for why prompts, skills and corpus are
# excluded from that scan.
GENERIC_KEY_HEADINGS = frozenset({"references", "verification"})


def _norm_heading(line: str) -> str | None:
    """A markdown heading reduced to comparable words, or None if the line is not one.

    Every non-alphanumeric character becomes a space, so "Ground-truth resolution" and
    "Ground Truth Resolution" compare equal. The previous version tried to do that with
    `re.sub(r"\\s*[-–—]?\\s*", " ", text)`, where every group is optional and therefore
    matches the empty string at every position: it inserted a space between each
    character and turned "references" into "r e f e r e n c e s". The result was that no
    ordinary heading ever matched, so the heading half of the leak check never fired.
    """
    m = re.match(r"^#{1,6}\s*(.*?)\s*#*\s*$", line.strip())
    if not m:
        return None
    text = m.group(1).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip() or None


def _is_key_heading(text: str) -> bool:
    if "answer key" in text and "do not show to the agent" in text:
        return True
    if text.startswith("critical failure"):
        return True
    if text.startswith("not a critical failure"):
        return True
    return text in UNIQUE_KEY_HEADINGS


def _is_generic_key_heading(text: str) -> bool:
    return text in GENERIC_KEY_HEADINGS


def _content_leak_headings(text: str, generic: bool) -> bool:
    for line in text.splitlines():
        h = _norm_heading(line)
        if h is None:
            continue
        if _is_key_heading(h) or (generic and _is_generic_key_heading(h)):
            return True
    return False


def _held_back_snippets() -> tuple[str, ...]:
    """Build normalised long-text signatures of the held-back material.

    Source of truth is the scenario files under ``scenarios/`` plus the blocks
    ``make_packets`` classifies as never released. Reading the builder's own
    definitions (rather than re-typing them) keeps this from drifting.
    """
    try:
        if str(ROOT / "tests") not in sys.path:
            sys.path.insert(0, str(ROOT / "tests"))
        import make_packets as mpk
    except Exception:
        return ()

    texts: list[str] = []
    for path in getattr(mpk, "FILES", {}).values():
        try:
            if not Path(path).is_file():
                continue
        except Exception:
            continue
        for _sid, block in mpk.blocks(Path(path)):
            hs = mpk.headings_of(block)
            for sec in list(getattr(mpk, "KEY", [])) + list(
                getattr(mpk, "KEY_EXTRA", [])
            ):
                if sec in getattr(mpk, "KEY_EXTRA", []):
                    for piece in mpk.sections(block, sec, hs, prefix=True):
                        if piece:
                            texts.append(piece)
                else:
                    one = mpk.section(block, sec, hs)
                    if one:
                        texts.append(one)
            cf = getattr(mpk, "critical_failures", lambda _b: "")(block)
            if cf:
                texts.append(cf)

    def _norm(s: str) -> str:
        # r"\\s+" matched a literal backslash followed by s, so nothing was ever
        # collapsed and a held-back block copied with different line wrapping produced a
        # different string from the original and was not detected.
        return re.sub(r"\s+", " ", s).strip().lower()

    pieces: set[str] = set()
    for t in texts:
        n = _norm(t)
        if len(n) < 120:
            continue
        # Sliding windows so a *partial* copy of a held-back block is still
        # caught, not only a whole sentence.
        window = 160
        step = 40
        if len(n) <= window:
            pieces.add(n)
            continue
        for i in range(0, len(n) - window + 1, step):
            pieces.add(n[i : i + window])
    return tuple(sorted(pieces))


@functools.lru_cache(maxsize=1)
def _held_back_signature_list() -> tuple[str, ...]:
    return _held_back_snippets()


def _eligible_for_block_scan(rel: str) -> bool:
    # Headings are checked on *every* file (see _content_leaks). Long-form
    # held-back block signatures are only matched against files that are not
    # part of the builder's trusted/allowed output, because those trees
    # legitimately reuse documentation prose and would otherwise false-positive:
    #   prompts/      released ticket + evidence (and is checked separately)
    #   .agents/      shipped skills, trusted content
    #   corpus/       cached research pages, deliberately included
    #   build artefacts (MANIFEST.json, opencode.jsonc, WORKSPACE.md)
    if rel.startswith("prompts/") and rel.endswith(".prompt.md"):
        return False
    if rel.startswith(".agents/"):
        return False
    if rel.startswith("corpus/"):
        return False
    if rel in {"MANIFEST.json", "opencode.jsonc", "WORKSPACE.md"}:
        return False
    return True


def _content_leaks(root: Path) -> list[str]:
    """Return relative paths in ``root`` whose *contents* hold back answer material."""
    hits: list[str] = []
    signatures = _held_back_signature_list()
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        try:
            raw = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if raw == "":
            continue
        generic = _eligible_for_block_scan(rel)
        if _content_leak_headings(raw, generic):
            hits.append(rel)
            continue
        if not generic:
            continue
        norm = re.sub(r"\s+", " ", raw).strip().lower()
        if any(sig in norm for sig in signatures):
            hits.append(rel)
    return hits


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
