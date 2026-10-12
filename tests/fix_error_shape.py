#!/usr/bin/env python3
"""Rewrite scenario error payloads into the shape Apigee actually returns.

Why this exists. All 45 graded scenarios originally showed a flat body like

    {"errorcode": "...", "faultstring": "...", "status": "500"}

That shape is invented. The documented example on every policy page is nested:

    {"fault": {"detail": {"errorcode": "..."}, "faultstring": "..."}}

and there is no `status` field in the body at all. HTTP status is the response status, not
body content. This matters beyond cosmetics: the core skill tells agents to trap the
`errorcode`, and that advice is only actionable if they know where `errorcode` actually
lives in the response.

Usage:
    python3 tests/fix_error_shape.py            # rewrite in place
    python3 tests/fix_error_shape.py --dry      # report only

The faultstring text is preserved as written. Where a scenario carried an invented
`faultname` or `status` field, the value is moved into a note rather than dropped, so no
information is lost silently.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SCEN = Path(__file__).resolve().parent.parent / "scenarios"

# Matches a fenced json block whose body is a flat error object.
BLOCK_RE = re.compile(r"```json\n(\{.*?\})\n```", re.DOTALL)


def convert(block: str) -> tuple[str, list[str]]:
    try:
        obj = json.loads(block)
    except json.JSONDecodeError:
        return f"```json\n{block}\n```", []
    if not isinstance(obj, dict) or "fault" in obj:
        # Already in the documented nested shape. Return the block unchanged, still
        # fenced, so the caller's comparison is against a like-for-like value.
        return f"```json\n{block}\n```", []
    if "errorcode" not in obj:
        return f"```json\n{block}\n```", []

    code = obj["errorcode"]
    faultstring = obj.get("faultstring")
    faultname = obj.get("faultname")
    status = obj.get("status")

    new: dict = {"fault": {"detail": {"errorcode": code}}}
    if faultstring:
        new["fault"]["faultstring"] = faultstring

    notes = []
    if status:
        notes.append(f"HTTP {status}")
    if faultname and faultname != code.split(".")[-1]:
        notes.append(f"fault name {faultname}")

    rendered = json.dumps(new, indent=2, ensure_ascii=False)
    rendered = "\n".join("  " + ln for ln in rendered.splitlines())
    out = "```json\n" + rendered + "\n```"

    if status:
        out += f"\n\nHTTP response status {status}."
    if faultname and faultname != code.split(".")[-1]:
        out += f" The fault name is {faultname}."
    return out, notes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    total = 0
    for path in sorted(SCEN.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if '"errorcode"' not in text:
            continue
        count = 0

        def repl(m: re.Match) -> str:
            nonlocal count
            new_block, _notes = convert(m.group(1))
            # convert() is handed the inner JSON but returns a full fenced block, so
            # comparing its output against m.group(0), which is also a full fenced block,
            # is what makes an unchanged block compare equal. Comparing the inner form
            # against the full match counted every already-converted block as a change
            # and would have stripped its fences.
            if new_block == m.group(0):
                return m.group(0)
            count += 1
            return new_block

        updated = BLOCK_RE.sub(repl, text)
        if count and not args.dry:
            path.write_text(updated, encoding="utf-8")
        total += count
        if count:
            verb = "would fix" if args.dry else "fixed"
            print(f"  {path.name}: {verb} {count} payload(s)")

    print(f"{'would fix' if args.dry else 'fixed'} {total} payloads total")
    if not total:
        print("nothing to do; no flat error payloads remain")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())