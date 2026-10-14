#!/usr/bin/env python3
"""Test that a provider failure can never be recorded as a completed answer.

Why this file exists. `parse_events` appended an error event's message to the assistant
text. The retry branch tested `etype or rc == -1 or not text`, while the give-up branch
tested only `not text`. An error event whose message was nonempty satisfied the second
test and not the first, so on the retry it satisfied neither and control fell through to
the OK branch. The provider's error text was written to `raw/<sid>.turn1.md` and the
scenario was recorded `TURN1_COMPLETE`, which is what put `upstream busy` into
`MED-13.turn1.md` as though the model had written it.

That matters because of what sits downstream. `grade_run.py` selects every scenario the
manifest marks `AWAITING_GRADE`, and a grader reads `raw/<sid>.turn<N>.md`. A false
success is not cosmetic: it hands an error string to a rubric and produces a score for a
turn the model never answered.

The invariant these cases pin down:

  * A provider error is never answer text, however the event stream is shaped.
  * A nonzero exit is never an answer, even when the stream carries text. A provider
    that dies partway through leaves the text it did emit behind, so "the stream was
    not empty" is not evidence that the turn finished.
  * One predicate decides whether an attempt produced an answer, and both the retry
    branch and the give-up branch use it, so nothing that failed can fall through to OK.
  * Every request that was spent is recorded with the status it actually got.
  * Only the OK branch writes an answer artifact. An exhausted retry writes none and
    records BLOCKED_BY_INFRASTRUCTURE.

`tests/test_generation_workspace.py` covers where the model runs. This file covers what
comes back. The two are deliberately separate suites that each stand alone: importing the
other's private names to share plumbing would make either file's failure depend on the
other's internals, and the shared surface here is small. The one thing deliberately not
stubbed is `tests/make_eval_workspace.py`, which runs for real through `subprocess` in
both files.

Usage:
    python3 tests/test_generation_outcomes.py
    python3 tests/test_generation_outcomes.py --json
    python3 tests/test_generation_outcomes.py --only retry
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import tempfile
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Protocol, TypedDict, cast

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "evaluation" / "results" / "run-3" / "run_generation.py"

# Two real scenarios, each with both turn packets in evaluation/packets/.
ALPHA = "MED-13"
BETA = "HARD-22"
ANSWER = "a real answer"
# A stream that stops mid-sentence. A provider that dies partway through still leaves
# the text it managed to emit in the event stream, so a non-empty stream is not evidence
# of a complete answer.
TRUNCATED = "The Quota policy rejects the revision at upload, because the interval"


# ---------------------------------------------------------------------------
# The slice of the manifest these cases assert on.
# ---------------------------------------------------------------------------


class _Turn(TypedDict):
    session_id: str | None
    attempts: int
    chars: int
    raw: str


class _Scenario(TypedDict):
    status: str
    turns: dict[str, _Turn]
    attempts: int
    error: str | None


class _Request(TypedDict):
    sid: str
    turn: int
    attempt: int
    status: str | None


class _Window(TypedDict):
    attempts: int
    quota_exhausted: bool
    requests: list[_Request]


class _Manifest(TypedDict):
    run: str
    protocol: str
    created: str
    model: str | None
    budget: dict[str, object]
    scenarios: dict[str, _Scenario]


# ---------------------------------------------------------------------------
# Harness plumbing. Only `opencode run` is faked.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Step:
    """One `opencode run` the stub returns.

    `timeout` models the harness's own `subprocess.TimeoutExpired` handler, which the
    workspace cases cannot reach because their stub always exits 0.
    """
    out: str = ""
    rc: int = 0
    err: str = ""
    timeout: bool = False


def turn_stream(text: str, session: str = "sess-1") -> str:
    """One turn's `opencode run --format json` event stream."""
    return json.dumps({"type": "text", "sessionID": session,
                       "part": {"type": "text", "text": text}}) + "\n"


def error_stream(message: str, etype: str = "ProviderError",
                 session: str = "sess-err") -> str:
    """An `opencode run --format json` stream carrying only a provider error."""
    return json.dumps({"type": "error", "sessionID": session,
                       "error": {"type": etype, "message": message}}) + "\n"


