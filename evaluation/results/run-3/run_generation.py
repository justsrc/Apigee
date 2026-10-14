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

Workspace invariants, because breaking one of these makes a run look complete when it is
not:

  * `ws_path` is the only mapping from a selection to a workspace directory, and the
    directory `opencode run` executes in is the one the builder was told to build.
  * A scenario's workspace is keyed on that scenario alone, so it is identical for turn 1
    and turn 2 and identical whether the run is the full suite or narrowed with `--only`.
    Resuming finds the workspace the earlier attempt used.
  * A workspace is checked against the scenario it is for, by reading the workspace's own
    MANIFEST.json, before any request is spent.
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
  * One predicate decides whether an attempt produced an answer, and the retry branch and
    the give-up branch both use it. Whatever earns a retry is therefore caught if the
    retry also fails, instead of falling through to OK.
  * Every request that was spent is recorded with the status it actually got, including
    the one that earns the retry.
  * Only the OK branch writes an answer artifact. An exhausted retry records
    BLOCKED_BY_INFRASTRUCTURE and leaves no `raw/<sid>.turn<N>.md` behind.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "evaluation" / "results" / "run-3"
RAW = RUN / "raw"
WS_ROOT = Path(os.environ.get("APIGEE_EVAL_WS_ROOT", "/tmp/apigee-run3"))
MANIFEST = RUN / "manifest.json"

# Protocol budget: 45 attempts per quota window, five below the reported 50.
MAX_ATTEMPTS = 45
QUOTA_RESET_UTC = 1791936000  # 2026-10-14 05:30 IST, as reported by X-RateLimit-Reset
QUOTA_ERRORS = ("rate-limit", "rate limit", "free-models-per-day", "quota",
                "free tier can only be used")

STATUSES = ["NOT_STARTED", "TURN1_COMPLETE", "TURN2_COMPLETE", "AWAITING_GRADE",
            "GRADED", "UNSCORABLE", "BLOCKED_BY_INFRASTRUCTURE"]


def scenarios() -> list[str]:
    """Every scenario ID, in suite order, from the generated turn-one packets."""
    return sorted(p.name[:-len(".prompt.md")]
                  for p in (ROOT / "evaluation" / "packets").glob("*.prompt.md")
                  if not p.name.endswith(".turn2.prompt.md"))


def now_ist() -> datetime:
    return datetime.now(timezone(timedelta(hours=5, minutes=30)))


def window_key(d: datetime) -> str:
    return d.strftime("%Y-%m-%d 05:30->05:29 IST")


def load() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    m = {
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


def save(m: dict) -> None:
    RUN.mkdir(parents=True, exist_ok=True)
    tmp = MANIFEST.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(m, indent=2) + "\n", encoding="utf-8")
    tmp.replace(MANIFEST)


def window(m: dict) -> dict:
    k = window_key(now_ist())
    return m["budget"]["windows"].setdefault(
        k, {"attempts": 0, "quota_exhausted": False, "requests": []})


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def parse_events(raw: str) -> tuple[str, str | None, str | None, str | None]:
    """Return (assistant text, error type, error message, session id).

    The session id comes from the event stream. It is what makes turn 2 continue the
    turn-1 conversation instead of starting over.

    A provider error's message is returned as `emsg` and is never appended to `text`.
    Appending it made an error event look like a delivered answer, which is how a 401
    body once reached `raw/*.turn1.md` as though the model had written it. The message
    stays available for the quota scan and for the recorded error; the answer text stays
    text the model actually produced.
    """
    text, etype, emsg, sid = [], None, None, None
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("sessionID") and not sid:
            sid = str(d["sessionID"])
        part = d.get("part") or {}
        if d.get("type") == "text" and part.get("type") == "text":
            text.append(part.get("text", ""))
        if d.get("type") == "error":
            err = d.get("error") or {}
            etype = str(err.get("type") or "error")
            emsg = str(err.get("message") or "")
    return "\n".join(t for t in text if t.strip()), etype, emsg, sid


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
    """
    return WS_ROOT / ("ws-" + hashlib.sha256("|".join(sorted(ids)).encode()).hexdigest()[:10])


def build_ws(ids: list[str]) -> Path:
    out = ws_path(ids)
    args = [x for i in ids for x in ("--scenario", i)]
    try:
        subprocess.run([sys.executable, "tests/make_eval_workspace.py", "--out", str(out),
                        "--force", *args], cwd=ROOT, check=True)
    except subprocess.CalledProcessError as e:
        # make_eval_workspace exits 1 both when a packet is missing and when it finds
        # answer material in the tree. Either way it is a workspace problem, not a
        # provider one, and it must not look like a model failure.
        raise WorkspaceError(f"builder exited {e.returncode} for {' '.join(ids)}") from e
    except OSError as e:
        raise WorkspaceError(f"builder could not be run for {' '.join(ids)}: {e}") from e
    return out


def scenario_ws(sid: str) -> Path:
    """The workspace `sid` runs in: built if absent, then checked against `sid`.

    A scenario's workspace is keyed on that scenario alone, so it is the same for turn 1
    and turn 2, and the same whether the run was started as the full suite or narrowed
    with `--only`. A resumed run therefore finds the workspace the earlier attempt used.

    The check reads the workspace's own MANIFEST.json rather than trusting that a
    directory exists: a directory left behind by an interrupted build can exist without
    the packet copies this scenario needs.
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
    return ws


