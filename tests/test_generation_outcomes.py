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
  * A scenario that stopped for a reason the next quota window clears comes back in the
    next window, and one that stopped for a reason it does not clear does not. Both were
    terminal once, because `todo` selected `NOT_STARTED` and nothing else, so a 429 or an
    interrupted run retired the scenario for the rest of the evaluation.
  * Turn 2 is not run cold. PROTOCOL.md requires it in the same conversation as turn 1,
    and the flag that carries the conversation was omitted when turn 1's stream carried
    no session id, which graded a follow-up answered without the original ticket.

`tests/test_generation_workspace.py` covers where the model runs. This file covers what
comes back, and whether the run can carry on afterwards. The two are deliberately separate
suites that each stand alone: importing the other's private names to share plumbing would
make either file's failure depend on the other's internals, and the shared surface here is
small. The one thing deliberately not stubbed is `tests/make_eval_workspace.py`, which runs
for real through `subprocess` in both files.

Usage:
    python3 tests/test_generation_outcomes.py
    python3 tests/test_generation_outcomes.py --json
    python3 tests/test_generation_outcomes.py --only retry
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
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
    `spawn_error` models the binary being missing or unrunnable, which the harness must
    not retry and must not report as a provider failure it can wait out.
    """
    out: str = ""
    rc: int = 0
    err: str = ""
    timeout: bool = False
    spawn_error: str | None = None


def step_finish(session: str | None = "sess-1") -> str:
    """The event the CLI writes when it closes a step.

    `--format json` emits `{"type":"step_finish","part":{"type":"step-finish",...}}`, and
    it is the only thing in the stream that says the answer finished. A run cut short
    after a step never emits it, which is what the truncated cases below model.
    `session=None` writes the closing event without a sessionID, which is what the
    sessionless stream needs so the closing event does not quietly supply the id the
    stream is supposed to be missing.
    """
    event: dict[str, object] = {"type": "step_finish", "part": {"type": "step-finish"}}
    if session is not None:
        event["sessionID"] = session
    return json.dumps(event) + "\n"


def turn_stream(text: str, session: str = "sess-1") -> str:
    """One complete turn's `opencode run --format json` event stream."""
    return json.dumps({"type": "text", "sessionID": session,
                       "part": {"type": "text", "text": text}}) + "\n" + step_finish(session)


def unfinished_stream(text: str, session: str = "sess-1") -> str:
    """Prose with no closing event: a stream that stopped mid-turn and exited 0.

    The provider can exit 0 after emitting the text it managed to produce, so this is the
    shape of a truncated answer, and it is the case no exit-code test can catch.
    """
    return json.dumps({"type": "text", "sessionID": session,
                       "part": {"type": "text", "text": text}}) + "\n"


def sessionless_stream(text: str) -> str:
    """A complete turn whose stream carries no `sessionID` at all.

    Nothing in the harness produced this, and it is not a provider error: it is the shape
    that let turn 2 run cold. Modelled here because the guard against it has to exist for
    the stream the harness did not get an id from, whatever the reason was.
    """
    return json.dumps({"type": "text", "part": {"type": "text", "text": text}}) + "\n" \
        + step_finish(None)


def error_stream(message: str, etype: str = "ProviderError",
                 session: str = "sess-err") -> str:
    """An `opencode run --format json` stream carrying only a provider error."""
    return json.dumps({"type": "error", "sessionID": session,
                       "error": {"type": etype, "message": message}}) + "\n"


def quota_stream() -> str:
    """A provider quota error, the one failure the protocol says closes the window."""
    return error_stream("free-models-per-day exhausted", etype="RateLimitError")


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
            if step.spawn_error:
                raise FileNotFoundError(step.spawn_error)
            return subprocess.CompletedProcess(cmd, step.rc, stdout=step.out, stderr=step.err)
        return cast("subprocess.CompletedProcess[str]", subprocess.run(
            cmd, cwd=cwd, check=check, capture_output=capture_output,
            text=text, timeout=timeout))


# run_generation.py is a script, not an importable package module, so it is loaded by path
# and cast to the surface these cases drive. Declaring that surface keeps basedpyright
# from treating every attribute as `Any`, which would hide a renamed or removed function.
class _Stream(Protocol):
    """The slice of run_generation.Stream these cases assert on."""
    text: str
    error_type: str | None
    error_message: str | None
    session_id: str | None
    completed: bool
    malformed: int


