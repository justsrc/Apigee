#!/usr/bin/env python3
"""Run 3 grading. Separate context from answer generation, blinded second grader.

Grading here is a scaffold, not an oracle. This file computes what the documented rubric
computes, from numbers a grader supplies, and refuses to guess a verdict it cannot derive.

It also refuses to grade a scenario the manifest says was never answered, and refuses to turn
a grading input error into a model failure. Both rules come from PROTOCOL.md, and both were
absent until 2026-10-14; see D-041 and D-042 in evaluation/defect-register.md.

Why the split exists. `evaluation/results/run-2/` graded its own answers in the same
conversation that produced them, which the run's own deviation log called out. Run 3 keeps
generation and grading in separate contexts. The primary grader's scores are written to
`grades/primary/`; the second grader reads `raw/`, `prompts/` and the frozen keys and is
pointed at a different directory, so it never sees the primary numbers.

Route 1 is canonical, per `PROTOCOL.md`: each scenario scores its own table, normalised as
`sum of anchors / (4 x rows)`. The critical-failure override is applied after the dimensions
are recorded, never instead of them.

A scenario with an invalid key is UNSCORABLE. It is not forced to PASS or FAIL to keep a
denominator, and the frozen key is never edited here.

WHAT A GRADE IS ABOUT. Each entry records the digest of the answer it was computed from,
not only the digest of the key. `key_sha256` alone certifies the rubric that was applied
and says nothing about which text was scored, so an answer file replaced between
collection and grading produced a PASS that no later reader could tie back to the response
it claimed to be about. `response_sha256` is the manifest's own digest of the turn the
harness recorded, read at grading time and compared with the bytes on disk: a mismatch
refuses the scenario instead of grading whatever is there.

A REFUSAL REMOVES WHAT IT REFUSES. A refused scenario used to write nothing, which left
the previous run's file in place. A directory that still holds last week's PASS for a
scenario this run refused reads exactly like a result, and the run's own summary says
nothing about files it did not write. A refusal now clears any file it is refusing, and
says in its summary entry whether there was one, so an absent file and a cleared file are
distinguishable from a file nobody looked at.

GRADES ARE WRITTEN ATOMICALLY. A grader interrupted mid-write used to leave truncated
JSON under a scenario's name, which is a file that exists and parses as nothing. Each
entry is written to a temporary file beside its destination and moved into place, so what
is under a scenario's name is either the previous entry or the whole new one.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import NotRequired, TypedDict, cast

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "evaluation" / "results" / "run-3"
PK = ROOT / "evaluation" / "packets"
MANIFEST = RUN / "manifest.json"

PASS_AT, MARGINAL_AT = 0.75, 0.50

SUITES = {"EASY": "easy", "MED": "medium", "HARD": "hard",
          "ADV": "adversarial", "REG": "regression"}


class Scenario(TypedDict):
    status: str
    turns: dict[str, object]
    attempts: int
    error: str | None
    block_kind: NotRequired[str]


class Manifest(TypedDict):
    run: str
    protocol: str
    created: str
    model: str | None
    scenarios: dict[str, Scenario]


class GradeInput(TypedDict, total=False):
    """What a grader supplies. Every field is optional because the grader's JSON is
    free-form and `main` checks each one before trusting it; naming the shape does not
    make missing fields safe, it just says which ones are consulted."""
    anchors: dict[str, int]
    critical: bool
    note: str
    unscorable_reason: str
    critical_evidence: str


class GradeEntry(TypedDict):
    scenario: str
    suite: str
    rubric_route: str
    rows: int
    anchors: dict[str, int]
    critical_failure: bool
    normalized_score: float | None
    verdict: str
    unscorable_reason: str | None
    note: str | None
    grader: str
    key_sha256: str
    critical_failure_evidence: NotRequired[str | None]
    # The answer this verdict is about. Not optional on purpose: an entry written without
    # it is an entry whose subject cannot be identified later.
    response_sha256: dict[str, str]
    # Set when the bytes on disk did not match what the manifest recorded for this turn.
    # The scenario is refused in that case, so this only ever appears on an entry that
    # records the mismatch it was refused for, never on a scored one.
    response_drift: NotRequired[dict[str, str]]


class Args(argparse.Namespace):
    list: bool = False
    grader: str = "primary"
    run: bool = False
    scores: str | None = None


# Difficulty-stratified second-grader sample, fixed by rule before any output exists:
# per suite, sort the IDs and take evenly spaced indices so easy, medium and hard are all
# represented and the choice does not depend on any answer.
SECOND_GRADER_SAMPLE: dict[str, list[str]] = {}
for _pre, _n in (("EASY", 3), ("MED", 9), ("HARD", 4), ("ADV", 2), ("REG", 2)):
    _ids = sorted(p.name.split(".")[0] for p in PK.glob(f"{_pre}-*.prompt.md")
                  if not p.name.endswith(".turn2.prompt.md"))
    if not _ids:
        continue
    _take = min(_n, len(_ids))
    _idx = sorted({round(i * (len(_ids) - 1) / (_take - 1)) if _take > 1 else 0
                   for i in range(_take)})
    SECOND_GRADER_SAMPLE[_pre] = [_ids[i] for i in _idx]


def suite_of(sid: str) -> str:
    return SUITES.get(sid.split("-")[0], "unknown")


def rubric_rows(key: str) -> int:
    """Number of scored rows in the scenario's own table."""
    block = re.search(r"^## Evaluation Rubric\s*$(.*?)(?=^## |\Z)", key,
                      re.M | re.S)
    if not block:
        return 0
    rows = [line for line in block.group(1).splitlines()
            if line.strip().startswith("|")
            and not re.match(r"^\|[\s-]+\|", line.strip())]
    return max(0, len(rows) - 1)  # minus the header row