class _SubprocessShim:
    """Stands in for the `subprocess` module the harness holds a reference to.

    Only `opencode run` is intercepted. Everything else reaches the real `subprocess`,
    so the workspace builder under test stays the real one.

    `run` spells out the keywords run_generation.py passes rather than accepting
    `**kwargs`, so a call the shim does not model raises here instead of quietly
    reaching a provider.
    """

    TimeoutExpired: type[subprocess.TimeoutExpired] = subprocess.TimeoutExpired
    CalledProcessError: type[subprocess.CalledProcessError] = subprocess.CalledProcessError

    def __init__(self, owner: "Harness") -> None:
        self.owner: Harness = owner

    def run(self, cmd: list[str], cwd: Path | None = None, check: bool = False,
            capture_output: bool = False, text: bool = False,
            timeout: float | None = None) -> subprocess.CompletedProcess[str]:
        if cmd and cmd[0] == "opencode":
            self.owner.calls.append({"cwd": cwd, "argv": list(cmd)})
            plan = self.owner.plan
            step = plan.pop(0) if len(plan) > 1 else (plan[0] if plan else Step())
            if step.timeout:
                raise subprocess.TimeoutExpired(cmd, timeout if timeout is not None else 0)
            return subprocess.CompletedProcess(cmd, step.rc, stdout=step.out, stderr=step.err)
        return cast("subprocess.CompletedProcess[str]", subprocess.run(
            cmd, cwd=cwd, check=check, capture_output=capture_output,
            text=text, timeout=timeout))


# run_generation.py is a script, not an importable package module, so it is loaded by path
# and cast to the surface these cases drive. Declaring that surface keeps basedpyright
# from treating every attribute as `Any`, which would hide a renamed or removed function.
class _Harness(Protocol):
    RUN: Path
    RAW: Path
    MANIFEST: Path
    WS_ROOT: Path
    MAX_ATTEMPTS: int
    subprocess: _SubprocessShim

    def save(self, m: Mapping[str, object]) -> None: ...
    def ws_path(self, ids: list[str]) -> Path: ...
    def one_turn(self, m: Mapping[str, object], sid: str, turn: int, model: str,
                 timeout: int) -> str: ...
    def parse_events(self, raw: str) -> tuple[str, str | None, str | None, str | None]: ...


class _ProviderCall(TypedDict):
    cwd: object
    argv: list[str]


def load_harness() -> _Harness:
    """A fresh copy of the real harness, so one case cannot inherit another's patches."""
    spec = importlib.util.spec_from_file_location("run_generation_under_test", HARNESS)
    assert spec is not None and spec.loader is not None, HARNESS
    mod: ModuleType = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return cast("_Harness", cast("object", mod))


class Harness:
    """The real module with its output paths redirected and the provider call faked.

    The redirection is what keeps this file safe: the harness writes its manifest, its raw
    event streams and its workspaces wherever its module globals point, so pointing them
    at a temporary directory is the difference between a test and an overwritten run.
    There is nothing to tear down; each call loads a separate copy of the module.
    """

    def __init__(self, tmp: Path) -> None:
        self.mod: _Harness = load_harness()
        self.mod.RUN = tmp / "run"
        self.mod.RAW = self.mod.RUN / "raw"
        self.mod.MANIFEST = self.mod.RUN / "manifest.json"
        self.mod.WS_ROOT = tmp / "ws"
        self.calls: list[_ProviderCall] = []
        self.plan: list[Step] = []
        self.mod.subprocess = _SubprocessShim(self)

    def script(self, *steps: Step) -> None:
        self.plan = list(steps)

    def manifest(self, ids: list[str]) -> _Manifest:
        m: _Manifest = {
            "run": "run-3", "protocol": "evaluation/results/run-3/PROTOCOL.md",
            "created": "2026-01-01T00:00:00+05:30", "model": None,
            "budget": {"max_attempts_per_window": self.mod.MAX_ATTEMPTS, "windows": {}},
            "scenarios": {s: {"status": "NOT_STARTED", "turns": {}, "attempts": 0,
                              "error": None} for s in ids},
        }
        self.mod.save(m)
        return m


CASES: list[tuple[str, Callable[[], None]]] = []


