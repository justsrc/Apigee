#!/usr/bin/env python3
"""Find duplicate and near-duplicate scenarios.

Two scenarios can share a source and still test different things. Two scenarios can use
completely different wording and test exactly the same thing. A file count is not coverage,
and "103 scenarios" says nothing about whether the 103 are 103 distinct diagnostic
challenges or 60 plus 43 rewrites.

This compares them on several axes, because any one of them alone produces false positives:

  exact       identical body text
  normalised  identical after stripping punctuation, digits and backticks, which catches
              reformatting and ID renumbering
  shared-src  same cited source URL, which is a candidate, not a finding
  ticket      similarity of the initial support ticket, the part the agent actually reads

It reports candidates for human judgement. It does not decide that two scenarios are the
same, because deciding that needs someone who knows Apigee.

Usage:
    python3 tests/find_duplicates.py
    python3 tests/find_duplicates.py --threshold 0.82
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))

import check_repo as cr  # noqa: E402

ID_RE = re.compile(r"\b(EASY|MED|HARD|ADV|REG)-\d+\b")


def normalise(text: str) -> str:
    text = ID_RE.sub("ID", text)
    text = re.sub(r"https?://\S+", "URL", text)
    text = re.sub(r"[`*_#>|\[\]()<>-]", " ", text)
    text = re.sub(r"\b\d+\b", "N", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def section(block: str, name: str) -> str:
    for _sid, b in cr.find_scenario_blocks(block):
        pass
    ok, _size = cr.section_present(block, name)
    hs = cr.parse_headings(block)
    target = cr._norm(name)
    for i, (_lvl, text, ln) in enumerate(hs):
        if i == 0:
            continue
        if cr._norm(text) == target or target in cr._norm(text):
            lines = block.splitlines()
            stop = hs[i + 1][2] if i + 1 < len(hs) else len(lines)
            return "\n".join(lines[ln + 1:stop])
    return ""


def load() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for p in sorted((ROOT / "scenarios").glob("*.md")):
        if p.name == "index.md":
            continue
        for sid, block in cr.find_scenario_blocks(cr.read(p)):
            urls = set(cr.URL_RE.findall(block))
            ticket = section(block, "initial support ticket")
            out[sid] = {
                "file": p.name,
                "norm": normalise(block),
                "urls": urls,
                "ticket": normalise(ticket),
                "topic": (re.search(r"^- Primary topic:\s*(.+)$", block, re.M) or [None, "?"])[1]
                if re.search(r"^- Primary topic:\s*(.+)$", block, re.M) else "?",
            }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=float, default=0.80)
    args = ap.parse_args()

    data = load()
    ids = sorted(data)
    print(f"{len(ids)} scenarios loaded from scenarios/*.md\n")

    # 1. exact duplicates
    exact = defaultdict(list)
    for sid in ids:
        exact[data[sid]["norm"]].append(sid)
    exact_dupes = [v for v in exact.values() if len(v) > 1]

    # 2. normalised near-duplicates
    near = []
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            if data[a]["norm"] == data[b]["norm"]:
                continue
            r = difflib.SequenceMatcher(None, data[a]["norm"], data[b]["norm"]).ratio()
            if r >= args.threshold:
                near.append((r, a, b))

    # 3. shared source
    by_url = defaultdict(list)
    for sid in ids:
        for u in data[sid]["urls"]:
            by_url[u].append(sid)
    shared = {u: v for u, v in by_url.items() if len(v) > 2}

    # 4. ticket similarity among scenarios that do not share a source
    ticket_near = []
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            if not data[a]["ticket"] or not data[b]["ticket"]:
                continue
            r = difflib.SequenceMatcher(None, data[a]["ticket"], data[b]["ticket"]).ratio()
            if r >= 0.75:
                ticket_near.append((r, a, b))

    print("=" * 72)
    print("1. EXACT DUPLICATES (identical body text)")
    print("=" * 72)
    if exact_dupes:
        for grp in exact_dupes:
            print(f"  {', '.join(grp)}")
    else:
        print("  none")

    print()
    print("=" * 72)
    print(f"2. NEAR-DUPLICATES (normalised similarity >= {args.threshold})")
    print("=" * 72)
    if near:
        for r, a, b in sorted(near, reverse=True):
            print(f"  {r:.3f}  {a} ({data[a]['topic'][:34]})")
            print(f"         {b} ({data[b]['topic'][:34]})")
    else:
        print("  none")

    print()
    print("=" * 72)
    print(f"3. SHARED SOURCES cited by more than two scenarios (>= 3)")
    print("=" * 72)
    if shared:
        for u, v in sorted(shared.items(), key=lambda kv: -len(kv[1])):
            print(f"  {len(v):2}  {u}")
            print(f"      {', '.join(sorted(v))}")
    else:
        print("  none")

    print()
    print("=" * 72)
    print("4. SIMILAR INITIAL TICKETS (similarity >= 0.75)")
    print("=" * 72)
    if ticket_near:
        for r, a, b in sorted(ticket_near, reverse=True):
            print(f"  {r:.3f}  {a}  <->  {b}")
    else:
        print("  none")

    print()
    print("Shared sources are normal and not a defect: a popular policy page legitimately")
    print("backs several distinct faults. The judgement call is whether each scenario tests a")
    print("different diagnosis, which needs someone who knows Apigee, not a string match.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())