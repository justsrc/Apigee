#!/usr/bin/env python3
"""Test that a score cannot be recorded for a turn that was never answered.

Why this file exists. `grade_run.py --run` took the grader's JSON at face value. It never
read the manifest, so any scenario named in a scores file was graded and written out, whether
or not a turn had run. Driven against run 3's own manifest, where all 103 scenarios are
NOT_STARTED and no answer file exists on disk, MED-13 came out as:

    {"scenario": "MED-13", "normalized_score": 1.0, "verdict": "PASS"}

Nothing had been generated. The score was arithmetic on numbers the caller supplied, and
the only thing that made it look like a result was that it landed in the same directory as
real grades.

That matters because of what the file is for. `6600a19` stopped the generation harness from
writing a provider error into an answer file, and its message says a false success "hands an
error string to a rubric and produces a score for a turn the model never answered". This is
the other end of that sentence. The generation path was hardened and the component that
actually writes the score was not, so the outcome the earlier commit was written to prevent
was still reachable from the grading side, with no generation at all.

A second defect is here too. A computed score that came out `None` was coerced to `FAIL`
whenever the grader had supplied any anchors, so a typo in one anchor put a model failure in
the verdict counts. PROTOCOL.md says the opposite in one line: "An invalid grading reference
is never counted as a model failure."

The invariant these cases pin down:

  * A scenario may only be graded when the manifest marks it AWAITING_GRADE and both turn
    answer files exist. Otherwise it is refused, no grade file is written, and the run
    exits nonzero so the rest of the summary cannot be read as complete.
  * A refusal names the reason and names the scenario.
  * An input error is UNSCORABLE with a reason, never FAIL.
  * The ordinary path still works. A scenario that genuinely ran and was genuinely scored
    is graded, and a critical failure still fails it whatever the score.

Usage:
    python3 tests/test_grading_integrity.py
    python3 tests/test_grading_integrity.py --json
    python3 tests/test_grading_integrity.py --only refused
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRADER = ROOT / "evaluation" / "results" / "run-3" / "grade_run.py"

# A real scenario with a real seven-row rubric table in its answer key.
SID = "EASY-01"


def load_grader() -> object:
    """grade_run.py by path, as a module, so its paths can be pointed at a scratch run."""
    spec = importlib.util.spec_from_file_location("grade_run_under_test", GRADER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


class Sandbox:
    """A scratch run directory with a manifest and a key, and nothing else.

    The real answer keys are read from evaluation/packets, so the rubric table the grader
    scores against is the one that ships. The manifest and the raw/ answers are built here,
    because they are the things under test.
    """

    def __init__(self) -> None:
        self.dir = Path(tempfile.mkdtemp(prefix="apigee-grade-"))
        self.run = self.dir / "run-3"
        (self.run / "raw").mkdir(parents=True)
        self.packets = ROOT / "evaluation" / "packets"
        self.manifest_path = self.run / "manifest.json"
        self.manifest = {"model": "fake/model", "scenarios": {}}

    def set_status(self, sid: str, status: str) -> None:
        self.manifest["scenarios"][sid] = {"status": status, "turns": {}, "attempts": 0}
        self.write_manifest()

    def write_manifest(self) -> None:
        self.manifest_path.write_text(json.dumps(self.manifest, indent=2), encoding="utf-8")

    def write_answers(self, sid: str, turn1: str = "t1", turn2: str = "t2",
                      record_digests: bool = False) -> None:
        """Write both answer files, optionally the way run_generation.py records them.

        `record_digests` puts a `response_sha256` per turn into the manifest, which is
        what the harness writes when a turn completes and what the grader now compares
        the bytes on disk against. Left off it is an older manifest, and an older manifest
        must still be gradeable rather than refused for a field it predates.
        """
        turns: dict[str, dict] = {}
        for n, body in ((1, turn1), (2, turn2)):
            p = self.run / "raw" / f"{sid}.turn{n}.md"
            p.write_text(body, encoding="utf-8")
            if record_digests:
                turns[f"turn{n}"] = {
                    "response_sha256": hashlib.sha256(body.encode()).hexdigest(),
                    "session_id": "sess-1", "attempts": 1, "chars": len(body),
                    "raw": f"raw/{sid}.turn{n}.attempt1.jsonl",
                }
        if record_digests:
            self.manifest["scenarios"][sid]["turns"] = turns  # type: ignore[index]
            self.write_manifest()

    def seed_stale_grade(self, sid: str) -> Path:
        """A grade file from an earlier run of the same scenario."""
        d = self.run / "grades" / "primary"
        d.mkdir(parents=True, exist_ok=True)
        p = d / f"{sid}.json"
        p.write_text(json.dumps({"scenario": sid, "verdict": "PASS",
                                 "normalized_score": 1.0, "grader": "primary"}) + "\n",
                     encoding="utf-8")
        return p

    def run_grade(self, scores: dict, grader: str = "primary") -> subprocess.CompletedProcess:
        """Run the real grade_run.py in a subprocess, against this scratch run.

        A subprocess rather than an in-process call, so the module's ROOT-derived paths are
        replaced by editing a copy of the file rather than by mutating shared state. The
        grade_run.py source is copied with RUN, PK and MANIFEST repointed, which is the
        smallest change that makes the real file drive the real code against a fixture.
        """
        target = self.dir / "grade_run.py"
        text = GRADER.read_text(encoding="utf-8")
        text = text.replace('ROOT = Path(__file__).resolve().parents[3]',
                            f'ROOT = Path({str(self.dir / "fake-root")!r})')
        text = text.replace('RUN = ROOT / "evaluation" / "results" / "run-3"',
                            f'RUN = Path({str(self.run)!r})')
        text = text.replace('PK = ROOT / "evaluation" / "packets"',
                            f'PK = Path({str(self.packets)!r})')
        text = text.replace('MANIFEST = RUN / "manifest.json"',
                            f'MANIFEST = Path({str(self.manifest_path)!r})')
        target.write_text(text, encoding="utf-8")

        scores_path = self.dir / "scores.json"
        scores_path.write_text(json.dumps(scores), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(target), "--run", "--grader", grader,
             "--scores", str(scores_path)],
            capture_output=True, text=True, timeout=120,
        )

    def grade_file(self, sid: str) -> dict | None:
        p = self.run / "grades" / "primary" / f"{sid}.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None

    def summary(self) -> dict:
        p = self.run / "grades" / "primary" / "_summary.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def anchors_from_key(mod: object, sid: str, value: int) -> dict:
    """A complete set of anchors for the scenario's real rubric table."""
    key = (ROOT / "evaluation" / "packets" / f"{sid}.key.md").read_text(encoding="utf-8")
    rows = mod.rubric_rows(key)  # type: ignore[attr-defined]
    assert rows > 0, f"{sid} has no rubric table to score against"
    return {f"dimension {i}": value for i in range(rows)}