def one_turn(m: dict, sid: str, turn: int, model: str, timeout: int) -> str:
    """Run one turn. Returns the new scenario status."""
    rec = m["scenarios"][sid]
    win = window(m)
    suffix = "" if turn == 1 else ".turn2"
    packet = ROOT / "evaluation" / "packets" / f"{sid}{suffix}.prompt.md"
    prompt = packet.read_text(encoding="utf-8")

    try:
        ws = scenario_ws(sid)
    except WorkspaceError as e:
        # A local orchestration failure. It is not a model failure and not a quota
        # failure, and recording it as anything other than blocked would let an
        # incomplete scenario read as a completed evaluation.
        rec["status"] = "BLOCKED_BY_INFRASTRUCTURE"
        rec["error"] = f"workspace unusable: {e}"
        save(m)
        return rec["status"]

    # Carried across the two turns of one scenario so turn 2 continues the conversation.
    session_id = (rec.get("turns", {}).get("turn1") or {}).get("session_id")
    attempt = 0
    while attempt <= 1:  # one retry, never on a quota error
        if win.get("quota_exhausted"):
            rec["status"] = "BLOCKED_BY_INFRASTRUCTURE"
            rec["error"] = (f"quota window {window_key(now_ist())} already closed by a "
                            f"provider 429; not retried by rule")
            save(m)
            return rec["status"]
        if win["attempts"] >= MAX_ATTEMPTS:
            win["quota_exhausted"] = True
            rec["status"] = "BLOCKED_BY_INFRASTRUCTURE"
            rec["error"] = f"budget cap {MAX_ATTEMPTS} reached for {window_key(now_ist())}"
            save(m)
            return rec["status"]

        win["attempts"] += 1
        rec["attempts"] += 1
        attempt += 1
        ts = now_ist().isoformat()
        started = time.time()
        try:
            # Turn 2 must continue the SAME session as turn 1. Without --session,
            # `opencode run` starts a fresh conversation each time, so the scenario's own
            # two-turn design collapses: the turn-2 packet says "the customer has replied"
            # to a ticket the model has never seen, and it would score the evidence cold.
            cmd = ["opencode", "run", "--auto", "--model", model, "--format", "json"]
            if turn == 2 and session_id:
                cmd += ["--session", session_id]
            cmd.append(prompt)
            proc = subprocess.run(
                cmd, cwd=ws, capture_output=True, text=True, timeout=timeout)
            out, err, rc = proc.stdout, proc.stderr, proc.returncode
        except subprocess.TimeoutExpired:
            out, err, rc = "", "TIMEOUT", -1

        text, etype, emsg, got_sid = parse_events(out)
        if got_sid and not session_id:
            session_id = got_sid
        RAW.mkdir(parents=True, exist_ok=True)
        (RAW / f"{sid}.turn{turn}.attempt{attempt}.jsonl").write_text(out, encoding="utf-8")
        if err:
            (RAW / f"{sid}.turn{turn}.attempt{attempt}.stderr").write_text(err, encoding="utf-8")

        entry = {"turn": turn, "attempt": attempt, "at": ts,
                 "exit": rc, "seconds": round(time.time() - started, 1),
                 "error_type": etype, "prompt_sha256": sha(packet),
                 "bytes_out": len(text)}
        win["requests"].append({"sid": sid, "turn": turn, "attempt": attempt,
                                "at": ts, "status": None, "error_type": etype})

        blob = f"{etype} {emsg}".lower()
        if any(q in blob for q in QUOTA_ERRORS) or rc == 429:
            entry["status"] = "QUOTA_EXHAUSTED"
            entry["error"] = "quota exhausted; window closed, no retry"
            win["quota_exhausted"] = True
            win["requests"][-1]["status"] = "QUOTA_EXHAUSTED"
            rec["status"] = "BLOCKED_BY_INFRASTRUCTURE"
            rec["error"] = "provider quota exhausted (429); not retried by rule"
            save(m)
            return rec["status"]

        # One predicate, used by both branches below. They used to test different things:
        # the retry branch `etype or rc == -1 or not text`, the give-up branch only
        # `not text`. An error event carrying text satisfied the second test and not the
        # first, so on the retry it satisfied neither and fell through to OK, writing the
        # provider's error message as the answer. Sharing the predicate closes that path.
        failed = bool(etype) or rc == -1 or not text.strip()

        if failed and attempt == 1:
            entry["status"] = "RETRY_ONCE"
            win["requests"][-1]["status"] = "RETRY_ONCE"
            save(m)
            continue

        if failed:
            entry["status"] = "NO_ANSWER"
            entry["error"] = emsg or etype or (err.strip()[:200] if err else "empty response")
            win["requests"][-1]["status"] = "NO_ANSWER"
            rec["status"] = "BLOCKED_BY_INFRASTRUCTURE"
            rec["error"] = entry["error"]
            save(m)
            return rec["status"]

        entry["status"] = "OK"
        win["requests"][-1]["status"] = "OK"
        rec["turns"][f"turn{turn}"] = {
            "at": ts, "model": model, "session_id": got_sid or session_id,
            "prompt_sha256": entry["prompt_sha256"],
            "response_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "chars": len(text), "raw": f"raw/{sid}.turn{turn}.attempt{attempt}.jsonl",
            "attempts": attempt}
        (RAW / f"{sid}.turn{turn}.md").write_text(text, encoding="utf-8")
        rec["status"] = "TURN1_COMPLETE" if turn == 1 else "TURN2_COMPLETE"
        if turn == 2:
            rec["status"] = "AWAITING_GRADE"
        save(m)
        return rec["status"]

    rec["status"] = "BLOCKED_BY_INFRASTRUCTURE"
    save(m)
    return rec["status"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="print progress, spend nothing")
    ap.add_argument("--model", default="openrouter/nvidia/nemotron-3-ultra-550b-a55b:free")
    ap.add_argument("--batch", type=int, default=5)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--only", action="append", default=[])
    a = ap.parse_args()

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
        for wk, w in m["budget"]["windows"].items():
            print(f"  window {wk}: {w['attempts']} attempts, "
                  f"quota_exhausted={w['quota_exhausted']}")
        pend = [s for s in ids if m["scenarios"][s]["status"] != "AWAITING_GRADE"]
        print(f"  pending in selection: {len(pend)}")
        return 0

    todo = [s for s in ids if m["scenarios"][s]["status"] == "NOT_STARTED"]
    if not todo:
        print("nothing pending in this selection")
        return 0
    batch = todo[:a.batch]
    print(f"batch of {len(batch)}: {' '.join(batch)}")

    for sid in batch:
        if m["scenarios"][sid]["status"] != "NOT_STARTED":
            continue
        st = one_turn(m, sid, 1, a.model, a.timeout)
        print(f"  {sid} turn1 -> {st}")
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
          f"(cap {MAX_ATTEMPTS}), quota_exhausted={w['quota_exhausted']}")
    from collections import Counter
    c = Counter(r["status"] for r in m["scenarios"].values())
    print("status: " + ", ".join(f"{k}={v}" for k, v in sorted(c.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())