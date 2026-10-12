#!/usr/bin/env python3
"""Print the full register entry for one or more issue IDs, from the parsed JSON."""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
by_id = {e["id"]: e for e in json.loads((HERE / "ki-entries.json").read_text())}

for iid in sys.argv[1:]:
    e = by_id[iid]
    print("=" * 78)
    print(f"ISSUE {e['id']}  | product={e['product']}  | affects={e['affects']}")
    print(f"status={e['status']!r} open={e['open']} workaround={e['has_workaround']} "
          f"fix={e['has_fix']} rootcause={e['has_cause']}")
    print(f"fault_codes={e['fault_codes']}")
    print("-" * 78)
    body = e["body"]
    # Collapse devsite copy-to-copy wrappers, keep the code blocks.
    body = re.sub(r"\n<div>\n\n</div>\n", "\n", body)
    body = re.sub(r"``` devsite-(click-to-copy|terminal)\n", "```\n", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    print(body.strip())
    print()