CASES: list[tuple[str, Callable[[], None]]] = []


def case(name: str) -> Callable[[Callable[[], None]], Callable[[], None]]:
    def deco(f: Callable[[], None]) -> Callable[[], None]:
        CASES.append((name, f))
        return f
    return deco


# ---------------------------------------------------------------------------
# The regression: a scenario that never ran cannot be scored.
# ---------------------------------------------------------------------------


@case("a scenario the manifest says never started is refused, not scored")
def _():
    mod = load_grader()
    with tempfile.TemporaryDirectory(prefix="apigee-grade-") as d:
        sb = Sandbox()
        sb.dir = Path(d)
        sb.run = sb.dir / "run-3"
        (sb.run / "raw").mkdir(parents=True)
        sb.manifest_path = sb.run / "manifest.json"
        sb.set_status(SID, "NOT_STARTED")
        proc = sb.run_grade({SID: {"anchors": anchors_from_key(mod, SID, 4),
                                  "critical": False}})
        assert proc.returncode != 0, "a refusal must not exit 0"
        assert sb.grade_file(SID) is None, "a refused scenario wrote a grade file"
        assert "refused" in proc.stderr, proc.stderr
        assert "NOT_STARTED" in proc.stderr, proc.stderr
        s = sb.summary()
        assert s["graded"] == 0, s
        assert s["scored"] == 0, s
        assert s["refused"] and s["refused"][0]["scenario"] == SID, s


@case("a scenario blocked by infrastructure is refused, not scored")
def _():
    mod = load_grader()
    with tempfile.TemporaryDirectory(prefix="apigee-grade-") as d:
        sb = Sandbox()
        sb.dir = Path(d)
        sb.run = sb.dir / "run-3"
        (sb.run / "raw").mkdir(parents=True)
        sb.manifest_path = sb.run / "manifest.json"
        sb.set_status(SID, "BLOCKED_BY_INFRASTRUCTURE")
        proc = sb.run_grade({SID: {"anchors": anchors_from_key(mod, SID, 4),
                                  "critical": False}})
        assert proc.returncode != 0, proc.returncode
        assert sb.grade_file(SID) is None, "a refused scenario wrote a grade file"
        assert "BLOCKED_BY_INFRASTRUCTURE" in proc.stderr, proc.stderr