def normalized(anchors: dict[str, int], rows: int) -> float | None:
    """Route 1. Each dimension contributes its anchor value; 4 is the top anchor."""
    if rows <= 0 or not anchors:
        return None
    total = sum(anchors.values())
    if any(v not in (0, 1, 2, 3, 4) for v in anchors.values()):
        return None
    return total / (4 * rows)


def verdict(score: float | None, critical: bool) -> str:
    if score is None:
        return "UNSCORABLE"
    if critical:
        return "FAIL"
    if score >= PASS_AT:
        return "PASS"
    if score >= MARGINAL_AT:
        return "MARGINAL"
    return "FAIL"


def unscorable_reason(anchors: dict, rows: int) -> str:
    """Why a score could not be computed, naming the input that is wrong."""
    if not anchors:
        return "the grader supplied no anchors"
    if rows <= 0:
        return f"the answer key has no rubric table, so {len(anchors)} anchors have no " \
               f"denominator to be scored against"
    bad = sorted(f"{k}={v}" for k, v in anchors.items() if v not in (0, 1, 2, 3, 4))
    return f"anchor value outside the 0-to-4 scale ({', '.join(bad)}); this is a grading " \
           f"input error and is not a model failure"


def load_manifest() -> Manifest:
    if not MANIFEST.exists():
        print("no manifest; nothing has been generated yet", file=sys.stderr)
        raise SystemExit(2)
    return cast("Manifest", json.loads(MANIFEST.read_text(encoding="utf-8")))


def write_entry(path: Path, entry: object) -> Path:
    """Write one grade entry whole or not at all.

    `path.write_text` truncates the destination first, so a grader killed between the
    truncate and the write left a file that exists, is named after a scenario, and parses
    as nothing. The destination is only ever replaced by a file that is already complete.
    """
    # A unique name in the destination directory, not a derived one. A derived
    # `<name>.json.tmp` is shared by two graders writing the same scenario at once, and
    # by `_summary.json` and a scenario that happened to be named `_summary`.
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            _ = fh.write(json.dumps(entry, indent=2) + "\n")
        _ = os.replace(tmp, path)
    except BaseException:
        # os.replace either happened or it did not; either way this name must not survive.
        if os.path.exists(tmp):
            _ = os.unlink(tmp)
        raise
    return path


def why_ungradeable(sid: str, m: dict) -> str | None:
    """Why this scenario may not be graded, or None if it may.

    PROTOCOL.md says "manifest.json is authoritative for collection state" and that a grade
    is only meaningful against a response that exists. `--run` used to enforce neither. It
    took the grader's JSON at face value, so a scores file naming a scenario that was never
    run produced a scored, passing result: driven against run 3's own manifest, where all
    103 scenarios are NOT_STARTED and no answer file exists, MED-13 was written out as
    PASS with a normalized score of 1.0.

    The docstring here and the commit that fixed the sibling generation defect both claimed
    this file selects the scenarios the manifest marks AWAITING_GRADE. Only --list did.

    It also checks that the answers on disk are the answers the manifest recorded.
    `key_sha256` in a grade entry ties a verdict to a rubric; nothing tied it to a
    response, so an answer file rewritten between collection and grading was graded and
    recorded with no record of which text produced the score. The manifest holds
    `response_sha256` per turn for exactly this check, and it is made here, before any
    score is computed.
    """
    rec = m.get("scenarios", {}).get(sid)
    if rec is None:
        return "no such scenario in this run's manifest"
    status = rec.get("status")
    if status != "AWAITING_GRADE":
        return f"manifest says {status}, not AWAITING_GRADE"
    missing = [f"raw/{sid}.turn{n}.md" for n in (1, 2)
               if not (RUN / "raw" / f"{sid}.turn{n}.md").is_file()]
    if missing:
        return "no answer file for " + " or ".join(missing)
    drift = response_drift(sid, m)
    if drift:
        return ("the answer on disk is not the answer the manifest recorded: "
                + "; ".join(f"{turn} is {got[:12]} on disk, {want[:12]} when collected"
                            for turn, (got, want) in sorted(drift.items())))
    return None


