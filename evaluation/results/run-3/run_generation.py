#!/usr/bin/env python3
"""Run 3 answer generation. Resumable, budget-capped, manifest-backed.

Design notes, so this is not mistaken for a parallel evaluation system:

  * It reuses `tests/make_eval_workspace.py` to build the isolated workspace and
    `evaluation/packets/*.prompt.md` as the prompts. It invents neither.
  * Every request goes through the free OpenRouter route named in the protocol. There is
    no paid fallback in this file, by design. If the quota is gone the run stops.
  * The manifest is the authority on what has been collected. `--list` prints the state
    without spending anything, which is the first thing a resuming session should run.

Budget rules enforced here, not just documented:

  * `MAX_ATTEMPTS` caps request attempts inside one 05:30-to-05:29 IST quota window.
  * A 429 stops the window. It is never retried, and no alternate route is attempted.
  * At most one retry, and only for a non-quota transient failure.

Execution path: one `opencode run` per turn, in the isolated workspace, with the turn's
prompt file passed as the prompt. The workspace carries an `opencode.jsonc` denying
external_directory, shell, edit, webfetch, websearch and subagent, so the model has the
skill available and no route to an answer key.

Resumption, because 206 generation requests against 45 per window cannot finish in one
session and WORKING-STATE.md says each session adds a batch, checkpoints and stops. What
was resumable before: the window counter, and nothing else. `todo` selected
`status == "NOT_STARTED"`, and every path that stops a scenario writes some other status,
so a scenario the quota blocked at 23:00 on Tuesday was never offered again, and
`run_generation.py` answered "nothing pending in this selection" and exited 0. A run
interrupted between turn 1 and turn 2 left TURN1_COMPLETE, which was equally invisible.
`scenario_ws` was checked only at build time and `ws_path` keys on the scenario id alone,
so a workspace from one checkout or branch was reused verbatim by another.

The rule now in `pending_turn`:

  * A scenario is resumable when it owes a turn: NOT_STARTED owes turn 1, TURN1_COMPLETE
    owes turn 2, and a window-blocked scenario owes whatever it had not recorded yet.
  * A window block is recoverable and is retried. Quota exhaustion and the 45-attempt cap
    are per-WINDOW conditions by the protocol's own wording, so the next window re-queues
    the scenario. The retry is bounded without needing a counter of its own: every window
    block also closes the window, `main` refuses to start a batch in a closed window, and
    `one_turn` re-checks before spending, so one scenario is offered at most once per
    window and a full window costs at most MAX_ATTEMPTS requests either way.
  * A terminal block is not retried. A workspace that will not build, and a turn that spent
    its one retry and still produced no answer, need a decision from whoever resumes the
    run. Retrying them on a timer would spend the budget re-proving a known failure.
  * AWAITING_GRADE, GRADED and UNSCORABLE are terminal. Their scenario is done.

Workspace invariants, because breaking one of these makes a run look complete when it is
not:

  * `ws_path` is the only mapping from a selection to a workspace directory, and the
    directory `opencode run` executes in is the one the builder was told to build.
  * A scenario's workspace is keyed on that scenario alone, so it is identical for turn 1
    and turn 2 and identical whether the run is the full suite or narrowed with `--only`.
    Resuming finds the workspace the earlier attempt used.
  * A workspace is checked against the scenario it is for, by reading the workspace's own
    MANIFEST.json, before any request is spent.
  * That check is made on every use, not only at build time, and it verifies the material,
    not just the directory. The recorded `skill_dir_sha256` and `permission_config_sha256`
    are recomputed from the workspace and compared against the tree this run is running
    from. A directory whose enforcement config has been emptied, or whose skill files have
    been swapped, is refused rather than used: `opencode.jsonc` denying every route out of
    the tree is the isolation this protocol rests on, and a model answering inside a
    workspace where it was removed has produced an answer that cannot be trusted.
  * A workspace that cannot be built, or does not match, is recorded as
    BLOCKED_BY_INFRASTRUCTURE with a `workspace unusable:` error. It is never recorded as
    a completed turn, and never surfaces as a bare traceback from a missing `cwd`.
  * An unknown scenario id is rejected before a workspace is chosen.

Outcome invariants, for the same reason. A provider error must never be able to reach
`raw/<sid>.turn<N>.md`, because `grade_run.py` selects every scenario the manifest marks
`AWAITING_GRADE` and a grader reads those files:

  * A provider error's message is never answer text. `parse_events` returns it separately
    and does not append it to the assistant text, so an error event cannot satisfy the
    "did the model answer" test however the stream is shaped.
  * A turn is complete only when the CLI said so. `opencode run --format json` closes a
    step with a `step_finish` event, and its failure path can exit 0 having emitted text
    and nothing else: a provider stream that ends unexpectedly is swallowed in that
    compatibility mode, so neither the exit code nor the presence of prose proves the
    answer finished. Missing the completion event is a failure, not an answer.
  * A line the stream cannot parse is a failure, not a shrug. `--format json` writes one
    JSON object per line and nothing else to stdout, so a malformed non-blank line is a
    truncated or corrupted stream, and the count is recorded with the attempt.
  * One predicate decides whether an attempt produced an answer, and the retry branch and
    the give-up branch both use it. Whatever earns a retry is therefore caught if the
    retry also fails, instead of falling through to OK.
  * Every request that was spent is recorded with the status it actually got, including
    the one that earns the retry.
  * Only the OK branch writes an answer artifact. An exhausted retry records
    BLOCKED_BY_INFRASTRUCTURE and leaves no `raw/<sid>.turn<N>.md` behind.
  * A mistake made before any request is spent is terminal, not retried: an unreadable
    prompt packet, and a binary that cannot be run at all.
  * Turn 2 is not run at all without the session id that carries turn 1's conversation.
    The alternative was reachable and quiet: turn 1's stream yields no sessionID, the
    `--session` flag is skipped, `opencode run` opens a fresh conversation, and the
    turn-2 packet is answered by a model that has never seen the ticket it replies to.
    That lands in AWAITING_GRADE and is graded as though context carried within the
    scenario. Refused before the request, because a cold turn 2 cannot be detected as
    cold after the fact except by noticing a null session_id nobody was required to check.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import NamedTuple, NotRequired, TypedDict, cast

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "evaluation" / "results" / "run-3"
RAW = RUN / "raw"
# Scoped to this checkout. The root used to be the fixed /tmp/apigee-run3 while ws_path
# keys on the scenario id alone, so every checkout and every branch resolved a scenario to
# the same directory and could run the model inside a tree built from a different one's
# skills. verify_material now refuses such a workspace, but a path that cannot collide does
# not need refusing. APIGEE_EVAL_WS_ROOT still overrides it.
WS_ROOT = Path(os.environ.get("APIGEE_EVAL_WS_ROOT", "/tmp/apigee-run3-"
                              + hashlib.sha256(str(ROOT).encode()).hexdigest()[:8]))
MANIFEST = RUN / "manifest.json"

# Protocol budget: 45 attempts per quota window, five below the reported 50.
MAX_ATTEMPTS = 45
# The provider's daily quota window opens at 05:30 IST. Every reported X-RateLimit-Reset
# instant has been that boundary (2026-10-14 05:30 IST was 1791936000), but the window
# recurs daily, so the boundary is what the keys are computed from and a single reported
# timestamp is kept here as provenance, not as the thing that decides a window.
QUOTA_WINDOW_OPEN_HOUR = 5
QUOTA_WINDOW_OPEN_MINUTE = 30
QUOTA_RESET_UTC = 1791936000  # 2026-10-14 05:30 IST, as reported by X-RateLimit-Reset
QUOTA_ERRORS = ("rate-limit", "rate limit", "free-models-per-day", "quota",
                "free tier can only be used")

# How the CLI says a step finished, in `--format json`: `{"type":"step_finish", "part":
# {"type":"step-finish", ...}}`. Both spellings are accepted because the event and the
# part inside it differ, and a completeness rule must not depend on which one a version
# happens to emit.
COMPLETION_TYPES = frozenset({"step_finish", "step-finish"})

STATUSES = ["NOT_STARTED", "TURN1_COMPLETE", "TURN2_COMPLETE", "AWAITING_GRADE",
            "GRADED", "UNSCORABLE", "BLOCKED_BY_INFRASTRUCTURE"]

# BLOCKED_BY_INFRASTRUCTURE is one status but two situations, and only one of them clears
# itself. Both are recorded with the same status, because a blocked scenario must stay
# blocked as far as the grader is concerned and PROTOCOL.md counts "infra-blocked" as one
# evaluability class; `block_kind` says which it was, so a resuming run does not have to
# guess from the error string.
BLOCK_WINDOW = "WINDOW"      # a closed quota window: a 429, or the 45-attempt cap. Per
                             # WINDOW by the protocol, so the next window re-queues it.
BLOCK_TERMINAL = "TERMINAL"  # an unusable workspace, or a turn that spent its one retry
                             # and still produced no answer. Needs a human decision; a
                             # timer would only re-spend the budget on a known failure.


class Turn(TypedDict):
    at: str
    model: str
    session_id: str | None
    prompt_sha256: str
    response_sha256: str
    chars: int
    raw: str
    attempts: int


class Request(TypedDict):
    sid: str
    turn: int
    attempt: int
    at: str
    status: str | None
    error_type: str | None


class BudgetWindow(TypedDict):
    attempts: int
    quota_exhausted: bool
    requests: list[Request]


class Budget(TypedDict):
    max_attempts_per_window: int
    windows: dict[str, BudgetWindow]


class Scenario(TypedDict):
    status: str
    turns: dict[str, Turn]
    attempts: int
    error: str | None
    # Written by `block`, read by `pending_turn` and by --list, and popped again by the
    # branch that collects the turn. NotRequired because a manifest written before this
    # field existed has none, which --list reads as needing a decision.
    block_kind: NotRequired[str]


class Manifest(TypedDict):
    run: str
    protocol: str
    created: str
    model: str | None
    budget: Budget
    scenarios: dict[str, Scenario]


class ResponseEntry(TypedDict):
    turn: int
    attempt: int
    at: str
    exit: int
    seconds: float
    error_type: str | None
    prompt_sha256: str
    bytes_out: int
    completed: bool
    malformed_lines: int
    status: NotRequired[str]
    error: NotRequired[str]


class Stream(NamedTuple):
    """What one attempt's event stream actually said.

    `completed` is the field the exit code cannot supply: the CLI closes a step with
    `step_finish`, and a provider stream that ends unexpectedly can leave the process
    exiting 0 with text and no closing event at all. `malformed` counts the non-blank
    lines that were not JSON, which in `--format json` mode is a truncated stream rather
    than noise.
    """
    text: str
    error_type: str | None
    error_message: str | None
    session_id: str | None
    completed: bool
    malformed: int


class EventPart(TypedDict, total=False):
    type: str
    text: str


class EventError(TypedDict, total=False):
    type: str
    message: str


class Event(TypedDict, total=False):
    sessionID: str
    type: str
    part: EventPart
    error: EventError


class Args(argparse.Namespace):
    list: bool = False
    model: str = "openrouter/nvidia/nemotron-3-ultra-550b-a55b:free"
    batch: int = 5
    timeout: int = 600
    only: list[str] = []


def scenarios() -> list[str]:
    """Every scenario ID, in suite order, from the generated turn-one packets."""
    return sorted(p.name[:-len(".prompt.md")]
                  for p in (ROOT / "evaluation" / "packets").glob("*.prompt.md")
                  if not p.name.endswith(".turn2.prompt.md"))


def now_ist() -> datetime:
    return datetime.now(timezone(timedelta(hours=5, minutes=30)))


def window_start(d: datetime) -> datetime:
    """The 05:30 IST instant that opened the window `d` is spending from.

    Keyed by the window's start rather than by the calendar day, because the quota is
    not. The old key was `d.strftime("%Y-%m-%d ...")`, so a run at 04:00 IST on the
    fifteenth was filed under a fresh window that the provider would not open for another
    hour and a half: the day's 45 attempts had already been spent by midnight and the
    counter started again anyway.
    """
    opened = d.replace(hour=QUOTA_WINDOW_OPEN_HOUR, minute=QUOTA_WINDOW_OPEN_MINUTE,
                       second=0, microsecond=0)
    return opened - timedelta(days=1) if d < opened else opened


def window_key(d: datetime) -> str:
    return window_start(d).strftime("%Y-%m-%d 05:30->05:29 IST")


def load() -> Manifest:
    if MANIFEST.exists():
        return cast("Manifest", json.loads(MANIFEST.read_text(encoding="utf-8")))
    m: Manifest = {
        "run": "run-3",
        "protocol": "evaluation/results/run-3/PROTOCOL.md",
        "created": now_ist().isoformat(),
        "model": None,
        "budget": {"max_attempts_per_window": MAX_ATTEMPTS,
                   "windows": {}},
        "scenarios": {sid: {"status": "NOT_STARTED", "turns": {}, "attempts": 0,
                            "error": None} for sid in scenarios()},
    }
    # Written immediately so grade_run.py --list and any resuming session see the full
    # scenario roster before the first request. Creating it costs zero requests.
    save(m)
    return m


def save(m: Manifest) -> None:
    RUN.mkdir(parents=True, exist_ok=True)
    tmp = MANIFEST.with_suffix(".json.tmp")
    _ = tmp.write_text(json.dumps(m, indent=2) + "\n", encoding="utf-8")
    _ = tmp.replace(MANIFEST)


def window(m: Manifest) -> BudgetWindow:
    k = window_key(now_ist())
    return m["budget"]["windows"].setdefault(
        k, {"attempts": 0, "quota_exhausted": False, "requests": []})


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def block(m: Manifest, rec: Scenario, kind: str, error: str) -> str:
    """Record a scenario as blocked and say whether the next window may retry it.

    Every blocking path goes through here so that `block_kind` cannot be forgotten on one
    of them. The distinction is the whole of R1: without it there was one way to be
    blocked, and it was terminal, so a 429 at 23:00 cost the scenario the rest of the run.
    """
    rec["status"] = "BLOCKED_BY_INFRASTRUCTURE"
    rec["block_kind"] = kind
    rec["error"] = error
    save(m)
    return rec["status"]


def pending_turn(rec: Scenario) -> int | None:
    """The turn this scenario still owes, or None when nothing further can be done to it.

    The one place that decides whether a scenario is resumable, so `main` and `--list`
    cannot disagree about what a resuming run will do.

    This used to be `status == "NOT_STARTED"`, which excluded every state a run can stop
    in and so excluded every scenario a stopped run had anything left to say. The states
    split three ways:

      * it owes a turn. NOT_STARTED owes turn 1, TURN1_COMPLETE owes turn 2, and a
        window-blocked scenario owes whichever of the two it has not recorded.
      * a terminal block. The scenario needs a decision, and a timer would only re-spend
        the budget confirming the failure.
      * it is finished. AWAITING_GRADE, GRADED, UNSCORABLE and anything not named above.
    """
    status = rec.get("status")
    turns = rec.get("turns") or {}
    if status == "NOT_STARTED":
        return 1
    if status == "TURN1_COMPLETE":
        return 2
    if status == "BLOCKED_BY_INFRASTRUCTURE" and rec.get("block_kind") == BLOCK_WINDOW:
        # The turn is read off the record rather than off a remembered status, so a
        # scenario the quota blocked during turn 2 comes back for turn 2 and not turn 1.
        # Re-running turn 1 would spend a second request on an answer already collected.
        return 2 if "turn1" in turns else 1
    return None


def parse_events(raw: str) -> Stream:
    """Read one `opencode run --format json` stream.

    The session id comes from the event stream. It is what makes turn 2 continue the
    turn-1 conversation instead of starting over.

    A provider error's message is returned as `error_message` and is never appended to
    `text`. Appending it made an error event look like a delivered answer, which is how a
    401 body once reached `raw/*.turn1.md` as though the model had written it. The message
    stays available for the quota scan and for the recorded error; the answer text stays
    text the model actually produced.

    Two more things are reported rather than inferred. `completed` is true only when the
    stream carried the CLI's closing `step_finish` event, because a stream cut short can
    still exit 0 with the prose it managed to emit. `malformed` counts non-blank lines
    that were not JSON: this format writes one object per line and nothing else to
    stdout, so such a line is a truncated or corrupted stream, not decoration.
    """
    text: list[str] = []
    etype: str | None = None
    emsg: str | None = None
    sid: str | None = None
    completed = False
    malformed = 0
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        if not isinstance(d, dict):
            malformed += 1
            continue
        event = cast("Event", d)
        if event.get("sessionID") and not sid:
            sid = str(event.get("sessionID"))
        kind = str(event.get("type") or "")
        part: EventPart = event.get("part") or {}
        part_kind = str(part.get("type") or "")
        # Named both ways on purpose: the CLI writes `step_finish` for the event and
        # `step-finish` for the part inside it, and which one is read should not depend on
        # the version that produced the stream.
        if kind in COMPLETION_TYPES or part_kind in COMPLETION_TYPES:
            completed = True
        if kind == "text" and part_kind == "text":
            text.append(part.get("text", ""))
        if kind == "error":
            err: EventError = event.get("error") or {}
            etype = str(err.get("type") or "error")
            emsg = str(err.get("message") or "")
    return Stream("\n".join(t for t in text if t.strip()), etype, emsg, sid,
                  completed, malformed)


class WorkspaceError(RuntimeError):
    """The isolated workspace could not be built, or is not the one the scenario needs.

    Raised instead of letting the problem surface later as an OS error from `opencode run`
    with a `cwd` that does not exist.
    """


def ws_path(ids: list[str]) -> Path:
    """The one mapping from a scenario selection to its workspace directory.

    Every caller goes through this. The path used to be computed twice: once here over
    the ids handed to `build_ws`, and once in `one_turn` over the whole manifest roster.
    The two never agreed, `build_ws` returned the directory it had actually built, and
    `one_turn` threw that return value away, so the harness built one directory and then
    ran the model in another. The ids are sorted so the mapping is a function of the set
    and not of the order a caller happened to pass them in.

    The default root also carries this checkout's identity. The path was a fixed
    /tmp/apigee-run3 while the only key was the scenario id, so two checkouts, or two
    branches, resolved a scenario to the same directory and the second one ran the model
    inside a tree built from the first one's skills. The digests below now refuse that
    workspace outright; scoping the root stops the collision from arising at all, and
    leaves `verify_material` as the check that catches material moving under a live path.
    """
    return WS_ROOT / ("ws-" + hashlib.sha256("|".join(sorted(ids)).encode()).hexdigest()[:10])


def build_ws(ids: list[str]) -> Path:
    out = ws_path(ids)
    args = [x for i in ids for x in ("--scenario", i)]
    try:
        _ = subprocess.run([sys.executable, "tests/make_eval_workspace.py", "--out", str(out),
                            "--force", *args], cwd=ROOT, check=True)
    except subprocess.CalledProcessError as e:
        # make_eval_workspace exits 1 both when a packet is missing and when it finds
        # answer material in the tree. Either way it is a workspace problem, not a
        # provider one, and it must not look like a model failure.
        raise WorkspaceError(f"builder exited {e.returncode} for {' '.join(ids)}") from e
    except OSError as e:
        raise WorkspaceError(f"builder could not be run for {' '.join(ids)}: {e}") from e
    return out


def _skill_digest(d: Path) -> str:
    """sha256 over a skills tree, matching tests/make_eval_workspace.py's `dir_digest`.

    Restated rather than imported so the same function can digest the repository tree and a
    built workspace and have the two numbers mean the same thing. The builder's copytree
    drops __pycache__ and *.pyc, so they are dropped here too. If this ever stopped
    agreeing with the builder, the workspace would fail its own manifest and every scenario
    would block, which is the direction that failure has to point: a stale digest function
    must stop the run, not quietly pass everything it is asked to check.
    """
    h = hashlib.sha256()
    if not d.is_dir():
        return h.hexdigest()[:16]
    for p in sorted(d.rglob("*")):
        rel = p.relative_to(d)
        if "__pycache__" in rel.parts or p.suffix == ".pyc":
            continue
        if p.is_file():
            h.update(rel.as_posix().encode())
            h.update(p.read_bytes())
    return h.hexdigest()[:16]


def _expected_permissions() -> list[dict[str, str]]:
    """The permission rules the builder writes, read out of the builder itself.

    Imported, not restated. These rules are the isolation this run rests on, and a second
    copy of the list in this file would be a second thing able to disagree with the
    artifact it claims to verify. If the builder cannot be loaded the caller turns that
    into a WorkspaceError: a check that could not run must never read as one that passed.
    """
    path = ROOT / "tests" / "make_eval_workspace.py"
    try:
        spec = importlib.util.spec_from_file_location("make_eval_workspace_under_test", path)
        if spec is None or spec.loader is None:
            raise ImportError(f"no loader for {path}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except (OSError, ImportError, SyntaxError) as e:
        raise WorkspaceError(f"cannot read the builder's permission rules from {path}: {e}") from e
    perms = getattr(mod, "PERMISSIONS", None)
    if not isinstance(perms, list) or not perms:
        raise WorkspaceError(f"{path} defines no PERMISSIONS to check a workspace against")
    return perms


def verify_material(ws: Path, built: dict) -> None:
    """Refuse a workspace whose material is not the material this run is running.

    Two checks, because either one alone has a hole. Recomputing the recorded digests from
    the workspace itself catches an edit that left MANIFEST.json alone; comparing the
    recorded digests against the tree this run is running from catches an edit that
    rewrote MANIFEST.json to match. An emptied `opencode.jsonc` is also compared rule by
    rule against the builder's own PERMISSIONS, which needs no stored digest to trust.

    This is not paranoia about the builder. `scenario_ws` used to check only that the
    directory existed, that no packet was missing and that the scenario id was in the list,
    and it checked those only at build time. A workspace built once and then emptied of its
    deny rules, or given a different skill, was handed to `opencode run` unchanged, and the
    turn came back TURN1_COMPLETE with no isolation and no record that any had been lost.

    Blocked rather than rebuilt, deliberately. The harness cannot rebuild its way out of
    this safely: a scenario whose turn 1 was collected inside that workspace would then
    answer turn 2 against different material, and PROTOCOL.md says mixing material
    versions inside one result is worse than an incomplete run. So each message says what
    to do about it, and leaves the deciding to a human: delete the directory, or point
    APIGEE_EVAL_WS_ROOT at a fresh one.
    """
    skills, cfg = ws / ".agents/skills", ws / "opencode.jsonc"
    want_skill = built.get("skill_dir_sha256")
    want_perm = built.get("permission_config_sha256")
    how = f"delete {ws} to rebuild it, or point APIGEE_EVAL_WS_ROOT elsewhere"

    if not skills.is_dir() or not cfg.is_file():
        raise WorkspaceError(
            f"{ws} is missing the isolation material ({skills}, {cfg}); {how}")
    if not want_skill or not want_perm:
        raise WorkspaceError(
            f"{ws}/MANIFEST.json records no skill_dir_sha256 or permission_config_sha256, "
            f"so its contents cannot be checked against this tree; {how}")

    got_skill = _skill_digest(skills)
    if got_skill != want_skill:
        raise WorkspaceError(
            f"{ws} holds skills digest {got_skill} but its MANIFEST.json records "
            f"{want_skill}: the workspace was changed after it was built; {how}")
    got_perm = hashlib.sha256(cfg.read_bytes()).hexdigest()[:16]
    if got_perm != want_perm:
        raise WorkspaceError(
            f"{ws}/opencode.jsonc is digest {got_perm} but its MANIFEST.json records "
            f"{want_perm}: the enforcement config was changed after the workspace was "
            f"built; {how}")

    source_skill = _skill_digest(ROOT / ".agents/skills")
    if want_skill != source_skill:
        raise WorkspaceError(
            f"{ws} was built from skills digest {want_skill} but this tree is now "
            f"{source_skill}; the two are different runs' material and are not "
            f"interchangeable; {how}")

    try:
        got_perms = (json.loads(cfg.read_text(encoding="utf-8")) or {}).get("permissions")
    except (OSError, ValueError) as e:
        raise WorkspaceError(f"{cfg} is unreadable: {e}; {how}") from e
    expected = _expected_permissions()
    if got_perms != expected:
        raise WorkspaceError(
            f"{cfg} does not carry the isolation the builder writes ({len(got_perms or [])} "
            f"rules against {len(expected)}); a model run here could read outside it; {how}")


def scenario_ws(sid: str) -> Path:
    """The workspace `sid` runs in: built if absent, then checked against `sid`.

    A scenario's workspace is keyed on that scenario alone, so it is the same for turn 1
    and turn 2, and the same whether the run was started as the full suite or narrowed
    with `--only`. A resumed run therefore finds the workspace the earlier attempt used.

    The check reads the workspace's own MANIFEST.json rather than trusting that a
    directory exists: a directory left behind by an interrupted build can exist without
    the packet copies this scenario needs. It also verifies what is inside the directory,
    because a resumed run is exactly when a workspace has had time to change underneath
    the manifest. The digests the builder recorded were only ever written, never read.
    """
    ws = ws_path([sid])
    if not (ws / "MANIFEST.json").exists():
        ws = build_ws([sid])
    mf = ws / "MANIFEST.json"
    if not mf.is_file():
        raise WorkspaceError(f"{ws} has no MANIFEST.json after the builder reported success")
    # Written by tests/make_eval_workspace.py. `missing_packets` names any packet the builder
    # could not copy, so a workspace that lists one is not one this scenario can run.
    try:
        built = json.loads(mf.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise WorkspaceError(f"{mf} is unreadable: {e}") from e
    missing = built.get("missing_packets") or []
    if missing:
        raise WorkspaceError(f"{ws} is missing packets: {', '.join(missing)}")
    if sid not in (built.get("scenarios") or []):
        raise WorkspaceError(f"{ws} was built for {built.get('scenarios')}, not {sid}")
    verify_material(ws, built)
    return ws


def one_turn(m: Manifest, sid: str, turn: int, model: str, timeout: int) -> str:
    """Run one turn. Returns the new scenario status."""
    rec = m["scenarios"][sid]
    win = window(m)
    suffix = "" if turn == 1 else ".turn2"
    packet = ROOT / "evaluation" / "packets" / f"{sid}{suffix}.prompt.md"
    try:
        prompt = packet.read_text(encoding="utf-8")
    except OSError as e:
        # A packet that cannot be read is a repository fault, not a provider one, and the
        # retry rule is for the provider. Left as an exception it ended the whole batch
        # with a traceback and a partly written manifest; recorded here the scenario says
        # what is missing and the rest of the batch still runs.
        return block(m, rec, BLOCK_TERMINAL,
                     f"prompt packet {packet.name} is unreadable: {e}")

    try:
        ws = scenario_ws(sid)
    except WorkspaceError as e:
        # A local orchestration failure. It is not a model failure and not a quota
        # failure, and recording it as anything other than blocked would let an
        # incomplete scenario read as a completed evaluation. Terminal: nothing about the
        # next window changes a workspace whose material does not match this tree.
        return block(m, rec, BLOCK_TERMINAL, f"workspace unusable: {e}")

    # Carried across the two turns of one scenario so turn 2 continues the conversation.
    turn1 = rec.get("turns", {}).get("turn1")
    session_id: str | None = turn1.get("session_id") if turn1 else None
    if turn == 2 and not session_id:
        # Turn 1 completed without a session id, so there is no conversation to continue
        # and `opencode run` would open a fresh one. PROTOCOL.md requires turn 2 to run in
        # the same conversation as turn 1; the turn-2 packet answers a customer reply to a
        # ticket the model has not seen, and grading it would score a scenario the run
        # never held. Refused here, before the request, rather than graded and detected
        # afterwards by a null session_id nobody has to look at.
        #
        # Terminal, and deliberately not re-run from turn 1: turn 1 already cost a request
        # and its answer is on disk, so discarding it to try again would spend a second one
        # on a guess. The scenario needs a human to clear `turns` and start it over.
        return block(m, rec, BLOCK_TERMINAL,
                     "turn 2 needs turn 1's session id to continue the conversation and "
                     "turn 1 recorded none; clear this scenario's turns and rerun turn 1")

    attempt = 0
    while attempt <= 1:  # one retry, never on a quota error
        if win.get("quota_exhausted"):
            return block(m, rec, BLOCK_WINDOW,
                         f"quota window {window_key(now_ist())} already closed by a "
                         f"provider 429; not retried by rule")
        if win["attempts"] >= MAX_ATTEMPTS:
            win["quota_exhausted"] = True
            return block(m, rec, BLOCK_WINDOW,
                         f"budget cap {MAX_ATTEMPTS} reached for {window_key(now_ist())}")

        win["attempts"] += 1
        rec["attempts"] += 1
        attempt += 1
        ts = now_ist().isoformat()
        started = time.time()
        spawn_error: str | None = None
        try:
            # Turn 2 must continue the SAME session as turn 1. Without --session,
            # `opencode run` starts a fresh conversation each time, so the scenario's own
            # two-turn design collapses: the turn-2 packet says "the customer has replied"
            # to a ticket the model has never seen, and it would score the evidence cold.
            # The guard above makes `session_id` a precondition of reaching this line, so
            # this is no longer "add the flag when there is one to add".
            cmd = ["opencode", "run", "--auto", "--model", model, "--format", "json"]
            if turn == 2:
                cmd += ["--session", session_id]
            cmd.append(prompt)
            proc = subprocess.run(
                cmd, cwd=ws, capture_output=True, text=True, timeout=timeout)
            out, err, rc = proc.stdout, proc.stderr, proc.returncode
        except subprocess.TimeoutExpired:
            out, err, rc = "", "TIMEOUT", -1
        except OSError as e:
            # A binary that is missing or cannot be executed is not a transient provider
            # failure, so it does not earn the retry: the second attempt fails identically
            # and the run would report two requests spent on a mistake made before either.
            out, err, rc = "", f"could not run opencode: {e}", 127
            spawn_error = f"could not run opencode: {e}"

        stream = parse_events(out)
        text, etype, emsg, got_sid = (
            stream.text, stream.error_type, stream.error_message, stream.session_id)
        if got_sid and not session_id:
            session_id = got_sid
        RAW.mkdir(parents=True, exist_ok=True)
        _ = (RAW / f"{sid}.turn{turn}.attempt{attempt}.jsonl").write_text(
            out, encoding="utf-8")
        if err:
            _ = (RAW / f"{sid}.turn{turn}.attempt{attempt}.stderr").write_text(
                err, encoding="utf-8")

        entry: ResponseEntry = {"turn": turn, "attempt": attempt, "at": ts,
                                "exit": rc, "seconds": round(time.time() - started, 1),
                                "error_type": etype, "prompt_sha256": sha(packet),
                                "bytes_out": len(text),
                                "completed": stream.completed,
                                "malformed_lines": stream.malformed}
        win["requests"].append({"sid": sid, "turn": turn, "attempt": attempt,
                                "at": ts, "status": None, "error_type": etype})

        blob = f"{etype} {emsg}".lower()
        if any(q in blob for q in QUOTA_ERRORS) or rc == 429:
            entry["status"] = "QUOTA_EXHAUSTED"
            entry["error"] = "quota exhausted; window closed, no retry"
            win["quota_exhausted"] = True
            win["requests"][-1]["status"] = "QUOTA_EXHAUSTED"
            # Window-scoped, so the next window offers this scenario again. It was not
            # retried here and it is not retried for the rest of this window; the counter
            # above has been closed, so there is nothing left to spend it on.
            return block(m, rec, BLOCK_WINDOW,
                         "provider quota exhausted (429); not retried by rule")

        # One predicate, used by both branches below. They used to test different things:
        # the retry branch `etype or rc == -1 or not text`, the give-up branch only
        # `not text`. An error event carrying text satisfied the second test and not the
        # first, so on the retry it satisfied neither and fell through to OK, writing the
        # provider's error message as the answer. Sharing the predicate closes that path.
        #
        # The exit code is tested as `rc != 0`, not as `rc == -1`. -1 is this harness's
        # own sentinel for a TimeoutExpired, and testing for it alone accepted every
        # other nonzero exit as an answer. That is the same defect by another route: a
        # provider that dies partway through still leaves the text it managed to emit in
        # the event stream, so a stream that is not empty says nothing about whether the
        # turn finished. A truncated answer written to raw/<sid>.turn1.md is graded
        # exactly like a whole one.
        #
        # `not stream.completed` closes the last version of that same hole, the one no
        # exit code covers. The CLI closes a step with `step_finish`, and its provider
        # failure path can exit 0 having emitted prose and no closing event at all, so
        # "rc == 0 and there is text" is exactly the shape a truncated answer takes.
        # `stream.malformed` closes the same hole from the other side: this format writes
        # one JSON object per line and nothing else to stdout, so a line that is not JSON
        # is a stream that was cut or corrupted mid-write.
        failed = (spawn_error is not None or bool(etype) or rc != 0 or not text.strip()
                  or not stream.completed or bool(stream.malformed))

        if failed and attempt == 1 and spawn_error is None:
            entry["status"] = "RETRY_ONCE"
            win["requests"][-1]["status"] = "RETRY_ONCE"
            save(m)
            continue

        if failed:
            entry["status"] = "NO_ANSWER"
            why = spawn_error or emsg or etype or (err.strip()[:200] if err else "")
            if stream.malformed:
                # Named before the exit code: when both are true, a corrupt stream is the
                # more informative reason, and the exit code is appended under it.
                why = (f"{stream.malformed} line(s) of the event stream were not valid JSON"
                       + (f"; {why}" if why else ""))
            elif not stream.completed and not etype and rc == 0:
                why = (why or "") + ("; " if why else "") + (
                    "the provider exited 0 but never reported the step as finished, "
                    "so this stream cannot be shown to be a complete answer")
            if rc != 0 and not (emsg or etype):
                # The exit code is the only thing that went wrong, so name it. Falling
                # through to "empty response" described a turn that returned text as one
                # that returned none, which is the kind of wrong reason that costs an
                # afternoon.
                why = f"opencode run exited {rc}" + (f": {why}" if why else "")
            entry["error"] = why or "empty response"
            win["requests"][-1]["status"] = "NO_ANSWER"
            # Terminal. The quota window is not why this failed and the next window
            # changes nothing about it, so re-queueing would buy a second and third
            # identical answer for the same broken turn.
            return block(m, rec, BLOCK_TERMINAL, entry["error"])

        entry["status"] = "OK"
        win["requests"][-1]["status"] = "OK"
        rec["turns"][f"turn{turn}"] = {
            "at": ts, "model": model, "session_id": got_sid or session_id,
            "prompt_sha256": entry["prompt_sha256"],
            "response_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "chars": len(text), "raw": f"raw/{sid}.turn{turn}.attempt{attempt}.jsonl",
            "attempts": attempt}
        _ = (RAW / f"{sid}.turn{turn}.md").write_text(text, encoding="utf-8")
        rec["status"] = "TURN1_COMPLETE" if turn == 1 else "TURN2_COMPLETE"
        if turn == 2:
            rec["status"] = "AWAITING_GRADE"
        # Cleared on the way through. A scenario the quota blocked in one window and
        # collected in the next carried the old block_kind and the old error forever, and
        # --list counts on block_kind to say what will resume.
        rec.pop("block_kind", None)
        rec["error"] = None
        save(m)
        return rec["status"]

    # Unreachable while the loop only ever continues on `RETRY_ONCE`, and the next
    # iteration returns or exits. Kept because a status left unset here would read as the
    # scenario's previous status, which is how a half-finished turn reads as a finished one.
    return block(m, rec, BLOCK_TERMINAL, "turn ended without an outcome")


def main() -> int:
    ap = argparse.ArgumentParser()
    _ = ap.add_argument("--list", action="store_true",
                        help="print progress, spend nothing")
    _ = ap.add_argument("--model",
                        default="openrouter/nvidia/nemotron-3-ultra-550b-a55b:free")
    _ = ap.add_argument("--batch", type=int, default=5)
    _ = ap.add_argument("--timeout", type=int, default=600)
    _ = ap.add_argument("--only", action="append", default=[])
    a = ap.parse_args(namespace=Args())

    m = load()
    m["model"] = a.model
    ids = a.only or scenarios()

    # Reject an unknown id before any workspace is chosen. The roster in the manifest is
    # fixed when the manifest is first written, so a packet added after that point makes
    # a full run select an id the manifest has no record of. Failing here says which id
    # is wrong; falling through used to raise KeyError, and picking a workspace for an id
    # nobody vouched for is the failure this harness exists to avoid.
    unknown = [s for s in ids if s not in m["scenarios"]]
    if unknown:
        print("no such scenario in this run's manifest: " + ", ".join(unknown),
              file=sys.stderr)
        return 2

    if a.list:
        from collections import Counter
        c = Counter(r["status"] for r in m["scenarios"].values())
        print(f"run-3  {len(m['scenarios'])} scenarios  model {m['model']}")
        for k, v in sorted(c.items()):
            print(f"  {k:<28} {v}")
        # The one status worth splitting. BLOCKED_BY_INFRASTRUCTURE covers a closed quota
        # window, which the next window retries, and a workspace or a turn that failed for
        # good, which it does not. Printed because --list is the first thing a resuming
        # session runs and this is the line that says how much of the suite is coming back.
        # A block with no kind recorded at all is a manifest written before this field
        # existed, and reads as needing a decision, which is the safe direction to guess.
        kinds = Counter(r.get("block_kind") for r in m["scenarios"].values()
                        if r["status"] == "BLOCKED_BY_INFRASTRUCTURE")
        for kind, n in sorted(kinds.items(), key=lambda kv: str(kv[0])):
            print(f"    blocked, {kind}: {n} "
                  f"({'retried next window' if kind == BLOCK_WINDOW else 'needs a decision'})")
        for wk, w in m["budget"]["windows"].items():
            print(f"  window {wk}: {w['attempts']} attempts, "
+ f"quota_exhausted={w['quota_exhausted']}")
        # Counted the same way `todo` below is, so the two cannot disagree. This used to
        # count every scenario that was not AWAITING_GRADE, which included the ones already
        # graded and reported a suite with nothing to do as 40 pending.
        pend = [s for s in ids if pending_turn(m["scenarios"][s]) is not None]
        print(f"  pending in selection: {len(pend)}")
        return 0

    # The same predicate `pending_turn` gives `--list`, over every scenario the selection
    # can still collect. It selected `NOT_STARTED` alone, which is the whole of R1: a
    # scenario stopped at TURN1_COMPLETE or at a window block was not in this list, so a
    # second invocation in the same run printed "nothing pending" and exited 0 while the
    # suite was unfinished.
    todo = [s for s in ids if pending_turn(m["scenarios"][s]) is not None]
    if not todo:
        print("nothing pending in this selection")
        return 0

    # A closed window stops the run before a batch is chosen, not after one scenario has
    # been picked up and refused. Everything that closes a window also marks the scenario
    # that hit it window-blocked, so without this the scenario it blocked is offered again
    # on the next invocation of the same window and blocked again for having spent nothing.
    # After the todo test, because a run with nothing left to do should say so rather than
    # report a quota problem it was never going to act on.
    w0 = window(m)
    if w0["quota_exhausted"]:
        print(f"quota window {window_key(now_ist())} is closed "
              f"({w0['attempts']} attempts); nothing to spend it on. It reopens at the "
              f"next 05:30 IST boundary")
        return 0

    batch = todo[:a.batch]
    print(f"batch of {len(batch)}: {' '.join(batch)}")

    for sid in batch:
        turn = pending_turn(m["scenarios"][sid])
        if turn is None:
            continue
        st = one_turn(m, sid, turn, a.model, a.timeout)
        print(f"  {sid} turn{turn} -> {st}")
        if turn == 2:
            # Resuming at turn 2, so there is no turn 1 to pair it with and no way to tell a
            # blocked turn 2 from a completed one here. The window tells us; a terminal
            # block on one scenario is not a reason to strand the rest of the batch.
            if window(m)["quota_exhausted"]:
                print("quota exhausted; stopping this batch")
                break
            continue
        if st != "TURN1_COMPLETE":
            break
        st = one_turn(m, sid, 2, a.model, a.timeout)
        print(f"  {sid} turn2 -> {st}")
        if window(m)["quota_exhausted"]:
            print("quota exhausted; stopping this batch")
            break

    save(m)
    w = window(m)
    print(f"\nwindow {window_key(now_ist())}: {w['attempts']} attempts used "
          + f"(cap {MAX_ATTEMPTS}), quota_exhausted={w['quota_exhausted']}")
    from collections import Counter
    c = Counter(r["status"] for r in m["scenarios"].values())
    print("status: " + ", ".join(f"{k}={v}" for k, v in sorted(c.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())