@case("a scenario awaiting grade with a missing answer file is refused")
def _():
    mod = load_grader()
    with tempfile.TemporaryDirectory(prefix="apigee-grade-") as d:
        sb = Sandbox()
        sb.dir = Path(d)
        sb.run = sb.dir / "run-3"
        (sb.run / "raw").mkdir(parents=True)
        sb.manifest_path = sb.run / "manifest.json"
        sb.set_status(SID, "AWAITING_GRADE")
        sb.write_answers(SID, turn2="")          # turn 1 only
        (sb.run / "raw" / f"{SID}.turn2.md").unlink()
        proc = sb.run_grade({SID: {"anchors": anchors_from_key(mod, SID, 4),
                                  "critical": False}})
        assert proc.returncode != 0, proc.returncode
        assert sb.grade_file(SID) is None, "a refused scenario wrote a grade file"
        assert "answer file" in proc.stderr, proc.stderr


@case("a scenario id the manifest has never heard of is refused")
def _():
    load_grader()
    with tempfile.TemporaryDirectory(prefix="apigee-grade-") as d:
        sb = Sandbox()
        sb.dir = Path(d)
        sb.run = sb.dir / "run-3"
        (sb.run / "raw").mkdir(parents=True)
        sb.manifest_path = sb.run / "manifest.json"
        sb.set_status(SID, "AWAITING_GRADE")
        proc = sb.run_grade({"MED-99": {"anchors": {"a": 4}, "critical": False}})
        assert proc.returncode != 0, proc.returncode
        assert "no such scenario" in proc.stderr, proc.stderr


# ---------------------------------------------------------------------------
# PROTOCOL.md: an invalid grading reference is never a model failure.
# ---------------------------------------------------------------------------


@case("an anchor outside the 0-to-4 scale is unscorable, not a model failure")
def _():
    mod = load_grader()
    with tempfile.TemporaryDirectory(prefix="apigee-grade-") as d:
        sb = Sandbox()
        sb.dir = Path(d)
        sb.run = sb.dir / "run-3"
        (sb.run / "raw").mkdir(parents=True)
        sb.manifest_path = sb.run / "manifest.json"
        sb.set_status(SID, "AWAITING_GRADE")
        sb.write_answers(SID)
        anchors = anchors_from_key(mod, SID, 3)
        first = next(iter(anchors))
        anchors[first] = 7
        sb.run_grade({SID: {"anchors": anchors, "critical": False}})
        g = sb.grade_file(SID)
        assert g is not None, "no grade file was written for a gradeable scenario"
        assert g["verdict"] == "UNSCORABLE", g["verdict"]
        assert g["normalized_score"] is None, g["normalized_score"]
        assert g["unscorable_reason"], "an unscorable verdict must say why"
        assert "7" in g["unscorable_reason"], g["unscorable_reason"]
        s = sb.summary()
        assert s["by_verdict"]["FAIL"] == 0, \
            "a grading input error was counted as a model failure"
        assert s["by_verdict"]["UNSCORABLE"] == 1, s["by_verdict"]


# ---------------------------------------------------------------------------
# The ordinary path must still work.
# ---------------------------------------------------------------------------


@case("a scenario that ran and was scored is graded normally")
def _():
    mod = load_grader()
    with tempfile.TemporaryDirectory(prefix="apigee-grade-") as d:
        sb = Sandbox()
        sb.dir = Path(d)
        sb.run = sb.dir / "run-3"
        (sb.run / "raw").mkdir(parents=True)
        sb.manifest_path = sb.run / "manifest.json"
        sb.set_status(SID, "AWAITING_GRADE")
        sb.write_answers(SID)
        proc = sb.run_grade({SID: {"anchors": anchors_from_key(mod, SID, 4),
                                  "critical": False}})
        assert proc.returncode == 0, proc.stderr
        g = sb.grade_file(SID)
        assert g is not None, "a gradeable scenario wrote no grade file"
        assert g["verdict"] == "PASS", g
        assert g["normalized_score"] == 1.0, g
        assert sb.summary()["graded"] == 1, sb.summary()


