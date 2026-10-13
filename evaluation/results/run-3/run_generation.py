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
            text.append(emsg)
    return "\n".join(t for t in text if t.strip()), etype, emsg, sid


def build_ws(ids: list[str]) -> Path:
    out = WS_ROOT / ("ws-" + hashlib.sha256("|".join(ids).encode()).hexdigest()[:10])
    subprocess.run([sys.executable, "tests/make_eval_workspace.py", "--out", str(out),
                    "--force"] + sum([["--scenario", i] for i in ids], []),
                   cwd=ROOT, check=True)
    return out


def one_turn(m: dict, sid: str, turn: int, model: str, timeout: int) -> str:
    """Run one turn. Returns the new scenario status."""
    rec = m["scenarios"][sid]
    win = window(m)
    suffix = "" if turn == 1 else ".turn2"
    packet = ROOT / "evaluation" / "packets" / f"{sid}{suffix}.prompt.md"
    prompt = packet.read_text(encoding="utf-8")

    ws = WS_ROOT / ("ws-" + hashlib.sha256(
        json.dumps(sorted(m["scenarios"])).encode()).hexdigest()[:10])
    if not (ws / "MANIFEST.json").exists():
        build_ws([sid])

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

        if (etype or rc == -1 or not text.strip()) and attempt == 1:
            entry["status"] = "RETRY_ONCE"
            save(m)
            continue

        if not text.strip():
            entry["status"] = "NO_ANSWER"
            entry["error"] = etype or (err.strip()[:200] if err else "empty response")
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