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

The last thing it checks is the tree an evaluating model is allowed to see, which is the
only check that can find answer material one Read away. That check can fail to run, and when
it does the script reports INCOMPLETE and exits nonzero rather than PASS, because a check
that did not run has established nothing about the tree.

Usage:
    python3 tests/test_leakage.py
"""

from __future__ import annotations

import importlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import Protocol, cast

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))


class _MakePackets(Protocol):
    FILES: dict[str, Path]

    def blocks(self, path: Path) -> list[tuple[str, str]]: ...

    def headings_of(self, block: str) -> list[tuple[int, str, int]]: ...

    def section(
        self, block: str, wanted: str, headings: list[tuple[int, str, int]]
    ) -> str | None: ...


class _MakeEvalWorkspace(Protocol):
    def all_scenario_ids(self) -> list[str]: ...

    def build(self, out: Path, ids: list[str], with_corpus: bool, force: bool) -> int: ...

    def find_leaks(self, root: Path) -> list[str]: ...


mp = cast("_MakePackets", cast("object", importlib.import_module("make_packets")))

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

# Verdicts for the workspace half of the test. The third state exists because that half used
# to answer with a bool and returned True when tests/make_eval_workspace.py could not be
# imported. True is success, so deleting that one file turned the check off silently: the
# script printed RESULT: PASS, exited 0, and release_gate.py recorded E2 as PASS having
# verified nothing about agent-workspace isolation. Three states, so an unrunnable check can
# be told apart from a passing one.
WS_OK, WS_LEAK, WS_UNRUNNABLE = "OK", "LEAK", "UNRUNNABLE"


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", text.lower())).strip()


def sentences(text: str) -> list[str]:
    """Long sentences from a block, normalised, ignoring headings and short fragments."""
    out: list[str] = []
    for raw in re.split(r"(?<=[.!?])\s+", text):
        s = re.sub(r"[`*_#>|\[\]()-]", " ", raw)
        s = norm(s)
        if len(s.split()) >= 8:
            out.append(s)
    return out


def _sections(sid: str) -> dict[str, str]:
    """Map section name to section text for one scenario.

    This used to be `blocks = {s: b for s, b in _blocks(sid)}`, which looks right and is
    not: `make_packets.blocks()` yields (scenario_id, whole_block) pairs, so the dict was
    keyed by scenario ID and `blocks.get("ground-truth resolution")` was always the empty
    string. `sentences("")` returns nothing, so the loop never ran and the ground-truth and
    incorrect-answer comparisons below compared nothing against anything. The test printed
    "no ground truth leaks into any prompt packet" having checked no ground truth at all.

    The canary test caught real leakage end to end, so the headline result was not wrong.
    But the per-file check, which is the thing that would catch a leak in MED-13's
    particular ground truth, has been inert since it was written.
    """
    out: dict[str, str] = {}
    for _bsid, block in _blocks(sid):
        headings = mp.headings_of(block)
        for want in ("ground-truth resolution", "common incorrect answers",
                     "initial support ticket", "diagnostic evidence"):
            body = mp.section(block, want, headings)
            if body:
                out[want] = body
    return out


def _workspace_test() -> tuple[str, str]:
    """Build the tree an evaluating model is allowed to see, and look for answers in it.

    Everything above this function inspects one file at a time and asks whether its text is
    clean. That cannot answer the question a reader actually has, which is whether a model
    running in this repository could find the answer. The answer keys live in
    evaluation/packets/, the full scenario text including every ground truth lives in
    scenarios/, and scenarios/index.md maps each ID to its title.

    That last one is the interesting path. make_packets.py strips the scenario title from
    the prompt on purpose, because titles like "Root cause cannot be established" state the
    grading criterion. It then writes the scenario ID into the prompt as `# Support case
    MED-13`, and index.md turns that ID back into the title in a single lookup. Restoring a
    deliberately dropped title is the same leak the dropping was for.

    So build the workspace and assert the answers are not in it.

    Returns (verdict, detail), the verdict being one of WS_OK, WS_LEAK or WS_UNRUNNABLE. The
    verdict used to be a bool, which cannot express the third of those, so every way this
    check could fail to run returned success.
    """
    try:
        mew = cast("_MakeEvalWorkspace",
                   cast("object", importlib.import_module("make_eval_workspace")))
    except ImportError:
        # The wip branch's typing sweep replaced this fallback with a bare return, which
        # both dropped a retry that works and reinstated the old `True`, and True is
        # success. The fallback is kept: the import above is importlib, which needs the
        # module on sys.path, and this is what puts tests/ there.
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        try:
            import make_eval_workspace as mew
        except ImportError:
            return WS_UNRUNNABLE, ("UNRUNNABLE (tests/make_eval_workspace.py not "
                                    "importable, so the workspace was never built and "
                                    "nothing in it was checked)")

    ids = mew.all_scenario_ids()
    sample = ids[:: max(1, len(ids) // 12)][:12] or ids[:1]
    if not sample:
        # The empty build is clean by construction and would have read as a pass. A
        # workspace holding nothing is not evidence that a workspace holds no answers.
        return WS_UNRUNNABLE, ("UNRUNNABLE (no scenario IDs, so the workspace would have "
                                "been built empty and had nothing to hide)")
    with tempfile.TemporaryDirectory(prefix="apigee-leakws-") as d:
        out = Path(d) / "ws"
        rc = mew.build(out, sample, False, True)
        if rc == 2:                      # could not build; already reported
            return WS_UNRUNNABLE, "UNRUNNABLE (the workspace could not be built)"
        leaks = mew.find_leaks(out)
        if leaks:
            return WS_LEAK, f"LEAK, workspace contains: {', '.join(leaks[:3])}"

        # Belt and braces. The name patterns are the fast check; confirm directly that the
        # things that actually hold answers are absent.
        for sub in ("evaluation", "scenarios", "research"):
            if (out / sub).exists():
                return WS_LEAK, f"LEAK, workspace contains a {sub}/ directory"
        if list(out.rglob("*.key.md")):
            return WS_LEAK, "LEAK, workspace contains an answer key"

    return WS_OK, f"OK, {len(sample)} scenarios built with no answer material reachable"


def main() -> int:
    failures: list[str] = []
    incomplete: list[str] = []
    checked = 0

    packets = ROOT / "evaluation" / "packets"
    for path in sorted(packets.glob("*.prompt.md")):
        checked += 1
        sid = path.name.split(".")[0]
        text = path.read_text(encoding="utf-8")

        for sec in HELD_BACK:
            # Match the section as a heading, not as a substring. A prose sentence
            # containing the word "verification" or "references" is not a leak; the first
            # version of this test flagged "describe how you would verify it" and "The
            # user references a routine", which are the opposite of findings.
            if re.search(rf"^#{{1,6}}\s*{re.escape(sec)}\s*$", text, re.M | re.I):
                failures.append(f"{path.name}: contains held-back section heading "
                                + f"'{sec}'")

        blocks = _sections(sid)
        gt = blocks.get("ground-truth resolution", "")
        # No [:12] cap. The first version checked only the first twelve sentences, so the
        # tail of a long ground-truth section was never compared against anything. Nine
        # scenarios have more than twelve sentences.
        for s in sentences(gt):
            if s and s in norm(text):
                failures.append(f"{path.name}: contains ground-truth text: {s[:70]}...")
                break

        cia = blocks.get("common incorrect answers", "")
        for s in sentences(cia):
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
                                    + f"heading: {m.group(0)[:70]}")
                    break

            # The heading test above has a blind spot: a title pasted into the ticket as a
            # sentence produces no heading at all. That is the shape a real leak takes, since
            # the generator drops the title but nothing stops a future edit from inlining it
            # in a block quote. The one legitimate case is a title that IS the customer's own
            # text, which by definition appears in the scenario's Initial support ticket.
            # Anything else appearing in the body is a leak.
            ticket = norm(blocks.get("initial support ticket", ""))
            bare = norm(re.sub(r"^[A-Z]+-\d+\.?\s*", "", title)).strip("\"'“”` ")
            if bare and bare[:60] in norm(text) and bare[:60] not in ticket:
                failures.append(f"{path.name}: title text appears in the packet body but "
                                + f"not in the customer's ticket: {bare[:60]}...")

    # Deliberate leak: inject a canary into held-back material and prove it does not escape.
    leaked_ok = _canary_test()

    # The packet text being clean is necessary and not sufficient. The answer keys, the
    # scenario files and the ID-to-title index all sit under the repository root, one Read
    # away from a model whose working directory is that root. Build the tree the agent is
    # actually allowed to see and assert the answer material is not in it.
    ws_state, ws_detail = _workspace_test()

    print(f"checked {checked} prompt packets across {checked // 2} scenarios")
    for f in failures:
        print(f"  LEAK: {f}")
    if not failures:
        print("  no ground truth, incorrect answers, titles or held-back sections found "
              + "in any prompt")
    print()
    print(f"deliberate canary leak test: {'held back correctly' if leaked_ok else 'LEAKED'}")
    if not leaked_ok:
        failures.append("canary phrase leaked into a prompt packet")
    print()
    print(f"agent workspace isolation: {ws_detail}")
    if ws_state == WS_LEAK:
        failures.append("the agent workspace contains answer material")
    elif ws_state == WS_UNRUNNABLE:
        # Kept apart from failures: a leak is a finding and a non-run is not, and the
        # verdict line below says which one happened. Neither is a pass.
        incomplete.append(f"agent workspace isolation did not run: {ws_detail}")

    if incomplete:
        print(f"\nRESULT: INCOMPLETE, {len(incomplete)} check(s) could not run: "
              f"{'; '.join(incomplete)}")
        print("A check that did not run is not a check that passed.")
    if failures:
        print(f"\nRESULT: FAIL, {len(failures)} leakage finding(s)")
    if incomplete or failures:
        return 1
    print("\nRESULT: PASS, no ground truth leaks into any prompt packet")
    return 0


def _blocks(sid: str) -> Iterator[tuple[str, str]]:
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
        _ = shutil.copytree(ROOT, sandbox,
                            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
        sc = sandbox / "scenarios" / "easy.md"
        text = sc.read_text(encoding="utf-8")
        anchor = "#### Ground-truth resolution\n"
        if anchor not in text:
            print("  WARNING: no ground-truth heading found, canary test skipped",
                  file=sys.stderr)
            return False
        text = text.replace(anchor, anchor + f"\nMARKER_SENTENCE {MARKER}.\n", 1)
        _ = sc.write_text(text, encoding="utf-8")

        env = {"PYTHONPATH": str(sandbox / "tests")}
        _ = subprocess.run(
            [sys.executable, str(sandbox / "tests" / "make_packets.py"),
             "--all", "--turn", "1"],
            capture_output=True, text=True, env={**dict(os.environ), **env},
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
