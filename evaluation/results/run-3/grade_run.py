#!/usr/bin/env python3
"""Run 3 grading. Separate context from answer generation, blinded second grader.

Grading here is a scaffold, not an oracle. This file computes what the documented rubric
computes, from numbers a grader supplies, and refuses to guess a verdict it cannot derive.

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
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
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


class Manifest(TypedDict):
    run: str
    protocol: str
    created: str
    model: str | None
    scenarios: dict[str, Scenario]


class GradeInput(TypedDict, total=False):
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


def load_manifest() -> Manifest:
    if not MANIFEST.exists():
        print("no manifest; nothing has been generated yet", file=sys.stderr)
        raise SystemExit(2)
    return cast("Manifest", json.loads(MANIFEST.read_text(encoding="utf-8")))


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

    written: list[GradeEntry] = []
    for sid, rec in supplied.items():
        key = (PK / f"{sid}.key.md")
        if not key.is_file():
            print(f"  {sid}: no key, skipped", file=sys.stderr)
            continue
        rows = rubric_rows(key.read_text(encoding="utf-8"))
        anchors = {k: int(v) for k, v in (rec.get("anchors") or {}).items()}
        crit = bool(rec.get("critical", False))
        # A grader who scores fewer dimensions than the table has rows has under-counted the
        # denominator, which silently inflates the score. Refuse rather than scale it.
        if anchors and rows and len(anchors) < rows:
            entry: GradeEntry = {
                "scenario": sid, "suite": suite_of(sid), "rubric_route": "Route 1",
                "rows": rows, "anchors": anchors, "critical_failure": crit,
                "normalized_score": None, "verdict": "UNSCORABLE",
                "unscorable_reason": (f"grader supplied {len(anchors)} anchors for a "
                                      + f"{rows}-row table; the score is not computable"),
                "note": rec.get("note"), "grader": a.grader,
                "key_sha256": hashlib.sha256(key.read_bytes()).hexdigest(),
            }
            _ = (out_dir / f"{sid}.json").write_text(json.dumps(entry, indent=2) + "\n",
                                                     encoding="utf-8")
            written.append(entry)
            continue
        score = normalized(anchors, rows)
        v = verdict(score, crit)
        if v == "UNSCORABLE" and not rec.get("unscorable_reason"):
            v = "FAIL" if anchors else "UNSCORABLE"
        entry = {
            "scenario": sid, "suite": suite_of(sid),
            "rubric_route": "Route 1 (scenario table)",
            "rows": rows, "anchors": anchors,
            "critical_failure": crit,
            "critical_failure_evidence": rec.get("critical_evidence"),
            "normalized_score": None if score is None else round(score, 4),
            "verdict": v,
            "unscorable_reason": rec.get("unscorable_reason"),
            "note": rec.get("note"),
            "grader": a.grader,
            "key_sha256": hashlib.sha256(key.read_bytes()).hexdigest(),
        }
        _ = (out_dir / f"{sid}.json").write_text(json.dumps(entry, indent=2) + "\n",
                                                 encoding="utf-8")
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
        "critical_failure_free": cf,
        "mean_normalized_score": round(sum(scores) / len(scores), 4) if scores else None,
        "scored": len(scores),
    }
    _ = (out_dir / "_summary.json").write_text(json.dumps(summary, indent=2) + "\n",
                                               encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())