class _Harness(Protocol):
    RUN: Path
    RAW: Path
    MANIFEST: Path
    WS_ROOT: Path
    MAX_ATTEMPTS: int
    BLOCK_WINDOW: str
    BLOCK_TERMINAL: str
    subprocess: _SubprocessShim

    def save(self, m: Mapping[str, object]) -> None: ...
    def ws_path(self, ids: list[str]) -> Path: ...
    def one_turn(self, m: Mapping[str, object], sid: str, turn: int, model: str,
                 timeout: int) -> str: ...
    def parse_events(self, raw: str) -> _Stream: ...
    def window_key(self, d: datetime) -> str: ...
    def main(self) -> int: ...
    def now_ist(self) -> datetime: ...


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
        self.out: str = ""
        self.err: str = ""
        self.mod.subprocess = _SubprocessShim(self)

    def script(self, *steps: Step) -> None:
        self.plan = list(steps)

    def run_main(self, *argv: str) -> int:
        """Drive the harness's own main() with a controlled argv, capturing its output.

        A second invocation in the same window is the whole of R1: selection used to read
        the manifest afresh through main(), and what it then selected was the question.
        """
        out, err = io.StringIO(), io.StringIO()
        saved = sys.argv
        sys.argv = ["run_generation.py", *argv]
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = self.mod.main()
        finally:
            sys.argv = saved
        self.out, self.err = out.getvalue(), err.getvalue()
        return int(rc)

    def next_window(self) -> None:
        """Move this harness's clock on one day: what a quota reset looks like from inside.

        `window()` keys its counter on the date, so a later day is a fresh counter with
        `quota_exhausted` back to False. Nothing else in the manifest moves, which is the
        point: a scenario the previous window blocked has to come back on its own, without
        anybody editing the file by hand.
        """
        real = self.mod.now_ist
        self.mod.now_ist = lambda: real() + timedelta(days=1)

    def reload(self) -> _Manifest:
        """The manifest as it is on disk.

        `main` reads the file itself, so every invocation gets its own dict and a handle
        taken before a `run_main` is stale afterwards. Every case below reloads rather than
        reading the object it passed in, which is what a resuming session sees.
        """
        return cast("_Manifest",
                    json.loads(self.mod.MANIFEST.read_text(encoding="utf-8")))

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
    s = h.mod.parse_events(error_stream("upstream busy") + turn_stream("real prose"))
    assert s.text == "real prose", f"the error leaked into the answer text: {s.text!r}"
    assert s.error_type == "ProviderError", s.error_type
    assert s.error_message == "upstream busy", s.error_message


@case("error text and answer text in one stream keeps only the answer")
def _():
    h = harness(Path("/nonexistent"))
    s = h.mod.parse_events(error_stream("upstream busy") + turn_stream(ANSWER))
    assert s.text == ANSWER, s.text
    assert s.error_message == "upstream busy", s.error_message


@case("a complete stream reports the CLI's closing step event")
def _():
    h = harness(Path("/nonexistent"))
    s = h.mod.parse_events(turn_stream(ANSWER))
    assert s.completed is True, s
    assert s.malformed == 0, s


@case("a stream that stopped before the closing event is not complete")
def _():
    h = harness(Path("/nonexistent"))
    s = h.mod.parse_events(unfinished_stream(TRUNCATED))
    assert s.text == TRUNCATED, s.text
    assert s.completed is False, s


@case("a line that is not JSON is counted, not ignored")
def _():
    h = harness(Path("/nonexistent"))
    s = h.mod.parse_events(turn_stream(ANSWER) + "{not json\n" + "42\n")
    assert s.malformed == 2, s
    assert s.text == ANSWER, s.text


@case("text alone at exit 0 is not an answer")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA])
        # Exit 0, prose in the stream, no step_finish: the shape a provider cut short
        # leaves behind. Nothing about it says the answer finished.
        h.script(Step(unfinished_stream(TRUNCATED)), Step(unfinished_stream(TRUNCATED)))
        st = h.mod.one_turn(m, ALPHA, 1, "fake/model", 30)
        assert st == "BLOCKED_BY_INFRASTRUCTURE", st
        assert_no_answer(h, m, ALPHA)
        assert statuses(m) == [(ALPHA, 1, "RETRY_ONCE"), (ALPHA, 2, "NO_ANSWER")], statuses(m)
        err = m["scenarios"][ALPHA]["error"] or ""
        assert "never reported the step as finished" in err, err


