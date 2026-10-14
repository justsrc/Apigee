#!/usr/bin/env python3
"""Print the full register entry for one or more issue IDs, from the parsed JSON."""
import json
import re
import sys
from pathlib import Path
from typing import TypedDict, cast


class Entry(TypedDict):
    id: str
    product: str
    affects: str
    status: str
    open: bool
    summary: str
    body: str
    has_workaround: bool
    has_fix: bool
    has_cause: bool
    fault_codes: list[str]
    backticked: list[str]
    chars: int


HERE = Path(__file__).resolve().parent
raw_entries = cast(list[Entry], json.loads((HERE / "ki-entries.json").read_text()))
by_id: dict[str, Entry] = {str(e["id"]): e for e in raw_entries}

for iid in sys.argv[1:]:
    e = by_id[iid]
    print("=" * 78)
    print(f"ISSUE {e['id']}  | product={e['product']}  | affects={e['affects']}")
    print(f"status={e['status']!r} open={e['open']} workaround={e['has_workaround']} "
          + f"fix={e['has_fix']} rootcause={e['has_cause']}")
    print(f"fault_codes={e['fault_codes']}")
    print("-" * 78)
    body = str(e["body"])
    # Collapse devsite copy-to-copy wrappers, keep the code blocks.
    body = re.sub(r"\n<div>\n\n</div>\n", "\n", body)
    body = re.sub(r"``` devsite-(click-to-copy|terminal)\n", "```\n", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    print(body.strip())
    print()
