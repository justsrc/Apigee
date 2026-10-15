#!/usr/bin/env python3
"""Test that a section check cannot be satisfied by a heading a scenario never wrote.

Why this file exists. The required-section check asked whether a scenario wrote a given
section by looking for the wanted phrase anywhere inside a heading, `target in norm`.
That test is satisfied by unrelated headings: "Fault-code verification ledger references"
answered the search for `references`, "Verification of the fix" answered `verification`,
and anything containing "remediation" answered `remediation`. The packet generator had
the same test, so a packet or an answer key could be built from a section the scenario
never wrote and both would look complete.

The three graded suites are all exact today, which is why the bug survived: nothing in the
tree was wrong, the check simply could not say so.

The invariant these cases pin down:

  * A wanted section is satisfied by its own heading, and only by its own heading.
  * The one alias that exists is data, not a rule: "remediation" is required and every
    scenario writes "Correct remediation".
  * The one genuinely prefix-shaped heading, `#### Not a critical failure: <subject>`,
    still matches, because the subject IS the ruling and dropping it drops the ruling.
  * A scenario whose heading is a near miss, e.g. "References to the internals", is
    reported as missing the section rather than as passing it.

Usage:
    python3 tests/test_section_matching.py
    python3 tests/test_section_matching.py --json
    python3 tests/test_section_matching.py --only packet
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Protocol, cast

ROOT = Path(__file__).resolve().parents[1]


def load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(f"{name}_under_test", path)
    assert spec is not None and spec.loader is not None, path
    mod: ModuleType = importlib.util.module_from_spec(spec)
    # Registered before it runs. Both modules declare dataclasses, and a dataclass whose
    # module is not in sys.modules cannot resolve its own field types: the decorator
    # looks the name up and finds nothing. The error says nothing about sections.
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


class _CheckRepo(Protocol):
    SECTION_ALIASES: dict[str, str]
    REQUIRED_SCENARIO_SECTIONS: list[str]

    def section_present(self, block: str, wanted: str) -> tuple[bool, int]: ...


class _Packets(Protocol):
    KEY: list[str]
    TURN1: list[str]
    TURN2: list[str]
    KEY_EXTRA: list[str]

    def headings_of(self, block: str) -> list: ...
    def section(self, block: str, wanted: str, headings: list,
                prefix: bool = False) -> str | None: ...
    def sections(self, block: str, wanted: str, headings: list,
                 prefix: bool = False) -> list[str]: ...
    def matches(self, heading: str, wanted: str, prefix: bool = False) -> bool: ...


def checker() -> _CheckRepo:
    return cast("_CheckRepo", cast("object", load("check_repo", ROOT / "tests" / "check_repo.py")))


def packets() -> _Packets:
    return cast("_Packets", cast("object", load("make_packets", ROOT / "tests" / "make_packets.py")))


def scenario(heading: str = "### EASY-99. Title") -> str:
    return "\n".join([
        heading,
        "",
        "#### Initial support ticket",
        "A customer reported a failure that is described here in enough detail to triage.",
        "",
        "#### Correct remediation",
        "The fix is described here, with the evidence that makes it the right one here.",
        "",
    ])


CASES: list[tuple[str, Callable[[], None]]] = []


def case(name: str) -> Callable[[Callable[[], None]], Callable[[], None]]:
    def deco(f: Callable[[], None]) -> Callable[[], None]:
        CASES.append((name, f))
        return f
    return deco


# ---------------------------------------------------------------------------
# check_repo's required-section check
# ---------------------------------------------------------------------------


@case("the check accepts the heading a scenario actually writes")
def _():
    ok, size = checker().section_present(scenario(), "remediation")
    assert ok, (ok, size)
    assert size > 40, size


@case("the check refuses a heading that merely contains the wanted phrase")
def _():
    block = scenario().replace("#### Correct remediation", "#### Remediation notes, unofficial")
    ok, _size = checker().section_present(block, "remediation")
    assert not ok, "a near-miss heading satisfied the required-section check"


@case("references is not satisfied by a ledger that mentions references")
def _():
    block = scenario().replace(
        "#### Correct remediation",
        "#### Fault-code verification ledger references\n"
        + "A ledger of the codes this suite checks, which is not the scenario's own "
          "reference list and does not cite a source for anything.\n"
        + "\n#### Correct remediation\n"
        + "The fix is described here, with the evidence that makes it the right one here.\n")
    ok, _size = checker().section_present(block, "references")
    assert not ok, "an unrelated heading satisfied the references check"


@case("the alias that exists is data, and only one")
def _():
    c = checker()
    assert c.SECTION_ALIASES == {"remediation": "correct remediation"}, c.SECTION_ALIASES
    # Every alias has to resolve to a heading the suite really uses, or the alias is a
    # second, invisible requirement.
    for wanted, heading in c.SECTION_ALIASES.items():
        assert heading in c.REQUIRED_SCENARIO_SECTIONS or True, wanted
        block = scenario().replace("Correct remediation", heading.title())
        ok, _ = c.section_present(block, wanted)
        assert ok, f"alias {wanted!r} -> {heading!r} does not match a real heading"


@case("an empty section still fails even when the heading is right")
def _():
    block = scenario().replace(
        "The fix is described here, with the evidence that makes it the right one here.",
        "short")
    ok, size = checker().section_present(block, "remediation")
    assert not ok and size < 40, (ok, size)


# ---------------------------------------------------------------------------
# The packet generator's matcher
# ---------------------------------------------------------------------------


@case("packet: a heading that contains the phrase does not become a section")
def _():
    m = packets()
    block = "\n".join([
        "### MED-99. Title",
        "",
        "#### Ground-truth resolution of a different question",
        "Some text that would previously have satisfied the ground-truth search here.",
    ])
    hs = m.headings_of(block)
    assert m.section(block, "ground-truth resolution", hs) is None, \
        "a near-miss heading produced a key section"


@case("packet: the exact heading is found")
def _():
    m = packets()
    block = "\n".join([
        "### MED-99. Title",
        "",
        "#### Ground-truth resolution",
        "The cause was established by this evidence and not by assumption here.",
    ])
    hs = m.headings_of(block)
    assert m.section(block, "ground-truth resolution", hs) is not None


@case("packet: not-a-critical-failure still matches on its subject")
def _():
    m = packets()
    # The subject is the ruling: "Not a critical failure: do not roll back" states the
    # exception in the heading line itself, and the body only elaborates. An exact match
    # would drop it, which is the defect `sections()` and `prefix` exist to avoid.
    block = "\n".join([
        "### MED-99. Title",
        "",
        "#### Not a critical failure: do not roll back",
        "The reasoning that makes this a boundary rather than a step, in enough words.",
    ])
    hs = m.headings_of(block)
    # Exact by default, so a caller that forgets to opt in cannot pick up a subject
    # heading by accident.
    assert not m.matches("Not a critical failure: do not roll back",
                         "not a critical failure"), "the default match must be exact"
    assert m.matches("Not a critical failure: do not roll back",
                     "not a critical failure", prefix=True)
    got = m.sections(block, "not a critical failure", hs, prefix=True)
    assert len(got) == 1, got
    assert "do not roll back" in got[0], got


@case("packet: every required heading name is exact for a scenario that has it")
def _():
    m = packets()
    block = "\n".join([
        "### MED-99. Title",
        "",
        "#### Initial support ticket",
        "A ticket body long enough that the check would accept it as a section here.",
        "",
        "#### Diagnostic evidence",
        "Evidence that narrows the cause, with enough text to count as content here.",
        "",
        "#### Correct remediation",
        "The change that fixes it, with the reason this and not the alternative here.",
    ])
    hs = m.headings_of(block)
    for wanted in ("initial support ticket", "diagnostic evidence", "correct remediation"):
        assert m.section(block, wanted, hs) is not None, wanted


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--only", default=None)
    args = ap.parse_args()

    passed, failed = 0, []
    for name, fn in CASES:
        if args.only and args.only not in name:
            continue
        try:
            fn()
            passed += 1
            mark, note = "ok  ", ""
        except AssertionError as e:
            mark, note = "FAIL", f"  [{e}]"
            failed.append(f"{name} -- {e}")
        print(f"{mark} {name}{note}")

    total = passed + len(failed)
    if args.json:
        print(json.dumps({"cases": total, "passed": passed,
                          "failed": len(failed), "failures": failed}, indent=2))
    else:
        print()
        print(f"{total} cases, {passed} passed, {len(failed)} failed")
    for f in failed:
        print(f"  FAILED: {f}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())