@case("a malformed line in an otherwise complete stream is not an answer")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA])
        h.script(Step(turn_stream(ANSWER) + '{"type":"text","part":{"typ\n'),
                  Step(turn_stream(ANSWER) + '{"type":"text","part":{"typ\n'))
        st = h.mod.one_turn(m, ALPHA, 1, "fake/model", 30)
        assert st == "BLOCKED_BY_INFRASTRUCTURE", st
        assert_no_answer(h, m, ALPHA)
        err = m["scenarios"][ALPHA]["error"] or ""
        assert "not valid JSON" in err, err


@case("a binary that cannot be run is terminal and spends one request")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA])
        h.script(Step(spawn_error="opencode"), Step(turn_stream(ANSWER)))
        st = h.mod.one_turn(m, ALPHA, 1, "fake/model", 30)
        assert st == "BLOCKED_BY_INFRASTRUCTURE", st
        assert_no_answer(h, m, ALPHA)
        # One attempt, not two: a missing binary is not a transient provider failure.
        assert len(h.calls) == 1, h.calls
        assert statuses(m) == [(ALPHA, 1, "NO_ANSWER")], statuses(m)
        err = m["scenarios"][ALPHA]["error"] or ""
        assert "could not run opencode" in err, err
        assert m["scenarios"][ALPHA]["block_kind"] == harness_kind(h, "BLOCK_TERMINAL")


@case("a prompt packet that cannot be read is terminal and spends nothing")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest(["NOPE-99"])
        st = h.mod.one_turn(m, "NOPE-99", 1, "fake/model", 30)
        assert st == "BLOCKED_BY_INFRASTRUCTURE", st
        assert len(h.calls) == 0, h.calls
        err = m["scenarios"]["NOPE-99"]["error"] or ""
        assert "NOPE-99.prompt.md is unreadable" in err, err


@case("the quota window opens at 05:30 IST, not at midnight")
def _():
    h = harness(Path("/nonexistent"))      # window_key is pure; no request is made
    ist = timezone(timedelta(hours=5, minutes=30))
    before = datetime(2026, 10, 16, 4, 59, tzinfo=ist)
    after = datetime(2026, 10, 16, 5, 30, tzinfo=ist)
    late = datetime(2026, 10, 16, 23, 59, tzinfo=ist)
    # 04:59 IST still spends from the window that opened the previous day.
    assert h.mod.window_key(before) == "2026-10-15 05:30->05:29 IST", h.mod.window_key(before)
    assert h.mod.window_key(after) == "2026-10-16 05:30->05:29 IST", h.mod.window_key(after)
    assert h.mod.window_key(late) == "2026-10-16 05:30->05:29 IST", h.mod.window_key(late)


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


# ---------------------------------------------------------------------------
# Resumption. `todo` selected `NOT_STARTED` and nothing else, so every state a run can
# stop in was also a state it could not come back from. A quota window reset and an
# interrupted process are the two a resuming session meets first.
# ---------------------------------------------------------------------------


def blocked_kind(h: Harness, m: _Manifest, sid: str) -> str | None:
    """The recorded block kind, or None if the scenario is not blocked at all.

    `block_kind` is what separates "the next window retries this" from "this needs a
    decision", so the cases below assert on it directly rather than on the error string.
    """
    rec = cast("dict[str, object]", m["scenarios"][sid])
    kind = rec.get("block_kind")
    return cast("str | None", kind)


def harness_kind(h: Harness, which: str) -> str:
    """`run_generation.py`'s BLOCK_WINDOW or BLOCK_TERMINAL, read by name.

    Through an assertion, so a case pinning the kind fails on the value it recorded rather
    than on an AttributeError for a constant that did not exist yet. The name is looked up
    rather than hardcoded here so that renaming the constant fails these cases too.
    """
    value = getattr(h.mod, which, None)
    assert value, f"run_generation.py defines no {which}"
    return cast(str, value)