def case(name: str) -> Callable[[Callable[[], None]], Callable[[], None]]:
    def deco(f: Callable[[], None]) -> Callable[[], None]:
        CASES.append((name, f))
        return f
    return deco


# ---------------------------------------------------------------------------
# Assertion helpers.
# ---------------------------------------------------------------------------


def requests(m: _Manifest) -> list[_Request]:
    """Every request spent, in order, across all quota windows."""
    windows = cast("dict[str, _Window]", m["budget"]["windows"])
    return [r for w in windows.values() for r in w["requests"]]


def statuses(m: _Manifest) -> list[tuple[str, int, str | None]]:
    """(scenario, attempt, recorded status) for every request spent, in order.

    `attempt` restarts at 1 for each `one_turn` call, so two scenarios both open with
    attempt 1. Pairing it with the scenario is what makes the log readable.
    """
    return [(r["sid"], r["attempt"], r["status"]) for r in requests(m)]


def answer_file(h: Harness, sid: str, turn: int) -> Path:
    return h.mod.RAW / f"{sid}.turn{turn}.md"


def harness(tmp: Path) -> Harness:
    return Harness(tmp)


def assert_no_answer(h: Harness, m: _Manifest, sid: str, turn: int = 1) -> None:
    """A turn that failed left nothing a grader could read."""
    rec = m["scenarios"][sid]
    path = answer_file(h, sid, turn)
    assert not path.exists(), f"a failed turn wrote an answer artifact: {path.read_text()!r}"
    assert rec["turns"] == {}, f"a failed turn recorded a completed turn: {rec['turns']}"
    assert rec["status"] not in ("TURN1_COMPLETE", "TURN2_COMPLETE", "AWAITING_GRADE"), \
        f"a failed turn reads as completed: {rec['status']}"
    assert rec["error"], "a blocked turn must record why"


# ---------------------------------------------------------------------------
# The regression: an error event carrying text is not an answer.
# ---------------------------------------------------------------------------


@case("a provider error carrying text is never written as the answer")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA])
        h.script(Step(error_stream("upstream busy")), Step(error_stream("upstream busy")))
        st = h.mod.one_turn(m, ALPHA, 1, "fake/model", 30)
        assert st == "BLOCKED_BY_INFRASTRUCTURE", st
        assert_no_answer(h, m, ALPHA)
        # The provider's message is kept, as the reason, rather than as the answer.
        assert "upstream busy" in (m["scenarios"][ALPHA]["error"] or ""), \
            m["scenarios"][ALPHA]["error"]


@case("a provider error without text is not an answer either")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA])
        h.script(Step(error_stream("")), Step(error_stream("")))
        st = h.mod.one_turn(m, ALPHA, 1, "fake/model", 30)
        assert st == "BLOCKED_BY_INFRASTRUCTURE", st
        assert_no_answer(h, m, ALPHA)


@case("an error event's message never reaches the assistant text")
def _():
    h = harness(Path("/nonexistent"))       # no request is made; only parse_events is used
    text, etype, emsg, _sid = h.mod.parse_events(
        error_stream("upstream busy") + turn_stream("real prose"))
    assert text == "real prose", f"the error leaked into the answer text: {text!r}"
    assert etype == "ProviderError", etype
    assert emsg == "upstream busy", emsg


@case("error text and answer text in one stream keeps only the answer")
def _():
    h = harness(Path("/nonexistent"))
    text, _etype, emsg, _sid = h.mod.parse_events(
        error_stream("upstream busy") + turn_stream(ANSWER))
    assert text == ANSWER, text
    assert emsg == "upstream busy", emsg


# ---------------------------------------------------------------------------
# Request accounting. Every request spent carries the status it actually got.
# ---------------------------------------------------------------------------


@case("a first-attempt failure is recorded as RETRY_ONCE, not as a blank request")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA])
        h.script(Step(error_stream("upstream busy")), Step(turn_stream(ANSWER)))
        st = h.mod.one_turn(m, ALPHA, 1, "fake/model", 30)
        assert st == "TURN1_COMPLETE", st
        assert statuses(m) == [(ALPHA, 1, "RETRY_ONCE"), (ALPHA, 2, "OK")], statuses(m)


