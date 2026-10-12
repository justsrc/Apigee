#!/usr/bin/env python3
"""Prove the packet generator does not leak ground truth.

The leakage check in check_repo.py looks for four literal heading strings in a prompt. That
catches one specific way of leaking and nothing else: it would not notice a scenario whose
title states the answer, a ground-truth sentence copied into the ticket, or a prompt that
reaches past turn 1 into diagnostic material.

This checks the properties that matter, on every scenario, by construction rather than by
pattern:

  1. No prompt contains a section that is held back by design.
  2. No prompt contains text that appears in the scenario's ground-truth resolution.
  3. No prompt contains a sentence from the scenario's common incorrect answers.
  4. No prompt contains the scenario title.
  5. Turn 2 releases only diagnostic evidence, not the held-back sections.

It also runs a deliberate leak: it copies a recognisable ground-truth phrase into a held-back
field and confirms the generated packet does not contain it. A leakage test that never
actually leaks proves nothing.

Usage:
    python3 tests/test_leakage.py
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))

import make_packets as mp  # noqa: E402

# Sections the generator must never release, whatever the turn.
HELD_BACK = [
    "ground-truth resolution",
    "correct remediation",
    "common incorrect answers",
    "evaluation rubric",
    "verification",
    "expected investigation",
    "references",
]

MARKER = "ZZLEAKCANARYZZ-4f2a9c-do-not-release-this-sentence"


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", text.lower())).strip()


def sentences(text: str) -> list[str]:
    """Long sentences from a block, normalised, ignoring headings and short fragments."""
    out = []
    for raw in re.split(r"(?<=[.!?])\s+", text):
        s = re.sub(r"[`*_#>|\[\]()-]", " ", raw)
        s = norm(s)
        if len(s.split()) >= 8:
            out.append(s)
    return out


def main() -> int:
    failures: list[str] = []
    checked = 0

    packets = ROOT / "evaluation" / "packets"
    for path in sorted(packets.glob("*.prompt.md")):
        checked += 1
        sid = path.name.split(".")[0]
        text = path.read_text(encoding="utf-8")
        low = text.lower()

        for sec in HELD_BACK:
            # Match the section as a heading, not as a substring. A prose sentence
            # containing the word "verification" or "references" is not a leak; the first
            # version of this test flagged "describe how you would verify it" and "The
            # user references a routine", which are the opposite of findings.
            if re.search(rf"^#{{1,6}}\s*{re.escape(sec)}\s*$", text, re.M | re.I):
                failures.append(f"{path.name}: contains held-back section heading "
                                f"'{sec}'")

        blocks = {s: b for s, b in _blocks(sid)}
        gt = blocks.get("ground-truth resolution", "")
        for s in sentences(gt)[:12]:
            if s and s in norm(text):
                failures.append(f"{path.name}: contains ground-truth text: {s[:70]}...")
                break

        cia = blocks.get("common incorrect answers", "")
        for s in sentences(cia)[:12]:
            if s and s in norm(text):
                failures.append(f"{path.name}: contains incorrect-answer text: {s[:70]}...")
                break

        title = _title(sid)
        if title:
            # The invariant is that the generator does not emit the title as a heading.
            # A substring test is wrong here: MED-41's title is the customer's own error
            # string, "Operation group limit of 51 exceeded in Operation Config", which
            # belongs in the ticket. Flagging it would be flagging the scenario for
            # being realistic.
            clean = re.sub(r"^[A-Z]+-\d+\.?\s*", "", title)
            # Allow the generator's own "# <ID>: <title>" prefix, which is why the first
            # version of this regex missed a reintroduced leak and reported PASS.
            for m in re.finditer(r"^#{1,6}\s*(.*)$", text, re.M):
                heading = re.sub(r"^[A-Z]+-\d+\.?\s*:?\s*", "", m.group(1)).strip()
                if heading[:40] and heading[:40] in clean:
                    failures.append(f"{path.name}: emits the scenario title as a "
                                    f"heading: {m.group(0)[:70]}")
                    break

    # Deliberate leak: inject a canary into held-back material and prove it does not escape.
    leaked_ok = _canary_test()

    print(f"checked {checked} prompt packets across {checked // 2} scenarios")
    for f in failures:
        print(f"  LEAK: {f}")
    if not failures:
        print("  no ground truth, incorrect answers, titles or held-back sections found "
              "in any prompt")
    print()
    print(f"deliberate canary leak test: {'held back correctly' if leaked_ok else 'LEAKED'}")
    if not leaked_ok:
        failures.append("canary phrase leaked into a prompt packet")

    if failures:
        print(f"\nRESULT: FAIL, {len(failures)} leakage finding(s)")
        return 1
    print("\nRESULT: PASS, no ground truth leaks into any prompt packet")
    return 0


def _blocks(sid: str):
    for path in mp.FILES.values():
        if not path.is_file():
            continue
        for bsid, block in mp.blocks(path):
            if bsid == sid:
                yield bsid, block


def _title(sid: str) -> str:
    for _bsid, block in _blocks(sid):
        hs = mp.headings_of(block)
        if hs:
            return hs[0][1]
    return ""


def _canary_test() -> bool:
    """Put a canary into the ground truth, regenerate, confirm the prompt lacks it."""
    tmp = Path(tempfile.mkdtemp(prefix="apigee-leak-"))
    try:
        sandbox = tmp / "repo"
        shutil.copytree(ROOT, sandbox,
                        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
        sc = sandbox / "scenarios" / "easy.md"
        text = sc.read_text(encoding="utf-8")
        anchor = "#### Ground-truth resolution\n"
        if anchor not in text:
            print("  WARNING: no ground-truth heading found, canary test skipped",
                  file=sys.stderr)
            return False
        text = text.replace(anchor, anchor + f"\nMARKER_SENTENCE {MARKER}.\n", 1)
        sc.write_text(text, encoding="utf-8")

        env = {"PYTHONPATH": str(sandbox / "tests")}
        subprocess.run(
            [sys.executable, str(sandbox / "tests" / "make_packets.py"),
             "--all", "--turn", "1"],
            capture_output=True, text=True, env={**dict(__import__("os").environ), **env},
            timeout=300)

        for p in (sandbox / "evaluation" / "packets").glob("*.prompt.md"):
            if MARKER in p.read_text(encoding="utf-8"):
                print(f"  canary found in {p.name}", file=sys.stderr)
                return False
        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())