@case("a critical failure still fails a scenario that scored perfectly")
def _():
    mod = load_grader()
    with tempfile.TemporaryDirectory(prefix="apigee-grade-") as d:
        sb = Sandbox()
        sb.dir = Path(d)
        sb.run = sb.dir / "run-3"
        (sb.run / "raw").mkdir(parents=True)
        sb.manifest_path = sb.run / "manifest.json"
        sb.set_status(SID, "AWAITING_GRADE")
        sb.write_answers(SID)
        sb.run_grade({SID: {"anchors": anchors_from_key(mod, SID, 4), "critical": True}})
        g = sb.grade_file(SID)
        assert g is not None
        assert g["normalized_score"] == 1.0, g
        assert g["verdict"] == "FAIL", g["verdict"]


@case("one refused scenario does not stop the rest of the run")
def _():
    mod = load_grader()
    with tempfile.TemporaryDirectory(prefix="apigee-grade-") as d:
        sb = Sandbox()
        sb.dir = Path(d)
        sb.run = sb.dir / "run-3"
        (sb.run / "raw").mkdir(parents=True)
        sb.manifest_path = sb.run / "manifest.json"
        sb.set_status(SID, "AWAITING_GRADE")
        sb.write_answers(SID)
        sb.set_status("MED-13", "NOT_STARTED")
        proc = sb.run_grade({
            SID: {"anchors": anchors_from_key(mod, SID, 4), "critical": False},
            "MED-13": {"anchors": {"a": 4}, "critical": False},
        })
        assert proc.returncode != 0, "a refusal must not exit 0"
        assert sb.grade_file(SID) is not None, "the gradeable scenario was not graded"
        assert sb.grade_file("MED-13") is None, "the refused scenario was graded"
        s = sb.summary()
        assert s["graded"] == 1 and s["scored"] == 1, s
        assert len(s["refused"]) == 1, s


@case("more anchors than the rubric has rows is unscorable, not a score above one")
def _():
    # Eight anchors at the top anchor on a seven-row table is 32/28. That is not a grade,
    # it is a score above the scale's own maximum, and it was recorded as a clean PASS.
    mod = load_grader()
    with tempfile.TemporaryDirectory(prefix="apigee-grade-") as d:
        sb = Sandbox()
        sb.dir = Path(d)
        sb.run = sb.dir / "run-3"
        (sb.run / "raw").mkdir(parents=True)
        sb.manifest_path = sb.run / "manifest.json"
        sb.set_status(SID, "AWAITING_GRADE")
        sb.write_answers(SID)
        anchors = anchors_from_key(mod, SID, 4)
        anchors["a dimension the rubric does not have"] = 4
        sb.run_grade({SID: {"anchors": anchors, "critical": False}})
        g = sb.grade_file(SID)
        assert g is not None
        assert g["verdict"] == "UNSCORABLE", g
        assert g["normalized_score"] is None, g
        assert "more" in g["unscorable_reason"], g["unscorable_reason"]
        assert sb.summary()["by_verdict"]["PASS"] == 0, sb.summary()


# ---------------------------------------------------------------------------
# A verdict must name the answer it is about, and a refusal must not leave the
# previous run's verdict standing in its place.
# ---------------------------------------------------------------------------


@case("a grade records the digest of the answer it was computed from")
def _():
    mod = load_grader()
    with tempfile.TemporaryDirectory(prefix="apigee-grade-") as d:
        sb = Sandbox()
        sb.dir = Path(d)
        sb.run = sb.dir / "run-3"
        (sb.run / "raw").mkdir(parents=True)
        sb.manifest_path = sb.run / "manifest.json"
        sb.set_status(SID, "AWAITING_GRADE")
        sb.write_answers(SID, record_digests=True)
        proc = sb.run_grade({SID: {"anchors": anchors_from_key(mod, SID, 4),
                                  "critical": False}})
        assert proc.returncode == 0, proc.stderr
        g = sb.grade_file(SID)
        assert g is not None
        # key_sha256 ties the verdict to a rubric. response_sha256 ties it to a response.
        # Without the second, a grade file says which rules produced it and not what they
        # were applied to.
        assert set(g["response_sha256"]) == {"turn1", "turn2"}, g["response_sha256"]
        for n, body in ((1, "t1"), (2, "t2")):
            want = hashlib.sha256(body.encode()).hexdigest()
            assert g["response_sha256"][f"turn{n}"] == want, g["response_sha256"]