@case("a scenario blocked by a quota error is collected in the next window")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA])
        h.script(Step(quota_stream()),
                 Step(turn_stream("turn one answer")), Step(turn_stream("turn two answer")))
        assert h.run_main("--only", ALPHA) == 0, h.err
        m = h.reload()
        rec = m["scenarios"][ALPHA]
        assert rec["status"] == "BLOCKED_BY_INFRASTRUCTURE", rec["status"]
        assert statuses(m) == [(ALPHA, 1, "QUOTA_EXHAUSTED")], statuses(m)
        kind = blocked_kind(h, m, ALPHA)
        spent = len(h.calls)

        # The quota window resets. Nothing was edited by hand: the manifest still holds the
        # blocked status it was left with, and the scenario has to come back on its own.
        h.next_window()
        assert h.run_main("--only", ALPHA) == 0, h.err
        m = h.reload()
        rec = m["scenarios"][ALPHA]
        assert rec["status"] == "AWAITING_GRADE", (rec["status"], h.out)
        assert kind == harness_kind(h, "BLOCK_WINDOW"), kind
        assert len(h.calls) - spent == 2, f"expected both turns, spent {len(h.calls) - spent}"
        # The block is cleared on the way through. Left behind, it would make --list
        # report a collected scenario as one still waiting on a window.
        assert blocked_kind(h, m, ALPHA) is None, blocked_kind(h, m, ALPHA)
        assert rec["error"] is None, rec["error"]
        assert answer_file(h, ALPHA, 1).read_text(encoding="utf-8") == "turn one answer"
        assert answer_file(h, ALPHA, 2).read_text(encoding="utf-8") == "turn two answer"


@case("a scenario blocked during turn 2 comes back for turn 2, not for turn 1 again")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA])
        h.script(Step(turn_stream("turn one answer", "sess-9")), Step(quota_stream()),
                 Step(turn_stream("turn two answer", "sess-9")))
        assert h.run_main("--only", ALPHA) == 0, h.err
        m = h.reload()
        rec = m["scenarios"][ALPHA]
        assert rec["status"] == "BLOCKED_BY_INFRASTRUCTURE", rec["status"]
        assert sorted(rec["turns"]) == ["turn1"], rec["turns"]
        spent = len(h.calls)

        h.next_window()
        assert h.run_main("--only", ALPHA) == 0, h.err
        m = h.reload()
        rec = m["scenarios"][ALPHA]
        assert rec["status"] == "AWAITING_GRADE", (rec["status"], h.out)
        # One request, not two. Turn 1 was collected; re-running it would spend a second
        # request on an answer the grader will read.
        assert len(h.calls) - spent == 1, f"spent {len(h.calls) - spent} requests"
        assert requests(m)[-1]["turn"] == 2, requests(m)[-1]
        argv = h.calls[-1]["argv"]
        assert argv[argv.index("--session") + 1] == "sess-9", argv


@case("a scenario left at TURN1_COMPLETE by an interrupted run gets its turn 2")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA, BETA])
        # Turn 1 lands and the process dies before turn 2, which is what a killed session
        # or a closed laptop leaves behind. TURN1_COMPLETE is a state with work in it, and
        # a resumed session is expected to work through the batch, not one scenario of it.
        h.script(Step(turn_stream("turn one answer", "sess-3")))
        assert h.mod.one_turn(m, ALPHA, 1, "fake/model", 30) == "TURN1_COMPLETE"
        assert h.mod.one_turn(m, BETA, 1, "fake/model", 30) == "TURN1_COMPLETE"
        assert m["scenarios"][ALPHA]["status"] == "TURN1_COMPLETE"

        assert h.run_main("--only", ALPHA, "--only", BETA) == 0, h.err
        assert "nothing pending" not in h.out, h.out
        m = h.reload()
        for sid in (ALPHA, BETA):
            rec = m["scenarios"][sid]
            assert rec["status"] == "AWAITING_GRADE", (sid, rec["status"], h.out)
            assert sorted(rec["turns"]) == ["turn1", "turn2"], (sid, rec["turns"])
        assert len(h.calls) == 4, f"a resumed run stopped after one scenario: {h.calls}"
        assert answer_file(h, ALPHA, 2).read_text(encoding="utf-8") == "turn one answer"


@case("a window-blocked scenario is not offered again inside the window that blocked it")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA, BETA])
        h.script(Step(quota_stream()), Step(turn_stream("beta answer")))
        assert h.run_main("--only", ALPHA, "--only", BETA) == 0, h.err
        assert h.calls and h.calls[-1]["argv"][0] == "opencode"
        spent = len(h.calls)
        m = h.reload()

        # Same window. The quota is still gone, so there is nothing to spend, and BETA must
        # not be marked blocked for a window it never ran in.
        assert h.run_main("--only", ALPHA, "--only", BETA) == 0, h.err
        assert len(h.calls) == spent, "a closed window spent requests anyway"
        m = h.reload()
        assert m["scenarios"][ALPHA]["status"] == "BLOCKED_BY_INFRASTRUCTURE"
        assert m["scenarios"][BETA]["status"] == "NOT_STARTED", m["scenarios"][BETA]
        assert m["scenarios"][BETA]["error"] is None, m["scenarios"][BETA]


