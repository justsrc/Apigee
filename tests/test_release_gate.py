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
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from release_gate import (  # noqa: E402
    BLOCKED, DECLARED, EXECUTED, FAIL, NOT_QUALIFIED, PASS, PROVISIONAL, QUALIFIED,
    UNVERIFIED, Criterion, audit_manifest, decide, f6_status,
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
# The run auditor behind E5
# ---------------------------------------------------------------------------


def _run_record(tmp: Path, body: str) -> Path:
    p = tmp / "RUNS.md"
    p.write_text(body, encoding="utf-8")
    return p


@case("a-complete-ab-run-qualifies")
def _run_qualifies():
    import release_gate
    with tempfile.TemporaryDirectory() as d:
        p = _run_record(Path(d), (
            "## Run 9, 2026-01-01\n\n"
            "| Field | Value |\n| --- | --- |\n"
            "| Arms | A baseline, B assisted |\n"
            "| Turns released | Both |\n"
            "| Model | some/model-1 |\n"
            "| Protocol | protocol.md |\n"))
        runs = release_gate.audit_eval_runs(p)
        assert len(runs) == 1 and runs[0]["qualifies"], runs


@case("an-assisted-only-run-does-not-qualify")
def _run_one_arm():
    """Run 2's own wording is the trap: "1, assisted. **No baseline arm.**"

    The word "baseline" is present, in a negation. An auditor that tests for the substring
    reads that run as a completed A/B and the gate starts implying an evaluation exists.
    """
    import release_gate
    with tempfile.TemporaryDirectory() as d:
        p = _run_record(Path(d), (
            "## Run 2, 2026-10-13\n\n"
            "| Field | Value |\n| --- | --- |\n"
            "| Arms | 1, assisted. **No baseline arm.** |\n"
            "| Turns released | Both |\n"
            "| Model | some/model-1 |\n"
            "| Protocol | protocol.md |\n"))
        runs = release_gate.audit_eval_runs(p)
        assert len(runs) == 1, runs
        assert not runs[0]["qualifies"], runs
        assert runs[0]["missing"] == ["a baseline arm"], runs


@case("a-turn-one-run-does-not-qualify")
def _run_one_turn():
    import release_gate
    with tempfile.TemporaryDirectory() as d:
        p = _run_record(Path(d), (
            "## Run 1, 2026-10-11\n\n"
            "| Field | Value |\n| --- | --- |\n"
            "| Arms | A no skill, B with skill |\n"
            "| Turns released | **1 only.** Diagnostic evidence was never released. |\n"
            "| Model | Subagent via the harness. Exact model id not captured. |\n"))
        runs = release_gate.audit_eval_runs(p)
        assert not runs[0]["qualifies"], runs
        assert "both turns released" in runs[0]["missing"], runs
        assert "a captured model id" in runs[0]["missing"], runs


@case("a-plan-section-is-not-a-run")
def _run_plan_section():
    """RUNS.md carries "## Runs not yet performed". Counting it would invent a failed run."""
    import release_gate
    with tempfile.TemporaryDirectory() as d:
        p = _run_record(Path(d), "## Runs not yet performed\n\nNothing yet.\n")
        assert release_gate.audit_eval_runs(p) == [], p


@case("the-repository-runs-do-not-qualify")
def _run_real_record():
    """Whatever this repository records today, the honest state has to be visible."""
    import release_gate
    runs = release_gate.audit_eval_runs(
        Path(release_gate.__file__).resolve().parent.parent / "evaluation/results/RUNS.md")
    assert runs, "the run record is empty or unreadable"
    assert not any(r["qualifies"] for r in runs), \
        f"a recorded run now qualifies: {[r['name'] for r in runs if r['qualifies']]}"


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


@case("rubric-defines-a-verdict-threshold")
def _rubric_threshold():
    """A weighted total with no pass mark is not a measurement.

    Every one of the 103 scenario rubrics uses 0/2/4 anchors on a subset of the dimensions,
    with no stated normalisation and no stated pass mark. Two reviewers of the medium
    scenarios both reported the same thing independently: for any response that trips no
    critical failure, the verdict is undefined.
    """
    txt = (Path(__file__).resolve().parent.parent / "evaluation" / "rubric.md")
    assert txt.is_file(), "evaluation/rubric.md is missing"
    body = txt.read_text(encoding="utf-8")

    assert re.search(r"divided by \(4 x number of rows", body), \
        "the scenario-table normalisation rule is missing"
    for threshold in ("0.75", "0.50"):
        assert threshold in body, f"no {threshold} pass threshold in the rubric"
    assert re.search(r"not applicable|does not apply", body, re.I), \
        "the rubric does not say how to treat a dimension that does not apply"
    assert re.search(r"excluded from the denominator", body), \
        "an inapplicable dimension must be excluded from the denominator, not scored zero"
    assert re.search(r"never excluded", body), \
        "Recognition of missing information must be non-excludable; it is the dimension " \
        "that carries calibration, and excluding it is how a confident wrong answer scores"


@case("scenario-rubric-tables-are-scorable")
def _scenario_tables():
    """Every per-scenario rubric must have anchors on all its rows.

    A row with an empty anchor column cannot be scored, so the scenario's own denominator
    overstates what was measured.
    """
    root = Path(__file__).resolve().parent.parent
    bad, checked = [], 0
    for f in sorted((root / "scenarios").glob("*.md")):
        if f.name == "index.md":
            continue
        in_table = False
        rows = 0
        for line in f.read_text(errors="replace").splitlines():
            if line.startswith("#### Evaluation rubric"):
                in_table = True
                continue
            if in_table and line.startswith("####"):
                in_table = False
            if not in_table or not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 4 or set("".join(cells)) <= set("-: "):
                continue
            rows += 1
            checked += 1
            if len(cells) < 4 or not cells[2] or not cells[3]:
                bad.append(f"{f.name}: row with a missing 0 or 4 anchor: {cells[0][:40]}")
    assert not bad, "\n".join(bad[:8])
    assert checked >= 200, f"only {checked} rubric rows found; the sweep did not run"


@case("f6-passes-on-structural-plus-classifier")
def _f6_ok():
    v, _, _ = decide([crit("F6", f6_status("PASS", "PASS"))])
    assert v == QUALIFIED, v


@case("f6-fails-if-structural-fails")
def _f6_struct():
    assert f6_status("FAIL", "PASS") == FAIL, f6_status("FAIL", "PASS")


@case("f6-fails-if-classifier-fails")
def _f6_clf():
    assert f6_status("PASS", "FAIL") == FAIL, f6_status("PASS", "FAIL")


@case("f6-does-not-require-live-model-evidence")
def _f6_live():
    # The live tier is INCONCLUSIVE whenever a free provider quota runs out. That is not a
    # failure of the mechanism, so a live tier that never reached a model must not FAIL F6.
    # The criterion is about the mechanism; the unseen live result is disclosed in the
    # evidence detail and in evaluation/isolation-report.md instead.
    assert f6_status("PASS", "PASS") == PASS


@case("f6-evidence-never-claims-live-isolation-was-demonstrated")
def _f6_words():
    # F6's own wording is the claim a reader sees on the gate table. It must not suggest an
    # adversarial model was refused. These read the module source, so they only bite if the
    # wording is reintroduced; a copy of the string here would not.
    import inspect
    import release_gate as rg
    src = inspect.getsource(rg.main)
    for phrase in ("live isolation passes", "isolation demonstrated", "boundary held",
                   "no breach occurred", "blocked all eight"):
        assert phrase not in src.lower(), f"F6 wording overclaims: {phrase}"


@case("model-criteria-carry-the-live-isolation-limitation")
def _g_words():
    # E5, G1 and G2 tell a reader whether isolation was actually tested. If they pass
    # without that note, a run with no live-isolation evidence could be read as isolated.
    import inspect
    import release_gate as rg
    src = inspect.getsource(rg.main)
    assert "live isolation has not been demonstrated" in src.lower(), \
        "G1/G2 detail must carry the live-isolation limitation"


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
