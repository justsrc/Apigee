#!/usr/bin/env python3
"""Test the release gate's verdict logic and the checks it previously asserted in prose.

Why this file exists. The project's own history is a list of checkers that reported success
while checking nothing, and `tests/fault_probe.py` exists to catch that class of defect in
`tests/check_repo.py`. The release gate was never probed at all, and it had three of the same
defect:

  * `qualified = not failed and not blocked` treated UNVERIFIED as harmless, so a gate with
    three unresolved mandatory criteria printed VERDICT: QUALIFIED.
  * C2 read `PASS if unresolved else PASS`, which returns PASS for every possible value of
    the quantity it names.
  * C4 mapped `check_urls.py`'s exit 2 - the code it uses for "I could not audit anything" -
    to PASS, because the test was `FAIL if code == 1 else PASS`.

Each of those is now a test below. The tests are written so that reintroducing the old
behaviour fails them.

Usage:
    python3 tests/test_release_gate.py
    python3 tests/test_release_gate.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from release_gate import (  # noqa: E402
    BLOCKED, DECLARED, EXECUTED, FAIL, NOT_QUALIFIED, PASS, PROVISIONAL, QUALIFIED,
    UNVERIFIED, Criterion, audit_manifest, decide,
)

CASES: list[dict] = []


def case(name: str, fn=None) -> None:
    """Register a case. Usable as @case("name") or @case("name", fn)."""
    def deco(f):
        CASES.append({"name": name, "fn": f})
        return f
    if fn is not None:
        deco(fn)
    else:
        return deco


def crit(cid: str, status: str, mandatory: bool = True) -> Criterion:
    return Criterion(id=cid, category="test", requirement=cid, status=status,
                     mandatory=mandatory)


# ---------------------------------------------------------------------------
# Verdict semantics
# ---------------------------------------------------------------------------


@case("all-mandatory-pass-is-qualified")
def _qualified():
    v, code, _ = decide([crit("A", PASS), crit("B", PASS), crit("C", PASS)])
    assert v == QUALIFIED, v
    assert code == 0, code


@case("mandatory-fail-is-not-qualified")
def _failed():
    v, code, ctrl = decide([crit("A", PASS), crit("B", FAIL), crit("C", PASS)])
    assert v == NOT_QUALIFIED, v
    assert code == 1, code
    assert "B" in ctrl, ctrl


@case("blocked-is-not-qualified")
def _blocked():
    v, code, ctrl = decide([crit("A", PASS), crit("C4", BLOCKED)])
    assert v == NOT_QUALIFIED, v
    assert code == 1, code
    assert "C4" in ctrl, ctrl


@case("unverified-mandatory-is-provisional-never-qualified")
def _provisional():
    v, code, ctrl = decide([crit("A", PASS), crit("E5", UNVERIFIED), crit("G1", UNVERIFIED)])
    assert v == PROVISIONAL, v
    assert code == 1, code
    assert sorted(ctrl) == ["E5", "G1"], ctrl


@case("regression-unverified-does-not-yield-qualified")
def _regression():
    """The defect this file was written for.

    `qualified = not failed and not blocked` returned QUALIFIED for the exact criterion set
    the project has always shipped with: 27 PASS and 3 UNVERIFIED. If someone restores that
    rule, this case fails.
    """
    criteria = [crit(f"A{i}", PASS) for i in range(27)]
    criteria += [crit("E5", UNVERIFIED), crit("G1", UNVERIFIED), crit("G2", UNVERIFIED)]
    v, code, _ = decide(criteria)
    assert v != QUALIFIED, f"27 PASS + 3 UNVERIFIED produced {v}; that is the old bug"
    assert v == PROVISIONAL, v
    assert code == 1, code


@case("unverified-non-mandatory-does-not-block")
def _non_mandatory():
    v, code, _ = decide([crit("A", PASS), crit("Z", UNVERIFIED, mandatory=False)])
    assert v == QUALIFIED, v
    assert code == 0, code


@case("non-mandatory-fail-does-not-block")
def _non_mandatory_fail():
    """A non-mandatory criterion is an explicit, justified exemption, not a silent one."""
    v, _, _ = decide([crit("A", PASS), crit("Z", FAIL, mandatory=False)])
    assert v == QUALIFIED, v


@case("failure-outranks-blocked-and-unverified")
def _precedence():
    v, _, ctrl = decide([crit("A", FAIL), crit("B", BLOCKED), crit("C", UNVERIFIED)])
    assert v == NOT_QUALIFIED, v
    assert sorted(ctrl) == ["A", "B"], ctrl


@case("empty-criterion-list-is-not-qualified")
def _empty():
    """A gate that checked nothing must not certify. Zero criteria is not a clean sweep."""
    v, code, _ = decide([])
    assert v == PROVISIONAL, v
    assert code == 1, code


# ---------------------------------------------------------------------------
# The manifest auditor behind C1 and C2
# ---------------------------------------------------------------------------


def _write_manifest(tmp: Path, rows: list[str], pages: list[str]) -> tuple[Path, Path]:
    man = tmp / "MANIFEST.tsv"
    man.write_text("# header\n" + "".join(r + "\n" for r in rows), encoding="utf-8")
    pdir = tmp / "pages"
    pdir.mkdir()
    for p in pages:
        (pdir / f"{p}.txt").write_text("body", encoding="utf-8")
    return man, pdir


@case("manifest-clean-passes")
def _manifest_clean():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        man, pdir = _write_manifest(
            tmp,
            ["good\thttps://example.test/a\trecorded",
             "lost\t\tUNRESOLVED;real path not confirmed"],
            ["good", "lost"])
        r = audit_manifest(man, pdir)
        assert not r["bad_unresolved"], r
        assert not r["orphans"], r
        assert r["prov"]["UNRESOLVED"] == 1, r


@case("manifest-unresolved-with-a-url-is-rejected")
def _manifest_guessed():
    """The C2 defect. A page called UNRESOLVED that nonetheless carries a URL is a guess."""
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        man, pdir = _write_manifest(
            tmp, ["lost\thttps://example.test/probably\tUNRESOLVED"], ["lost"])
        r = audit_manifest(man, pdir)
        assert r["bad_unresolved"] == ["lost"], r


@case("manifest-unresolved-without-a-reason-is-rejected")
def _manifest_noreason():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        man, pdir = _write_manifest(tmp, ["lost\t\tUNRESOLVED"], ["lost"])
        r = audit_manifest(man, pdir)
        assert r["bad_unresolved"] == ["lost"], r


@case("manifest-unresolved-with-empty-reason-is-rejected")
def _manifest_emptyreason():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        man, pdir = _write_manifest(tmp, ["lost\t\tUNRESOLVED;"], ["lost"])
        r = audit_manifest(man, pdir)
        assert r["bad_unresolved"] == ["lost"], r


@case("manifest-page-without-a-row-is-rejected")
def _manifest_orphan():
    """C1 is about coverage of the corpus, not about the manifest describing itself."""
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        man, pdir = _write_manifest(tmp, ["known\thttps://example.test/a\trecorded"],
                                    ["known", "unlisted"])
        r = audit_manifest(man, pdir)
        assert r["orphans"] == ["unlisted"], r


@case("manifest-empty-provenance-is-rejected")
def _manifest_undeclared():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        man, pdir = _write_manifest(tmp, ["known\thttps://example.test/a\t"], ["known"])
        r = audit_manifest(man, pdir)
        assert r["undeclared"] == ["known"], r


@case("manifest-missing-entirely-is-rejected")
def _manifest_absent():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        pdir = tmp / "pages"
        pdir.mkdir()
        r = audit_manifest(tmp / "nope.tsv", pdir)
        assert r["prov"] == {}, r
        assert not r["orphans"], "a missing manifest must not silently look clean"


# ---------------------------------------------------------------------------
# The real corpus and the real criterion set
# ---------------------------------------------------------------------------


@case("real-manifest-passes-c1-and-c2")
def _real_manifest():
    root = Path(__file__).resolve().parent.parent
    r = audit_manifest(root / "research/pages/MANIFEST.tsv", root / "research/pages")
    assert not r["bad_unresolved"], f"UNRESOLVED rows that guess: {r['bad_unresolved']}"
    assert not r["orphans"], f"cached pages with no provenance row: {r['orphans']}"
    assert not r["undeclared"], f"rows with empty provenance: {r['undeclared']}"
    assert not r["malformed"], f"malformed rows: {r['malformed']}"


@case("model-evaluation-criteria-are-mandatory-and-unverified")
def _model_criteria():
    """E5, G1 and G2 must never be quietly demoted to non-mandatory.

    Demoting them would make the gate return QUALIFIED without changing a single check,
    which is the same false qualification this gate is being fixed for.
    """
    import release_gate
    src = Path(release_gate.__file__).read_text(encoding="utf-8")
    lines = src.splitlines()
    for cid in ("E5", "G1", "G2"):
        idx = next((i for i, ln in enumerate(lines)
                    if f'"{cid}"' in ln and "rep.add" in ln), None)
        assert idx is not None, f"{cid} is not registered with the gate at all"
        # The status is on the rep.add line or one of the next few; the call is short.
        window = "\n".join(lines[idx:idx + 6])
        assert "UNVERIFIED" in window, \
            f"{cid} is no longer UNVERIFIED:\n{window}"
        assert "mandatory=False" not in window, \
            f"{cid} was quietly made non-mandatory, which would make the gate return\n" \
            f"QUALIFIED without a single check changing:\n{window}"


@case("declared-is-not-the-default-evidence-kind")
def _declared_inventory():
    """DECLARED means 'no check ran here'. It must be a deliberate annotation.

    If DECLARED were the default, a criterion added later without thinking would silently
    become an assertion rather than a check, and the gate would keep printing PASS.
    """
    import release_gate
    rep = release_gate.Report(generated="test")
    rep.add("X", "c", "explicit", PASS, kind=DECLARED)
    rep.add("Y", "c", "default", PASS)
    assert rep.criteria[0].evidence_kind == DECLARED
    assert rep.criteria[1].evidence_kind == EXECUTED, \
        "the default must be EXECUTED, not DECLARED"
    assert rep.evidence_counts() == {DECLARED: 1, EXECUTED: 1}, rep.evidence_counts()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--only", default=None, help="substring filter on case name")
    args = ap.parse_args()

    results = []
    for c in CASES:
        if args.only and args.only not in c["name"]:
            continue
        try:
            c["fn"]()
            results.append({"name": c["name"], "ok": True, "note": ""})
        except AssertionError as e:
            results.append({"name": c["name"], "ok": False, "note": str(e) or "assertion failed"})
        except Exception as e:  # noqa: BLE001 - a crash is a failure, not an error to hide
            results.append({"name": c["name"], "ok": False,
                            "note": f"{type(e).__name__}: {e}"})

    failed = [r for r in results if not r["ok"]]
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"{'ok  ' if r['ok'] else 'FAIL'} {r['name']}"
                  + (f"\n       {r['note']}" if r["note"] else ""))
        print()
        print(f"{len(results)} cases, {len(results) - len(failed)} passed, {len(failed)} failed")
        for r in failed:
            print(f"  FAILED: {r['name']} -- {r['note']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