@case("a scenario blocked for a reason the next window cannot clear is not retried")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA])
        # A provider failure, not the quota: the window is untouched, so the next window
        # has nothing to clear. Retrying it would spend the budget proving again that the
        # same turn fails.
        h.script(Step(error_stream("upstream busy")), Step(error_stream("upstream busy")),
                 Step(turn_stream("an answer that must not be collected")))
        assert h.run_main("--only", ALPHA) == 0, h.err
        m = h.reload()
        assert m["scenarios"][ALPHA]["status"] == "BLOCKED_BY_INFRASTRUCTURE"
        kind = blocked_kind(h, m, ALPHA)
        spent = len(h.calls)

        h.next_window()
        assert h.run_main("--only", ALPHA) == 0, h.err
        assert len(h.calls) == spent, "a terminal block was retried in the next window"
        assert "nothing pending" in h.out, h.out
        assert kind == harness_kind(h, "BLOCK_TERMINAL"), kind
        assert not answer_file(h, ALPHA, 1).exists(), "the retry wrote an answer"


@case("--list agrees with what a resuming run would actually collect")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA, BETA])
        h.script(Step(turn_stream("an answer")))
        assert h.run_main("--only", ALPHA) == 0, h.err
        m["scenarios"][BETA]["status"] = "GRADED"
        h.mod.save(m)

        assert h.run_main("--only", ALPHA, "--only", BETA, "--list") == 0, h.err
        # One pending: BETA. Counting "not AWAITING_GRADE" reported the graded one too, so
        # --list and the batch it announces could not be reconciled.
        assert "pending in selection: 1" in h.out, h.out


# ---------------------------------------------------------------------------
# Turn 2 must run in turn 1's conversation. Without it the follow-up is answered cold and
# graded as though the scenario's two turns had shared context.
# ---------------------------------------------------------------------------


@case("turn 2 with no session id from turn 1 is refused and spends nothing")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA])
        h.script(Step(sessionless_stream("turn one answer")))
        assert h.mod.one_turn(m, ALPHA, 1, "fake/model", 30) == "TURN1_COMPLETE"
        rec = m["scenarios"][ALPHA]
        assert rec["turns"]["turn1"]["session_id"] is None, rec["turns"]["turn1"]
        spent = len(h.calls)

        h.script(Step(turn_stream("turn two answer", "sess-cold")))
        st = h.mod.one_turn(m, ALPHA, 2, "fake/model", 30)
        assert st == "BLOCKED_BY_INFRASTRUCTURE", st
        assert len(h.calls) == spent, "a cold turn 2 was spent"
        rec = m["scenarios"][ALPHA]
        assert rec["status"] != "AWAITING_GRADE", rec["status"]
        assert not answer_file(h, ALPHA, 2).exists(), "a cold turn 2 wrote an answer"
        assert "turn2" not in rec["turns"], rec["turns"]
        assert "session id" in (rec["error"] or ""), rec["error"]
        # Turn 1's collected answer is untouched. A cold turn 2 is not a reason to throw
        # away a request that was already spent.
        assert answer_file(h, ALPHA, 1).read_text(encoding="utf-8") == "turn one answer"


@case("a cold turn 2 is terminal, because turn 1 has to be rerun to fix it")
def _():
    with tempfile.TemporaryDirectory(prefix="apigee-genout-") as d:
        h = harness(Path(d))
        m = h.manifest([ALPHA])
        h.script(Step(sessionless_stream("turn one answer")))
        assert h.mod.one_turn(m, ALPHA, 1, "fake/model", 30) == "TURN1_COMPLETE"
        assert h.mod.one_turn(m, ALPHA, 2, "fake/model", 30) == "BLOCKED_BY_INFRASTRUCTURE"
        spent = len(h.calls)

        # The next window does not turn up the session id turn 1 failed to yield, so
        # re-queueing this scenario would spend a request to arrive at the same place.
        h.next_window()
        assert h.run_main("--only", ALPHA) == 0, h.err
        assert len(h.calls) == spent, "a scenario with no session id was retried"
        assert blocked_kind(h, m, ALPHA) == harness_kind(h, "BLOCK_TERMINAL"), \
            blocked_kind(h, m, ALPHA)


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