def response_drift(sid: str, m: dict) -> dict[str, tuple[str, str]]:
    """Turns whose answer file no longer matches the digest the manifest recorded.

    Returns (on_disk, recorded) per turn. A turn the manifest never recorded a digest for
    is not drift: an older manifest predates the field, and refusing those would make a
    recorded run ungradable rather than making it auditable. The scenario is still
    refused when any of its turns did drift.
    """
    drift: dict[str, tuple[str, str]] = {}
    turns = (m.get("scenarios", {}).get(sid) or {}).get("turns") or {}
    for n in (1, 2):
        recorded = (turns.get(f"turn{n}") or {}).get("response_sha256")
        p = RUN / "raw" / f"{sid}.turn{n}.md"
        if not recorded or not p.is_file():
            continue
        got = hashlib.sha256(p.read_bytes()).hexdigest()
        if got != recorded:
            drift[f"turn{n}"] = (got, str(recorded))
    return drift


def main() -> int:
    ap = argparse.ArgumentParser()
    _ = ap.add_argument("--list", action="store_true")
    _ = ap.add_argument("--grader", default="primary", choices=["primary", "second"])
    _ = ap.add_argument("--run", action="store_true", help="summarise existing grade files")
    _ = ap.add_argument("--scores", help="JSON file of {sid: {anchors, critical, note}}")
    a = ap.parse_args(namespace=Args())

    if a.list:
        m = load_manifest()
        ready = sorted(s for s, r in m["scenarios"].items()
                       if r["status"] == "AWAITING_GRADE")
        print(f"model            {m.get('model')}")
        print(f"generated        {len(ready)} awaiting grade")
        print(f"second-grader sample ({sum(len(v) for v in SECOND_GRADER_SAMPLE.values())}):")
        for pre in ("EASY", "MED", "HARD", "ADV", "REG"):
            ids = SECOND_GRADER_SAMPLE.get(pre, [])
            print(f"  {pre:<5} {len(ids)}  {' '.join(ids)}")
        return 0

    if not a.run:
        ap.error("use --list, or --run with --scores")

    if not a.scores:
        print("--run needs --scores pointing at the grader's JSON output", file=sys.stderr)
        return 2
    supplied = cast("dict[str, GradeInput]",
                    json.loads(Path(a.scores).read_text(encoding="utf-8")))
    out_dir = RUN / "grades" / a.grader
    out_dir.mkdir(parents=True, exist_ok=True)

    m = load_manifest()
    refused: list[dict] = []
    for sid, rec in supplied.items():
        # `_summary.json` is the run's own summary and `_summary` is the id that would
        # write it. A scores file naming it was refused for being unknown to the manifest,
        # and the refusal cleanup then deleted the summary it had just been about to
        # write. Ids beginning with an underscore are refused here instead, and nothing is
        # removed for them.
        why = (f"scenario id {sid!r} is reserved: ids beginning with _ are the run's own "
               "summaries, not scenarios") if sid.startswith("_") else why_ungradeable(sid, m)
        if why is None:
            continue
        if sid.startswith("_"):
            refused.append({"scenario": sid, "reason": why, "stale_grade_removed": False})
            print(f"  {sid}: refused, {why}", file=sys.stderr)
            continue
        # A refusal that leaves the previous run's file in place is not a refusal: a
        # reader of grades/<grader>/ sees the old PASS and no indication that this run
        # declined to produce one. Clear it, and record whether there was something to
        # clear so an absent file, a cleared file, and a file nobody looked at stay
        # distinguishable.
        stale = out_dir / f"{sid}.json"
        cleared = stale.is_file()
        if cleared:
            _ = stale.unlink()
        refused.append({"scenario": sid, "reason": why, "stale_grade_removed": cleared})
        print(f"  {sid}: refused, {why}", file=sys.stderr)
        if cleared:
            print(f"  {sid}: removed the previous run's grade file for this scenario",
                  file=sys.stderr)

    written: list[GradeEntry] = []
    for sid, rec in supplied.items():
        if any(r["scenario"] == sid for r in refused):
            continue
        key = (PK / f"{sid}.key.md")
        if not key.is_file():
            print(f"  {sid}: no key, skipped", file=sys.stderr)
            continue
        rows = rubric_rows(key.read_text(encoding="utf-8"))
        anchors = {k: int(v) for k, v in (rec.get("anchors") or {}).items()}
        crit = bool(rec.get("critical", False))
        # What the verdict is about, read from the manifest and checked against the bytes
        # being scored above. Recorded on every entry so a later reader can tell which
        # text produced this score without trusting the grade file's own word.
        answered = {f"turn{n}": hashlib.sha256(
            (RUN / "raw" / f"{sid}.turn{n}.md").read_bytes()).hexdigest() for n in (1, 2)}
        # A grader whose anchor count is not the rubric's row count is not scoring this
        # table, and the score is not computable. The guard used to test `len(anchors) <
        # rows` only, which caught the under-count and waved the over-count through:
        # eight anchors at the top anchor on a seven-row table scores 32/28 = 1.1429,
        # rounds to 1.14, and is recorded as a clean PASS above the scale's own maximum.
        # Direction matters here. Under-counting inflates the score, and over-counting
        # inflates it too, so neither is a number to scale and both are refusals.
        if anchors and rows and len(anchors) != rows:
            direction = "fewer" if len(anchors) < rows else "more"
            entry: GradeEntry = {
                "scenario": sid, "suite": suite_of(sid), "rubric_route": "Route 1",
                "rows": rows, "anchors": anchors, "critical_failure": crit,
                "normalized_score": None, "verdict": "UNSCORABLE",
                "unscorable_reason": (f"grader supplied {len(anchors)} anchors for a "
                                      + f"{rows}-row table, which is {direction} than the "
                                      "table has rows; the score is not computable"),
                "note": rec.get("note"), "grader": a.grader,
                "key_sha256": hashlib.sha256(key.read_bytes()).hexdigest(),
                "response_sha256": answered,
            }
            _ = write_entry(out_dir / f"{sid}.json", entry)
            written.append(entry)
            continue
        score = normalized(anchors, rows)
        v = verdict(score, crit)
        reason = rec.get("unscorable_reason")
        if v == "UNSCORABLE" and not reason:
            # PROTOCOL.md: "An invalid grading reference is never counted as a model
            # failure." This used to coerce to FAIL whenever anchors were present and the
            # score could not be computed, so a grader's typo became a model failure in
            # the counts: one anchor of 7 on a 0-to-4 scale produced verdict FAIL with a
            # null score and no reason recorded. State what is wrong with the input
            # instead of guessing a verdict from it.
            reason = unscorable_reason(anchors, rows)
            v = "UNSCORABLE"
        entry = {
            "scenario": sid, "suite": suite_of(sid),
            "rubric_route": "Route 1 (scenario table)",
            "rows": rows, "anchors": anchors,
            "critical_failure": crit,
            "critical_failure_evidence": rec.get("critical_evidence"),
            "normalized_score": None if score is None else round(score, 4),
            "verdict": v,
            "unscorable_reason": reason,
            "note": rec.get("note"),
            "grader": a.grader,
            "key_sha256": hashlib.sha256(key.read_bytes()).hexdigest(),
            "response_sha256": answered,
        }
        _ = write_entry(out_dir / f"{sid}.json", entry)
        written.append(entry)

    n = len(written)
    by = {"PASS": 0, "MARGINAL": 0, "FAIL": 0, "UNSCORABLE": 0}
    scores: list[float] = []
    cf = 0
    for e in written:
        by[e["verdict"]] = by.get(e["verdict"], 0) + 1
        if e["normalized_score"] is not None:
            scores.append(e["normalized_score"])
        if not e["critical_failure"]:
            cf += 1
    summary = {
        "grader": a.grader, "graded": n, "by_verdict": by,
        "refused": refused,
        "critical_failure_free": cf,
        "mean_normalized_score": round(sum(scores) / len(scores), 4) if scores else None,
        "scored": len(scores),
    }
    _ = write_entry(out_dir / "_summary.json", summary)
    print(json.dumps(summary, indent=2))
    if refused:
        # A refused scenario wrote no grade file, so it cannot be mistaken for a result.
        # The nonzero exit is what stops the rest of the summary being read as complete.
        print(f"{len(refused)} scenario(s) refused; see \"refused\" in the summary above",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())