@case("a successful retry is recorded as holding the real answer")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA])
        h.script(Step(error_stream("upstream busy")), Step(turn_stream(ANSWER)))
        st = h.mod.one_turn(m, ALPHA, 1, "fake/model", 30)
        assert st == "TURN1_COMPLETE", st
        assert answer_file(h, ALPHA, 1).read_text(encoding="utf-8") == ANSWER
        turn = m["scenarios"][ALPHA]["turns"]["turn1"]
        assert turn["attempts"] == 2, turn
        assert turn["chars"] == len(ANSWER), turn
        assert turn["raw"] == f"raw/{ALPHA}.turn1.attempt2.jsonl", turn


@case("a clean first response is one request, recorded OK")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA])
        h.script(Step(turn_stream(ANSWER)))
        st = h.mod.one_turn(m, ALPHA, 1, "fake/model", 30)
        assert st == "TURN1_COMPLETE", st
        assert len(h.calls) == 1, h.calls
        assert m["scenarios"][ALPHA]["attempts"] == 1, m["scenarios"][ALPHA]["attempts"]
        assert statuses(m) == [(ALPHA, 1, "OK")], statuses(m)
        assert answer_file(h, ALPHA, 1).read_text(encoding="utf-8") == ANSWER


# ---------------------------------------------------------------------------
# Exhausted retries must not produce a completed answer artifact.
# ---------------------------------------------------------------------------


@case("an exhausted retry leaves no answer artifact and keeps the raw evidence")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA])
        h.script(Step(error_stream("upstream busy")), Step(error_stream("upstream busy")))
        st = h.mod.one_turn(m, ALPHA, 1, "fake/model", 30)
        assert st == "BLOCKED_BY_INFRASTRUCTURE", st
        assert_no_answer(h, m, ALPHA)
        assert m["scenarios"][ALPHA]["attempts"] == 2, m["scenarios"][ALPHA]["attempts"]
        assert statuses(m) == [(ALPHA, 1, "RETRY_ONCE"),
                               (ALPHA, 2, "NO_ANSWER")], statuses(m)
        kept = sorted(p.name for p in h.mod.RAW.glob(f"{ALPHA}.turn1.*"))
        assert kept == [f"{ALPHA}.turn1.attempt1.jsonl",
                        f"{ALPHA}.turn1.attempt2.jsonl"], kept


@case("a turn-2 failure does not reach AWAITING_GRADE")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA])
        h.script(Step(turn_stream("turn one answer")),
                 Step(error_stream("upstream busy")),
                 Step(error_stream("upstream busy")))
        assert h.mod.one_turn(m, ALPHA, 1, "fake/model", 30) == "TURN1_COMPLETE"
        st = h.mod.one_turn(m, ALPHA, 2, "fake/model", 30)
        assert st == "BLOCKED_BY_INFRASTRUCTURE", st
        rec = m["scenarios"][ALPHA]
        assert rec["status"] != "AWAITING_GRADE", rec["status"]
        # Turn one is still on disk and still readable; turn two wrote nothing.
        assert answer_file(h, ALPHA, 1).read_text(encoding="utf-8") == "turn one answer"
        assert not answer_file(h, ALPHA, 2).exists(), "a failed turn 2 wrote an answer"
        assert "turn2" not in rec["turns"], rec["turns"]


@case("a timeout is not an answer")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA])
        h.script(Step(timeout=True), Step(timeout=True))
        st = h.mod.one_turn(m, ALPHA, 1, "fake/model", 30)
        assert st == "BLOCKED_BY_INFRASTRUCTURE", st
        assert_no_answer(h, m, ALPHA)
        assert "TIMEOUT" in (m["scenarios"][ALPHA]["error"] or ""), \
            m["scenarios"][ALPHA]["error"]


@case("a quota error is still not retried and still writes no answer")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA])
        h.script(Step(error_stream("free-models-per-day exhausted", etype="RateLimitError")),
                 Step(turn_stream(ANSWER)))
        st = h.mod.one_turn(m, ALPHA, 1, "fake/model", 30)
        assert st == "BLOCKED_BY_INFRASTRUCTURE", st
        assert len(h.calls) == 1, "a quota error was retried"
        assert statuses(m) == [(ALPHA, 1, "QUOTA_EXHAUSTED")], statuses(m)
        assert_no_answer(h, m, ALPHA)


