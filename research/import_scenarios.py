#!/usr/bin/env python3
"""Import proposed scenarios from a research note into the scenario library.

Research agents write candidate scenarios into notes-rw-*.md rather than editing the
scenario files directly. That keeps a possibly-wrong contribution out of the graded
library until it has been checked, which matters because every agent that edited
scenarios directly in this project also introduced defects.

This script appends them to the right file and refuses anything that is not structurally
sound. It does not check technical accuracy; that is what the review passes are for, and
this project's own history is that structural soundness and accuracy are independent.

Usage:
    python3 research/import_scenarios.py research/notes-rw-github.md --into medium
    python3 research/import_scenarios.py <file> --into hard --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parent.parent
SCEN = ROOT / "scenarios"

TARGETS = {
    "easy": SCEN / "easy.md",
    "medium": SCEN / "medium.md",
    "hard": SCEN / "hard.md",
    "adversarial": SCEN / "adversarial.md",
    "regression": SCEN / "regression.md",
}

# Same list the harness enforces, so an import cannot create a file that fails the check.
# Aligned with tests/check_repo.py, which does not require a diagnostic evidence
# section. The regression scenarios are deliberately single-turn and short, so requiring
# one would reject sound material. Enforcing a stricter rule than the harness means the
# gate and the suite disagree, and the gate wins in practice because it is what actually
# blocks an import.
REQUIRED = [
    "scenario metadata", "initial support ticket", "initial evidence",
    "expected investigation", "ground-truth resolution",
    "correct remediation", "verification", "common incorrect answers",
    "evaluation rubric", "references",
]
OPTIONAL = ["diagnostic evidence"]

ID_RE = re.compile(r"^###\s+((?:EASY|MED|HARD|ADV|REG)-\d{2,3})\b")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def norm(t: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z ]", " ", t.lower())).strip()


def headings(block: str) -> list[tuple[int, str, int]]:
    out: list[tuple[int, str, int]] = []
    fenced = False
    for i, line in enumerate(block.splitlines()):
        if FENCE_RE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            out.append((len(m.group(1)), m.group(2).strip(), i))
    return out


def extract_blocks(text: str) -> list[tuple[str, str]]:
    lines = text.splitlines()
    starts: list[tuple[int, str]] = []
    fenced = False
    for i, line in enumerate(lines):
        if FENCE_RE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        m = ID_RE.match(line)
        if m:
            starts.append((i, m.group(1)))
    out: list[tuple[str, str]] = []
    for n, (ln, sid) in enumerate(starts):
        end = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
        out.append((sid, "\n".join(lines[ln:end]).rstrip()))
    return out


def problems(block: str) -> list[str]:
    """Structural faults only. Returns a list, empty meaning structurally fine."""
    bad: list[str] = []
    hs = headings(block)
    body = block.splitlines()
    seen: set[str] = set()
    # Normalise the search terms too. "Ground-truth resolution" normalises to
    # "ground truth resolution" while the literal in REQUIRED keeps its hyphen, so the
    # comparison silently never matched and every scenario was rejected. This is the
    # third time this project has made that exact mistake in three different scripts.
    wanted = [(want, norm(want)) for want in REQUIRED[1:]]
    for idx, (_lvl, text, ln) in enumerate(hs):
        if idx == 0:
            continue
        n = norm(text)
        for want, wn in wanted:
            if n == wn or wn in n:
                stop = hs[idx + 1][2] if idx + 1 < len(hs) else len(body)
                content = "\n".join(body[ln + 1:stop]).strip()
                # A section can be deliberately empty. ADV-06 is a vague report where the
                # correct behaviour is to ask questions, so its initial evidence is
                # literally "None." Rejecting that would reject the scenario for being
                # true to its own premise.
                deliberate = content.strip().rstrip(".").lower() in {
                    "none", "nothing", "n/a", "not applicable", "(none)",
                }
                if len(content) < 40 and not deliberate:
                    bad.append(f"section '{text}' present but nearly empty")
                seen.add(want)
                break
    for want, _wn in wanted:
        if want not in seen:
            bad.append(f"missing section '{want}'")
    if not re.search(r"https?://", block):
        bad.append("no source URL anywhere in the block")
    # Error payloads must be the documented nested shape.
    if '"errorcode"' in block and '"fault"' not in block:
        bad.append("flat error payload; must be nested under fault.detail.errorcode")
    # Every fenced JSON block must actually parse. A blockquote prefix lands inside the
    # captured group, so strip it before checking.
    for m in re.finditer(r"```json\n(.*?)\n(?:>\s*)?```", block, re.DOTALL):
        payload = re.sub(r"^>\s?", "", m.group(1), flags=re.MULTILINE)
        try:
            import json as _json
            _json.loads(payload)
        except ValueError as e:
            bad.append(f"JSON block does not parse: {e}")
    return bad


def existing_ids(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    return {sid for sid, _ in extract_blocks(path.read_text(encoding="utf-8"))}


def main() -> int:
    ap = argparse.ArgumentParser()
    _ = ap.add_argument("note")
    _ = ap.add_argument("--into", required=True, choices=sorted(TARGETS))
    _ = ap.add_argument("--dry-run", action="store_true")
    _ = ap.add_argument("--allow-dupes", action="store_true",
                        help="import even if the note's IDs collide with existing ones")
    args = ap.parse_args()

    note = Path(cast(str, args.note))
    if not note.is_file():
        print(f"no such note: {note}", file=sys.stderr)
        return 1

    blocks = extract_blocks(note.read_text(encoding="utf-8"))
    if not blocks:
        print("no scenario blocks found; expected headings like '### MED-23. Title'",
              file=sys.stderr)
        return 1

    target = TARGETS[cast(str, args.into)]
    have = existing_ids(target)
    added: list[tuple[str, str]] = []
    skipped: list[str] = []

    for sid, block in blocks:
        problems_found = problems(block)
        if sid in have and not cast(bool, args.allow_dupes):
            skipped.append(f"{sid}: id already in {target.name}")
            continue
        if problems_found:
            skipped.append(f"{sid}: " + "; ".join(problems_found))
            continue
        added.append((sid, block))

    print(f"{note.name}: {len(blocks)} candidate(s), {len(added)} importable, "
          + f"{len(skipped)} rejected")
    for reason in skipped:
        print(f"  REJECT {reason}")

    if not added:
        return 1

    if cast(bool, args.dry_run):
        for sid, _ in added:
            print(f"  would import {sid}")
        return 0

    existing = target.read_text(encoding="utf-8").rstrip()
    header = "" if existing.endswith("---") else "\n\n---\n\n"
    payload = header + "\n\n".join(b for _s, b in added) + "\n"
    _ = target.write_text(existing + payload, encoding="utf-8")
    print(f"imported {', '.join(s for s, _ in added)} into {target.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())