@case("an answer rewritten after collection is refused, not graded")
def _():
    mod = load_grader()
    with tempfile.TemporaryDirectory(prefix="apigee-grade-") as d:
        sb = Sandbox()
        sb.dir = Path(d)
        sb.run = sb.dir / "run-3"
        (sb.run / "raw").mkdir(parents=True)
        sb.manifest_path = sb.run / "manifest.json"
        sb.set_status(SID, "AWAITING_GRADE")
        sb.write_answers(SID, record_digests=True)
        # Same scenario, still AWAITING_GRADE, but turn 2 has been replaced since the
        # manifest recorded it. Grading it would produce a score with no record of which
        # text produced it.
        (sb.run / "raw" / f"{SID}.turn2.md").write_text("a different answer",
                                                        encoding="utf-8")
        proc = sb.run_grade({SID: {"anchors": anchors_from_key(mod, SID, 4),
                                  "critical": False}})
        assert proc.returncode != 0, "answer drift must not exit 0"
        assert sb.grade_file(SID) is None, "a drifted answer was graded"
        assert "not the answer the manifest recorded" in proc.stderr, proc.stderr


@case("an answer the manifest never recorded a digest for is still gradeable")
def _():
    # The opposite failure to guard against: a manifest written before the field existed
    # must not become ungradable, which would turn "cannot prove" into "refused" and read
    # as a run that collected nothing.
    mod = load_grader()
    with tempfile.TemporaryDirectory(prefix="apigee-grade-") as d:
        sb = Sandbox()
        sb.dir = Path(d)
        sb.run = sb.dir / "run-3"
        (sb.run / "raw").mkdir(parents=True)
        sb.manifest_path = sb.run / "manifest.json"
        sb.set_status(SID, "AWAITING_GRADE")
        sb.write_answers(SID)
        proc = sb.run_grade({SID: {"anchors": anchors_from_key(mod, SID, 4),
                                  "critical": False}})
        assert proc.returncode == 0, proc.stderr
        assert sb.grade_file(SID)["verdict"] == "PASS", sb.grade_file(SID)


@case("a refusal clears the previous run's grade for that scenario")
def _():
    mod = load_grader()
    with tempfile.TemporaryDirectory(prefix="apigee-grade-") as d:
        sb = Sandbox()
        sb.dir = Path(d)
        sb.run = sb.dir / "run-3"
        (sb.run / "raw").mkdir(parents=True)
        sb.manifest_path = sb.run / "manifest.json"
        stale = sb.seed_stale_grade(SID)
        assert stale.is_file()
        sb.set_status(SID, "NOT_STARTED")
        proc = sb.run_grade({SID: {"anchors": anchors_from_key(mod, SID, 4),
                                  "critical": False}})
        assert proc.returncode != 0
        # The old PASS was written by a run that could grade this scenario. This run
        # cannot, and a directory still holding that file reads exactly like a result.
        assert not stale.exists(), "the stale grade file survived its own refusal"
        s = sb.summary()
        assert s["refused"][0]["stale_grade_removed"] is True, s["refused"]


@case("a refusal with no earlier grade says so rather than claiming a removal")
def _():
    mod = load_grader()
    with tempfile.TemporaryDirectory(prefix="apigee-grade-") as d:
        sb = Sandbox()
        sb.dir = Path(d)
        sb.run = sb.dir / "run-3"
        (sb.run / "raw").mkdir(parents=True)
        sb.manifest_path = sb.run / "manifest.json"
        sb.set_status(SID, "NOT_STARTED")
        sb.run_grade({SID: {"anchors": anchors_from_key(mod, SID, 4), "critical": False}})
        assert sb.summary()["refused"][0]["stale_grade_removed"] is False, sb.summary()


@case("a grade file is replaced whole, never truncated in place")
def _():
    mod = load_grader()
    with tempfile.TemporaryDirectory(prefix="apigee-grade-") as d:
        sb = Sandbox()
        sb.dir = Path(d)
        sb.run = sb.dir / "run-3"
        (sb.run / "raw").mkdir(parents=True)
        sb.manifest_path = sb.run / "manifest.json"
        sb.set_status(SID, "AWAITING_GRADE")
        sb.write_answers(SID)
        sb.run_grade({SID: {"anchors": anchors_from_key(mod, SID, 4), "critical": False}})
        grades = sb.run / "grades" / "primary"
        # A write that truncates its destination first leaves a file named after a
        # scenario that parses as nothing when the grader dies mid-write. The temporary
        # file is renamed into place instead, so nothing partial ever holds that name.
        assert not list(grades.glob("*.tmp")), sorted(p.name for p in grades.iterdir())
        for p in grades.glob("*.json"):
            json.loads(p.read_text(encoding="utf-8"))  # every file under that name parses


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


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