@case("a nonzero exit carrying text is not an answer")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA])
        h.script(Step(turn_stream(TRUNCATED), rc=1, err="provider stream aborted"),
                 Step(turn_stream(TRUNCATED), rc=1, err="provider stream aborted"))
        st = h.mod.one_turn(m, ALPHA, 1, "fake/model", 30)
        assert st == "BLOCKED_BY_INFRASTRUCTURE", st
        assert_no_answer(h, m, ALPHA)
        assert statuses(m) == [(ALPHA, 1, "RETRY_ONCE"),
                               (ALPHA, 2, "NO_ANSWER")], statuses(m)


@case("a nonzero exit is reported as a nonzero exit, not as an empty response")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA])
        # No stderr and no error event: the only thing that says the call failed is the
        # exit code. Recording "empty response" here would be a false description of a
        # turn that returned text.
        h.script(Step(turn_stream(TRUNCATED), rc=2), Step(turn_stream(TRUNCATED), rc=2))
        assert h.mod.one_turn(m, ALPHA, 1, "fake/model", 30) == "BLOCKED_BY_INFRASTRUCTURE"
        assert_no_answer(h, m, ALPHA)
        err = m["scenarios"][ALPHA]["error"] or ""
        assert "2" in err, f"the exit code is not in the recorded reason: {err!r}"
        assert "empty response" not in err, err


@case("a 429 exit is still a quota error, not a generic failure")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA])
        # 429 is a nonzero exit and now satisfies the failure predicate, so the quota
        # branch above it has to keep taking precedence or the budget window would be
        # retried against a provider that has already said it is done.
        h.script(Step(turn_stream(TRUNCATED), rc=429), Step(turn_stream(ANSWER)))
        st = h.mod.one_turn(m, ALPHA, 1, "fake/model", 30)
        assert st == "BLOCKED_BY_INFRASTRUCTURE", st
        assert len(h.calls) == 1, "a 429 exit was retried"
        assert statuses(m) == [(ALPHA, 1, "QUOTA_EXHAUSTED")], statuses(m)
        assert_no_answer(h, m, ALPHA)


@case("one scenario failing does not stop the next one")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA, BETA])
        h.script(Step(error_stream("upstream busy")), Step(error_stream("upstream busy")),
                 Step(turn_stream("beta answer")))
        assert h.mod.one_turn(m, ALPHA, 1, "fake/model", 30) == "BLOCKED_BY_INFRASTRUCTURE"
        assert h.mod.one_turn(m, BETA, 1, "fake/model", 30) == "TURN1_COMPLETE"
        assert not answer_file(h, ALPHA, 1).exists(), "ALPHA kept a fake answer"
        assert answer_file(h, BETA, 1).read_text(encoding="utf-8") == "beta answer"
        assert statuses(m) == [(ALPHA, 1, "RETRY_ONCE"), (ALPHA, 2, "NO_ANSWER"),
                               (BETA, 1, "OK")], statuses(m)


def main() -> int:
    ap = argparse.ArgumentParser()
    _ = ap.add_argument("--json", action="store_true")
    _ = ap.add_argument("--only", default=None, help="substring filter on case name")
    args = ap.parse_args()

    only = cast("str | None", args.only)
    results: list[dict[str, object]] = []
    for name, fn in CASES:
        if only and only not in name:
            continue
        try:
            fn()
            results.append({"name": name, "ok": True, "note": ""})
        except AssertionError as e:
            results.append({"name": name, "ok": False, "note": str(e) or "assertion failed"})
        except Exception as e:  # a crash is a failure, not an error to hide
            results.append({"name": name, "ok": False, "note": f"{type(e).__name__}: {e}"})

    failed = [r for r in results if not r["ok"]]
    if bool(args.json):
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            mark = "ok  " if r["ok"] else "FAIL"
            note = f"\n       {r['note']}" if r["note"] else ""
            print(f"{mark} {r['name']}{note}")
        print()
        print(f"{len(results)} cases, {len(results) - len(failed)} passed, {len(failed)} failed")
        for r in failed:
            print(f"  FAILED: {r['name']} -- {r['note']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())